"""Match a generated icon's purple saturation to an existing CSC atlas cell.

Example: python match_icon_saturation.py Workshop_Output.png CSC_TAILORS_256.dds
         --reference-index 5 --output Workshop_Output_Matched.png
"""
import argparse

import numpy as np
from PIL import Image


def purple_mask(rgba):
    rgb = rgba[:, :, :3].astype(np.float32)
    red, green, blue = (rgb[:, :, i] for i in range(3))
    return ((rgba[:, :, 3] > 180) & (rgb.max(axis=2) > 70)
            & (red > green * 1.15) & (blue > green * 1.10))


def saturation(rgb):
    rgb = rgb.astype(np.float32)
    high = rgb.max(axis=2)
    return (high - rgb.min(axis=2)) / np.maximum(high, 1)


def subject_mask(rgba):
    return (rgba[:, :, 3] > 180) & (rgba[:, :, :3].max(axis=2) > 65)


def match(source, reference):
    source_rgba = np.asarray(source.convert('RGBA'))
    reference_rgba = np.asarray(reference.convert('RGBA'))
    source_mask = purple_mask(source_rgba)
    reference_mask = purple_mask(reference_rgba)
    if source_mask.sum() < 100 or reference_mask.sum() < 100:
        raise ValueError('Too few purple subject pixels to match reliably')
    target = float(saturation(reference_rgba[:, :, :3])[reference_mask].mean())
    start = float(saturation(source_rgba[:, :, :3])[source_mask].mean())

    hsv = np.asarray(source.convert('RGB').convert('HSV')).copy()
    original_rgb = source_rgba[:, :, :3].astype(np.float32)
    rgb = original_rgb
    red, green, blue = (rgb[:, :, i] for i in range(3))
    strength = np.clip((np.minimum(red, blue) - green - 4) / 18, 0, 1)
    strength *= np.clip((rgb.max(axis=2) - 40) / 50, 0, 1)
    strength *= (source_rgba[:, :, 3] > 0)

    def boosted(multiplier):
        adjusted_hsv = hsv.copy()
        adjusted_hsv[:, :, 1] = np.clip(hsv[:, :, 1].astype(np.float32) * multiplier, 0, 255).astype(np.uint8)
        enhanced_rgb = np.asarray(Image.fromarray(adjusted_hsv, 'HSV').convert('RGB')).astype(np.float32)
        result_rgb = np.clip(original_rgb + (enhanced_rgb - original_rgb) * strength[:, :, None], 0, 255).astype(np.uint8)
        return result_rgb

    lower, upper = 1.0, 4.0
    for _ in range(20):
        middle = (lower + upper) / 2
        candidate = source_rgba.copy()
        candidate[:, :, :3] = boosted(middle)
        achieved = float(saturation(candidate[:, :, :3])[purple_mask(candidate)].mean())
        if achieved < target:
            lower = middle
        else:
            upper = middle
    result = source_rgba.copy()
    result[:, :, :3] = boosted((lower + upper) / 2)
    roof_scale = (lower + upper) / 2

    reference_global = float(saturation(reference_rgba[:, :, :3])[subject_mask(reference_rgba)].mean())
    current_global = float(saturation(result[:, :, :3])[subject_mask(result)].mean())
    if current_global > reference_global:
        nonpurple_strength = 1 - strength
        current_rgb = result[:, :, :3].astype(np.float32)
        current_hsv = np.asarray(Image.fromarray(result[:, :, :3], 'RGB').convert('HSV')).copy()

        def balance(multiplier):
            adjusted_hsv = current_hsv.copy()
            adjusted_hsv[:, :, 1] = np.clip(current_hsv[:, :, 1].astype(np.float32) * multiplier, 0, 255).astype(np.uint8)
            subdued_rgb = np.asarray(Image.fromarray(adjusted_hsv, 'HSV').convert('RGB')).astype(np.float32)
            return np.clip(current_rgb + (subdued_rgb - current_rgb) * nonpurple_strength[:, :, None], 0, 255).astype(np.uint8)

        lower_global, upper_global = 0.4, 1.0
        for _ in range(20):
            middle = (lower_global + upper_global) / 2
            achieved = float(saturation(balance(middle))[subject_mask(result)].mean())
            if achieved < reference_global:
                lower_global = middle
            else:
                upper_global = middle
        result[:, :, :3] = balance((lower_global + upper_global) / 2)

    final_roof = float(saturation(result[:, :, :3])[purple_mask(result)].mean())
    final_global = float(saturation(result[:, :, :3])[subject_mask(result)].mean())
    return Image.fromarray(result, 'RGBA'), (start, target, final_roof, roof_scale), (current_global, reference_global, final_global)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source')
    parser.add_argument('reference')
    parser.add_argument('--reference-index', type=int, help='Cell index in a 4x4 256px atlas')
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    source = Image.open(args.source)
    reference = Image.open(args.reference)
    if args.reference_index is not None:
        if not 0 <= args.reference_index < 16 or reference.size != (1024, 1024):
            raise ValueError('Reference index requires a 1024x1024 4x4 atlas')
        x = args.reference_index % 4 * 256
        y = args.reference_index // 4 * 256
        reference = reference.crop((x, y, x + 256, y + 256))
    result, roof, overall = match(source, reference)
    result.save(args.output)
    print(f'Purple saturation: source {roof[0]:.3f}, reference {roof[1]:.3f}, matched {roof[2]:.3f}; scale {roof[3]:.3f}')
    print(f'Overall saturation: purple-only {overall[0]:.3f}, reference {overall[1]:.3f}, matched {overall[2]:.3f}')
    print(args.output)


if __name__ == '__main__':
    main()
