"""Export visually selected SAM 2.1 object boundaries without image-snapped paths."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw

from export_sam2_hybrid_paths import contours_for_mask, svg_path


SELECTION = {
    'main_pink_roof': 2,
    'stall_pink_canopy': 2,
    'stone_doorway': 1,
    'cutting_cloth': 2,
    'gold_hanging_garment': 2,
    'teal_hanging_garment': 1,
    'cream_hanging_garment': 2,
    'front_dress_form': 1,
    'door_display_coat': 1,
}

MASS_CLEANUP = {
    'main_pink_roof': (61, 5.0),
    'upper_timber_story': (23, 4.0),
    'stone_ground_floor': (17, 3.0),
    'stone_doorway': (9, 2.0),
    'cutting_cloth': (11, 2.0),
}


def clean_semantic_mask(mask, key):
    size, sigma = MASS_CLEANUP.get(key, (3, 0.0))
    if size > 3:
        element = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (size, size))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, element)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))
    if sigma:
        mask = np.uint8(cv2.GaussianBlur(mask.astype(np.float32), (0, 0), sigma) >= .48) * 255
    if key == 'main_pink_roof':
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if contours:
            hull = cv2.convexHull(max(contours, key=cv2.contourArea))
            mask = np.zeros_like(mask)
            cv2.fillPoly(mask, [hull], 255)
    return mask


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('mask_dir', type=Path)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    report = json.loads((args.mask_dir/'sam2_prediction_report.json').read_text(encoding='utf-8'))
    masks = np.load(args.mask_dir/'candidate_masks.npz')
    source = Image.open(report['source']).convert('RGBA')
    names = {obj['key']: obj['name'] for obj in report['objects']}
    rgb = np.asarray(source)[:, :, :3]
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    pink = np.uint8((hsv[:, :, 0] >= 125) & (hsv[:, :, 0] <= 169) &
                    (hsv[:, :, 1] >= 55)) * 255
    manifest = {'canvas': list(source.size), 'outer_radius': 7, 'inner_radius': 4,
                'interior_width': 5, 'basis': 'SAM 2.1 prompted masks only; visual candidate selection',
                'selected_candidates': SELECTION, 'paths': []}
    review = source.copy()
    draw = ImageDraw.Draw(review)
    for key, index in SELECTION.items():
        mask = masks[f'{key}_{index}'].astype(np.uint8)*255
        if key == 'main_pink_roof':
            mask = cv2.bitwise_and(mask, pink)
        elif key == 'upper_timber_story':
            mask = cv2.bitwise_and(mask, cv2.bitwise_not(pink))
        mask = clean_semantic_mask(mask, key)
        for contour in contours_for_mask(mask):
            if cv2.contourArea(contour) < 100:
                continue
            path = svg_path(contour)
            if path:
                manifest['paths'].append({'shape': names[key], 'd': path})
            pts = [(int(p[0][0]), int(p[0][1])) for p in contour]
            if len(pts) > 2:
                draw.line(pts+[pts[0]], fill=(0, 255, 255, 255), width=2)
    output = args.output_dir/'sam2_only_paths.json'
    output.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    review.save(args.output_dir/'SAM2_Only_Path_Review.png')
    print(json.dumps({'manifest': str(output), 'path_count': len(manifest['paths'])}))


if __name__ == '__main__':
    main()
