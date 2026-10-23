"""Stage and publish the tower identity migration without altering archived snapshots."""
import sys,json,shutil,hashlib,os,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];MOD=ROOT/'Civ Supply Chains';OUT=Path(sys.argv[2]);STAGE=OUT/'staged'
OLD='CSC_BAKERS_Wind_Mill_'+'Plaster'+'_Tower';NEW='CSC_BAKERS_Wind_Mill_Tower'
ART=Path.home()/'Desktop/Working Files/3D Art';SOURCE=ART/'BAKERS/Wind Mill'/('plaster'+'-tower');DEST=SOURCE.with_name('tower');LIB=ART/'Textures/CSC_Props';RELEASE='2026-10-22_Shared_01_r041'
PAIRS=[(OLD,NEW),('plaster'+'_tower','tower'),('plaster'+'-tower','tower'),('Plaster'+'-Tower','Tower')]
def rename(s):
 for a,b in PAIRS:s=s.replace(a,b)
 return s
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
TEXT={'.py','.cs','.md','.json','.xml','.ast','.geo','.anm','.mtl','.tex','.xlp','.artdef','.civ6proj','.cn6','.txt','.toml','.yaml','.yml','.sql'}
def rewrite(data):
 for a,b in PAIRS:data=data.replace(a.encode(),b.encode())
 return data
def stage():
 OUT.mkdir(parents=True,exist_ok=True);plan=[];backup=OUT/'before-files';backup.mkdir(exist_ok=True)
 def record(old,new,src):
  if any(r['destination']==str(new) for r in plan):raise ValueError('Duplicate target '+str(new))
  b=backup/(str(len(plan))+'-'+old.name);shutil.copy2(old,b)
  collision=None
  if old!=new and new.exists():
   collision=backup/(str(len(plan))+'-collision-'+new.name);shutil.copy2(new,collision)
  plan.append(dict(old=str(old),destination=str(new),source=str(src),before=sha(old),backup=str(b),collision=str(collision) if collision else None,collision_hash=sha(new) if collision else None))
 # Runtime graph and all active repository documentation/tool references.
 for base in [MOD,ROOT/'project',ROOT/'memory',ROOT/'docs']:
  for p in list(base.rglob('*')):
   if not p.is_file() or any(x in ['Archive','archive','__pycache__','node_modules','.git'] for x in p.parts):continue
   dest=p.with_name(rename(p.name))
   if p.suffix.lower() not in TEXT and dest==p:continue
   data=p.read_bytes();newdata=rewrite(data) if p.suffix.lower() in TEXT else data
   if data==newdata and dest==p:continue
   rel=dest.relative_to(ROOT);target=(STAGE/dest.relative_to(MOD)) if p.is_relative_to(MOD) else OUT/'repository'/rel;target.parent.mkdir(parents=True,exist_ok=True)
   # Geometry/animation payloads were freshly regenerated under the new identity.
   if not(p.suffix=='.fgx' and p.is_relative_to(MOD) and target.exists()):target.write_bytes(newdata)
   record(p,dest,target)
 # Consolidate the older, unused Tower XLP entry with the newly renamed one.
 sys.path.insert(0,str(ROOT/'project/tools/art'));from windmill_tower_integrate import read_xml,save,txt
 xlp=STAGE/'XLPs/CSC_Tilebases.xlp';root=read_xml(xlp);entries=root.find('m_Entries');seen=set()
 for e in list(entries):
  ident=txt(e,'m_EntryID')
  if ident==NEW and ident in seen:entries.remove(e)
  seen.add(ident)
 save(root,xlp)
 # New eight-second ANM generated alongside the clip supersedes copied metadata.
 anm=STAGE/'Animations'/(NEW+'_Turn.anm');root=read_xml(anm);root.find('m_fDuration').text='8.000000';save(root,anm)
 # Stage the source folder, preserving snapshots in before-source at install.
 newsource=OUT/'source-folder';shutil.copytree(SOURCE,newsource,dirs_exist_ok=True)
 for p in sorted(newsource.rglob('*'),key=lambda p:len(p.parts),reverse=True):
  if not p.is_file():continue
  if p.suffix=='.blend1':p.unlink();continue
  if p.suffix.lower() in TEXT:p.write_bytes(rewrite(p.read_bytes()))
  target=p.with_name(rename(p.name))
  if target!=p:p.rename(target)
 for suffix in ['', '_CON+PIL']:
  shutil.copy2(OUT/'masters'/(NEW+suffix+'.blend'),newsource/(NEW+suffix+'.blend'))
  shutil.copy2(STAGE/'Geometries'/(NEW+suffix+'.cn6'),newsource/(NEW+suffix+'.cn6'))
 for ext in ['.fbx','.json']:shutil.copy2(STAGE/'Animations'/(NEW+'_Turn'+ext),newsource/(NEW+'_Turn'+ext))
 atlas=OUT/'atlas-release';shutil.copytree(LIB/'Current',atlas,dirs_exist_ok=True)
 for p in list(atlas.rglob('*')):
  if not p.is_file() or p.name=='library.json':continue
  if p.suffix.lower() in TEXT:p.write_bytes(rewrite(p.read_bytes()))
  target=p.with_name(rename(p.name))
  if target!=p:p.rename(target)
 lib=json.loads(rewrite((LIB/'Current/library.json').read_bytes()));lib.update(release=RELEASE,content_revision=41,snapshot_path='Releases/'+RELEASE,change_authorization='Henno requested the Tower identity everywhere and an eight-second rotation. Pixel content unchanged.')
 lib['source_approved_blend_sha256'].update({str(DEST/p.name):sha(p) for p in (OUT/'masters').glob('*.blend')});lib['files']={p.relative_to(atlas).as_posix():sha(p) for p in atlas.rglob('*') if p.is_file() and p.name!='library.json'}
 (atlas/'library.json').write_text(json.dumps(lib,indent=2)+'\n')
 (OUT/'install-plan.json').write_text(json.dumps(plan,indent=2));(OUT/'library-baseline.json').write_text(json.dumps({str(p):sha(p) for p in (LIB/'Current').rglob('*') if p.is_file()},indent=2))
 # Make renamed helper references available for isolated validation only.
 for r in plan:
  if Path(r['old']).is_relative_to(ROOT/'project/tools'):
   shutil.copy2(r['source'],r['destination'])
   if r['old']!=r['destination']:Path(r['old']).unlink()
 print('RENAME_STAGED',len(plan),'files')

