# Civ 6 Strategic View LoRA Training Script
# Run this in a terminal on Shadow (not via OpenClaw - long-running process)
#
# Prerequisites:
#   pip install kohya-ss
#   OR: git clone https://github.com/kohya-ss/sd-scripts && cd sd-scripts && pip install -r requirements.txt
#
# Training data: C:\Users\Shadow\ComfyUI\training_data\civ6_sv_lora\ (463 captioned PNGs)
#   - All Districts_*.dds variants (visible, revealed, under construction, pillaged)
#   - Buildings with district prefix only (Buildings_DistrictName_BuildingName_*)
#   - Extracted from pantry: ...SDK Assets\Civ6\
# Base model: C:\Users\Shadow\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors
# Output: C:\Users\Shadow\ComfyUI\models\loras\civ6_strategic_view.safetensors
#
# ControlNet (for inference): diffusers_xl_canny_mid.safetensors -> models\controlnet\
#   Workflow: Blender render -> canny edges -> ControlNet + this LoRA -> SV sprite
#
# Expected time: ~1-2 hours on RTX 2000 Ada (15GB VRAM)

$baseModel = "C:\Users\Shadow\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors"
$trainData = "C:\Users\Shadow\ComfyUI\training_data\civ6_sv_lora"
$outputDir = "C:\Users\Shadow\ComfyUI\models\loras"
$outputName = "civ6_strategic_view"

accelerate launch --num_cpu_threads_per_process=2 sdxl_train_network.py `
  --pretrained_model_name_or_path="$baseModel" `
  --train_data_dir="$trainData" `
  --output_dir="$outputDir" `
  --output_name="$outputName" `
  --resolution=256 `
  --train_batch_size=1 `
  --max_train_steps=1500 `
  --learning_rate=1e-4 `
  --network_module=networks.lora `
  --network_dim=32 `
  --network_alpha=16 `
  --optimizer_type="AdamW8bit" `
  --mixed_precision="fp16" `
  --save_precision="fp16" `
  --cache_latents `
  --cache_latents_to_disk `
  --gradient_checkpointing `
  --save_every_n_steps=500 `
  --caption_extension=".txt" `
  --seed=42 `
  --xformers

Write-Host "Training complete! LoRA saved to: $outputDir\$outputName.safetensors"
Write-Host "Test it in ComfyUI with trigger: 'civ 6 strategic view sprite'"
