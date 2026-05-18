"""
SAM-based region outlines for Civ Supply Chains icon post-processing.

This module is imported by icon_postprocess.py when ENABLE_SAM_OUTLINES is true.
It expects Meta Segment Anything's `segment_anything` Python package plus a SAM
checkpoint. The default checkpoint path is outside the repo so we do not
accidentally commit a 375 MB model file.
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


SAM_MODEL_TYPE = os.environ.get("CSC_ICON_SAM_MODEL_TYPE", "vit_h")  # Larger SAM variants can segment better but need matching checkpoints and more VRAM. (vit_b/vit_l/vit_h; vit_b lightest, vit_h strongest/slowest)
# Matching official SAM checkpoint filenames/URLs:
#   vit_b -> sam_vit_b_01ec64.pth -> https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth
#   vit_l -> sam_vit_l_0b3195.pth -> https://dl.fbaipublicfiles.com/segment_anything/sam_vit_l_0b3195.pth
#   vit_h -> sam_vit_h_4b8939.pth -> https://dl.fbaipublicfiles.com/segment_anything/sam_vit_h_4b8939.pth
SAM_CHECKPOINT = os.environ.get(
    "CSC_ICON_SAM_CHECKPOINT",
    os.path.expanduser(r"~\.cache\civ_supply_chains\sam\sam_vit_h_4b8939.pth"),
)
SAM_DEVICE = os.environ.get("CSC_ICON_SAM_DEVICE", "cuda")
# "cuda" = faster if GPU works; "cpu" = slower but more compatible. (cuda/cpu; no numeric sensitivity)

SAM_LINE_WIDTH = int(os.environ.get("CSC_ICON_SAM_LINE_WIDTH", "10"))
# Higher = thicker SAM interior boundaries; lower = thinner, lighter boundaries. (1-25 px; 6-12 useful, very sensitive)

SAM_MIN_AREA = int(os.environ.get("CSC_ICON_SAM_MIN_AREA", "3000"))
# Higher = ignores small details/speckles; lower = keeps more small segmented parts. (100-10000 px area; 1000-3000 useful, medium sensitivity)

SAM_MAX_AREA_FRACTION = float(os.environ.get("CSC_ICON_SAM_MAX_AREA_FRACTION", "0.65"))
# Higher = allows broad whole-building masks; lower = rejects large masks, keeping smaller parts. (0-1; 0.65-0.9 useful, medium sensitivity)

SAM_MAX_MASKS = int(os.environ.get("CSC_ICON_SAM_MAX_MASKS", "30"))
# Higher = more region outlines/clutter; lower = fewer, cleaner broad outlines. (5-100 masks; 25-70 useful, medium sensitivity)

SAM_COLOR = tuple(int(x) for x in os.environ.get("CSC_ICON_SAM_COLOR", "0,0,0,255").split(","))
# RGB/A line color; lower RGB = darker, lower A = more transparent. (each channel 0-255; RGB 0-40 dark, alpha 180-255 opaque)

SAM_POINTS_PER_SIDE = int(os.environ.get("CSC_ICON_SAM_POINTS_PER_SIDE", "16"))
# Higher = more masks/detail but slower; lower = faster with broader/simple masks. (8-64 points; 16-32 useful, expensive/sensitive)

SAM_PRED_IOU_THRESH = float(os.environ.get("CSC_ICON_SAM_PRED_IOU_THRESH", "0.8"))
# Higher = keeps only confident masks; lower = more masks, including messy ones. (0-1; 0.6-0.9 useful, sensitive)

SAM_STABILITY_THRESH = float(os.environ.get("CSC_ICON_SAM_STABILITY_THRESH", "0.90"))
# Higher = more stable/clean masks only; lower = more fragile fine details. (0-1; 0.85-0.95 useful, sensitive)

SAM_CROP_LAYERS = int(os.environ.get("CSC_ICON_SAM_CROP_LAYERS", "0"))
# Higher = searches crops for small details but much slower; lower = faster/broader masks. (0-2 practical; 0 fastest, 1 detailed, 2 very slow)

SAM_INTERIOR_ERODE = int(os.environ.get("CSC_ICON_SAM_INTERIOR_ERODE", "1"))
# Higher = keeps SAM lines farther from silhouette edge; lower = lets lines approach outer outline. (1-15 px; 3-7 useful, very sensitive)

_SAM_MASK_GENERATOR = None


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
            "Use the checkpoint matching CSC_ICON_SAM_MODEL_TYPE: "
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


def apply_sam_outlines(img):
    """Draw SAM region boundaries inside the current alpha mask.

    SAM sees the generated RGB image and returns semantic-ish masks. We filter
    out tiny fragments and near-whole-image masks, then draw only the mask
    boundaries that fall inside the icon subject alpha.
    """
    import cv2

    rgba = np.array(img.convert("RGBA"))
    alpha = rgba[:, :, 3]
    subject = alpha > 128
    if not subject.any():
        return img

    # SAM does not use alpha. Composite transparent pixels to white so it sees a
    # clean icon rather than black/transparent garbage around the subject.
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

    # Larger masks first gives broad roof/wall splits, then selected details.
    kept.sort(reverse=True, key=lambda item: item[0])
    kept = kept[:SAM_MAX_MASKS]

    line_mask = np.zeros((h, w), dtype=np.uint8)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (SAM_LINE_WIDTH, SAM_LINE_WIDTH))
    for _, seg in kept:
        seg_u8 = seg.astype(np.uint8) * 255
        eroded = cv2.erode(seg_u8, kernel, iterations=1)
        boundary = (seg_u8 > 0) & (eroded == 0)
        line_mask[boundary] = 255

    # Keep lines inside the subject and avoid making the very outside silhouette
    # fight with the dedicated silhouette-outline pass.
    interior = cv2.erode(
        subject.astype(np.uint8) * 255,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (SAM_INTERIOR_ERODE, SAM_INTERIOR_ERODE)),
        iterations=1,
    ) > 0
    line_mask = (line_mask > 0) & interior

    out = rgba.copy()
    out[line_mask] = SAM_COLOR
    return Image.fromarray(out)
