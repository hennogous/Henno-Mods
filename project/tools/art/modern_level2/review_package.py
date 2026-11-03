from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont,ImageOps
O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028';D=Path.home()/'Desktop/Working Files/3D Art/Level 2/modern/revision-01-concept-base'
bg=(26,30,33);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',30);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',21)
concept=Image.open(Path.home()/'Desktop/Codex/bakery-modern-concept-20261026/Bakery_Modern_Sheltered_Dispatch_Concept.png').convert('RGBA').crop((285,10,1245,885))
model=Image.open(O/'review/converted.png').convert('RGBA');model=model.crop(model.getbbox())
canvas=Image.new('RGBA',(2200,1160),bg+(255,));draw=ImageDraw.Draw(canvas)
for x,im,label in [(0,concept,'Approved Bakery concept'),(1100,model,'Level 2 base + workshop shell')]:
 im=ImageOps.contain(im,(1060,1000),Image.Resampling.LANCZOS);canvas.alpha_composite(im,(x+(1100-im.width)//2,70+(1000-im.height)//2));draw.text((x+30,20),label,font=font,fill=(230,230,220))
draw.line((1100,15,1100,1100),fill=(65,71,74));draw.text((1130,1100),'First architectural version · emission off',font=small,fill=(190,195,190))
canvas.convert('RGB').save(O/'Level2_Concept_Comparison.png')
sheet=Image.new('RGBA',(1500,1080),bg+(255,));draw=ImageDraw.Draw(sheet)
variants=['B-only','neutral-off-A','neutral-on-A','converted','neutral-off-B','neutral-on-B']
for i,v in enumerate(variants):
 im=Image.open(O/'review'/(v+'.png')).convert('RGBA').resize((500,500),Image.Resampling.LANCZOS);x=i%3*500;y=i//3*540;sheet.alpha_composite(im,(x,y+35));draw.text((x+12,y+5),v,font=small,fill='white')
sheet.convert('RGB').save(O/'Material_Checks.png')
shutil=None
report={'review_images':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/'review').glob('*.png')},'concept':str(Path.home()/'Desktop/Codex/bakery-modern-concept-20261026/Bakery_Modern_Sheltered_Dispatch_Concept.png'),'scope':'Reusable architecture only; main and workshop independent','differences_by_scope':'No bakery equipment, storefront stall/awning, sign, planter, paving or trees in this architectural version. Rear unseen in concept is extrapolated.','fixes':['Roof seams corrected to follow roof slope','Gable brick sampling matches wall scale','Workshop roof-wall joins closed','Sloped wall-cap brick sample scale corrected'],'emission_in_comparison':False,'AE_or_game_tested':False}
(O/'visual-review.json').write_text(json.dumps(report,indent=2))
print(O/'Level2_Concept_Comparison.png')
