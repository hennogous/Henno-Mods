"""Disposable saved-AST placement comparison for the storage pivot migration."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "project/tools/blender"))
from ae_asset_render_blender import Builder


def render(out, labels=("before", "staged"), focus=None):
    for label in labels:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        job = json.loads((out / "review" / label / "job.json").read_text())
        builder = Builder(job, "icon")

        def material(key, uvcount):
            if key not in builder.materials:
                mat = bpy.data.materials.new(key)
                digest = hashlib.sha256(key.encode()).digest()
                mat.diffuse_color = tuple(.3 + v / 510 for v in digest[:3]) + (1,)
                builder.materials[key] = mat
            return builder.materials[key]

        builder.material = material
        builder.assemble(job["root"], root=True)
        scene = bpy.context.scene
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "MATERIAL"
        scene.display.shading.show_shadows = True
        scene.display.shading.show_cavity = True
        scene.display.shading.background_type = "WORLD"
        scene.world = bpy.data.worlds.new("Review background")
        scene.world.color = (.14, .14, .14)
        camera = bpy.data.objects.new("ComparisonCamera", bpy.data.cameras.new("ComparisonCamera"))
        scene.collection.objects.link(camera)
        scene.camera = camera
        camera.data.type = "ORTHO"
        scene.render.resolution_x = 1200
        scene.render.resolution_y = 900
        scene.render.resolution_percentage = 100
        scene.render.image_settings.file_format = "PNG"
        for view, target, offset, scale in (
            ("district", (0, 0, 10), (300, -420, 520), 520),
            ("storage", focus or (-31.39355, 167.99298, 28), (160, -240, 240), 240),
            ("top", focus or (-31.39355, 167.99298, 0), (0, 0, 500), 240),
        ):
            camera.location = Vector(target) + Vector(offset)
            camera.rotation_euler = (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
            camera.data.ortho_scale = scale
            scene.render.filepath = str(out / "review" / label / (view + ".png"))
            bpy.ops.render.render(write_still=True)
        print("VISUAL_REVIEW", label, len(builder.objects), "mesh groups")


def validators(out):
    from csc_scene_validation import validate_current_scene
    reports = {}
    for label in ("before-sources", "sources"):
        reports[label] = {}
        for path in (out / label).glob("*.blend"):
            bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
            # Review light repair only; it does not affect exported geometry.
            if label == "sources" and path.stem == "CSC_Storage_L_PIL_Decals":
                scene = bpy.data.scenes.get("Review")
                light = scene.objects.get("Review_Key") if scene else None
                if scene and light is None:
                    light = bpy.data.objects.new("Review_Key", bpy.data.lights.new("Review_Key", "SUN"))
                    scene.collection.objects.link(light)
                    light.rotation_euler = (math.radians(25), math.radians(-30), math.radians(-25))
                if light:
                    light.data.type = "SUN"
                    light.data.energy = 3.2
                    light.data.color = (1, .92, .8)
                    light.data.angle = math.radians(6)
                    light.data.use_shadow = True
                    bpy.ops.wm.save_as_mainfile(filepath=str(path))
            report = validate_current_scene()
            reports[label][path.name] = report
            print("VALIDATION", label, path.name, report["error_count"])
    (out / "source-validation-comparison.json").write_text(json.dumps(reports, indent=2))


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("phase", choices=("render", "validators"))
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--labels", nargs="+", default=["before", "staged"])
    p.add_argument("--focus", nargs=3, type=float)
    args = p.parse_args(sys.argv[sys.argv.index("--") + 1:])
    # Prevent the authoring add-on from repairing or rewriting source files.
    for handlers in (bpy.app.handlers.load_post, bpy.app.handlers.depsgraph_update_post):
        for handler in list(handlers):
            if "csc_scene" in getattr(handler, "__module__", ""):
                handlers.remove(handler)
    if args.phase == "render":
        render(args.output, args.labels, args.focus)
    else:
        validators(args.output)
