> **Documentation audit — 2026-09-12: Needs refresh.** Mixes an obsolete Mac OneDrive checkout with Windows commands and has an unterminated final path quote. SV command locations are outdated. Examples need a platform-specific rewrite before copy/paste use.
> Classification: Tool commands. See the [full audit](../DOCUMENT-AUDIT.md).

cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\project\tools\blender"

py .\export_assets.py `
  --blend-directory "C:\Users\Shadow\Desktop\Working Files\3D Art\TAILORS\Textile Workshop\revision-08-export-ready" `

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

py -3 "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\project\tools\blender\render_ae_asset.py" `
  "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\Civ Supply Chains\Assets\CSC_TAILORS_Textile_Workshop.ast"

mean curvature blur 20 steps
sharpen amount 1.5
brightness -20

grow selection 8px, exterior stroke 22px
interior stroke 7px

### Building SV sprites

give codex the blend and output location
stroke 8px

-- manual edit shadows

brightness +3
contrast -3

py "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\project\tools\comfyui\sv_pipeline\sv_postprocess.py" "C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\Bakers\StrategicView\CSC_BAKERS_SV_Water_Mill_Test_Visible_PreShadow.png"

### Quarter SV sprites

py sv_postprocess.py "C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\Bakers\StrategicView\CSC_BAKERS_SV_Quarter_Visible_PreShadow.png" --quarter

### Archive

& 'C:\Users\Shadow\AppData\Local\Programs\Python\Python312\python.exe' -B `
  'C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\project\tools\gimp\create_building_icon_xcf.py' `
  'C:\Users\Shadow\Desktop\Working Files\3D Art\TAILORS\Tailor\revision-09-terrain-attachments\CSC_TAILORS_Tailor.blend' 3

#### Icon
-- start comfyui

cd C:\Users\Shadow\ComfyUI
py -3.12 main.py --listen 127.0.0.1 --port 8188


cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\project\tools\comfyui\icon_pipeline"

py icon_img2img.py "C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\Tailors\CSC_TAILORS_Textile_Workshop_Input.png"

#### SV
cd C:\Users\Shadow\ComfyUI
py -3.12 main.py --listen 127.0.0.1 --port 8188

cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\project\tools\comfyui\sv_pipeline"

py sv_img2img.py "C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\Bakers\StrategicView\CSC_BAKERS_SV_Water_Mill_Test_Input.png"

### Localization regeneration

cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\
py -3 project/tools/localization/loc_md_to_sql.py project/localization
py -3 project/tools/localization/loc_md_to_sql.py --check project/localization
