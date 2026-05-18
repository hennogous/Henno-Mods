"""
Post-process pipeline for Civ 6 SV sprites.
Tuned 2026-03-27 by Henno + Bill.

Steps (all toggleable/tweakable):
  0. Remove background (rembg U2-Net) — skipped if input already has alpha
  1. Brighten image
  2. Add charcoal outlines: outer silhouette + inner edge
  3. Add SAM structural outlines inside subject mask
  4. Optionally composite a 256px shadow plate behind the sprite
  5. Resize and composite onto transparent canvas

The historical filename is misleading now: this script intentionally does not
add the old elliptical shadow. Use the base shadow plate (step 4) instead.
"""
from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np
from PIL import Image

OUTPUT_DIR = Path(os.environ.get(
    "CSC_COMFYUI_OUTPUT_DIR",
    r"C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\ComfyUI output",
))


def env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on", "y"}


def env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    return default if value is None or value == "" else int(value)


def env_optional_int(name: str, default: Optional[int]) -> Optional[int]:
    value = os.getenv(name)
    return default if value is None or value == "" else int(value)


def env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    return default if value is None or value == "" else float(value)


def parse_color(value: str) -> Tuple[int, int, int]:
    value = value.strip()
    if value.startswith("#"):
        value = value[1:]
    if len(value) != 6:
        raise ValueError(f"Expected RGB hex color like #3A3A3A, got: {value!r}")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16))


# -----------------------------------------------------------------------------
# Post-processing effect toggles
# -----------------------------------------------------------------------------
# These are the master switches. Edit here for normal use, override with CLI
# flags for one-off tests, or set env vars for repeatable batch runs.
ENABLE_BACKGROUND_REMOVAL = env_bool("CSC_SV_ENABLE_BACKGROUND_REMOVAL", True)
ENABLE_PADDING_BEFORE_REMBG = env_bool("CSC_SV_ENABLE_PADDING_BEFORE_REMBG", True)
ENABLE_BRIGHTNESS = env_bool("CSC_SV_ENABLE_BRIGHTNESS", False)
ENABLE_OUTLINES = env_bool("CSC_SV_ENABLE_OUTLINES", True)
ENABLE_RESIZE_CANVAS = env_bool("CSC_SV_ENABLE_RESIZE_CANVAS", True)
ENABLE_SAM_OUTLINES = env_bool("CSC_SV_ENABLE_SAM_OUTLINES", True)
# Higher = adds SAM structural outlines inside the subject mask.
# Optional — requires sv_sam_outline.py + segment_anything + torch. Default: on
# (but graceful fallback if module/model is absent).

ENABLE_BASE_SHADOW = env_bool("CSC_SV_ENABLE_BASE_SHADOW", True)
# Master switch for compositing a shadow plate behind the generated sprite.
# Default on; use --no-base-shadow / CSC_SV_ENABLE_BASE_SHADOW=0 for pre-shadow intermediates.

# -----------------------------------------------------------------------------
# Effect settings
# -----------------------------------------------------------------------------
REMBG_PAD = env_int("CSC_SV_REMBG_PAD", 50)
# Higher = more border/context before rembg; lower = tighter/faster but edge cuts are more likely. (0-300 px; 40-80 useful, low/medium sensitivity for SV)

REMBG_MASK_ALPHA = env_int("CSC_SV_REMBG_MASK_ALPHA", 8)
# Alpha threshold used when checking whether the input already has transparency. (0-255; 4-16 useful, low sensitivity)

BRIGHTNESS_FACTOR = env_float("CSC_SV_BRIGHTNESS_FACTOR", 1.35)
# Higher = brighter/washed-out SV look; lower = preserves raw generation contrast. (0.5-2.0; 1.15-1.45 useful, medium sensitivity)

MASK_ALPHA_THRESHOLD = env_int("CSC_SV_MASK_ALPHA_THRESHOLD", 10)
# Higher = outlines only solid pixels; lower = includes soft alpha fringes. (0-255; 8-32 useful, sensitive)

OUTER_OUTLINE_PX = env_int("CSC_SV_OUTER_OUTLINE_PX", 4)
# Higher = thicker charcoal silhouette; lower = subtler outline. 0 disables outer outline. (0-20 px; 6-12 useful, very sensitive)

INNER_EDGE_PX = env_int("CSC_SV_INNER_EDGE_PX", 4)
# Higher = thicker inner edge/detail band; lower = finer detail. 0 disables inner edge. (0-10 px; 2-5 useful, very sensitive)

