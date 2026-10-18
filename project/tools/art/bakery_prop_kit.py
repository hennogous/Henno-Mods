"""Collect independent editable Bakery masters into one reviewable prop-kit blend."""
import bpy,sys,json,hashlib,math
from pathlib import Path
from mathutils import Vector,Matrix
sys.path.insert(0,str(Path(__file__).parent))
from build_bakery_props import setup,C,SOURCE,OUT,IDS,V,RELEASE
def main():
 # Refresh paint-only review renders from the actual final portable texture snapshot.
 for ident in ([] if '--kit-only' in sys.argv else IDS):
  p=SOURCE/(ident+'.blend')
  with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  if any(s.get('atlas_release')!=RELEASE for s in bpy.data.scenes if s.name in ('Export','Review')):
   for s in bpy.data.scenes:
    if s.name in ('Export','Review'):s['atlas_release']=RELEASE
   bpy.ops.wm.save_as_mainfile(filepath=str(p))
  report=V.validate_current_scene();report['source_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();assert report['automated_pass'];(OUT/(ident+'-validation.json')).write_text(json.dumps(report,indent=2))
  for im in bpy.data.images:
   if im.source=='FILE' and im.users and Path(bpy.path.abspath(im.filepath)).exists():im.reload()
  if '--no-render' not in sys.argv:
   s=bpy.data.scenes['Review'];bpy.context.window.scene=s;s.render.filepath=str(OUT/(ident+'-preview.png'));bpy.ops.render.render(write_still=True)
 setup('CSC_BAKERS_Bakery_Prop_Kit');exp=bpy.data.scenes['Export'];rev=bpy.data.scenes['Review'];rig=next(o for o in exp.objects if o.type=='ARMATURE')
 slots=[(-45,-20,0),(0,-20,0),(40,-20,0),(65,-20,0),(90,-20,0),(45,20,0),(-45,40,0)]
 counts={}
 for ident,loc in zip(IDS,slots):
  # Load only the Export scene, then move mesh objects under a support controller.
  with bpy.data.libraries.load(str(SOURCE/(ident+'.blend')),link=False) as (a,b):b.scenes=['Export']
  scene=b.scenes[0];bpy.context.window.scene=scene;bpy.context.view_layer.update();meshes=[o for o in scene.objects if o.type=='MESH'];world={o.name:o.matrix_world.copy() for o in meshes}
  controller=bpy.data.objects.new(ident+'_Master',None);exp.collection.objects.link(controller);rev.collection.objects.link(controller);controller.location=loc;controller['instance_id']=ident;controller['source_asset_id']=ident;controller['export_role']='custom_attachment';controller['support']='ground';controller['terrain_follow']='pivot';controller['reuse_scope']='quarter';controller['reuse_approved']=True;controller['reuse_reference']='Henno Bakery prop brief 16 October 2026; independent installed master '+ident
  scale=.65 if ident.endswith('Oven_v2') else 1
  controller.scale=(scale,)*3
  for ob in meshes:
   for col in list(ob.users_collection):col.objects.unlink(ob)
   exp.collection.objects.link(ob);rev.collection.objects.link(ob);ob.parent=controller;ob.matrix_parent_inverse=Matrix.Identity(4);ob.matrix_basis=world[ob.name];ob['instance_id']=ident;ob['source_asset_id']=ident;ob['export_role']='attachment_geometry'
   for mod in list(ob.modifiers):ob.modifiers.remove(mod)
   ob.modifiers.new('Kit_Static_Rig','ARMATURE').object=rig
  counts[ident]=sum(V.export_vertex_count(o.data) for o in meshes);bpy.data.scenes.remove(scene)
 bpy.context.window.scene=rev;center=Vector((15,18,24));rev.camera.location=center+Vector((150,-220,200));rev.camera.rotation_euler=(center-rev.camera.location).to_track_quat('-Z','Y').to_euler();rev.camera.data.ortho_scale=240;rev.render.resolution_x=1600;rev.render.resolution_y=1000
 path=SOURCE/'CSC_BAKERS_Bakery_Prop_Kit.blend';bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(path))
 with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
 report=V.validate_current_scene();report['source_sha256']=hashlib.sha256(path.read_bytes()).hexdigest();(OUT/'kit-validation.json').write_text(json.dumps(report,indent=2));assert report['automated_pass'],V.format_report(report)
 if '--no-render' not in sys.argv:
  rev=bpy.data.scenes['Review'];bpy.context.window.scene=rev;rev.render.filepath=str(OUT/'Bakery_Prop_Kit.png');bpy.ops.render.render(write_still=True)
 print('KIT COMPLETE',counts)
if __name__=='__main__':main()
