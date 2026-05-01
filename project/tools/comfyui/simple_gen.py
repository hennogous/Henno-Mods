import requests
import json
import time

def generate_simple():
    workflow = {
        "1": {
            "inputs": {"ckpt_name": "sd_v1-5-pruned.safetensors"},
            "class_type": "CheckpointLoaderSimple"
        },
        "2": {
            "inputs": {
                "text": "Tokyo cityscape at night, neon lights, urban photography",
                "clip": ["1", 1]
            },
            "class_type": "CLIPTextEncode"
        },
        "3": {
            "inputs": {"text": "ugly, blurry", "clip": ["1", 1]},
            "class_type": "CLIPTextEncode"
        },
        "4": {
            "inputs": {"width": 512, "height": 512, "batch_size": 1},
            "class_type": "EmptyLatentImage"
        },
        "5": {
            "inputs": {
                "seed": 42, "steps": 15, "cfg": 7, 
                "sampler_name": "euler", "scheduler": "normal", "denoise": 1,
                "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]
            },
            "class_type": "KSampler"
        },
        "6": {
            "inputs": {"samples": ["5", 0], "vae": ["1", 2]},
            "class_type": "VAEDecode"
        },
        "7": {
            "inputs": {"filename_prefix": "test", "images": ["6", 0]},
            "class_type": "SaveImage"
        }
    }
    
    print("Sending generation request...")
    response = requests.post("http://127.0.0.1:8188/prompt", 
                           json={"prompt": workflow})
    
    if response.status_code == 200:
        result = response.json()
        print(f"Queued: {result.get('prompt_id')}")
        return True
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return False

if __name__ == "__main__":
    if generate_simple():
        print("Check ComfyUI output folder in 30 seconds...")
    else:
        print("Failed")