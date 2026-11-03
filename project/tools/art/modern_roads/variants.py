"""Classical-style complete road geometries for the agreed development variants."""
from pathlib import Path
import sys,json,copy,shutil,hashlib,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(Path(__file__).parent),str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
import combined as c
D=c.D;A=c.A;O=A/'layout-variants-20261029';MOD=ROOT/'Civ Supply Chains'
FIRST=['Roundabout','NW','NE','SE']
PLAN=[('01','All stone',[]),('02','First building',FIRST),
      ('03','East destination',FIRST+['E']),
      ('04','Southwest destination',FIRST+['SW','Connector']),
      ('05','All routes',FIRST+['E','SW','Connector'])]
def ident(number):return 'CSC_ALL_Modern_Base_'+number+'_Road_Decals'
def read(p):return ET.fromstring(p.read_text(encoding='utf-8-sig').replace('AssetObjects:','AssetObjects..'))
def txt(r,k):
 n=r.find(k);return n.get('text','') if n is not None else ''

def inspect():
 rows=[]
 for number in range(1,6):
  name=f'CSC_ALL_Classical_Base_{number:02}_Road_Decals';gp=MOD/'Geometries'/(name+'.geo');ap=MOD/'Assets'/f'CSC_BAKERS_Classical_Base_{number:02}.ast'
  g=read(gp);a=read(ap);m=next(x for x in a.findall('m_GeometrySet/m_ModelInstances/Element') if txt(x,'m_GeoName')==name)
  states={};materials={}
  for r in m.findall('m_GroupStates/Element'):
   state=txt(r,'m_StateName');vals={txt(v,'m_ParamName'):v for v in r.findall('m_Values/m_Values/Element')};visible=vals['Visible'].findtext('m_bValue')=='true'
   states.setdefault(state,{'visible':[],'hidden':[]})['visible' if visible else 'hidden'].append(txt(r,'m_MeshName'))
   if state=='Worked':materials[txt(r,'m_MeshName')]=txt(vals['Material'],'m_ObjectName')
  meshes=[txt(x,'m_Name') for x in g.findall('m_Meshes/Element')]
  assert set(states['Worked']['visible'])==set(meshes) and not states['Worked']['hidden']
  rows.append({'id':name,'geometry':str(gp),'geometry_sha256':c.sha(gp),'asset':str(ap),'asset_sha256':c.sha(ap),'mesh_count':len(meshes),'materials':materials,'states':states})
 c.dump(O/'classical-inspection.json',rows)
 print('CLASSICAL_INSPECTED: mesh counts', [r['mesh_count'] for r in rows],'; all included meshes visible in Worked')

def build():
 import bpy
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 import decode_blend as dec
 source=D/(c.ID+'.blend');check=json.loads((c.O/'saved-validation.json').read_text());assert c.sha(source)==check['sha256']
 original={m['name']:m for m in json.loads((c.O/'model.json').read_text())['meshes']};reports=[]
 for number,title,modern in PLAN:
  name=ident(number);path=D/(name+'.blend');assert not path.exists(),path
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
  selected={k for k in original if k.endswith('_Industrial') or k.removeprefix('CSC_Road_').removesuffix('_Modern') in modern}
  for ob in list(bpy.data.objects):
   key=ob.name.removeprefix('Preview_')
   if key in original:
    if key not in selected:bpy.data.objects.remove(ob,do_unlink=True)
    else:ob.hide_render=False;ob.hide_viewport=False
  for s in (bpy.data.scenes['Review'],bpy.data.scenes['Export']):s['asset_id']=name
  t=bpy.data.texts['START HERE'];t.clear();t.write(title+'. Complete variant geometry: all seven stone pieces plus Modern '+(', '.join(modern) or 'none')+'. Only the included pieces export; all are intended visible. Add once at origin/rotation0/scale1 with the existing stone/tarmac materials. 03 and 04 are independent destination variants, not sequential upgrades. Z20 projection already authored.\n')
  bpy.context.window.scene=bpy.data.scenes['Review'];bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
  validation=validate_current_scene();assert validation['automated_pass'],validation['findings']
  meshes=[]
  bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update()
  for ob in bpy.data.scenes['Export'].objects:
   if ob.type!='MESH':continue
   m=dec.decode_mesh(ob,ob.matrix_world);m['name']=ob.name
   for mat in m['materials']:mat['external']=mat['name']
   previous=original[ob.name];assert m['vertices']==previous['vertices'] and m['triangles']==previous['triangles']
   assert m['materials'][0]['name']==previous['materials'][0]['name'];meshes.append(m)
  assert {m['name'] for m in meshes}==selected
  # Stone first, asphalt second, in the same approved module order.
  meshes.sort(key=lambda m:(m['name'].endswith('_Modern'),list(original).index(m['name'])))
  c.dump(O/'models'/(name+'.json'),{'asset_id':name,'kind':'decal','meshes':meshes})
  reports.append({'id':name,'title':title,'modern':modern,'source':str(path),'sha256':c.sha(path),'meshes':len(meshes),'automated_pass':True,'geometry_UV_material_parity':True})
 c.dump(O/'saved-validation.json',reports);print('FIVE_SAVED_VARIANTS_PASS',[(r['id'],r['meshes']) for r in reports],flush=True)

