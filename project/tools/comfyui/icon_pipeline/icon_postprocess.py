"""
Icon post-processing: optional background removal, Canny crease overlay,
structural outlines, SAM outlines, silhouette outline, and canvas centering.
Can be run standalone on existing raw images.
Usage: python icon_postprocess.py <input.png> [output.png] [canny.png]
"""
import sys, os
import numpy as np
from PIL import Image

from icon_utils import env_bool, scale_like_comfy_center

# -----------------------------------------------------------------------------
# Post-processing effect toggles
# -----------------------------------------------------------------------------
# These are the master switches. Edit them here for normal use, or override with
# env vars of the same name when running quick tests.
ENABLE_BACKGROUND_REMOVAL = env_bool("CSC_ICON_ENABLE_BACKGROUND_REMOVAL", True)
ENABLE_PADDING_BEFORE_REMBG = env_bool("CSC_ICON_ENABLE_PADDING_BEFORE_REMBG", True)
ENABLE_CANNY_CREASE_OVERLAY = env_bool("CSC_ICON_ENABLE_CANNY_CREASE_OVERLAY", False)
ENABLE_COLOR_CORRECTION = env_bool("CSC_ICON_ENABLE_COLOR_CORRECTION", True)
ENABLE_STRUCTURAL_OUTLINES = env_bool("CSC_ICON_ENABLE_STRUCTURAL_OUTLINES", False)
ENABLE_SAM_OUTLINES = env_bool("CSC_ICON_ENABLE_SAM_OUTLINES", True)
ENABLE_SILHOUETTE_OUTLINE = env_bool("CSC_ICON_ENABLE_SILHOUETTE_OUTLINE", True)
ENABLE_CENTER_ON_CANVAS = env_bool("CSC_ICON_ENABLE_CENTER_ON_CANVAS", True)

# -----------------------------------------------------------------------------
# Effect settings
# -----------------------------------------------------------------------------
DROPZONE_DIR = os.environ.get(
    "CSC_COMFYUI_OUTPUT_DIR",
    r"C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\ComfyUI output"
)
REMBG_PAD = int(os.environ.get("CSC_ICON_REMBG_PAD", "150"))
# Higher = more border/context before rembg; lower = tighter/faster but edge cuts are more likely. (0-300 px; 100-180 useful, low/medium sensitivity)

CENTER_CANVAS_SIZE = int(os.environ.get("CSC_ICON_CENTER_CANVAS_SIZE", "256"))
# Higher = larger final PNG canvas; lower = smaller output canvas. 256 is the current CSC icon target.

CENTER_PADDING = int(os.environ.get("CSC_ICON_CENTER_PADDING", "20"))
# Higher = smaller icon with more transparent margin; lower = larger icon, closer to canvas edge. (0-80 px useful at 256px output, very visible)

OUTLINE_THICKNESS = int(os.environ.get("CSC_ICON_OUTLINE_THICKNESS", "15"))
# Higher = thicker outer black silhouette; lower = thinner, subtler outline. (1-40 px; 12-24 useful, very sensitive)

OUTLINE_ALPHA_THRESHOLD = int(os.environ.get("CSC_ICON_OUTLINE_ALPHA_THRESHOLD", "220"))
# Higher = outline hugs solid pixels tighter; lower = outline follows softer rembg fringe. (0-255; 160-220 useful, sensitive)

INNER_OUTLINE_WIDTH = int(os.environ.get("CSC_ICON_INNER_OUTLINE_WIDTH", "5"))
# Higher = thicker interior structural lines; lower = finer/lighter detail lines. (1-12 px; 3-6 useful, very sensitive)

INNER_OUTLINE_LOW = int(os.environ.get("CSC_ICON_INNER_OUTLINE_LOW", "20"))
# Higher = fewer weak interior edges; lower = more faint/noisy edges included. (0-255; 15-60 useful, medium sensitivity)

INNER_OUTLINE_HIGH = int(os.environ.get("CSC_ICON_INNER_OUTLINE_HIGH", "50"))
# Higher = only stronger interior edges survive; lower = more medium edges become lines. (0-255; 40-120 useful, medium sensitivity)

INNER_OUTLINE_MIN_AREA = int(os.environ.get("CSC_ICON_INNER_OUTLINE_MIN_AREA", "8"))
# Higher = filters small speckles/details; lower = keeps more tiny edge fragments. (1-100 px area; 6-25 useful, medium sensitivity)

