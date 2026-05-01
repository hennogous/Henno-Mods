import requests, time, os

workflow = {
    "1": {"inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}, "class_type": "CheckpointLoaderSimple"},
    "2": {"inputs": {
        "text": "isometric medieval bakery building for Civilization 6 strategy game, simple exaggerated chunky shapes like toy model, stone walls with warm bread tones, thatched roof with detail visible from above, wood beam accents, small chimney with smoke, bread oven visible, flour sacks outside, warm golden lighting from southwest, game asset on hex tile, stylized not realistic, big shapes with 3:2:1 ratio of large medium small details, fun wonky shapes avoiding straight lines, roof detail important for top-down camera angle",
        "clip": ["1", 1]
    }, "class_type": "CLIPTextEncode"},
    "3": {"inputs": {
        "text": "realistic, photographic, blurry, low quality, distorted, text, watermark, UI elements, modern, sci-fi, cartoon, anime, pixel art",
        "clip": ["1", 1]
    }, "class_type": "CLIPTextEncode"},
    "4": {"inputs": {"width": 768, "height": 768, "batch_size": 1}, "class_type": "EmptyLatentImage"},
    "5": {"inputs": {
        "seed": 88442, "steps": 30, "cfg": 8.0,
        "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1.0,
        "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]
    }, "class_type": "KSampler"},
    "6": {"inputs": {"samples": ["5", 0], "vae": ["1", 2]}, "class_type": "VAEDecode"},
    "7": {"inputs": {"filename_prefix": "csc_bakery_concept", "images": ["6", 0]}, "class_type": "SaveImage"}
}

print("Generating CSC Bakery concept art...")
r = requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow})
if r.status_code != 200:
    print(f"Error: {r.text}")
    exit(1)

prompt_id = r.json()["prompt_id"]
print(f"Queued: {prompt_id}")

for i in range(120):
    time.sleep(2)
    q = requests.get("http://127.0.0.1:8188/queue").json()
    if len(q.get("queue_running", [])) == 0 and len(q.get("queue_pending", [])) == 0:
        print("Done!")
        break
    if i % 10 == 0:
        print(f"  {i*2}s elapsed...")

# Find the output
output_dir = r"C:\Users\Shadow\ComfyUI\output"
for f in sorted(os.listdir(output_dir), key=lambda x: os.path.getmtime(os.path.join(output_dir, f)), reverse=True):
    if f.startswith("csc_bakery") and f.endswith(".png"):
        path = os.path.join(output_dir, f)
        print(f"FOUND: {path}")
        break
else:
    print("Image not found in output")
