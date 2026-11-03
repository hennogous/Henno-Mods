"""Compact window emissive, geometry-preserving UV3 update and selective native export."""
import sys,json,shutil,subprocess,math
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from modular_v9 import ROOT,ART,BASE,sha,dump
O=Path.home()/'Desktop/Codex/modern-normal-correction-20261027/emissive-r007';WATER='CSC_BAKERS_Water_Mill_Modern';LIB=ART/'Textures/CSC_Buildings_Modern';REL='2026-10-27_Modern_r007'
MOD=ROOT/'Civ Supply Chains'
DESTS={BASE:ART/'Level 1/modern/revision-04-painted-kit',WATER:ART/'BAKERS/Water Mill/modern/revision-02-painted-kit'}
def prepare():
 import numpy as np
 from PIL import Image,ImageFilter
 O.mkdir(exist_ok=True);shutil.copytree(LIB/'Current',O/'library',dirs_exist_ok=True)
 baseline={'sources':{str(DESTS[i]/(i+'.blend')):sha(DESTS[i]/(i+'.blend')) for i in (BASE,WATER)},'library':{str(p.relative_to(LIB/'Current')):sha(p) for p in (LIB/'Current').rglob('*') if p.is_file()},'runtime':{str(p.relative_to(MOD)):sha(p) for d in ('Assets','Geometries','Materials','Textures','ArtDefs','XLPs') for p in (MOD/d).iterdir() if p.is_file()}}
 dump(O/'baseline.json',baseline)
 Y,X=np.mgrid[:1024,:1024];im=np.zeros((1024,1024,3),float)
 # Glazing rectangles measured in the unchanged window patch (building cell7).
 for (x0,x1,y0,y1),rgb in zip([(32,60,29,61),(66,96,29,61),(32,60,66,99),(66,96,66,99)],[(205,140,60)]*4):
  d=np.minimum.reduce([X-(384+x0+.6),(384+x1-.6)-X,Y-(128+y0+.6),(128+y1-.6)-Y]);a=np.clip(d/1.5,0,1);a=a*a*(3-2*a);im+=a[:,:,None]*np.array(rgb)
 image=Image.fromarray(np.uint8(im)).resize((256,256),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.45));image.save(O/'library/textures/CSC_Atlas_Modern_E.png');image.save(O/'library/sources/registered_E.png')
 plan=json.loads((O/'library/atlas-plan.json').read_text());plan['building']['emissive']={'size':256,'layout':'Quarter atlas coordinates match UV1; only Stage2 cell7 glazing lit, all other regions black','UV3':'Upstairs windows (world minimum Z above 30) copy UV1; ground-floor windows and all other meshes use black (0.02,0.02)','panes':'All four panes equally warm; frame and stone surround black'};dump(O/'library/atlas-plan.json',plan);print('EMISSIVE_PREPARED')
def build():
 import bpy
 sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
 import decode_blend as dec
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 for ident in (BASE,WATER):
  with suspend_csc_repairs():
   source=DESTS[ident]/(ident+'.blend');bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False);scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;windows=[];dark_windows=[]
   fingerprint=lambda o:([list(v.co) for v in o.data.vertices],[list(p.vertices) for p in o.data.polygons],[list(d.uv) for d in o.data.uv_layers[0].data],[list(d.uv) for d in o.data.uv_layers[1].data],[list(r) for r in o.matrix_world])
   before={o.name:fingerprint(o) for o in scene.objects if o.type=='MESH'}
   for o in scene.objects:
    if o.type!='MESH':continue
    is_window='Window' in o.name and o.data.materials[0].name.startswith('CSC_BAKERS_Modern')
    window=is_window and min((o.matrix_world @ v.co).z for v in o.data.vertices)>30
    if is_window and not window:dark_windows.append(o.name)
    for i,d in enumerate(o.data.uv_layers[2].data):d.uv=o.data.uv_layers[0].data[i].uv if window else (.02,.02)
    if window:windows.append(o.name)
    assert before[o.name]==fingerprint(o),o.name
   folder=O/'masters'/ident;shutil.copytree(DESTS[ident]/'textures',folder/'textures',dirs_exist_ok=True);shutil.copy2(O/'library/textures/CSC_Atlas_Modern_E.png',folder/'textures/CSC_Atlas_Modern_E.png')
   for mat in {m for o in scene.objects if o.type=='MESH' for m in o.data.materials}:
    for n in mat.node_tree.nodes:
     if n.type=='TEX_IMAGE' and n.image and Path(n.image.filepath.replace('\\','/')).name=='CSC_Atlas_Modern_E.png':
      if n.image.packed_file:n.image.unpack(method='REMOVE')
      n.image.filepath='//textures/CSC_Atlas_Modern_E.png'
   bpy.context.window.scene=bpy.data.scenes['Review'];bpy.ops.wm.save_as_mainfile(filepath=str(folder/(ident+'.blend')),relative_remap=False);bpy.ops.wm.open_mainfile(filepath=str(folder/(ident+'.blend')),load_ui=False,use_scripts=False)
   report=validate_current_scene();assert report['automated_pass'];dump(folder/'validation.json',report)
   bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();groups={}
   for o in bpy.context.scene.objects:
    if o.type!='MESH':continue
    label=('SiloSideSupports' if o.get('optional_silo_side_support') else 'Shelter' if 'Shelter_' in o.name or 'Support_Foot_' in o.name else 'Building') if ident==BASE else ('Building' if o.data.materials[0].name.startswith('CSC_BAKERS_Modern') else 'Machinery')
    groups.setdefault(label,[]).append(dec.decode_mesh(o,o.matrix_world))
   assert len(windows)==5,(ident,windows)
   assert len(dark_windows)==(1 if ident==BASE else 0),(ident,dark_windows)
   (O/'models').mkdir(exist_ok=True);dump(O/'models'/(ident+'.json'),{'asset_id':ident,'kind':'building','meshes':[dec.merge_meshes(ident+'_'+k,v) for k,v in groups.items()]});dump(folder/'uv3-check.json',{'geometry_UV1_UV2_unchanged':True,'upstairs_lit':windows,'ground_floor_dark':dark_windows});print('UV3_UPDATED',ident,len(windows),flush=True)