CREASE_OPACITY = float(os.environ.get("CSC_ICON_CREASE_OPACITY", "0.3"))
# Higher = darker Canny crease overlay; lower = subtler/lighter creases. (0-1; 0.25-0.7 useful, sensitive)

CREASE_WIDTH = int(os.environ.get("CSC_ICON_CREASE_WIDTH", "3"))
# Higher = thicker Canny crease lines; lower = thinner crease lines. (1-10 px; 2-4 useful, very sensitive)

CREASE_THRESHOLD = int(os.environ.get("CSC_ICON_CREASE_THRESHOLD", "10"))
# Higher = fewer Canny guide pixels drawn; lower = more/fainter guide pixels drawn. (0-255; 8-32 useful, sensitive at low values)

COLOR_BALANCE_MID_GREEN = float(os.environ.get("CSC_ICON_COLOR_BALANCE_MID_GREEN", "0.054"))
# Higher = pushes midtones greener; lower/negative = pushes midtones magenta. (-1 to 1; -0.1 to 0.1 useful, sensitive)

COLOR_BALANCE_MID_BLUE = float(os.environ.get("CSC_ICON_COLOR_BALANCE_MID_BLUE", "0.015"))
# Higher = pushes midtones bluer/cooler; lower/negative = pushes midtones yellow/warmer. (-1 to 1; -0.05 to 0.05 useful, sensitive)

COLOR_SATURATION_SCALE = float(os.environ.get("CSC_ICON_COLOR_SATURATION_SCALE", "0.8"))
# Higher = more saturated/vivid; lower = more muted/grey. (0-2; 0.75-1.15 useful, medium sensitivity)

COLOR_LEVELS_GAMMA = float(os.environ.get("CSC_ICON_COLOR_LEVELS_GAMMA", "1.2"))
# Higher = darker midtones; lower = brighter midtones. (0.25-3; 0.7-1.2 useful, sensitive)

COLOR_TEMP_ORIGINAL = float(os.environ.get("CSC_ICON_COLOR_TEMP_ORIGINAL", "6500"))
# Source white point for temperature correction; normally leave at daylight. (1000-40000 K; 6500 standard)

COLOR_TEMP_INTENDED = float(os.environ.get("CSC_ICON_COLOR_TEMP_INTENDED", "6108.6"))
# Higher = cooler/bluer correction; lower = warmer/yellower correction. (1000-40000 K; 5500-7000 subtle, low/medium sensitivity)

# Keep onnxruntime quiet and deterministic for rembg. The Windows Python env has
# onnxruntime-gpu installed without the CUDA 12 DLLs on PATH, so the default
# provider probe prints a noisy cublasLt64_12.dll error before falling back.
os.environ.setdefault("ORT_LOGGING_LEVEL", "3")

_REMBG_SESSION = None


def get_rembg_session():
    """Create one CPU-only rembg session and reuse it for the process."""
    from rembg import new_session

    global _REMBG_SESSION
    if _REMBG_SESSION is None:
        _REMBG_SESSION = new_session("u2net", providers=["CPUExecutionProvider"])
    return _REMBG_SESSION


def remove_background(img):
    """Remove background using rembg (U2-Net)."""
    from rembg import remove

    return remove(img, session=get_rembg_session())


def _kelvin_to_rgb(kelvin):
    """Approximate a black-body white point as RGB multipliers."""
    temp = max(1000.0, min(40000.0, kelvin)) / 100.0
    if temp <= 66.0:
        red = 255.0
        green = 99.4708025861 * np.log(temp) - 161.1195681661
        blue = 0.0 if temp <= 19.0 else 138.5177312231 * np.log(temp - 10.0) - 305.0447927307
    else:
        red = 329.698727446 * ((temp - 60.0) ** -0.1332047592)
        green = 288.1221695283 * ((temp - 60.0) ** -0.0755148492)
        blue = 255.0
    return np.clip([red, green, blue], 0, 255).astype(np.float32) / 255.0


