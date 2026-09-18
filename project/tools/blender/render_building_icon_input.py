"""Render a CSC building scene to a transparent icon input without saving the blend.

Run: blender --background FILE.blend --python render_building_icon_input.py -- OUTPUT.png
"""
import math
import os
import sys

import bpy
from mathutils import Vector


def main():
    args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    if len(args) != 1:
        raise SystemExit("Expected one output PNG path after --")
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
    meshes = [o for o in scene.objects if o.type == "MESH" and not o.hide_render]
    building = max(meshes, key=lambda o: o.dimensions.x * o.dimensions.y * o.dimensions.z)
    foundation = building.vertex_groups.get("Foundation")
    if foundation is None:
        below_ground = [v.index for v in building.data.vertices if (building.matrix_world @ v.co).z < 0]
        if below_ground:
            foundation = building.vertex_groups.new(name="ICON_Foundation_BelowGround")
            foundation.add(below_ground, 1.0, "REPLACE")
            print("ICON_FOUNDATION_VERTICES", building.name, len(below_ground))
    if foundation is not None:
        foundation_mask = building.modifiers.new(name="ICON_HideFoundation", type="MASK")
        foundation_mask.vertex_group = foundation.name
        foundation_mask.invert_vertex_group = True

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
    camera_data.lens = 50
    camera = bpy.data.objects.new("ICON_Input_Camera", camera_data)
    scene.collection.objects.link(camera)
    scene.camera = camera
    direction = Vector((0, -1, math.tan(math.radians(30)))).normalized()
    camera.location = target + direction * 350
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.clip_end = 2000

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
    bpy.ops.render.render(write_still=True)
    print("ICON_OUTPUT", output)


if __name__ == "__main__":
    main()
