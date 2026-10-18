"""r029 changes crown UV1 only; every geometry coordinate, UV2/AO and rig remains unchanged."""
import bpy,sys,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import *
def export(ident,index,before,path):
 cell=[512+(index%4)*128,(index//4)*128,640+(index%4)*128,128+(index//4)*128]
 exp=bpy.data.scenes['Export'];bpy.context.window.scene=exp
 parts=[o for o in exp.objects if o.type=='MESH'];arm=next(o for o in exp.objects if o.type=='ARMATURE' and o.name==ident+'_Rig')
 for o in bpy.context.selected_objects:o.select_set(False)
 copies=[]
 for o in parts:
  c=bpy.data.objects.new(o.name+'_Prepared',o.data.copy());c.data.transform(o.matrix_world);exp.collection.objects.link(c);c.select_set(True);copies.append(c)
 bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=copies[0];joined.name=ident;joined.vertex_groups.new(name='Bone').add(list(range(len(joined.data.vertices))),1,'REPLACE');joined.modifiers.new('Static rig','ARMATURE').object=arm
 cn6=OUT/(ident+'.cn6');geo=OUT/(ident+'.geo');fgx=OUT/(ident+'.fgx');E.csc_do_export_selected(str(cn6),[arm,joined]);summary,vertices,triangles=E.csc_write_geo(str(geo),ident,str(cn6),'LandmarkModel');geo.write_text(geo.read_text().replace('AssetObjects:','AssetObjects..'))
 lib=ROOT/'project/tools/cn6libs'
 for args,label in [([lib/'CN6ToFGX.exe',cn6,fgx,2],'conversion'),([lib/'FGXToCN6.exe',fgx,OUT/(ident+'-roundtrip.cn6')],'roundtrip')]:
  r=subprocess.run([str(a) for a in args],cwd=lib,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);(OUT/(ident+'-'+label+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==0
 (OUT/(ident+'-export.json')).write_text(json.dumps(dict(asset_id=ident,vertices=vertices,triangles=triangles,ao_cell=cell,source=str(path),source_sha256=before),indent=2));print('BAKERY EXPORTED',ident,vertices,triangles,flush=True)
for index,ident in enumerate(IDS):
 if ident not in IDS[2:6]:continue
 path=SOURCE/(ident+'.blend')
 with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 for scene in bpy.data.scenes:
  if scene.name in ('Export','Review'):scene['atlas_release']=RELEASE
 for ob in bpy.data.scenes['Export'].objects:
  if ob.type!='MESH' or 'Bread_Fill' not in ob.name:continue
  kind=next(k for k in ['Round','Oval','Long'] if '_'+k+'_' in ob.name);patch={'Round':'bakery_round_crust','Oval':'bakery_oval_bread','Long':'bakery_long_crust'}[kind]
  crown=ob.data.polygons[0];xs=[ob.data.vertices[v].co.x for v in crown.vertices];ys=[ob.data.vertices[v].co.y for v in crown.vertices];x,y,x1,y1=C.REGIONS[patch]
  for loop in crown.loop_indices:
   v=ob.data.vertices[ob.data.loops[loop].vertex_index].co;u=.015+.97*(v.x-min(xs))/(max(xs)-min(xs));t=.015+.97*(v.y-min(ys))/(max(ys)-min(ys));ob.data.uv_layers[0].data[loop].uv=((x+(x1-x)*u)/1024,1-(y+(y1-y)*(1-t))/1024)
 bpy.ops.wm.save_as_mainfile(filepath=str(path))
 before=hashlib.sha256(path.read_bytes()).hexdigest()
 with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 report=V.validate_current_scene();report['source_sha256']=before;assert report['automated_pass'];(OUT/(ident+'-validation.json')).write_text(json.dumps(report,indent=2))
 export(ident,index,before,path)
