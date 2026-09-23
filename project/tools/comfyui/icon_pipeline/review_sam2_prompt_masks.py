"""Enlarge stored SAM 2 candidate masks for human review; no model rerun."""
import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mask_dir', type=Path)
    args = ap.parse_args()
    directory = args.mask_dir
    report = json.loads((directory / 'sam2_prediction_report.json').read_text(encoding='utf-8'))
    source = Image.open(report['source']).convert('RGBA')
    rgba = np.asarray(source)
    rgb = rgba[:, :, :3].copy()
    rgb[rgba[:, :, 3] < 128] = 255
    masks = np.load(directory / 'candidate_masks.npz')
    font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf', 18)
    for obj in report['objects']:
        x1, y1, x2, y2 = obj['box']
        pad = 12
        crop = (max(0, x1-pad), max(0, y1-pad), min(source.width, x2+pad), min(source.height, y2+pad))
        w, h = crop[2]-crop[0], crop[3]-crop[1]
        scale = min(4, max(1, 480//max(w, h))) if max(w, h) > 160 else 4
        panels = []
        for idx in range(3):
            key = f"{obj['key']}_{idx}"
            mask = masks[key][crop[1]:crop[3], crop[0]:crop[2]].astype(bool)
            panel = Image.fromarray(rgb[crop[1]:crop[3], crop[0]:crop[2]]).convert('RGBA')
            tint = Image.new('RGBA', panel.size, (0, 220, 240, 0))
            tint.putalpha(Image.fromarray(mask.astype(np.uint8)*130, 'L'))
            panel.alpha_composite(tint)
            if scale > 1:
                panel = panel.resize((w*scale, h*scale), Image.Resampling.NEAREST)
            card = Image.new('RGBA', (panel.width, panel.height+30), (50, 50, 50, 255))
            card.alpha_composite(panel, (0, 30))
            ImageDraw.Draw(card).text((8, 4), f"{obj['name']} #{idx}", font=font, fill='white')
            panels.append(card)
        sheet = Image.new('RGBA', (sum(p.width for p in panels), max(p.height for p in panels)), (50, 50, 50, 255))
        cursor = 0
        for panel in panels:
            sheet.alpha_composite(panel, (cursor, 0))
            cursor += panel.width
        out = directory / f"{obj['key']}_review_large.png"
        sheet.save(out)
        print(out)


if __name__ == '__main__':
    main()
