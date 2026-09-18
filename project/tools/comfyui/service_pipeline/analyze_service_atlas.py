"""Measure service-icon cells in a Civ VI RGBA icon atlas.

The report distinguishes fully opaque primary artwork from the lower-opacity
secondary artwork used by CSC service pictograms. It can also write a labelled
preview of the requested cells on a checkerboard background.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw


def bbox_for(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    ys, xs = np.where(mask)
    if not len(xs):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def describe_cell(cell: Image.Image, index: int) -> dict[str, object]:
    alpha = np.asarray(cell.getchannel("A"), dtype=np.uint8)
    visible = alpha > 0
    solid = alpha >= 230
    secondary_core = (alpha >= 190) & (alpha <= 215)
    visible_bbox = bbox_for(visible)
    solid_bbox = bbox_for(solid)
    secondary_bbox = bbox_for(secondary_core)
    levels, counts = np.unique(alpha[visible], return_counts=True)
    common = sorted(zip(counts.tolist(), levels.tolist()), reverse=True)[:10]

    def with_size(box: tuple[int, int, int, int] | None) -> dict[str, object] | None:
        if box is None:
            return None
        x0, y0, x1, y1 = box
        return {"bbox": box, "size": (x1 - x0, y1 - y0)}

    return {
        "index": index,
        "visible": with_size(visible_bbox),
        "primary_opaque": with_size(solid_bbox),
        "secondary_75_85pct": with_size(secondary_bbox),
        "visible_pixels": int(visible.sum()),
        "opaque_pixels": int(solid.sum()),
        "common_nonzero_alpha": [
            {"alpha": level, "pixels": count} for count, level in common
        ],
    }


def checkerboard(size: tuple[int, int], step: int = 16) -> Image.Image:
    out = Image.new("RGBA", size, (44, 44, 44, 255))
    draw = ImageDraw.Draw(out)
    for y in range(0, size[1], step):
        for x in range(0, size[0], step):
            if (x // step + y // step) % 2:
                draw.rectangle((x, y, x + step - 1, y + step - 1), fill=(76, 76, 76, 255))
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("atlas", type=Path)
    parser.add_argument("indices", nargs="+", type=int)
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--cell-size", type=int, default=256)
    parser.add_argument("--preview", type=Path)
    parser.add_argument("--transparent-preview", action="store_true")
    args = parser.parse_args()

    atlas = Image.open(args.atlas).convert("RGBA")
    cells: list[Image.Image] = []
    report = []
    for index in args.indices:
        x = index % args.columns * args.cell_size
        y = index // args.columns * args.cell_size
        cell = atlas.crop((x, y, x + args.cell_size, y + args.cell_size))
        cells.append(cell)
        report.append(describe_cell(cell, index))

    if args.preview:
        label_h = 28
        background = (255, 255, 255, 0) if args.transparent_preview else (24, 24, 24, 255)
        preview = Image.new("RGBA", (len(cells) * args.cell_size, args.cell_size + label_h), background)
        draw = ImageDraw.Draw(preview)
        for n, (index, cell) in enumerate(zip(args.indices, cells)):
            base = Image.new("RGBA", cell.size, (255, 255, 255, 0)) if args.transparent_preview else checkerboard(cell.size)
            base.alpha_composite(cell)
            preview.alpha_composite(base, (n * args.cell_size, label_h))
            if not args.transparent_preview:
                draw.text((n * args.cell_size + 8, 7), f"atlas cell {index}", fill=(255, 255, 255, 255))
        args.preview.parent.mkdir(parents=True, exist_ok=True)
        preview.save(args.preview)

    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