def stage():
 from PIL import Image
 import modular_v9_native as n
 exp=n.exp;shutil.copytree(O.parent/'emissive/staged',O/'staged',dirs_exist_ok=True);dst=O/'staged'
 for directory in ('Assets','Geometries','Materials','Textures'):
  for p in (dst/directory).iterdir():
   if p.is_file() and (MOD/directory/p.name).is_file():shutil.copy2(MOD/directory/p.name,p)
 (dst/'CN6').mkdir(exist_ok=True);exe,_=n.helper(O/'native-reader');conv=ROOT/'project/tools/cn6libs/CN6ToFGX.exe';results=[]
 for ident in (BASE,WATER):
  model=json.loads((O/'models'/(ident+'.json')).read_text());cn6=dst/'CN6'/(ident+'.cn6');fgx=dst/'Geometries'/(ident+'.fgx');exp.write_cn6(cn6,model);n.save(dst/'Geometries'/(ident+'.geo'),exp.geometry(model,n.read(MOD/'Geometries'/(ident+'.geo'))))
  p=subprocess.run([str(conv),str(cn6),str(fgx),'2'],cwd=conv.parent,capture_output=True,text=True);assert p.returncode==0,p.stdout+p.stderr
  new=O/(ident+'-native.json');old=O/(ident+'-before.json')
  for source,target in ((fgx,new),(MOD/'Geometries'/(ident+'.fgx'),old)):subprocess.run([str(exe),str(exe.parent),str(source),str(target)],cwd=exe.parent,check=True,capture_output=True)
  a=json.loads(new.read_text());b=json.loads(old.read_text());bm={m['name']:m for m in b['meshes']};err=0
  for m,expected in zip(a['meshes'],model['meshes']):
   previous=bm[m['name']];assert m['triangles']==previous['triangles'] and len(m['vertices'])==len(previous['vertices']) and m['boneBindings']==previous['boneBindings']==['Bone']
   for v,w,e in zip(m['vertices'],previous['vertices'],expected['vertices']):
    for k in ('position','normal','tangent','binormal','uv','uv2','boneWeights','boneIndices'):assert v[k]==w[k],(ident,k)
    err=max(err,max(abs(x-y) for x,y in zip(v['uv3'],e[16:18])))
   assert err<1e-5,err
  results.append({'asset':ident,'all_except_UV3_exact_native_match':True,'UV3_max_error':err})
 p=O/'library/textures/CSC_Atlas_Modern_E.png';r=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-srgb','-o',str(dst/'Textures'),str(p)],capture_output=True,text=True);assert r.returncode==0
 exp.validate_dds(dst/'Textures/CSC_Atlas_Modern_E.dds',{'slot':'E','size':[256,256],'format':'R8G8B8A8_UNORM'})
 tex=n.read(MOD/'Textures/CSC_Atlas_Modern_E.tex');tex.find('m_Width').text=tex.find('m_Height').text='256';tex.find('m_NumMipMaps').text='8';n.save(dst/'Textures/CSC_Atlas_Modern_E.tex',tex)
 dump(O/'staging-validation.json',{'passed':True,'native':results,'publish_files':[f'Geometries/{i}.{e}' for i in (BASE,WATER) for e in ('fgx','geo')]+['Textures/CSC_Atlas_Modern_E.dds','Textures/CSC_Atlas_Modern_E.tex']});print('EMISSIVE_STAGED',results)
