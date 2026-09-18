from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from service_icon_compose import LayerPlacement, compose_service_icon


def _symbol(path: Path, shape: str) -> None:
    image = Image.new("RGBA", (128, 128), (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    if shape == "primary":
        draw.rectangle((24, 12, 103, 115), fill=(255, 255, 255, 255))
    else:
        draw.ellipse((20, 20, 107, 107), fill=(255, 255, 255, 255))
    image.save(path)


def test_composition_uses_measured_extent_and_two_opacities(tmp_path: Path) -> None:
    primary = tmp_path / "primary.png"
    secondary = tmp_path / "secondary.png"
    output = tmp_path / "output.png"
    _symbol(primary, "primary")
    _symbol(secondary, "secondary")

    compose_service_icon(
        primary,
        output,
        secondary,
        primary=LayerPlacement(scale=0.72, x=-0.18, y=0.12, opacity=1.0),
        secondary=LayerPlacement(scale=0.55, x=0.22, y=-0.22, opacity=0.80),
    )

    alpha = np.asarray(Image.open(output).getchannel("A"))
    ys, xs = np.where(alpha > 0)
    assert max(xs.max() - xs.min() + 1, ys.max() - ys.min() + 1) == 179
    assert alpha.max() == 255
    assert np.any((alpha >= 201) & (alpha <= 207))
    assert abs((xs.min() + xs.max()) / 2 - 127.5) <= 1
    assert abs((ys.min() + ys.max()) / 2 - 127.5) <= 1
