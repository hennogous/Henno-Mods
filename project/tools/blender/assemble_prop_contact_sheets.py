"""Build labelled overview/category PNGs from render_prop_contact_previews.py.

Requires Pillow. --library points to the source blends/catalogue; --output is
the same approved output directory used for rendering. Discovers added blends.
"""
import argparse
from collections import OrderedDict, Counter
from datetime import date
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

BG = '#eeede6'
CARD = '#faf9f3'
INK = '#263c35'
MUTED = '#64716a'
LINE = '#d7dbd1'
ACCENTS = ['#466c52', '#9a7547', '#6c807d', '#a57765', '#627998', '#79756c', '#675481']
CATEGORIES = ['Work surfaces & stands', 'Barrels', 'Crates & boxes', 'Pots', 'Textiles', 'Other props', 'CSC props']


def font(size, bold=False):
    names = [f'/System/Library/Fonts/Supplemental/Arial{" Bold" if bold else ""}.ttf',
             'C:/Windows/Fonts/arialbd.ttf' if bold else 'C:/Windows/Fonts/arial.ttf',
             '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf']
    for name in names:
        if Path(name).is_file():
            return ImageFont.truetype(name, size)
    raise FileNotFoundError('Install Arial or DejaVu Sans, or update the font paths')


def category(asset_id, source_pack=None):
    name = asset_id.lower()
    if any(s in name for s in ['table', 'workbench', 'bench', 'stand']):
        return CATEGORIES[0]
    if 'barrel' in name or 'vat' in name:
        return CATEGORIES[1]
    if any(s in name for s in ['crate', 'box']):
        return CATEGORIES[2]
    if 'pot' in name:
        return CATEGORIES[3]
    if any(s in name for s in ['rug', 'loom', 'cloth', 'sail', 'bale']):
        return CATEGORIES[4]
    return CATEGORIES[5]


def place_preview(canvas, path, box):
    image = Image.open(path).convert('RGBA')
    bounds = image.getbbox()
    if not bounds:
        raise ValueError(f'Empty preview: {path}')
    # Crop only empty transparent margin; preserve the rendered asset shape.
    image = image.crop(bounds)
    x, y, w, h = box
    image.thumbnail((round(w), round(h)), Image.Resampling.LANCZOS)
    canvas.paste(image, (round(x + (w - image.width) / 2), round(y + (h - image.height) / 2)), image)


def wrapped_id(draw, name, width, size):
    f = font(size, True)
    if draw.textlength(name, font=f) <= width:
        return [name], f
    candidates = [i + 1 for i, c in enumerate(name) if c == '_']
    for split in sorted(candidates, key=lambda i: abs(i - len(name) / 2)):
        parts = [name[:split], name[split:]]
        if max(draw.textlength(part, font=f) for part in parts) <= width:
            return parts, f
    return wrapped_id(draw, name, width, size - 1)


def card(canvas, row, output, box, accent, detail=False):
    x, y, w, h = box
    draw = ImageDraw.Draw(canvas)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=12, fill=CARD, outline=LINE, width=2)
    draw.rounded_rectangle((x + 18, y + 16, x + 68, y + 43), radius=6, fill=accent)
    draw.text((x + 43, y + 29), f'{row["number"]:02}', font=font(17, True), fill='white', anchor='mm')
    pack = row.get('source_pack', 'Uncatalogued')
    draw.text((x + w - 18, y + 29), pack, font=font(18), fill=MUTED, anchor='rm')
    image_height = h - (150 if detail else 141)
    if detail:
        place_preview(canvas, output / row['views'][0]['image'], (x + 25, y + 61, w * .65 - 35, image_height - 35))
        place_preview(canvas, output / row['views'][1]['image'], (x + w * .65, y + 99, w * .35 - 24, image_height - 82))
        draw.text((x + w * .82, y + image_height + 33), 'SECOND VIEW', font=font(13, True), fill=MUTED, anchor='mm')
    else:
        place_preview(canvas, output / row['views'][0]['image'], (x + 30, y + 57, w - 60, image_height - 12))
    lines, f = wrapped_id(draw, row['asset_id'], w - 36, 22 if detail else 20)
    if row.get('review_note'):
        draw.text((x + 18, y + h - 103), 'MATERIAL PREVIEW NEEDS REVIEW', font=font(14, True), fill='#a25e33')
    name_y = y + h - 80
    for i, line in enumerate(lines):
        draw.text((x + 18, name_y + i * 24), line, font=f, fill=INK)
    dims = row['dimensions']
    dimensions = ' × '.join(f'{v:.1f}' for v in dims)
    draw.text((x + 18, y + h - 19), dimensions + '  |  X × Y × Z', font=font(17), fill=MUTED, anchor='ls')