def install():
 plan=json.loads((OUT/'install-plan.json').read_text())
 for r in plan:
  if Path(r['old']).is_relative_to(ROOT/'project/tools'):
   assert sha(r['destination'])==sha(r['source']);continue
  assert sha(r['old'])==r['before'],r['old']
  if r['collision']:assert sha(r['destination'])==r['collision_hash']
 for p,h in json.loads((OUT/'library-baseline.json').read_text()).items():assert sha(p)==h,p
 for r in json.loads((OUT/'inspection.json').read_text()):assert sha(r['path'])==r['sha']
 assert not DEST.exists() and not (LIB/'Releases'/RELEASE).exists()
 anim=json.loads((OUT/'native-animation-validation.json').read_text());assert anim['frames_checked']==241 and anim['duration_seconds']==8
 log=(OUT/'cook-renamed/stdout.log').read_text();assert 'XLP cook completed with success.' in log and '(ERRORS!!)' not in log and 'Replacing asset:' not in log
 for name in [NEW,NEW+'_CON+PIL']:
  v=json.loads((OUT/(name+'-source-validation.json')).read_text());assert v['error_count']==v['warning_count']==0
 for r in plan:
  if not Path(r['old']).is_relative_to(ROOT/'project/tools'):
   shutil.copy2(r['source'],r['destination'])
   if r['old']!=r['destination']:Path(r['old']).unlink()
  r['installed_sha256']=sha(r['destination'])
 # All source/library paths are explicit checked children of their known roots.
 assert SOURCE.parent.resolve()==(ART/'BAKERS/Wind Mill').resolve()
 assert DEST.parent.resolve()==SOURCE.parent.resolve()
 shutil.move(str(SOURCE),str(OUT/'before-source'));shutil.copytree(OUT/'source-folder',DEST)
 shutil.copy2(LIB/'CURRENT.json',OUT/'before-CURRENT.json');shutil.copytree(LIB/'Current',OUT/'before-library');shutil.copytree(OUT/'atlas-release',LIB/'Current',dirs_exist_ok=True);shutil.copytree(OUT/'atlas-release',LIB/'Releases'/RELEASE)
 for p in (LIB/'Current').rglob('*'):
  if p.is_file() and rename(p.name)!=p.name:p.unlink()
 (LIB/'CURRENT.json').write_text(json.dumps(dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-22',library_sha256=sha(LIB/'Current/library.json')),indent=2)+'\n')
 (OUT/'publication-report.json').write_text(json.dumps(dict(installed=True,release=RELEASE,files=plan,seconds_per_turn=8),indent=2));print('RENAMED_INSTALLED',len(plan))

def finish_library():
 # Windows may hold atlas subdirectories open. Verify the complete backup and
 # finish with in-place file copies, without moving/deleting those directories.
 for p,h in json.loads((OUT/'library-baseline.json').read_text()).items():assert sha(OUT/'before-library'/Path(p).relative_to(LIB/'Current'))==h
 plan=json.loads((OUT/'install-plan.json').read_text())
 for r in plan:assert sha(r['source'])==sha(r['destination']);r['installed_sha256']=sha(r['destination'])
 assert DEST.is_dir() and not SOURCE.exists()
 shutil.copytree(OUT/'atlas-release',LIB/'Current',dirs_exist_ok=True)
 for p in (LIB/'Current').rglob('*'):
  if p.is_file() and rename(p.name)!=p.name:
   assert sha(p)==sha(OUT/'before-library'/p.relative_to(LIB/'Current'));p.unlink()
 shutil.copytree(OUT/'atlas-release',LIB/'Releases'/RELEASE,dirs_exist_ok=True)
 (LIB/'CURRENT.json').write_text(json.dumps(dict(release=RELEASE,current='Current',manifest='Current/library.json',snapshot='Releases/'+RELEASE,updated_on='2026-10-22',library_sha256=sha(LIB/'Current/library.json')),indent=2)+'\n')
 (OUT/'publication-report.json').write_text(json.dumps(dict(installed=True,release=RELEASE,files=plan,seconds_per_turn=8,library_updated_in_place=True),indent=2));print('RENAMED_INSTALLED',len(plan))

def check():
 sys.path.insert(0,str(ROOT/'project/tools/art'));from windmill_tower_integrate import helper,read_xml,txt
 exe,_=helper(OUT/'cache');results=[]
 for suffix in ['', '_CON+PIL']:
  name=NEW+suffix;native=OUT/(name+'-native.json');subprocess.run([str(exe),str(exe.parent),str(STAGE/'Geometries'/(name+'.fgx')),str(native)],cwd=exe.parent,check=True)
  actual=json.loads(native.read_text());oldpath=OUT.parent/'windmill-simplify-20261022'/(OLD+suffix+'-native.json');old=json.loads(rename(oldpath.read_text()))
  assert actual['meshes']==old['meshes'],'Geometry changed beyond names';assert actual['models']==old['models'],'Skeleton changed beyond names'
  geo=read_xml(STAGE/'Geometries'/(name+'.geo'));assert geo.tag=='AssetObjects..GeometryInstance'
  for m in actual['meshes']:
   g=next(x for x in geo.findall('m_Meshes/Element') if txt(x,'m_Name')==m['name']);assert int(g.findtext('m_nBoundBoneCount'))==len(m['boneBindings'])==1
  results.append(dict(asset=name,native_geometry_and_skeleton_unchanged_except_names=True))
 shutil.copy2(OUT/(NEW+'-native.json'),OUT/'tower-native.json')
 subprocess.run([sys.executable,str(ROOT/'project/tools/art/readback_windmill_ground_animation.py'),str(OUT)],check=True)
 p=OUT/'validate-motion.py';p.write_text(p.read_text().replace("'duration_seconds':10","'duration_seconds':8"))
 (OUT/'rename-native-check.json').write_text(json.dumps(results,indent=2));print('NATIVE_RENAME_PARITY_PASSED')

def cache():
 path=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json';original=path.read_bytes();data=json.loads(original.decode('utf-8-sig'))
 (OUT/'assetcloud-before-rename.json').write_bytes(original)
 def convert(x):
  if isinstance(x,str):return rename(x)
  if isinstance(x,list):return [convert(v) for v in x]
  if isinstance(x,dict):return {rename(k):convert(v) for k,v in sorted(x.items(),key=lambda kv:OLD in kv[0])}
  return x
 files={}
 for item in sorted(data['Files'],key=lambda x:OLD in x['Filename']):
  item=convert(item);files[item['Filename']]=item
 data=convert(data);data['Files']=list(files.values());assert path.read_bytes()==original
 path.write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
 subprocess.run([sys.executable,str(ROOT/'project/tools/art/register_windmill_tower.py'),str(OUT)],check=True)

def verify():
 pub=json.loads((OUT/'publication-report.json').read_text())
 for r in pub['files']:assert sha(r['source'])==sha(r['destination']),r['destination']
 atlas=OUT/'atlas-release'
 for p in atlas.rglob('*'):
  if p.is_file():assert sha(p)==sha(LIB/'Current'/p.relative_to(atlas))==sha(LIB/'Releases'/RELEASE/p.relative_to(atlas))
 for p in (OUT/'before-library/textures').glob('*.png'):assert sha(p)==sha(LIB/'Current/textures'/p.name)
 assert not SOURCE.exists()
 leftovers=[]
 for base in [MOD,ROOT/'project',ROOT/'memory',ROOT/'docs',DEST,LIB/'Current']:
  for p in base.rglob('*'):
   if not p.is_file() or any(x in ['Archive','archive','__pycache__','node_modules','.git'] for x in p.parts):continue
   if rename(p.name)!=p.name:leftovers.append(str(p))
   if p.suffix.lower() in TEXT and rewrite(p.read_bytes())!=p.read_bytes():leftovers.append(str(p))
 assert not leftovers,leftovers
 sys.path.insert(0,str(ROOT/'project/tools/art'));from windmill_tower_integrate import read_xml,txt
 xlp=read_xml(MOD/'XLPs/CSC_Tilebases.xlp');assert sum(txt(n,'m_EntryID')==NEW for n in xlp.findall('m_Entries/Element'))==1
 anm=read_xml(MOD/'Animations'/(NEW+'_Turn.anm'));assert abs(float(anm.findtext('m_fDuration'))-8)<1e-6
 import struct
 NAME=NEW;RUIN=NEW+'_CON+PIL';code=(ROOT/'project/tools/art/verify_windmill_wood.py').read_text();code=code[code.index('def fnv(s):'):code.index('if installed:')].replace('cook-wood','cook-renamed');env=dict(OUT=OUT,NAME=NAME,RUIN=RUIN,struct=struct);exec(compile(code,'cooked_format_check','exec'),env)
 pub.update(verified=True,active_old_name_occurrences=0,texture_pixels_unchanged=True,cooked_formats=env['cooked']);(OUT/'publication-report.json').write_text(json.dumps(pub,indent=2));print('RENAME_AND_EIGHT_SECOND_LOOP_VERIFIED')

if __name__=='__main__':globals()[sys.argv[1]]()
