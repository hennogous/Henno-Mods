"""
Strategic View LoRA img2img -- source image + SDXL + SV LoRA.

Workflow:
  1. Extract alpha mask from input image
  2. Prepare input for ComfyUI (plot transparent bg pixels to neutral mid-gray)
  3. Upload prepped input to ComfyUI
  4. Generate (img2img, no ControlNet)
  5. Apply input alpha mask to raw output -> crops any model-invented background
  6. Post-process only to the large pre-shadow editing image (_Visible_PreShadow)

The final 256px placement/scaling and Visible/Revealed game assets are
intentionally not produced here. Paint directional/self-shadowing manually on
the larger _Visible_PreShadow image, then run sv_postprocess.py on that
hand-edited file to scale/place onto the 256px canvas, add shadow plates, and
add state variants.

An Asset Editor screenshot is RGBA with a coloured backplate (green at
alpha=0). ComfyUI's VAEEncode discards alpha, so those RGB pixels would
leak into the latent. prepare_upload_image() neutralises them before
upload; apply_alpha_mask() restores the correct silhouette after.
"""
import argparse
import hashlib

import io
import json
import mimetypes
import os
import random
import sys
import tempfile
import time

import urllib.parse
import urllib.request
import uuid
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from sv_postprocess import (
    add_processing_options,
    config_from_args,
    process as sv_process,
)

COMFYUI_URL = os.environ.get("CSC_COMFYUI_URL", "http://127.0.0.1:8188")
OUTPUT_DIR = Path(os.environ.get(
    "CSC_COMFYUI_OUTPUT_DIR",
    r"C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\ComfyUI output",
))
WORKFLOW_SIZE = 1024  # ComfyUI SDXL img2img native resolution
RUN_ID = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]

# -----------------------------------------------------------------------------
# Generation knobs
# -----------------------------------------------------------------------------
DENOISE = float(os.environ.get("CSC_SV_DENOISE", "0.3"))
# Higher = more freedom/style drift from input; lower = preserves source more tightly. (0-1; 0.45-0.65 useful, sensitive)

LORA_STR = float(os.environ.get("CSC_SV_LORA_STR", "1.2"))
# Higher = stronger Civ 6 strategic-view LoRA style; lower = more base SDXL/general style. (0-1.2; 0.5-0.75 useful, medium sensitivity)

CFG_VALUE = float(os.environ.get("CSC_SV_CFG_VALUE", "10.0"))
# Single CFG value for this pipeline run. Higher = follows prompt harder; lower = softer/more varied. (1-15; 8-10 useful)

STEPS = int(os.environ.get("CSC_SV_STEPS", "35"))
# Higher = slower with slightly cleaner/refined output; lower = faster but rougher. (15-50; 20-30 useful, low/medium sensitivity)

SEED = int(os.environ.get("CSC_SV_SEED", "42"))
# Same seed = repeatable output for the same workflow; change for a different composition. (any int)

SAMPLER = os.environ.get("CSC_SV_SAMPLER", "dpmpp_2m")
# ComfyUI sampler name. Normally leave at dpmpp_2m.

SCHEDULER = os.environ.get("CSC_SV_SCHEDULER", "karras")
# ComfyUI scheduler. Normally leave at karras.

CHECKPOINT = os.environ.get("CSC_SV_CHECKPOINT", "sd_xl_base_1.0.safetensors")
# Base SDXL checkpoint in ComfyUI/models/checkpoints.

LORA_NAME = os.environ.get("CSC_SV_LORA_NAME", "civ6_strategic_view.safetensors")
# Strategic-view LoRA file in ComfyUI/models/loras.

PROMPT = os.environ.get(
    "CSC_SV_PROMPT",
    "classical period industrial utility building, civ 6 strategic view sprite, building icon, top-down isometric, "
    "simplified illustration, muted earth tones, hand-painted style",
)
# Positive prompt. Keep 'civ 6 strategic view sprite' in here unless intentionally testing drift.
# IMPORTANT: do NOT add "background" or "ground" here — that invites the model to paint a green floor.

