"""Run in background Blender: verify fixed class cameras ignore prop layout.

blender --background --factory-startup --python-exit-code 1 --python THIS_FILE
No renders or source assets are written. Tests exercise the actual camera setup.
"""
import json
import copy
from pathlib import Path
import sys

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Vector

sys.path.insert(0, str(Path(__file__).parent))
from ae_asset_render_blender import Builder
from render_ae_asset import PRESETS, CAMERA_PRESETS


def cube(name, center, size):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata([(x*size, y*size, z*size) for x in (-1,1) for y in (-1,1) for z in (-1,1)], [], [])
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.location = center
    return obj


def snapshot(builder, landmarks):
    report = builder.setup()
    scene = bpy.context.scene
    camera = scene.camera
    registration = (tuple(tuple(row) for row in camera.matrix_world), camera.data.lens,
                    camera.data.ortho_scale, camera.data.sensor_width, camera.data.shift_x,
                    camera.data.shift_y, scene.render.resolution_x, scene.render.resolution_y)
    projected = [tuple(world_to_camera_view(scene, camera, point)) for point in landmarks]
    return registration, projected, report


def check(level, fixed, mode):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    settings = {"presets": PRESETS, "samples": 1, "resolution": 1024, "camera_class": level or "auto"}
    if fixed:
        settings["fixed_camera"] = fixed
    builder = Builder({"settings": settings, "warnings": [], "output": str(Path(__file__).parent)}, mode)
    target = Vector(fixed["target"] if fixed else (0,0,0))
    building = cube("Building", target, 20)
    prop = cube("Prop", target + Vector((30,-20,0)), 5)
    builder.objects = [building, prop]
    bpy.context.view_layer.update()
    landmarks = [building.matrix_world @ v.co for v in building.data.vertices]
    before = snapshot(builder, landmarks)
    prop.location += Vector((1000,-800,400))
    prop.scale = (4,4,4)
    builder.objects.append(cube("NewProp", target + Vector((-600,200,0)), 100))
    bpy.context.view_layer.update()
    after = snapshot(builder, landmarks)
    if fixed:
        assert before[0] == after[0], (level,mode,"camera/framing changed")
        assert before[1] == after[1], (level,mode,"main building pixel registration changed")
        assert before[2]["bounds"] != after[2]["bounds"], "Fixture did not change bounds"
    else:
        assert before[0] != after[0] and before[1] != after[1], "Legacy framing control should move"
    return {"class": level or "auto", "mode": mode, "registration_stable": bool(fixed),
            "main_building_landmarks_checked": len(landmarks)}


profiles = json.loads(CAMERA_PRESETS.read_text())["classes"]

# Compare actual projections with Henno's manual 1024px-canvas calibrations.
# The offsets below use positive X=right, positive Y=up (image Y is opposite).
for level, zoom, right, up in (("L1",1050/1024,0,35), ("L2",1,0,47), ("L3",1,41,71)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    baseline = copy.deepcopy(profiles[level])
    baseline["icon"]["lens"] = 37.0
    baseline["icon"]["shift_x"] = baseline["icon"]["shift_y"] = 0.0
    settings = {"presets": PRESETS, "samples": 1, "resolution": 1024,
                "camera_class": level, "fixed_camera": baseline}
    builder = Builder({"settings": settings, "warnings": [], "output": str(Path(__file__).parent)}, "icon")
    building = cube("CalibrationBuilding", Vector(baseline["target"]), 20)
    builder.objects = [building]
    bpy.context.view_layer.update()
    landmarks = [building.matrix_world @ vertex.co for vertex in building.data.vertices]
    before = snapshot(builder, landmarks)
    settings["fixed_camera"] = profiles[level]
    after = snapshot(builder, landmarks)
    maximum_pixel_error = 0.0
    for old, new in zip(before[1], after[1]):
        expected = (0.5 + zoom*(old[0]-0.5) + right/1024,
                    0.5 + zoom*(old[1]-0.5) + up/1024)
        maximum_pixel_error = max(maximum_pixel_error, *(abs(new[i]-expected[i])*1024 for i in (0,1)))
    assert maximum_pixel_error < 0.001, (level, maximum_pixel_error)
    assert before[0][0] == after[0][0], "Camera pose changed during pixel calibration"
    print("ICON_CALIBRATION", json.dumps({"class": level, "zoom": zoom, "right_pixels": right,
                                          "upward_pixels": up, "maximum_pixel_error": maximum_pixel_error}))

results = [check(level, profile, mode) for level, profile in profiles.items() for mode in ("icon","sv")]
results += [check(None, None, mode) for mode in ("icon","sv")]
print("CAMERA_REGISTRATION_TESTS", json.dumps(results))