MIN_COMPONENT_PX = env_int("CSC_SV_MIN_COMPONENT_PX", 9)
# Drop connected components smaller than this (pixel count) from the building mask
# before drawing any outlines. Filters out noise specks from the alpha threshold.
# (4-20 useful; 9 = 3x3 pixel minimum. Set 0 to disable filtering.)

OUTLINE_COLOR = parse_color(os.getenv("CSC_SV_OUTLINE_COLOR", "#3A3A3A"))
# RGB hex charcoal colour for both outline passes. Default #3A3A3A matches tuned SV style.

OUTER_OUTLINE_ALPHA = env_int("CSC_SV_OUTER_OUTLINE_ALPHA", 255)
# Higher = more opaque outer silhouette; lower = softer/lighter edge. (0-255; 200-255 useful)

INNER_EDGE_ALPHA = env_int("CSC_SV_INNER_EDGE_ALPHA", 200)
# Higher = darker interior edge band; lower = softer details. (0-255; 120-220 useful)

CANVAS_SIZE = env_int("CSC_SV_CANVAS_SIZE", 256)
# Final square PNG canvas size. 256 is the Civ VI SV target size.

SPRITE_SIZE = env_int("CSC_SV_SPRITE_SIZE", 160)
# Building sprite size pasted onto the canvas. Higher = larger building; lower = more transparent margin. (90-140 useful, very visible)

SHADOW_PATH = os.environ.get(
    "CSC_SV_SHADOW_PATH",
    r"images\sv_visible_shadow.png",
)
# Path to a 256×256 RGBA shadow plate to composite behind the generated sprite.
# Leave unset or set to empty to disable. The image is expected to be the same
# size as CANVAS_SIZE; it is pasted first and the sprite is composited on top.

REVEALED_SHADOW_PATH = os.environ.get(
    "CSC_SV_REVEALED_SHADOW_PATH",
    r"images\sv_revealed_shadow.png",
)

REVEALED_NOISE_STRENGTH  = env_float("CSC_SV_REVEALED_NOISE_STRENGTH", 1)
# Optional pre-shadow grain. Default 0 because the reference XCF uses only
# Desaturate → Brightness/Contrast → Colorize adjustment filters.

# Reference: C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\CSC_BAKERS_SV_Revealed.xcf
# The XCF stores three non-destructive GIMP filters on the exported _Visible
# sprite. The brightness/contrast filter is present in the XCF metadata, but
# applying that GEGL value literally makes the sprite far darker than GIMP's
# visible result / the revealed hammer overlay. Defaults below are tuned against
# the hammer tone in images/sv_revealed_construction.png.
#
#   1. gimp:desaturate       mode=3
#   2. gimp:brightness-contrast brightness=-0.78740157480314965 contrast=-0.023622047244094488
#   3. gimp:colorize         hue=0.09950249642133713 saturation=0.6836735010147095 lightness=-0.23137253522872925
# They are applied to the sprite BEFORE the revealed shadow plate and state overlays.
REVEALED_DESATURATE_MODE   = env_int("CSC_SV_REVEALED_DESATURATE_MODE", 3)
REVEALED_DESATURATE_AMOUNT = env_float("CSC_SV_REVEALED_DESATURATE_AMOUNT", 1.0)
# GIMP's desaturate filter is a full greyscale conversion with no amount slider;
# this extra pipeline knob blends original→desaturated for tuning convenience.
REVEALED_BRIGHTNESS        = env_float("CSC_SV_REVEALED_BRIGHTNESS", -0.25)
REVEALED_CONTRAST       = env_float("CSC_SV_REVEALED_CONTRAST", 0.0)
REVEALED_COLORIZE_HUE   = env_float("CSC_SV_REVEALED_COLORIZE_HUE", 0.11)
REVEALED_COLORIZE_SAT   = env_float("CSC_SV_REVEALED_COLORIZE_SATURATION", 0.45)
REVEALED_COLORIZE_LIGHT = env_float("CSC_SV_REVEALED_COLORIZE_LIGHTNESS", -0.231)

OFFSET_X = env_optional_int("CSC_SV_OFFSET_X", None)
OFFSET_Y = env_optional_int("CSC_SV_OFFSET_Y", None)
# Paste offset. Leave unset to center; set both for deliberate sprite positioning.


