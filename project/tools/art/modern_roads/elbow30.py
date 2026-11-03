"""Bake a reusable 30-degree bend from existing painted road surfaces."""
from pathlib import Path
import sys,json,math,shutil,hashlib
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(Path(__file__).parent))
import raise_tarmac as z
D=z.D;A=z.A;MOD=z.MOD;O=A/'vanilla-shoulder-calibration-20261029';RECT=[400,184,504,240];SIZE=[42,26]
sha=z.sha;dump=z.dump

def prepare():
 import numpy as np
 from PIL import Image
 import integrate as i
 import repair_height as h
 z.O=O;z.prepare()
 for p in (D/'textures').rglob('*'):
  if p.is_file():q=O/'before/source'/p.relative_to(D);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 manifest=json.loads((D/'atlas-layout.json').read_text());assert 'elbow30' not in manifest['cells']
 for name,cell in manifest['cells'].items():
  a,b,c,d=cell['rect'];assert c+4<=RECT[0] or a-4>=RECT[2] or d+4<=RECT[1] or b-4>=RECT[3],name
 x0,y0,x1,y1=RECT;w=x1-x0;hh=y1-y0
 x,y=np.meshgrid((np.arange(w)+.5)/w*SIZE[0]-SIZE[0]/2,SIZE[1]/2-(np.arange(hh)+.5)/hh*SIZE[1]);radius=np.hypot(x,y+60);theta=np.arctan2(x,y+60);arc=theta*60;cross=radius-60
 # Inverse UV bake: original straight paint/coverage on a 15-unit carriageway.
 s=15/26;cell=manifest['cells']['straight'];a,b,c,d=cell['rect'];sx,sy=cell['size']
 uu=(arc/sx+.5);vv=.5-cross/s/sy;xx=a+.5+uu*(c-a-1)-.5;yy=b+.5+vv*(d-b-1)-.5
 valid=(np.abs(theta)<=math.radians(15))&(vv>=0)&(vv<=1)
 ix=np.clip(xx, a,c-1.00001);iy=np.clip(yy,b,d-1.00001);ix0=ix.astype(int);iy0=iy.astype(int);fx=(ix-ix0)[:,:,None];fy=(iy-iy0)[:,:,None]
 (O/'staged/Textures').mkdir(parents=True,exist_ok=True);rows=[]
 for era in ['Industrial','Modern']:
  outputs={}
  for channel in ['B','FOW','H']:
   path=D/'textures'/f'CSC_Roads_{era}_01_{channel}.png';old=np.array(Image.open(path).convert('RGBA'));assert old[y0:y1,x0:x1,3].max()==0,(era,channel,'occupied')
   p=old.astype(float);chunk=(p[iy0,ix0]*(1-fx)+p[iy0,ix0+1]*fx)*(1-fy)+(p[iy0+1,ix0]*(1-fx)+p[iy0+1,ix0+1]*fx)*fy
   chunk[:,:,3]*=valid;new=old.copy();new[y0:y1,x0:x1]=np.rint(chunk).clip(0,255).astype('uint8');outputs[channel]=new
  # Technical coverage must agree across B/H/FOW, including filtering.
  for ch in ['H','FOW']:outputs[ch][y0:y1,x0:x1,3]=outputs['B'][y0:y1,x0:x1,3]
  for ch,new in outputs.items():
   path=D/'textures'/f'CSC_Roads_{era}_01_{ch}.png';old=np.array(Image.open(path).convert('RGBA'));mask=np.ones((512,512),bool);mask[y0:y1,x0:x1]=False;assert np.array_equal(old[mask],new[mask])
   Image.fromarray(new).save(path)
   args=[ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-o',O/'staged/Textures']
   if ch in ['B','FOW']:args+=['-srgb']
   i.run(args+[path],O/(path.stem+'-convert.log'))
   rows.append({'source':str(path),'sha256':sha(path),'outside_new_cell_unchanged':True})
  bm=h.mips(O/'staged/Textures'/f'CSC_Roads_{era}_01_B.dds');hm=h.mips(O/'staged/Textures'/f'CSC_Roads_{era}_01_H.dds');assert len(bm)==len(hm)==10
  assert all(np.max(np.abs(x[:,:,3].astype(int)-y[:,:,3].astype(int)))<=1 for x,y in zip(bm,hm))
 manifest['cells']['elbow30']={'rect':RECT,'size':SIZE,'turn_degrees':30,'centerline_radius':60,'main_road_width':15,'source':'Inverse-UV bake of existing straight B/FOW/H paint; no new material paint','shoulders':'Current CSC shoulder profile; measured wider vanilla target recorded separately'}
 dump(D/'atlas-layout.json',manifest);dump(O/'texture-validation.json',rows);print('ELBOW_BAKE_PASS: six maps; existing atlas pixels unchanged',flush=True)

def build():
 import bpy
 sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
 import decode_blend as dec
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 reports=[]
 for era in ['Industrial','Modern']:
  name='CSC_Road_Elbow30_'+era;target=D/'modules'/(name+'.blend');assert not target.exists()
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(D/'modules'/('CSC_Road_Connector_'+era+'.blend')),load_ui=False,use_scripts=False)
  exp=bpy.data.scenes['Export'];ob=next(o for o in exp.objects if o.type=='MESH');me=ob.data
  linked=[o for o in bpy.data.objects if o.type=='MESH' and o.data==me];me.clear_geometry();me.from_pydata([(-21,-13,0),(21,-13,0),(21,13,0),(-21,13,0)],[],[(0,1,2,3)]);me.update()
  while me.uv_layers:me.uv_layers.remove(me.uv_layers[0])
  a,b,c,d=RECT;uv=[((a+.5)/512,1-(d-.5)/512),((c-.5)/512,1-(d-.5)/512),((c-.5)/512,1-(b+.5)/512),((a+.5)/512,1-(b+.5)/512)]
  for ch in ['UV1','UV2','UV3']:
   layer=me.uv_layers.new(name=ch)
   for li in me.loops:layer.data[li.index].uv=uv[li.vertex_index]
  for obj in linked:
   obj.name=obj.name.replace('Connector','Elbow30');vg=obj.vertex_groups.get('Bone') or obj.vertex_groups.new(name='Bone');vg.add([0,1,2,3],1,'REPLACE')
  ob.name='CSC_Projection_Elbow30_'+era
  for scene in bpy.data.scenes:
   scene['asset_id']=name
   if scene.camera:
    scene.camera.location=(0,0,100);scene.camera.rotation_euler=(0,0,0);scene.camera.data.type='ORTHO';scene.camera.data.ortho_scale=65;scene.render.resolution_x=700;scene.render.resolution_y=500
  for img in bpy.data.images:
   if img.source=='FILE':img.filepath='//../textures/'+Path(bpy.path.abspath(img.filepath)).name
  t=bpy.data.texts.get('START HERE');t.clear();t.write('Reusable 30-degree elbow. Radius60, nominal carriageway15, matching Industrial/Modern UV cell. Tangents differ by30 degrees. Endpoints approximately (+/-15.53,-2.04). Rotate/translate in AE; uniform scale only. Existing atlas paint reused. Stone Z0 / tarmac Z1.\n')
  bpy.context.window.scene=bpy.data.scenes['Review'];bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(target),relative_remap=False)
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False,use_scripts=False)
  bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();ob=next(o for o in bpy.context.scene.objects if o.type=='MESH');m=dec.decode_mesh(ob,ob.matrix_world);m['name']=name
  for mat in m['materials']:mat['external']=mat['name']
  check=validate_current_scene();assert check['automated_pass'],check['findings'];dump(O/'models'/(name+'.json'),{'asset_id':name,'kind':'decal','meshes':[m]});reports.append({'id':name,'source':str(target),'sha256':sha(target),'automated_pass':True})
 dump(O/'saved-validation.json',reports);print('ELBOW_MASTERS_PASS',flush=True)

