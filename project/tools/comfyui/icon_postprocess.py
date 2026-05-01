"""
Icon post-processing: rembg background removal + structural outlines + silhouette outline + centering.
Can be run standalone on existing raw images.
Usage: python icon_postprocess.py <input.png> [output.png]
"""
import sys, os
import numpy as np
from PIL import Image, ImageFilter, ImageOps
from rembg import remove


def remove_background(img):
    """Remove background using rembg (U2-Net)."""
    return remove(img)


def add_structural_outlines(img, low=60, high=140, line_width=1):
    """Paint solid black lines on structural edges using OpenCV Canny on the generated image.
    Runs after bg removal so edges are clean — no background noise."""
    import cv2
    arr = np.array(img).copy()
    alpha = arr[:, :, 3]
    opaque = alpha > 128

    # Canny on the RGB of the generated image
    rgb_arr = arr[:, :, :3]
    gray = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    edges = cv2.Canny(blurred, low, high)

    # Optional: dilate slightly for visible line width
    if line_width > 1:
        kernel = np.ones((line_width, line_width), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)

    edge_mask = (edges > 0) & opaque
    arr[edge_mask, 0] = 15
    arr[edge_mask, 1] = 15
    arr[edge_mask, 2] = 15

    return Image.fromarray(arr)


def add_silhouette_outline(img, thickness=14, color=(15, 15, 15, 255)):
    """Thick black outline around the entire building silhouette using OpenCV dilation."""
    import cv2
    arr = np.array(img)
    alpha = arr[:, :, 3]
    original_opaque = alpha > 64

    # Binary mask → dilate with circular kernel for smooth outline
    mask = original_opaque.astype(np.uint8) * 255
    radius = thickness
    kernel_size = radius * 2 + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    dilated = cv2.dilate(mask, kernel, iterations=1)
    outline_region = (dilated > 128) & ~original_opaque

    h, w = arr.shape[:2]
    result = np.zeros((h, w, 4), dtype=np.uint8)
    result[outline_region] = list(color)
    result[original_opaque] = arr[original_opaque]

    return Image.fromarray(result)


def center_on_canvas(img, canvas_size=1024, padding=160):
    """Center content on a larger transparent canvas with breathing room."""
    arr = np.array(img)
    alpha = arr[:, :, 3]

    # Use a high threshold (128) to ignore faint rembg artifact pixels
    # that can throw off the bounding box far from the actual building
    solid = alpha > 128
    rows = np.any(solid, axis=1)
    cols = np.any(solid, axis=0)

    if not rows.any():
        return img

    rmin, rmax = np.where(rows)[0][[0, -1]]
    cmin, cmax = np.where(cols)[0][[0, -1]]

    # Add a small margin so the silhouette outline isn't clipped
    margin = 8
    rmin = max(0, rmin - margin)
    rmax = min(arr.shape[0] - 1, rmax + margin)
    cmin = max(0, cmin - margin)
    cmax = min(arr.shape[1] - 1, cmax + margin)

    content = img.crop((cmin, rmin, cmax + 1, rmax + 1))
    cw, ch = content.size

    # Scale to fit within canvas minus padding — always rescale
    # Use a fixed target size rather than a cap, so the building
    # always has consistent margins regardless of content width
    target_dim = canvas_size - padding * 2   # e.g. 1024 - 2*160 = 704
    scale = min(target_dim / cw, target_dim / ch)
    new_w = int(cw * scale)
    new_h = int(ch * scale)
    content = content.resize((new_w, new_h), Image.LANCZOS)
    cw, ch = new_w, new_h

    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    x = (canvas_size - cw) // 2
    y = (canvas_size - ch) // 2
    canvas.paste(content, (x, y), content)
    return canvas


def pad_image(img, pad=128):
    """Add transparent padding around the image before bg removal.
    This gives rembg clear context that the edges are background,
    and gives the centering step room to work with."""
    w, h = img.size
    canvas = Image.new("RGBA", (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    # Fill pad area with the average edge color so rembg sees a clean background
    # Use a solid neutral gray for the pad to help rembg distinguish subject
    bg = Image.new("RGBA", (w + pad * 2, h + pad * 2), (100, 100, 100, 255))
    rgb = img.convert("RGB")
    bg.paste(rgb, (pad, pad))
    # Convert back to RGBA for rembg
    return bg.convert("RGBA"), pad


def process_icon(input_path, output_path):
    """Full pipeline: pad → remove bg → structural outlines → silhouette → center."""
    print(f"Processing: {input_path}")
    img = Image.open(input_path).convert("RGBA")

    print("  0. Padding image edges...")
    img, pad_amount = pad_image(img, pad=150)

    print("  1. Removing background (rembg)...")
    img = remove_background(img)
    
    print("  2. SAM per-region + outer outlines...")
    try:
        import importlib.util as _ilu, os as _os
        _spec = _ilu.spec_from_file_location("sam_outline", _os.path.join(_os.path.dirname(__file__), "sam_outline.py"))
        _sam = _ilu.module_from_spec(_spec); _spec.loader.exec_module(_sam)
        img = _sam.apply_sam_outlines(img)
    except Exception as e:
        print(f"  SAM failed ({e}), falling back to silhouette-only")
        img = add_silhouette_outline(img, thickness=14)

    print("  3. Centering on 1024x1024 canvas...")
    img = center_on_canvas(img, canvas_size=1024, padding=160)

    img.save(output_path)
    print(f"  Done: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Process all raw icon files in tmp/
        import glob
        raws = sorted(glob.glob(r"C:\Users\Shadow\.openclaw\workspace\tmp\icon_v2_raw_*.png"))
        if not raws:
            print("No raw icon files found. Pass an input path as argument.")
            sys.exit(1)
        for raw in raws:
            idx = raw.split("_")[-1].replace(".png", "")
            out = os.path.join(os.path.dirname(raw), f"icon_v2_{idx}.png")
            process_icon(raw, out)
    else:
        inp = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else inp.replace(".png", "_icon.png")
        process_icon(inp, out)
