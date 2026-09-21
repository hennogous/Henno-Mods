"""Render a CSC building scene to a transparent icon input without saving the blend.

Run: blender --background FILE.blend --python render_building_icon_input.py -- OUTPUT.png
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
    parser.add_argument("output", help="Transparent PNG destination")
    parser.add_argument("--camera-distance", type=float,
                        help="Distance from the building bounds center; default is 1.5 times the widest span")
    parser.add_argument("--lens", type=float, default=30.0,
                        help="Perspective lens in mm (default: 30)")
    parsed = parser.parse_args(args)
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
    print("ICON_HIDDEN_CONTEXT", len(hidden_context), hidden_context)
    meshes = [o for o in scene.objects if o.type == "MESH" and not o.hide_render]
    building = max(meshes, key=lambda o: o.dimensions.x * o.dimensions.y * o.dimensions.z)
    # A vertex-group MASK removes whole wall faces whenever one bottom vertex is
    # below ground. Bisect a render-only mesh copy instead so the ground floor stays.
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
    print("ICON_FOUNDATION_CLIP", building.name, before_faces, len(building.data.polygons))

    depsgraph = bpy.context.evaluated_depsgraph_get()
    points = []
    for obj in meshes:
        evaluated = obj.evaluated_get(depsgraph)
        evaluated_mesh = evaluated.to_mesh()
        points.extend(evaluated.matrix_world @ vertex.co for vertex in evaluated_mesh.vertices)
        evaluated.to_mesh_clear()
    low = Vector(tuple(min(p[i] for p in points) for i in range(3)))
    high = Vector(tuple(max(p[i] for p in points) for i in range(3)))
    target = (low + high) * 0.5
    print("ICON_BOUNDS", tuple(round(v, 2) for v in low), tuple(round(v, 2) for v in high))

    camera_data = bpy.data.cameras.new("ICON_Input_Camera")
    camera_data.type = "PERSP"
    camera_data.lens = parsed.lens
    camera = bpy.data.objects.new("ICON_Input_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    direction = Vector((0, -1, math.tan(math.radians(30)))).normalized()
    span = max(high.x - low.x, high.y - low.y, high.z - low.z)
    camera_distance = parsed.camera_distance or span * 1.5
    camera.location = target + direction * camera_distance
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.clip_end = 2000
    print("ICON_CAMERA", "PERSP", "distance", round(camera_distance, 2),
          "lens", round(camera_data.lens, 2))

    # A broad frontal key keeps the facade and occupational props readable in
    # the small icon without flattening their shadows.
    key_data = bpy.data.lights.new("ICON_FrontLeft_Key", type="SUN")
    key_data.energy = 3.0
    key_data.angle = math.radians(8)
    key = bpy.data.objects.new("ICON_FrontLeft_Key", key_data)
    scene.collection.objects.link(key)
    key.location = target + Vector((-240, -280, 360))
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
    print("ICON_OUTPUT", output)


if __name__ == "__main__":
    main()
