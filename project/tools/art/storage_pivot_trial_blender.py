"""Inspect and prepare the October 2026 storage pivot migration in background Blender."""
import argparse
import hashlib
import json
import math
from collections import defaultdict
import shutil
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[3]
SOURCE = Path(r"C:\Users\Shadow\Desktop\Working Files\3D Art\Storage\Storage_L")
NAMES = ("CSC_Storage_L", "CSC_Storage_L_CON+PIL", "CSC_Storage_L_PIL_Decals")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def disable_repairs():
    for event in ("load_post", "depsgraph_update_post"):
        for callback in list(getattr(bpy.app.handlers, event)):
            if callback.__module__.rsplit(".", 1)[-1] == "csc_scene_tools":
                getattr(bpy.app.handlers, event).remove(callback)


def bounds(points):
    return [[min(p[i] for p in points) for i in range(3)],
            [max(p[i] for p in points) for i in range(3)]] if points else None


def inventory(path):
    bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
    if "Export" in bpy.data.scenes:
        bpy.context.window.scene = bpy.data.scenes["Export"]
    bpy.context.scene.frame_set(1)
    rows = []
    for obj in bpy.data.objects:
        row = dict(name=obj.name, type=obj.type, parent=obj.parent.name if obj.parent else None,
                   parent_type=obj.parent_type, parent_bone=obj.parent_bone,
                   matrix=[list(r) for r in obj.matrix_world],
                   basis=[list(r) for r in obj.matrix_basis],
                   props=dict(obj.items()), scenes=[s.name for s in obj.users_scene])
        if obj.type == "MESH":
            directions = defaultdict(float)
            for poly in obj.data.polygons:
                n = poly.normal
                if abs(n.z) < 0.05:
                    directions[round(math.degrees(math.atan2(n.y, n.x)) % 90, 3)] += poly.area
            row.update(vertices=len(obj.data.vertices), polygons=len(obj.data.polygons),
                       bounds=bounds([obj.matrix_world @ v.co for v in obj.data.vertices]),
                       local_bounds=bounds([v.co for v in obj.data.vertices]),
                       materials=[m.name if m else None for m in obj.data.materials],
                       uv_layers=[u.name for u in obj.data.uv_layers],
                       modifiers=[(m.name, m.type) for m in obj.modifiers],
                       wall_directions=sorted(directions.items(), key=lambda x: -x[1])[:10])
        elif obj.type == "ARMATURE":
            row["bones"] = [dict(name=b.name, parent=b.parent.name if b.parent else None,
                                 matrix=[list(r) for r in b.matrix_local]) for b in obj.data.bones]
            row["action"] = obj.animation_data.action.name if obj.animation_data and obj.animation_data.action else None
        rows.append(row)
    return dict(source=str(path), sha256=digest(path), objects=rows,
                scenes=[dict(name=s.name, props=dict(s.items())) for s in bpy.data.scenes])


def plan(out):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE / "CSC_Storage_L.blend"), load_ui=False, use_scripts=False)
    obj = bpy.data.objects["CSC_Storage_L_Bldg"]
    wall = max((p for p in obj.data.polygons if abs(p.normal.z) < .01), key=lambda p:p.area)
    angle = math.atan2(wall.normal.y, wall.normal.x) % (math.pi / 2)
    unrotate = Matrix.Rotation(-angle, 4, "Z")
    low = min(v.co.z for v in obj.data.vertices)
    foundation = [p for p in obj.data.polygons
                  if abs(p.normal.z) > .99 and all(abs(obj.data.vertices[i].co.z-low) < .01 for i in p.vertices)]
    points = [unrotate @ v.co for v in obj.data.vertices if abs(v.co.z-low) < .01]
    box = bounds(points)
    center = unrotate.inverted() @ Vector([(box[0][i]+box[1][i])/2 for i in range(3)])
    center.z = 0
    hit, location, normal, index = obj.ray_cast(center + Vector((0, 0, 1000)), Vector((0, 0, -1)))
    assert hit and location.z > 0, "Proposed pivot is outside the building footprint"
    placement = Matrix.Translation(center) @ Matrix.Rotation(angle, 4, "Z")
    data = dict(pivot_policy="Centre of axis-aligned foundation footprint after removing building rotation; ground Z=0; roof ray confirms inside building",
                translation_blender=list(center), rotation_blender_degrees=math.degrees(angle),
                attachment_position=[v / 10 for v in center],
                attachment_rotation=[0, 0, -angle],
                local_to_district=[list(r) for r in placement],
                district_to_local=[list(r) for r in placement.inverted()],
                foundation_vertex_count=len(points), roof_ray_hit=list(location))
    (out / "transform.json").write_text(json.dumps(data, indent=2))
    print("TRANSFORM", json.dumps(data))


