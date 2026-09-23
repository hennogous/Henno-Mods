"""Match the accepted Tailor SV subject scale and save an editable painted XCF.

The accepted Tailor 1200 px PNG export occupies about 121 x 117 px at 256.
Scale each painted source's alpha bounds to the same approximate subject area
on a 1600 px editing canvas by default. The Blender render is retained as
the scene and provenance reference.
Brightness is stored as a live GIMP Brightness-Contrast filter on the layer.

Usage: python create_sv_painted_xcf.py PAINTED.png RENDER.png OUTPUT.xcf
"""

import argparse
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import traceback


SCRIPT = Path(__file__).resolve()
DEFAULT_GIMP = Path(r"C:\Users\Shadow\AppData\Local\Programs\GIMP 3\bin\gimp-console-3.exe")
SV_PIPELINE = SCRIPT.parents[1] / "comfyui" / "sv_pipeline"
TARGET_SUBJECT_GEOMEAN_256 = 119.0  # 22 Sep Tailor 1200 px export: 567 x 548 alpha bbox.


def alpha_bbox(image):
    return image.getchannel("A").point(lambda value: 255 if value > 8 else 0).getbbox()


def matched_art_size(painted, reference, canvas_size, final_canvas_size):
    """Size painted alpha to the accepted Tailor's visible subject area."""
    painted_box = alpha_bbox(painted)
    reference_box = alpha_bbox(reference)
    if painted_box is None or reference_box is None:
        raise ValueError("Painted image and reference render must both have visible alpha")
    painted_fraction = ((painted_box[2] - painted_box[0]) / painted.width *
                        (painted_box[3] - painted_box[1]) / painted.height)
    size = round(canvas_size / final_canvas_size *
                 TARGET_SUBJECT_GEOMEAN_256 / math.sqrt(painted_fraction))
    if not 0 < size <= canvas_size:
        raise ValueError(f"Calculated art size {size} does not fit {canvas_size} px canvas")
    return size, painted_box, reference_box


def gimp_batch():
    import gi

    gi.require_version("Gimp", "3.0")
    from gi.repository import Gimp, Gio

    prepared = Path(os.environ["CSC_SV_XCF_PREPARED"])
    output = Path(os.environ["CSC_SV_XCF_OUTPUT"])
    report_path = Path(os.environ["CSC_SV_XCF_REPORT"])
    brightness = int(os.environ["CSC_SV_XCF_BRIGHTNESS"])
    canvas_size = int(os.environ["CSC_SV_XCF_CANVAS_SIZE"])
    report = {"prepared": str(prepared), "xcf": str(output), "brightness_ui": brightness}
    try:
        image = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE, Gio.File.new_for_path(str(prepared)))
        if image is None or (image.get_width(), image.get_height()) != (canvas_size, canvas_size):
            raise RuntimeError(f"Could not load {canvas_size} px prepared image")
        layer = image.get_layers()[0]
        layer.set_name(f"Painted SV | centred {int(os.environ['CSC_SV_XCF_ART_SIZE'])} px art square")

        # GIMP's UI brightness slider is -127..127; GEGL stores it as -1..1.
        filt = Gimp.DrawableFilter.new(layer, "gimp:brightness-contrast",
                                       f"Brightness {brightness:+d}")
        if filt is None:
            raise RuntimeError("GIMP could not create Brightness-Contrast filter")
        config = filt.get_config()
        config.set_property("brightness", brightness / 127.0)
        config.set_property("contrast", 0.0)
        layer.append_filter(filt)
        filt.update()

        if not Gimp.file_save(Gimp.RunMode.NONINTERACTIVE, image,
                              Gio.File.new_for_path(str(output))):
            raise RuntimeError("GIMP could not save XCF")
        reopened = Gimp.file_load(Gimp.RunMode.NONINTERACTIVE,
                                  Gio.File.new_for_path(str(output)))
        if reopened is None or (reopened.get_width(), reopened.get_height()) != (canvas_size, canvas_size):
            raise RuntimeError(f"Saved XCF could not be reopened at {canvas_size} px")
        saved_layer = reopened.get_layers()[0]
        filters = saved_layer.get_filters()
        if not filters:
            raise RuntimeError("Brightness filter was not preserved in XCF")
        report.update({"saved_and_reopened": True,
                       "canvas": [canvas_size, canvas_size],
                       "layer": saved_layer.get_name(),
                       "filters": [item.get_name() for item in filters]})
        print(json.dumps(report))
    except Exception:
        report["error"] = traceback.format_exc()
        print(report["error"])
    finally:
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")


