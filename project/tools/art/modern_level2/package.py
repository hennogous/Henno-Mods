"""Portable Stage3 candidate atlas and review package; shared Current is untouched."""
from pathlib import Path
import json,hashlib,shutil,subprocess
from PIL import Image,ImageDraw,ImageFont
O=Path.home()/'Desktop/Codex/modern-level2-v1-20261028';ART=Path.home()/'Desktop/Working Files/3D Art';D=ART/'Level 2/modern/revision-01-concept-base';ROOT=Path(__file__).resolve().parents[4]
source=ART/'Textures/CSC_Buildings_Modern/Current';candidate=D/'atlas-candidate';shutil.copytree(source,candidate,dirs_exist_ok=True);shutil.copytree(O/'textures',candidate/'textures',dirs_exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
for p in (O/'textures').glob('*.png'):
 old=Image.open(source/'textures'/p.name).convert('RGB');new=Image.open(p).convert('RGB');w,h=new.size
 # Occupied Stage2 and lower-half reservations remain byte-for-byte identical.
 for rect in [(0,0,w//2,h//2),(0,h//2,w,h)]:assert old.crop(rect).tobytes()==new.crop(rect).tobytes(),p.name
 checks[p.name]=sha(p)
for ch in ('B','N','G','M','E'):
 name='CSC_Atlas_Modern'+('_B_BAKERS' if ch=='B' else '_'+ch)+'.png';shutil.copy2(O/'textures'/name,candidate/'sources'/('registered_'+ch+'.png'))
for group,ident in [('Building','CSC_Level_2_Modern'),('Workshop','CSC_Level_2_Modern_Workshop')]:shutil.copy2(O/'bakes'/(group+'.png'),candidate/'bakes'/(ident+'.png'))
plan=json.loads((candidate/'atlas-plan.json').read_text());alloc=json.loads((O/'atlas-allocation.json').read_text());plan['building']['stage3_used_tiles']={'0':'ochre brick','1':'blue slate masonry','2':'sage standing seam roof','3':'cream olive bargeboard','4':'cream timber','5':'cream four-pane window','6':'green six-pane shopfront','7':'chimney masonry','8':'green timber','9':'brown timber','10':'concrete','11':'plaster','12':'workshop paving','13':'interior recess','14':'iron','15':'end grain'}
for group,ident in [('Building','CSC_Level_2_Modern'),('Workshop','CSC_Level_2_Modern_Workshop')]:plan['AO_allocations'][ident]=['building',alloc['AO'][group]]
plan['building']['stage3_emissive']='Cream windows all four panes; UV3 upstairs only. Ground-floor windows dark.';(candidate/'atlas-plan.json').write_text(json.dumps(plan,indent=2))
info=json.loads((candidate/'library.json').read_text());info.update(release='2026-10-28_Modern_Stage3_candidate01',status='Level2 first authoring version; not promoted to shared Current or installed into AE',source=str(D/'CSC_Level_2_Modern.blend'),source_sha256=sha(D/'CSC_Level_2_Modern.blend'),maps=checks);(candidate/'library.json').write_text(json.dumps(info,indent=2))
for name in ('Stage3_Generated_B.png','Stage3_Projection_Layout.png','relief-registration.json','brief.json'):shutil.copy2(O/name,candidate/'sources'/name)
shutil.copytree(O/'height',candidate/'sources/stage3-height',dirs_exist_ok=True)
for name in ('build.py','materials.py','relief.py','refine_sampling.py','pack.py'):shutil.copy2(Path(__file__).with_name(name),candidate/'sources'/name)
prompt='Built-in ImageGen. Exact 4x4 projection/layout guide; approved Bakery sheltered-dispatch concept as palette/material authority; DIS_COM_Base_B as Firaxis painting reference. Ochre brick, dark blue-grey masonry, muted sage standing-seam roofs, cream chunky trim and four-pane frames, green glazed shopfront; selected edge wear and recessed construction shadows, calm material fields; no perspective, glow, text or scene lighting. Final generated artwork retained verbatim; measured structural profiles authored separately for N. Original ImageGen request is in this conversation.'
(D/'Texture-authoring.txt').write_text(prompt)
(O/'package-validation.json').write_text(json.dumps({'existing_atlas_regions_preserved':True,'candidate_only':True,'maps':checks,'source_current_release':json.loads((source/'library.json').read_text())['release']},indent=2))
# Convert the changed surface maps and verify exact top-level native pixels.
(O/'native/textures').mkdir(parents=True,exist_ok=True)
for ch in ('B_BAKERS','N','G','M','E'):
 p=O/'textures'/('CSC_Atlas_Modern_'+ch+'.png');r=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-o',str(O/'native/textures'),str(p)],capture_output=True,text=True);assert r.returncode==0
 assert Image.open(O/'native/textures'/(p.stem+'.dds')).convert('RGB').tobytes()==Image.open(p).convert('RGB').tobytes()
print('CANDIDATE_ATLAS_AND_DDS_VERIFIED')