@dataclass
class PostProcessConfig:

    enable_brightness: bool = ENABLE_BRIGHTNESS
    brightness_factor: float = BRIGHTNESS_FACTOR

    enable_outlines: bool = ENABLE_OUTLINES
    mask_alpha_threshold: int = MASK_ALPHA_THRESHOLD
    outer_outline_px: int = OUTER_OUTLINE_PX
    inner_edge_px: int = INNER_EDGE_PX
    min_component_px: int = MIN_COMPONENT_PX
    outline_color: Tuple[int, int, int] = OUTLINE_COLOR
    outer_outline_alpha: int = OUTER_OUTLINE_ALPHA
    inner_edge_alpha: int = INNER_EDGE_ALPHA

    enable_sam_outlines: bool = ENABLE_SAM_OUTLINES

    enable_background_removal: bool = ENABLE_BACKGROUND_REMOVAL
    enable_padding_before_rembg: bool = ENABLE_PADDING_BEFORE_REMBG
    rembg_pad: int = REMBG_PAD
    rembg_mask_alpha: int = REMBG_MASK_ALPHA

    enable_resize_canvas: bool = ENABLE_RESIZE_CANVAS
    canvas_size: int = CANVAS_SIZE
    sprite_size: int = SPRITE_SIZE
    shadow_path: str | None = SHADOW_PATH
    enable_base_shadow: bool = ENABLE_BASE_SHADOW
    offset_x: Optional[int] = OFFSET_X
    offset_y: Optional[int] = OFFSET_Y

    @classmethod
    def from_env(cls) -> "PostProcessConfig":
        return cls(
            enable_brightness=ENABLE_BRIGHTNESS,
            brightness_factor=BRIGHTNESS_FACTOR,
            enable_outlines=ENABLE_OUTLINES,
            mask_alpha_threshold=MASK_ALPHA_THRESHOLD,
            outer_outline_px=OUTER_OUTLINE_PX,
            inner_edge_px=INNER_EDGE_PX,
            min_component_px=MIN_COMPONENT_PX,
            outline_color=OUTLINE_COLOR,
            outer_outline_alpha=OUTER_OUTLINE_ALPHA,
            inner_edge_alpha=INNER_EDGE_ALPHA,
            enable_sam_outlines=ENABLE_SAM_OUTLINES,
            enable_background_removal=ENABLE_BACKGROUND_REMOVAL,
            enable_padding_before_rembg=ENABLE_PADDING_BEFORE_REMBG,
            rembg_pad=REMBG_PAD,
            rembg_mask_alpha=REMBG_MASK_ALPHA,
            enable_resize_canvas=ENABLE_RESIZE_CANVAS,
            canvas_size=CANVAS_SIZE,
            sprite_size=SPRITE_SIZE,
            shadow_path=SHADOW_PATH,
            enable_base_shadow=ENABLE_BASE_SHADOW,
            offset_x=OFFSET_X,
            offset_y=OFFSET_Y,
        )

    def resolved_offset(self) -> Tuple[int, int]:
        default_offset = (self.canvas_size - self.sprite_size) // 2
        return (
            default_offset if self.offset_x is None else self.offset_x,
            default_offset if self.offset_y is None else self.offset_y,
        )


@dataclass
class RevealedPostProcessConfig:
    """Settings specific to the Revealed pipeline variant."""

    noise_strength: float  = REVEALED_NOISE_STRENGTH
    desaturate_mode: int = REVEALED_DESATURATE_MODE
    desaturate_amount: float = REVEALED_DESATURATE_AMOUNT
    brightness: float = REVEALED_BRIGHTNESS
    contrast: float = REVEALED_CONTRAST
    colorize_hue: float = REVEALED_COLORIZE_HUE
    colorize_saturation: float = REVEALED_COLORIZE_SAT
    colorize_lightness: float = REVEALED_COLORIZE_LIGHT
    shadow_path: str | None = REVEALED_SHADOW_PATH
    canvas_size: int = CANVAS_SIZE
    sprite_size: int = SPRITE_SIZE
    offset_x: Optional[int] = OFFSET_X
    offset_y: Optional[int] = OFFSET_Y

    @classmethod
    def from_env(cls) -> "RevealedPostProcessConfig":
        return cls(
            noise_strength=REVEALED_NOISE_STRENGTH,
            desaturate_mode=REVEALED_DESATURATE_MODE,
            desaturate_amount=REVEALED_DESATURATE_AMOUNT,
            brightness=REVEALED_BRIGHTNESS,
            contrast=REVEALED_CONTRAST,
            colorize_hue=REVEALED_COLORIZE_HUE,
            colorize_saturation=REVEALED_COLORIZE_SAT,
            colorize_lightness=REVEALED_COLORIZE_LIGHT,
            shadow_path=REVEALED_SHADOW_PATH,
            canvas_size=CANVAS_SIZE,
            sprite_size=SPRITE_SIZE,
            offset_x=OFFSET_X,
            offset_y=OFFSET_Y,
        )

    def resolved_offset(self) -> Tuple[int, int]:
        default_offset = (self.canvas_size - self.sprite_size) // 2
        return (
            default_offset if self.offset_x is None else self.offset_x,
            default_offset if self.offset_y is None else self.offset_y,
        )