def stage(out):
    import io_export_cn6 as cn6
    data = json.loads((out / "transform.json").read_text())
    transform = Matrix(data["district_to_local"])
    saved = out / "sources"
    native = out / "staged/Geometries"
    saved.mkdir(exist_ok=True)
    native.mkdir(parents=True, exist_ok=True)
    report = {}
    for name in NAMES:
        path = SOURCE / (name + ".blend")
        backup = out / "before-sources" / path.name
        backup.parent.mkdir(exist_ok=True)
        if not backup.exists():
            shutil.copy2(path, backup)
        bpy.ops.wm.open_mainfile(filepath=str(backup), load_ui=False, use_scripts=False)
        for image in bpy.data.images:
            if image.source == "FILE":
                # Resolve // paths against the original file, not the backup location.
                original = image.filepath
                if original.startswith("//"):
                    image.filepath = str((path.parent / original[2:]).resolve())
        before = {}
        for obj in bpy.data.objects:
            if obj.type == "MESH":
                assert max(abs(obj.matrix_world[i][j] - Matrix.Identity(4)[i][j])
                           for i in range(4) for j in range(4)) < 1e-5, obj.name
                mesh = obj.data
                normals = [transform.to_3x3() @ n.vector for n in mesh.corner_normals] if mesh.has_custom_normals else None
                before[obj.name] = [v.co.copy() for v in mesh.vertices]
                mesh.transform(transform)
                mesh.update()
                if normals:
                    mesh.normals_split_custom_set(normals)
                obj["storage_pivot_rebase"] = "2026-10-20"
            elif obj.type in ("CAMERA", "LIGHT", "EMPTY"):
                obj.matrix_world = transform @ obj.matrix_world
        for sc in bpy.data.scenes:
            sc["storage_local_to_district"] = json.dumps(data["local_to_district"])
        # The runtime's five named decals are the saved Review geometry.
        if name.endswith("_PIL_Decals"):
            export = bpy.data.scenes["Export"]
            for obj in list(export.objects):
                for collection in list(obj.users_collection):
                    if collection.name in {c.name for c in export.collection.children_recursive} or collection == export.collection:
                        collection.objects.unlink(obj)
            rig = bpy.data.objects[name]
            export.collection.objects.link(rig)
            for obj in bpy.data.objects:
                if obj.type == "MESH" and obj.parent == rig:
                    export.collection.objects.link(obj)
            # Keep the unpublished alternate layout in a separate source scene.
            alt = bpy.data.scenes.get("Alternate_Decal_Layout") or bpy.data.scenes.new("Alternate_Decal_Layout")
            for obj in bpy.data.objects:
                if obj.name == name+".001" or (obj.parent and obj.parent.name == name+".001"):
                    if obj.name not in alt.objects:
                        alt.collection.objects.link(obj)
        bpy.context.window.scene = bpy.data.scenes["Export"]
        rig = bpy.data.objects[name]
        target = saved / path.name
        bpy.ops.wm.save_as_mainfile(filepath=str(target))
        inverse = transform.inverted()
        error = max((inverse @ bpy.data.objects[n].data.vertices[i].co - point).length
                    for n, points in before.items() for i, point in enumerate(points))
        assert error < .0001, (name, error)
        geo_class = "DecalGeometry" if name.endswith("_PIL_Decals") else "LandmarkModel"
        result = cn6.csc_export_fgx_geo(name, str(native), geo_class, 3, True, rig)
        p = native / (name + ".geo")
        p.write_text(p.read_text().replace("AssetObjects:", "AssetObjects.."))
        report[name] = dict(source=str(target), restore_error_blender=error, exporter_result=result)
    (out / "stage-report.json").write_text(json.dumps(report, indent=2, default=str))
    print("STAGED_STORAGE", json.dumps(report, default=str))