NEGATIVE = os.environ.get(
    "CSC_SV_NEGATIVE",
    "realistic, photo, blurry, text, watermark, ugly, deformed, added details, "
    "invented features, new elements, background, environment, ground, landscape, "
    "sky, horizon, scenery, context, grass, terrain, floor plane",
)
# Negative prompt. Exclude background/ground/terrain explicitly so the model does not
# invent a green floor or sky around the building. Add failure modes here.

MASK_ALPHA_CUTOFF = int(os.environ.get("CSC_SV_MASK_ALPHA_CUTOFF", "8"))
# Hardens faint background residue on the input alpha mask. (0-255; 4-24 useful, sensitive)

KEEP_INTERMEDIATES = os.environ.get("CSC_SV_KEEP_INTERMEDIATES", "0").strip().lower() in {"1", "true", "yes", "on", "y"}
# Debug switch: keep _Visible_Raw beside the exported large _Visible_PreShadow.
# Default off; _Visible_PreShadow is always exported because it is the manual
# shadow-painting handoff point.


# -----------------------------------------------------------------------------
# Helpers

def ensure_output_dir(source_dir: Path | None = None) -> Path:
    """Return the output directory. Defaults to CSC_COMFYUI_OUTPUT_DIR when source_dir is absent."""
    if source_dir is not None:
        return source_dir
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    if not OUTPUT_DIR.is_dir():
        raise FileNotFoundError(f"Output directory does not exist and could not be created: {OUTPUT_DIR}")
    return OUTPUT_DIR


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())



# -----------------------------------------------------------------------------
# Alpha-mask helpers  (mirrors icon_img2img.py make_generation_mask / apply_alpha_mask)
# -----------------------------------------------------------------------------
from PIL import Image
import numpy as np


def make_generation_mask(input_path: str, size: int = WORKFLOW_SIZE) -> Image.Image | None:
    """Extract the input's alpha channel and scale to workflow size.

    Returns None if the input is fully opaque — in that case the generated
    output is left fully opaque too (nothing to crop).
    """
    src = Image.open(input_path).convert("RGBA")
    alpha = src.getchannel("A")
    if alpha.getextrema() == (255, 255):
        print("  Input has no transparency; output will remain opaque.")
        return None
    mask = alpha.resize((size, size), Image.LANCZOS)
    # Harden faint antialiasing / background residue while keeping edge softness.
    mask = mask.point(lambda p: 0 if p <= MASK_ALPHA_CUTOFF else p)
    print(f"  Alpha mask extracted: {input_path}")
    return mask


def apply_alpha_mask(image_data: bytes, mask: Image.Image | None) -> Image.Image:
    """Re-apply the source alpha mask to ComfyUI's generated output."""
    img = Image.open(io.BytesIO(image_data)).convert("RGBA")
    if mask is None:
        return img
    if img.size != mask.size:
        mask = mask.resize(img.size, Image.LANCZOS)
    img.putalpha(mask)
    return img


# -----------------------------------------------------------------------------
# Verify uploaded image
# -----------------------------------------------------------------------------
def verify_uploaded_image(upload_result: dict, expected_sha256: str) -> None:
    """Fetch ComfyUI's uploaded input back and compare hashes."""
    params = urllib.parse.urlencode({
        "filename": upload_result["name"],
        "subfolder": upload_result.get("subfolder", ""),
        "type": upload_result.get("type", "input"),
    })
    uploaded_bytes = urllib.request.urlopen(f"{COMFYUI_URL}/view?{params}").read()
    uploaded_sha256 = sha256_bytes(uploaded_bytes)
    if uploaded_sha256 != expected_sha256:
        raise RuntimeError(
            "ComfyUI uploaded-input verification failed: "
            f"local sha256={expected_sha256}, ComfyUI sha256={uploaded_sha256}, "
            f"uploaded name={upload_result['name']}"
        )
    print(f"  Verified uploaded input sha256: {uploaded_sha256[:12]}…")


