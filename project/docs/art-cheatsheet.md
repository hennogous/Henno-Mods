## 3D Art

### Generate N, M, G PBR textures

cd "/Users/henno.gous/Library/CloudStorage/OneDrive-InterIKEAGroup/Documents/GitHub/Play/Henno Mods"
or
cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods"

node project/tools/blender/csc_generate_pbr_maps.mjs \
  --base "/Users/henno.gous/Library/CloudStorage/GoogleDrive-henno.gous@gmail.com/Other computers/My PC/Working Files/3D Art/Textures/CSC_Atlas_Props_B.png" \
  --asset-name CSC_Atlas_Props \
  --out-dir "/Users/henno.gous/Library/CloudStorage/GoogleDrive-henno.gous@gmail.com/Other computers/My PC/Working Files/3D Art/Textures" \
  --size 1024 \
  --preset auto \
  --overwrite \
  --backup


## 2D Art

### Building icon

-- start comfyui

cd C:\Users\Shadow\ComfyUI
py -3.12 main.py --listen 127.0.0.1 --port 8188


cd "C:\Users\Shadow\Documents\'Firaxis ModBuddy'\'Civilization VI'\Henno Mods\project\tools\comfyui\icon_pipeline"

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