def publish():
 import modular_v9_native as native
 baseline=json.loads((O/'baseline.json').read_text());check=json.loads((O/'staging-validation.json').read_text());assert check['passed']
 assert json.loads((O/'visual-review.json').read_text())['reviewed']
 cook=json.loads((O/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
 log=(O/'cook-check/stdout.log').read_text(errors='replace').replace('\x00','');assert '(ERRORS!!)' not in log and 'I/O error' not in log
 for p,h in baseline['sources'].items():assert sha(p)==h,('Concurrent source edit',p)
 for p,h in baseline['runtime'].items():assert sha(MOD/p)==h,('Concurrent runtime edit',p)
 for p,h in baseline['library'].items():assert sha(LIB/'Current'/p)==h,('Concurrent library edit',p)
 assert not (LIB/'Releases'/REL).exists()
 root=O/'library';shutil.copy2(Path(__file__).with_name('rebuild_modern_atlases.py'),root/'scripts/rebuild_modern_atlases.py')
 for p in (root/'textures').iterdir():
  if p.name!='CSC_Atlas_Modern_E.png':assert sha(p)==sha(LIB/'Current/textures'/p.name)
 info=json.loads((root/'library.json').read_text());info.update(release=REL,status='Registered structural normals retained from r005; compact 256px warm window emissive with UV3-only model updates',source_sha256=sha(O/'masters'/BASE/(BASE+'.blend')),maps={p.name:sha(p) for p in (root/'textures').iterdir() if p.is_file()});dump(root/'library.json',info)
 shutil.copy2(Path(__file__),root/'sources/emissive-authoring.py');shutil.copy2(O/'visual-review.json',root/'sources/emissive-review.json')
 payload={}
 for p in root.rglob('*'):
  if p.is_file():
   for dst in (LIB/'Current',LIB/'Releases'/REL):payload[dst/p.relative_to(root)]=p
 pointer=O/'CURRENT.json';dump(pointer,{'release':REL,'current':'Current','snapshot':'Releases/'+REL,'manifest':'Current/library.json'});payload[LIB/'CURRENT.json']=pointer
 for ident,folder in DESTS.items():
  payload[folder/(ident+'.blend')]=O/'masters'/ident/(ident+'.blend')
  payload[folder/'textures/CSC_Atlas_Modern_E.png']=root/'textures/CSC_Atlas_Modern_E.png'
  payload[folder/(ident+'.cn6')]=O/'staged/CN6'/(ident+'.cn6')
  payload[folder/'emissive-uv3-check.json']=O/'masters'/ident/'uv3-check.json'
 for rel in check['publish_files']:payload[MOD/rel]=O/'staged'/rel
 backup=O/'publication-backup';backup.mkdir(exist_ok=True);rows=[]
 for i,(dst,p) in enumerate(payload.items()):
  row={'destination':str(dst),'source':str(p),'before':sha(dst) if dst.exists() else None}
  if dst.exists():q=backup/f'{i:04}-{dst.name}';shutil.copy2(dst,q);row['backup']=str(q)
  rows.append(row)
 dump(backup/'manifest.json',rows)
 for row,(dst,p) in zip(rows,payload.items()):
  assert (sha(dst) if dst.exists() else None)==row['before'];dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst);row['after']=sha(dst);assert row['after']==sha(p)
 allowed=set(check['publish_files'])
 for rel,h in baseline['runtime'].items():
  if Path(rel).as_posix() not in allowed:assert sha(MOD/rel)==h,rel
 cache=[str(MOD/'Assets'/(i+'.ast')) for i in (BASE,WATER,'CSC_BAKERS_Wind_Mill_Modern')]+[str(MOD/'Materials/CSC_BAKERS_Modern.mtl')]
 dump(O/'publication-report.json',{'installed':True,'files':rows,'runtime_changes':sorted(allowed),'geometry_UV1_UV2_B_AO_AST_unchanged':True,'cache_inputs':cache,'in_game_tested':False});native.cache(O);print('PUBLISHED_EMISSIVE',len(rows))

if __name__=='__main__':globals()[sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else sys.argv[1]]()
