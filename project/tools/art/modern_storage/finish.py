"""Review boards, preserved source checks and portable candidate library packaging."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json,hashlib,shutil
O=Path.home()/'Desktop/Codex/modern-storage-v1-20261029';A=Path.home()/'Desktop/Working Files/3D Art';C=Path.home()/'Desktop/Codex/storage-modern-concepts-20261029'
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',30);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
def fit(im,size):
 im=im.copy();im.thumbnail(size,Image.Resampling.LANCZOS);return im
for size,title in (('M','Modern medium storage'),('L','Modern large storage')):
 ims=[Image.open(O/'review'/f'{size}_{variant}.png').convert('RGBA') for variant in ('Standard','Dispatch')]
 boxes=[im.getchannel('A').getbbox() for im in ims];crop=(max(0,min(b[0] for b in boxes)-18),max(0,min(b[1] for b in boxes)-18),min(1200,max(b[2] for b in boxes)+18),min(1200,max(b[3] for b in boxes)+18))
 board=Image.new('RGB',(1800,1050),(24,28,33));d=ImageDraw.Draw(board)
 for i,(im,label) in enumerate(zip(ims,('Receiving / storage','Dispatch / '+('pallet jack' if size=='M' else 'compact flatbed')))):
  im=fit(im.crop(crop),(870,900));x=15+900*i+(870-im.width)//2;y=75+(900-im.height)//2;board.paste(im,(x,y),im);d.text((450+i*900,32),label,font=font,fill='#e2e7ed',anchor='mm')
 d.text((25,1005),title+' — Blender v1 · daytime, emission disabled',font=small,fill='#b6c2cd');board.save(O/f'Storage_{size}_Modern_Review.png')
 # Concept fidelity check kept alongside the primary delivery boards.
 concept=Image.open(C/f'Modern_Storage_{size}_Concept_v01.png').convert('RGB');concept=concept.crop((0,0,concept.width//2,round(concept.height*.9)));modern=ims[0].crop(crop)
 page=Image.new('RGB',(1800,1050),(24,28,33));d=ImageDraw.Draw(page)
 for i,(im,label) in enumerate(((concept,'Concept direction'),(modern,'Blender — '+('historical scale' if size=='M' else 'rebalanced cross-gable')))):
  im=fit(im,(870,900));x=15+i*900+(870-im.width)//2;y=75+(900-im.height)//2;page.paste(im,(x,y),im if im.mode=='RGBA' else None);d.text((450+i*900,32),label,font=font,fill='#e2e7ed',anchor='mm')
 page.save(O/f'Storage_{size}_Concept_Comparison.png')
# Contact sheet includes exact paint-only and relief-only evidence without image alteration.
page=Image.new('RGB',(1920,1080),(24,28,33));d=ImageDraw.Draw(page)
for row,size in enumerate(('M','L')):
 for col,(label,key) in enumerate((('Paint only','B_Only'),('Normals off','N_Off_0'),('Normals on','N_On_0'),('Other light','N_On_1'))):
  im=Image.open(O/'review'/f'{size}_{key}.png').convert('RGBA');b=im.getchannel('A').getbbox();im=fit(im.crop(b),(460,470));x=10+col*480+(460-im.width)//2;y=45+row*540+(470-im.height)//2;page.paste(im,(x,y),im);d.text((col*480+240,row*540+20),size+' · '+label,font=small,fill='#e2e7ed',anchor='mm')
page.save(O/'Paint_Normal_Review.png')
plan=json.loads((O/'atlas-plan.json').read_text());plan['props_new_cells']['48']='painted metal swatch recoloured from existing cream; drum';plan['accepted_changes']='Lower narrower large cross-gable; compact 37.3x18.8 truck; open receiving edge; corrected non-overlapping jambs; consistent masonry scale'
for p,sha in plan['source_hashes'].items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==sha,('Published source changed',p)
(O/'atlas-plan.json').write_text(json.dumps(plan,indent=2))
for fam,prefix in (('CSC_Buildings_Modern','CSC_Atlas_Modern'),('CSC_Props_Modern','CSC_Props_Modern_01')):
 dest=A/'Textures'/fam/'Candidates/2026-10-29_Storage_v001';(dest/'textures').mkdir(parents=True,exist_ok=True);(dest/'sources').mkdir(exist_ok=True)
 for p in (O/'textures').glob(prefix+'*.png'):shutil.copy2(p,dest/'textures'/p.name)
 for p in (O/'sources').glob('Storage_*'):shutil.copy2(p,dest/'sources'/p.name)
 shutil.copy2(O/'atlas-plan.json',dest/'atlas-plan.json')
 (dest/'library.json').write_text(json.dumps({'status':'candidate; not published or installed','maps':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (dest/'textures').glob('*.png')},'source_package':str(O),'build_scripts':'project/tools/art/modern_storage','dependency':'Published buildings r015 / props r010 plus preserved Cafe candidate cells'},indent=2))
masters=json.loads((O/'masters.json').read_text());counts={r['group']:r['vertices'] for r in masters};budgets={'M_standard':counts['M']+counts['Drum'],'M_dispatch':counts['M']+counts['Drum']+counts['PalletJack'],'L_standard':counts['L']+counts['Hoist']+counts['Drum'],'L_dispatch':counts['L']+counts['Hoist']+counts['Drum']+counts['Truck']}
report={'stage':'Blender review and native-format verified; no AE or game installation','masters':masters,'saved_files':json.loads((O/'final-saved-validation.json').read_text()),'native':json.loads((O/'native-validation.json').read_text()),'published_source_hashes_unchanged':True,'normal_gate':'B-only plus normals off/on under two oblique lights; separate AO-only images','advisory_budgets':budgets,'budget_scope':'All new geometry counted conservatively; existing reusable flour props excluded here and included in full scene records. Large dispatch exceeds2200 target; allowed advisory.'}
(O/'delivery.json').write_text(json.dumps(report,indent=2));print('BOARDS_AND_CANDIDATES_READY')
