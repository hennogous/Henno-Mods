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
    parser.add_argument("--elevation", type=float, default=30.0,
                        help="Camera elevation in degrees above the ground (default: 30)")
    parser.add_argument("--view-transform", choices=("scene", "AgX", "Standard"),
                        default="scene", help="Color management transform (default: keep scene setting)")
    parser.add_argument("--exposure", type=float,
                        help="Color management exposure in stops (default: keep scene setting)")
    parser.add_argument("--sun-energy", type=float, default=3.0,
                        help="Front-left key sun energy (default: 3)")
    parser.add_argument("--world-strength", type=float,
                        help="World Background node strength (default: keep scene setting)")
    parser.add_argument("--world-color", type=float, nargs=3, metavar=("R", "G", "B"),
                        help="Linear world Background RGB (default: keep scene setting)")
    parser.add_argument("--geometry-passes-dir",
                        help="Optional folder for render-only normal and depth PNGs")
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
    if not 0 < parsed.elevation < 90:
        raise ValueError("Camera elevation must be between 0 and 90 degrees")
    direction = Vector((0, -1, math.tan(math.radians(parsed.elevation)))).normalized()
    span = max(high.x - low.x, high.y - low.y, high.z - low.z)
    camera_distance = parsed.camera_distance or span * 1.5
    camera.location = target + direction * camera_distance
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    camera_data.clip_end = 2000
    print("ICON_CAMERA", "PERSP", "distance", round(camera_distance, 2),
          "lens", round(camera_data.lens, 2), "elevation", parsed.elevation)

    # A broad frontal key keeps the facade and occupational props readable in
    # the small icon without flattening their shadows.
    key_data = bpy.data.lights.new("ICON_FrontLeft_Key", type="SUN")
    key_data.energy = parsed.sun_energy
    key_data.angle = math.radians(8)
    key = bpy.data.objects.new("ICON_FrontLeft_Key", key_data)
    scene.collection.objects.link(key)
    key.location = target + Vector((-240, -280, 360))
    key.rotation_euler = (target - key.location).to_track_quat("-Z", "Y").to_euler()

    if parsed.view_transform != "scene":
        scene.view_settings.view_transform = parsed.view_transform
    if parsed.exposure is not None:
        scene.view_settings.exposure = parsed.exposure
    if parsed.world_strength is not None or parsed.world_color is not None:
        background = None
        if scene.world is not None and scene.world.use_nodes:
            background = next((node for node in scene.world.node_tree.nodes
                               if node.type == "BACKGROUND"), None)
        if background is None:
            # Some final building scenes have no node-based world. Construct a
            # render-only one; the source blend is never saved by this helper.
            world = bpy.data.worlds.new("ICON_Render_World")
            world.use_nodes = True
            world.node_tree.nodes.clear()
            background = world.node_tree.nodes.new("ShaderNodeBackground")
            output_node = world.node_tree.nodes.new("ShaderNodeOutputWorld")
            world.node_tree.links.new(background.outputs["Background"],
                                      output_node.inputs["Surface"])
            scene.world = world
            print("ICON_WORLD_CREATED", world.name)
        if parsed.world_strength is not None:
            background.inputs["Strength"].default_value = parsed.world_strength
        if parsed.world_color is not None:
            background.inputs["Color"].default_value = (*parsed.world_color, 1.0)
    print("ICON_LIGHTING", "sun", key_data.energy, "world",
          scene.world.node_tree.nodes.get("Background").inputs["Strength"].default_value
          if scene.world and scene.world.use_nodes and scene.world.node_tree.nodes.get("Background") else "scene",
          "transform", scene.view_settings.view_transform,
          "exposure", scene.view_settings.exposure)

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
    if parsed.geometry_passes_dir:
        pass_dir = os.path.abspath(parsed.geometry_passes_dir)
        os.makedirs(pass_dir, exist_ok=True)
        layer = scene.view_layers[0]
        original_override = layer.material_override
        original_transform = scene.view_settings.view_transform
        original_exposure = scene.view_settings.exposure
        scene.view_settings.view_transform = "Standard"
        scene.view_settings.exposure = 0

        def emission_material(name, color_socket):
            mat = bpy.data.materials.new(name)
            mat.use_nodes = True
            nodes = mat.node_tree.nodes
            nodes.clear()
            links = mat.node_tree.links
            emission = nodes.new("ShaderNodeEmission")
            output_node = nodes.new("ShaderNodeOutputMaterial")
            links.new(color_socket(nodes, links), emission.inputs["Color"])
            links.new(emission.outputs["Emission"], output_node.inputs["Surface"])
            return mat

        def normal_color(nodes, links):
            geometry = nodes.new("ShaderNodeNewGeometry")
            multiply = nodes.new("ShaderNodeVectorMath")
            multiply.operation = "SCALE"
            multiply.inputs[3].default_value = 0.5
            add = nodes.new("ShaderNodeVectorMath")
            add.operation = "ADD"
            add.inputs[1].default_value = (0.5, 0.5, 0.5)
            links.new(geometry.outputs["Normal"], multiply.inputs[0])
            links.new(multiply.outputs["Vector"], add.inputs[0])
            return add.outputs["Vector"]

        def depth_color(nodes, links):
            camera_node = nodes.new("ShaderNodeCameraData")
            map_range = nodes.new("ShaderNodeMapRange")
            map_range.inputs[1].default_value = max(0, camera_distance - span * 1.25)
            map_range.inputs[2].default_value = camera_distance + span * 1.25
            links.new(camera_node.outputs["View Z Depth"], map_range.inputs[0])
            return map_range.outputs["Result"]

        try:
            for label, source in (("Normal", normal_color), ("Depth", depth_color)):
                layer.material_override = emission_material("ICON_" + label + "_Pass", source)
                scene.render.filepath = os.path.join(pass_dir, label + ".png")
                bpy.ops.render.render(scene=scene.name, write_still=True)
                print("ICON_GEOMETRY_PASS", label, scene.render.filepath)
        finally:
            layer.material_override = original_override
            scene.render.filepath = output
            scene.view_settings.view_transform = original_transform
            scene.view_settings.exposure = original_exposure


if __name__ == "__main__":
    main()
