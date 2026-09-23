"""Render a building blend and add its 1024px PNG to its stage XCF template.

Normal use (from regular Python):
    python create_building_icon_xcf.py BUILDING.blend 3

The XCF is saved beside BUILDING.blend. The render and run report are saved
under Desktop/Codex/art-work/<building>-icon-editable/. Neither the blend nor
the template is saved or changed. This script also runs inside GIMP 3 through
its internal batch mode; that mode is selected by CSC_ICON_XCF_BATCH.
"""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import traceback


SCRIPT = Path(__file__).resolve()
DEFAULT_BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")
DEFAULT_GIMP = Path(r"C:\Users\Shadow\AppData\Local\Programs\GIMP 3\bin\gimp-console-3.exe")
RENDER_SCRIPT = SCRIPT.parents[1] / "blender" / "render_building_icon_input.py"

# The icon skill currently records one calibrated perspective/light setup (the
# Tailor Stage 3 setup). Stage-specific camera overrides have not yet been
# measured, so all three stages use that setup with automatic scene-span framing.
CAMERA_BY_STAGE = {
    2: {"elevation": 23.0, "lens": 37.0},
    3: {"elevation": 23.0, "lens": 37.0},
    4: {"elevation": 23.0, "lens": 37.0},
}
TEMPLATE_BY_STAGE = {
    stage: SCRIPT.with_name(f"icon_template_stage_{stage}.xcf")
    for stage in CAMERA_BY_STAGE
}


def gimp_batch():
    """Run inside GIMP 3's python-fu-eval interpreter."""
    import gi
    gi.require_version("Gimp", "3.0")
    from gi.repository import Gimp, Gio

    template = Path(os.environ["CSC_ICON_XCF_TEMPLATE"])
    render = Path(os.environ["CSC_ICON_XCF_RENDER"])
    raw_render = Path(os.environ["CSC_ICON_XCF_RAW_RENDER"])
    output = Path(os.environ["CSC_ICON_XCF_OUTPUT"])
    report_path = Path(os.environ["CSC_ICON_XCF_REPORT"])
    pixel_shift_y = int(os.environ["CSC_ICON_XCF_PIXEL_SHIFT_Y"])
    report = {"template": str(template), "render": str(render),
              "raw_render": str(raw_render), "xcf": str(output)}

    def path_inventory(image):
        return [{"name": path.get_name(), "strokes": [
            {"points": list(path.stroke_get_points(sid)[1]),
             "closed": bool(path.stroke_get_points(sid)[2])}
            for sid in path.get_strokes()]}
            for path in image.get_paths()]

    try:
        image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,
                               Gio.File.new_for_path(str(template)))
        if image is None or (image.get_width(), image.get_height()) != (1024, 1024):
            raise ValueError("Template must be a readable 1024 x 1024 XCF")
        before = path_inventory(image)
        report["template_paths"] = [{"name": p["name"], "strokes": len(p["strokes"])}
                                    for p in before]
        report["template_layers"] = [layer.get_name() for layer in image.get_layers()]
        layer = Gimp.file_load_layer(Gimp.RunMode.NONINTERACTIVE, image,
                                     Gio.File.new_for_path(str(render)))
        if layer is None or (layer.get_width(), layer.get_height()) != (1024, 1024):
            raise ValueError("Blender render must be a readable 1024 x 1024 PNG")
        if not image.insert_layer(layer, None, 0):
            raise RuntimeError("GIMP could not insert the render layer")
        layer.set_name("Blender render | 1024 px")
        layer.set_offsets(0, 0)
        layer.set_visible(True)
        image.set_selected_layers([layer])
        if not Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image,
                              Gio.File.new_for_path(str(output))):
            raise RuntimeError("GIMP could not save the XCF")

        reopened = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,
                                  Gio.File.new_for_path(str(output)))
        if reopened is None:
            raise RuntimeError("GIMP could not reopen the saved XCF")
        after = path_inventory(reopened)
        if len(before) != len(after):
            raise RuntimeError("The template path count changed")
        max_delta = 0.0
        for left, right in zip(before, after):
            if left["name"] != right["name"] or len(left["strokes"]) != len(right["strokes"]):
                raise RuntimeError("A template path name or stroke count changed")
            for a, b in zip(left["strokes"], right["strokes"]):
                if a["closed"] != b["closed"] or len(a["points"]) != len(b["points"]):
                    raise RuntimeError("A template path changed structure")
                if a["points"]:
                    max_delta = max(max_delta,
                                    max(abs(x-y) for x, y in zip(a["points"], b["points"])))
        if max_delta >= .001:
            raise RuntimeError(f"Template path positions changed by {max_delta} px")
        layers = reopened.get_layers()
        if len(layers) != len(report["template_layers"]) + 1:
            raise RuntimeError("A template layer was lost")
        if layers[0].get_name() != "Blender render | 1024 px" or \
                (layers[0].get_width(), layers[0].get_height()) != (1024, 1024) or \
                tuple(layers[0].get_offsets()[1:]) != (0, 0):
            raise RuntimeError("The render layer changed on XCF save")
        if [item.get_name() for item in layers[1:]] != report["template_layers"]:
            raise RuntimeError("Template layer order or names changed")
        report.update({"saved_and_reopened": True, "path_count": len(after),
                       "max_path_coordinate_delta_px": max_delta,
                       "render_layer_offset": [0, 0],
                       "render_pixel_shift_y": pixel_shift_y,
                       "layers": [item.get_name() for item in layers]})
        print(json.dumps({"xcf": str(output), "path_count": len(after),
                          "saved_and_reopened": True}))
    except Exception:
        report["error"] = traceback.format_exc()
        print(report["error"])
    finally:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def run_logged(command, log, *, env=None, cwd=None):
    result = subprocess.run(command, text=True, capture_output=True,
                            errors="replace", env=env, cwd=cwd, check=False)
    log.write_text(result.stdout + result.stderr, encoding="utf-8")
    if result.returncode:
        tail = (result.stdout + result.stderr)[-2500:]
        raise RuntimeError(f"{command[0]} failed ({result.returncode}); see {log}\n{tail}")
    return result