# -----------------------------------------------------------------------------
# Background removal (rembg U2-Net)
# -----------------------------------------------------------------------------
_REMBG_SESSION = None


def resolve_pipeline_asset(path: str | Path | None) -> Path | None:
    """Resolve a pipeline asset path relative to this script when needed."""
    if not path:
        return None
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = Path(__file__).resolve().parent / resolved
    return resolved


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


def input_has_alpha(img: Image.Image, threshold: int = 8) -> bool:
    """Return True if the image already carries meaningful transparency."""
    alpha = img.getchannel("A")
    return alpha.getextrema()[0] <= threshold


def pad_image(img, pad=REMBG_PAD):
    """Add a neutral gray border before rembg so edges aren't mistaken for subject."""
    w, h = img.size
    padded = Image.new("RGBA", (w + pad * 2, h + pad * 2), (100, 100, 100, 255))
    rgb = img.convert("RGB")
    padded.paste(rgb, (pad, pad))
    return padded.convert("RGBA"), pad


def add_outlines(
    img: Image.Image,
    *,
    mask_alpha_threshold: int = 10,
    outer_px: int = 10,
    inner_px: int = 4,
    min_component_px: int = 9,
    color: Tuple[int, int, int] = (58, 58, 58),
    outer_alpha: int = 255,
    inner_alpha: int = 200,
) -> Image.Image:
    """Add outer silhouette and inner edge outlines using the alpha mask."""
    from scipy.ndimage import binary_dilation, binary_erosion

    rgba = np.array(img.convert("RGBA"))
    alpha = rgba[:, :, 3]
    building = alpha > mask_alpha_threshold

    # Drop tiny connected components (noise specks) before any dilation/erosion.
    if min_component_px > 0:
        from scipy.ndimage import label
        labeled, num_features = label(building)
        if num_features > 0:
            counts = np.bincount(labeled.ravel())
            big_groups = counts > min_component_px
            keep = big_groups[labeled]
            building = building & keep.reshape(building.shape)

    result = rgba.copy()

    if outer_px > 0:
        dilated_outer = binary_dilation(building, iterations=outer_px)
        outline_outer = dilated_outer & ~building
        result[outline_outer] = [*color, outer_alpha]

    if inner_px > 0:
        eroded = binary_erosion(building, iterations=inner_px)
        inner_edge = building & ~eroded
        result[inner_edge] = [*color, inner_alpha]

    return Image.fromarray(result, "RGBA")


def brighten(img: Image.Image, factor: float = 1.35) -> Image.Image:
    """Boost brightness of non-transparent pixels."""
    from PIL import ImageEnhance

    rgb = img.convert("RGB")
    rgb = ImageEnhance.Brightness(rgb).enhance(factor)
    rgba = img.convert("RGBA")
    r, g, b = rgb.split()
    rgba.paste(Image.merge("RGB", (r, g, b)), mask=None)
    rgba.putalpha(img.split()[3])
    return rgba


