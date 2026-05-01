"""
Icon LoRA img2img v3 — ControlNet Canny + SDXL + icon LoRA
Canny edges lock structure; LoRA pushes to Civ 6 icon style.
Post-processing: rembg bg removal + thick outer silhouette (OpenCV).
"""
import json, urllib.request, urllib.parse, time, sys, os, uuid, importlib.util
import numpy as np
from PIL import Image, ImageFilter

COMFYUI_URL = "http://127.0.0.1:8188"
INPUT_IMAGE = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Shadow\Desktop\Working Files\Screenshot 2026-03-29 at 09.32.16.png"
OUTPUT_DIR = r"C:\Users\Shadow\.openclaw\workspace\tmp"
os.makedirs(OUTPUT_DIR, exist_ok=True)

DENOISE     = 0.55   # Enough freedom for painterly style
LORA_STR    = 0.92
CFG         = 7.0
STEPS       = 30
CN_STRENGTH = 0.90   # CN holds geometry while LoRA drives style
SEEDS       = [2025]  # v3 is consistently the best seed

PROMPT = (
    "civ 6 icon, cartoon isometric, bold black outlines, outlined illustration, "
    "thick stroke, hand-painted, cel-shaded, sticker style, "
    "classical era industrial building, stone and timber, warm earthy tones, "
    "olive green roof tiles, game building icon, single building centered, "
    "isometric 3/4 view, muted palette, painterly brush strokes, "
    "black outline on every architectural element, outline art style"
)
NEGATIVE = (
    "blurry, realistic, photograph, text, watermark, multiple buildings, "
    "cluttered, dark, noisy, modern, futuristic, sky, clouds, grass, ground plane"
)


def upload_image(filepath, name_override=None):
    filename = name_override or os.path.basename(filepath)
    with open(filepath, "rb") as f:
        data = f.read()
    boundary = uuid.uuid4().hex
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{COMFYUI_URL}/upload/image", data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST"
    )
    result = json.loads(urllib.request.urlopen(req).read())
    print(f"  Uploaded: {result['name']}")
    return result["name"]


def prepare_canny(input_path, low=80, high=180):
    """Extract Canny edges and save as PNG for ControlNet."""
    import cv2
    img = cv2.imread(input_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Slight blur first to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, low, high)
    # Dilate slightly so edges are visible to CN
    kernel = np.ones((2, 2), np.uint8)
    edges = cv2.dilate(edges, kernel, iterations=1)
    # Convert to 3-channel RGB (CN expects colour image)
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    canny_path = os.path.join(OUTPUT_DIR, "canny_input.png")
    cv2.imwrite(canny_path, edges_rgb)
    print(f"  Canny saved: {canny_path}")
    return canny_path


def build_workflow(image_name, canny_name, seed):
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
            "inputs": {"filename_prefix": "icon_cn_v3", "images": ["13", 0]}
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
            return history[prompt_id]
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


def load_postprocess():
    spec = importlib.util.spec_from_file_location(
        "icon_postprocess",
        os.path.join(os.path.dirname(__file__), "icon_postprocess.py")
    )
    pp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pp)
    return pp


if __name__ == "__main__":
    pp = load_postprocess()

    print("Preparing Canny edges...")
    canny_path = prepare_canny(INPUT_IMAGE)

    print("Uploading images...")
    image_name = upload_image(INPUT_IMAGE)
    canny_name = upload_image(canny_path, name_override="canny_input.png")

    results = []
    for i, seed in enumerate(SEEDS):
        print(f"\nGenerating variant {i+1}/{len(SEEDS)} (seed={seed})...")
        workflow = build_workflow(image_name, canny_name, seed)
        prompt_id = queue_prompt(workflow)
        history = wait_for_completion(prompt_id)
        img_data, filename = get_output_image(history)
        if img_data:
            raw_path = os.path.join(OUTPUT_DIR, f"icon_v3_raw_{i+1}.png")
            with open(raw_path, "wb") as f:
                f.write(img_data)
            out_path = os.path.join(OUTPUT_DIR, f"icon_v3_{i+1}.png")
            pp.process_icon(raw_path, out_path)
            results.append(out_path)

    print(f"\nDone! {len(results)} variants.")
    for r in results:
        print(r)
