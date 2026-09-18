"""Render a composed CSC building to a transparent Strategic View input.

Run: blender --background FILE.blend --python render_building_sv_input.py -- OUTPUT.png
Does not save the source blend.
"""
import math
import os
import sys

import bpy
from mathutils import Vector


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 1:
        raise SystemExit("Expected one output PNG after --")
    output = os.path.abspath(args[0])
    scene = bpy.context.scene
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

    for obj in scene.objects:
        if obj.type == "MESH" and (obj.name.startswith("REVIEW_") or obj.name.startswith("ROAD_")):
            obj.hide_render = True
    meshes = [obj for obj in scene.objects if obj.type == "MESH" and not obj.hide_render]
    if not meshes:
        raise RuntimeError("No visible meshes")
    building = max(meshes, key=lambda obj: obj.dimensions.x * obj.dimensions.y * obj.dimensions.z)
    foundation = building.vertex_groups.get("Foundation")
    if foundation is None:
        below = [v.index for v in building.data.vertices if (building.matrix_world @ v.co).z < 0]
        if below:
            foundation = building.vertex_groups.new(name="SV_Foundation_BelowGround")
            foundation.add(below, 1.0, "REPLACE")
            print("SV_FOUNDATION_VERTICES", building.name, len(below))
    if foundation is not None:
        mask = building.modifiers.new(name="SV_HideFoundation", type="MASK")
        mask.vertex_group = foundation.name
        mask.invert_vertex_group = True

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
    direction = Vector((0, -1, 0.82)).normalized()
    camera.location = target + direction * 800
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    scene.camera = camera
    print("SV_CAMERA_SCALE", round(camera_data.ortho_scale, 2))

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
    bpy.ops.render.render(write_still=True)
    print("SV_OUTPUT", output)


if __name__ == "__main__":
    main()
