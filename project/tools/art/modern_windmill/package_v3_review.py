"""Package the Civ proportion revision and unaltered same-camera review renders."""
import json, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

root = Path.home() / 'Desktop/Codex'
out = root / 'modern-windmill-v3-20261026'
previous = root / 'modern-windmill-v2-20261026'
asset = 'CSC_BAKERS_Wind_Mill_Modern'
validation = json.loads((out / 'source-validation.json').read_text())
assert validation['automated_pass'] and validation['error_count'] == 0
dest = Path.home() / 'Desktop/Working Files/3D Art/BAKERS/Wind Mill/modern/revision-03-character'
dest.mkdir(parents=True, exist_ok=True)
for name in [asset+'.blend', 'house-review-report.json', 'source-validation.json']:
    target = dest / name
    if target.exists():
        assert target.read_bytes() == (out/name).read_bytes(), 'Existing revision differs'
    shutil.copy2(out/name, target)
shutil.copytree(out/'textures', dest/'textures', dirs_exist_ok=True)
(dest/'REVIEW.txt').write_text(
    'Modern Wind Mill — revision 03: Civ proportions\n\n'
    'House-only design review: enlarged painted windows, thickened roof caps and eaves, '
    'subtle roof sweep, heavier shelter structure, wider arch and coarser brick texture. '
    'Small details remain in textures and aligned normal/AO maps.\n\n'
    '949 exported vertices, 481 triangles. Saved-source automated validation passed. '
    'Silo composition and runtime installation remain pending house review.\n', encoding='utf-8')
# Contact sheet layout only; do not repaint or modify the actual model renders.
sheet = Image.new('RGB', (2048,1100), '#f4f5f7')
sheet.paste(Image.open(previous/'modern_v2_house.png').convert('RGB'), (0,76))
sheet.paste(Image.open(out/'modern_v3_house.png').convert('RGB'), (1024,76))
draw = ImageDraw.Draw(sheet)
font = ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',32)
draw.text((48,18), 'Previous proportions', font=font, fill='#28302d')
draw.text((1072,18), 'Revised — stronger Civ proportions', font=font, fill='#28302d')
sheet.save(out/'proportion_comparison.png')
(out/'review-package.json').write_text(json.dumps({'master':str(dest/(asset+'.blend')), 'comparison':str(out/'proportion_comparison.png'), 'runtime_updated':False},indent=2))
print(dest)
