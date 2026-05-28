"""
SAM-based region outlines for Civ Supply Chains SV sprite post-processing.

This module is a direct parallel of the icon pipeline's sam_outline.py, tuned
for 1024px SV workflow sprites. Lazily imported by sv_postprocess.py when
ENABLE_SAM_OUTLINES is true so the pipeline degrades gracefully if SAM (or
torch) is not installed.

Env var prefix: CSC_SV_  (mirrors icon pipeline's CSC_ICON_ prefix)
"""
import os
import warnings

import numpy as np
from PIL import Image

warnings.filterwarnings(
    "ignore",
    message=".*You are using `torch.load` with `weights_only=False`.*",
    category=FutureWarning,
)

# -----------------------------------------------------------------------------
# Configuration — all knobbed via env vars, same pattern as sam_outline.py
# -----------------------------------------------------------------------------
SAM_MODEL_TYPE = os.environ.get("CSC_SV_SAM_MODEL_TYPE", "vit_h")
SAM_CHECKPOINT = os.environ.get(
    "CSC_SV_SAM_CHECKPOINT",
    os.path.expanduser(r"~\.cache\civ_supply_chains\sam\sam_vit_h_4b8939.pth"),
)
SAM_DEVICE = os.environ.get("CSC_SV_SAM_DEVICE", "cuda")  # cuda / cpu

SAM_LINE_WIDTH = int(os.environ.get("CSC_SV_SAM_LINE_WIDTH", "16"))
# Higher = thicker SAM interior boundary lines. (1-25 px; 2-6 useful for 1024px sprites, very sensitive)

SAM_MIN_AREA = int(os.environ.get("CSC_SV_SAM_MIN_AREA", "4000"))
# Higher = ignores tiny details/speckles; lower = keeps more small segmented parts.
# Adjusted for 1024×1024 workflow scale. (50-20000 px area; 200-800 useful, medium sensitivity)

SAM_MAX_AREA_FRACTION = float(os.environ.get("CSC_SV_SAM_MAX_AREA_FRACTION", "0.85"))
# Higher = lets broad near-full-sprite masks pass; lower = keeps mask count focused on details. (0-1; 0.70-0.90 useful)

SAM_MAX_MASKS = int(os.environ.get("CSC_SV_SAM_MAX_MASKS", "20"))
# Higher = more region outlines; lower = fewer broader regions. (5-200; 30-70 useful)

SAM_COLOR = tuple(int(x) for x in os.environ.get("CSC_SV_SAM_COLOR", "58,58,58,255").split(","))
# RGBA line colour. (each channel 0-255; opacity 180-225 useful for layered look)

SAM_POINTS_PER_SIDE = int(os.environ.get("CSC_SV_SAM_POINTS_PER_SIDE", "24"))
# Higher = more masks/detail but slower; lower = faster/broader masks. (8-64; 16-48 useful, expensive)

SAM_PRED_IOU_THRESH = float(os.environ.get("CSC_SV_SAM_PRED_IOU_THRESH", "0.90"))
# Higher = only confident masks; lower = more masks including messy fragments. (0-1; 0.7-0.88 useful, sensitive)

SAM_STABILITY_THRESH = float(os.environ.get("CSC_SV_SAM_STABILITY_THRESH", "0.95"))
# Higher = stable/clean masks only; lower = more fragile fine details. (0-1; 0.82-0.96 useful, sensitive)

SAM_CROP_LAYERS = int(os.environ.get("CSC_SV_SAM_CROP_LAYERS", "1"))
# Higher = searches crops for small details but much slower; lower = faster/broader masks. (0-2 practical; 0 for SV)

SAM_INTERIOR_ERODE = int(os.environ.get("CSC_SV_SAM_INTERIOR_ERODE", "1"))
# Higher = keeps SAM lines farther from the outer silhouette; lower = lines can approach the edge. (1-15 px; 1-5 useful)

_SAM_MASK_GENERATOR = None  # loaded once per process


