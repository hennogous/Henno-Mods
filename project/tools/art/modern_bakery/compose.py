from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,shutil
O=Path.home()/'Desktop/Codex/modern-bakery-v1-20261028'
D=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Bakery/modern/revision-01-sheltered-bakery'
bg=(25,29,35,255)
model=Image.open(O/'review/combined.png').convert('RGBA')
solo=Image.new('RGBA',model.size,bg);solo.alpha_composite(model);solo.convert('RGB').save(O/'Bakery_Modern_First_Version.png')
concept=Image.open(Path.home()/'Desktop/Codex/bakery-modern-concept-20261026/Bakery_Modern_Sheltered_Dispatch_Concept.png').convert('RGBA').crop((295,20,1210,935))
canvas=Image.new('RGBA',(2200,1190),bg);d=ImageDraw.Draw(canvas)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',32);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23)
for x,im,title in [(0,concept,'Approved Bakery concept'),(1100,model,'First Blender version — reusable L2 base')]:
 d.text((x+45,30),title,font=font,fill=(231,230,215))
 if x==0:im=im.resize((1000,1000),Image.Resampling.LANCZOS);canvas.alpha_composite(im,(x+50,105))
 else:canvas.alpha_composite(im,(x,80))
d.text((45,1136),'Concept equipment adapted to the retained historical openings and forward shelter.',font=small,fill=(174,184,192))
canvas.convert('RGB').save(O/'Bakery_Concept_Comparison.png')
for p in [O/'Bakery_Modern_First_Version.png',O/'Bakery_Concept_Comparison.png',O/'native-validation.json',O/'architecture-preservation.json',O/'masters.json']:
 if p.exists():shutil.copy2(p,D/p.name)
report=json.loads((D/'assembly-validation.json').read_text());print(json.dumps({'counts':report['counts'],'errors':report['error_count'],'warnings':report['warning_count']}))