def delivery_source(out):
    source = SOURCE / "Delivery/CSC_TAILORS_Storage_Delivery.blend"
    backup = out / "before-sources" / source.name
    if not backup.exists():
        shutil.copy2(source, backup)
    bpy.ops.wm.open_mainfile(filepath=str(backup), load_ui=False, use_scripts=False)
    bpy.context.window.scene = bpy.data.scenes["Export"]
    scene = bpy.context.scene
    transform = Matrix(json.loads((out/"transform.json").read_text())["district_to_local"])
    samples = (1,113,301,721,811,841,901,1081,1261,1321,1366,1411,1561,1741,2041)
    meshes = [o for o in scene.objects if o.type == "MESH"]
    rigs = [o for o in scene.objects if o.type == "ARMATURE"]

    def positions(obj):
        ob = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = ob.to_mesh()
        result = [ob.matrix_world@v.co for v in mesh.vertices]
        ob.to_mesh_clear()
        return result

    expected = {}
    for frame in samples:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        expected[frame] = dict(meshes={o.name:[transform@p for p in positions(o)] for o in meshes},
                              bones={o.name:{b.name:transform@o.matrix_world@b.matrix
                                             for b in o.pose.bones} for o in rigs})
    scene.frame_set(1)
    roots = [(o, o.matrix_basis.copy()) for o in bpy.data.objects if o.parent is None]
    frame_root = bpy.data.objects.new("CSC_Storage_Pivot_Frame", None)
    frame_root["storage_coordinate_frame"] = "Local storage ground pivot; district placement is stored in transform.json"
    frame_root["local_to_district"] = json.dumps(json.loads((out/"transform.json").read_text())["local_to_district"])
    for sc in bpy.data.scenes:
        sc.collection.objects.link(frame_root)
    frame_root.matrix_world = transform
    for obj, basis in roots:
        obj.parent = frame_root
        obj.matrix_parent_inverse = Matrix.Identity(4)
        obj.matrix_basis = basis
    errors = {}
    for frame in samples:
        scene.frame_set(frame)
        bpy.context.view_layer.update()
        vertex_error = max((a-b).length for o in meshes
                           for a,b in zip(expected[frame]["meshes"][o.name], positions(o)))
        bone_error = max(abs((o.matrix_world@b.matrix)[i][j]-expected[frame]["bones"][o.name][b.name][i][j])
                         for o in rigs for b in o.pose.bones for i in range(4) for j in range(4))
        assert vertex_error < .001 and bone_error < .001, (frame, vertex_error, bone_error)
        errors[frame] = dict(vertex_error=vertex_error, bone_matrix_error=bone_error)
    for image in bpy.data.images:
        if image.source == "FILE" and image.filepath.startswith("//"):
            image.filepath = str((source.parent/image.filepath[2:]).resolve())
    scene.frame_set(1)
    target = out/"sources"/source.name
    bpy.ops.wm.save_as_mainfile(filepath=str(target))
    (out/"delivery-source-check.json").write_text(json.dumps(dict(source=str(target), frames=errors), indent=2))
    print("DELIVERY_SOURCE_PASS", max(e["vertex_error"] for e in errors.values()))


def validate_sources(out):
    sys.path.insert(0, str(ROOT/"project/tools/blender"))
    from csc_scene_validation import validate_current_scene, format_report
    summary = {}
    for path in (out/"sources").glob("*.blend"):
        bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
        report = validate_current_scene()
        (out/(path.stem+"-validation.json")).write_text(json.dumps(report, indent=2))
        (out/(path.stem+"-validation.txt")).write_text(format_report(report))
        summary[path.stem] = dict(status=report["status"], errors=report["error_count"],
                                 findings=report["findings"])
    (out/"source-validation-summary.json").write_text(json.dumps(summary, indent=2))
    print("SOURCE_VALIDATION", json.dumps(summary))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=("inspect", "plan", "stage", "delivery-source", "validate"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:])
    disable_repairs()
    args.output.mkdir(parents=True, exist_ok=True)
    if args.phase == "plan":
        plan(args.output)
        return
    if args.phase == "stage":
        stage(args.output)
        return
    if args.phase == "delivery-source":
        delivery_source(args.output)
        return
    if args.phase == "validate":
        validate_sources(args.output)
        return
    report = {}
    for name, path in [(n, SOURCE / (n + ".blend")) for n in NAMES] + [
            ("delivery", SOURCE / "Delivery/CSC_TAILORS_Storage_Delivery.blend")]:
        report[name] = inventory(path)
        print(name, json.dumps([{k: r[k] for k in ("name", "type", "scenes", "bounds",
                                                       "wall_directions") if k in r}
                                for r in report[name]["objects"] if "Export" in r["scenes"]]))
    (args.output / "source-inventory.json").write_text(json.dumps(report, indent=2, default=str))
    print("STORAGE_PIVOT_INSPECTED", args.output)


if __name__ == "__main__":
    main()