# -----------------------------------------------------------------------------
# Lazy SAM loader
# -----------------------------------------------------------------------------
def _get_device():
    if SAM_DEVICE == "cuda":
        try:
            import torch
            if torch.cuda.is_available():
                return "cuda"
        except Exception:
            pass
    return "cpu"


def _get_mask_generator():
    """Load SAM once per process."""
    global _SAM_MASK_GENERATOR
    if _SAM_MASK_GENERATOR is not None:
        return _SAM_MASK_GENERATOR

    if not os.path.exists(SAM_CHECKPOINT):
        raise FileNotFoundError(
            f"SAM checkpoint not found: {SAM_CHECKPOINT}. "
            "Use the checkpoint matching CSC_SV_SAM_MODEL_TYPE: "
            "vit_b=sam_vit_b_01ec64.pth, "
            "vit_l=sam_vit_l_0b3195.pth, "
            "vit_h=sam_vit_h_4b8939.pth."
        )

    from segment_anything import SamAutomaticMaskGenerator, sam_model_registry

    device = _get_device()
    sam = sam_model_registry[SAM_MODEL_TYPE](checkpoint=SAM_CHECKPOINT)
    sam.to(device=device)

    _SAM_MASK_GENERATOR = SamAutomaticMaskGenerator(
        model=sam,
        points_per_side=SAM_POINTS_PER_SIDE,
        pred_iou_thresh=SAM_PRED_IOU_THRESH,
        stability_score_thresh=SAM_STABILITY_THRESH,
        crop_n_layers=SAM_CROP_LAYERS,
        min_mask_region_area=SAM_MIN_AREA,
    )
    return _SAM_MASK_GENERATOR


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------
def apply_sam_sv_outlines(img: Image.Image) -> Image.Image:
    """Draw SAM region boundaries inside the current alpha mask.

    Working directly on the rgba output of the alpha-masked generation step
    (1024×1024).  SAM sees RGB only, so transparent padding is composited to
    white before inference.  Only lines **strictly inside** the subject mask
    are kept so SAM cannot create new outer silhouettes — that job belongs to
    the charcoal outer-outline pass.

    Degrades gracefully: if torch / segment_anything is unavailable the image
    is returned unchanged.
    """
    try:
        import cv2
    except ImportError:
        print("  SAM outlines: opencv-python not available, skipping.")
        return img

    rgba = np.array(img.convert("RGBA"))
    alpha = rgba[:, :, 3]
    subject = alpha > 128
    if not subject.any():
        return img

    # SAM is RGB-only — composite transparent pixels to white so it sees the
    # subject against a clean background rather than black/extreme transparency.
    rgb = rgba[:, :, :3].copy()
    rgb[~subject] = (255, 255, 255)

    generator = _get_mask_generator()
    masks = generator.generate(rgb)
    if not masks:
        return img

    h, w = alpha.shape
    max_area = h * w * SAM_MAX_AREA_FRACTION
    kept = []
    for mask in masks:
        area = int(mask.get("area", 0))
        if area < SAM_MIN_AREA or area > max_area:
            continue
        seg = mask["segmentation"] & subject
        if seg.any():
            kept.append((area, seg))

    # Largest masks first gives broad structural splits before fine details.
    kept.sort(reverse=True, key=lambda item: item[0])
    kept = kept[:SAM_MAX_MASKS]

    line_mask = np.zeros((h, w), dtype=np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (SAM_LINE_WIDTH, SAM_LINE_WIDTH))
    for _, seg in kept:
        seg_u8 = seg.astype(np.uint8) * 255
        eroded = cv2.erode(seg_u8, kernel, iterations=1)
        boundary = (seg_u8 > 0) & (eroded == 0)
        line_mask[boundary] = 255

    # Restrict lines to strictly interior pixels so the outer silhouette pass
    # (built on the alpha mask) stays clean and unambiguous.
    interior = cv2.erode(
        subject.astype(np.uint8) * 255,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (SAM_INTERIOR_ERODE, SAM_INTERIOR_ERODE)),
        iterations=1,
    ) > 0
    line_mask = (line_mask > 0) & interior

    out = rgba.copy()
    out[line_mask] = SAM_COLOR
    return Image.fromarray(out)