def revealed_desaturate_xcf(img: Image.Image, mode: int = 3, amount: float = 1.0) -> Image.Image:
    """Approximate GIMP's ``gimp:desaturate`` filter as stored in the reference XCF.

    The XCF records ``mode=3``. In current GIMP builds this is the Value-style
    desaturation, i.e. the greyscale value is the maximum RGB channel. Other
    modes are included as fallbacks for quick tuning via env vars.

    GIMP's desaturate operation itself has no amount slider; ``amount`` is a
    deliberate CSC tuning addition that blends original→desaturated. ``1.0`` is
    faithful to the XCF filter, ``0.0`` disables this stage.
    """
    amount = float(np.clip(amount, 0.0, 1.0))
    if amount <= 0.0:
        return img.convert("RGBA")

    arr = np.array(img.convert("RGBA"), dtype=np.float32)
    original_rgb = arr[:, :, :3].copy()
    rgb = arr[:, :, :3]

    if mode == 0:      # Lightness: (max + min) / 2
        grey = (rgb.max(axis=2) + rgb.min(axis=2)) * 0.5
    elif mode == 1:    # Luma / Rec. 601
        grey = rgb[:, :, 0] * 0.299 + rgb[:, :, 1] * 0.587 + rgb[:, :, 2] * 0.114
    elif mode == 2:    # Average
        grey = rgb.mean(axis=2)
    else:              # Value (XCF default: mode=3)
        grey = rgb.max(axis=2)

    grey_rgb = grey[:, :, None]
    arr[:, :, :3] = original_rgb * (1.0 - amount) + grey_rgb * amount
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def gimp_brightness_contrast(
    img: Image.Image,
    brightness: float = REVEALED_BRIGHTNESS,
    contrast: float = REVEALED_CONTRAST,
) -> Image.Image:
    """Apply GIMP/GEGL-like brightness-contrast values from the Revealed XCF."""
    arr = np.array(img.convert("RGBA"), dtype=np.float32)
    rgb = arr[:, :, :3] / 255.0

    if brightness < 0:
        rgb *= (1.0 + brightness)
    elif brightness > 0:
        rgb += (1.0 - rgb) * brightness

    if contrast != 0:
        factor = np.tan((contrast + 1.0) * np.pi / 4.0)
        rgb = (rgb - 0.5) * factor + 0.5

    arr[:, :, :3] = np.clip(rgb * 255.0, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def gimp_colorize_xcf(
    img: Image.Image,
    hue: float = REVEALED_COLORIZE_HUE,
    saturation: float = REVEALED_COLORIZE_SAT,
    lightness: float = REVEALED_COLORIZE_LIGHT,
) -> Image.Image:
    """Approximate GIMP's ``gimp:colorize`` filter from the reference XCF.

    GIMP stores hue/saturation in 0..1 and lightness in -1..1. The filter keeps
    the source luminance shape, applies the target hue/saturation, then shifts
    lightness with the same darken/lighten slider semantics as the UI.
    """
    arr = np.array(img.convert("RGBA"), dtype=np.float32)
    rgb = arr[:, :, :3] / 255.0
    max_c = rgb.max(axis=2)
    min_c = rgb.min(axis=2)
    lum = (max_c + min_c) * 0.5

    if lightness < 0:
        lum *= (1.0 + lightness)
    elif lightness > 0:
        lum += (1.0 - lum) * lightness
    lum = np.clip(lum, 0.0, 1.0)

    # Vectorised HLS→RGB for constant H/S and per-pixel L.
    h = hue % 1.0
    s = np.clip(saturation, 0.0, 1.0)
    q = np.where(lum < 0.5, lum * (1.0 + s), lum + s - lum * s)
    p = 2.0 * lum - q

    def hue_to_rgb(t):
        t = (t % 1.0)
        return np.where(
            t < 1.0 / 6.0,
            p + (q - p) * 6.0 * t,
            np.where(
                t < 0.5,
                q,
                np.where(t < 2.0 / 3.0, p + (q - p) * (2.0 / 3.0 - t) * 6.0, p),
            ),
        )

    arr[:, :, 0] = hue_to_rgb(h + 1.0 / 3.0) * 255.0
    arr[:, :, 1] = hue_to_rgb(h) * 255.0
    arr[:, :, 2] = hue_to_rgb(h - 1.0 / 3.0) * 255.0
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def apply_revealed_xcf_effects(img: Image.Image, config: RevealedPostProcessConfig) -> Image.Image:
    """Apply the Revealed effect stack copied from ``CSC_BAKERS_SV_Revealed.xcf``."""
    img = revealed_desaturate_xcf(img, config.desaturate_mode, config.desaturate_amount)
    img = gimp_brightness_contrast(img, config.brightness, config.contrast)
    if config.noise_strength > 0:
        img = add_revealed_noise(img, config.noise_strength)
    img = gimp_colorize_xcf(img, config.colorize_hue, config.colorize_saturation, config.colorize_lightness)
    return img


def add_revealed_noise(img: Image.Image, strength: float = 12.0) -> Image.Image:
    """Per-pixel luminance-preserving Gaussian noise (alpha untouched)."""
    arr = np.array(img.convert("RGBA"), dtype=np.float32)
    noise = np.random.normal(0, strength, arr[:, :, :3].shape)
    arr[:, :, :3] = np.clip(arr[:, :, :3] + noise, 0, 255)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


def composite_overlay(img: Image.Image, overlay_path: str | Path) -> Image.Image:
    """Alpha-composite a 256×256 RGBA state overlay on top of the visible sprite."""
    overlay = Image.open(overlay_path).convert("RGBA")
    if overlay.size != img.size:
        overlay = overlay.resize(img.size, Image.LANCZOS)
    result = img.copy()
    result.alpha_composite(overlay)
    return result


def resize_to_canvas(img: Image.Image, config: PostProcessConfig) -> Image.Image:
    """Resize sprite, optionally composite a shadow plate, then paste on canvas."""
    img = img.resize((config.sprite_size, config.sprite_size), Image.LANCZOS)

    shadow_abs = resolve_pipeline_asset(config.shadow_path)
    if config.enable_base_shadow and shadow_abs and shadow_abs.exists():
        canvas = Image.open(shadow_abs).convert("RGBA")
        canvas = canvas.resize((config.canvas_size, config.canvas_size), Image.LANCZOS)
        # Shadow is already the right canvas size. Overlay the sprite centred.
        offset = config.resolved_offset()
        canvas.alpha_composite(img, dest=offset)
        return canvas
    else:
        canvas = Image.new("RGBA", (config.canvas_size, config.canvas_size), (0, 0, 0, 0))
        offset = config.resolved_offset()
        canvas.paste(img, offset, img)
        return canvas


def process_revealed(
    input_path: str,
    output_path: str | None = None,
    base_config: PostProcessConfig | None = None,
    revealed_config: RevealedPostProcessConfig | None = None,
    *,
    shadow_path: str | None = None,
    noise_strength: float | None = None,
    state_overlays: list[tuple[str, str]] | None = None,
) -> list[str]:
    """Build a Revealed sprite variant.

    Normal path: ``input_path`` is the pre-shadow 256px ``_Visible`` canvas
    produced by ``process(..., enable_base_shadow=False)``. In that case no
    further Visible-stage processing is applied here; the XCF-derived Revealed
    effect stack runs directly on those pixels, then the lighter Revealed shadow
    is underlaid:

        Desaturate(mode=3) → Brightness/Contrast → optional grain → Colorize
        → Revealed shadow

    Legacy/raw path: if the input is not already a 256px canvas, this function
    first applies the same brightness/outline/resize treatment used by the
    Visible export, then applies the Revealed effect stack and revealed shadow.

    State overlays are always composited last. Returns the files written:
    ``[<base>, ...<state variants>]``.
    """
    config = base_config or PostProcessConfig.from_env()
    revealed_config = revealed_config or RevealedPostProcessConfig.from_env()
    if noise_strength is not None:
        revealed_config.noise_strength = noise_strength
    if shadow_path is not None:
        revealed_config.shadow_path = shadow_path
    overlays = state_overlays if state_overlays is not None else _REVEALED_STATE_OVERLAYS

    img = Image.open(input_path).convert("RGBA")
    is_visible_canvas = img.size == (config.canvas_size, config.canvas_size)

    if not is_visible_canvas:
        # Legacy/raw input path: build the same cleaned sprite the Visible pipeline
        # would have built before applying the Revealed treatment.
        if config.enable_brightness:
            img = brighten(img, config.brightness_factor)
        if config.enable_outlines:
            img = add_outlines(img, **{
                "mask_alpha_threshold": config.mask_alpha_threshold,
                "outer_px": config.outer_outline_px,
                "inner_px": config.inner_edge_px,
                "min_component_px": config.min_component_px,
                "color": config.outline_color,
                "outer_alpha": config.outer_outline_alpha,
                "inner_alpha": config.inner_edge_alpha,
            })

    # Revealed treatment happens before revealed shadow and state overlays. For
    # normal sv_img2img runs this receives the pre-shadow _Visible canvas.
    img = apply_revealed_xcf_effects(img, revealed_config)

    if is_visible_canvas:
        # Normal path: the input is already a 256px canvas, but should not have
        # the darker Visible shadow baked in. Underlay the lighter Revealed
        # shadow here so Visible and Revealed can use separate shadow plates.
        shadow_abs = resolve_pipeline_asset(revealed_config.shadow_path)
        if shadow_abs and shadow_abs.exists():
            canvas = Image.open(shadow_abs).convert("RGBA")
            canvas = canvas.resize((config.canvas_size, config.canvas_size), Image.LANCZOS)
            canvas.alpha_composite(img)
            img = canvas

    src_dir   = Path(input_path).parent
    base_path = Path(output_path) if output_path else default_revealed_output_path(input_path)
    if not base_path.is_absolute():
        base_path = src_dir / base_path
    base_path.parent.mkdir(parents=True, exist_ok=True)

    if not is_visible_canvas:
        # Legacy/raw input path: resize and add the revealed shadow plate.
        img = img.resize((config.sprite_size, config.sprite_size), Image.LANCZOS)
        shadow_abs = resolve_pipeline_asset(revealed_config.shadow_path)
        if shadow_abs and shadow_abs.exists():
            canvas = Image.open(shadow_abs).convert("RGBA")
            canvas = canvas.resize((config.canvas_size, config.canvas_size), Image.LANCZOS)
            offset = config.resolved_offset()
            canvas.alpha_composite(img, dest=offset)
            img = canvas
        else:
            canvas = Image.new("RGBA", (config.canvas_size, config.canvas_size), (0, 0, 0, 0))
            offset = config.resolved_offset()
            canvas.paste(img, offset, img)
            img = canvas

    img.save(base_path)
    results = [str(base_path)]

    # State overlays
    for tag, rel_path in overlays:
        overlay_abs = Path(__file__).resolve().parent / rel_path
        if not overlay_abs.exists():
            print(f"  Revealed overlay {tag}: not found ({rel_path}); skipping.")
            continue
        state_path = base_path.parent / f"{base_path.stem}_{tag}{base_path.suffix}"
        composite = composite_overlay(img, str(overlay_abs))
        composite.save(state_path)
        results.append(str(state_path))

    return results


_REVEALED_STATE_OVERLAYS: list[tuple[str, str]] = [
    ("UnderConstruction", "images/sv_revealed_construction.png"),
    ("Pillaged",          "images/sv_revealed_pillaged.png"),
]


def default_output_path(input_path: str) -> Path:
    input_file = Path(input_path)
    return input_file.parent / f"{input_file.stem}_Visible.png"


def default_revealed_output_path(input_path: str) -> Path:
    """Default Revealed output path for a Visible sprite input.

    ``Foo_Visible.png`` becomes ``Foo_Revealed.png``. Other inputs get the
    conservative ``<stem>_Revealed.png`` suffix.
    """
    input_file = Path(input_path)
    stem = input_file.stem
    for suffix in ("_Visible_PreShadow", "_Visible", "_Revealed", "_UnderConstruction", "_Pillaged", "_Raw"):
        if stem.endswith(suffix):
            stem = stem[: -len(suffix)]
            break
    return input_file.parent / f"{stem}_Revealed.png"


def process(
    input_path: str,
    output_path: str | Path | None = None,
    config: PostProcessConfig | None = None,
):
    config = config or PostProcessConfig.from_env()

    if output_path is None:
        output_path = default_output_path(input_path)
    else:
        output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    img = Image.open(input_path).convert("RGBA")

    # Step 0: background removal via rembg — only if input is effectively opaque.
    if config.enable_background_removal and not input_has_alpha(img, config.rembg_mask_alpha):
        if config.enable_padding_before_rembg:
            img, _ = pad_image(img, pad=config.rembg_pad)
        img = remove_background(img)
    elif config.enable_background_removal:
        print("  0. Background removal: input already has alpha; preserving mask...")

    if config.enable_brightness:
        img = brighten(img, config.brightness_factor)

    if config.enable_outlines:
        img = add_outlines(
            img,
            mask_alpha_threshold=config.mask_alpha_threshold,
            outer_px=config.outer_outline_px,
            inner_px=config.inner_edge_px,
            min_component_px=config.min_component_px,
            color=config.outline_color,
            outer_alpha=config.outer_outline_alpha,
            inner_alpha=config.inner_edge_alpha,
        )

    if config.enable_sam_outlines:
        try:
            print("  SAM structural outlines: on")
            import sv_sam_outline
            img = sv_sam_outline.apply_sam_sv_outlines(img)
        except Exception as exc:
            print(f"  SAM outlines: failed ({exc}); continuing without SAM.")

    if config.enable_resize_canvas:
        img = resize_to_canvas(img, config)

    img.save(output_path)
    return str(output_path)


def add_processing_options(parser: argparse.ArgumentParser) -> None:
    """Add post-processing knobs to a CLI parser."""
    parser.add_argument("--revealed-from-visible", action="store_true",
                        help="Treat input as a pre-shadow 256px Visible canvas and rebuild _Revealed + state overlays only (no ComfyUI).")
    parser.add_argument("--background-removal", dest="enable_background_removal", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--padding-before-rembg", dest="enable_padding_before_rembg", action=argparse.BooleanOptionalAction, default=None,
                        help="Add gray padding before rembg for better edge detection. Default/env: on.")
    parser.add_argument("--rembg-pad", type=int, default=None,
                        help="Padding border in px before rembg. Default/env: 50.")
    parser.add_argument("--rembg-mask-alpha", type=int, default=None,
                        help="Alpha threshold to detect transparent input. Default/env: 8.")
    parser.add_argument("--brightness", dest="enable_brightness", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--brightness-factor", type=float, default=None, help="Brightness multiplier. Default/env: 1.35.")

    parser.add_argument("--outlines", dest="enable_outlines", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--mask-alpha-threshold", type=int, default=None, help="Alpha threshold for outline mask. Default/env: 10.")
    parser.add_argument("--outer-outline-px", type=int, default=None, help="Outer silhouette thickness in px. Default/env: 4; 0 disables outer outline.")
    parser.add_argument("--inner-edge-px", type=int, default=None, help="Inner edge thickness in px. Default/env: 4; 0 disables inner edge.")
    parser.add_argument("--outline-color", type=parse_color, default=None, help="RGB hex outline color, e.g. #3A3A3A.")
    parser.add_argument("--outer-outline-alpha", type=int, default=None, help="Outer outline alpha 0-255. Default/env: 255.")
    parser.add_argument("--inner-edge-alpha", type=int, default=None, help="Inner edge alpha 0-255. Default/env: 200.")
    parser.add_argument("--min-component-px", type=int, default=None,
                        help="Drop outline components smaller than this pixel count. 0 disables. Default/env: 9.")

    parser.add_argument("--sam-outlines", dest="enable_sam_outlines",
                        action=argparse.BooleanOptionalAction, default=None,
                        help="Enable SAM structural outlines inside subject. Requires torch+segment_anything. Default/env: on.")

    parser.add_argument("--resize-canvas", dest="enable_resize_canvas", action=argparse.BooleanOptionalAction, default=None)
    parser.add_argument("--canvas-size", type=int, default=None, help="Final square canvas size. Default/env: 256.")
    parser.add_argument("--sprite-size", type=int, default=None, help="Sprite size pasted onto canvas. Default/env: 160.")
    parser.add_argument("--base-shadow", dest="enable_base_shadow", action=argparse.BooleanOptionalAction, default=None,
                        help="Composite sv_visible_shadow.png behind sprite. Default/env: on.")
    parser.add_argument("--shadow-path", type=str, default=None,
                        help="Path to shadow plate PNG (expects 256x256 RGBA). Overrides env CSC_SV_SHADOW_PATH.")
    parser.add_argument("--offset-x", type=int, default=None, help="Paste X offset. Default: centered.")
    parser.add_argument("--offset-y", type=int, default=None, help="Paste Y offset. Default: centered.")

    parser.add_argument("--revealed-desaturate-mode", dest="desaturate_mode", type=int, default=None,
                        help="Revealed desaturate mode. Default/env: 3.")
    parser.add_argument("--revealed-desaturate-amount", dest="desaturate_amount", type=float, default=None,
                        help="Blend amount for the desaturate stage, 0..1. Default/env: 1.0; XCF-faithful is 1.0.")
    parser.add_argument("--revealed-brightness", dest="brightness", type=float, default=None,
                        help="Revealed pre-colorize brightness. Default/env: -0.25.")
    parser.add_argument("--revealed-contrast", dest="contrast", type=float, default=None,
                        help="Revealed pre-colorize contrast. Default/env: 0.0.")
    parser.add_argument("--revealed-hue", dest="colorize_hue", type=float, default=None,
                        help="Revealed colorize hue, 0..1. Default/env: 0.11.")
    parser.add_argument("--revealed-saturation", dest="colorize_saturation", type=float, default=None,
                        help="Revealed colorize saturation, 0..1. Default/env: 0.45.")
    parser.add_argument("--revealed-lightness", dest="colorize_lightness", type=float, default=None,
                        help="Revealed colorize lightness, -1..1. Default/env: -0.231.")
    parser.add_argument("--revealed-noise-strength", dest="noise_strength", type=float, default=None,
                        help="Optional Revealed grain/noise strength. Default/env: 0.0.")
    parser.add_argument("--revealed-shadow-path", dest="revealed_shadow_path", type=str, default=None,
                        help="Revealed shadow plate PNG. Used for both pre-shadow Visible inputs and raw-input fallback.")


def add_cli_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("input", help="Input PNG to post-process.")
    parser.add_argument("output", nargs="?", help="Output PNG. Defaults to the CSC ComfyUI output folder.")
    add_processing_options(parser)


def config_from_args(args: argparse.Namespace) -> PostProcessConfig:
    config = PostProcessConfig.from_env()
    for field in config.__dataclass_fields__:
        if hasattr(args, field):
            value = getattr(args, field)
            if value is not None:
                setattr(config, field, value)
    return config


def revealed_config_from_args(args: argparse.Namespace) -> RevealedPostProcessConfig:
    config = RevealedPostProcessConfig.from_env()
    for field in config.__dataclass_fields__:
        if hasattr(args, field):
            value = getattr(args, field)
            if value is not None:
                setattr(config, field, value)
    if getattr(args, "revealed_shadow_path", None) is not None:
        config.shadow_path = args.revealed_shadow_path
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description="Post-process a Civ 6 strategic-view sprite.")
    add_cli_options(parser)
    args = parser.parse_args()
    if args.revealed_from_visible:
        saved = process_revealed(
            args.input,
            args.output,
            base_config=config_from_args(args),
            revealed_config=revealed_config_from_args(args),
        )
        print("Saved:")
        for path in saved:
            print(f"  {path}")
    else:
        saved = process(args.input, args.output, config=config_from_args(args))
        print(f"Saved: {saved}")


if __name__ == "__main__":
    main()