def stage():
 import integrate as i
 n=i.n;stage=O/'staged';reader,_=n.helper(O/'native-reader');converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe';checks=[]
 for folder in ['Assets','Geometries','Materials','Textures','CN6']:(stage/folder).mkdir(parents=True,exist_ok=True)
 for folder,pattern in [('Materials','CSC_Roads_*.mtl'),('Textures','CSC_Roads_*')]:
  for p in (MOD/folder).glob(pattern):
   if not (stage/folder/p.name).exists():shutil.copy2(p,stage/folder/p.name)
 for row in json.loads((O/'saved-validation.json').read_text()):
  name=row['id'];m=json.loads((O/'models'/(name+'.json')).read_text());cn6=stage/'CN6'/(name+'.cn6');fgx=stage/'Geometries'/(name+'.fgx');n.exp.write_cn6(cn6,m);i.run([converter,cn6,fgx,'2'],O/(name+'-convert.log'),converter.parent);i.run([reader,reader.parent,fgx,O/(name+'-native.json')],O/(name+'-read.log'),reader.parent)
  a=m['meshes'][0];b=json.loads((O/(name+'-native.json')).read_text())['meshes'][0];assert a['name']==b['name'] and a['triangles']==b['triangles'];assert b['boneBindings']==['Bone'] and b['materialName']==a['materials'][0]['name'];error=0
  for v,w in zip(a['vertices'],b['vertices']):
   vals=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'];error=max(error,max(abs(x-y) for x,y in zip(v,vals)));assert w['boneIndices']==[0]*8 and w['boneWeights']==[255,0,0,0,0,0,0,0]
  assert error<1e-4
  g=n.exp.geometry(m,n.read(MOD/'Geometries/CSC_Road_Connector_Industrial.geo'));n.text(g,'m_SourceFilePath',row['source']);n.save(stage/'Geometries'/(name+'.geo'),g);n.save(stage/'Assets'/(name+'.ast'),n.fresh_asset(name,m,n.read(MOD/'Assets/CSC_BAKERS_Wind_Mill_Modern.ast')));checks.append({'id':name,'native_max_error':error})
 # Existing layout verifies that the atlas addition is compatible with current UVs.
 name='CSC_ALL_Modern_Base_05_Road_Decals'
 for suffix in ['.fgx','.geo']:shutil.copy2(MOD/'Geometries'/(name+suffix),stage/'Geometries'/(name+suffix))
 shutil.copy2(A/'vanilla-width-calibration-20261029/staged/Assets'/(name+'.ast'),stage/'Assets'/(name+'.ast'))
 dump(O/'staging-validation.json',checks);print('ELBOW_NATIVE_PASS',flush=True)

