"""Create a saved editable single-model master matching the fixed flour native export."""
import argparse
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT/"project/tools/blender"))
sys.path.insert(0, str(ROOT/"project/tools/art"))
from ae_asset_render_blender import Builder
from csc_scene_validation import validate_current_scene
from storage_pivot_trial_blender import disable_repairs

MILL = "CSC_BAKERS_Water_Mill"


def prepare(out):
    import io_export_cn6 as cn6
    disable_repairs()
    plan = json.loads((out/"plan.json").read_text())
    bpy.ops.wm.open_mainfile(filepath=str(out/"before-sources"/(MILL+".blend")),
                            load_ui=False, use_scripts=False)
    rig = bpy.data.objects[MILL]
    original = [bpy.data.objects[n] for n in plan["original_meshes"]]
    # Retain the exact existing skeleton conversion, including its bone convention.
    cn6.csc_do_export_selected(str(out/"source-header.cn6"), [rig, *original])
    for ob in list(bpy.data.objects):
        if ob != rig:
            bpy.data.objects.remove(ob, do_unlink=True)
    for mesh in list(bpy.data.meshes):
        if not mesh.users:
            bpy.data.meshes.remove(mesh)
    for mat in list(bpy.data.materials):
        bpy.data.materials.remove(mat, do_unlink=True)
    for image in list(bpy.data.images):
        if not image.users:
            bpy.data.images.remove(image)
    export = bpy.context.scene
    export.name = "Export"
    source_dir = out/"sources"
    source_dir.mkdir(exist_ok=True)
    materials = json.loads((out/"materials.json").read_text())
    builder = Builder(dict(output=str(source_dir), materials=materials["materials"], warnings=[]), "icon")
    export.name = "Export"
    if "placement_authority" in export:
        del export["placement_authority"]
    export["geometry_authority"] = "Native mill geometry plus saved AE flour placements, 2026-10-20. AE owns remaining attachments."
    export["fixed_flour_variant_visibility"] = "CSC_Fixed_Mill_Flour_Variant_2 is visible only in Water_Mill_2; cart loads remain attachments."
    raw = json.loads((out/"merged-native.json").read_text())
    meshes = []
    for entry in raw["meshes"]:
        vertices = entry["vertices"]
        mesh = bpy.data.meshes.new(entry["name"])
        mesh.from_pydata([v["position"] for v in vertices], [], [t[:3] for t in entry["triangles"]])
        mesh.update()
        for i, key in enumerate(("uv","uv2","uv3"),1):
            layer = mesh.uv_layers.new(name=f"UV{i}")
            for loop in mesh.loops:
                u,v = vertices[loop.vertex_index][key]
                layer.data[loop.index].uv = (u,1-v)
        mesh.polygons.foreach_set("use_smooth", [True]*len(mesh.polygons))
        mesh.normals_split_custom_set([vertices[l.vertex_index]["normal"] for l in mesh.loops])
        for group in plan["groups"][entry["name"]]:
            mat = builder.material(materials["keys"][group],3)
            mat.name = group
            assert mat.name == group, (mat.name, group)
            mesh.materials.append(mat)
        assert len(mesh.materials) == 1
        ob = bpy.data.objects.new(entry["name"],mesh)
        export.collection.objects.link(ob)
        ob.parent = rig
        ob.matrix_parent_inverse = Matrix.Identity(4)
        ob.matrix_basis = Matrix.Identity(4)
        ob.vertex_groups.new(name="Bone").add(list(range(len(vertices))),1,"REPLACE")
        ob.modifiers.new("Armature", "ARMATURE").object = rig
        ob["export_role"] = "fixed_geometry" if entry["name"].startswith("CSC_Fixed_") else "building_geometry"
        ob["fixed_flour_provenance"] = "Saved AST placement and installed native geometry" if entry["name"].startswith("CSC_Fixed_") else "Existing native Water Mill geometry"
        meshes.append(ob)
    for image in builder.images.values():
        if image.packed_file:
            image.unpack(method="REMOVE")
        image.filepath = "//textures/"+Path(image.filepath).name
    review = bpy.data.scenes.new("Review")
    for ob in [rig, *meshes]:
        review.collection.objects.link(ob)
    world = bpy.data.worlds.new("CSC_World")
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (.7,.8,1,1)
    bg.inputs["Strength"].default_value = .65
    for sc, view, exposure in ((export,"AgX",.35),(review,"Standard",-.1)):
        sc.world = world
        sc.render.engine = "CYCLES"
        sc.view_settings.view_transform = view
        sc.view_settings.exposure = exposure
        sc.view_settings.gamma = 1
    light = bpy.data.objects.new("Review_Key",bpy.data.lights.new("Review_Key","SUN"))
    review.collection.objects.link(light)
    light.data.energy = 3.2
    light.data.color = (1,.92,.8)
    light.data.angle = math.radians(6)
    light.data.use_shadow = True
    light.rotation_euler = (math.radians(25),math.radians(-30),math.radians(-25))
    camera = bpy.data.objects.new("Review_Camera",bpy.data.cameras.new("Review_Camera"))
    review.collection.objects.link(camera)
    camera.location = Vector((-40,0,20))+Vector((150,-220,180))
    camera.rotation_euler = (Vector((-40,0,20))-camera.location).to_track_quat("-Z","Y").to_euler()
    camera.data.type = "ORTHO"
    camera.data.ortho_scale = 200
    review.camera = camera
    bpy.context.window.scene = export
    target = source_dir/(MILL+".blend")
    bpy.ops.wm.save_as_mainfile(filepath=str(target), relative_remap=False)
    bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False,use_scripts=False)
    report = validate_current_scene()
    (out/"source-validation.json").write_text(json.dumps(report,indent=2))
    assert report["error_count"] == 0, report["findings"]
    checks = {}
    for entry in raw["meshes"]:
        ob = bpy.data.objects[entry["name"]]
        assert [m.name for m in ob.data.materials] == plan["groups"][entry["name"]]
        err = max((ob.matrix_world @ v.co-Vector(r["position"])).length
                  for v,r in zip(ob.data.vertices,entry["vertices"]))
        assert err < .0001
        checks[entry["name"]] = err
    (out/"source-geometry-validation.json").write_text(json.dumps(checks,indent=2))
    print("SAVED_SOURCE_PASS",len(checks),"meshes;",report["warning_count"],"advisory warnings")


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",required=True,type=Path)
    args=p.parse_args(sys.argv[sys.argv.index("--")+1:])
    prepare(args.output)
