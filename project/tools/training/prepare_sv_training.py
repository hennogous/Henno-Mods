"""
Extract and prepare Civ 6 Strategic View sprites for LoRA training.
Converts DDS to PNG and generates caption files.
"""
import os
from PIL import Image
from pathlib import Path

PANTRY_TEXTURES = r"C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\pantry\Textures"
OUTPUT_DIR = r"C:\Users\Shadow\ComfyUI\training_data\civ6_strategic_view"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Caption templates by category
CAPTIONS = {
    # Districts
    "StrategicView_Districts_Commercial Hub": "commercial hub district, civ 6 strategic view sprite, simplified building illustration, muted earth tones, hand-painted style, top-down view",
    "StrategicView_Districts_Culture": "theater square culture district, civ 6 strategic view sprite, simplified building illustration, muted earth tones, hand-painted style, top-down view",
    "StrategicView_Districts_Generic_District": "generic district, civ 6 strategic view sprite, simplified building illustration, muted earth tones, hand-painted style, top-down view",
    "StrategicView_Districts_Gold": "commercial gold district, civ 6 strategic view sprite, simplified building illustration, warm golden tones, hand-painted style, top-down view",
    "StrategicView_Districts_Production": "industrial production district, civ 6 strategic view sprite, simplified building illustration, muted earth tones, hand-painted style, top-down view",
    "StrategicView_Districts_Science": "campus science district, civ 6 strategic view sprite, simplified building illustration, cool blue tones, hand-painted style, top-down view",
    
    # Improvements
    "StrategicView_Improvements_Farm": "farm improvement, civ 6 strategic view sprite, simplified agricultural illustration, green and brown tones, hand-painted style, top-down view",
    "StrategicView_Improvements_Harbor": "harbor improvement, civ 6 strategic view sprite, simplified port illustration, blue and brown tones, hand-painted style, top-down view",
    "StrategicView_Improvements_Mine": "mine improvement, civ 6 strategic view sprite, simplified mining illustration, grey and brown tones, hand-painted style, top-down view",
    "StrategicView_Improvements_Quarry": "quarry improvement, civ 6 strategic view sprite, simplified stone quarry illustration, grey tones, hand-painted style, top-down view",
    
    # Wonders
    "StrategicView_Wonders_Generic_Wonder": "wonder building, civ 6 strategic view sprite, simplified monument illustration, golden tones, hand-painted style, top-down view",
    "StrategicView_Wonders_Natural_Wonder": "natural wonder, civ 6 strategic view sprite, simplified natural landmark illustration, vibrant colors, hand-painted style, top-down view",
    
    # Terrain sprites (hills, mountains)
    "SV_Sprites_HillsDesert_Color": "desert hills terrain, civ 6 strategic view sprite, simplified terrain illustration, sandy brown tones, hand-painted style",
    "SV_Sprites_HillsGrasslands_Color": "grassland hills terrain, civ 6 strategic view sprite, simplified terrain illustration, green tones, hand-painted style",
    "SV_Sprites_HillsPlains_Color": "plains hills terrain, civ 6 strategic view sprite, simplified terrain illustration, golden brown tones, hand-painted style",
    "SV_Sprites_HillsSnow_Color": "snow hills terrain, civ 6 strategic view sprite, simplified terrain illustration, white and blue tones, hand-painted style",
    "SV_Sprites_HillsTundra_Color": "tundra hills terrain, civ 6 strategic view sprite, simplified terrain illustration, grey-green tones, hand-painted style",
    
    # Terrain mountains
    "SV_TerrainMountain": "mountain terrain, civ 6 strategic view sprite, simplified mountain illustration, grey and brown tones, hand-painted style",
    "SV_TerrainMountains": "mountain range terrain, civ 6 strategic view sprite, simplified mountain illustration, grey and brown tones, hand-painted style",
    
    # Features
    "SV_Features_Icecaps": "ice cap feature, civ 6 strategic view sprite, simplified ice illustration, white and blue tones, hand-painted style",
    "SV_TerrainFeature_Reef": "reef feature, civ 6 strategic view sprite, simplified coral reef illustration, blue and coral tones, hand-painted style",
    
    # Effects
    "SV_Effects_NuclearFallout": "nuclear fallout effect, civ 6 strategic view sprite, simplified toxic illustration, green-yellow tones, hand-painted style",
}

# Default caption for anything not explicitly mapped
DEFAULT_CAPTION = "civ 6 strategic view sprite, simplified illustration, muted earth tones, hand-painted style, top-down view, strategy game art"

converted = 0
skipped = 0

# Process all relevant DDS files
for dds_file in Path(PANTRY_TEXTURES).glob("*.dds"):
    name = dds_file.stem
    
    # Skip non-strategic-view files
    if not (name.startswith("StrategicView_") or name.startswith("SV_")):
        continue
    
    # Skip UI-only elements (move counters, hex borders, etc)
    skip_prefixes = ["StrategicView_Move", "StrategicView_Hex", "StrategicView_Route",
                     "StrategicView_Ranged", "StrategicView_Adjacency", 
                     "StrategicView_DarkHex", "StrategicView_YieldAtlas",
                     "StrategicView_CultureBorder", "StrategicView_Riverbank",
                     "StrategicView_Sprite_Error"]
    if any(name.startswith(p) for p in skip_prefixes):
        skipped += 1
        continue
    
    # Skip FOW (fog of war) variants - we want the visible/color versions
    if "_FOW" in name and "_FOW_" not in name:
        skipped += 1
        continue
    if name.endswith("_FOW"):
        skipped += 1
        continue
    
    # Skip Revealed variants (want Visible)
    if "_Revealed" in name:
        skipped += 1
        continue
    
    # Convert DDS to PNG
    try:
        img = Image.open(str(dds_file))
        png_path = os.path.join(OUTPUT_DIR, f"{name}.png")
        img.save(png_path)
        
        # Generate caption
        caption = DEFAULT_CAPTION
        for prefix, cap in CAPTIONS.items():
            if name.startswith(prefix):
                caption = cap
                break
        
        # Write caption file (kohya-ss format: same name, .txt extension)
        caption_path = os.path.join(OUTPUT_DIR, f"{name}.txt")
        with open(caption_path, "w") as f:
            f.write(caption)
        
        converted += 1
        print(f"OK: {name} ({img.size[0]}x{img.size[1]})")
        
    except Exception as e:
        print(f"FAIL: {name} - {e}")
        skipped += 1

print(f"\nDone! Converted: {converted}, Skipped: {skipped}")
print(f"Output: {OUTPUT_DIR}")
