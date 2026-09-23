"""Turn reviewed SAM 2 masks into unstroked icon paths alongside image-snapped edges."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw


def contours_for_mask(mask):
    # Keep the prompted object, not small false-positive islands or pinholes.
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, 8)
    if count < 2:
        return []
    largest = 1 + int(np.argmax(stats[1:, cv2.CC_STAT_AREA]))
    clean = np.uint8(labels == largest) * 255
    clean = cv2.morphologyEx(clean, cv2.MORPH_CLOSE,
                             cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)))
    contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return sorted(contours, key=cv2.contourArea, reverse=True)


def svg_path(contour):
    smoothed = cv2.approxPolyDP(contour, 1.1, True).reshape(-1, 2)
    if len(smoothed) < 3:
        return None
    return 'M ' + ' L '.join(f'{int(x)} {int(y)}' for x, y in smoothed) + ' Z'


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mask_dir', type=Path)
    ap.add_argument('snapped_paths', type=Path)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = json.loads((args.mask_dir/'sam2_prediction_report.json').read_text(encoding='utf-8'))
    snap = json.loads(args.snapped_paths.read_text(encoding='utf-8'))
    source = Image.open(report['source']).convert('RGBA')
    masks = np.load(args.mask_dir/'candidate_masks.npz')
    selected = {
        'stall_pink_canopy': 2,
        'gold_hanging_garment': 2,
        'teal_hanging_garment': 1,
        'cream_hanging_garment': 2,
        'front_dress_form': 1,
        'door_display_coat': 1,
    }
    names = {obj['key']: obj['name'] for obj in report['objects']}
    manifest = {key: snap[key] for key in ('canvas', 'outer_radius', 'inner_radius', 'interior_width')}
    # The roof failed visual review. Preserve only four trustworthy snapped architectural lines.
    exclude_snapped = {'Stall canopy left edge', 'Stall canopy front eave'}
    manifest['paths'] = [p for p in snap['paths'] if p['shape'] not in exclude_snapped]
    review = source.copy()
    draw = ImageDraw.Draw(review)
    for key, idx in selected.items():
        raw = masks[f'{key}_{idx}'].astype(np.uint8)
        for contour in contours_for_mask(raw):
            if cv2.contourArea(contour) < 100:
                continue
            path = svg_path(contour)
            if path:
                manifest['paths'].append({'shape': names[key], 'd': path})
            pts = [(int(p[0][0]), int(p[0][1])) for p in contour]
            if len(pts) > 2:
                draw.line(pts + [pts[0]], fill=(0, 255, 255, 255), width=2)
    # Magenta marks the retained image-snapped architecture, cyan the SAM 2 masses.
    for path in manifest['paths'][:len(snap['paths'])-len(exclude_snapped)]:
        import re
        pts = [(int(x), int(y)) for x, y in re.findall(r'(\d+) (\d+)', path['d'])]
        if len(pts) > 1:
            draw.line(pts, fill=(255, 50, 220, 255), width=2)
    manifest['basis'] = 'Visually selected SAM 2.1 prompted masks for canopy and garments; retained image-snapped architecture; unstroked GIMP paths'
    manifest['sam2_candidates'] = selected
    output = args.output_dir/'hybrid_paths.json'
    output.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    review.save(args.output_dir/'Hybrid_Path_Review.png')
    print(json.dumps({'manifest': str(output), 'path_count': len(manifest['paths']),
                      'review': str(args.output_dir/'Hybrid_Path_Review.png')}))


if __name__ == '__main__':
    main()
