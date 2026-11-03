"""Package the tower-position correction and side-by-side source-model renders."""
import json,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
out=Path.home()/'Desktop/Codex/modern-windmill-v5-20261026'
dest=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/modern/revision-05-tower-position'
asset='CSC_BAKERS_Wind_Mill_Modern'
validation=json.loads((out/'source-validation.json').read_text());report=json.loads((out/'assembly-review-report.json').read_text())
assert validation['automated_pass'] and validation['error_count']==0 and report['center_error']<.001
report['camera']='L1 icon camera angle; identical 0.8x lens and shift for shared wider framing to retain the historical sails; matching lighting'
(out/'assembly-review-report.json').write_text(json.dumps(report,indent=2))
dest.mkdir(parents=True,exist_ok=True)
for name in (asset+'.blend','source-validation.json','assembly-review-report.json'):
    target=dest/name
    if target.exists():assert target.read_bytes()==(out/name).read_bytes(),'Existing revision differs'
    shutil.copy2(out/name,target)
shutil.copytree(out/'textures',dest/'textures',dirs_exist_ok=True)
(dest/'REVIEW.txt').write_text('Modern Wind Mill revision 05 — exact historical tower position\n\nSilo axis measured from the original mill tower and matched within 0.001 unit. Elevator and stock adjusted around the corrected position. Original shelter silhouette retained, with the enclosed support removed at the tower junction.\n\nComparison uses the L1 icon camera angle with identical lighting, and the same 20 percent lens reduction in both frames to retain the historical sail tips. This is a model comparison, not a finalized saved-AST art input or a runtime installation.\n',encoding='utf-8')
sheet=Image.new('RGB',(2048,1096),'#f4f5f7')
for x,name in [(0,'historical_icon_angle.png'),(1024,'modern_v5_icon_angle.png')]:sheet.paste(Image.open(out/name).convert('RGB'),(x,72))
d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',30)
d.text((40,17),'Historical wind mill',font=font,fill='#28302d');d.text((1064,17),'Modern — silo on the original tower position',font=font,fill='#28302d')
sheet.save(out/'historical_modern_2d_angle.png')
(out/'review-package.json').write_text(json.dumps({'master':str(dest/(asset+'.blend')),'comparison':str(out/'historical_modern_2d_angle.png'),'runtime_updated':False},indent=2))
print(dest)
