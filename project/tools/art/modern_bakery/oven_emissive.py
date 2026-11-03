"""Shared modern prop E: registered oven window emission, UV3-only master edit."""
import json,sys,hashlib,shutil,math,subprocess,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];MOD=ROOT/'Civ Supply Chains';O=Path.home()/'Desktop/Codex/modern-oven-emissive-20261028'
ART=Path.home()/'Desktop/Working Files/3D Art';LIB=ART/'Textures/CSC_Props_Modern';SRC=ART/'BAKERS/Bakery/modern/revision-04-ae';ID='CSC_BAKERS_Deck_Oven_Modern';EID='CSC_Props_Modern_01_E'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2))
def prepare():
 import numpy as np
 from PIL import Image,ImageDraw,ImageFilter
 for d in ('textures','sources','models','masters','staged/Textures','staged/Geometries','staged/Assets','staged/Materials'):(O/d).mkdir(parents=True,exist_ok=True)
 assert not (O/'baseline.json').exists()
 dump(O/'baseline.json',{p.relative_to(MOD).as_posix():sha(p) for f in ('Assets','Geometries','Textures','Materials','ArtDefs','XLPs') for p in (MOD/f).iterdir() if p.is_file()})
 b=LIB/'Current/textures/CSC_Props_Modern_01_B.png';shutil.copy2(b,O/'sources'/b.name);shutil.copy2(LIB/'Current/textures'/(EID+'.png'),O/'sources'/('Before_'+EID+'.png'))
 tile=Image.open(b).convert('RGB').crop((256,384,384,512));rgb=np.array(tile,dtype=float)/255;linear=np.where(rgb<=.04045,rgb/12.92,((rgb+.055)/1.055)**2.4)
 mask=Image.new('L',(128,128));draw=ImageDraw.Draw(mask)
 for rect in ((21,24,97,41),(21,70,97,86)):draw.rectangle(rect,fill=255)
 mask=mask.filter(ImageFilter.GaussianBlur(.7));radiance=(linear*.65+np.array([.02,.011,.004]))*(np.array(mask)/255)[:,:,None];srgb=np.where(radiance<=.0031308,radiance*12.92,1.055*radiance**(1/2.4)-.055)
 patch=Image.fromarray(np.uint8(np.clip(srgb*255,0,255)));page=Image.new('RGB',(256,256));page.paste(patch.resize((32,32),Image.Resampling.LANCZOS),(64,96));page.save(O/'textures'/(EID+'.png'));patch.save(O/'sources/Oven_Window_E_Registered.png');mask.save(O/'sources/Oven_Window_Mask.png')
 dump(O/'allocation.json',{'atlas_size':256,'grid':[8,8],'cell_size':32,'occupied':{'26':'Deck oven front, same normalized UV1 chart; only the two painted cavities emit'},'black_sentinel':[.02,.02],'black_region':'All cells except26 remain black; reserve lower-left cell56 for dark UVs','source_B_hash':sha(b),'method':'E derived from approved painted B through two registered window masks; no new albedo artwork','linear_painted_gain':.65,'minimum_weight_unchanged':True})
 print('E_PREPARED',flush=True)
