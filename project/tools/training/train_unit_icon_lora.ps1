# Civ 6 Unit Icon Style LoRA Training Script
#
# Dataset prepared from:
#   C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\pantry\Textures\Units256.dds
#
# Metadata/captions are generated from the game's IconDefinitions rows in:
#   ...\Base\Assets\UI\Icons\Icons_Units.xml
#
# Training data:
#   C:\Users\Shadow\ComfyUI\training_data\civ6_unit_icons_lora\1_civ6unit
#
# Output:
#   C:\Users\Shadow\ComfyUI\models\loras\civ6_unit_icons.safetensors
#
# Trigger:
#   civ 6 unit icon
#
# IMPORTANT Windows lessons from previous CSC LoRAs:
#   - Use PYTHONUTF8=1
#   - Use mixed_precision=no
#   - Use AdamW, not AdamW8bit
#   - Delete stale .npz latent caches if precision/settings change

$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"

$baseModel = "C:\Users\Shadow\ComfyUI\models\checkpoints\sd_xl_base_1.0.safetensors"
$trainData = "C:\Users\Shadow\ComfyUI\training_data\civ6_unit_icons_lora"
$outputDir = "C:\Users\Shadow\ComfyUI\models\loras"
$outputName = "civ6_unit_icons"
$sdScripts = "C:\Users\Shadow\sd-scripts"

if (!(Test-Path $baseModel)) { throw "Base model not found: $baseModel" }
if (!(Test-Path $trainData)) { throw "Training data not found: $trainData" }
if (!(Test-Path $sdScripts)) { throw "sd-scripts not found: $sdScripts" }

Set-Location $sdScripts
. .\venv\Scripts\Activate.ps1

accelerate launch --num_cpu_threads_per_process=2 --mixed_precision=no sdxl_train_network.py `
  --pretrained_model_name_or_path="$baseModel" `
  --train_data_dir="$trainData" `
  --output_dir="$outputDir" `
  --output_name="$outputName" `
  --resolution=256 `
  --train_batch_size=1 `
  --max_train_steps=1000 `
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
Write-Host "Trigger: 'civ 6 unit icon'"
