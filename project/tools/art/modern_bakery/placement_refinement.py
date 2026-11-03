"""Match modern display/truck placement to the saved historical Bakery AST."""
import sys,json,hashlib,shutil,math,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];MOD=ROOT/'Civ Supply Chains';O=Path.home()/'Desktop/Codex/modern-bakery-placement-20261028'
sys.path.insert(0,str(ROOT/'project/tools/blender'))
IDS=['CSC_BAKERS_Bakery_2','CSC_BAKERS_Bakery_Modern','CSC_BAKERS_Bakery_Modern_2']
def prepare():
 from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,prepare_geometry,PRESETS
 O.mkdir(exist_ok=True);r=Resolver(MOD,DEFAULT_SDK)
 for ident in IDS:
  a=Assembly(r,'Worked');key=a.asset(MOD/'Assets'/(ident+'.ast'));run=O/ident;run.mkdir(exist_ok=True);prepare_geometry(a,O/'cache',run)
  settings={'presets':PRESETS,'resolution':1100,'samples':40,'camera_class':'L2','fixed_camera':json.loads((ROOT/'project/tools/blender/ae_render_camera_presets.json').read_text())['classes']['L2'],'render_emission_enabled':False,'state':'Worked'}
  job={'root':key,'assets':a.assets,'geometries':a.geometries,'materials':a.materials,'excluded':a.excluded,'warnings':a.warnings,'settings':settings,'output':str(run)}
  (run/'job.json').write_text(json.dumps(job,indent=2))
def measure():
 import bpy
 from mathutils import Matrix
 from ae_asset_render_blender import Builder
 facts={};frame=Matrix.Rotation(0.626573,4,'Z')
 for ident in IDS:
  run=O/ident;job=json.loads((run/'job.json').read_text());bpy.ops.wm.read_factory_settings(use_empty=True);b=Builder(job,'icon');b.assemble(job['root'],root=True);bpy.context.view_layer.update();rows=[]
  for ob in b.objects:
   pts=[ob.matrix_world@v.co for v in ob.data.vertices];local=[frame@p for p in pts]
   bounds=lambda pp:[[min(p[i] for p in pp) for i in range(3)],[max(p[i] for p in pp) for i in range(3)]]
   rows.append({'name':ob.name,'path':ob.get('ae_semantic_path'),'world':bounds(pts),'frame':bounds(local),'matrix':[list(r) for r in ob.matrix_world]})
  facts[ident]=rows
 (O/'measurements.json').write_text(json.dumps(facts,indent=2));print('MEASURED',flush=True)
def edit():
 import xml.etree.ElementTree as E
 facts=json.loads((O/'measurements.json').read_text());hist=facts[IDS[0]]
 stand=next(r for r in hist if '/CSC_ALL_Stand/' in r['path']);table=next(r for r in hist if '/DIS_COM_Table/' in r['path'])
 width=table['frame'][1][0]-table['frame'][0][0];scale=width/48
 center=[(min(stand['frame'][0][i],table['frame'][0][i])+max(stand['frame'][1][i],table['frame'][1][i]))/2 for i in range(2)]
 # Modern display local bounds are [-24,24] x [-10,8]; account for its -1 Y center.
 old=next(r for r in facts[IDS[2]] if '/CSC_Attach_Display/' in r['path']);angle=.626573;c=math.cos(angle);s=math.sin(angle)
 oldpos=[old['matrix'][i][3] for i in range(2)];pframe=[c*oldpos[0]-s*oldpos[1],s*oldpos[0]+c*oldpos[1]]
 offset=[(old['frame'][0][i]+old['frame'][1][i])/2-pframe[i] for i in range(2)]
 target=[center[i]-offset[i]*scale for i in range(2)];pos=[(c*target[0]+s*target[1])/10,(-s*target[0]+c*target[1])/10,0]
 historical=E.parse(MOD/'Assets/CSC_BAKERS_Bakery_2.ast').getroot()
 cart=next(r for r in historical.findall('.//m_Points/Element') if any(e.get('text')=='CSC_BAKERS_Bread_Cart' for e in r.findall('.//m_EntryName')))
 truckpos=[float(cart.findtext('m_position/'+a)) for a in 'xyz'];truckrot=[float(cart.findtext('m_orientation/'+a)) for a in 'xyz']
 changes=[]
 for ident in IDS[1:]:
  path=MOD/'Assets'/(ident+'.ast');raw=path.read_text();backup=O/(ident+'-before.ast');assert not backup.exists();shutil.copy2(path,backup)
  root=E.fromstring(raw)
  def patch(name,position,rotation=None,newscale=None):
   nonlocal raw
   point=next(r for r in root.findall('.//m_Points/Element') if r.find('m_Name').get('text')==name)
   marker=re.search(r'(?m)^(\s*)<m_Name text="'+re.escape(name)+r'"\s*/>',raw);assert marker
   indent=marker.group(1);start=raw.rfind(indent[:-1]+'<Element>',0,marker.start());end=raw.index(indent[:-1]+'</Element>',marker.end())+len(indent[:-1]+'</Element>');assert start>=0
   block=raw[start:end]
   for tag,values in [('m_position',position),('m_orientation',rotation)]:
    if values is None:continue
    match=re.search('<'+tag+r'>.*?</'+tag+'>',block,re.S);assert match
    part=match.group()
    for axis,value in zip('xyz',values):part=re.sub('<'+axis+r'>.*?</'+axis+'>',f'<{axis}>{value:.6f}</{axis}>',part)
    block=block[:match.start()]+part+block[match.end():]
   if newscale is not None:block=re.sub(r'<m_scale>.*?</m_scale>',f'<m_scale>{newscale:.6f}</m_scale>',block)
   raw=raw[:start]+block+raw[end:]
  patch('CSC_Attach_Display',pos,newscale=scale)
  if ident.endswith('_2'):patch('CSC_Attach_Truck',truckpos,truckrot)
  final=E.fromstring(raw)
  # Compare every other field after normalizing just the specifically authorized values.
  for a,b in zip(root.findall('.//m_Points/Element'),final.findall('.//m_Points/Element')):
   name=a.find('m_Name').get('text')
   fields=['m_position','m_scale'] if name=='CSC_Attach_Display' else ['m_position','m_orientation'] if name=='CSC_Attach_Truck' else []
   for tag in fields:
    aa=a.find(tag);bb=b.find(tag)
    if len(aa):
     for x,y in zip(aa,bb):y.text=x.text
    else:bb.text=aa.text
  assert E.tostring(root)==E.tostring(final)
  # Preserve original CRLF and all bytes except the selected attachment fields.
  data=raw.replace('\n','\r\n').encode('utf-8') if b'\r\n' in path.read_bytes() else raw.encode('utf-8');path.write_bytes(data)
  changes.append({'destination':str(path),'backup':str(backup),'before':hashlib.sha256(backup.read_bytes()).hexdigest(),'after':hashlib.sha256(data).hexdigest()})
 (O/'publication-report.json').write_text(json.dumps({'installed':True,'files':changes,'display_scale':scale,'display_position':pos,'truck_position':truckpos,'truck_orientation':truckrot,'all_other_AST_fields_preserved':True,'geometry_textures_unchanged':True},indent=2));print('PLACEMENTS_UPDATED',scale,pos,truckpos,flush=True)
if __name__=='__main__':measure() if '--' in sys.argv else edit() if 'edit' in sys.argv else prepare()
