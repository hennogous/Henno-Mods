"""
Full pipeline: flat render → canny edges → ControlNet + SV LoRA → sprite
"""
import json, urllib.request, time, random, os
import numpy as np
from PIL import Image, ImageFilter

COMFY_URL = "http://127.0.0.1:8188"
RENDER_PATH = "C:/Users/Shadow/.openclaw/workspace/sv_render_output/sv_render.png"
OUTPUT_PREFIX = "sv_sprite_controlled"

def upload_image(path):
    """Upload image to ComfyUI for use as ControlNet input."""
    import urllib.parse, mimetypes
    boundary = "----FormBoundary" + str(random.randint(100000, 999999))
    with open(path, 'rb') as f:
        img_data = f.read()
    filename = os.path.basename(path)
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{filename}"\r\n'
        f"Content-Type: image/png\r\n\r\n"
    ).encode() + img_data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{COMFY_URL}/upload/image",
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def queue_prompt(workflow):
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def wait_for_completion(prompt_id, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}") as r:
            history = json.loads(r.read())
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(3)
    return None

# Upload the render
print("Uploading render to ComfyUI...")
upload_result = upload_image(RENDER_PATH)
uploaded_filename = upload_result["name"]
print(f"  Uploaded as: {uploaded_filename}")

# Build workflow: SDXL + LoRA + ControlNet (canny)
workflow = {
    "1": {  # Checkpoint
        "class_type": "CheckpointLoaderSimple",
        "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}
    },
    "2": {  # LoRA
        "class_type": "LoraLoader",
        "inputs": {
            "model": ["1", 0], "clip": ["1", 1],
            "lora_name": "civ6_strategic_view.safetensors",
            "strength_model": 0.85, "strength_clip": 0.85
        }
    },
    "3": {  # Positive prompt
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": ["2", 1],
            "text": "bakery building, civ 6 strategic view sprite, top-down isometric, simplified illustration, muted earth tones, hand-painted style, fully visible"
        }
    },
    "4": {  # Negative prompt
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": ["2", 1],
            "text": "realistic, photo, 3d render, blurry, text, watermark, ugly, deformed, photorealistic"
        }
    },
    "5": {  # Load ControlNet
        "class_type": "ControlNetLoader",
        "inputs": {"control_net_name": "diffusers_xl_canny_mid.safetensors"}
    },
    "6": {  # Load image
        "class_type": "LoadImage",
        "inputs": {"image": uploaded_filename}
    },
    "7": {  # Canny edge detection (built-in)
        "class_type": "Canny",
        "inputs": {
            "image": ["6", 0],
            "low_threshold": 0.4,
            "high_threshold": 0.8,
        }
    },
    "8": {  # Apply ControlNet
        "class_type": "ControlNetApplyAdvanced",
        "inputs": {
            "positive": ["3", 0],
            "negative": ["4", 0],
            "control_net": ["5", 0],
            "image": ["7", 0],
            "strength": 0.8,
            "start_percent": 0.0,
            "end_percent": 0.8
        }
    },
    "9": {  # Empty latent
        "class_type": "EmptyLatentImage",
        "inputs": {"width": 512, "height": 512, "batch_size": 1}
    },
    "10": {  # KSampler
        "class_type": "KSampler",
        "inputs": {
            "model": ["2", 0],
            "positive": ["8", 0],
            "negative": ["8", 1],
            "latent_image": ["9", 0],
            "seed": 42,
            "steps": 28,
            "cfg": 7.0,
            "sampler_name": "dpmpp_2m",
            "scheduler": "karras",
            "denoise": 1.0
        }
    },
    "11": {  # VAE decode
        "class_type": "VAEDecode",
        "inputs": {"samples": ["10", 0], "vae": ["1", 2]}
    },
    "12": {  # Save
        "class_type": "SaveImage",
        "inputs": {"images": ["11", 0], "filename_prefix": OUTPUT_PREFIX}
    }
}

print("Queuing ControlNet + LoRA generation...")
resp = queue_prompt(workflow)
pid = resp["prompt_id"]
print(f"  Prompt ID: {pid}")

print("Waiting for completion (this takes ~2-3 min)...")
result = wait_for_completion(pid, timeout=300)
if result and "outputs" in result:
    for node_id, node_out in result["outputs"].items():
        if "images" in node_out:
            for img in node_out["images"]:
                print(f"  Done: {img['filename']}")
else:
    print("  FAILED or timed out")