def upload_image(path: Path, name_override: str | None = None) -> dict:
    # Use unique ComfyUI input filenames. Reusing names lets ComfyUI rename to
    # "file (1).png" / "file (2).png" and makes cache behaviour muddy.
    if name_override:
        filename = name_override
    else:
        stem = path.stem
        ext = path.suffix or ".png"
        filename = f"{stem}_{sha256_file(path)[:12]}_{RUN_ID}{ext}"

    with path.open("rb") as f:
        img_data = f.read()

    boundary = uuid.uuid4().hex
    content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
    body = b"".join([
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
            f"Content-Type: {content_type}\r\n\r\n"
        ).encode() + img_data + b"\r\n",
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="type"\r\n\r\n'
            f"input\r\n"
        ).encode(),
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="overwrite"\r\n\r\n'
            f"true\r\n"
        ).encode(),
        f"--{boundary}--\r\n".encode(),
    ])
    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    result = json.loads(urllib.request.urlopen(req).read())
    print(f"  Uploaded: {result['name']}")
    return result


def resize_to_workflow(img: Image.Image, size: int = WORKFLOW_SIZE) -> Image.Image:
    """Center-crop + scale to exactly `size x size`, matching ComfyUI's ImageScale center."""
    w, h = img.size
    side = min(w, h)
    left = (w - side) // 2
    top = (h - side) // 2
    img = img.crop((left, top, left + side, top + side))
    return img.resize((size, size), Image.LANCZOS)


def prepare_upload_image(input_path: str, workflow_size: int = WORKFLOW_SIZE) -> Image.Image:
    """Prepare an RGBA input for ComfyUI upload by compositing onto neutral gray.

    Asset Editor screenshots are RGBA with a coloured backplate behind the
    building transparent pixels. ComfyUI's VAEEncode discards alpha — it
    encodes whatever RGB is at those transparent pixels. If those pixels are
    green (R=158, G=192, B=83) the model sees green as its initial state and
    tends to generate into or bleed into those regions as green background.

    The fix is to paste the RGBA onto a neutral mid-gray (128, 128, 128) before
    uploading, so the VAE encodes gray instead of green. The correct alpha is
    restored post-generation by apply_alpha_mask() and post-processing still
    produces clean transparent edges on the final sprite.
    """
    img = Image.open(input_path).convert("RGBA")
    img = resize_to_workflow(img, workflow_size)
    arr = np.array(img)
    alpha = arr[:, :, 3]

    # Fill fully-transparent pixels with neutral gray RGB before encoding.
    # Semi-transparent fringe pixels keep their original RGB so they still
    # influence the VAE as soft-edge building pixels, not as flat gray.
    fully_transparent = alpha == 0
    if fully_transparent.any():
        arr[fully_transparent, :3] = [128, 128, 128]
        arr[fully_transparent, 3] = 255  # opaque gray for VAE encoding

    return Image.fromarray(arr, "RGBA")


def build_workflow(image_name: str, cfg: float, run_id: str) -> dict:
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "2": {"class_type": "LoraLoader", "inputs": {
            "model": ["1", 0],
            "clip": ["1", 1],
            "lora_name": LORA_NAME,
            "strength_model": LORA_STR,
            "strength_clip": LORA_STR,
        }},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": PROMPT}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": NEGATIVE}},
        "5": {"class_type": "LoadImage", "inputs": {"image": image_name}},
        "6": {"class_type": "VAEEncode", "inputs": {"pixels": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "KSampler", "inputs": {
            "model": ["2", 0],
            "positive": ["3", 0],
            "negative": ["4", 0],
            "latent_image": ["6", 0],
            "seed": SEED,
            "steps": STEPS,
            "cfg": cfg,
            "sampler_name": SAMPLER,
            "scheduler": SCHEDULER,
            "denoise": DENOISE,
        }},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"sv_img2img_{run_id}"}},
    }


def queue_prompt(workflow: dict) -> str:
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    result = json.loads(urllib.request.urlopen(req).read())
    print(f"  Queued: {result['prompt_id']}")
    return result["prompt_id"]


