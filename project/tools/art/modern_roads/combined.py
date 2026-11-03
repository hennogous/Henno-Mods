"""Combined visibility-editable road geometry, authored from the approved modules.

Run build in background Blender, then stage/publish/cache/verify with Python.
"""
from pathlib import Path
import sys,json,hashlib,shutil,copy

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT/'project/tools/art/modern_windmill'),str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
A=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout'
O=A/'combined-layout-20261029'
ID='CSC_ALL_Modern_Base_Road_Decals'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2))

def build():
 import bpy
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 import decode_blend as dec
 records=json.loads((A/'masters.json').read_text());approved={r['id']:r for r in json.loads((A/'delivery-validation.json').read_text())['models']}
 for r in records:assert sha(r['blend'])==approved[r['id']]['source_sha256'],r['id']
 path=D/(ID+'.blend');assert not path.exists(),'Do not regenerate a human-edited combined master'
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(D/'CSC_ALL_Modern_Roundabout_Kit.blend'),load_ui=False,use_scripts=False)
 exp=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];rig=next(o for o in exp.objects if o.type=='ARMATURE')
 # Keep the existing review ground/lights and the validated common static rig.
 for ob in list(bpy.data.objects):
  if ob.type=='MESH' and any(slot.material and slot.material.name.startswith('CSC_Roads_') for slot in ob.material_slots):bpy.data.objects.remove(ob,do_unlink=True)
 for scene in list(bpy.data.scenes):
  if scene not in (exp,review):bpy.data.scenes.remove(scene)
 ec=bpy.data.collections.new('EXPORT - all road visibility pieces');exp.collection.children.link(ec)
 rc=bpy.data.collections.new('REVIEW - road layout');review.collection.children.link(rc)
 first={'Roundabout','NW','NE','SE'}
 for row in records:
  source=row['id'].replace('CSC_Road_','CSC_Projection_')
  with bpy.data.libraries.load(row['blend'],link=False) as (src,dst):
   assert source in src.objects;dst.objects=[source]
  ob=dst.objects[0];world=ob.matrix_world.copy();ob.parent=rig;ob.matrix_world=world
  for mod in ob.modifiers:
   if mod.type=='ARMATURE':mod.object=rig
  ob.name=row['id'];ec.objects.link(ob)
  # Appending can suffix material identities: canonicalize using the native name.
  matname='CSC_Roads_'+('Industrial' if row['id'].endswith('_Industrial') else 'Modern')+'_01'
  canonical=bpy.data.materials.get(matname)
  if canonical is None:canonical=ob.data.materials[0];canonical.name=matname
  ob.data.materials.clear();ob.data.materials.append(canonical)
  preview=ob.copy();preview.name='Preview_'+row['id'];preview.location.z=0
  preview['review_only']=True;rc.objects.link(preview)
  if row['id'].endswith('_Modern'):
   preview.location.z=.04;preview.hide_render=row['id'].removeprefix('CSC_Road_').removesuffix('_Modern') not in first
  ob.hide_render=False;ob.hide_viewport=False
 for s in (exp,review):s['asset_id']=ID
 for image in bpy.data.images:
  if image.source=='FILE':image.filepath='//textures/'+Path(bpy.path.abspath(image.filepath)).name
 t=bpy.data.texts.get('START HERE') or bpy.data.texts.new('START HERE');t.clear();t.write('One DecalGeometry with fourteen separately named meshes: seven stone underlay and seven tarmac pieces. Export contains ALL pieces; toggle their visibility in AE to make district variants. Material groups use CSC_Roads_Industrial_01 or CSC_Roads_Modern_01. Keep all Industrial pieces visible; first overlay is Roundabout/NW/NE/SE Modern. Review shows this first-building proposal. Mesh coordinates include projection Z20. Add the combined geometry once at zero position/rotation and scale1. AE owns the variant assembly.\n')
 bpy.context.window.scene=review;bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
 with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 validation=validate_current_scene();assert validation['automated_pass'],validation['findings']
 meshes=[]
 bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update()
 for row in records:
  ob=bpy.data.scenes['Export'].objects[row['id']];m=dec.decode_mesh(ob,ob.matrix_world);m['name']=row['id']
  for mat in m['materials']:mat['external']=mat['name']
  previous=json.loads((A/'models'/(row['id']+'.json')).read_text())['meshes'][0]
  assert m['vertices']==previous['vertices'] and m['triangles']==previous['triangles'],row['id']
  assert m['materials'][0]['name']==previous['materials'][0]['name']
  meshes.append(m)
 assert len([ob for ob in bpy.data.scenes['Export'].objects if ob.type=='MESH'])==14
 dump(O/'model.json',{'asset_id':ID,'kind':'decal','meshes':meshes})
 dump(O/'saved-validation.json',{'automated_pass':True,'source':str(path),'sha256':sha(path),'module_geometry_uv_material_parity':True,'mesh_count':14,'counts':validation['counts']})
 print('COMBINED_MASTER_PASS: 14 separately named meshes; exact module parity',flush=True)

