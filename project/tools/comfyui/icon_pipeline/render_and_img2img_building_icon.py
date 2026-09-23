"""Render a clean CSC building, grade it to an AE reference, then run img2img.

Example (PowerShell):
  python render_and_img2img_building_icon.py BUILDING.blend AE_SCREENSHOT.png OUTPUT_DIR \
    --name CSC_TAILORS_Tailor --reference-bounds 35 55 700 690

The source blend is never saved. Existing outputs are backed up before reruns.
"""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request

from match_ae_icon_input import match_ae


DEFAULT_BLENDER = Path(r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe")


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def backup_existing(paths, directory):
    existing = [path for path in paths if path.exists()]
    if not existing:
        return None
    backup = directory / "History" / datetime.now().strftime("%Y%m%d_%H%M%S")
    backup.mkdir(parents=True)
    for path in existing:
        shutil.copy2(path, backup / path.name)
    return backup


def run_logged(command, log_path, environment=None):
    completed = subprocess.run(command, capture_output=True, text=True, env=environment,
                               check=False, errors="replace")
    log_path.write_text(completed.stdout + completed.stderr, encoding="utf-8")
    print(completed.stdout)
    if completed.stderr:
        print(completed.stderr, file=sys.stderr)
    if completed.returncode:
        raise RuntimeError(f"Command failed ({completed.returncode}): {command[0]}; see {log_path}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("blend", type=Path)
    parser.add_argument("ae_reference", type=Path)
    parser.add_argument("output_dir", type=Path)
    parser.add_argument("--name", required=True, help="Asset stem, e.g. CSC_TAILORS_Tailor")
    parser.add_argument("--blender", type=Path, default=DEFAULT_BLENDER)
    parser.add_argument("--elevation", type=float, default=23.0)
    parser.add_argument("--lens", type=float, default=37.0)
    parser.add_argument("--camera-distance", type=float)
    parser.add_argument("--view-transform", default="Standard", choices=("Standard", "AgX", "scene"))
    parser.add_argument("--exposure", type=float, default=0.0)
    parser.add_argument("--sun-energy", type=float, default=3.0)
    parser.add_argument("--world-strength", type=float, default=0.8)
    parser.add_argument("--world-color", type=float, nargs=3, default=(1.0, 1.0, 0.9))
    parser.add_argument("--reference-bounds", type=int, nargs=4,
                        metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
    parser.add_argument("--grade-strength", type=float, default=1.0)
    parser.add_argument("--skip-img2img", action="store_true", help="Only render and grade")
    args = parser.parse_args()

    blend = args.blend.resolve(strict=True)
    ae_reference = args.ae_reference.resolve(strict=True)
    blender = args.blender.resolve(strict=True)
    output_dir = args.output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    raw = output_dir / f"{args.name}_BlenderRaw.png"
    treated = output_dir / f"{args.name}_Input.png"
    icon = output_dir / f"{args.name}_Output.png"
    report_path = output_dir / f"{args.name}_AE_Color_Match.json"
    manifest_path = output_dir / f"{args.name}_Run.json"
    backup = backup_existing((raw, treated, icon, report_path, manifest_path), output_dir)
    if backup:
        print("Backed up existing outputs:", backup)

    render_script = Path(__file__).resolve().parents[2] / "blender" / "render_building_icon_input.py"
    render_command = [str(blender), "--background", str(blend), "--python",
                      str(render_script), "--", str(raw), "--elevation", str(args.elevation),
                      "--lens", str(args.lens), "--view-transform", args.view_transform,
                      "--exposure", str(args.exposure), "--sun-energy", str(args.sun_energy),
                      "--world-strength", str(args.world_strength), "--world-color",
                      *(str(value) for value in args.world_color)]
    if args.camera_distance is not None:
        render_command += ["--camera-distance", str(args.camera_distance)]
    run_logged(render_command, output_dir / f"{args.name}_Blender.log")
    if not raw.is_file():
        raise FileNotFoundError(f"Blender reported success without creating {raw}")

    grade_report = match_ae(raw, ae_reference, treated,
                            args.reference_bounds, args.grade_strength)
    report_path.write_text(json.dumps(grade_report, indent=2), encoding="utf-8")
    print("AE color treatment:", treated)

    img2img_command = None
    if not args.skip_img2img:
        try:
            urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=5).close()
        except Exception as error:
            raise RuntimeError("ComfyUI is unavailable at 127.0.0.1:8188") from error
        img2img_command = [sys.executable,
                           str(Path(__file__).resolve().with_name("icon_img2img.py")), str(treated)]
        run_logged(img2img_command, output_dir / f"{args.name}_Img2Img.log")
        if not icon.is_file():
            raise FileNotFoundError(f"img2img reported success without creating {icon}")

    manifest = {
        "blend": str(blend), "blend_sha256": sha256(blend),
        "ae_reference": str(ae_reference), "ae_reference_sha256": sha256(ae_reference),
        "render_command": render_command, "render": str(raw), "render_sha256": sha256(raw),
        "grade": str(treated), "grade_sha256": sha256(treated),
        "grade_report": str(report_path), "img2img_command": img2img_command,
        "icon": str(icon) if img2img_command and icon.is_file() else None,
        "icon_sha256": sha256(icon) if img2img_command and icon.is_file() else None,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print("Run manifest:", manifest_path)


if __name__ == "__main__":
    main()
