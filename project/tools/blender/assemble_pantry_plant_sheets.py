"""Assemble review-only plant contact sheets from Blender candidate previews."""
from collections import OrderedDict
from pathlib import Path
import html
import json
import math
import re
import sys

from PIL import Image, ImageDraw, ImageFont

OUT = Path(sys.argv[1]).resolve()
APPROVED = "--approved" in sys.argv
SHEET_DIR = "approved-contact-sheets" if APPROVED else "contact-sheets"
FONTS = (Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/arialbd.ttf"))


def font(size, bold=False):
    return ImageFont.truetype(str(FONTS[bool(bold)]), size)


def fitted(canvas, path, box):
    image = Image.open(OUT / path).convert("RGBA")
    bounds = image.getbbox()
    if bounds:
        image = image.crop(bounds)
    x, y, width, height = box
    image.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas.paste(image, (x + (width - image.width) // 2, y + (height - image.height) // 2), image)


selection = (json.loads((OUT / "candidate-index.json").read_text())["candidates"]
             if APPROVED else json.loads((OUT / "selection.json").read_text()))
if APPROVED:
    selection = [item for item in selection if item["number"] not in {14, 20, 45}]
catalogue = json.loads((OUT / "candidate-catalogue.json").read_text())
by_id = {row["asset_id"]: row for row in catalogue["assets"]}
rows = []
for item in selection:
    metadata_path = OUT / "previews" / (item["asset_id"] + ".json")
    if not metadata_path.is_file():
        continue
    metadata = json.loads(metadata_path.read_text())
    row = dict(item)
    row.update(metadata)
    row["number"] = item.get("number", len(rows) + 1)
    row["vertices"] = sum(component["vertices"] for component in by_id[item["asset_id"]].get("components", []))
    rows.append(row)

groups = OrderedDict()
for row in rows:
    groups.setdefault(row["category"], []).append(row)


def sheet(items, title, filename, detail):
    columns, width, height, gap = (3, 590, 395, 18) if detail else (5, 365, 305, 15)
    margin, top = 36, 170
    canvas_width = margin * 2 + columns * width + (columns - 1) * gap
    canvas_height = top + math.ceil(len(items) / columns) * (height + gap) + 84
    canvas = Image.new("RGB", (canvas_width, canvas_height), "#e9ede9")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 23), "CIV SUPPLY CHAINS  /  APPROVED PLANT LIBRARY" if APPROVED else "CIV SUPPLY CHAINS  /  PANTRY PLANT REVIEW", font=font(21, True), fill="#617564")
    draw.text((margin, 62), title, font=font(37, True), fill="#244333")
    draw.text((margin, 115), "Native Civ VI asset IDs · individually fitted previews · original source geometry and textures", font=font(20), fill="#617564")
    for index, row in enumerate(items):
        x = margin + index % columns * (width + gap)
        y = top + index // columns * (height + gap)
        draw.rounded_rectangle((x, y, x + width, y + height), radius=12, fill="#fbfcf8", outline="#c6d2c6", width=2)
        draw.text((x + 15, y + 12), f"{row['number']:02}", font=font(23, True), fill="#305a3e")
        draw.text((x + width - 13, y + 15), row["source_pack"], font=font(15), fill="#65776a", anchor="ra")
        if detail:
            fitted(canvas, row["views"][0]["image"], (x + 16, y + 50, 350, 236))
            fitted(canvas, row["views"][1]["image"], (x + 375, y + 78, 190, 174))
        else:
            fitted(canvas, row["views"][0]["image"], (x + 12, y + 45, width - 24, 182))
        label = row["asset_id"]
        label_size = 18 if detail else 15
        while draw.textlength(label, font=font(label_size, True)) > width - 26 and label_size > 11:
            label_size -= 1
        label_y = y + height - (76 if detail else 67)
        draw.text((x + 13, label_y), label, font=font(label_size, True), fill="#213c30")
        dimensions = " × ".join(f"{value:.1f}" for value in row["dimensions"])
        draw.text((x + 13, y + height - 39), f"{dimensions} units · {row['vertices']:,} verts", font=font(15 if detail else 13), fill="#65776a")
    draw.text((margin, canvas_height - 66), "47 native plants added to the CSC prop library; review numbers 14, 20 and 45 excluded." if APPROVED else "Selection preview only: no plants were added to the prop library.", font=font(19), fill="#4d6557")
    draw.text((margin, canvas_height - 38), "Blender materials approximate Firaxis shaders; native states and game placement remain untested.", font=font(16), fill="#65776a")
    target = OUT / SHEET_DIR / filename
    target.parent.mkdir(exist_ok=True)
    canvas.save(target)
    return target.relative_to(OUT).as_posix()


sheets = [dict(title="Approved plants" if APPROVED else "All options", path=sheet(rows, "Approved plants — overview" if APPROVED else "Plant options — overview", "00_Overview.png", False))]
for group_index, (group, items) in enumerate(groups.items(), 1):
    for start in range(0, len(items), 12):
        page = start // 12 + 1
        title = group + (f" — page {page}" if len(items) > 12 else "")
        filename = f"{group_index:02}_{re.sub('[^a-z0-9]+', '_', group.lower()).strip('_')}_{page}.png"
        sheets.append(dict(title=title, path=sheet(items[start:start + 12], title, filename, True)))

links = "".join(f'<a href="{html.escape(item["path"])}">{html.escape(item["title"])}</a>' for item in sheets)
cards = []
for row in rows:
    pictures = "".join(f'<a href="{html.escape(view["image"])}"><img src="{html.escape(view["image"])}" loading="lazy"></a>' for view in row["views"])
    dimensions = " × ".join(f"{value:.1f}" for value in row["dimensions"])
    cards.append(f'<article data-category="{html.escape(row["category"])}"><div class="number">{row["number"]:02} · {html.escape(row["source_pack"])}</div><div class="pictures">{pictures}</div><h3>{html.escape(row["asset_id"])}</h3><p>{dimensions} source units · {row["vertices"]:,} vertices · {html.escape(row["preview_state"])} preview</p></article>')
document = f'''<!doctype html><meta charset="utf-8"><title>CSC Pantry plant options</title><style>
*{{box-sizing:border-box}}body{{margin:0;background:#e9ede9;color:#213c30;font:16px system-ui,sans-serif}}header,main{{max-width:1560px;margin:auto;padding:28px}}h1{{font-size:42px;margin:10px 0}}p{{line-height:1.45}}nav{{display:flex;gap:12px;flex-wrap:wrap;margin-top:18px}}nav a{{background:#fbfcf8;border:1px solid #c6d2c6;padding:10px;border-radius:8px}}a{{color:#305a3e}}.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:18px}}article{{background:#fbfcf8;border:1px solid #c6d2c6;border-radius:12px;padding:18px}}.pictures{{display:flex;height:215px;align-items:center}}.pictures a{{width:50%}}.pictures img{{width:100%;max-height:210px;object-fit:contain}}h3{{font-size:17px;overflow-wrap:anywhere}}.number{{color:#65776a}}
</style><header><div>CSC / SOURCE ASSET EXPLORATION</div><h1>Pantry plant options</h1><p>{len(rows)} candidate plants for your review across five groups. Use the sheet number or exact asset ID to identify removals. These are source geometry and texture previews, not in-game renders. No library assets were added.</p><nav>{links}</nav></header><main><div class="grid">{''.join(cards)}</div></main>'''
if not APPROVED:
    (OUT / "index.html").write_text(document, encoding="utf-8")
    (OUT / "candidate-index.json").write_text(json.dumps(dict(candidates=rows, sheets=sheets, unpreviewed=[row for row in selection if row["asset_id"] not in {item["asset_id"] for item in rows}]), indent=2))
else:
    (OUT / "approved-plant-index.json").write_text(json.dumps(dict(candidates=rows, sheets=sheets), indent=2))
print("CONTACT_SHEETS_COMPLETE", len(rows), "candidates", len(sheets), "sheets")