def apply_color_correction(
    img,
    mid_green=COLOR_BALANCE_MID_GREEN,
    mid_blue=COLOR_BALANCE_MID_BLUE,
    saturation=COLOR_SATURATION_SCALE,
    gamma=COLOR_LEVELS_GAMMA,
    temp_original=COLOR_TEMP_ORIGINAL,
    temp_intended=COLOR_TEMP_INTENDED,
):
    """Apply the Market icon reference colour grade extracted from the XCF.

    The defaults mirror the non-destructive GIMP effects found on
    Market_Output.xcf: Color Balance midtones green +0.054 / blue +0.015,
    Saturation scale 0.884, Levels value gamma 0.79, and Color Temperature
    6500K → 6108.6K. This is an approximation in plain Pillow/NumPy, not a full
    GEGL reimplementation, but it preserves alpha and keeps the same knob shape.
    """
    arr = np.array(img.convert("RGBA")).astype(np.float32)
    rgb = arr[:, :, :3] / 255.0
    alpha = arr[:, :, 3]
    subject = alpha > 0
    if not subject.any():
        return img

    # Color Balance, midtones only. The triangular mask targets middle values
    # and fades out toward black/white so shadows and highlights stay stable.
    luma = rgb[:, :, 0] * 0.2126 + rgb[:, :, 1] * 0.7152 + rgb[:, :, 2] * 0.0722
    midtone = np.clip(1.0 - np.abs(luma - 0.5) * 2.0, 0.0, 1.0)[:, :, None]
    rgb[:, :, 1:2] += mid_green * midtone
    rgb[:, :, 2:3] += mid_blue * midtone
    rgb = np.clip(rgb, 0.0, 1.0)

    # GEGL saturation scale approximation: interpolate away from/to luma.
    gray = (rgb[:, :, 0] * 0.2126 + rgb[:, :, 1] * 0.7152 + rgb[:, :, 2] * 0.0722)[:, :, None]
    rgb = np.clip(gray + (rgb - gray) * saturation, 0.0, 1.0)

    # GIMP Levels value gamma approximation. Values below 1 brighten midtones.
    gamma = max(0.01, gamma)
    rgb = np.clip(rgb, 0.0, 1.0) ** gamma

    # Color Temperature approximation: adapt from original to intended white.
    original_rgb = _kelvin_to_rgb(temp_original)
    intended_rgb = _kelvin_to_rgb(temp_intended)
    rgb *= (intended_rgb / np.maximum(original_rgb, 1e-6)).reshape(1, 1, 3)
    rgb = np.clip(rgb, 0.0, 1.0)

    arr[:, :, :3] = rgb * 255.0
    arr[:, :, 3] = alpha
    return Image.fromarray(arr.astype(np.uint8))


def add_structural_outlines(
    img,
    low=INNER_OUTLINE_LOW,
    high=INNER_OUTLINE_HIGH,
    line_width=INNER_OUTLINE_WIDTH,
    min_area=INNER_OUTLINE_MIN_AREA,
    color=(15, 15, 15, 255),
):
    """Paint black inner lines on major building structure.

    This is intentionally alpha-aware and conservative: it only draws inside the
    existing subject mask, filters tiny Canny speckles, then thickens the kept
    components. The outer silhouette is handled separately by
    add_silhouette_outline().
    """
    import cv2
    arr = np.array(img).copy()
    alpha = arr[:, :, 3]
    opaque = alpha > 128
    if not opaque.any():
        return img

    # Canny on the RGB of the generated image. Bilateral filtering keeps strong
    # roof/wall/window boundaries but suppresses painterly texture noise.
    rgb_arr = arr[:, :, :3]
    gray = cv2.cvtColor(rgb_arr, cv2.COLOR_RGB2GRAY)
    filtered = cv2.bilateralFilter(gray, d=7, sigmaColor=45, sigmaSpace=45)
    edges = cv2.Canny(filtered, low, high)

    # Do not let alpha/silhouette boundary dominate this pass; that is the job
    # of the outer outline. Keep the pass focused on interior structure.
    subject = opaque.astype(np.uint8) * 255
    interior = cv2.erode(
        subject,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)),
        iterations=1,
    ) > 0
    edges[~interior] = 0

    # Remove tiny texture fragments. This keeps "major structural elements" —
    # roof breaks, wall seams, windows/doors, beams — instead of every brush mark.
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats((edges > 0).astype(np.uint8), 8)
    kept = np.zeros_like(edges, dtype=np.uint8)
    for label in range(1, num_labels):
        area = stats[label, cv2.CC_STAT_AREA]
        width = stats[label, cv2.CC_STAT_WIDTH]
        height = stats[label, cv2.CC_STAT_HEIGHT]
        if area >= min_area or max(width, height) >= 24:
            kept[labels == label] = 255

    if line_width > 1:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (line_width, line_width))
        kept = cv2.dilate(kept, kernel, iterations=1)

    edge_mask = (kept > 0) & opaque
    arr[edge_mask, 0] = color[0]
    arr[edge_mask, 1] = color[1]
    arr[edge_mask, 2] = color[2]
    arr[edge_mask, 3] = color[3]

    return Image.fromarray(arr)


