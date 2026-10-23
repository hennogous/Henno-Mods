"""Extract a local animated donkey child from the installed delivery; no source mutations."""
import argparse
import json
import math
from pathlib import Path
import subprocess
import sys

import bpy
from mathutils import Matrix, Vector
from civ6_animation import core, backend
import io_export_cn6 as cn6

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "Civ Supply Chains"
NAME = "CSC_TRIAL_Delivery_Donkey"
NEXUS = r"C:\Program Files (x86)\CivNexus6_Release-1.3.3\CivNexus6"
BRIDGE = Path(r"C:\Users\Shadow\Desktop\Codex\CSC_Storage_L\delivery-01\bridge\CN6ToFGX.exe")
C = Matrix(((0, 1, 0, 0), (0, 0, 1, 0), (1, 0, 0, 0), (0, 0, 0, 1)))
SAMPLES = (1, 113, 301, 601, 811, 841, 901, 1081, 1261, 1321, 1411, 1561, 1741, 1891, 2041)


def vertices(obj):
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = evaluated.to_mesh()
    result = [evaluated.matrix_world @ v.co for v in mesh.vertices]
    evaluated.to_mesh_clear()
    return result


def run(out):
    out.mkdir(parents=True, exist_ok=True)
    for event in ("load_post", "depsgraph_update_post"):
        for handler in list(getattr(bpy.app.handlers, event)):
            if "csc_scene" in getattr(handler, "__module__", ""):
                getattr(bpy.app.handlers, event).remove(handler)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Export"
    model = MOD/"Geometries/CSC_ALL_Delivery_Pivot.fgx"
    clip = MOD/"Animations/CSC_ALL_Delivery_Pivot.fgx"
    backend.run(NEXUS, "extract", model, clip, out/"parent-sampled", 30, 0, 0)
    sample = core.parse_na2(out/"parent-sampled/clip.na2")[0]
    paths = [core.world_matrix(v) for v in sample["tracks"]["DonkeyPath"]]
    rig, _ = core.import_native(clip, model, NEXUS)
    mesh = next(o for o in scene.objects if o.type == "MESH" and "Donkey" in o.name)
    expected = {}
    for f in SAMPLES:
        scene.frame_set(f)
        expected[f] = vertices(mesh)
    # Native attachment axes differ from Blender bone display axes by C.
    bind_path = rig.matrix_world @ rig.data.bones["DonkeyPath"].matrix_local @ C.inverted()
    inverse_bind = bind_path.inverted()
    original_normals = [normal.vector.copy() for normal in mesh.data.corner_normals]
    bone_names = [b.name for b in rig.data.bones if b.name.startswith("Donkey_")]
    assert len(bone_names) == 24, bone_names
    mesh_world = mesh.matrix_world.copy()
    mesh.parent = None
    mesh.matrix_world = Matrix.Identity(4)
    mesh.data.transform(inverse_bind @ mesh_world)
    normal_transform = (inverse_bind @ mesh_world).to_3x3().inverted().transposed()
    mesh.data.normals_split_custom_set([(normal_transform @ normal).normalized() for normal in original_normals])
    # The importer stores native tangent frames for its companion exporter.
    if "originalTangentsBinormals" in mesh.data:
        frames = mesh.data["originalTangentsBinormals"]
        for key in frames.keys():
            values = list(frames[key])
            frames[key] = [v for i in (0, 3, 6) for v in normal_transform @ Vector(values[i:i+3])]
    rig.animation_data_clear()
    rig.matrix_world = Matrix.Identity(4)
    rig.data.transform(inverse_bind)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for bone in list(rig.data.edit_bones):
        if bone.name not in bone_names:
            rig.data.edit_bones.remove(bone)
    bpy.ops.object.mode_set(mode="OBJECT")
    rig.name = NAME
    rig.data.name = NAME
    rig["civ6_root_name"] = NAME
    mesh.name = NAME+"_Mesh"
    mesh.parent = rig
    mesh.matrix_parent_inverse = Matrix.Identity(4)
    mesh.matrix_basis = Matrix.Identity(4)
    mesh["export_role"] = "building_geometry"
    mesh["source_asset_id"] = NAME
    mesh["derived_from"] = "Existing approved CSC delivery donkey/sled, extracted without changing topology or UVs"
    for obj in list(bpy.data.objects):
        if obj not in (rig, mesh):
            bpy.data.objects.remove(obj, do_unlink=True)
    for modifier in mesh.modifiers:
        if modifier.type == "ARMATURE":
            modifier.object = rig
    rows = ["FrameSets: 1", f"FrameCount: {sample['count']}", "FirstFrame: 1",
            f"LastFrame: {sample['count']}", "FPS: 30", f"Bones: {len(bone_names)+1}", NAME]
    rows += ["1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"] * sample["count"]
    for name in bone_names:
        rows.append(name)
        for p, values in zip(paths, sample["tracks"][name]):
            local = p.inverted() @ core.world_matrix(values)
            rows.append(" ".join(f"{v:.10g}" for v in core.to_na2(local, bone=False)))
    local_clip = out/"donkey-local.na2"
    local_clip.write_text("\n".join(rows)+"\n")
    core.import_na2(local_clip, rig, action_name="Donkey_Local_68s")
    errors = {}
    for f in SAMPLES:
        scene.frame_set(f)
        actual = [paths[f-1] @ p for p in vertices(mesh)]
        assert len(actual) == len(expected[f])
        errors[f] = max((a-b).length for a, b in zip(actual, expected[f]))
    assert max(errors.values()) < .002, errors
    # Dedicated editable child master: only its mesh and rig export.
    review = bpy.data.scenes.new("Review")
    review.collection.objects.link(rig)
    review.collection.objects.link(mesh)
    for sc in (scene, review):
        sc.render.engine = "CYCLES"
        sc.render.fps = 30
        sc.frame_start, sc.frame_end = 1, 2041
        sc.world = bpy.data.worlds.new(sc.name+"_World")
        sc.world.use_nodes = True
        bg = sc.world.node_tree.nodes.get("Background")
        bg.inputs["Color"].default_value = (.7, .8, 1, 1)
        bg.inputs["Strength"].default_value = .65
        sc.view_settings.view_transform = "AgX" if sc == scene else "Standard"
        sc.view_settings.exposure = .35 if sc == scene else -.1
        sc.view_settings.gamma = 1
    light = bpy.data.objects.new("Review_Key", bpy.data.lights.new("Review_Key", "SUN"))
    review.collection.objects.link(light)
    light.data.energy, light.data.color, light.data.angle = 3.2, (1, .92, .8), math.radians(6)
    light.data.use_shadow = True
    light.rotation_euler = (.4, -.5, -.4)
    scene.frame_set(811)
    master_path = out/(NAME+".blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(master_path))
    stage = out/"staged"
    geo = stage/"Geometries"
    anim = stage/"Animations"
    geo.mkdir(parents=True, exist_ok=True)
    anim.mkdir(parents=True, exist_ok=True)
    cn6.csc_do_export_selected(str(geo/(NAME+".cn6")), [rig, mesh])
    result = subprocess.run([str(BRIDGE), str(geo/(NAME+".cn6")), str(geo/(NAME+".fgx")), "2", "--skinned"],
                            cwd=BRIDGE.parent, capture_output=True, text=True)
    (out/"geometry-conversion.log").write_text(result.stdout+result.stderr)
    assert result.returncode == 0, result.stdout+result.stderr
    cn6.csc_write_geo(str(geo/(NAME+".geo")), NAME, str(geo/(NAME+".cn6")), "LandmarkModel")
    descriptor = geo/(NAME+".geo")
    descriptor.write_text(descriptor.read_text().replace("AssetObjects:", "AssetObjects.."))
    report = core.export_animation(anim/(NAME+".fgx"), rig, NEXUS, 1, 2041, include_model=False, overwrite=True)
    assert abs(report["duration"]-68) < .001, report
    check = bpy.data.scenes.new("Native_Check")
    bpy.context.window.scene = check
    converted, _ = core.import_native(anim/(NAME+".fgx"), geo/(NAME+".fgx"), NEXUS)
    converted_mesh = next(o for o in check.objects if o.type == "MESH")
    native_errors = {}
    for f in SAMPLES:
        check.frame_set(f)
        actual = [paths[f-1] @ p for p in vertices(converted_mesh)]
        # Vertex splitting/order can change in conversion; compare the geometric sets.
        native_errors[f] = max(min((a-b).length for b in actual) for a in expected[f])
    assert max(native_errors.values()) < .4, native_errors
    # Render actual reimported native child restored onto the original route.
    check.render.engine = "BLENDER_WORKBENCH"
    check.display.shading.light = "STUDIO"
    check.display.shading.color_type = "SINGLE"
    check.display.shading.single_color = (.55, .43, .3)
    check.display.shading.show_cavity = True
    check.world = bpy.data.worlds.new("CheckWorld")
    check.world.color = (.15, .15, .15)
    camera = bpy.data.objects.new("CheckCamera", bpy.data.cameras.new("CheckCamera"))
    check.collection.objects.link(camera)
    check.camera = camera
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 100
    check.render.resolution_x, check.render.resolution_y, check.render.resolution_percentage = 1000, 650, 100
    # Snapshot evaluated vertices: the imported rig has an identity object track,
    # which would reset an ad hoc object placement when the renderer evaluates.
    converted_mesh.hide_render = True
    for f in (301, 811, 1741):
        check.frame_set(f)
        bpy.context.view_layer.update()
        evaluated = converted_mesh.evaluated_get(bpy.context.evaluated_depsgraph_get())
        posed = evaluated.to_mesh()
        points = [paths[f-1] @ evaluated.matrix_world @ v.co for v in posed.vertices]
        faces = [list(p.vertices) for p in posed.polygons]
        data = bpy.data.meshes.new("NativePose")
        data.from_pydata(points, [], faces)
        data.update()
        evaluated.to_mesh_clear()
        snapshot = bpy.data.objects.new("NativePose", data)
        check.collection.objects.link(snapshot)
        center = sum(points, Vector())/len(points)
        camera.location = center+Vector((85, -100, 60))
        camera.rotation_euler = (center-camera.location).to_track_quat("-Z", "Y").to_euler()
        check.render.filepath = str(out/f"native-donkey-{f}.png")
        bpy.ops.render.render(write_still=True)
        bpy.data.objects.remove(snapshot, do_unlink=True)
    # Validate the saved single-model handoff, not the disposable check scene.
    vertex_count = len(mesh.data.vertices)
    bpy.ops.wm.open_mainfile(filepath=str(master_path), load_ui=False, use_scripts=False)
    sys.path.insert(0, str(ROOT/"project/tools/blender"))
    from csc_scene_validation import validate_current_scene
    validation = validate_current_scene()
    (out/"source-validation.json").write_text(json.dumps(validation, indent=2))
    summary = dict(source=str(master_path), source_errors=errors, native_errors=native_errors,
                   clip=report, path_scale_range=[min(p.to_scale().x for p in paths), max(p.to_scale().x for p in paths)],
                   bind_path=[list(row) for row in bind_path],
                   vertices=vertex_count,
                   validator_findings=validation["findings"], game_verified=False)
    (out/"split-check.json").write_text(json.dumps(summary, indent=2))
    print("DONKEY_SPLIT_PASS", max(errors.values()), max(native_errors.values()))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    run(args.output)
