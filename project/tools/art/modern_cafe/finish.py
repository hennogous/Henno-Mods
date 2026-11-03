from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,xml.etree.ElementTree as ET,shutil
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029';A=Path.home()/'Desktop/Working Files/3D Art';D=A/'BAKERS/Cafe/modern/revision-01-garden'
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',29);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
ims=[Image.open(O/'review'/f'Cafe_{v}_{t}.png').convert('RGBA') for t in ('Day','Night') for v in ('Standard','Alternate')];boxes=[im.getchannel('A').getbbox() for im in ims];crop=(max(0,min(b[0] for b in boxes)-15),max(0,min(b[1] for b in boxes)-15),min(1200,max(b[2] for b in boxes)+15),min(1200,max(b[3] for b in boxes)+15))
for row,time in enumerate(('Day','Night')):
 pics=[ims[row*2+i].crop(crop) for i in range(2)];w,h=pics[0].size;page=Image.new('RGB',(w*2+60,h+115),(24,28,33));d=ImageDraw.Draw(page)
 for i,(p,label) in enumerate(zip(pics,('Garden Café','Garden Café + coffee van'))):
  x=20+i*(w+20);page.paste(p,(x,70),p);d.text((x+w/2,30),label,font=font,fill='#e2e7ed',anchor='mm')
 d.text((20,h+88),'First Blender version  •  '+('Daytime — emissive disabled' if time=='Day' else 'Night lighting preview — soft room emissive'),font=small,fill='#bbc5d0');page.save(O/f'Cafe_Option_C_{time}.png')
page=Image.new('RGB',(1580,660),(24,28,33));d=ImageDraw.Draw(page)
for col,(ch,title) in enumerate((('B_BAKERS','Daytime colour'),('N','Registered relief'),('E_BAKERS','Soft emissive'))):
 im=Image.open(O/'textures'/f'CSC_Interiors_Modern_{ch}.png').convert('RGB');im=im.crop((0,0,im.width,im.height//2)).resize((500,250));x=20+col*520;page.paste(im,(x,70));d.text((x+250,30),title,font=font,fill='#e2e7ed',anchor='mm')
 d.text((x,340),'Top row: Bakery    /    second row: Café',font=small,fill='#bbc5d0')
 if col==0:
  for row in range(2):
   for i,label in enumerate(('Rear','Side','Floor','Reserve')):d.text((x+62+i*125,85+row*125),label,font=small,fill='white',stroke_width=2,stroke_fill='#293031',anchor='mt')
d.text((20,400),'Fixed 4 × 4 UV layout. B + N: 1024px. E: 512px.',font=font,fill='#e2e7ed');d.text((20,450),'The lower two rows remain reserved. Furniture and equipment inside rooms are painted, not modeled.',font=small,fill='#bbc5d0')
page=page.crop((0,0,1580,505));page.save(O/'Dedicated_Interior_Atlases.png')
concept=Image.open(Path.home()/'Desktop/Codex/cafe-modern-concepts-20261029/C_Garden_Cafe.png').convert('RGB').crop((0,75,887,825));pic=ims[0].crop(crop);page=Image.new('RGB',(1820,950),(24,28,33));d=ImageDraw.Draw(page)
for i,(p,title) in enumerate(((concept,'Approved concept C'),(pic,'First Blender version'))):
 p.thumbnail((880,850),Image.Resampling.LANCZOS);x=20+i*900+(880-p.width)//2;y=70+(850-p.height)//2;page.paste(p,(x,y),p if p.mode=='RGBA' else None);d.text((460+i*900,30),title,font=font,fill='#e2e7ed',anchor='mm')
page.save(O/'Cafe_Concept_Compared.png')
# Refresh texture hashes in exported candidate contracts after paint refinements.
for path in (O/'models').glob('*.json'):
 model=json.loads(path.read_text())
 for m in model['meshes']:
  for ma in m['materials']:
   for info in ma.get('images',{}).values():
    p=Path(info['path'])
    if p.is_file():info['sha256']=hashlib.sha256(p.read_bytes()).hexdigest()
 path.write_text(json.dumps(model))
plan=json.loads((O/'atlas-plan.json').read_text());plan['props_surface_cells']={'40':'espresso face','41':'pastry display','42':'reserved','43':'cup emblem','44':'dark green trim','45':'glass'};plan['AO_candidate']=json.loads((O/'AO_allocations.json').read_text());(O/'atlas-plan.json').write_text(json.dumps(plan,indent=2));shutil.copy2(O/'atlas-plan.json',D/'candidate-atlas-plan.json')
for p in (O/'textures').glob('CSC_Interiors*'):assert Image.open(p).size==((512,512) if '_E_' in p.name else (1024,1024))
# Exact AST comparison for the separately authorized trolley move.
Q=Path.home()/'Desktop/Codex/modern-bakery-display-depth-20261029';before=ET.fromstring((Q/'Bakery_2_before_trolley_move.ast').read_bytes());after=ET.parse(ROOT/'Civ Supply Chains/Assets/CSC_BAKERS_Bakery_Modern_2.ast').getroot()
diff=[]
for a,b in zip(before.iter(),after.iter()):
 assert a.tag==b.tag and a.attrib==b.attrib
 if (a.text or '').strip()!=(b.text or '').strip():diff.append((a.tag,(a.text or '').strip(),(b.text or '').strip()))
assert diff==[('x','-16.919180','-17.310166'),('y','-6.597803','-7.137929')],diff
report={'candidate_only':True,'Café_installed':False,'saved_native_checks':json.loads((O/'native-validation.json').read_text()),'source_checks':json.loads((O/'final-saved-validation.json').read_text()),'Bakery_migration':json.loads((O/'interior-migration.json').read_text()),'trolley_AST_exact_diff':diff,'texture_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (O/'textures').glob('*.png')},'visual_review':'Day/night, B-only/N-only, alpha room depth, original silhouette, shelf and frame registration, van clearance; game shader untested','retained_first_version_limit':'Historical wooden garden chairs/tables retained; no green metal chair asset yet.'}
(O/'delivery.json').write_text(json.dumps(report,indent=2));print('REVIEW_BOARDS_AND_DELIVERY_READY')