def add_silhouette_outline(
    img,
    thickness=OUTLINE_THICKNESS,
    color=(0, 0, 0, 255),
    alpha_threshold=OUTLINE_ALPHA_THRESHOLD,
):
    """Thick black outline around the building silhouette using OpenCV dilation.

    The outline is anchored to the solid subject mask, then the original icon is
    alpha-composited back over the black outline. This deliberately lets the
    outline sit underneath rembg's soft/anti-aliased edge pixels instead of
    starting outside them, which removes the visible transparent moat that can
    appear between the generated image and the silhouette outline.
    """
    import cv2
    arr = np.array(img)
    alpha = arr[:, :, 3]
    solid_subject = alpha > alpha_threshold
    if not solid_subject.any():
        solid_subject = alpha > 0
    if not solid_subject.any():
        return img

    # Binary mask → dilate with circular kernel for smooth outline.
    mask = solid_subject.astype(np.uint8) * 255
    radius = thickness
    kernel_size = radius * 2 + 1
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    dilated = cv2.dilate(mask, kernel, iterations=1)
    outline_region = dilated > 128

    h, w = arr.shape[:2]
    outline = np.zeros((h, w, 4), dtype=np.uint8)
    outline[outline_region] = list(color)

    outline_img = Image.fromarray(outline)
    outline_img.alpha_composite(img)
    return outline_img


def overlay_canny_creases(
    img,
    canny_path,
    opacity=CREASE_OPACITY,
    line_width=CREASE_WIDTH,
    threshold=CREASE_THRESHOLD,
    pad_amount=0,
):
    """Overlay the Canny guide as semi-transparent black crease lines.

    If postprocess padded an opaque raw image before rembg, the generated image
    is now larger and shifted by that padding. Preserve the same transform for
    the Canny guide by pasting it into the padded canvas rather than resizing it
    across the whole padded image. Transparent inputs skip padding, so their
    guide can be used directly.
    """
    import cv2
    if not canny_path or not os.path.exists(canny_path):
        return img

    arr = np.array(img).copy()
    alpha = arr[:, :, 3]
    opaque = alpha > 128

    canny = Image.open(canny_path).convert("L")
    if canny.size != img.size:
        if pad_amount > 0:
            inner_w = img.size[0] - pad_amount * 2
            inner_h = img.size[1] - pad_amount * 2
            if inner_w > 0 and inner_h > 0:
                if canny.size != (inner_w, inner_h):
                    canny = canny.resize((inner_w, inner_h), Image.NEAREST)
                padded = Image.new("L", img.size, 0)
                padded.paste(canny, (pad_amount, pad_amount))
                canny = padded
            else:
                canny = scale_like_comfy_center(canny, img.size[0], img.size[1], Image.NEAREST)
        else:
            canny = scale_like_comfy_center(canny, img.size[0], img.size[1], Image.NEAREST)
    mask = np.array(canny) > threshold

    if line_width > 1:
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (line_width, line_width))
        mask = cv2.dilate(mask.astype(np.uint8) * 255, kernel, iterations=1) > 0

    mask &= opaque
    opacity = max(0.0, min(1.0, opacity))
    arr[mask, :3] = (arr[mask, :3].astype(np.float32) * (1.0 - opacity)).astype(np.uint8)
    return Image.fromarray(arr)


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
    # Use a solid neutral gray for the pad to help rembg distinguish subject
    bg = Image.new("RGBA", (w + pad * 2, h + pad * 2), (100, 100, 100, 255))
    rgb = img.convert("RGB")
    bg.paste(rgb, (pad, pad))
    # Convert back to RGBA for rembg
    return bg.convert("RGBA"), pad


