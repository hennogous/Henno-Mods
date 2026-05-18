"""
Icon LoRA img2img v3 — ControlNet Canny + SDXL + icon LoRA.

Canny edges lock structure; LoRA pushes to Civ 6 icon style.
Post-processing: rembg background removal + outline/detail passes.
"""
import argparse
import json, urllib.request, urllib.parse, time, os, uuid, io
import numpy as np
from PIL import Image

from icon_utils import scale_like_comfy_center

COMFYUI_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = os.environ.get(
    "CSC_COMFYUI_OUTPUT_DIR",
    r"C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\ComfyUI output"
)
RUN_ID = time.strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
def ensure_output_dir():
    """Create the configured output directory immediately before each local write."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    if not os.path.isdir(OUTPUT_DIR):
        raise FileNotFoundError(f"Output directory does not exist and could not be created: {OUTPUT_DIR}")


ensure_output_dir()

DENOISE     = 0.4
# Higher = more freedom/style drift from input; lower = preserves source image more tightly. (0-1; 0.35-0.55 useful, quite sensitive)

LORA_STR    = 0.92
# Higher = stronger Civ 6 icon LoRA style; lower = more base SDXL/general style. (0-1.2; 0.8-1.0 useful, medium sensitivity)

CFG         = 9.0
# Higher = follows prompt harder but can get harsh; lower = softer/more varied but may ignore prompt. (1-15; 7-10 useful, medium sensitivity)

STEPS       = 40
# Higher = slower with slightly cleaner/refined output; lower = faster but rougher/less resolved. (15-50; 25-35 useful, low/medium sensitivity)

CN_STRENGTH = 0.95
# Higher = Canny geometry locks shape harder; lower = lets composition/shape drift more. (0-1.5; 0.75-1.0 useful, sensitive near 1.0)

SEEDS       = [2025]
# Add/change seeds for more variants; same seed = repeatable output, different seed = different composition. (any int; not a low/high knob)

CANNY_LOW   = 80
# Higher = ignores faint source edges; lower = includes more weak/noisy edges. (0-255; 40-100 useful, medium sensitivity)

CANNY_HIGH  = 180
# Higher = requires stronger source edges; lower = produces denser Canny structure. (0-255; 120-220 useful, medium sensitivity)

ALPHA_EDGE_LOW = 16
# Higher = cleaner alpha silhouette with fewer soft-edge pixels; lower = includes more antialias fringe. (0-255; 8-32 useful, sensitive)

ALPHA_EDGE_HIGH = 64
# Higher = only strongest alpha transitions outline silhouette; lower = more alpha edge detail. (0-255; 48-96 useful, medium sensitivity)

CANNY_DILATE_SIZE = 2
# Higher = thicker ControlNet guide lines; lower = thinner guide lines. (1-5 px; 1-3 useful, very sensitive)

MASK_ALPHA_CUTOFF = 8
# Higher = removes more faint transparent residue; lower = preserves softer alpha edges. (0-255; 4-24 useful, sensitive)

KEEP_RAW = os.environ.get("CSC_ICON_KEEP_RAW", "1").strip().lower() in {"1", "true", "yes", "on", "y"}
# Keep the alpha-masked _Raw image beside the final output. Default on for
# backwards compatibility with icon_postprocess.py's raw-file batch mode.

PROMPT = (
    "civ 6 icon, cartoon isometric, bold black outlines, outlined illustration, "
    "thick stroke, hand-painted, cel-shaded, sticker style, "
    "classical era industrial building, stone and timber, warm earthy tones, "
    "game building icon, single building centered, "
    "isometric 3/4 view, muted palette, painterly brush strokes, "
    "black outline on every architectural element, outline art style"
)
NEGATIVE = (
    "blurry, realistic, photograph, text, watermark, multiple buildings, "
    "cluttered, dark, noisy, modern, futuristic, sky, clouds, grass, ground plane"
)


def upload_image(filepath, name_override=None):
    # Use unique ComfyUI input filenames. Reusing names lets ComfyUI rename to
    # "file (1).png" / "file (2).png" and makes cache behaviour hard to reason
    # about; unique names keep each run tied to the exact file passed on the CLI.
    if name_override:
        filename = name_override
    else:
        stem, ext = os.path.splitext(os.path.basename(filepath))
        filename = f"{stem}_{RUN_ID}{ext or '.png'}"
    with open(filepath, "rb") as f:
        data = f.read()
    boundary = uuid.uuid4().hex
    parts = [
        (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
            f"Content-Type: image/png\r\n\r\n"
        ).encode() + data + b"\r\n",
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
    ]
    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image", data=b"".join(parts),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    result = json.loads(urllib.request.urlopen(req).read())
    print(f"  Uploaded: {result['name']}")
    return result["name"]


def prepare_canny(input_path, low=CANNY_LOW, high=CANNY_HIGH):
    """Extract alpha-aware Canny edges at the exact 1024x1024 workflow size."""
    import cv2
    pil = Image.open(input_path).convert("RGBA")
    pil = scale_like_comfy_center(pil, 1024, 1024, Image.LANCZOS)
    rgba = np.array(pil)
    alpha = rgba[:, :, 3]
    rgb = rgba[:, :, :3].copy()
    # Transparent pixels are not part of the subject. Composite them to white
    # and mask edges back out so ControlNet sees only the supplied icon.
    rgb[alpha <= ALPHA_EDGE_LOW] = (255, 255, 255)
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    # Slight blur first to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, low, high)
    subject = alpha > ALPHA_EDGE_LOW
    alpha_edges = cv2.Canny(alpha, ALPHA_EDGE_LOW, ALPHA_EDGE_HIGH)
    edges[~subject] = 0
    edges = cv2.bitwise_or(edges, alpha_edges)
    # Dilate slightly so edges are visible to CN
    kernel = np.ones((CANNY_DILATE_SIZE, CANNY_DILATE_SIZE), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    # Convert to 3-channel RGB (CN expects colour image)
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    canny_path = os.path.join(OUTPUT_DIR, "canny_input.png")
    ensure_output_dir()
    if not cv2.imwrite(canny_path, edges_rgb):
        raise IOError(f"Failed to write Canny image: {canny_path}")
    print(f"  Canny saved: {canny_path}")
    return canny_path


def make_generation_mask(input_path, size=1024):
    """Return a 1024x1024 alpha mask matching the workflow's centered image scale.

    The workflow generates RGB, so it cannot preserve transparency by itself.
    We restore transparency from the input alpha after generation, which keeps
    the raw LoRA output bounded to the exact source silhouette.
    """
    src = Image.open(input_path).convert("RGBA")
    alpha = src.getchannel("A")
    if alpha.getextrema() == (255, 255):
        print("Input has no transparency; raw output will remain opaque.")
        return None
    mask = scale_like_comfy_center(alpha, size, size, Image.LANCZOS)
    # Harden faint antialiasing/background residue while keeping edge softness.
    mask = mask.point(lambda p: 0 if p <= MASK_ALPHA_CUTOFF else p)
    return mask


def apply_alpha_mask(image_data, mask):
    img = Image.open(io.BytesIO(image_data)).convert("RGBA")
    if mask is None:
        return img
    if img.size != mask.size:
        mask = mask.resize(img.size, Image.LANCZOS)
    img.putalpha(mask)
    return img


def output_filename_for_input(input_path, variant_index, raw=False):
    """Build human-readable output names from the source icon filename.

    Example:
    CSC_BAKERS_Wind_Mill_Input.png -> CSC_BAKERS_Wind_Mill_Output.png
    """
    stem, ext = os.path.splitext(os.path.basename(input_path))
    ext = ext or ".png"
    if stem.endswith("_Input"):
        stem = stem[:-len("_Input")] + "_Output"
    elif "Input" in stem:
        stem = stem.replace("Input", "Output")
    elif not stem.endswith("_Output"):
        stem = stem + "_Output"

    if raw:
        stem = stem + "_Raw"
    if len(SEEDS) > 1:
        stem = f"{stem}_{variant_index}"
    return stem + ext


def build_workflow(image_name, canny_name, seed, run_id=None):
    # Make SaveImage unique per run. ComfyUI can otherwise report a fully
    # cached success with an empty outputs block, causing "Done! 0 variants."
    run_id = run_id or time.strftime("%Y%m%d_%H%M%S")
    return {
        # 1. Load checkpoint
        "1": {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}
        },
        # 2. Load LoRA
        "2": {
            "class_type": "LoraLoader",
            "inputs": {
                "lora_name": "civ6_icons.safetensors",
                "strength_model": LORA_STR,
                "strength_clip": LORA_STR,
                "model": ["1", 0],
                "clip": ["1", 1]
            }
        },
        # 3. Load ControlNet
        "3": {
            "class_type": "ControlNetLoader",
            "inputs": {"control_net_name": "diffusers_xl_canny_mid.safetensors"}
        },
        # 4. Positive prompt
        "4": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": PROMPT, "clip": ["2", 1]}
        },
        # 5. Negative prompt
        "5": {
            "class_type": "CLIPTextEncode",
            "inputs": {"text": NEGATIVE, "clip": ["2", 1]}
        },
        # 6. Load input image
        "6": {
            "class_type": "LoadImage",
            "inputs": {"image": image_name}
        },
        # 7. Scale input to 1024 for generation (downscale after)
        "7": {
            "class_type": "ImageScale",
            "inputs": {
                "upscale_method": "lanczos",
                "width": 1024, "height": 1024,
                "crop": "center",
                "image": ["6", 0]
            }
        },
        # 8. Load canny image
        "8": {
            "class_type": "LoadImage",
            "inputs": {"image": canny_name}
        },
        # 9. Scale canny to 1024
        "9": {
            "class_type": "ImageScale",
            "inputs": {
                "upscale_method": "lanczos",
                "width": 1024, "height": 1024,
                "crop": "center",
                "image": ["8", 0]
            }
        },
        # 10. Apply ControlNet to conditioning
        "10": {
            "class_type": "ControlNetApply",
            "inputs": {
                "conditioning": ["4", 0],
                "control_net": ["3", 0],
                "image": ["9", 0],
                "strength": CN_STRENGTH
            }
        },
        # 11. VAE encode input image
        "11": {
            "class_type": "VAEEncode",
            "inputs": {"pixels": ["7", 0], "vae": ["1", 2]}
        },
        # 12. KSampler
        "12": {
            "class_type": "KSampler",
            "inputs": {
                "seed": seed,
                "steps": STEPS,
                "cfg": CFG,
                "sampler_name": "dpmpp_2m",
                "scheduler": "karras",
                "denoise": DENOISE,
                "model": ["2", 0],
                "positive": ["10", 0],
                "negative": ["5", 0],
                "latent_image": ["11", 0]
            }
        },
        # 13. VAE decode
        "13": {
            "class_type": "VAEDecode",
            "inputs": {"samples": ["12", 0], "vae": ["1", 2]}
        },
        # 14. Save
        "14": {
            "class_type": "SaveImage",
            "inputs": {"filename_prefix": f"icon_cn_v3_{run_id}", "images": ["13", 0]}
        }
    }


def queue_prompt(workflow):
    data = json.dumps({"prompt": workflow}).encode()
    req = urllib.request.Request(
        f"{COMFYUI_URL}/prompt", data=data,
        headers={"Content-Type": "application/json"}, method="POST"
    )
    result = json.loads(urllib.request.urlopen(req).read())
    print(f"  Queued: {result['prompt_id']}")
    return result["prompt_id"]


def wait_for_completion(prompt_id, timeout=180):
    start = time.time()
    while time.time() - start < timeout:
        resp = urllib.request.urlopen(f"{COMFYUI_URL}/history/{prompt_id}")
        history = json.loads(resp.read())
        if prompt_id in history:
            entry = history[prompt_id]
            status = entry.get("status", {})
            if status.get("completed"):
                return entry
        time.sleep(2)
    raise TimeoutError("ComfyUI timed out")


def get_output_image(history):
    for node_output in history["outputs"].values():
        if "images" in node_output:
            img_info = node_output["images"][0]
            params = urllib.parse.urlencode({
                "filename": img_info["filename"],
                "subfolder": img_info.get("subfolder", ""),
                "type": img_info.get("type", "output")
            })
            return urllib.request.urlopen(f"{COMFYUI_URL}/view?{params}").read(), img_info["filename"]
    return None, None


def summarize_history_failure(history):
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


def main():
    parser = argparse.ArgumentParser(description="Generate a Civ 6 icon from a source image via ComfyUI img2img.")
    parser.add_argument("source_image", help="Source/reference image to upload to ComfyUI.")
    parser.add_argument("--keep-raw", dest="keep_raw", action=argparse.BooleanOptionalAction, default=None,
                        help="Keep the alpha-masked _Raw intermediate. Default/env: on.")
    args = parser.parse_args()

    import icon_postprocess as pp

    keep_raw = KEEP_RAW if args.keep_raw is None else args.keep_raw
    input_abs = os.path.abspath(args.source_image)
    if not os.path.exists(input_abs):
        raise FileNotFoundError(input_abs)
    print(f"Input image: {input_abs}")
    print(f"Run id: {RUN_ID}")
    generation_mask = make_generation_mask(input_abs)
    if generation_mask is not None:
        print("Input transparency detected; raw LoRA output will be masked to the input silhouette.")

    print("Preparing Canny edges...")
    canny_path = prepare_canny(input_abs)

    print("Uploading images...")
    image_name = upload_image(input_abs)
    canny_name = upload_image(canny_path, name_override=f"canny_input_{RUN_ID}.png")

    results = []
    for i, seed in enumerate(SEEDS):
        print(f"\nGenerating variant {i+1}/{len(SEEDS)} (seed={seed})...")
        workflow = build_workflow(image_name, canny_name, seed, run_id=f"{RUN_ID}_{i+1}")
        prompt_id = queue_prompt(workflow)
        history = wait_for_completion(prompt_id)
        img_data, filename = get_output_image(history)
        if not img_data:
            print(f"  {summarize_history_failure(history)}")
            print("  Retrying once with a cache-busting save prefix...")
            workflow = build_workflow(image_name, canny_name, seed, run_id=f"{RUN_ID}_{i+1}_retry")
            prompt_id = queue_prompt(workflow)
            history = wait_for_completion(prompt_id)
            img_data, filename = get_output_image(history)
            if not img_data:
                raise RuntimeError(summarize_history_failure(history))
        if img_data:
            ensure_output_dir()
            raw_path = os.path.join(OUTPUT_DIR, output_filename_for_input(input_abs, i+1, raw=True))
            raw_img = apply_alpha_mask(img_data, generation_mask)
            raw_img.save(raw_path)
            out_path = os.path.join(OUTPUT_DIR, output_filename_for_input(input_abs, i+1))
            pp.process_icon(raw_path, out_path, canny_path)
            if not keep_raw:
                try:
                    os.remove(raw_path)
                except OSError as exc:
                    print(f"  Could not remove raw intermediate {raw_path}: {exc}")
            results.append(out_path)

    print(f"\nDone! {len(results)} variants.")
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