def wait_for_completion(prompt_id: str, timeout: int = 300) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}") as r:
            history = json.loads(r.read())
        if prompt_id in history:
            entry = history[prompt_id]
            status = entry.get("status", {})
            if status.get("completed", True):
                return entry
        time.sleep(3)
    raise TimeoutError("ComfyUI timed out")


def get_output_image(history: dict):
    for node_output in history.get("outputs", {}).values():
        if "images" in node_output:
            img_info = node_output["images"][0]
            params = urllib.parse.urlencode({
                "filename": img_info["filename"],
                "subfolder": img_info.get("subfolder", ""),
                "type": img_info.get("type", "output"),
            })
            return urllib.request.urlopen(f"{COMFYUI_URL}/view?{params}").read(), img_info["filename"]
    return None, None


def summarize_history_failure(history: dict) -> str:
    status = history.get("status", {})
    messages = status.get("messages", [])
    cached = []
    errors = []
    for kind, payload in messages:
        if kind == "execution_cached":
            cached = payload.get("nodes", [])
        elif "error" in kind:
            errors.append((kind, payload))
    if errors:
        return f"ComfyUI reported errors: {errors}"
    if cached and not history.get("outputs"):
        return "ComfyUI returned cached execution with no output images."
    return f"No image outputs found in ComfyUI history. Status: {status.get('status_str', 'unknown')}"


_SUFFIXES = (
    "_Visible_PreShadow",
    "_Input",
    "_Revealed",
    "_Visible",
    "_UnderConstruction",
    "_Pillaged",
    "_Raw",
)
"""Pipeline suffix types, ordered longest-match-first for iterative stripping."""


def output_stem_for_source(source_path: Path, cfg: float, raw: bool = False) -> str:
    """Output filename stem for a single-CFG pipeline run.

    Naming order is always ``[name]_Visible[_Raw]`` — no cfg tag.
    All pipeline suffixes are iteratively stripped before re-suffixing, so
    passing an already-processed filename is idempotent.
    """
    stem = source_path.stem
    # Strip all known pipeline suffixes, then any residual bare "Input" token
    for _ in range(4):
        for suf in _SUFFIXES:
            if stem.endswith(suf):
                stem = stem[: -len(suf)]
                break
        else:
            if "Input" in stem:
                stem = stem.replace("Input", "")
                continue
            break
    stem = stem + "_Visible"
    if raw:
        stem = stem + "_Raw"
    return stem


def revealed_stem_for_source(source_path: Path, cfg: float) -> str:
    """Like output_stem_for_source but produces the '_Revealed' base stem."""
    stem = source_path.stem
    for _ in range(4):
        for suf in _SUFFIXES:
            if stem.endswith(suf):
                stem = stem[: -len(suf)]
                break
        if "Input" in stem:
            stem = stem.replace("Input", "")
            continue
        break
    return stem + "_Revealed"


