# extract_unit_icon_training_data.py
#
# Slice the base-game Units256.dds atlas from the Civ VI SDK pantry into
# individual 256px unit-icon PNGs with kohya/sd-scripts caption files.
#
# Metadata is read from the game's IconDefinitions XML rows rather than guessed
# from atlas position. A manifest CSV is written alongside the images so the
# atlas/index/icon-name provenance is auditable.
#
# Default output:
#   C:/Users/Shadow/ComfyUI/training_data/civ6_unit_icons_lora/1_civ6unit/

from __future__ import annotations

import argparse
import csv
import re
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
import numpy as np

GAME_ROOT = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI")
SDK_ROOT = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK Assets/Civ6")
DEFAULT_ATLAS = SDK_ROOT / "pantry" / "Textures" / "Units256.dds"
DEFAULT_OUTPUT_DIR = Path("C:/Users/Shadow/ComfyUI/training_data/civ6_unit_icons_lora/1_civ6unit")
ICON_SIZE = 256
MIN_ALPHA = 10
TRIGGER = "civ 6 unit icon"
STYLE = "cartoon unit portrait, bold outline, hand-painted, cel-shaded, game icon"

# Keep the captions useful but do not overfit too much to Civ internal naming.
DROP_TOKENS = {
    "unit",
}

UNIT_PHRASE_HINTS = {
    "great general": "great person military general",
    "great admiral": "great person naval admiral",
    "great engineer": "great person engineer",
    "great merchant": "great person merchant",
    "great prophet": "great person prophet",
    "great scientist": "great person scientist",
    "great writer": "great person writer",
    "great artist": "great person artist",
    "great musician": "great person musician",
    "warrior monk": "religious warrior monk",
    "modern at": "modern anti tank crew",
    "at crew": "anti tank crew",
    "mobile sam": "mobile anti-air missile unit",
    "rocket artillery": "rocket artillery",
    "jet fighter": "jet fighter aircraft",
    "jet bomber": "jet bomber aircraft",
    "nuclear submarine": "nuclear submarine",
    "mechanized infantry": "mechanized infantry",
    "machine gun": "machine gun crew",
    "aircraft carrier": "aircraft carrier",
}

UNIT_ROLE_HINTS = {
    "settler": "civilian settler",
    "builder": "civilian builder",
    "trader": "civilian trader",
    "missionary": "religious missionary",
    "apostle": "religious apostle",
    "inquisitor": "religious inquisitor",
    "archaeologist": "civilian archaeologist",
    "spy": "civilian spy",
    "naturalist": "civilian naturalist",
    "warrior": "ancient melee warrior",
    "slinger": "ancient ranged slinger",
    "scout": "recon scout",
    "archer": "ranged archer",
    "spearman": "anti cavalry spearman",
    "swordsman": "melee swordsman",
    "horseman": "light cavalry horseman",
    "chariot": "ancient chariot unit",
    "catapult": "siege catapult",
    "tower": "siege support tower",
    "galley": "naval galley",
    "longship": "naval longship",
    "quadrireme": "naval quadrireme",
    "knight": "heavy cavalry knight",
    "crossbowman": "ranged crossbowman",
    "pikeman": "anti cavalry pikeman",
    "musketman": "gunpowder musketman",
    "bombard": "siege bombard",
    "frigate": "naval frigate",
    "privateer": "naval privateer",
    "cannon": "field cannon",
    "cavalry": "industrial cavalry",
    "medic": "support medic",
    "ironclad": "naval ironclad",
    "ranger": "recon ranger",
    "balloon": "observation balloon",
    "biplane": "early aircraft biplane",
    "infantry": "modern infantry",
    "artillery": "siege artillery",
    "battleship": "naval battleship",
    "submarine": "naval submarine",
    "crew": "anti tank crew",
    "tank": "armored tank",
    "fighter": "fighter aircraft",
    "bomber": "bomber aircraft",
    "machine": "machine gun crew",
    "carrier": "aircraft carrier",
    "destroyer": "naval destroyer",
    "helicopter": "helicopter gunship",
    "armor": "modern armor",
    "guru": "religious guru",
    "trebuchet": "siege trebuchet",
    "arms": "medieval man at arms",
}

@dataclass(frozen=True)
class IconMeta:
    icon_name: str
    atlas: str
    index: int
    source_xml: str


def safe_stem(text: str) -> str:
    text = text.lower().replace("icon_", "")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_")


def humanize_icon_name(icon_name: str) -> str:
    parts = icon_name.replace("ICON_", "").lower().split("_")
    parts = [p for p in parts if p not in DROP_TOKENS]
    # Preserve civ/adjective tokens in the visible subject name; they help for
    # unique units such as roman legion, aztec eagle warrior, etc.
    return " ".join(parts)


def role_hint(subject: str) -> str:
    for phrase, hint in UNIT_PHRASE_HINTS.items():
        if phrase in subject:
            return hint
    words = set(subject.split())
    for token, hint in UNIT_ROLE_HINTS.items():
        if token in words:
            return hint
    return "civilization unit"


