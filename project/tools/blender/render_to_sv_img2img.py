"""
img2img pipeline: Blender render -> LoRA style transfer
Vary denoise + LoRA strength to find the sweet spot.
"""
import json, urllib.request, time, random, os, sys
sys.path.insert(0, "C:/Users/Shadow/.openclaw/workspace")
from add_sv_shadow import process as sv_process
from PIL import Image

COMFY_URL = "http://127.0.0.1:8188"
RENDER_PATH = "C:/Users/Shadow/.openclaw/workspace/sv_render_output/sv_render.png"

def upload_image(path):
    boundary = "----FormBoundary" + str(random.randint(100000, 999999))
    with open(path, 'rb') as f:
        img_data = f.read()
    filename = os.path.basename(path)
    body = (f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{filename}\"\r\nContent-Type: image/png\r\n\r\n"
            ).encode() + img_data + f"\r\n--{boundary}--\r\n".encode()
    req = urllib.request.Request(f"{COMFY_URL}/upload/image", data=body,
                                  headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

def queue_prompt(workflow):
    data = json.dumps({"prompt": workflow}).encode("utf-8")
    req = urllib.request.Request(f"{COMFY_URL}/prompt", data=data,
                                  headers={"Content-Type": "application/json"})
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

def run(denoise, lora_strength, suffix):
    workflow = {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": "sd_xl_base_1.0.safetensors"}},
        "2": {"class_type": "LoraLoader", "inputs": {
            "model": ["1", 0], "clip": ["1", 1],
            "lora_name": "civ6_strategic_view.safetensors",
            "strength_model": lora_strength, "strength_clip": lora_strength
        }},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1],
            "text": "classical period industrial utility building, civ 6 strategic view sprite, simplified illustration, muted earth tones, hand-painted style"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1],
            "text": "realistic, photo, blurry, text, watermark, ugly, deformed, added details, invented features, new elements"}},
        "5": {"class_type": "LoadImage", "inputs": {"image": uploaded_filename}},
        "6": {"class_type": "VAEEncode", "inputs": {"pixels": ["5", 0], "vae": ["1", 2]}},
        "7": {"class_type": "KSampler", "inputs": {
            "model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0], "latent_image": ["6", 0],
            "seed": 42, "steps": 25, "cfg": 6.0 if "cfg6" in suffix else 8.0,
            "sampler_name": "dpmpp_2m", "scheduler": "karras", "denoise": denoise
        }},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["1", 2]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": f"sv_img2img_{suffix}"}}
    }
    print(f"Queuing denoise={denoise} lora={lora_strength} -> {suffix}...")
    resp = queue_prompt(workflow)
    result = wait_for_completion(resp["prompt_id"])
    if result and "outputs" in result:
        for node_out in result["outputs"].values():
            if "images" in node_out:
                fname = node_out['images'][0]['filename']
                print(f"  Done: {fname}")
                # Post-process: add SV shadow
                fpath = f"C:/Users/Shadow/ComfyUI/output/{fname}"
                shadow_path = sv_process(fpath)
                print(f"  SV: {os.path.basename(shadow_path)}")
    else:
        print("  FAILED")

print("Uploading render...")
upload_result = upload_image(RENDER_PATH)
uploaded_filename = upload_result["name"]
print(f"  Uploaded: {uploaded_filename}")

run(denoise=0.55, lora_strength=0.6, suffix="classical_cfg6")
run(denoise=0.55, lora_strength=0.6, suffix="classical_cfg8")
