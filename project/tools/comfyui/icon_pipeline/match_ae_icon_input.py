"""Match a transparent Blender icon render to the palette of an AE screenshot.

The screenshot's sky/terrain never enters the output.  Instead, broad material
colour families are measured independently, then their median colour and
contrast are transferred to the render with feathered weights.  This is more
useful than one global brightness slider: the Tailor reference has a brighter
pink roof and stone, but *darker* plaster than the Blender render.
"""

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image


def ramp_up(values, low, high):
    return np.clip((values - low) / (high - low), 0.0, 1.0)


def ramp_down(values, low, high):
    return 1.0 - ramp_up(values, low, high)


def band(values, low, feather, high):
    return ramp_up(values, low - feather, low + feather) * ramp_down(
        values, high - feather, high + feather
    )


def families(hsv):
    """Soft masks in PIL's 0..255 HSV scale for CSC building materials."""
    hue, sat, val = (hsv[..., index].astype(np.float32) for index in range(3))
    return {
        "roof_magenta": band(hue, 175, 10, 235) * ramp_up(sat, 35, 75) * ramp_up(val, 65, 100),
        "timber": band(hue, 8, 8, 48) * ramp_up(sat, 25, 60) * ramp_down(val, 190, 225),
        "cyan_cloth": band(hue, 115, 12, 170) * ramp_up(sat, 50, 90),
        "plaster": ramp_down(sat, 45, 85) * ramp_up(val, 125, 180),
        "stone": ramp_down(sat, 55, 100) * band(val, 65, 25, 185),
    }


def reference_region(size, bounds):
    width, height = size
    if bounds is None:
        return np.ones((height, width), dtype=bool)
    left, top, right, bottom = bounds
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError("Reference bounds must fit within the screenshot")
    region = np.zeros((height, width), dtype=bool)
    region[top:bottom, left:right] = True
    return region


def robust_color(rgb, selection):
    pixels = rgb[selection]
    if len(pixels) < 100:
        return None
    return {
        "median": np.median(pixels, axis=0),
        "iqr": np.percentile(pixels, 75, axis=0) - np.percentile(pixels, 25, axis=0),
        "count": int(len(pixels)),
    }


def match_ae(render_path: Path, reference_path: Path, output_path: Path,
             reference_bounds=None, strength=1.0):
    if not 0 <= strength <= 1:
        raise ValueError("Strength must be between 0 and 1")
    render = Image.open(render_path).convert("RGBA")
    reference = Image.open(reference_path).convert("RGB")
    source_rgb = np.asarray(render, dtype=np.uint8)[..., :3]
    source_alpha = np.asarray(render.getchannel("A"), dtype=np.uint8)
    reference_rgb = np.asarray(reference, dtype=np.uint8)
    source_hsv = np.asarray(render.convert("RGB").convert("HSV"), dtype=np.uint8)
    reference_hsv = np.asarray(reference.convert("HSV"), dtype=np.uint8)
    source_families = families(source_hsv)
    reference_families = families(reference_hsv)
    region = reference_region(reference.size, reference_bounds)

    source = source_rgb.astype(np.float32)
    corrections = np.zeros_like(source)
    total_weight = np.zeros(source.shape[:2], dtype=np.float32)
    report = {"source": str(render_path), "reference": str(reference_path),
              "strength": strength, "families": {}}
    for name, source_weight in source_families.items():
        reference_weight = reference_families[name]
        source_stats = robust_color(source_rgb,
                                    (source_weight > 0.75) & (source_alpha > 240))
        family_region = region
        if name == "cyan_cloth":
            # The AE sky is also blue, while the cloth and garments are below
            # the upper storey in this icon view.
            family_region = region & (np.indices(region.shape)[0] > reference.height * 0.5)
        reference_stats = robust_color(reference_rgb,
                                       (reference_weight > 0.75) & family_region)
        if source_stats is None or reference_stats is None:
            raise ValueError(f"Too few reference/render pixels for {name}")
        source_median = source_stats["median"]
        reference_median = reference_stats["median"]
        contrast = np.clip(reference_stats["iqr"] / np.maximum(source_stats["iqr"], 8.0),
                           0.75, 1.4)
        adjusted = reference_median + (source - source_median) * contrast
        delta = np.clip(adjusted - source, -45.0, 45.0)
        corrections += source_weight[..., None] * delta
        total_weight += source_weight
        report["families"][name] = {
            "render_median": source_median.round(1).tolist(),
            "reference_median": reference_median.round(1).tolist(),
            "contrast": contrast.round(3).tolist(),
            "render_pixels": source_stats["count"],
            "reference_pixels": reference_stats["count"],
        }

    # Normalize overlaps so pale stone/plaster edges receive a blended grade.
    delta = corrections / np.maximum(total_weight[..., None], 1.0)
    graded = np.clip(source + strength * delta, 0, 255).astype(np.uint8)
    output = np.dstack((graded, source_alpha))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(output, "RGBA").save(output_path)
    report["output"] = str(output_path)
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("render", type=Path)
    parser.add_argument("reference", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--reference-bounds", type=int, nargs=4,
                        metavar=("LEFT", "TOP", "RIGHT", "BOTTOM"))
    parser.add_argument("--strength", type=float, default=1.0)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    report = match_ae(args.render, args.reference, args.output,
                      args.reference_bounds, args.strength)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
