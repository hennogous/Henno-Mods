"""Composite visually authored image-space paths without repainting the source.

The manifest contains canvas, paths (SVG M/L/Q/C/Z), interior_width,
outer_radius and inner_radius, all in source-image pixels. No segmentation model
or Blender geometry is required. Paths must be reviewed for each camera view.
"""
import argparse
import json
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


def points_from_path(path):
    tokens = re.findall(r"[MLQCZ]|-?\d+(?:\.\d+)?", path)
    points, current, start, index = [], (0, 0), None, 0
    while index < len(tokens):
        command = tokens[index]
        index += 1
        count = {"M": 2, "L": 2, "Q": 4, "C": 6, "Z": 0}[command]
        values = list(map(float, tokens[index:index + count]))
        index += count
        if command in ("M", "L"):
            current = tuple(values)
            start = current if command == "M" else start
            points.append(current)
        elif command == "Z":
            current = start
            points.append(start)
        else:
            origin = current
            controls = [tuple(values[i:i + 2]) for i in range(0, count, 2)]
            for step in range(1, 65):
                t = step / 64
                if command == "Q":
                    p, q = controls
                    point = tuple((1-t)**2*origin[k] + 2*(1-t)*t*p[k] + t*t*q[k] for k in range(2))
                else:
                    p, q, r = controls
                    point = tuple((1-t)**3*origin[k] + 3*(1-t)**2*t*p[k] + 3*(1-t)*t*t*q[k] + t**3*r[k] for k in range(2))
                points.append(point)
            current = controls[-1]
    return points


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text(encoding="utf-8-sig"))
    base = Image.open(args.source).convert("RGBA")
    if list(base.size) != data["canvas"]:
        raise ValueError("Manifest coordinates do not match the source canvas")
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    scale = 4
    mask_hi = Image.new("L", (base.width*scale, base.height*scale))
    draw = ImageDraw.Draw(mask_hi)
    width = data["interior_width"]
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {base.width} {base.height}">']
    for path in data["paths"]:
        pts = [(x*scale, y*scale) for x, y in points_from_path(path["d"])]
        draw.line(pts, fill=255, width=round(width*scale), joint="curve")
        radius = width*scale/2
        for x, y in (pts[0], pts[-1]):
            draw.ellipse((x-radius, y-radius, x+radius, y+radius), fill=255)
        svg.append(f'<path d="{path["d"]}" fill="none" stroke="black" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>')
    svg.append('</svg>')
    (out / "Interior_Outlines.svg").write_text("\n".join(svg), encoding="utf-8")
    interior = mask_hi.resize(base.size, Image.Resampling.LANCZOS)
    alpha = base.getchannel("A")
    dilated = alpha.filter(ImageFilter.MaxFilter(2*data["outer_radius"]+1))
    eroded = alpha.filter(ImageFilter.MinFilter(2*data["inner_radius"]+1))
    a = np.asarray(alpha, dtype=np.float32)/255
    internal_alpha = np.rint(np.asarray(interior)*a).astype(np.uint8)
    inner_border = np.maximum(np.asarray(alpha, dtype=np.int16)-np.asarray(eroded, dtype=np.int16), 0).astype(np.uint8)
    ink = Image.new("RGBA", base.size, (0, 0, 0, 0))
    ink.putalpha(Image.fromarray(np.maximum(internal_alpha, inner_border)))
    result = Image.new("RGBA", base.size, (0, 0, 0, 0))
    result.putalpha(dilated)
    result.alpha_composite(base)
    result.alpha_composite(ink)
    result.save(out / "Tailor_Outlined_Render.png")
    ink.save(out / "Outline_Overlay.png")
    interior.save(out / "Interior_Mask.png")
    bbox = result.getbbox()
    def fit(im, size):
        im = im.crop(bbox)
        im.thumbnail((round(size*.91), round(size*.91)), Image.Resampling.LANCZOS)
        canvas = Image.new("RGBA", (size, size))
        canvas.alpha_composite(im, ((size-im.width)//2, (size-im.height)//2))
        return canvas
    for size in (256, 50):
        fit(result, size).save(out / f"Tailor_Outlined_{size}.png")
    sheet = Image.new("RGB", (1080, 610), (55, 58, 61))
    draw = ImageDraw.Draw(sheet)
    font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 20)
    for x, label, im in ((0, "Original Blender render", base), (540, "Same render + selected outlines", result)):
        preview = fit(im, 530)
        sheet.paste(preview, (x+5, 5), preview)
        draw.text((x+20, 538), label, font=font, fill="white")
        small = fit(im, 50)
        sheet.paste(small, (x+455, 550), small)
    sheet.save(out / "Before_After.png")
    # Verify that all pixels outside the ink and silhouette treatment are intact.
    unchanged = (internal_alpha == 0) & (inner_border == 0) & (np.asarray(alpha) == 255)
    before, after = np.asarray(base), np.asarray(result)
    assert np.array_equal(before[unchanged], after[unchanged])
    report = {"source": str(args.source), "path_count": len(data["paths"]),
              "interior_width": width, "unpainted_opaque_pixels_verified": int(unchanged.sum()),
              "method": "Visually authored image-space paths; alpha silhouette; no image synthesis or geometry"}
    (out / "verification.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
