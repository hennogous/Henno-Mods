# extract_icon_training_data.py
# Slices all relevant 256px icon atlases from the Civ6 pantry into individual
# 256px icons with captions for LoRA training.
#
# Each DDS file is matched to its correct atlas name via the game's Icon XML files,
# so DLC atlases get the right index->name mapping.
#
# Output: C:/Users/Shadow/ComfyUI/training_data/civ6_icons_lora/1_civ6icon/

import glob
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from PIL import Image
import numpy as np

SDK_ROOT  = "C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK Assets/Civ6"
GAME_ROOT = "C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI"
OUTPUT_DIR = "C:/Users/Shadow/ComfyUI/training_data/civ6_icons_lora/1_civ6icon"
ICON_SIZE  = 256
MIN_ALPHA  = 10

# DDS stems to extract (no FOW, no leaders/civs/UI)
TARGET_STEMS = [
    # Buildings — isometric architectural style, matches what CSC needs to generate
    "Buildings256",
    "XP1_Buildings256",
    "XP2_Buildings256",
    "XP1_DistrictBuildings256",
    "XP2_DistrictBuildings256",
    # Wonders — same isometric architectural style
    "Wonders256",
    "XP1_Wonders256",
    "XP2_Wonders256",
    # Excluded: Districts (hex badge UI icons - different style)
    # Excluded: Units (character portraits), Resources, Features, Projects (abstract symbols)
]

# Category hint per stem (for caption generation)
STEM_CATEGORY = {
    "Buildings256": "building",             "XP1_Buildings256": "building",     "XP2_Buildings256": "building",
    "XP1_DistrictBuildings256": "building", "XP2_DistrictBuildings256": "building",
    "Wonders256": "wonder",                 "XP1_Wonders256": "wonder",         "XP2_Wonders256": "wonder",
}

# ---------------------------------------------------------------------------
# Build two indexes:
#   filename_to_atlas:  stem -> atlas_name  (from IconTextureAtlas rows)
#   atlas_to_icons:     atlas_name -> {index: icon_name}  (from icon definition rows)
# ---------------------------------------------------------------------------

def build_indexes():
    filename_to_atlas = {}  # stem (no .dds) -> atlas name (non-FOW)
    atlas_to_icons    = {}  # atlas name -> {idx: icon_name}

    xml_patterns = [
        f"{GAME_ROOT}/**/*Icons_Buildings*.xml",
        f"{GAME_ROOT}/**/*Icons_Districts*.xml",
        f"{GAME_ROOT}/**/*Icons_Wonders*.xml",
        f"{GAME_ROOT}/**/*Icons_Units*.xml",
        f"{GAME_ROOT}/**/*Icons_Resources*.xml",
        f"{GAME_ROOT}/**/*Icons_Features*.xml",
        f"{GAME_ROOT}/**/*Icons_Projects*.xml",
    ]

    # First pass: collect ALL atlas name candidates per stem, and all icon maps
    stem_to_candidates = {}  # stem -> [(atlas_name, icon_count)]

    for pattern in xml_patterns:
        for xml_path in glob.glob(pattern, recursive=True):
            try:
                tree = ET.parse(xml_path)
                root = tree.getroot()
                for row in root.iter('Row'):
                    fname  = row.get('Filename', '')
                    atlas  = row.get('Name', '')

                    # IconTextureAtlas rows: Filename + Name (atlas name), no Index
                    if fname and '256' in fname and atlas and not row.get('Index'):
                        stem = fname.replace('.dds','').replace('.DDS','')
                        if 'FOW' not in atlas:
                            if stem not in stem_to_candidates:
                                stem_to_candidates[stem] = []
                            stem_to_candidates[stem].append(atlas)

                    # Icon definition rows: Atlas + Index + Name
                    atlas2 = row.get('Atlas', '')
                    idx2   = row.get('Index', '')
                    name2  = row.get('Name', '')
                    if atlas2 and idx2 and name2 and 'FOW' not in atlas2:
                        if atlas2 not in atlas_to_icons:
                            atlas_to_icons[atlas2] = {}
                        i = int(idx2)
                        if i not in atlas_to_icons[atlas2]:
                            atlas_to_icons[atlas2][i] = name2

            except Exception as e:
                pass

    # Second pass: for each stem, pick the atlas candidate with the most icon definitions
    for stem, candidates in stem_to_candidates.items():
        best = max(candidates, key=lambda a: len(atlas_to_icons.get(a, {})))
        filename_to_atlas[stem] = best

    return filename_to_atlas, atlas_to_icons


