"""Deterministic front end for Blender-render-driven CSC SV generation.

The Blender path benefits from two repeatable grades:

* render grade before ComfyUI, so the VAE/LoRA sees clear, colourful surfaces;
* generated grade before SAM, so segmentation sees separated values and edges.

This module also exposes ``generate`` and ``finalize`` commands that select the
Blender-specific crop/scale and SAM defaults without changing screenshot-driven
uses of sv_img2img.py or sv_postprocess.py. The generated PreShadow handoff is
softened after SAM with GIMP-equivalent linear-light contrast -3 and 10%
desaturation, so all six final states inherit the same tonal correction.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass

import numpy as np
from PIL import Image, ImageEnhance, ImageFilter


@dataclass(frozen=True)
class Grade:
    target_luma: float
    target_saturation: float
    contrast: float
    clarity_percent: int
    clarity_radius: float
    max_brightness: float = 1.65
    max_saturation: float = 1.85


RENDER_GRADE = Grade(0.43, 0.46, 1.12, 55, 1.4)
GENERATED_GRADE = Grade(0.41, 0.43, 1.16, 70, 1.2)
# Final visible treatment is deliberately calmer than the segmentation grade.
# The Market/Industrial Workshop references use controlled highlights; lowering
# saturation also keeps bright Quarter roof colours from reading neon.
FINAL_GRADE = Grade(0.395, 0.35, 1.18, 45, 0.9, max_brightness=1.25, max_saturation=1.15)
GIMP_OUTPUT_CONTRAST = -3
OUTPUT_SATURATION_SCALE = 0.90


def _subject_metrics(img: Image.Image) -> tuple[float, float]:
    rgba = np.asarray(img.convert("RGBA"), dtype=np.float32) / 255.0
    subject = rgba[:, :, 3] > (16 / 255.0)
    if not subject.any():
        return 0.0, 0.0
    rgb = rgba[:, :, :3][subject]
    luma = rgb @ np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    saturation = (rgb.max(axis=1) - rgb.min(axis=1)) / np.maximum(rgb.max(axis=1), 1e-6)
    return float(luma.mean()), float(saturation.mean())


def grade_subject(img: Image.Image, grade: Grade) -> Image.Image:
    """Grade RGB deterministically while preserving the source alpha exactly."""
    rgba = img.convert("RGBA")
    alpha = rgba.getchannel("A")
    luma, saturation = _subject_metrics(rgba)
    brightness_factor = min(grade.max_brightness, grade.target_luma / max(luma, 1e-6))
    saturation_factor = min(grade.max_saturation, grade.target_saturation / max(saturation, 1e-6))
    rgb = rgba.convert("RGB")
    rgb = ImageEnhance.Brightness(rgb).enhance(brightness_factor)
    rgb = ImageEnhance.Color(rgb).enhance(saturation_factor)
    rgb = ImageEnhance.Contrast(rgb).enhance(grade.contrast)
    rgb = rgb.filter(ImageFilter.UnsharpMask(
        radius=grade.clarity_radius,
        percent=grade.clarity_percent,
        threshold=3,
    ))
    result = rgb.convert("RGBA")
    result.putalpha(alpha)
    return result


def grade_blender_render(img: Image.Image) -> Image.Image:
    return grade_subject(img, RENDER_GRADE)


def grade_generated_for_sam(img: Image.Image) -> Image.Image:
    return grade_subject(img, GENERATED_GRADE)


def grade_final_visible(img: Image.Image) -> Image.Image:
    """Mild final grade calibrated against the accepted Bakery visible sprite."""
    return grade_subject(img, FINAL_GRADE)


def gimp_linear_contrast(img: Image.Image, ui_value: int = GIMP_OUTPUT_CONTRAST) -> Image.Image:
    """Apply GIMP/GEGL contrast slider semantics in linear sRGB.

    GIMP's integer UI range maps approximately to -127..127. The conversion is
    performed in linear light, matching GIMP's strong dark-tone lift at small
    negative UI values while preserving alpha exactly.
    """
    rgba = np.asarray(img.convert("RGBA"), dtype=np.float32)
    rgb = rgba[:, :, :3] / 255.0
    linear = np.where(
        rgb <= 0.04045,
        rgb / 12.92,
        ((rgb + 0.055) / 1.055) ** 2.4,
    )
    normalized = max(-1.0, min(1.0, ui_value / 127.0))
    factor = np.tan((normalized + 1.0) * np.pi / 4.0)
    linear = np.clip((linear - 0.5) * factor + 0.5, 0.0, 1.0)
    srgb = np.where(
        linear <= 0.0031308,
        linear * 12.92,
        1.055 * np.power(linear, 1.0 / 2.4) - 0.055,
    )
    rgba[:, :, :3] = np.clip(np.rint(srgb * 255.0), 0, 255)
    return Image.fromarray(rgba.astype(np.uint8), "RGBA")


def prepare_preshadow_handoff(img: Image.Image) -> Image.Image:
    """Grade the ComfyUI/SAM result, then soften it before shadow review."""
    contrasted = gimp_linear_contrast(grade_final_visible(img), GIMP_OUTPUT_CONTRAST)
    alpha = contrasted.getchannel("A")
    rgb = ImageEnhance.Color(contrasted.convert("RGB")).enhance(OUTPUT_SATURATION_SCALE)
    result = rgb.convert("RGBA")
    result.putalpha(alpha)
    return result


def _set_pipeline_defaults() -> None:
    os.environ.setdefault("CSC_SV_BLENDER_FRONTEND", "1")
    os.environ.setdefault("CSC_SV_TRIM_TO_SUBJECT", "1")
    # Bakery reference bbox is 131x117. A 132px fit box matches its longest side.
    os.environ.setdefault("CSC_SV_SPRITE_SIZE", "132")
    # With a 132px fit box, centered Y is 62. Place the sprite five pixels lower
    # while the separately composited full-canvas shadow plate stays fixed.
    os.environ.setdefault("CSC_SV_OFFSET_Y", "67")
    # Cleaner Blender-source structural boundaries than the old broad 16px pass.
    os.environ.setdefault("CSC_SV_SAM_LINE_WIDTH", "8")
    os.environ.setdefault("CSC_SV_SAM_MIN_AREA", "1200")
    os.environ.setdefault("CSC_SV_SAM_MAX_MASKS", "24")
    os.environ.setdefault("CSC_SV_SAM_CROP_LAYERS", "0")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("generate", "finalize", "grade-render", "prepare-handoff"))
    parser.add_argument("input")
    parser.add_argument("output", nargs="?")
    args, rest = parser.parse_known_args()
    _set_pipeline_defaults()

    if args.command == "grade-render":
        source = Image.open(args.input).convert("RGBA")
        output = args.output or str(os.path.splitext(args.input)[0] + "_Frontend.png")
        grade_blender_render(source).save(output)
        print(output)
        return

    if args.command == "prepare-handoff":
        source = Image.open(args.input).convert("RGBA")
        output = args.output or args.input
        prepare_preshadow_handoff(source).save(output)
        print(output)
        return

    if args.command == "generate":
        import sv_img2img
        sys.argv = ["sv_img2img.py", args.input, *rest]
        sv_img2img.main()
        return

    import sv_postprocess
    argv = ["sv_postprocess.py", args.input]
    if args.output:
        argv.append(args.output)
    argv.extend(rest)
    sys.argv = argv
    sv_postprocess.main()


if __name__ == "__main__":
    main()
