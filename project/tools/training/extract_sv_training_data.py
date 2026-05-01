# extract_sv_training_data.py
# Extracts Civ 6 strategic view building/district sprites for LoRA training.
#
# Include rules:
#   Districts_*.dds  -> all variants
#   Buildings_*.dds  -> only if format is Buildings_DistrictName_BuildingName_*
#                       (core depth == 2 after stripping state suffixes)
#                       excludes standalone Buildings_LibraryName_* (depth == 1)
#
# Output: C:/Users/Shadow/ComfyUI/training_data/civ6_sv_lora/

import glob
import os
import re
from pathlib import Path
from PIL import Image

SDK_ROOT = "C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK Assets/Civ6"
OUTPUT_DIR = "C:/Users/Shadow/ComfyUI/training_data/civ6_sv_lora"

STATE_TOKENS = {"Visible", "Revealed", "Pillaged", "UnderConstruction"}

STATE_LABELS = {
    "Visible":                      "fully visible",
    "Revealed":                     "fog of war revealed",
    "UnderConstruction_Visible":    "under construction visible",
    "UnderConstruction_Revealed":   "under construction revealed",
    "Pillaged_Visible":             "pillaged visible",
    "Pillaged_Revealed":            "pillaged revealed",
}

def strip_state(parts):
    "Strip trailing state tokens, return (core_parts, state_key)."
    i = len(parts)
    while i > 0 and parts[i-1] in STATE_TOKENS:
        i -= 1
    core = parts[1:i]   # drop leading category (Buildings/Districts)
    state_parts = parts[i:]
    state_key = "_".join(state_parts) if state_parts else "Visible"
    return core, state_key

def should_include(stem):
    "Return True if this file should be in the training set."
    parts = stem.replace(" ", "_").split("_")
    cat = parts[0].lower()

    if cat == "districts":
        return True
    elif cat == "buildings":
        core, _ = strip_state(parts)
        return len(core) == 2   # DistrictName + BuildingName
    return False

def make_caption(stem):
    parts = stem.replace(" ", "_").split("_")
    cat = parts[0].lower()
    core, state_key = strip_state(parts)

    state_label = STATE_LABELS.get(state_key, state_key.lower().replace("_", " "))

    if cat == "districts":
        # e.g. Districts_CommercialHub_Visible -> "commercial hub district"
        district_name = " ".join(core).lower()
        subject = f"{district_name} district"
        kind = "district"
    else:
        # e.g. Buildings_Campus_Library -> "campus district library building"
        district_name = core[0].lower() if core else ""
        building_name = " ".join(core[1:]).lower() if len(core) > 1 else ""
        subject = f"{building_name} building in {district_name} district"
        kind = "building"

    return (
        f"{subject}, {state_label}, "
        f"civ 6 strategic view sprite, {kind} icon, "
        f"top-down isometric, simplified illustration, muted colors, hand-painted style"
    )

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    all_dds = glob.glob(SDK_ROOT + "/**/*.dds", recursive=True)
    candidates = [
        f for f in all_dds
        if re.match(r"^(buildings|districts)_", Path(f).stem, re.IGNORECASE)
    ]

    included = [f for f in candidates if should_include(Path(f).stem)]
    excluded = len(candidates) - len(included)

    print(f"Found {len(candidates)} buildings_/districts_ DDS files")
    print(f"  Including: {len(included)}")
    print(f"  Excluding (standalone buildings): {excluded}")

    converted = skipped = errors = 0

    for dds_path in sorted(included):
        stem = Path(dds_path).stem
        out_png = os.path.join(OUTPUT_DIR, stem + ".png")
        out_txt = os.path.join(OUTPUT_DIR, stem + ".txt")

        if os.path.exists(out_png) and os.path.exists(out_txt):
            skipped += 1
            continue

        try:
            img = Image.open(dds_path)
            if img.width <= 128:
                img = img.resize((256, 256), Image.LANCZOS)
            img.save(out_png)

            caption = make_caption(stem)
            with open(out_txt, "w") as f:
                f.write(caption)

            converted += 1
            if converted % 50 == 0:
                print(f"  {converted} converted...")

        except Exception as e:
            print(f"  ERROR: {stem} -- {e}")
            errors += 1

    print(f"\nDone! Converted: {converted}, Skipped (existing): {skipped}, Errors: {errors}")
    print(f"Output: {OUTPUT_DIR}")

    # Sample captions
    txts = sorted(f for f in os.listdir(OUTPUT_DIR) if f.endswith(".txt"))
    print("\nSample captions:")
    for t in txts[:8]:
        with open(os.path.join(OUTPUT_DIR, t)) as f:
            print(f"  {t}")
            print(f"    {f.read()}")

if __name__ == "__main__":
    main()