def stage():
 import integrate as i
 n=i.n;stage=O/'staged'
 for f in ('Geometries','Materials','Textures','Assets','CN6'):(stage/f).mkdir(parents=True,exist_ok=True)
 reader,_=n.helper(O/'native-reader');converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe';checks=[]
 for row in json.loads((O/'saved-validation.json').read_text()):
  assert c.sha(row['source'])==row['sha256'];name=row['id'];m=json.loads((O/'models'/(name+'.json')).read_text())
  cn6=stage/'CN6'/(name+'.cn6');fgx=stage/'Geometries'/(name+'.fgx');n.exp.write_cn6(cn6,m)
  i.run([converter,cn6,fgx,'2'],O/(name+'-convert.log'),converter.parent)
  i.run([reader,reader.parent,fgx,O/(name+'-native.json')],O/(name+'-read.log'),reader.parent)
  native=json.loads((O/(name+'-native.json')).read_text());assert len(native['meshes'])==len(m['meshes']);error=0
  for a,b in zip(m['meshes'],native['meshes']):
   assert a['name']==b['name'] and a['triangles']==b['triangles'] and len(a['vertices'])==len(b['vertices'])
   assert b['boneBindings']==['Bone'] and b['materialName']==a['materials'][0]['name']
   for v,w in zip(a['vertices'],b['vertices']):
    values=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'];error=max(error,max(abs(x-y) for x,y in zip(v,values)))
    assert w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
  assert error<1e-4
  geo=n.exp.geometry(m,n.read(MOD/'Geometries/CSC_Level_1_S.geo'));n.text(geo,'m_SourceFilePath',row['source']);n.text(geo,'m_Description',row['title']+'; ready-to-use road layout subset')
  n.save(stage/'Geometries'/(name+'.geo'),geo)
  ast=n.fresh_asset(name,m,n.read(MOD/'Assets/CSC_BAKERS_Wind_Mill_Modern.ast'))
  # Match observed classical asset visibility conventions in the private cook test.
  visible=('Worked','Unworked','Pillaged','Unbuilt') if name==ident('01') else n.exp.STATES
  ast.find(n.exp.MODELS).clear();ast.find(n.exp.MODELS).append(n.exp.model_instance(m,{mat['name']:mat['name'] for mesh in m['meshes'] for mat in mesh['materials']},visible))
  n.save(stage/'Assets'/(name+'.ast'),ast);shutil.copy2(cn6,D/cn6.name)
  checks.append({'id':name,'meshes':len(m['meshes']),'native_max_error':error,'passed':True})
 dependencies=[]
 for era in ('Industrial','Modern'):
  mat='CSC_Roads_'+era+'_01'
  for folder,fn in [('Materials',mat+'.mtl')]+[('Textures',mat+'_'+ch+ext) for ch in ('B','H','FOW','S') for ext in ('.dds','.tex')]:
   p=MOD/folder/fn;shutil.copy2(p,stage/folder/fn);dependencies.append({'path':str(p),'sha256':c.sha(p)})
 c.dump(O/'staging-validation.json',{'passed':True,'variants':checks,'dependencies':dependencies});print('NATIVE_VARIANTS_PASS',flush=True)

def publish():
 import integrate as i
 check=json.loads((O/'staging-validation.json').read_text());cook=json.loads((O/'cook-check/result.json').read_text())
 assert check['passed'] and cook['exit_code']==0 and cook['blps']
 assert all(c.sha(r['source'])==r['sha256'] for r in json.loads((O/'saved-validation.json').read_text()))
 assert all(c.sha(r['path'])==r['sha256'] for r in check['dependencies'])
 files=[]
 for number,_,_ in PLAN:
  for ext in ('.geo','.fgx'):assert not (MOD/'Geometries'/(ident(number)+ext)).exists()
 for number,_,_ in PLAN:
  for ext in ('.geo','.fgx'):
   src=O/'staged/Geometries'/(ident(number)+ext);dst=MOD/'Geometries'/src.name;shutil.copy2(src,dst);assert c.sha(src)==c.sha(dst);files.append({'destination':str(dst),'after':c.sha(dst),'before':None})
 c.dump(O/'publication-report.json',{'installed':True,'files':files,'existing_assemblies_modified':False,'public_ASTs_added':False})
 i.n.cache(O);i.OUT=O;i.verify()

if __name__=='__main__':
 mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else sys.argv[1];globals()[mode]()
