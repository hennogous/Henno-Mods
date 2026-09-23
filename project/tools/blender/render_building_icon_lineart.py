"""Render three Freestyle outline trials using the existing icon camera.

Run in background Blender with the source blend loaded, then pass OUTPUT_DIR.
Only the in-memory render scene is changed; no blend is saved.
"""
import argparse
import json
import math
from pathlib import Path
import runpy
import sys

import bpy
import bmesh
from bpy_extras.object_utils import world_to_camera_view


def main():
    argv = sys.argv[sys.argv.index("--") + 1:]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--elevation", type=float, default=23)
    parser.add_argument("--lens", type=float, default=37)
    args = parser.parse_args(argv)
    out = args.output_dir.resolve()
    out.mkdir(parents=True, exist_ok=True)

    # The same preparation code supplies camera, visibility, foundation clipping,
    # and color render. It is never recreated from a bounding box in image space.
    helper = Path(__file__).with_name("render_building_icon_input.py")
    sys.argv = [str(helper), "--", str(out / "Blender_Color.png"),
                "--elevation", str(args.elevation), "--lens", str(args.lens),
                "--view-transform", "Standard", "--exposure", "0",
                "--sun-energy", "3", "--world-strength", "0.8",
                "--world-color", "1", "1", "0.9"]
    runpy.run_path(str(helper), run_name="__main__")
    scene = bpy.data.scenes.get("Export") or bpy.context.scene
    if bpy.context.window:
        bpy.context.window.scene = scene
    layer = scene.view_layers[0]
    layer.update()

    architecture = bpy.data.collections.new("ICON_Line_Architecture")
    props = bpy.data.collections.new("ICON_Line_Props")
    scene.collection.children.link(architecture)
    scene.collection.children.link(props)
    groups = {"architecture": [], "props": []}
    marked_edges = {}
    projected_guides = {"architecture": [], "props": []}
    for obj in list(scene.objects):
        if obj.type != "MESH" or obj.hide_render:
            continue
        # Imported material/UV seams can duplicate vertices. Weld the temporary
        # line-pass copy so those seams are not interpreted as open mesh borders.
        # Freeze the evaluated pose on the temporary copy before classifying
        # creases. Source kit meshes can carry a Static_Bone armature modifier.
        layer.update()
        depsgraph = layer.depsgraph
        evaluated = obj.evaluated_get(depsgraph)
        world = evaluated.matrix_world.copy()
        posed_mesh = bpy.data.meshes.new_from_object(evaluated, depsgraph=depsgraph)
        obj.modifiers.clear()
        obj.data = posed_mesh
        obj.matrix_world = world
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        bmesh.ops.remove_doubles(bm, verts=list(bm.verts), dist=0.00001)
        bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
        bm.verts.index_update()
        # Tiny sliver faces in the kit can have a large normal angle while
        # visually belonging to one roof surface. Ignore those incidental folds.
        face_widths = {}
        for face in bm.faces:
            points = [world_to_camera_view(scene, scene.camera, obj.matrix_world @ v.co) for v in face.verts]
            pairs = list(zip(points, points[1:] + points[:1]))
            twice_area = abs(sum(a.x*b.y - b.x*a.y for a, b in pairs)) * 1024 * 1024
            longest = max(math.hypot(a.x-b.x, a.y-b.y) * 1024 for a, b in pairs)
            face_widths[face] = twice_area / max(longest, 0.00001)
        strong_edges = {tuple(sorted(v.index for v in edge.verts)) for edge in bm.edges
                        if len(edge.link_faces) == 2 and edge.calc_face_angle(0) >= math.radians(45)
                        and min(face_widths[f] for f in edge.link_faces) >= 4.0}
        bm.to_mesh(obj.data)
        bm.free()
        obj.data.update()
        marks = obj.data.attributes.get("freestyle_edge")
        if marks is None:
            marks = obj.data.attributes.new("freestyle_edge", "BOOLEAN", "EDGE")
        flags = [tuple(sorted(edge.vertices)) in strong_edges for edge in obj.data.edges]
        marks.data.foreach_set("value", flags)
        marked_edges[obj.name] = sum(flags)
        group_name = "architecture" if max(obj.dimensions) >= 45 else "props"
        (architecture if group_name == "architecture" else props).objects.link(obj)
        groups[group_name].append(obj.name)
        layer.update()
        for edge, marked in zip(obj.data.edges, flags):
            if group_name == "architecture" and not marked:
                continue
            coords = [world_to_camera_view(scene, scene.camera, obj.matrix_world @ obj.data.vertices[i].co)
                      for i in edge.vertices]
            if all(p.z > 0 for p in coords):
                projected_guides[group_name].append([coords[0].x * 1024, (1 - coords[0].y) * 1024,
                                                    coords[1].x * 1024, (1 - coords[1].y) * 1024])

    # Freestyle draws on a white unlit surface. This lets the compositor extract
    # antialiased line coverage without depending on the Blender 5 compositor API.
    white = bpy.data.materials.new("ICON_Line_White")
    white.use_nodes = True
    nodes = white.node_tree.nodes
    nodes.clear()
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Color"].default_value = (1, 1, 1, 1)
    output = nodes.new("ShaderNodeOutputMaterial")
    white.node_tree.links.new(emission.outputs[0], output.inputs["Surface"])
    layer.material_override = white
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0
    scene.view_settings.gamma = 1
    scene.render.use_freestyle = True
    fs = layer.freestyle_settings
    fs.mode = "EDITOR"
    fs.as_render_pass = False
    fs.use_view_map_cache = True
    fs.use_smoothness = False
    fs.crease_angle = math.radians(110)
    for line_set in list(fs.linesets):
        fs.linesets.remove(line_set)

    def add_set(name, collection, include_creases, min_length):
        line_set = fs.linesets.new(name)
        line_set.select_by_collection = True
        line_set.collection = collection
        line_set.collection_negation = "INCLUSIVE"
        line_set.select_by_visibility = True
        line_set.visibility = "VISIBLE"
        line_set.select_by_edge_types = True
        for prop in line_set.bl_rna.properties:
            if prop.identifier.startswith("select_") and not prop.identifier.startswith("select_by_"):
                setattr(line_set, prop.identifier, False)
        line_set.select_contour = True
        # Open seams in imported kit topology are not architectural divisions.
        line_set.select_border = False
        # Explicit marks use actual posed face angles. Automatic Freestyle
        # creases produced spurious strokes across this imported kit's roof.
        line_set.select_crease = False
        line_set.select_edge_mark = include_creases
        style = line_set.linestyle
        style.color = (0, 0, 0)
        style.alpha = 1
        style.caps = "ROUND"
        style.use_chaining = True
        style.use_length_min = True
        style.length_min = min_length
        return style

    major = add_set("Architecture", architecture, True, 18)
    minor = add_set("Prop contours", props, False, 25)
    strengths = [("Light", 3.5, 2.0), ("Medium", 5.5, 3.0), ("Bold", 8.0, 4.0)]
    for label, major_width, minor_width in strengths:
        major.thickness = major_width
        minor.thickness = minor_width
        scene.render.filepath = str(out / ("Freestyle_" + label + ".png"))
        bpy.ops.render.render(scene=scene.name, write_still=True)
        print("ICON_FREESTYLE", label, major_width, minor_width, flush=True)
    report = {"blend": bpy.data.filepath, "groups": groups,
              "camera_matrix_world": [list(row) for row in scene.camera.matrix_world],
              "lens": scene.camera.data.lens, "elevation": args.elevation,
              "crease_selection": "Marked posed-mesh edges with face-normal angle >=45 degrees",
              "minimum_adjacent_face_projected_width_px": 4.0,
              "marked_edge_counts": marked_edges, "strengths": strengths,
              "working_resolution": [1024, 1024]}
    (out / "render_manifest.json").write_text(json.dumps(report, indent=2))
    (out / "projected_edge_guides.json").write_text(json.dumps(projected_guides))


if __name__ == "__main__":
    main()
