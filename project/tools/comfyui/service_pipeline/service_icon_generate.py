"""
Generate abstract CSC service/unit icons with the civ6_unit_icons LoRA, then
post-process each render into a transparent flat-white pictogram.

Default smoke-test concepts:
  storekeeper, innkeeper, horticulturist, ride technician, groundskeeper
"""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

from service_postprocess import ServiceIconPostprocessConfig, process_image

COMFY = "http://127.0.0.1:8188"
SCRIPT_DIR = Path(__file__).resolve().parent
OUT_DIR = SCRIPT_DIR / "outputs"
RAW_DIR = OUT_DIR / "raw"
FINAL_DIR = OUT_DIR / "final"

CHECKPOINT = "sd_xl_base_1.0.safetensors"
LORA = "civ6_unit_icons.safetensors"
LORA_STRENGTH = 1.0
WIDTH = 768
HEIGHT = 768
STEPS = 28
CFG = 8.0
SAMPLER = "dpmpp_2m"
SCHEDULER = "karras"

NEGATIVE = (
    "person, human, face, portrait, body, hands, character, worker, man, woman, people, "
    "photo, realistic, 3d render, colorful, gradients, complex scene, environment, landscape, "
    "text, letters, numbers, watermark, logo, label, sign text, noisy, deformed, cluttered, detailed background, "
    "outline, line art, hollow shape, thin strokes, sketch, hatching, shading, grey background, "
    "border, frame, square border, rectangular frame, box outline"
)

# Keep each service concept to one symbol if possible. The training data is
# symbolic: crossbowman -> crossbow, not a person with a crossbow.
TESTS = [
    ("storekeeper", "wooden storage crate"),
    ("innkeeper", "beer mug and key"),
    ("horticulturist", "single sprouting leaf"),
    ("ride_technician", "gear and wrench"),
    ("groundskeeper", "garden rake"),
]


def make_prompt(concept: str, symbol: str) -> str:
    return (
        f"civ 6 unit icon, {concept}, solid filled white silhouette of {symbol}, "
        "no outlines, no hollow line art, no border, no frame, solid black background, "
        "centered flat vector stencil, minimal geometric shape, abstract symbolic icon, "
        "no person, no face, no body, no scene, no text, readable at 32 pixels"
    )


def post_json(path: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(COMFY + path, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def get_json(path: str) -> dict:
    with urllib.request.urlopen(COMFY + path, timeout=30) as r:
        return json.loads(r.read())


def build_workflow(prompt: str, seed: int, prefix: str) -> dict:
    return {
        "1": {"class_type": "CheckpointLoaderSimple", "inputs": {"ckpt_name": CHECKPOINT}},
        "2": {"class_type": "LoraLoader", "inputs": {
            "model": ["1", 0], "clip": ["1", 1], "lora_name": LORA,
            "strength_model": LORA_STRENGTH, "strength_clip": LORA_STRENGTH,
        }},
        "3": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": prompt}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["2", 1], "text": NEGATIVE}},
        "5": {"class_type": "EmptyLatentImage", "inputs": {"width": WIDTH, "height": HEIGHT, "batch_size": 1}},
        "6": {"class_type": "KSampler", "inputs": {
            "model": ["2", 0], "positive": ["3", 0], "negative": ["4", 0], "latent_image": ["5", 0],
            "seed": seed, "steps": STEPS, "cfg": CFG, "sampler_name": SAMPLER, "scheduler": SCHEDULER, "denoise": 1.0,
        }},
        "7": {"class_type": "VAEDecode", "inputs": {"samples": ["6", 0], "vae": ["1", 2]}},
        "8": {"class_type": "SaveImage", "inputs": {"images": ["7", 0], "filename_prefix": prefix}},
    }


def wait_for(prompt_id: str, timeout: int = 600) -> dict:
    start = time.time()
    while time.time() - start < timeout:
        hist = get_json(f"/history/{prompt_id}")
        if prompt_id in hist:
            entry = hist[prompt_id]
            status = entry.get("status", {})
            if status.get("completed", True):
                return entry
        time.sleep(2)
    raise TimeoutError(prompt_id)


def download_first_image(history: dict, out_path: Path) -> Path:
    for node_output in history.get("outputs", {}).values():
        for img in node_output.get("images", []):
            qs = urllib.parse.urlencode({"filename": img["filename"], "subfolder": img.get("subfolder", ""), "type": img.get("type", "output")})
            with urllib.request.urlopen(COMFY + "/view?" + qs, timeout=60) as r:
                out_path.write_bytes(r.read())
            return out_path
    raise RuntimeError(f"No images in history outputs: {history.get('outputs')}")


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    run_id = time.strftime("%Y%m%d_%H%M%S")
    post_cfg = ServiceIconPostprocessConfig(output_size=256, target_fill=0.78)
    results = []

    for i, (slug, symbol) in enumerate(TESTS, start=1):
        prompt = make_prompt(slug.replace("_", " "), symbol)
        seed = 629000 + i
        prefix = f"csc_service_icon_{run_id}_{i:02d}_{slug}"
        print(f"\n[{i}/{len(TESTS)}] {slug}")
        print(prompt)
        prompt_id = post_json("/prompt", {"prompt": build_workflow(prompt, seed, prefix)})["prompt_id"]
        hist = wait_for(prompt_id)
        raw = download_first_image(hist, RAW_DIR / f"{i:02d}_{slug}_raw.png")
        final = process_image(raw, FINAL_DIR / f"{i:02d}_{slug}.png", post_cfg)
        print(f"raw:   {raw}")
        print(f"final: {final}")
        results.append({
            "slug": slug,
            "symbol": symbol,
            "prompt": prompt,
            "negative": NEGATIVE,
            "seed": seed,
            "prompt_id": prompt_id,
            "raw": str(raw),
            "final": str(final),
        })

    manifest = OUT_DIR / f"manifest_{run_id}.json"
    manifest.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("\nDONE")
    print(manifest)
    for row in results:
        print(row["final"])


if __name__ == "__main__":
    main()