def process_icon(input_path, output_path, canny_path=None):
    """Run the enabled post-processing effects in a stable order."""
    print(f"Processing: {input_path}")
    img = Image.open(input_path).convert("RGBA")

    alpha = img.getchannel("A")
    has_transparency = alpha.getextrema()[0] < 255
    pad_amount = 0

    if has_transparency:
        print("  0. Input already has transparency; preserving alpha mask...")
    elif ENABLE_BACKGROUND_REMOVAL:
        if ENABLE_PADDING_BEFORE_REMBG:
            print(f"  0. Padding image edges ({REMBG_PAD}px)...")
            img, pad_amount = pad_image(img, pad=REMBG_PAD)
        else:
            print("  0. Padding disabled; using opaque image directly for rembg...")

        print("  1. Removing background (rembg)...")
        img = remove_background(img)
    else:
        print("  0. Background removal disabled; keeping image alpha as-is...")

    if ENABLE_COLOR_CORRECTION:
        print(
            "  1.5. Applying Market reference color correction: "
            f"mid_green={COLOR_BALANCE_MID_GREEN:.3f}, mid_blue={COLOR_BALANCE_MID_BLUE:.3f}, "
            f"saturation={COLOR_SATURATION_SCALE:.3f}, gamma={COLOR_LEVELS_GAMMA:.3f}, "
            f"temp={COLOR_TEMP_ORIGINAL:.0f}K->{COLOR_TEMP_INTENDED:.1f}K"
        )
        img = apply_color_correction(img)
    else:
        print("  1.5. Color correction: off")

    print("  2. Applying enabled outline/detail effects...")

    if ENABLE_STRUCTURAL_OUTLINES:
        print(
            "     Structural outlines: "
            f"width={INNER_OUTLINE_WIDTH}px, canny={INNER_OUTLINE_LOW}/{INNER_OUTLINE_HIGH}, "
            f"min_area={INNER_OUTLINE_MIN_AREA}"
        )
        img = add_structural_outlines(img)
    else:
        print("     Structural outlines: off")

    if ENABLE_CANNY_CREASE_OVERLAY and canny_path:
        print(f"     Canny crease overlay: opacity={CREASE_OPACITY:.2f}, width={CREASE_WIDTH}px")
        img = overlay_canny_creases(img, canny_path, pad_amount=pad_amount)
    elif ENABLE_CANNY_CREASE_OVERLAY:
        print("     Canny crease overlay: on, but no canny path supplied")
    else:
        print("     Canny crease overlay: off")

    if ENABLE_SAM_OUTLINES:
        sam_path = os.path.join(os.path.dirname(__file__), "icon_sam_outline.py")
        if os.path.exists(sam_path):
            try:
                print("     SAM outlines: on")
                import icon_sam_outline
                img = icon_sam_outline.apply_sam_outlines(img)
            except Exception as exc:
                print(f"     SAM outlines: failed ({exc}); continuing")
        else:
            print("     SAM outlines: on, but icon_sam_outline.py not found")
    else:
        print("     SAM outlines: off")

    if ENABLE_SILHOUETTE_OUTLINE:
        print(
            f"     Outer silhouette outline: thickness={OUTLINE_THICKNESS}px, "
            f"alpha_threshold={OUTLINE_ALPHA_THRESHOLD}"
        )
        img = add_silhouette_outline(img, thickness=OUTLINE_THICKNESS)
    else:
        print("     Outer silhouette outline: off")

    if ENABLE_CENTER_ON_CANVAS:
        print(
            "  3. Centering on canvas: "
            f"{CENTER_CANVAS_SIZE}x{CENTER_CANVAS_SIZE}, padding={CENTER_PADDING}px"
        )
        img = center_on_canvas(img, canvas_size=CENTER_CANVAS_SIZE, padding=CENTER_PADDING)
    else:
        print("  3. Centering on canvas: off")

    img.save(output_path)
    print(f"  Done: {output_path}")
    return output_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        # Process all raw icon files in the configured dropzone.
        import glob
        raws = sorted(glob.glob(os.path.join(DROPZONE_DIR, "*_Raw.png")))
        if not raws:
            print("No raw icon files found. Pass an input path as argument.")
            sys.exit(1)
        for raw in raws:
            out = raw[:-len("_Raw.png")] + "_Postprocessed.png"
            process_icon(raw, out)
    else:
        inp = sys.argv[1]
        out = sys.argv[2] if len(sys.argv) > 2 else inp.replace(".png", "_icon.png")
        canny = sys.argv[3] if len(sys.argv) > 3 else None
        process_icon(inp, out, canny)