def run_variant(image_name: str, source_path: Path, cfg: float,
                postprocess_config, generation_mask, keep_intermediates: bool = KEEP_INTERMEDIATES) -> list[str]:
    print(f"\nGenerating (cfg={cfg}, seed={SEED})...")
    workflow = build_workflow(image_name, cfg, run_id=RUN_ID)
    prompt_id = queue_prompt(workflow)
    history = wait_for_completion(prompt_id)
    img_data, filename = get_output_image(history)
    if not img_data:
        print(f"  {summarize_history_failure(history)}")
        print("  Retrying once with a cache-busting save prefix...")
        workflow = build_workflow(image_name, cfg, run_id=f"{RUN_ID}_retry_{random.randint(1000, 9999)}")
        prompt_id = queue_prompt(workflow)
        history = wait_for_completion(prompt_id)
        img_data, filename = get_output_image(history)
        if not img_data:
            raise RuntimeError(summarize_history_failure(history))

    src_dir = source_path.parent
    produced: list[str] = []
    intermediate_paths: list[Path] = []
    intermediate_dir = src_dir if keep_intermediates else Path(tempfile.gettempdir())

    # Step 4: apply the input alpha mask to crop the generated output to the subject
    masked_img = apply_alpha_mask(img_data, generation_mask)

    if keep_intermediates:
        raw_path = intermediate_dir / f"{output_stem_for_source(source_path, cfg, raw=True)}.png"
    else:
        raw_path = intermediate_dir / f"{output_stem_for_source(source_path, cfg, raw=True)}_{RUN_ID}.png"
        intermediate_paths.append(raw_path)
    masked_img.save(raw_path)
    print(f"  Raw intermediate: {raw_path}")

    # Step 5: post-process only to the large pre-shadow handoff image. This is
    # the file to paint manually before sv_postprocess.py scales/places it onto
    # the final 256px canvas and adds shadow plates / state variants.
    postprocess_config.enable_base_shadow = False
    postprocess_config.enable_resize_canvas = False
    pre_shadow_path = src_dir / f"{output_stem_for_source(source_path, cfg)}_PreShadow.png"
    pre_shadow_result = sv_process(str(raw_path), str(pre_shadow_path), config=postprocess_config)
    print(f"  PreShadow handoff: {pre_shadow_result}")

    produced = [pre_shadow_result]
    if keep_intermediates:
        produced.insert(0, str(raw_path))

    if not keep_intermediates:
        for path in intermediate_paths:
            try:
                path.unlink(missing_ok=True)
            except OSError as exc:
                print(f"  Could not remove intermediate {path}: {exc}")

    return produced


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Civ 6 strategic-view sprite from a source image.")
    parser.add_argument("source_image", help="Source/reference image to upload to ComfyUI for img2img.")
    parser.add_argument("--keep-intermediates", dest="keep_intermediates",
                        action=argparse.BooleanOptionalAction, default=None,
                        help="Keep _Visible_Raw beside the exported large _Visible_PreShadow. Default/env: off.")
    add_processing_options(parser)
    args = parser.parse_args()

    source_path = Path(args.source_image).expanduser().resolve()
    if not source_path.exists():
        raise FileNotFoundError(f"Source image not found: {source_path}")

    src_dir = source_path.parent
    ensure_output_dir()          # still a no-op guard; OUTPUT_DIR still created if needed
    local_input_sha256 = sha256_file(source_path)
    print(f"Input image: {source_path}")
    print(f"Input sha256: {local_input_sha256}")
    print(f"Run id: {RUN_ID}")
    print(f"Output dir: {src_dir}")

    # Step 1: extract alpha mask from input BEFORE uploading
    print("Extracting alpha mask from input...")
    generation_mask = make_generation_mask(str(source_path))

    print("Uploading source image...")
    # Prepare for ComfyUI upload: composite RGBA transparent pixels onto neutral
    # mid-gray so the VAEEncode node (which drops alpha) encodes gray background
    # instead of the green Asset Editor backplate. apply_alpha_mask() restores
    # transparency post-generation on the raw output.
    prepared_img = prepare_upload_image(str(source_path))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tf:
        temp_prepared_path = tf.name
    try:
        prepared_img.save(temp_prepared_path)
        upload_result = upload_image(Path(temp_prepared_path))
        prepared_sha256 = sha256_file(Path(temp_prepared_path))
        verify_uploaded_image(upload_result, prepared_sha256)
    finally:
        try:
            Path(temp_prepared_path).unlink(missing_ok=True)
        except OSError as exc:
            print(f"Could not remove temporary prepared upload {temp_prepared_path}: {exc}")
    image_name = upload_result["name"]
    print(f"Workflow LoadImage input: {image_name}")

    postprocess_config = config_from_args(args)
    cfg = CFG_VALUE
    keep_intermediates = KEEP_INTERMEDIATES if args.keep_intermediates is None else args.keep_intermediates
    results = run_variant(
        image_name,
        source_path,
        cfg,
        postprocess_config,
        generation_mask,
        keep_intermediates=keep_intermediates,
    )

    print(f"\nDone! {len(results)} file(s).")
    for result in results:
        print(result)
    print("\nNext: paint directional shading on the _Visible_PreShadow file, then run:")
    print(f"  python {SCRIPT_DIR / 'sv_postprocess.py'} {results[-1]}")


if __name__ == "__main__":
    main()