def stage():
 import integrate as i
 n=i.n;stage=O/'staged'
 for f in ('Geometries','Materials','Textures','Assets','CN6'):(stage/f).mkdir(parents=True,exist_ok=True)
 check=json.loads((O/'saved-validation.json').read_text());assert check['automated_pass'] and sha(check['source'])==check['sha256']
 m=json.loads((O/'model.json').read_text());cn6=stage/'CN6'/(ID+'.cn6');fgx=stage/'Geometries'/(ID+'.fgx')
 n.exp.write_cn6(cn6,m);converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe'
 i.run([converter,cn6,fgx,'2'],O/'convert.log',converter.parent)
 reader,_=n.helper(O/'native-reader');i.run([reader,reader.parent,fgx,O/'native.json'],O/'read.log',reader.parent)
 native=json.loads((O/'native.json').read_text());assert len(native['meshes'])==14
 error=0
 for a,b in zip(m['meshes'],native['meshes']):
  assert a['name']==b['name'] and a['triangles']==b['triangles'] and len(a['vertices'])==len(b['vertices'])
  assert b['boneBindings']==['Bone'] and b['materialName']==a['materials'][0]['name']
  for v,w in zip(a['vertices'],b['vertices']):
   values=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'];error=max(error,max(abs(x-y) for x,y in zip(v,values)))
   assert w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
 assert error<1e-4
 geo=n.exp.geometry(m,n.read(i.MOD/'Geometries/CSC_Level_1_S.geo'));n.text(geo,'m_SourceFilePath',check['source']);n.text(geo,'m_Description','Complete road layout: toggle individual Industrial/Modern meshes in Asset Editor')
 n.save(stage/'Geometries'/(ID+'.geo'),geo)
 assert len(geo.findall('m_Meshes/Element'))==14
 ast=n.fresh_asset(ID,m,n.read(i.MOD/'Assets/CSC_BAKERS_Wind_Mill_Modern.ast'))
 # Native test asset only. Material/visibility state rows are independent per mesh.
 rows=ast.findall(n.exp.MODELS+'/Element/m_GroupStates/Element')
 assert len({n.exp.txt(r,'m_MeshName') for r in rows})==14
 n.save(stage/'Assets'/(ID+'.ast'),ast)
 dependencies=[]
 for era in ('Industrial','Modern'):
  mat='CSC_Roads_'+era+'_01'
  for folder,fn in [('Materials',mat+'.mtl')]+[( 'Textures',mat+'_'+ch+ext) for ch in ('B','H','FOW','S') for ext in ('.dds','.tex')]:
   p=i.MOD/folder/fn;shutil.copy2(p,stage/folder/fn);dependencies.append({'path':str(p),'sha256':sha(p)})
 shutil.copy2(cn6,D/cn6.name)
 dump(O/'staging-validation.json',{'passed':True,'native_max_error':error,'meshes':14,'independent_visibility_material_rows':True,'dependencies':dependencies})
 print('NATIVE_COMBINED_PASS: 14 meshes and material/visibility rows',flush=True)

def publish():
 import integrate as i
 check=json.loads((O/'staging-validation.json').read_text());cook=json.loads((O/'cook-check/result.json').read_text());saved=json.loads((O/'saved-validation.json').read_text())
 assert check['passed'] and cook['exit_code']==0 and cook['blps'] and sha(saved['source'])==saved['sha256']
 assert all(sha(r['path'])==r['sha256'] for r in check['dependencies'])
 files=[]
 for ext in ('.geo','.fgx'):
  src=O/'staged/Geometries'/(ID+ext);dst=i.MOD/'Geometries'/src.name;assert not dst.exists(),dst
  shutil.copy2(src,dst);assert sha(src)==sha(dst);files.append({'destination':str(dst),'after':sha(dst),'before':None})
 dump(O/'publication-report.json',{'installed':True,'files':files,'existing_assemblies_modified':False})
 i.n.cache(O)
 old=i.OUT;i.OUT=O;i.verify();i.OUT=old

if __name__=='__main__':
 mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else sys.argv[1]
 globals()[mode]()
