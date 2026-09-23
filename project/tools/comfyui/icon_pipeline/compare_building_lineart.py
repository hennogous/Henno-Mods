"""Compare registered Blender Freestyle passes against existing icon processing.

Reuses a saved raw ComfyUI image; does not run or modify diffusion settings.
All line compositing precedes the existing silhouette/crop/resize operations.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import icon_img2img as generator
import icon_postprocess as pp


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("trial_dir", type=Path)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--raw", required=True, type=Path)
    parser.add_argument("--sam-reference", required=True, type=Path)
    args = parser.parse_args()
    root = args.trial_dir.resolve()
    source = Image.open(args.input).convert("RGBA")
    render = Image.open(root / "Blender_Color.png").convert("RGBA")
    if source.size != render.size or not np.array_equal(np.asarray(source.getchannel("A")),
                                                       np.asarray(render.getchannel("A"))):
        raise ValueError("Blender render and img2img input alpha differ; exact registration is not established")
    raw = generator.apply_alpha_mask(args.raw.read_bytes(), generator.make_generation_mask(str(args.input)))
    raw.save(root / "Comfy_Raw_Registered.png")
    graded = pp.apply_color_correction(raw) if pp.ENABLE_COLOR_CORRECTION else raw
    graded.save(root / "Comfy_Graded_1024.png")
    if pp.FINAL_TARGET_SATURATION > 0:
        raise ValueError("This comparison expects the current default final saturation setting")

    def finish(image):
        image = pp.add_silhouette_outline(image, thickness=pp.OUTLINE_THICKNESS)
        return pp.center_on_canvas(image, canvas_size=pp.CENTER_CANVAS_SIZE, padding=pp.CENTER_PADDING)

    finish(graded).save(root / "Tailor_NoSAM.png")
    variants = []
    guides = json.loads((root / "projected_edge_guides.json").read_text())
    render_manifest = json.loads((root / "render_manifest.json").read_text())
    widths = {label: (major, minor) for label, major, minor in render_manifest["strengths"]}
    for label in ("Light", "Medium", "Bold"):
        rendered = Image.open(root / ("Freestyle_" + label + ".png")).convert("RGBA")
        if rendered.size != graded.size:
            raise ValueError("Line pass resolution does not match working image")
        rgba = np.asarray(rendered).astype(np.float32) / 255
        coverage = (1 - rgba[:, :, :3].mean(axis=2)) * rgba[:, :, 3]
        # Freestyle occasionally misidentifies an edge during tessellation of
        # imported meshes. Keep its visibility and antialiasing, but accept ink
        # only near projected, explicitly selected 3D edges. For small props,
        # all mesh edges are eligible; Freestyle still chooses visible contours.
        support = Image.new("L", graded.size, 0)
        pen = ImageDraw.Draw(support)
        for group, width in zip(("architecture", "props"), widths[label]):
            radius = (width + 2) / 2
            for x1, y1, x2, y2 in guides[group]:
                pen.line((x1, y1, x2, y2), fill=255, width=math.ceil(width + 2))
                for x, y in ((x1, y1), (x2, y2)):
                    pen.ellipse((x-radius, y-radius, x+radius, y+radius), fill=255)
        coverage *= np.asarray(support, dtype=np.float32) / 255
        coverage *= np.asarray(raw.getchannel("A"), dtype=np.float32) / 255
        mask = Image.fromarray(np.rint(coverage * 255).astype(np.uint8), "L")
        mask.save(root / ("Lines_" + label + "_1024.png"))
        line_layer = Image.new("RGBA", graded.size, (0, 0, 0, 0))
        line_layer.putalpha(mask)
        combined = Image.alpha_composite(graded, line_layer)
        # Line drawing never changes the source alpha; its only effect is color.
        combined.putalpha(graded.getchannel("A"))
        combined.save(root / ("Tailor_" + label + "_1024.png"))
        icon = finish(combined)
        icon.save(root / ("Tailor_" + label + "_256.png"))
        icon.resize((50, 50), Image.Resampling.LANCZOS).save(root / ("Tailor_" + label + "_50.png"))
        variants.append((label + " — Blender", icon))
    sam = Image.open(args.sam_reference).convert("RGBA")
    sam.save(root / "Tailor_SAM_256.png")
    variants.append(("Current SAM", sam))

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    sheet = Image.new("RGB", (4 * 286, 358), (36, 39, 42))
    draw = ImageDraw.Draw(sheet)
    for i, (label, icon) in enumerate(variants):
        x = 286 * i + 15
        panel = Image.new("RGBA", icon.size, (70, 74, 78, 255))
        panel.alpha_composite(icon)
        sheet.paste(panel.convert("RGB"), (x, 10))
        draw.text((x, 276), label, font=font, fill="white")
        small = icon.resize((50, 50), Image.Resampling.LANCZOS)
        panel = Image.new("RGBA", (50, 50), (70, 74, 78, 255))
        panel.alpha_composite(small)
        sheet.paste(panel.convert("RGB"), (x, 304))
        draw.text((x + 60, 317), "50 px", font=font, fill=(190, 195, 200))
    sheet.save(root / "Tailor_Freestyle_Comparison.png")
    report = {
        "source_input": str(args.input.resolve()), "raw_comfy_image": str(args.raw.resolve()),
        "raw_sha256": hashlib.sha256(args.raw.read_bytes()).hexdigest(),
        "registration": "Source alpha exactly equals current Blender color-render alpha at 1024x1024",
        "processing": "Existing grade, Freestyle black line composite at 1024, existing silhouette and centering",
        "line_strengths": ["Light", "Medium", "Bold"],
        "sam_reference": str(args.sam_reference.resolve()),
    }
    (root / "comparison_manifest.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
