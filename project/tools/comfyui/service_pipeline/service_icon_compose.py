"""Compose one or two flat-white CSC service pictograms on a 256px canvas.

The primary concept is always fully opaque. An optional secondary concept is
placed behind it at 80% opacity. The combined silhouette is centered and fitted
to the measured Bakers service-icon scale by default (179px maximum extent).
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter


@dataclass(frozen=True)
class LayerPlacement:
    scale: float = 1.0
    x: float = 0.0
    y: float = 0.0
    opacity: float = 1.0


def _bbox(alpha: np.ndarray, threshold: int = 0) -> tuple[int, int, int, int] | None:
    ys, xs = np.where(alpha > threshold)
    if not len(xs):
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _cropped_white_symbol(path: Path) -> Image.Image:
    image = Image.open(path).convert("RGBA")
    alpha = np.asarray(image.getchannel("A"), dtype=np.uint8)
    box = _bbox(alpha, threshold=8)
    if box is None:
        raise ValueError(f"No visible pictogram in {path}")
    symbol = image.crop(box)
    white = Image.new("RGBA", symbol.size, (255, 255, 255, 0))
    white.putalpha(symbol.getchannel("A"))
    return white


def _prepare_layer(
    path: Path,
    placement: LayerPlacement,
    reference_extent: int,
) -> Image.Image:
    symbol = _cropped_white_symbol(path)
    target = max(1, round(reference_extent * placement.scale))
    scale = target / max(symbol.size)
    size = (max(1, round(symbol.width * scale)), max(1, round(symbol.height * scale)))
    symbol = symbol.resize(size, Image.Resampling.LANCZOS)
    alpha = np.asarray(symbol.getchannel("A"), dtype=np.float32)
    alpha = np.floor(alpha * placement.opacity + 0.5).clip(0, 255).astype(np.uint8)
    symbol.putalpha(Image.fromarray(alpha, "L"))
    return symbol


def compose_service_icon(
    primary_path: Path,
    output_path: Path,
    secondary_path: Path | None = None,
    *,
    canvas_size: int = 256,
    target_extent: int = 179,
    separation: int = 8,
    primary: LayerPlacement = LayerPlacement(),
    secondary: LayerPlacement = LayerPlacement(scale=0.58, x=0.23, y=-0.23, opacity=0.80),
) -> Path:
    """Compose symbols, fit their combined bounds, and center the result.

    Layer x/y offsets are fractions of ``target_extent``. Positive x moves
    right; positive y moves down. The secondary layer is composited first.
    """
    if not 0 < primary.opacity <= 1:
        raise ValueError("Primary opacity must be in (0, 1]")
    if not 0 < secondary.opacity <= 1:
        raise ValueError("Secondary opacity must be in (0, 1]")

    stage_size = canvas_size * 3
    primary_stage = Image.new("RGBA", (stage_size, stage_size), (255, 255, 255, 0))
    secondary_stage = Image.new("RGBA", (stage_size, stage_size), (255, 255, 255, 0))
    center = stage_size // 2

    def place(path: Path, spec: LayerPlacement, destination: Image.Image) -> None:
        layer = _prepare_layer(path, spec, target_extent)
        x = round(center - layer.width / 2 + spec.x * target_extent)
        y = round(center - layer.height / 2 + spec.y * target_extent)
        destination.alpha_composite(layer, (x, y))

    if secondary_path is not None:
        place(secondary_path, secondary, secondary_stage)
    place(primary_path, primary, primary_stage)

    combined_alpha = np.maximum(
        np.asarray(primary_stage.getchannel("A"), dtype=np.uint8),
        np.asarray(secondary_stage.getchannel("A"), dtype=np.uint8),
    )
    group_box = _bbox(combined_alpha)
    if group_box is None:
        raise ValueError("Composed icon is empty")
    primary_group = primary_stage.crop(group_box)
    secondary_group = secondary_stage.crop(group_box)
    fit = target_extent / max(primary_group.size)
    fitted_size = (max(1, round(primary_group.width * fit)), max(1, round(primary_group.height * fit)))
    primary_group = primary_group.resize(fitted_size, Image.Resampling.LANCZOS)
    secondary_group = secondary_group.resize(fitted_size, Image.Resampling.LANCZOS)

    if secondary_path is not None and separation > 0:
        primary_core = primary_group.getchannel("A").point(lambda value: 255 if value >= 16 else 0)
        halo = primary_core.filter(ImageFilter.MaxFilter(separation * 2 + 1))
        secondary_alpha = np.asarray(secondary_group.getchannel("A"), dtype=np.uint8).copy()
        secondary_alpha[np.asarray(halo) > 0] = 0
        secondary_group.putalpha(Image.fromarray(secondary_alpha, "L"))

    canvas = Image.new("RGBA", (canvas_size, canvas_size), (255, 255, 255, 0))
    position = ((canvas_size - fitted_size[0]) // 2, (canvas_size - fitted_size[1]) // 2)
    canvas.alpha_composite(secondary_group, position)
    canvas.alpha_composite(primary_group, position)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("primary", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--secondary", type=Path)
    parser.add_argument("--target-extent", type=int, default=179)
    parser.add_argument("--separation", type=int, default=8)
    parser.add_argument("--primary-scale", type=float, default=1.0)
    parser.add_argument("--primary-x", type=float, default=0.0)
    parser.add_argument("--primary-y", type=float, default=0.0)
    parser.add_argument("--secondary-scale", type=float, default=0.58)
    parser.add_argument("--secondary-x", type=float, default=0.23)
    parser.add_argument("--secondary-y", type=float, default=-0.23)
    args = parser.parse_args()

    output = compose_service_icon(
        args.primary,
        args.output,
        args.secondary,
        target_extent=args.target_extent,
        separation=args.separation,
        primary=LayerPlacement(args.primary_scale, args.primary_x, args.primary_y, 1.0),
        secondary=LayerPlacement(
            args.secondary_scale,
            args.secondary_x,
            args.secondary_y,
            0.80,
        ),
    )
    print(output)


if __name__ == "__main__":
    main()
