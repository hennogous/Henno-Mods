# Civ 6 Icon Style LoRA Training Script
# Run from inside the sd-scripts venv: .\venv\Scripts\Activate.ps1
#
# Training data: C:\Users\Shadow\ComfyUI\training_data\civ6_icons_lora\ (413 captioned PNGs)
#   - Buildings, Districts, Wonders, Units, Resources, Features, Projects
#   - All base game + XP1 + XP2 atlases
#   - Source: pantry *256.dds atlases, sliced by extract_icon_training_data.py
#
# Base model: SDXL 1.0
# Output: C:\Users\Shadow\ComfyUI\models\loras\civ6_icons.safetensors
#
# Art style: cartoon isometric, bold outline, hand-painted, cel-shaded
# Use with trigger: "civ 6 icon, cartoon isometric, bold outline"
#
# Expected time: ~2-3 hours on RTX 2000 Ada (fp32, no mixed precision)

$baseModel = "C:\Users\Shadow\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors"
$trainData = "C:\Users\Shadow\ComfyUI\training_data\civ6_icons_lora"
$outputDir = "C:\Users\Shadow\ComfyUI\models\loras"
$outputName = "civ6_icons"

$env:PYTHONUTF8 = "1"

accelerate launch --num_cpu_threads_per_process=2 --mixed_precision=no sdxl_train_network.py `
  --pretrained_model_name_or_path="$baseModel" `
  --train_data_dir="$trainData" `
  --output_dir="$outputDir" `
  --output_name="$outputName" `
  --resolution=256 `
  --train_batch_size=1 `
  --max_train_steps=2000 `
  --learning_rate=1e-4 `
  --network_module=networks.lora `
  --network_dim=32 `
  --network_alpha=16 `
  --optimizer_type="AdamW" `
  --mixed_precision="no" `
  --save_precision="fp16" `
  --cache_latents `
  --cache_latents_to_disk `
  --gradient_checkpointing `
  --save_every_n_steps=500 `
  --caption_extension=".txt" `
  --seed=42 `
  --sdpa

Write-Host "Training complete! LoRA saved to: $outputDir\$outputName.safetensors"
Write-Host "Trigger: 'civ 6 icon, cartoon isometric, bold outline, hand-painted, cel-shaded'"
