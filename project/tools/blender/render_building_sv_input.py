"""Render a composed CSC building to a transparent Strategic View input.

Run: blender --background FILE.blend --python render_building_sv_input.py -- OUTPUT.png
Does not save the source blend.
"""
import argparse
import math
import os
import sys

import bpy
import bmesh
from mathutils import Vector


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", help="Transparent 1024px PNG destination")
    parser.add_argument("--elevation", type=float,
                        default=math.degrees(math.atan(0.82)),
                        help="Camera elevation in degrees (default: existing 39.35-degree SV view)")
    parser.add_argument("--clockwise-turn", type=float, default=0.0,
                        help="Apparent building turn in degrees; camera orbits instead of moving geometry")
    parsed = parser.parse_args(args)
    if not 0 < parsed.elevation < 90:
        parser.error("--elevation must be between 0 and 90 degrees")
    if not -180 <= parsed.clockwise_turn <= 180:
        parser.error("--clockwise-turn must be between -180 and 180 degrees")
    output = os.path.abspath(parsed.output)
    scene = bpy.data.scenes.get("Export") or bpy.context.scene
    source_dir = os.path.dirname(bpy.data.filepath)
    texture_dir = os.path.join(source_dir, "textures")
    missing = []
    for img in bpy.data.images:
        if img.source != "FILE":
            continue
        name = os.path.basename(bpy.path.abspath(img.filepath))
        candidate = os.path.join(texture_dir, name)
        if os.path.isfile(candidate):
            img.filepath = candidate
            img.reload()
        elif name:
            missing.append(name)
    if missing:
        raise RuntimeError("Missing scene textures: " + ", ".join(sorted(set(missing))))

    context_prefixes = ("review_", "road_", "csc_road_", "csc_dirt_", "preview_")
    context_fragments = ("decal", "terrain", "ground", "grass", "cobble", "paving")
    hidden_context = []
    for obj in scene.objects:
        name = obj.name.casefold()
        if obj.type == "MESH" and (name.startswith(context_prefixes) or any(part in name for part in context_fragments)):
            obj.hide_render = True
            hidden_context.append(obj.name)
    print("SV_HIDDEN_CONTEXT", len(hidden_context), hidden_context)
    meshes = [obj for obj in scene.objects if obj.type == "MESH" and not obj.hide_render]
    if not meshes:
        raise RuntimeError("No visible meshes")
    building = max(meshes, key=lambda obj: obj.dimensions.x * obj.dimensions.y * obj.dimensions.z)
    # Bisect a render-only mesh copy: masking below-ground vertices also removes
    # the wall faces spanning Z=0 and makes the entire lower storey disappear.
    building.data = building.data.copy()
    mesh = bmesh.new()
    mesh.from_mesh(building.data)
    before_faces = len(mesh.faces)
    local_ground = building.matrix_world.inverted() @ Vector((0, 0, 0))
    local_up = (building.matrix_world.transposed().to_3x3() @ Vector((0, 0, 1))).normalized()
    bmesh.ops.bisect_plane(
        mesh, geom=list(mesh.verts) + list(mesh.edges) + list(mesh.faces),
        plane_co=local_ground, plane_no=local_up, clear_inner=True,
    )
    mesh.to_mesh(building.data)
    mesh.free()
    building.data.update()
    print("SV_FOUNDATION_CLIP", building.name, before_faces, len(building.data.polygons))

    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in meshes:
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        points.extend(evaluated.matrix_world @ vertex.co for vertex in mesh.vertices)
        evaluated.to_mesh_clear()
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    target = (low + high) * 0.5
    print("SV_BOUNDS", tuple(round(v, 2) for v in low), tuple(round(v, 2) for v in high))

    camera_data = bpy.data.cameras.new("SV_Input_Camera")
    camera_data.type = "ORTHO"
    camera_data.ortho_scale = max(high.x - low.x, high.y - low.y, high.z - low.z) * 1.70
    camera_data.clip_end = 5000
    camera = bpy.data.objects.new("SV_Input_Camera", camera_data)
    scene.collection.objects.link(camera)
    # Orbiting the camera counterclockwise by N degrees makes the composed
    # building appear turned clockwise by N degrees, with no scene edits.
    turn = math.radians(parsed.clockwise_turn)
    direction = Vector((math.sin(turn), -math.cos(turn),
                        math.tan(math.radians(parsed.elevation)))).normalized()
    camera.location = target + direction * 800
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    print("SV_CAMERA", "ORTHO", "elevation", round(parsed.elevation, 3),
          "building_turn_clockwise", parsed.clockwise_turn,
          "direction", tuple(round(value, 5) for value in direction),
          "scale", round(camera_data.ortho_scale, 2))

    # In this front-view camera, negative X is image left. A high, left,
    # frontal sun creates form shading on right-facing walls/roof pitches.
    for obj in scene.objects:
        if obj.type == "LIGHT":
            obj.hide_render = True
    key_data = bpy.data.lights.new("SV_UpperLeft_Key", type="SUN")
    key_data.energy = 3.0
    key_data.angle = math.radians(8)
    key = bpy.data.objects.new("SV_UpperLeft_Key", key_data)
    scene.collection.objects.link(key)
    key.location = target + Vector((-300, -280, 500))
    key.rotation_euler = (target - key.location).to_track_quat("-Z", "Y").to_euler()

    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1024
    scene.render.resolution_y = 1024
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.filepath = output
    os.makedirs(os.path.dirname(output), exist_ok=True)
    bpy.ops.render.render(scene=scene.name, write_still=True)
    print("SV_OUTPUT", output)


if __name__ == "__main__":
    main()
