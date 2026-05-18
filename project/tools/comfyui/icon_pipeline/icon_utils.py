"""Shared helpers for Civ Supply Chains icon generation/post-processing."""


def env_bool(name, default):
    """Read a boolean environment variable with common truthy values."""
    import os

    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def scale_like_comfy_center(img, width=1024, height=1024, resample=None):
    """Match ComfyUI common_upscale(..., crop='center') crop+resize math."""
    if resample is None:
        from PIL import Image
        resample = Image.LANCZOS

    old_width, old_height = img.size
    old_aspect = old_width / old_height
    new_aspect = width / height
    x = 0
    y = 0
    if old_aspect > new_aspect:
        x = round((old_width - old_width * (new_aspect / old_aspect)) / 2)
    elif old_aspect < new_aspect:
        y = round((old_height - old_height * (old_aspect / new_aspect)) / 2)
    cropped = img.crop((x, y, old_width - x, old_height - y))
    return cropped.resize((width, height), resample)
