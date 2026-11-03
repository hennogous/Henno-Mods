"""Record the inspected native colour/AO views and assemble their comparison sheet."""
import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path.home()/'Desktop/Codex/modern-l2-states-20261029';BASE='CSC_Level_2_Modern';ID=BASE+'_CON+PIL'
validation=json.loads((O/'masters'/ID/'validation.json').read_text());assert validation['automated_pass']
assert all(x['grain_aligned'] for x in json.loads((O/'masters'/ID/'timber-UV-audit.json').read_text()))
assert 'ERRORS!!' not in (O/'cook-console.log').read_text(encoding='utf-16') if (O/'cook-console.log').read_bytes().startswith(b'\xff\xfe') else 'ERRORS!!' not in (O/'cook-console.log').read_text()
paths=[O/'review'/BASE/st/'render.png' for st in ('Worked','Construction','Pillaged')]+[O/'review'/BASE/'Pillaged'/f for f in ('AO-front.png','AO-back.png')]+[O/'review/CSC_BAKERS_Bakery_Modern_2/Pillaged/render.png']
assert all(p.exists() for p in paths)
report={'passed':True,'reviewer':'agent','evidence':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},'checked':['Current footprint and opening locations; foundations reach -30','No extension, shelter, floor, props or painted interiors in state geometry','Brick and stone sampling matches worked: 3.875 px/unit horizontal, brick 4.127 vertical','Longitudinal wood UVs and mapped normal relief','Outward manifold wall solids and clean native AO front/back','Scaffold Construction only; Pillaged shell with native burn material binding','Worked meshes, attachments, placements and existing pillage decals unchanged'],'limits':['Blender preview does not reproduce the native burn overlay or particles/decal projection','No live Asset Editor viewport or in-game test']}
(O/'visual-review.json').write_text(json.dumps(report,indent=2))
ims=[Image.open(p).convert('RGBA') for p in paths[:3]];boxes=[im.getchannel('A').getbbox() for im in ims];crop=(min(b[0] for b in boxes)-18,min(b[1] for b in boxes)-18,max(b[2] for b in boxes)+18,max(b[3] for b in boxes)+18)
w,h=crop[2]-crop[0],crop[3]-crop[1];sheet=Image.new('RGB',(w*3+80,h+132),(25,29,35));draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',18)
for i,(im,label) in enumerate(zip(ims,('Worked','Construction','Pillaged shell'))):
 x=20+i*(w+20);sheet.paste(im.crop(crop),(x,58),im.crop(crop));draw.text((x+w/2,24),label,font=font,fill=(233,234,231),anchor='mm')
draw.text((20,h+85),'Modern L2 main building • extension excluded • fixed L2 icon camera',font=small,fill=(193,199,207))
draw.text((20,h+109),'Pillaged preview shows the mesh; native burn overlay is applied by the game.',font=small,fill=(159,168,180))
sheet.save(O/'Modern_L2_Worked_CON_PIL.png');print('REVIEW_ACCEPTED_AND_SHEET_SAVED')