def author():
 import bpy
 sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 import decode_blend as dec
 def signature(ob):return ([list(v.co) for v in ob.data.vertices],[list(p.vertices) for p in ob.data.polygons],[list(x.uv) for x in ob.data.uv_layers[0].data],[list(x.uv) for x in ob.data.uv_layers[1].data],[list(r) for r in ob.matrix_world])
 rows=[]
 for name in (ID,'CSC_BAKERS_Bakery_Modern_Review','CSC_BAKERS_Bakery_Modern_2_Review'):
  source=SRC/(name+'.blend');folder=O/'masters'/name;folder.mkdir(exist_ok=True);shutil.copy2(source,folder/'before.blend');shutil.copytree(SRC/'textures',folder/'textures',dirs_exist_ok=True);shutil.copy2(O/'textures'/(EID+'.png'),folder/'textures'/(EID+'.png'))
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
  scene=bpy.data.scenes['Export'];before={ob.name:signature(ob) for ob in scene.objects if ob.type=='MESH'};faces=0
  for ob in scene.objects:
   if ob.type!='MESH' or ob.get('module')!='Oven':continue
   ob.data=ob.data.copy()
   for poly in ob.data.polygons:
    uv=[ob.data.uv_layers[0].data[k].uv for k in poly.loop_indices];u=sum(p.x for p in uv)/len(uv);v=sum(p.y for p in uv)/len(uv);slot=int(u*8)+8*int((1-v)*8)
    if slot!=26:continue
    faces+=1
    for k in poly.loop_indices:ob.data.uv_layers[2].data[k].uv=ob.data.uv_layers[0].data[k].uv
  assert faces==1,(name,faces);assert all(signature(scene.objects[k])==v for k,v in before.items())
  for im in bpy.data.images:
   fn=im.filepath.replace('\\','/').split('/')[-1]
   if (folder/'textures'/fn).is_file():
    if im.packed_file:im.unpack(method='REMOVE')
    im.filepath='//textures/'+fn
  path=folder/(name+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
  val=validate_current_scene();dump(folder/'validation.json',val);assert val['automated_pass']
  rows.append({'source':str(source),'before':sha(source),'prepared':str(path),'UV3_faces':faces,'other_mesh_data_unchanged':True})
  if name==ID:
   bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();model={'asset_id':ID,'kind':'prop','meshes':[dec.merge_meshes(ID,[dec.decode_mesh(ob,ob.matrix_world) for ob in bpy.context.scene.objects if ob.type=='MESH'])]}
   for mesh in model['meshes']:
    for mat in mesh['materials']:mat['external']='CSC_Props_Modern_01'
   dump(O/'models'/(ID+'.json'),model)
 dump(O/'authoring.json',rows);dump(O/'masters.json',[{'id':ID,'blend':rows[0]['prepared']}]);print('OVEN_UV3_READY',flush=True)
def stage():
 sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'));import modular_v9_native as n
 D=O/'staged';prior=Path.home()/'Desktop/Codex/modern-interior-lighting-20261028/staged'
 # Rebuild the already verified dependency closure from CURRENT runtime files,
 # including the user's most recent placements; never restore old stage bytes.
 for p in prior.rglob('*'):
  q=MOD/p.relative_to(prior)
  if p.is_file() and q.exists():dest=D/p.relative_to(prior);dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(q,dest)
 shutil.copy2(O/'native'/(ID+'.fgx'),D/'Geometries'/(ID+'.fgx'))
 result=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-srgb','-o',str(D/'Textures'),str(O/'textures'/(EID+'.png'))],capture_output=True,text=True);(O/'texture-convert.log').write_text(result.stdout+result.stderr);assert result.returncode==0
 n.exp.validate_dds(D/'Textures'/(EID+'.dds'),{'slot':'E','size':[256,256],'format':'R8G8B8A8_UNORM'})
 r=n.read(MOD/'Textures'/(EID+'.tex'))
 for tag,value in [('m_Width',256),('m_Height',256),('m_NumMipMaps',8)]:r.find(tag).text=str(value)
 n.save(D/'Textures'/(EID+'.tex'),r)
 exe,_=n.helper(O/'native-reader');old=O/'native/previous-oven.json';subprocess.run([str(exe),str(exe.parent),str(MOD/'Geometries'/(ID+'.fgx')),str(old)],cwd=exe.parent,capture_output=True,check=True)
 a=json.loads(old.read_text());b=json.loads((O/'native'/(ID+'.json')).read_text());changed=0
 for x,y in zip(a['meshes'],b['meshes']):
  assert x['triangles']==y['triangles'] and x['boneBindings']==y['boneBindings'] and len(x['vertices'])==len(y['vertices'])
  for v,w in zip(x['vertices'],y['vertices']):
   changed+=v['uv3']!=w['uv3']
   for k in v:
    if k!='uv3':assert max([abs(t-u) for t,u in zip(v[k],w[k])]+[0])<1e-5
 assert changed==4,changed
 # Inspect all native geometry directly used by assets with the shared prop material.
 cache=json.loads((Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json').read_text())['Dependencies'];geos=set()
 for key,deps in cache.items():
  if 'Civ Supply Chains/Materials/CSC_Props_Modern_01.mtl' in deps:
   geos.update(p for p in deps if p.endswith('.geo') and p.startswith('Civ Supply Chains/'))
 audit=[]
 for rel in sorted(geos):
  geo=ROOT/rel;native=MOD/'Geometries'/(geo.stem+'.fgx')
  if geo.stem==ID:continue
  target=O/'native-audit'/(geo.stem+'.json');target.parent.mkdir(exist_ok=True);subprocess.run([str(exe),str(exe.parent),str(native),str(target)],cwd=exe.parent,capture_output=True,check=True)
  raw=json.loads(target.read_text());hits=0
  for mesh in raw['meshes']:
   for vertex in mesh['vertices']:
    u,v=vertex['uv3'];hits+=.25<=u<=.375 and .5<=v<=.625
  assert hits==0,('Other geometry samples reserved E cell26',geo,hits)
  audit.append(geo.stem)
 dump(O/'staging-validation.json',{'passed':True,'UV3_changed_vertices':changed,'all_other_native_fields_identical':True,'other_geometry_clear_of_E_cell26':audit,'publish_files':['Geometries/'+ID+'.fgx','Textures/'+EID+'.dds','Textures/'+EID+'.tex']});print('STAGED_AND_AUDITED',len(audit),flush=True)
def review():
 import interior_lighting_review as r
 r.O=O;r.SPECS=['after-day','after-night'];r.prepare()
def publish():
 sys.path.insert(0,str(ROOT/'project/tools/art/modern_windmill'));import modular_v9_native as n
 checks=json.loads((O/'staging-validation.json').read_text());assert checks['passed'];cook=json.loads((O/'cook-check/result.json').read_text());log=(O/'cook-check/stdout.log').read_text(errors='replace').replace('\x00','');assert cook['exit_code']==0 and cook['blps'] and 'ERRORS!!' not in log
 assert (O/'review/after-night/render.png').exists()
 base=json.loads((O/'baseline.json').read_text());authors=json.loads((O/'authoring.json').read_text());allocation=json.loads((O/'allocation.json').read_text())
 assert sha(LIB/'Current/textures/CSC_Props_Modern_01_B.png')==allocation['source_B_hash']
 assert sha(LIB/'Current/textures'/(EID+'.png'))==sha(O/'sources'/('Before_'+EID+'.png'))
 for row in authors:assert sha(row['source'])==row['before'],('New source save',row['source'])
 for rel in checks['publish_files']:assert sha(MOD/rel)==base[rel],('New runtime edit',rel)
 cur=LIB/'Current';release='2026-10-28_Modern_r008';snap=LIB/'Releases'/release;assert not snap.exists();payload={}
 for p in cur.rglob('*'):
  if p.is_file():payload[snap/p.relative_to(cur)]=p.read_bytes()
 manifest=json.loads((cur/'library.json').read_text());manifest.update(previous_release=manifest['release'],release=release,status='Shared256 emissive atlas; two warm oven cavities in cell26, other props dark');manifest['maps'][EID+'.png']=sha(O/'textures'/(EID+'.png'))
 plan=json.loads((cur/'atlas-plan.json').read_text());plan['emissive']=allocation
 updates={'library.json':json.dumps(manifest,indent=2).encode(),'atlas-plan.json':json.dumps(plan,indent=2).encode(),'textures/'+EID+'.png':(O/'textures'/(EID+'.png')).read_bytes(),'sources/published-registered/'+EID+'.png':(O/'textures'/(EID+'.png')).read_bytes()}
 for name in ('Oven_Window_E_Registered.png','Oven_Window_Mask.png'):updates['sources/oven-emissive/'+name]=(O/'sources'/name).read_bytes()
 updates['sources/oven-emissive/allocation.json']=(O/'allocation.json').read_bytes()
 for rel,data in updates.items():payload[cur/rel]=data;payload[snap/rel]=data
 payload[LIB/'CURRENT.json']=json.dumps({'release':release,'current':'Current','snapshot':'Releases/'+release,'manifest':'Current/library.json'},indent=2).encode()
 for row in authors:payload[Path(row['source'])]=Path(row['prepared']).read_bytes()
 payload[SRC/'textures'/(EID+'.png')]=(O/'textures'/(EID+'.png')).read_bytes();payload[SRC/(ID+'.cn6')]=(O/'native'/(ID+'.cn6')).read_bytes()
 for rel in checks['publish_files']:payload[MOD/rel]=(O/'staged'/rel).read_bytes()
 backup=O/'publication-backup';backup.mkdir(exist_ok=True);records=[]
 for i,(p,data) in enumerate(payload.items()):
  row={'destination':str(p),'before':sha(p) if p.exists() else None,'after':hashlib.sha256(data).hexdigest()}
  if p.exists():q=backup/f'{i:03}-{p.name}';shutil.copy2(p,q);row['backup']=str(q)
  records.append(row)
 dump(backup/'manifest.json',records)
 for row,(p,data) in zip(records,payload.items()):
  assert (sha(p) if p.exists() else None)==row['before'],('Concurrent publication edit',p)
  p.parent.mkdir(parents=True,exist_ok=True);tmp=p.with_name(p.name+'.oven-E-tmp');tmp.write_bytes(data);os.replace(tmp,p)
 dump(O/'publication-report.json',{'installed':True,'files':records,'release':release,'AST_geometry_shape_AO_unchanged':True,'game_deployment':False})
 n.cache(O)
 unchanged={rel:sha(MOD/rel)==value for rel,value in base.items() if rel not in checks['publish_files']};assert all(unchanged.values()),[k for k,v in unchanged.items() if not v]
 assert all(sha(r['destination'])==r['after'] for r in records)
 dump(O/'final-verification.json',{'passed':True,'only_three_runtime_files_changed':checks['publish_files'],'all_assemblies_and_placements_preserved':True,'other_props_dark_geometry_checks':checks['other_geometry_clear_of_E_cell26'],'master_validation':'passed','native_cook':'passed','engine_night_brightness':'not yet reviewed in engine'})
 print('PUBLISHED_OVEN_E',release,flush=True)
def render():
 sys.path.insert(0,str(Path(__file__).parent))
 import interior_lighting_review as r
 r.O=O;r.SPECS=['after-day','after-night'];r.render()
if __name__=='__main__':(render() if 'render' in sys.argv else author()) if '--' in sys.argv else globals()[sys.argv[1]]()