# ---------------------------------------------------------------------------
# Caption generation
# ---------------------------------------------------------------------------
def make_caption(icon_name, category):
    parts = icon_name.replace("ICON_", "").lower().split("_")
    # Drop leading category word
    if parts and parts[0] in ("building", "district", "wonder", "unit",
                               "resource", "feature", "project"):
        parts = parts[1:]
    name = " ".join(parts)
    style = "civ 6 icon, cartoon isometric, bold outline, hand-painted, cel-shaded"
    return f"{name} {category} icon, {style}"


# ---------------------------------------------------------------------------
# Atlas slicer
# ---------------------------------------------------------------------------
def slice_atlas(atlas_path, icon_map, category, output_dir):
    img  = Image.open(atlas_path).convert("RGBA")
    cols = img.width  // ICON_SIZE
    rows = img.height // ICON_SIZE

    saved = skipped_empty = skipped_existing = 0

    for i in range(cols * rows):
        col  = i % cols
        row  = i // cols
        cell = img.crop((col * ICON_SIZE, row * ICON_SIZE,
                         (col+1) * ICON_SIZE, (row+1) * ICON_SIZE))

        if np.array(cell)[:, :, 3].max() < MIN_ALPHA:
            skipped_empty += 1
            continue

        icon_name = icon_map.get(i, f"UNKNOWN_{i}")
        safe      = icon_name.lower().replace("icon_", "").replace(" ", "_")
        stem      = Path(atlas_path).stem
        out_png   = os.path.join(output_dir, f"{stem}_{safe}.png")
        out_txt   = os.path.join(output_dir, f"{stem}_{safe}.txt")

        if os.path.exists(out_png) and os.path.exists(out_txt):
            skipped_existing += 1
            continue

        cell.save(out_png)
        with open(out_txt, "w") as f:
            f.write(make_caption(icon_name, category))
        saved += 1

    return saved, skipped_empty, skipped_existing


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Building icon indexes from game XML files...")
    filename_to_atlas, atlas_to_icons = build_indexes()
    print(f"  {len(filename_to_atlas)} filename->atlas mappings")
    print(f"  {len(atlas_to_icons)} atlases with icon definitions")

    total_saved = 0
    unknown_count = 0

    for stem in TARGET_STEMS:
        # Find the DDS file
        files = glob.glob(f"{SDK_ROOT}/**/{stem}.dds", recursive=True)
        if not files:
            print(f"\n  MISSING: {stem}.dds")
            continue

        # Get atlas name for this stem
        atlas_name = filename_to_atlas.get(stem)
        if not atlas_name:
            print(f"\n  NO ATLAS MAPPING: {stem}")
            continue

        # Get icon index map
        icon_map = atlas_to_icons.get(atlas_name, {})
        category = STEM_CATEGORY.get(stem, "icon")

        print(f"\n{stem} -> {atlas_name} ({len(icon_map)} named icons, {category})")

        for f in sorted(files):
            rel = Path(f).relative_to(SDK_ROOT)
            saved, empty, existing = slice_atlas(f, icon_map, category, OUTPUT_DIR)
            print(f"  {rel}: saved={saved}, empty={empty}, existing={existing}")
            total_saved += saved

    # Check for unknowns
    unknowns = [f for f in os.listdir(OUTPUT_DIR) if f.endswith(".png") and "unknown" in f.lower()]
    print(f"\nTotal icons extracted: {total_saved}")
    print(f"Unknown icons (no name mapping): {len(unknowns)}")
    print(f"Output: {OUTPUT_DIR}")

    # Sample captions
    txts = sorted(f for f in os.listdir(OUTPUT_DIR) if f.endswith(".txt") and "unknown" not in f)[:8]
    print("\nSample captions:")
    for t in txts:
        with open(os.path.join(OUTPUT_DIR, t)) as f:
            print(f"  {t}: {f.read()}")


if __name__ == "__main__":
    main()
