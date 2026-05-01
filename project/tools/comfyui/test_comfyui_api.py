import requests
import json
import time
import base64

# Simple API test for ComfyUI
def generate_image():
    # Basic workflow for SD 1.5
    workflow = {
        "3": {
            "inputs": {
                "seed": 42,
                "steps": 20,
                "cfg": 7.5,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "model": ["4", 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
                "latent_image": ["5", 0]
            },
            "class_type": "KSampler"
        },
        "4": {
            "inputs": {
                "ckpt_name": "sd_v1-5-pruned.safetensors"
            },
            "class_type": "CheckpointLoaderSimple"
        },
        "5": {
            "inputs": {
                "width": 1920,
                "height": 1080,
                "batch_size": 1
            },
            "class_type": "EmptyLatentImage"
        },
        "6": {
            "inputs": {
                "text": "Bill Murray aesthetic desktop wallpaper, Lost in Translation vibes, Tokyo neon lights at dusk, contemplative minimalism, pink and blue color palette, urban photography style, cinematic composition, moody atmosphere",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "7": {
            "inputs": {
                "text": "ugly, blurry, low quality, distorted",
                "clip": ["4", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "8": {
            "inputs": {
                "samples": ["3", 0],
                "vae": ["4", 2]
            },
            "class_type": "VAEDecode"
        },
        "9": {
            "inputs": {
                "filename_prefix": "bill_murray",
                "images": ["8", 0]
            },
            "class_type": "SaveImage"
        }
    }
    
    # Queue the prompt
    url = "http://127.0.0.1:8188/prompt"
    data = {
        "prompt": workflow,
        "client_id": "test_client"
    }
    
    print("Sending generation request...")
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        prompt_id = result.get('prompt_id')
        print(f"Generation queued with ID: {prompt_id}")
        return prompt_id
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def check_progress(prompt_id):
    # Check if generation is complete
    url = f"http://127.0.0.1:8188/history/{prompt_id}"
    response = requests.get(url)
    
    if response.status_code == 200:
        history = response.json()
        if prompt_id in history:
            return history[prompt_id]
    return None

if __name__ == "__main__":
    prompt_id = generate_image()
    if prompt_id:
        print("Waiting for generation to complete...")
        for i in range(30):  # Wait up to 30 seconds
            time.sleep(1)
            result = check_progress(prompt_id)
            if result:
                print("Generation complete!")
                print("Check ComfyUI/output folder for the image")
                break
            print(f"Checking... {i+1}/30")
        else:
            print("Timeout - check ComfyUI interface")