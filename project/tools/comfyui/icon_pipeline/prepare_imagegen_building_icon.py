"""Fit a transparent painted building master into a Civ VI 256px atlas cell.

This deliberately preserves the painted colours and edge treatment. It only
removes empty margins, resizes, and centers the complete subject.
"""

import argparse
from pathlib import Path

from PIL import Image


def prepare(source: Path, output: Path, size: int = 256, extent: int = 220, offset_y: int = 0) -> tuple[int, int]:
    image = Image.open(source).convert("RGBA")
    alpha = image.getchannel("A")
    solid = alpha.point(lambda value: 255 if value > 16 else 0)
    bounds = solid.getbbox()
    if bounds is None:
        raise ValueError(f"No visible subject in {source}")

    cropped = image.crop(bounds)
    width, height = cropped.size
    scale = extent / max(width, height)
    fitted_size = (round(width * scale), round(height * scale))
    if max(fitted_size) > size:
        raise ValueError("Requested extent exceeds canvas")
    fitted = cropped.resize(fitted_size, Image.Resampling.LANCZOS)

    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    x = (size - fitted_size[0]) // 2
    y = (size - fitted_size[1]) // 2 + offset_y
    if y < 0 or y + fitted_size[1] > size:
        raise ValueError("Vertical offset clips the subject")
    canvas.alpha_composite(fitted, (x, y))
    output.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output)
    return fitted_size


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--extent", type=int, default=220)
    parser.add_argument("--offset-y", type=int, default=0)
    args = parser.parse_args()
    print("fitted_size", prepare(args.source, args.output, args.size, args.extent, args.offset_y))
    print(args.output)


if __name__ == "__main__":
    main()
