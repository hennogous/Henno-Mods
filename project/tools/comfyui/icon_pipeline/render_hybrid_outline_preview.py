"""Draw a review PNG from the original render and an unstroked path manifest."""
import argparse
import json
import re
from pathlib import Path

import cv2
import numpy as np
from PIL import Image


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source', type=Path)
    ap.add_argument('manifest', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--white-background', action='store_true')
    args = ap.parse_args()
    spec = json.loads(args.manifest.read_text(encoding='utf-8'))
    rgba = np.asarray(Image.open(args.source).convert('RGBA')).copy()
    alpha = np.uint8(rgba[:, :, 3] >= 128) * 255
    outer = max(1, round((spec['outer_radius'] + spec['inner_radius']) * .68))
    inner = max(1, round(spec['interior_width'] * .68))
    # Place an opaque dark outline behind every visible silhouette pixel.
    expanded = cv2.dilate(alpha, cv2.getStructuringElement(cv2.MORPH_ELLIPSE,
                                                            (outer*2+1, outer*2+1)))
    backdrop = np.zeros_like(rgba)
    backdrop[:, :, 3] = expanded
    result = np.asarray(Image.alpha_composite(Image.fromarray(backdrop), Image.fromarray(rgba))).copy()
    contours, _ = cv2.findContours(alpha, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(result, contours, -1, (12, 11, 10, 255), outer, lineType=cv2.LINE_AA)
    for item in spec['paths']:
        points = [(int(x), int(y)) for x, y in re.findall(r'(\d+) (\d+)', item['d'])]
        if len(points) < 2:
            continue
        pts = np.array(points, np.int32).reshape(-1, 1, 2)
        closed = item['d'].rstrip().upper().endswith('Z')
        cv2.polylines(result, [pts], closed, (17, 15, 14, 255), inner, lineType=cv2.LINE_AA)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(result).save(args.output)
    ys, xs = np.where(expanded > 0)
    crop = (max(0, int(xs.min())-25), max(0, int(ys.min())-25),
            min(source_width := rgba.shape[1], int(xs.max())+26),
            min(source_height := rgba.shape[0], int(ys.max())+26))
    cutout = Image.fromarray(result).crop(crop)
    if args.white_background:
        white = Image.new('RGBA', cutout.size, (255, 255, 255, 255))
        white.alpha_composite(cutout)
        white.convert('RGB').save(args.output)
        print(args.output)
        return
    yy, xx = np.indices((cutout.height, cutout.width))
    tile = ((xx//24 + yy//24) % 2).astype(bool)
    back = np.full((cutout.height, cutout.width, 4), (214, 214, 214, 255), np.uint8)
    back[tile] = (176, 176, 176, 255)
    checker = Image.alpha_composite(Image.fromarray(back), cutout)
    checker_path = args.output.with_name(args.output.stem+'_Checker.png')
    checker.save(checker_path)
    print(args.output)
    print(checker_path)


if __name__ == '__main__':
    main()
