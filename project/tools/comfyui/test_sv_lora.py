"""
Test the civ6_strategic_view LoRA via ComfyUI API.
Generates a few SV-style sprites using text prompts.
"""
import json, urllib.request, urllib.parse, time, random

COMFY_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = "C:/Users/Shadow/ComfyUI/output"

def queue_prompt(prompt_workflow):
    data = json.dumps({"prompt": prompt_workflow}).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def get_history(prompt_id):
    with urllib.request.urlopen(f"{COMFY_URL}/history/{prompt_id}") as r:
        return json.loads(r.read())

def wait_for_completion(prompt_id, timeout=300):
    start = time.time()
    while time.time() - start < timeout:
        history = get_history(prompt_id)
        if prompt_id in history:
            return history[prompt_id]
        time.sleep(3)
    return None

def build_workflow(prompt_text, negative_prompt, seed, filename_prefix):
    """Minimal SDXL + LoRA workflow."""
    return {
        "1": {  # CheckpointLoader
            "class_type": "CheckpointLoaderSimple",
            "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}
        },
        "2": {  # LoRA loader
            "class_type": "LoraLoader",
            "inputs": {
                "model": ["1", 0],
                "clip": ["1", 1],
                "lora_name": "civ6_strategic_view.safetensors",
                "strength_model": 0.9,
                "strength_clip": 0.9
            }
        },
        "3": {  # Positive CLIP
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 1], "text": prompt_text}
        },
        "4": {  # Negative CLIP
            "class_type": "CLIPTextEncode",
            "inputs": {"clip": ["2", 1], "text": negative_prompt}
        },
        "5": {  # Empty latent
            "class_type": "EmptyLatentImage",
            "inputs": {"width": 256, "height": 256, "batch_size": 1}
        },
        "6": {  # KSampler
            "class_type": "KSampler",
            "inputs": {
                "model": ["2", 0],
                "positive": ["3", 0],
                "negative": ["4", 0],
                "latent_image": ["5", 0],
                "seed": seed,
                "steps": 25,
                "cfg": 7.5,
                "sampler_name": "euler",
                "scheduler": "karras",
                "denoise": 1.0
            }
        },
        "7": {  # VAE decode
            "class_type": "VAEDecode",
            "inputs": {"samples": ["6", 0], "vae": ["1", 2]}
        },
        "8": {  # Save image
            "class_type": "SaveImage",
            "inputs": {"images": ["7", 0], "filename_prefix": filename_prefix}
        }
    }

NEGATIVE = "realistic, photo, 3d render, blurry, text, watermark, ugly, deformed"

tests = [
    ("bakery building, civ 6 strategic view sprite, top-down isometric, simplified illustration, muted colors, hand-painted style, fully visible", "sv_test_bakery"),
    ("campus library building in campus district, fully visible, civ 6 strategic view sprite, top-down isometric, simplified illustration, muted colors, hand-painted style", "sv_test_library"),
    ("commercial hub district, fully visible, civ 6 strategic view sprite, district icon, top-down isometric, simplified illustration, muted colors, hand-painted style", "sv_test_commercial"),
]

print("Queuing SV LoRA test generations...")
results = []
for pos, prefix in tests:
    seed = random.randint(1, 999999)
    wf = build_workflow(pos, NEGATIVE, seed, prefix)
    resp = queue_prompt(wf)
    pid = resp["prompt_id"]
    print(f"  Queued: {prefix} (id={pid[:8]}...)")
    results.append((pid, prefix, pos))

print("\nWaiting for completions...")
output_files = []
for pid, prefix, pos in results:
    result = wait_for_completion(pid)
    if result and "outputs" in result:
        for node_id, node_out in result["outputs"].items():
            if "images" in node_out:
                for img in node_out["images"]:
                    fpath = f"C:/Users/Shadow/ComfyUI/output/{img['filename']}"
                    output_files.append((prefix, fpath))
                    print(f"  Saved: {img['filename']}")
    else:
        print(f"  FAILED or timed out: {prefix}")

print(f"\nDone. {len(output_files)} images generated.")
for prefix, fpath in output_files:
    print(f"  {prefix}: {fpath}")
