"""Build lens backing textures and close-button states."""

import argparse
import io
import math
from bisect import bisect_right
from pathlib import Path

from PIL import Image
from build_chevron_art import dds_rgba_mips


MOD = Path(__file__).resolve().parents[3] / "Civ Supply Chains"
TEXTURES = MOD / "Textures"
BACKING_SIZE = 256
WORK_SIZE = 300
CONTOUR_SIZE = 215
# Slot zero's measured half-alpha contour in the 70 px Quarter atlases.
CONTOUR = ((35, 0), (65, 17.5), (65, 52), (35, 69.5), (5, 52), (5, 17.5))
CLOSE_FRAME_SIZE = 134  # Matches CloseQuarterFocus and its state increment.


# Measured against the stock medallion in the 300 px design coordinates.
# The hex uses a continuous rise from the inner lip to the lit bevel.
HEX_BEVEL = (
    (0.0, (50, 34, 23), (33, 23, 19)),
    (1.3, (120, 90, 55), (74, 49, 32)),
    (8.0, (211, 180, 122), (135, 99, 67)),
    (12.0, (242, 218, 161), (156, 119, 81)),
    (14.0, (248, 230, 181), (161, 121, 84)),
    (15.3, (202, 170, 115), (124, 88, 61)),
    (18.0, (128, 94, 57), (86, 58, 41)),
    (20.0, (71, 48, 34), (53, 33, 27)),
    (21.5, (39, 27, 22), (32, 22, 19)),
)
# Keep the narrow stock-inspired inner accent on the round Service backing.
ROUND_BEVEL = HEX_BEVEL[:2] + (
    (3.5, (217, 190, 137), (146, 106, 67)),
    (4.2, (232, 208, 154), (152, 112, 74)),
    (5.2, (176, 141, 89), (112, 80, 55)),
) + HEX_BEVEL[2:]
OUTER_EDGE = HEX_BEVEL[-1][0]


def quarter_edges():
    contour = [((x - 35) * CONTOUR_SIZE / 70, (y - 35) * CONTOUR_SIZE / 70) for x, y in CONTOUR]
    edges = []
    for (ax, ay), (bx, by) in zip(contour, contour[1:] + contour[:1]):
        length = math.hypot(bx - ax, by - ay)
        nx, ny = (by - ay) / length, (ax - bx) / length
        edges.append((nx, ny, nx * ax + ny * ay))
    return edges


def metal(distance, light, top_lift, bevel, depths):
    index = min(bisect_right(depths, distance), len(bevel) - 1)
    low, light_low, dark_low = bevel[index - 1]
    high, light_high, dark_high = bevel[index]
    blend = (distance - low) / (high - low)
    color = tuple(
        (dl * (1 - light) + ll * light) * (1 - blend) + (dh * (1 - light) + lh * light) * blend
        for ll, dl, lh, dh in zip(light_low, dark_low, light_high, dark_high)
    )
    # Lift the lit bevel more than the dark inner and outer cuts.
    highlight = top_lift * (color[0] / 255) ** 2
    return tuple(min(255, round(value + strength * highlight)) for value, strength in zip(color, (16, 20, 22)))


def render_backing(navy_source, edges=None):
    """Draw the round or hex bevel from continuous geometry."""
    # Only the navy well samples the stock texture. Draw the brass and
    # silhouette at twice the final resolution, then antialias on output.
    stock = navy_source.resize((WORK_SIZE, WORK_SIZE), Image.Resampling.BICUBIC)
    pixels = stock.load()
    center = (WORK_SIZE - 1) / 2
    samples = BACKING_SIZE * 2
    output = Image.new("RGBA", (samples, samples))
    result = output.load()
    bevel = ROUND_BEVEL if edges is None else HEX_BEVEL
    depths = tuple(stop[0] for stop in bevel)
    for y in range(samples):
        dy = (y + .5) * WORK_SIZE / samples - WORK_SIZE / 2
        for x in range(samples):
            dx = (x + .5) * WORK_SIZE / samples - WORK_SIZE / 2
            radius = math.hypot(dx, dy)
            if edges is None:
                # Keep the stock circle's slight optical offset.
                distance = math.hypot(dx + 2, dy + 1) - 101
            else:
                distance = max(nx * dx + ny * dy - offset for nx, ny, offset in edges)
            if distance < 0:
                factor = min(1, 93 / radius)
                r, g, b, _ = pixels[round(center + dx * factor), round(center + dy * factor)]
                shade = min(1, .52 - distance / 12)
                result[x, y] = round(r * shade), round(g * shade), round(b * shade), 255
            elif distance <= OUTER_EDGE:
                light = math.sqrt(.5 - .5 * dy / radius)
                top_lift = max(0, -dy / radius) ** 2
                result[x, y] = (*metal(distance, light, top_lift, bevel, depths), 255)
            elif distance < OUTER_EDGE + 16:
                # A short shadow separates the hard metal edge from terrain.
                result[x, y] = (0, 0, 0, round(100 * math.exp(-(distance - OUTER_EDGE) / 4.5)))
    return output.resize((BACKING_SIZE, BACKING_SIZE), Image.Resampling.LANCZOS)


def grayscale(image):
    r, g, b, a = image.split()
    luminance = Image.merge("RGB", (r, g, b)).convert("L", (.2126, .7152, .0722, 0))
    return Image.merge("RGBA", (luminance, luminance, luminance, a))


def close_button(source):
    with Image.open(source) as texture:
        frames = texture.convert("RGBA")
    width, height = frames.size
    result = Image.new("RGBA", (CLOSE_FRAME_SIZE, height // width * CLOSE_FRAME_SIZE))
    # Resize each state separately to keep adjacent states out of the filter.
    for state, y in enumerate(range(0, height, width)):
        frame = frames.crop((0, y, width, y + width))
        result.paste(frame.resize((CLOSE_FRAME_SIZE, CLOSE_FRAME_SIZE), Image.Resampling.LANCZOS),
                     (0, state * CLOSE_FRAME_SIZE))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("medallion", type=Path, help="SDK ActionPanel_Notification2.dds")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    with Image.open(args.medallion) as source:
        navy_source = source.convert("RGBA")
    circle = render_backing(navy_source)
    hexagon = render_backing(navy_source, quarter_edges())
    assets = {
        "CSC_ServiceMedallion.dds": circle,
        "CSC_ServiceMedallionGray.dds": grayscale(circle),
        "CSC_QuarterLensBacking.dds": hexagon,
        "CSC_QuarterLensBackingGray.dds": grayscale(hexagon),
    }
    encoded = {name: dds_rgba_mips(image) for name, image in assets.items()}
    # The close strip contains four button states, so leave it single-level
    # to keep the neighboring states out of each other's texels.
    close = close_button(args.medallion.with_name("Controls_CloseButtonAltSmall.dds"))
    payload = io.BytesIO()
    close.save(payload, format="DDS")
    encoded["CSC_QuarterLensClose.dds"] = payload.getvalue()
    for name, data in encoded.items():
        output = TEXTURES / name
        if args.check:
            if output.read_bytes() != data:
                raise SystemExit(f"Regenerate {output.name}")
        elif not output.exists() or output.read_bytes() != data:
            output.write_bytes(data)


if __name__ == "__main__":
    main()
