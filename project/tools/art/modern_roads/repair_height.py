"""Repair road height RGB/coverage alpha; preserve layout, paint and AE assemblies."""
from pathlib import Path
import sys,json,shutil,hashlib,struct,xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(Path(__file__).parent))
D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
A=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout';O=A/'height-channel-repair-20261029';STAGE=O/'staged';MOD=ROOT/'Civ Supply Chains'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2))
def mips(p):
 import numpy as np
 raw=p.read_bytes();h,w=struct.unpack_from('<II',raw,12);count=struct.unpack_from('<I',raw,28)[0]
 if raw[84:88]==b'DX10':
  assert struct.unpack_from('<I',raw,128)[0] in (28,29);offset=148;shifts=[0,8,16,24]
 else:
  assert struct.unpack_from('<I',raw,88)[0]==32;offset=128
  masks=struct.unpack_from('<4I',raw,92);shifts=[(n&-n).bit_length()-1 for n in masks]
 result=[]
 for _ in range(count):
  pixels=np.frombuffer(raw,dtype='<u4',count=w*h,offset=offset).reshape(h,w)
  result.append(np.stack([((pixels>>s)&255).astype(np.uint8) for s in shifts],axis=2))
  offset+=w*h*4;w=max(1,w//2);h=max(1,h//2)
 assert offset==len(raw)
 return result

def prepare():
 import integrate as i
 import numpy as np
 from PIL import Image,ImageFilter,ImageDraw,ImageFont
 assert not (O/'baseline.json').exists(),'Do not overwrite an existing repair baseline'
 O.mkdir(parents=True,exist_ok=True)
 baseline={str(p):sha(p) for p in D.rglob('*') if p.is_file()}
 for folder in ('Assets','Geometries','Materials','Textures','ArtDefs','XLPs'):
  for p in (MOD/folder).glob('*'):
   if p.is_file():baseline[str(p)]=sha(p)
 dump(O/'baseline.json',baseline)
 for p in list(D.rglob('*.blend'))+[D/'atlas-layout.json']+list((D/'textures').glob('*H.png'))+list((D/'textures/native').glob('*H.dds')):
  dst=O/'before/source'/p.relative_to(D);dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
 for folder in ('Assets','Geometries','Materials','Textures'):(STAGE/folder).mkdir(parents=True,exist_ok=True)
 for f in (A/'layout-variants-20261029/staged/Assets').glob('*.ast'):
  shutil.copy2(f,STAGE/'Assets'/f.name)
 for folder,pattern in [('Geometries','CSC_ALL_Modern_Base_0*Road_Decals.*'),('Materials','CSC_Roads_*.mtl'),('Textures','CSC_Roads_*')]:
  for p in (MOD/folder).glob(pattern):shutil.copy2(p,STAGE/folder/p.name)
 # Current B artwork is authoritative, including any human paint changes.
 cells=json.loads((D/'atlas-layout.json').read_text())['cells'];report=[]
 for era in ('Industrial','Modern'):
  name='CSC_Roads_'+era+'_01';b=np.asarray(Image.open(D/'textures'/(name+'_B.png')).convert('RGBA'))
  bdds=mips(MOD/'Textures'/(name+'_B.dds'))
  assert np.max(np.abs(b.astype(int)-bdds[0].astype(int)))<=1,'Unpublished base paint; reconcile before repair'
  old=np.asarray(Image.open(D/'textures'/(name+'_H.png')).convert('RGBA'))
  native_path=A.parent/'draft-02-industrial/textures'/('Decals_Parts_'+era+'_01_H.dds')
  native=np.asarray(Image.open(native_path).convert('RGBA'));crop=native[268:452,310:498,0]
  height=np.full((512,512),float(np.median(crop)))
  for key,cell in cells.items():
   x0,y0,x1,y1=cell['rect'];sx,sy=cell['size'];w=x1-x0;h=y1-y0
   x,y=np.meshgrid((np.arange(w)+.5)/w*sx-sx/2,sy/2-(np.arange(h)+.5)/h*sy)
   def wrap(v,n):
    z=np.mod(v,2*n);return np.clip(np.where(z<n,z,2*n-1-z).astype(int),0,n-1)
   sampled=crop[wrap(y+113,crop.shape[0]),wrap(x+97,crop.shape[1])].astype(float)
   if era=='Industrial':
    # Keep native stone centers; convert the already painted shoulder detail to
    # restrained RGB relief at the measured Firaxis scale (rather than alpha).
    clean=np.asarray(Image.open(A/'history/before-worn-shoulders/textures'/(name+'_B.png')).convert('RGBA'))[y0:y1,x0:x1,3]/255
    lum=np.asarray(Image.fromarray(b[y0:y1,x0:x1,:3]).convert('L')).astype(float)
    smooth=np.asarray(Image.fromarray(lum.astype('uint8')).filter(ImageFilter.GaussianBlur(1.2))).astype(float)
    fringe=np.clip(89+(lum-smooth)*.06,86,92)
    sampled=sampled*clean+fringe*(1-clean)
   # Same per-cell padding as the existing UV layout; coverage is never padded.
   height[y0-4:y1+4,x0-4:x1+4]=np.pad(sampled,((4,4),(4,4)),mode='edge')
  grey=np.rint(height).astype('uint8');fixed=np.dstack([grey,grey,grey,b[:,:,3]])
  target=O/'textures'/(name+'_H.png');target.parent.mkdir(exist_ok=True);Image.fromarray(fixed).save(target)
  i.run([ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-o',STAGE/'Textures',target],O/(name+'-convert.log'))
  decoded=mips(STAGE/'Textures'/(name+'_H.dds'));assert len(decoded)==10
  assert np.array_equal(decoded[0],fixed)
  diffs=[int(np.max(np.abs(a[:,:,3].astype(int)-c[:,:,3].astype(int)))) for a,c in zip(decoded,bdds)]
  assert max(diffs)<=1,(name,diffs)
  assert np.all(fixed[:,:,3][b[:,:,3]==0]==0)
  assert np.all(fixed[:,:,:3]>=84) and np.all(fixed[:,:,:3]<=95)
  row={'era':era,'native_height_crop_rgb_range':[int(crop.min()),int(crop.max())],
       'before_rgb_range':[int(old[:,:,:3].min()),int(old[:,:,:3].max())],
       'before_nonzero_height_coverage_outside_base':int(np.count_nonzero(old[:,:,3][b[:,:,3]==0])),
       'after_nonzero_height_coverage_outside_base':0,'after_rgb_range':[int(grey.min()),int(grey.max())],
       'height_coverage_matches_base_all_mips_max_errors':diffs,'native_reference':str(native_path),'native_reference_sha256':sha(native_path)}
  report.append(row)
  # Diagnostic explicitly shows the heightmap coverage, not a simulated game render.
  board=Image.new('RGB',(1024,570),(30,34,39));draw=ImageDraw.Draw(board);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',22)
  for col,(label,img) in enumerate([('Before: height coverage',old[:,:,3]),('Corrected: matches road coverage',fixed[:,:,3])]):
   board.paste(Image.fromarray(img).convert('RGB'),(col*512,50));draw.text((col*512+12,12),label,font=font,fill='white')
  board.save(O/(era+'_Height_Coverage.png'))
 # Update private cook metadata to the user's present folder; no assembly mutations.
 for p in (STAGE/'Textures').glob('*.tex'):
  r=i.n.read(p);i.n.text(r,'m_SourceFilePath',str(D/'textures'/(p.stem+'.png')));i.n.save(p,r)
 dump(O/'height-validation.json',report);print('HEIGHT_CHANNELS_AND_ALL_MIP_COVERAGE_PASS',report,flush=True)

def preview():
 import bpy
 sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 import decode_blend as dec
 def shape():
  result=[]
  for ob in bpy.data.scenes['Export'].objects:
   if ob.type=='MESH':
    m=dec.decode_mesh(ob,ob.matrix_world);result.append({'name':ob.name,'vertices':m['vertices'],'triangles':m['triangles'],'materials':[v['name'] for v in m['materials']]})
  return result
 baseline=json.loads((O/'baseline.json').read_text());reports=[]
 for p in sorted(D.rglob('*.blend')):
  assert sha(p)==baseline[str(p)],('Concurrent Blender edit',p)
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  before=shape();edited=0
  for mat in bpy.data.materials:
   if not mat.use_nodes or not mat.name.startswith('CSC_Roads_'):continue
   nt=mat.node_tree
   for node in nt.nodes:
    if node.type!='TEX_IMAGE' or not node.image or not node.image.name.startswith('CSC_Roads_') or '_H.' not in node.image.name:continue
    node.image.colorspace_settings.name='Non-Color'
    for link in list(nt.links):
     if link.from_node==node and link.to_node.type=='BUMP' and link.to_socket.name=='Height':
      bump=link.to_node;nt.links.remove(link);nt.links.new(node.outputs['Color'],bump.inputs['Height']);bump.inputs['Distance'].default_value=.5;edited+=1
  assert edited>0,p
  assert shape()==before
  bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(p),relative_remap=False)
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  assert shape()==before;v=validate_current_scene();assert v['automated_pass'],v['findings']
  reports.append({'source':str(p),'before_sha256':baseline[str(p)],'sha256':sha(p),'preview_height_uses_rgb':True,'geometry_UVs_material_ids_preserved':True,'automated_pass':True})
 dump(O/'saved-preview-validation.json',reports);print('PREVIEW_REPAIRED_WITHOUT_GEOMETRY_EDITS',len(reports),flush=True)

def publish():
 import integrate as i
 checks=json.loads((O/'height-validation.json').read_text());cook=json.loads((O/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
 baseline=json.loads((O/'baseline.json').read_text());files=[]
 for era in ('Industrial','Modern'):
  name='CSC_Roads_'+era+'_01_H'
  for src,dst in [(O/'textures'/(name+'.png'),D/'textures'/(name+'.png')),
                  (STAGE/'Textures'/(name+'.dds'),D/'textures/native'/(name+'.dds')),
                  (STAGE/'Textures'/(name+'.dds'),MOD/'Textures'/(name+'.dds'))]:
   assert sha(dst)==baseline[str(dst)],('Concurrent height edit',dst)
   shutil.copy2(src,dst);assert sha(src)==sha(dst);files.append({'destination':str(dst),'before':baseline[str(dst)],'after':sha(dst)})
 # The user organized the sources into CSC_ALL_Modern_Roads after our last move.
 old=D.parent
 for folder,pattern in [('Textures','CSC_Roads_*.tex'),('Geometries','CSC_Road_*.geo'),('Geometries','CSC_ALL_Modern_Base*Road_Decals.geo')]:
  for p in (MOD/folder).glob(pattern):
   raw=p.read_bytes();r=i.n.read(p);node=r.find('m_SourceFilePath');source=node.get('text');target=source
   if str(old) in source and str(D) not in source:target=source.replace(str(old),str(D),1)
   assert Path(target).is_file(),target
   if target!=source:
    b=O/'before/wrappers'/p.name;b.parent.mkdir(exist_ok=True);b.write_bytes(raw)
    p.write_bytes(raw.replace(source.encode(),target.encode()));files.append({'destination':str(p),'before':hashlib.sha256(raw).hexdigest(),'after':sha(p)})
 changed={r['destination'] for r in files}
 preview=json.loads((O/'saved-preview-validation.json').read_text());changed|={r['source'] for r in preview}
 external=[]
 for path,digest in baseline.items():
  if path in changed:continue
  if sha(path)!=digest:
   assert Path(path).parent==MOD/'Assets',('Unexpected concurrent change',path)
   external.append(path)
 dump(O/'publication-report.json',{'installed':True,'files':files,'all_base_colour_and_FOW_and_spec_preserved':True,
      'all_native_geometry_preserved':True,'AE_assemblies_written':False,'concurrent_user_AST_saves_preserved':external,
      'game_visual_verification':False})
 i.n.cache(O)
 # Re-open browser cache and check exact current map payloads, including all mips.
 cache=json.loads((Path.home()/'AppData/Roaming/AssetCloud/mod-Civ Supply Chains-asset-deps.json').read_text(encoding='utf-8-sig'))
 indexed={r['Filename'].replace('\\','/') for r in cache['Files']}
 for r in files:
  p=Path(r['destination']);assert sha(p)==r['after']
  if p.is_relative_to(MOD):assert p.relative_to(ROOT).as_posix() in indexed
 dump(O/'final-verification.json',{'height_channels_and_coverage':checks,'saved_preview_files':len(preview),'installed_and_indexed':True,'native_geometry_and_AE_assembly_preserved':True,'cook_passed':True,'live_game_visual_check_pending':True})
 print('HEIGHT_REPAIR_INSTALLED_AND_VERIFIED',flush=True)

def maintain():
 # Keep active authoring inputs consistent with the user's folder and the
 # verified preview-only saves; preserve the earlier receipts in this repair.
 previews={Path(r['source']).stem:r for r in json.loads((O/'saved-preview-validation.json').read_text())}
 old=D.parent
 def remap(x):
  if isinstance(x,str):
   if str(old) in x and str(D) not in x:return x.replace(str(old),str(D),1)
   if old.as_posix() in x and D.as_posix() not in x:return x.replace(old.as_posix(),D.as_posix(),1)
   return x
  if isinstance(x,list):return [remap(v) for v in x]
  if isinstance(x,dict):return {k:remap(v) for k,v in x.items()}
  return x
 active=[A/'masters.json',A/'delivery-validation.json',A/'combined-layout-20261029/model.json',A/'combined-layout-20261029/saved-validation.json',A/'layout-variants-20261029/saved-validation.json']
 active+=list((A/'models').glob('*.json'))+list((A/'layout-variants-20261029/models').glob('*.json'))
 for p in active:
  data=remap(json.loads(p.read_text()))
  if p==A/'delivery-validation.json':
   for row in data['models']:row['source_sha256']=previews[row['id']]['sha256']
   data['latest_height_repair']=str(O/'final-verification.json')
  elif p.name=='saved-validation.json':
   for row in data if isinstance(data,list) else [data]:
    name=Path(row['source']).stem;row['sha256']=previews[name]['sha256']
  backup=O/'before/active-inputs'/p.relative_to(A);backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup);dump(p,data)
 manifest=D/'atlas-layout.json';data=json.loads(manifest.read_text());data['height_encoding']={'RGB':'linear grayscale relief; Industrial86-95, Modern84-90','alpha':'exact base-colour coverage, verified all ten mip levels','repair_evidence':str(O/'final-verification.json')};dump(manifest,data)
 for p in Path(__file__).parent.glob('*.py'):
  if p.name in ('repair_height.py','relocate.py'):continue
  text=p.read_text();updated=text.replace("Desktop/Working Files/3D Art/Decals'","Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'")
  if updated!=text:p.write_text(updated)
 print('ACTIVE_SOURCE_INPUTS_AND_HEIGHT_CONTRACT_UPDATED',flush=True)

if __name__=='__main__':
 mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else sys.argv[1];globals()[mode]()