def publish():
 import integrate as i
 cook=json.loads((O/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps'];base=json.loads((O/'baseline.json').read_text());files=[]
 for row in json.loads((O/'saved-validation.json').read_text()):
  assert sha(row['source'])==row['sha256']
  for suffix in ['.fgx','.geo']:assert not (MOD/'Geometries'/(row['id']+suffix)).exists()
 for row in json.loads((O/'texture-validation.json').read_text()):
  assert sha(row['source'])==row['sha256'];p=MOD/'Textures'/(Path(row['source']).stem+'.dds');assert sha(p)==base[str(p)]
 for row in json.loads((O/'saved-validation.json').read_text()):
  for suffix in ['.fgx','.geo']:
   p=MOD/'Geometries'/(row['id']+suffix);shutil.copy2(O/'staged/Geometries'/p.name,p);files.append({'destination':str(p),'after':sha(p)})
  shutil.copy2(O/'staged/CN6'/(row['id']+'.cn6'),Path(row['source']).with_suffix('.cn6'))
 for row in json.loads((O/'texture-validation.json').read_text()):
  p=MOD/'Textures'/(Path(row['source']).stem+'.dds');backup=O/'before/Textures'/p.name;backup.parent.mkdir(exist_ok=True);shutil.copy2(p,backup);shutil.copy2(O/'staged/Textures'/p.name,p);shutil.copy2(p,D/'textures/native'/p.name);files.append({'destination':str(p),'before':base[str(p)],'after':sha(p)})
 for path,digest in base.items():
  if Path(path).parent in [MOD/'Assets',MOD/'ArtDefs',MOD/'XLPs',MOD/'Geometries']:assert sha(path)==digest,path
 dump(O/'publication-report.json',{'installed':True,'files':files,'existing_geometry_and_assemblies_unchanged':True,'existing_atlas_pixels_unchanged':True,'shoulder_width_change_applied':False});i.n.cache(O);i.OUT=O;i.verify()
 records=json.loads((A/'masters.json').read_text())
 for row in json.loads((O/'saved-validation.json').read_text()):
  records.append({'id':row['id'],'blend':row['source']});shutil.copy2(O/'models'/(row['id']+'.json'),A/'models'/(row['id']+'.json'));shutil.copy2(O/(row['id']+'-native.json'),A/'native'/(row['id']+'.json'))
 dump(A/'masters.json',records);print('ELBOW_INSTALLED',flush=True)

if __name__=='__main__':
 mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else sys.argv[1];globals()[mode]()
