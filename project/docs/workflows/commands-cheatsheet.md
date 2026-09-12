> **Documentation audit — 2026-09-12: Needs refresh.** Mixes an obsolete Mac OneDrive checkout with Windows commands and has an unterminated final path quote. SV command locations are outdated. Examples need a platform-specific rewrite before copy/paste use.
> Classification: Tool commands. See the [full audit](../DOCUMENT-AUDIT.md).

## 3D Art

### Generate N, M, G PBR textures

cd "/Users/henno.gous/Library/CloudStorage/OneDrive-InterIKEAGroup/Documents/GitHub/Play/Henno Mods"

node project/tools/blender/csc_generate_pbr_maps.mjs \
  --base "C:\Users\Shadow\Desktop\Working Files\3D Art\Textures\CSC_Atlas_Props_2_B.png" \
  --asset-name CSC_Atlas_Props_2 \
  --out-dir "C:\Users\Shadow\Desktop\Working Files\3D Art\Textures" \
  --size 1024 \
  --preset auto \
  --overwrite \
  --backup

or

cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods"

node project/tools/blender/csc_generate_pbr_maps.mjs `
  --base "C:\Users\Shadow\Desktop\Working Files\3D Art\Textures\CSC_Atlas_Props_2_B.png" `
  --asset-name CSC_Atlas_Props_2 `
  --out-dir "C:\Users\Shadow\Desktop\Working Files\3D Art\Textures" `
  --size 1024 `
  --preset auto `
  --overwrite


## 2D Art

### Building icon

-- start comfyui

cd C:\Users\Shadow\ComfyUI
py -3.12 main.py --listen 127.0.0.1 --port 8188


cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\project\tools\comfyui\icon_pipeline"

py icon_img2img.py "C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\Tailors\CSC_TAILORS_Textile_Workshop_Input.png"

### Building SV sprites

cd C:\Users\Shadow\ComfyUI
py -3.12 main.py --listen 127.0.0.1 --port 8188

cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\project\tools\comfyui\sv_pipeline"

py sv_img2img.py "C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\Bakers\StrategicView\CSC_BAKERS_SV_Water_Mill_Test_Input.png"  

-- manual edit shadows

py sv_postprocess.py "C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\Bakers\StrategicView\CSC_BAKERS_SV_Water_Mill_Test_Visible_PreShadow.png" 

### Quarter SV sprites

py sv_postprocess.py "C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\Bakers\StrategicView\CSC_BAKERS_SV_Quarter_Visible_PreShadow.png" --quarter


### Localization regeneration

cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\
py -3 project/tools/localization/loc_md_to_sql.py project/localization
py -3 project/tools/localization/loc_md_to_sql.py --check project/localization