def main():
    from PIL import Image

    sys.path.insert(0, str(SV_PIPELINE))
    from sv_postprocess import CANVAS_SIZE, SPRITE_SIZE, OFFSET_X, OFFSET_Y

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Painted source PNG")
    parser.add_argument("reference_render", type=Path, help="Alpha Blender render used to create the painting")
    parser.add_argument("output", type=Path)
    parser.add_argument("--brightness", type=int, default=5,
                        help="GIMP Brightness-Contrast brightness slider value (default: +5)")
    parser.add_argument("--canvas-size", type=int, default=1600,
                        help="XCF canvas edge (default: 1600)")
    parser.add_argument("--gimp-console", type=Path, default=DEFAULT_GIMP)
    args = parser.parse_args()
    source = args.source.resolve(strict=True)
    reference_path = args.reference_render.resolve(strict=True)
    gimp = args.gimp_console.resolve(strict=True)
    output = args.output.resolve()
    if (source.suffix.lower() != ".png" or reference_path.suffix.lower() != ".png"
            or output.suffix.lower() != ".xcf"):
        parser.error("Expected painted and render PNG sources and an XCF output")
    if output.exists():
        parser.error(f"Refusing to overwrite existing XCF: {output}")
    if (CANVAS_SIZE, SPRITE_SIZE, OFFSET_X, OFFSET_Y) != (256, 160, None, None):
        parser.error("SV pipeline placement defaults changed; review sizing before creating XCF")
    if not -127 <= args.brightness <= 127:
        parser.error("Brightness must be between -127 and 127")
    if args.canvas_size < 640 or args.canvas_size % 2:
        parser.error("Canvas size must be an even number at least 640")

    output.parent.mkdir(parents=True, exist_ok=True)
    source_image = Image.open(source).convert("RGBA")
    reference = Image.open(reference_path).convert("RGBA")
    source_square, painted_box, reference_box = matched_art_size(
        source_image, reference, args.canvas_size, CANVAS_SIZE)
    offset = (args.canvas_size - source_square) // 2
    painted = source_image.resize(
        (source_square, source_square), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (args.canvas_size, args.canvas_size), (0, 0, 0, 0))
    canvas.alpha_composite(painted, (offset, offset))
    prepared = output.with_name(f"{output.stem}_Placed.png")
    canvas.save(prepared)

    report = output.with_name(f"{output.stem}_Report.json")
    report.unlink(missing_ok=True)
    env = os.environ.copy()
    env.update({"CSC_SV_XCF_BATCH": "1", "CSC_SV_XCF_PREPARED": str(prepared),
                "CSC_SV_XCF_OUTPUT": str(output), "CSC_SV_XCF_REPORT": str(report),
                "CSC_SV_XCF_BRIGHTNESS": str(args.brightness),
                "CSC_SV_XCF_CANVAS_SIZE": str(args.canvas_size),
                "CSC_SV_XCF_ART_SIZE": str(source_square)})
    batch = f"exec(open({str(SCRIPT)!r}, encoding='utf-8').read())"
    command = [str(gimp), "--new-instance", "--no-interface", "--no-splash",
               "--batch-interpreter=python-fu-eval", f"--batch={batch}", "--quit"]
    proc = subprocess.run(command, text=True, capture_output=True, errors="replace",
                          env=env, cwd=gimp.parent, check=False)
    log = output.with_name(f"{output.stem}_Gimp.log")
    log.write_text(proc.stdout + proc.stderr, encoding="utf-8")
    if proc.returncode or not report.exists():
        raise RuntimeError(f"GIMP failed; see {log}\n{(proc.stdout + proc.stderr)[-2000:]}")
    result = json.loads(report.read_text(encoding="utf-8"))
    if result.get("error") or not result.get("saved_and_reopened"):
        raise RuntimeError(f"GIMP did not verify XCF; see {report}\n{result.get('error')}")
    final_scale = CANVAS_SIZE / args.canvas_size
    result.update({"source": str(source),
                   "reference_render": str(reference_path),
                   "painted_alpha_bbox": painted_box,
                   "render_alpha_bbox": reference_box,
                   "target_subject_geomean_256": TARGET_SUBJECT_GEOMEAN_256,
                   "placement_256_equivalent": [round(source_square * final_scale, 2),
                                                round(offset * final_scale, 2),
                                                round(offset * final_scale, 2)],
                   "placement_xcf": [source_square, offset, offset]})
    report.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if os.environ.get("CSC_SV_XCF_BATCH") == "1":
    gimp_batch()
elif __name__ == "__main__":
    main()
