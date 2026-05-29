"""
Post-process CSC service/unit icon candidates into the same structural format as
Civ VI Units256 training data: transparent background + flat white pictogram.

Input may be a ComfyUI render on black/dark background. Output is an RGBA PNG:
  - near-black background -> alpha 0
  - bright foreground -> white with alpha from luminance
  - centered on a square canvas, default 256x256
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


@dataclass(frozen=True)
class ServiceIconPostprocessConfig:
    output_size: int = 256
    target_fill: float = 0.78
    black_cutoff: int = 22
    white_point: int = 210
    alpha_gamma: float = 0.75
    min_component_area: int = 24
    feather_radius: float = 0.0
    solid_threshold: int = 28
    close_radius: int = 2
    fill_holes: bool = False
    remove_frame_components: bool = False


def _largest_bbox(alpha: np.ndarray, threshold: int = 8) -> tuple[int, int, int, int] | None:
    ys, xs = np.where(alpha > threshold)
    if len(xs) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _fill_binary_holes(mask: np.ndarray) -> np.ndarray:
    """Fill transparent islands fully enclosed by foreground pixels."""
    h, w = mask.shape
    background = ~mask
    reachable = np.zeros_like(background, dtype=bool)
    stack: list[tuple[int, int]] = []

    for x in range(w):
        if background[0, x]:
            stack.append((0, x))
        if background[h - 1, x]:
            stack.append((h - 1, x))
    for y in range(h):
        if background[y, 0]:
            stack.append((y, 0))
        if background[y, w - 1]:
            stack.append((y, w - 1))

    while stack:
        y, x = stack.pop()
        if reachable[y, x] or not background[y, x]:
            continue
        reachable[y, x] = True
        if y > 0:
            stack.append((y - 1, x))
        if y + 1 < h:
            stack.append((y + 1, x))
        if x > 0:
            stack.append((y, x - 1))
        if x + 1 < w:
            stack.append((y, x + 1))

    holes = background & ~reachable
    return mask | holes


def _remove_frame_components(mask: np.ndarray) -> np.ndarray:
    """Drop thin rectangular frame/border components before hole filling.

    Some generations add a square border. If left in place, hole filling turns
    the entire icon cell into a white square. This removes components that span
    most of the image while occupying only a thin fraction of their bounding box.
    """
    h, w = mask.shape
    seen = np.zeros_like(mask, dtype=bool)
    out = mask.copy()

    for sy, sx in zip(*np.where(mask & ~seen)):
        stack = [(int(sy), int(sx))]
        pts: list[tuple[int, int]] = []
        seen[sy, sx] = True
        while stack:
            y, x = stack.pop()
            pts.append((y, x))
            for ny, nx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    stack.append((ny, nx))

        ys = [p[0] for p in pts]
        xs = [p[1] for p in pts]
        bw = max(xs) - min(xs) + 1
        bh = max(ys) - min(ys) + 1
        area = len(pts)
        bbox_area = bw * bh
        thin = area / max(1, bbox_area) < 0.22
        spans_cell = bw > 0.70 * w and bh > 0.70 * h
        if spans_cell and thin:
            for y, x in pts:
                out[y, x] = False

    return out


def _solidify_alpha(alpha_img: Image.Image, cfg: ServiceIconPostprocessConfig) -> Image.Image:
    """Convert extracted foreground into a solid white silhouette.

    ComfyUI often returns black line art on white; after inversion that becomes
    white outlines. This step closes small gaps and fills enclosed interiors so
    icons become filled pictograms rather than outline drawings.
    """
    mask_img = alpha_img.point(lambda p: 255 if p >= cfg.solid_threshold else 0)
    if cfg.close_radius > 0:
        # MaxFilter expands white strokes; MinFilter contracts them again. This
        # closes small line breaks before hole filling without greatly changing
        # the final silhouette size.
        size = cfg.close_radius * 2 + 1
        mask_img = mask_img.filter(ImageFilter.MaxFilter(size)).filter(ImageFilter.MinFilter(size))

    mask = np.array(mask_img) > 0
    if cfg.remove_frame_components:
        mask = _remove_frame_components(mask)
    if cfg.fill_holes:
        mask = _fill_binary_holes(mask)

    return Image.fromarray((mask.astype(np.uint8) * 255), "L")


def _estimate_corner_background_luminance(lum: np.ndarray, sample: int = 32) -> float:
    h, w = lum.shape
    s = max(4, min(sample, h // 4, w // 4))
    corners = np.concatenate([
        lum[:s, :s].reshape(-1),
        lum[:s, -s:].reshape(-1),
        lum[-s:, :s].reshape(-1),
        lum[-s:, -s:].reshape(-1),
    ])
    return float(np.median(corners))


def luminance_to_alpha(img: Image.Image, cfg: ServiceIconPostprocessConfig) -> Image.Image:
    rgba = np.array(img.convert("RGBA")).astype(np.float32)
    rgb = rgba[:, :, :3]
    src_alpha = rgba[:, :, 3] / 255.0
    lum = 0.2126 * rgb[:, :, 0] + 0.7152 * rgb[:, :, 1] + 0.0722 * rgb[:, :, 2]

    bg_lum = _estimate_corner_background_luminance(lum)

    if bg_lum >= 128:
        # SDXL sometimes ignores "white pictogram on black" and produces black
        # line art on a white square. Treat bright corners as background and turn
        # dark marks into the white foreground alpha.
        alpha = (bg_lum - lum) / max(1, bg_lum - cfg.black_cutoff)
    else:
        # Training-data-like case: black/dark background, white symbol.
        alpha = (lum - bg_lum) / max(1, cfg.white_point - bg_lum)

    alpha = np.clip(alpha, 0.0, 1.0)
    alpha = np.power(alpha, cfg.alpha_gamma)
    alpha = alpha * src_alpha

    out = np.zeros((*alpha.shape, 4), dtype=np.uint8)
    out[:, :, :3] = 255
    out[:, :, 3] = np.clip(alpha * 255.0, 0, 255).astype(np.uint8)

    result = Image.fromarray(out, "RGBA")
    result.putalpha(_solidify_alpha(result.getchannel("A"), cfg))
    if cfg.feather_radius > 0:
        # Optional edge feathering. Default is 0 because service icons should be
        # solid white pictograms, not semi-transparent line art.
        a = result.getchannel("A").filter(ImageFilter.GaussianBlur(cfg.feather_radius))
        result.putalpha(a)
    return result


def center_on_canvas(img: Image.Image, cfg: ServiceIconPostprocessConfig) -> Image.Image:
    img = img.convert("RGBA")
    alpha = np.array(img.getchannel("A"))
    bbox = _largest_bbox(alpha)
    canvas = Image.new("RGBA", (cfg.output_size, cfg.output_size), (255, 255, 255, 0))
    if bbox is None:
        return canvas

    subject = img.crop(bbox)
    sw, sh = subject.size
    if sw <= 0 or sh <= 0:
        return canvas

    target = max(1, int(cfg.output_size * cfg.target_fill))
    scale = min(target / sw, target / sh)
    nw, nh = max(1, int(round(sw * scale))), max(1, int(round(sh * scale)))
    subject = subject.resize((nw, nh), Image.LANCZOS)

    x = (cfg.output_size - nw) // 2
    y = (cfg.output_size - nh) // 2
    canvas.alpha_composite(subject, (x, y))
    return canvas


def process_image(input_path: Path, output_path: Path, cfg: ServiceIconPostprocessConfig) -> Path:
    img = Image.open(input_path).convert("RGBA")
    flat = luminance_to_alpha(img, cfg)
    final = center_on_canvas(flat, cfg)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Remove dark background and make a flat transparent white Civ VI service icon.")
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--size", type=int, default=256)
    parser.add_argument("--target-fill", type=float, default=0.78)
    parser.add_argument("--black-cutoff", type=int, default=22)
    parser.add_argument("--white-point", type=int, default=210)
    parser.add_argument("--alpha-gamma", type=float, default=0.75)
    args = parser.parse_args()

    cfg = ServiceIconPostprocessConfig(
        output_size=args.size,
        target_fill=args.target_fill,
        black_cutoff=args.black_cutoff,
        white_point=args.white_point,
        alpha_gamma=args.alpha_gamma,
    )
    out = process_image(args.input, args.output, cfg)
    print(out)


if __name__ == "__main__":
    main()