def main():
    import argparse
    import hashlib

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("blend", type=Path, help="Source building .blend")
    parser.add_argument("stage", type=int, choices=tuple(CAMERA_BY_STAGE),
                        help="Building stage (2, 3 or 4); selects its XCF path template")
    parser.add_argument("--template", type=Path,
                        help="Override the stage's default XCF template")
    parser.add_argument("--blender", type=Path, default=DEFAULT_BLENDER)
    parser.add_argument("--gimp-console", type=Path, default=DEFAULT_GIMP)
    parser.add_argument("--render-png", type=Path,
                        help="Render destination; defaults to Desktop/Codex/art-work")
    parser.add_argument("--vertical-shift-percent", type=float, default=6.0,
                        help="Move pixels upward within the 1024px layer (default: 6%%)")
    args = parser.parse_args()
    if not 0 <= args.vertical_shift_percent <= 25:
        parser.error("--vertical-shift-percent must be between 0 and 25")

    blend = args.blend.resolve(strict=True)
    template_source = args.template or TEMPLATE_BY_STAGE[args.stage]
    if not template_source.is_file():
        parser.error(f"Stage {args.stage} template is missing: {template_source}")
    template = template_source.resolve(strict=True)
    blender = args.blender.resolve(strict=True)
    gimp = args.gimp_console.resolve(strict=True)
    if blend.suffix.lower() != ".blend" or template.suffix.lower() != ".xcf":
        parser.error("Expected a .blend source and .xcf template")
    if not RENDER_SCRIPT.is_file():
        raise FileNotFoundError(RENDER_SCRIPT)
    source_name = re.sub(r"_FINAL$", "", blend.stem, flags=re.IGNORECASE)
    quarter_prefix = re.match(r"^CSC_[^_]+_(.+)$", source_name, flags=re.IGNORECASE)
    building = quarter_prefix.group(1) if quarter_prefix else source_name
    building = re.sub(r"[^A-Za-z0-9_-]+", "_", building).strip("_")
    work = Path.home() / "Desktop" / "Codex" / "art-work" / f"{building.lower()}-icon-editable"
    work.mkdir(parents=True, exist_ok=True)
    render = (args.render_png or work / f"{building}_Blender_Render_1024.png").resolve()
    render.parent.mkdir(parents=True, exist_ok=True)
    output = blend.with_name(f"{blend.stem}_icon.xcf")
    if output.resolve() == template or render == template or render == blend:
        raise ValueError("Output paths must differ from the source blend and template")
    preset = CAMERA_BY_STAGE[args.stage]
    shift_y = -round(1024 * args.vertical_shift_percent / 100)
    in_layer_render = render.with_name(f"{render.stem}_InLayer.png")
    from uuid import uuid4
    pending_render = render.with_name(f".{render.stem}.{uuid4().hex}.pending.png")

    blender_command = [str(blender), "--background", str(blend),
                       "--python-exit-code", "1", "--python",
                       str(RENDER_SCRIPT), "--", str(pending_render),
                       "--elevation", str(preset["elevation"]),
                       "--lens", str(preset["lens"]),
                       "--view-transform", "Standard", "--exposure", "0",
                       "--world-strength", "0.8", "--world-color", "1", "1", "0.9",
                       "--sun-energy", "3"]
    blend_hash = hashlib.sha256(blend.read_bytes()).hexdigest()
    blender_log = work / f"{building}_Blender.log"
    try:
        run_logged(blender_command, blender_log)
        if not pending_render.is_file() or pending_render.stat().st_size == 0:
            raise RuntimeError(f"Blender did not produce the render PNG; see {blender_log}")
        pending_render.replace(render)
    finally:
        pending_render.unlink(missing_ok=True)
    from PIL import Image
    with Image.open(render) as source:
        rgba = source.convert("RGBA")
    if rgba.size != (1024, 1024):
        raise ValueError("Blender render must be 1024 x 1024")
    content_bounds = rgba.getchannel("A").getbbox()
    if content_bounds and content_bounds[1] + shift_y < 0:
        raise ValueError("The requested upward move would crop visible pixels")
    shifted = Image.new("RGBA", (1024, 1024), (0, 0, 0, 0))
    shifted.paste(rgba, (0, shift_y))
    shifted.save(in_layer_render)
    # The user may edit the template while Blender is rendering. Pin the
    # template only for the GIMP load/save phase that actually consumes it.
    template_hash = hashlib.sha256(template.read_bytes()).hexdigest()

    # Preserve an earlier result before a repeat run. The output location itself
    # stays exactly beside the source blend.
    backup = None
    if output.exists():
        from datetime import datetime
        backup_dir = work / "History" / datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_dir.mkdir(parents=True)
        backup = backup_dir / output.name
        shutil.copy2(output, backup)
    report_path = work / f"{building}_XCF_Report.json"
    report_path.unlink(missing_ok=True)
    env = os.environ.copy()
    env.update({"CSC_ICON_XCF_BATCH": "1", "CSC_ICON_XCF_TEMPLATE": str(template),
                "CSC_ICON_XCF_RENDER": str(in_layer_render),
                "CSC_ICON_XCF_RAW_RENDER": str(render),
                "CSC_ICON_XCF_OUTPUT": str(output),
                "CSC_ICON_XCF_REPORT": str(report_path),
                "CSC_ICON_XCF_PIXEL_SHIFT_Y": str(shift_y)})
    batch = f"exec(open({str(SCRIPT)!r}, encoding='utf-8').read())"
    gimp_command = [str(gimp), "--new-instance", "--no-interface", "--no-splash",
                    "--batch-interpreter=python-fu-eval", f"--batch={batch}", "--quit"]
    run_logged(gimp_command, work / f"{building}_Gimp.log", env=env, cwd=gimp.parent)
    if not report_path.is_file():
        raise RuntimeError("GIMP did not write a report")
    report = json.loads(report_path.read_text(encoding="utf-8"))
    if report.get("error") or not report.get("saved_and_reopened"):
        raise RuntimeError(f"GIMP could not verify the XCF: {report.get('error', report)}")
    if hashlib.sha256(template.read_bytes()).hexdigest() != template_hash:
        raise RuntimeError("The source template changed during the run")
    if hashlib.sha256(blend.read_bytes()).hexdigest() != blend_hash:
        raise RuntimeError("The source blend changed during the run")
    report.update({"blend": str(blend), "blend_sha256": blend_hash,
                   "template_sha256": template_hash, "stage": args.stage,
                   "camera": preset, "vertical_shift_percent": args.vertical_shift_percent,
                   "render_pixel_shift_y": shift_y,
                   "render_log": str(work / f"{building}_Blender.log"),
                   "gimp_log": str(work / f"{building}_Gimp.log"),
                   "previous_xcf_backup": str(backup) if backup else None})
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"xcf": str(output), "render": str(in_layer_render),
                      "raw_render": str(render),
                      "template_paths_preserved": report["path_count"],
                      "report": str(report_path)}, indent=2))


if os.environ.get("CSC_ICON_XCF_BATCH") == "1":
    gimp_batch()
elif __name__ == "__main__":
    main()
