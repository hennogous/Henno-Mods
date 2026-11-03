"""AO-only atlas update and scoped display geometry publication; ASTs stay exact."""
import sys,json,hashlib,shutil,subprocess,os
from pathlib import Path
from PIL import Image
import numpy as np
from display_depth import ROOT,O,A,SRC,ID,dump
sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'));import modular_v9_native as n
from render_ae_asset import read_xml
MOD=n.MOD;LIB=A/'Textures/CSC_Props_Modern';CUR=LIB/'Current';D=O/'staged';AO='CSC_Props_Modern_01_AO.png'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd,log,cwd=None):
 r=subprocess.run(list(map(str,cmd)),cwd=cwd,capture_output=True,text=True);log.write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
def stage():
 old=Image.open(CUR/'textures'/AO).convert('RGB');page=old.copy();patch=Image.open(O/'bakes/Display.png').convert('RGB').resize((248,248),Image.Resampling.LANCZOS);patch=Image.fromarray(np.pad(np.array(patch),((4,4),(4,4),(0,0)),mode='edge'));page.paste(patch,(512,512));a=np.array(page,dtype=float)
 for tr in json.loads((O/'microAO-triangles.json').read_text()):
  q=np.array(tr['UV2'])*[2048,-2048]+[0,2048];uv=np.array(tr['UV1']);lo=np.maximum(0,np.floor(q.min(0)).astype(int));hi=np.minimum(2047,np.ceil(q.max(0)).astype(int));matrix=np.vstack((q.T,np.ones(3)))
  if abs(np.linalg.det(matrix))<1e-8:continue
  inv=np.linalg.inv(matrix);slot=tr['slot'];m=np.array(Image.open(CUR/'sources/bakery-v3'/f'tray_{slot}_microAO.png'),float)/255
  for y in range(lo[1],hi[1]+1):
   for x in range(lo[0],hi[0]+1):
    w=inv@np.array([x+.5,y+.5,1])
    if min(w)<-1e-6:continue
    u,v=w@uv;xx=int(round(u*1024-slot%8*128));yy=int(round((1-v)*1024-slot//8*128));a[y,x]*=m[np.clip(yy,0,127),np.clip(xx,0,127)]
 page=Image.fromarray(np.uint8(np.clip(a,0,255)));mask=np.ones((2048,2048),bool);mask[512:768,512:768]=False;assert np.array_equal(np.array(page)[mask],np.array(old)[mask])
 (O/'textures').mkdir(exist_ok=True);page.save(O/'textures'/AO)
 for f in (O/'masters').iterdir():shutil.copy2(O/'textures'/AO,f/'textures'/AO)
 # Stage the current full dependency set, including the newly published L2 CON/PIL.
 prior=Path.home()/'Desktop/Codex/modern-l2-states-20261029/staged'
 for p in prior.rglob('*'):
  q=MOD/p.relative_to(prior)
  if p.is_file() and q.is_file():target=D/p.relative_to(prior);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,target)
 (O/'scalar').mkdir(exist_ok=True);page.getchannel('R').save(O/'scalar'/AO)
 run([ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8_UNORM','--ignore-srgb','-o',D/'Textures',O/'scalar'/AO],O/'ao-conversion.log')
 dds=D/'Textures'/AO.replace('.png','.dds');spec={'slot':'AO','size':[2048,2048],'format':'R8_UNORM'};n.exp.normalize_ao_dds(dds,spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds');n.exp.validate_dds(dds,spec)
 model=json.loads((O/'models'/(ID+'.json')).read_text());native=O/'native';native.mkdir(exist_ok=True);cn6=native/(ID+'.cn6');fgx=D/'Geometries'/(ID+'.fgx');n.exp.write_cn6(cn6,model);n.save(D/'Geometries'/(ID+'.geo'),n.exp.geometry(model,read_xml(MOD/'Geometries'/(ID+'.geo'))))
 conv=ROOT/'project/tools/cn6libs/CN6ToFGX.exe';run([conv,cn6,fgx,'2'],O/'native-conversion.log',conv.parent);exe,_=n.helper(O/'native-reader');dest=native/(ID+'.json');run([exe,exe.parent,fgx,dest],O/'native-readback.log',exe.parent);actual=json.loads(dest.read_text());err=0
 for m,b in zip(model['meshes'],actual['meshes']):
  assert m['triangles']==b['triangles'] and len(m['vertices'])==len(b['vertices']) and b['boneBindings']==['Bone']
  for v,w in zip(m['vertices'],b['vertices']):
   vals=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'];err=max(err,max(abs(x-y) for x,y in zip(v,vals)));assert w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
 assert err<1e-4
 changes=['Geometries/'+ID+'.fgx','Geometries/'+ID+'.geo','Textures/'+dds.name];dump(O/'staging-validation.json',{'passed':True,'native_error':err,'native_vertices':sum(len(m['vertices']) for m in actual['meshes']),'publish_files':changes,'AO_outside_display_identical':True});print('STAGED_DISPLAY',err,flush=True)
def publish():
 checks=json.loads((O/'staging-validation.json').read_text());assert checks['passed'];cook=json.loads((O/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps'];assert 'ERRORS!!' not in (O/'cook-check/stdout.log').read_text(errors='replace').replace('\x00','');assert json.loads((O/'visual-review.json').read_text())['passed']
 base=json.loads((O/'baseline.json').read_text());assert all(sha(MOD/p)==h for p,h in base.items()),'Concurrent runtime edit'
 rows=json.loads((O/'authoring.json').read_text());assert all(sha(r['source'])==r['before'] for r in rows)
 manifest=json.loads((CUR/'library.json').read_text());assert all(sha(CUR/'textures'/p)==h for p,h in manifest['maps'].items());release='2026-10-29_Modern_r010';snap=LIB/'Releases'/release;assert not snap.exists()
 payload={snap/p.relative_to(CUR):p.read_bytes() for p in CUR.rglob('*') if p.is_file()};manifest.update(previous_release=manifest['release'],release=release,status='Bread display historical depth; isolated fresh display AO, all painted maps and oven E preserved');manifest['maps'][AO]=sha(O/'textures'/AO)
 plan=json.loads((CUR/'atlas-plan.json').read_text());plan['modern_bread_display_depth']=json.loads((O/'proportions.json').read_text())
 updates={'textures/'+AO:(O/'textures'/AO).read_bytes(),'library.json':json.dumps(manifest,indent=2).encode(),'atlas-plan.json':json.dumps(plan,indent=2).encode(),'sources/display-depth/before-AO.png':(CUR/'textures'/AO).read_bytes(),'sources/display-depth/Display_Bake.png':(O/'bakes/Display.png').read_bytes(),'sources/display-depth/microAO-triangles.json':(O/'microAO-triangles.json').read_bytes(),'sources/display-depth/proportions.json':(O/'proportions.json').read_bytes(),'sources/display-depth/packed-patch.png':b''}
 patchpath=O/'textures/Display_AO_Patch.png';Image.open(O/'textures'/AO).crop((512,512,768,768)).save(patchpath);updates['sources/display-depth/packed-patch.png']=patchpath.read_bytes()
 updates['scripts/apply_display_depth_ao.py']=b"from pathlib import Path\nfrom PIL import Image\np=Path(__file__).resolve().parents[1]\nim=Image.open(p/'sources/display-depth/before-AO.png').convert('RGB')\nim.paste(Image.open(p/'sources/display-depth/packed-patch.png'),(512,512))\nim.save(p/'textures/CSC_Props_Modern_01_AO.png')\n"
 for rel,data in updates.items():payload[CUR/rel]=data;payload[snap/rel]=data
 payload[LIB/'CURRENT.json']=json.dumps({'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'},indent=2).encode()
 for r in rows:
  payload[Path(r['source'])]=Path(r['prepared']).read_bytes();payload[Path(r['source']).with_name(Path(r['source']).stem+'-validation.json')]=Path(r['prepared']).with_name('validation.json').read_bytes()
 payload[SRC/'textures'/AO]=(O/'textures'/AO).read_bytes();payload[SRC/(ID+'.cn6')]=(O/'native'/(ID+'.cn6')).read_bytes()
 for rel in checks['publish_files']:payload[MOD/rel]=(D/rel).read_bytes()
 backup=O/'publication-backup';backup.mkdir(exist_ok=True);report=[]
 for i,(p,data) in enumerate(payload.items()):
  r={'destination':str(p),'before':sha(p) if p.exists() else None,'after':hashlib.sha256(data).hexdigest()}
  if p.exists():q=backup/f'{i:03}-{p.name}';shutil.copy2(p,q);r['backup']=str(q)
  report.append(r)
 dump(backup/'manifest.json',report)
 for r,(p,data) in zip(report,payload.items()):
  assert (sha(p) if p.exists() else None)==r['before'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);assert sha(p)==r['after']
 allowed={str(Path(p)) for p in checks['publish_files']};assert all(sha(MOD/p)==h for p,h in base.items() if p not in allowed)
 dump(O/'publication-report.json',{'installed':True,'files':report,'release':release,'ASTs_byte_unchanged':True,'game_deployment':False});n.cache(O);dump(O/'final-verification.json',{'passed':True,'published_files':len(report),'all_AST_placements_preserved':True,'props_release':release,'native_checks_and_cook':'passed','engine_review':'not performed'});print('PUBLISHED_DISPLAY_DEPTH',release)
if __name__=='__main__':globals()[sys.argv[1]]()
