from bakery_props_atlas import *
from PIL import Image,ImageDraw
m=json.loads((STAGE/'atlas/manifest.json').read_text());sheet=Image.new('RGB',(1440,4*500),(230,228,220));d=ImageDraw.Draw(sheet)
for i,name in enumerate(['bakery_round_crust','bakery_oval_bread','bakery_long_crust','bakery_bread_stack_side']):
 r=next(v for v in m['regions'] if v['name']==name);b=Image.open(STAGE/'atlas'/r['sources']['B']).convert('RGB');mask=Image.open(STAGE/'atlas/sources/relief-r030'/(name+'_ScoringMask.png')).convert('L');over=Image.composite(Image.new('RGB',b.size,(0,220,255)),b,mask.point(lambda v:int(v*.6)));sheet.paste(b,(0,i*500+20));sheet.paste(over,(480,i*500+20));sheet.paste(mask.convert('RGB'),(960,i*500+20));d.text((5,i*500+4),name+' B | cyan score mask | score mask',fill='black')
sheet.save(OUT/'Bread_Score_Alignment.jpg',quality=95)
for p in [ROOT/'project/tools/art/strengthen_bakery_revision06.py',OUT/'brick-grid-alignment.json',OUT/'normal-strength-report.json']:
 shutil.copy2(p,STAGE/'atlas/sources/relief-r030'/p.name);shutil.copy2(p,SOURCE/'art-provenance/relief-r030'/p.name)