def make_caption(icon_name: str) -> str:
    subject = humanize_icon_name(icon_name)
    hint = role_hint(subject)
    return f"{TRIGGER}, {subject}, {hint}, {STYLE}"


def build_unit_icon_index(game_root: Path) -> dict[int, IconMeta]:
    """Return index -> icon metadata for the base ICON_ATLAS_UNITS atlas."""
    result: dict[int, IconMeta] = {}
    xml_paths = sorted(game_root.rglob("*Icons_Units*.xml"))

    for xml_path in xml_paths:
        try:
            root = ET.parse(xml_path).getroot()
        except ET.ParseError as exc:
            print(f"WARN: could not parse {xml_path}: {exc}")
            continue

        for row in root.iter("Row"):
            atlas = row.get("Atlas", "")
            name = row.get("Name", "")
            idx = row.get("Index", "")
            if not (atlas == "ICON_ATLAS_UNITS" and name.startswith("ICON_UNIT_") and idx):
                continue
            if name.endswith("_FOW"):
                continue
            try:
                index = int(idx)
            except ValueError:
                continue

            meta = IconMeta(name, atlas, index, str(xml_path))
            # Prefer the first mapping encountered. Base XML appears before DLC
            # when sorted by path and is the correct source for Units256.dds.
            result.setdefault(index, meta)

    return result


def slice_units_atlas(atlas_path: Path, output_dir: Path, clean: bool = False) -> tuple[int, int, int, int]:
    if not atlas_path.exists():
        raise FileNotFoundError(f"Units atlas not found: {atlas_path}")

    if clean and output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    icon_index = build_unit_icon_index(GAME_ROOT)
    img = Image.open(atlas_path).convert("RGBA")
    cols = img.width // ICON_SIZE
    rows = img.height // ICON_SIZE
    if img.width % ICON_SIZE or img.height % ICON_SIZE:
        raise ValueError(f"Atlas size {img.size} is not divisible by {ICON_SIZE}")

    manifest_rows: list[dict[str, str | int]] = []
    saved = skipped_empty = skipped_unknown = skipped_existing = 0

    for index in range(cols * rows):
        col = index % cols
        row = index // cols
        cell = img.crop((col * ICON_SIZE, row * ICON_SIZE, (col + 1) * ICON_SIZE, (row + 1) * ICON_SIZE))
        alpha_max = int(np.array(cell)[:, :, 3].max())
        if alpha_max < MIN_ALPHA:
            skipped_empty += 1
            continue

        meta = icon_index.get(index)
        if meta is None:
            # Empty definitions happen in Firaxis atlases where the visual cell
            # was reserved/removed. Skip these rather than poisoning captions.
            skipped_unknown += 1
            continue

        out_stem = f"Units256_{index:03d}_{safe_stem(meta.icon_name)}"
        out_png = output_dir / f"{out_stem}.png"
        out_txt = output_dir / f"{out_stem}.txt"
        caption = make_caption(meta.icon_name)

        if out_png.exists() and out_txt.exists() and out_txt.read_text(encoding="utf-8") == caption:
            skipped_existing += 1
        else:
            cell.save(out_png)
            out_txt.write_text(caption, encoding="utf-8")
            saved += 1

        manifest_rows.append({
            "filename": out_png.name,
            "caption_file": out_txt.name,
            "caption": caption,
            "icon_name": meta.icon_name,
            "atlas": meta.atlas,
            "index": index,
            "column": col,
            "row": row,
            "source_atlas": str(atlas_path),
            "source_xml": meta.source_xml,
            "alpha_max": alpha_max,
        })

    manifest_path = output_dir / "manifest.csv"
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(manifest_rows[0].keys()) if manifest_rows else ["filename"])
        writer.writeheader()
        writer.writerows(manifest_rows)

    print(f"Atlas: {atlas_path}")
    print(f"Grid: {cols} x {rows} = {cols * rows} cells")
    print(f"IconDefinitions: {len(icon_index)} named ICON_ATLAS_UNITS entries")
    print(f"Saved/updated: {saved}")
    print(f"Skipped existing unchanged: {skipped_existing}")
    print(f"Skipped empty cells: {skipped_empty}")
    print(f"Skipped non-empty cells without IconDefinition: {skipped_unknown}")
    print(f"Dataset rows: {len(manifest_rows)}")
    print(f"Output: {output_dir}")
    print(f"Manifest: {manifest_path}")

    return saved, skipped_existing, skipped_empty, skipped_unknown


def main() -> None:
    parser = argparse.ArgumentParser(description="Slice Units256.dds into captioned unit-icon LoRA training images.")
    parser.add_argument("--atlas", type=Path, default=DEFAULT_ATLAS, help="Path to Units256.dds")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="kohya repeat folder output")
    parser.add_argument("--clean", action="store_true", help="Delete output folder before regenerating")
    args = parser.parse_args()

    slice_units_atlas(args.atlas, args.output_dir, clean=args.clean)


if __name__ == "__main__":
    main()
