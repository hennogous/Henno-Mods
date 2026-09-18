"""Normalize an ImageGen service-icon draft into a CSC atlas-ready PNG."""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


def _bbox(mask: np.ndarray) -> tuple[int, int, int, int] | None:
    ys, xs = np.where(mask)
    if not len(xs):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _keep_major_components(mask: np.ndarray, relative_area: float = 0.02) -> np.ndarray:
    """Remove small disconnected ImageGen fragments from a binary mask."""
    height, width = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    components: list[list[tuple[int, int]]] = []
    for start_y, start_x in zip(*np.where(mask & ~seen)):
        if seen[start_y, start_x]:
            continue
        stack = [(int(start_y), int(start_x))]
        seen[start_y, start_x] = True
        points: list[tuple[int, int]] = []
        while stack:
            y, x = stack.pop()
            points.append((y, x))
            for ny in range(max(0, y - 1), min(height, y + 2)):
                for nx in range(max(0, x - 1), min(width, x + 2)):
                    if mask[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        stack.append((ny, nx))
        components.append(points)
    if not components:
        return mask
    largest = max(len(points) for points in components)
    minimum = max(32, round(largest * relative_area))
    kept = np.zeros_like(mask, dtype=bool)
    for points in components:
        if len(points) >= minimum:
            ys, xs = zip(*points)
            kept[np.asarray(ys), np.asarray(xs)] = True
    return kept


def normalize(input_path: Path, output_path: Path, extent: int = 179, separation: int = 8) -> Path:
    image = Image.open(input_path).convert("RGBA")
    rgba = np.asarray(image, dtype=np.uint8)
    rgb = rgba[:, :, :3].astype(np.float32)
    src_alpha = rgba[:, :, 3]
    luminance = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]

    # ImageGen sometimes encodes transparent/reference noise as dark RGB with
    # nonzero alpha. Keep the intended pale pictogram pixels only.
    foreground = _keep_major_components((src_alpha >= 24) & (luminance >= 160), 0.005)
    primary_seed = _keep_major_components(foreground & (src_alpha >= 235))
    primary_region = np.asarray(
        Image.fromarray(primary_seed.astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(11))
    ) > 0

    primary = foreground & primary_region
    secondary = foreground & ~primary_region
    # Close only tiny generation pinholes without filling intentional icon
    # cutouts such as the anchor eye and clipboard slots.
    primary_img = Image.fromarray(primary.astype(np.uint8) * 255, "L")
    secondary_img = Image.fromarray(secondary.astype(np.uint8) * 255, "L")
    primary_img = primary_img.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    secondary_img = secondary_img.filter(ImageFilter.MaxFilter(5)).filter(ImageFilter.MinFilter(5))
    primary = np.asarray(primary_img) > 0
    secondary = np.asarray(secondary_img) > 0

    alpha = np.zeros(src_alpha.shape, dtype=np.uint8)
    alpha[secondary] = 204  # 80 percent
    alpha[primary] = 255
    box = _bbox(alpha > 0)
    if box is None:
        raise ValueError(f"No usable pictogram found in {input_path}")

    x0, y0, x1, y1 = box
    symbol_alpha = Image.fromarray(alpha[y0:y1, x0:x1], "L")
    scale = extent / max(symbol_alpha.size)
    size = (max(1, round(symbol_alpha.width * scale)), max(1, round(symbol_alpha.height * scale)))
    symbol_alpha = symbol_alpha.resize(size, Image.Resampling.LANCZOS)

    symbol = Image.new("RGBA", size, (255, 255, 255, 0))
    symbol.putalpha(symbol_alpha)
    canvas = Image.new("RGBA", (256, 256), (255, 255, 255, 0))
    canvas.alpha_composite(symbol, ((256 - size[0]) // 2, (256 - size[1]) // 2))
    if separation > 0:
        canvas_alpha = np.asarray(canvas.getchannel("A"), dtype=np.uint8).copy()
        primary_core = canvas_alpha >= 235
        primary_near = np.asarray(
            Image.fromarray(primary_core.astype(np.uint8) * 255, "L").filter(ImageFilter.MaxFilter(5))
        ) > 0
        secondary_pixels = (canvas_alpha > 0) & (canvas_alpha <= 225) & ~primary_near
        halo = np.asarray(
            Image.fromarray(primary_near.astype(np.uint8) * 255, "L").filter(
                ImageFilter.MaxFilter(separation * 2 + 1)
            )
        ) > 0
        canvas_alpha[secondary_pixels & halo] = 0
        canvas.putalpha(Image.fromarray(canvas_alpha, "L"))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--extent", type=int, default=179)
    parser.add_argument("--separation", type=int, default=8)
    args = parser.parse_args()
    print(normalize(args.input, args.output, args.extent, args.separation))


if __name__ == "__main__":
    main()
