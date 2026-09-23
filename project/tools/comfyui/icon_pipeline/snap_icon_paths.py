"""Snap selected building-icon boundaries to render pixels with OpenCV scissors.

Input JSON contains canvas, paths [{shape, anchors, closed?}], optional
max_excursion_px and simplify_px. The assistant still selects which major
boundaries matter and places a few anchors; this tool locates their image edges.
Output is a GIMP-importable path manifest and review images. It paints no ink.
"""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def deviation_from_segment(points, a, b):
    start, end = np.asarray(a, np.float32), np.asarray(b, np.float32)
    delta = end - start
    length2 = float(delta @ delta)
    if length2 == 0:
        return float('inf')
    t = np.clip(((points - start) @ delta) / length2, 0, 1)
    projected = start + t[:, None] * delta
    return float(np.linalg.norm(points - projected, axis=1).max())


def svg_path(points, closed):
    points = np.asarray(points).reshape(-1, 2)
    result = 'M ' + ' L '.join(f'{int(x)} {int(y)}' for x, y in points)
    return result + (' Z' if closed else '')


def render_overlay(source, overlays, width):
    image = Image.new('RGBA', source.size, (55, 58, 61, 255))
    image.alpha_composite(source)
    draw = ImageDraw.Draw(image)
    for item in overlays:
        anchors = item['anchors']
        if item['closed']:
            anchors = anchors + anchors[:1]
        draw.line([tuple(p) for p in anchors], fill=(255, 180, 42, 210), width=2, joint='curve')
        pts = [tuple(map(int, p)) for p in item['points']]
        if item['closed']:
            pts.append(pts[0])
        draw.line(pts, fill=(25, 230, 247, 255), width=width, joint='curve')
        for x, y in item['anchors']:
            draw.ellipse((x-3, y-3, x+3, y+3), fill=(255, 55, 45, 255))
    return image


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source', type=Path)
    ap.add_argument('guides', type=Path)
    ap.add_argument('--output-dir', type=Path, required=True)
    args = ap.parse_args()
    config = json.loads(args.guides.read_text(encoding='utf-8-sig'))
    source = Image.open(args.source).convert('RGBA')
    if list(source.size) != config['canvas']:
        raise ValueError('Guide canvas does not match source image')
    rgba = np.asarray(source)
    rgb = rgba[:, :, :3].copy()
    rgb[rgba[:, :, 3] == 0] = 255
    scissors = cv2.segmentation_IntelligentScissorsMB()
    scissors.applyImage(rgb)
    output = args.output_dir
    output.mkdir(parents=True, exist_ok=True)
    snapped_paths, overlays, results = [], [], []
    for spec in config['paths']:
        name = spec['shape']
        anchors = [tuple(map(int, point)) for point in spec['anchors']]
        closed = bool(spec.get('closed', False))
        if len(anchors) < (3 if closed else 2):
            raise ValueError(f'{name}: too few anchors')
        if any(not 0 <= x < source.width or not 0 <= y < source.height for x, y in anchors):
            raise ValueError(f'{name}: anchor outside canvas')
        pairs = list(zip(anchors, anchors[1:] + (anchors[:1] if closed else [])))
        pieces, excursions = [], []
        for a, b in pairs:
            scissors.buildMap(a)
            pixel_path = scissors.getContour(b).reshape(-1, 2)
            if tuple(pixel_path[0]) == b:
                pixel_path = pixel_path[::-1]
            if tuple(pixel_path[0]) != a or tuple(pixel_path[-1]) != b:
                raise RuntimeError(f'{name}: scissors returned unexpected segment endpoints')
            excursions.append(deviation_from_segment(pixel_path.astype(np.float32), a, b))
            cap = float(spec.get('max_excursion_px', config.get('max_excursion_px', 16)))
            if excursions[-1] > cap:
                raise ValueError(f'{name}: segment {a}->{b} wandered {excursions[-1]:.1f} px (limit {cap})')
            epsilon = float(spec.get('simplify_px', config.get('simplify_px', 1.5)))
            simplified = cv2.approxPolyDP(pixel_path, epsilon, False).reshape(-1, 2)
            simplified[0] = a
            simplified[-1] = b
            pieces.extend(simplified[:-1].tolist())
        if not closed:
            pieces.append(list(anchors[-1]))
        pieces = np.asarray(pieces, dtype=np.int32)
        if len(pieces) < 2:
            raise RuntimeError(f'{name}: empty snapped path')
        snapped_paths.append({'shape': name, 'd': svg_path(pieces, closed)})
        overlays.append({'shape': name, 'anchors': anchors, 'closed': closed, 'points': pieces.tolist()})
        results.append({'shape': name, 'anchors': len(anchors), 'editable_points': len(pieces),
                        'max_segment_excursion_px': round(max(excursions), 2), 'closed': closed})
    manifest = {'canvas': list(source.size), 'basis': 'OpenCV Intelligent Scissors guided by selected image-space anchors; review before stroking',
                'outer_radius': 7, 'inner_radius': 4, 'interior_width': 6.5, 'paths': snapped_paths}
    (output / 'snapped_paths.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    (output / 'snap_report.json').write_text(json.dumps({'source': str(args.source), 'guides': str(args.guides),
                                                        'paths': results}, indent=2), encoding='utf-8')
    overview = render_overlay(source, overlays, 3)
    overview.save(output / 'Snapped_Paths_Review.png')
    for view in config.get('review_crops', []):
        name = view['name']
        box = tuple(view['box'])
        overview.crop(box).resize(((box[2]-box[0])*2, (box[3]-box[1])*2), Image.Resampling.NEAREST).save(output / f'{name}_Review.png')
    print(json.dumps({'path_count': len(results), 'report': str(output / 'snap_report.json'),
                      'review': str(output / 'Snapped_Paths_Review.png')}))


if __name__ == '__main__':
    main()