def header(canvas, title, subtitle, total):
    d = ImageDraw.Draw(canvas)
    d.text((48, 35), 'CIV SUPPLY CHAINS  /  REUSABLE ASSET LIBRARY', font=font(21, True), fill=MUTED)
    d.text((45, 72), title, font=font(58, True), fill=INK)
    d.text((48, 149), subtitle, font=font(22), fill=MUTED)
    d.text((canvas.width - 48, 44), f'{total:02} ASSETS  ·  {date.today().isoformat()}', font=font(20, True), fill=INK, anchor='ra')


def footer(canvas):
    d = ImageDraw.Draw(canvas)
    y = canvas.height - 57
    d.line((48, y - 14, canvas.width - 48, y - 14), fill=LINE, width=2)
    d.text((48, y), 'Worked state • Blender previews • Views fitted individually, not to a common scale', font=font(20), fill=MUTED)
    d.text((48, y + 26), 'Dimensions: source/Blender units, visible geometry including source decals. Firaxis shader effects are approximated.', font=font(18), fill=MUTED)


def build(library, output):
    catalogue = json.loads((library / 'catalogue.json').read_text())
    by_id = {a['asset_id']: a for a in catalogue['assets']}
    review_path = output / 'review-notes.json'
    reviews = json.loads(review_path.read_text()) if review_path.is_file() else {}
    groups = OrderedDict((name, []) for name in CATEGORIES)
    for blend in sorted(library.glob('*.blend')):
        # Only CSC_ALL identities are candidates for the shared prop library.
        if blend.stem.startswith('CSC_') and not blend.stem.startswith('CSC_ALL_'):
            continue
        path = output / 'previews' / (blend.stem + '.json')
        if not path.is_file():
            raise FileNotFoundError(f'Run preview renderer for {blend.name} first')
        preview = json.loads(path.read_text())
        row = {key: by_id.get(blend.stem, {}).get(key) for key in ['source_pack', 'state_behavior', 'registration_status']}
        row.update(preview)
        row['source_pack'] = row['source_pack'] or 'Uncatalogued'
        row['blend_path'] = str(blend)
        row['review_note'] = reviews.get(blend.stem)
        row['category'] = category(blend.stem, row['source_pack'])
        groups[row['category']].append(row)
    groups = OrderedDict((key, rows) for key, rows in groups.items() if rows)
    rows = [row for items in groups.values() for row in items]
    for n, row in enumerate(rows, 1):
        row['number'] = n
    sheets = output / 'contact-sheets'
    sheets.mkdir(parents=True, exist_ok=True)
    width, cw, ch, gap, margin = 2500, 464, 377, 20, 50
    height = 211 + sum(61 + math.ceil(len(items) / 5) * (ch + gap) + 17 for items in groups.values()) + 91
    overview = Image.new('RGB', (width, height), BG)
    packs = Counter(row['source_pack'] for row in rows)
    subtitle = '  ·  '.join(f'{value} {key}' for key, value in packs.items()) + '  |  Exact source IDs and native dimensions'
    header(overview, 'The prop pantry', subtitle, len(rows))
    y = 211
    for name, items in groups.items():
        accent = ACCENTS[CATEGORIES.index(name)]
        d = ImageDraw.Draw(overview)
        d.text((margin, y + 5), name, font=font(29, True), fill=accent)
        d.text((width - margin, y + 7), f'{len(items)} assets', font=font(23), fill=MUTED, anchor='ra')
        y += 61
        for i, row in enumerate(items):
            card(overview, row, output, (margin + (i % 5) * (cw + gap), y + (i // 5) * (ch + gap), cw, ch), accent)
        y += math.ceil(len(items) / 5) * (ch + gap) + 17
    footer(overview)
    overview.save(sheets / 'CSC_Prop_Library_Overview.png')
    outputs = ['CSC_Prop_Library_Overview.png']
    detail_groups = list(groups.items())
    csc_assets = [row for row in rows if row['asset_id'].startswith('CSC_ALL_')]
    if csc_assets:
        detail_groups.append(('CSC props', csc_assets))
    for name, items in detail_groups:
        cw, ch, gap, width = 752, 516, 24, 2400
        height = 224 + math.ceil(len(items) / 3) * (ch + gap) + 91
        page = Image.new('RGB', (width, height), BG)
        header(page, name, 'Two views per asset  ·  Exact source IDs  ·  Native X × Y × Z dimensions', len(items))
        for i, row in enumerate(items):
            card(page, row, output, (48 + (i % 3) * (cw + gap), 222 + (i // 3) * (ch + gap), cw, ch), ACCENTS[CATEGORIES.index(name)], detail=True)
        footer(page)
        filename = f'{CATEGORIES.index(name) + 1:02}_' + name.replace(' & ', '_and_').replace(' ', '_') + '.png'
        page.save(sheets / filename)
        outputs.append(filename)
    manifest = {'library': str(library), 'asset_count': len(rows), 'sheets': outputs, 'assets': rows}
    (output / 'contact-sheet-index.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('CONTACT SHEETS COMPLETE', len(rows), 'assets,', len(outputs), 'sheets')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--library', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    build(args.library.resolve(), args.output.resolve())
