"""Keep the original main building intact; author a forward workshop and narrow rear return."""
import bpy,bmesh,math,json,sys,shutil,ast
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[4]
O=Path.home()/'Desktop/Codex/modern-level2-v2-footprint-20261028'
SRC=Path.home()/'Desktop/Working Files/3D Art/Level 2/modern/revision-01-concept-base'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs
O.mkdir(exist_ok=True);(O/'bakes').mkdir(exist_ok=True);(O/'models').mkdir(exist_ok=True)
shutil.copytree(SRC/'textures',O/'textures',dirs_exist_ok=True)
shutil.copy2(Path.home()/'Desktop/Codex/modern-level2-v1-20261028/bakes/Building.png',O/'bakes/Building.png')
with suspend_csc_repairs():
 bpy.ops.wm.open_mainfile(filepath=str(SRC/'CSC_Level_2_Modern.blend'),load_ui=False,use_scripts=False)
review=bpy.data.scenes['Review'];export=bpy.data.scenes['Export'];bpy.context.window.scene=review
rig=next(o for o in export.objects if o.type=='ARMATURE');ID='CSC_Level_2_Modern'
meshes=[o for o in export.objects if o.type=='MESH']
mat=bpy.data.materials['CSC_BAKERS_Modern'];ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=ns.get('Principled BSDF');maps={c:ns[c] for c in ('B','N','G','M','AO','E')}
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:im.filepath=str(O/'textures'/im.filepath.replace('\\','/').split('/')[-1]);im.reload()
# Reuse the established atlas-aware mesh helpers, without regenerating the main building.
src=(ROOT/'project/tools/art/modern_level2/build.py').read_text();tree=ast.parse(src)
for node in tree.body:
 if isinstance(node,ast.FunctionDef) and node.name in ('uvmap','mesh','box','panel'):
  exec(compile(ast.Module(body=[node],type_ignores=[]),'<mesh helper>','exec'),globals())
MODULE='Workshop'
# The forward work bay preserves the historical Tailor relationship to the house.
# Only a 12-unit side strip and 8-unit rear return continue around the corner.
roofz=lambda y: 33+(y+68)*8/41 if y<=-27 else 41-(y+27)*3/66
box('Workshop_Outer_Left_Wall',(-52,-65,-30),(-48,37,32),0)
box('Workshop_Left_Plinth',(-52.2,-65,-30),(-47.8,37,6),1)
box('Workshop_Back_Wall',(-48,34,-30),(-20,37,37.5),0)
box('Workshop_Back_Plinth',(-48,34,-30),(-20,37.2,6),1)
box('Workshop_Return_End',(-23,29,-30),(-20,34,37.7),0)
box('Workshop_Return_Front',(-40,27,-30),(-20,29,38.5),0)
box('Workshop_Front_Floor',(-48,-63,-2),(-21,-29,0),12)
box('Workshop_Side_Floor',(-48,-29,-2),(-40,34,0),12)
box('Workshop_Return_Floor',(-40,29,-2),(-23,34,0),12)
# Substantial portal and exposed side posts; beam/frame details remain textured.
box('Workshop_Front_Left_Post',(-49,-65,-30),(-45,-61,33.5),8)
box('Workshop_Front_Right_Post',(-22,-65,-30),(-18,-61,33.5),8)
box('Workshop_House_Right_Post',(-22,-32,-30),(-18,-28,40),8)
box('Workshop_Side_Rear_Support',(-43,24,-30),(-39,28,38.6),8)
box('Workshop_Front_Header',(-52,-65,30),(-18,-61,34),4)
# Outer wall follows the roof with no exposed gap or untextured cap.
for y0,y1 in [(-65,-34),(-34,-27),(-27,4),(4,37)]:
 za=roofz(y0);zb=roofz(y1)
 ob=mesh('Workshop_Sloped_Closure',[(-52,y0,32),(-48,y0,32),(-48,y1,32),(-52,y1,32),(-52,y0,za),(-48,y0,za),(-48,y1,zb),(-52,y1,zb)],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],0)
 for poly in ob.data.polygons:
  axis=max(range(3),key=lambda i:abs(poly.normal[i]));aa,bb=([1,2] if axis==0 else [0,2] if axis==1 else [0,1])
  coords=[ob.data.vertices[ob.data.loops[k].vertex_index].co for k in poly.loop_indices];lo=[min(v[i] for v in coords) for i in (aa,bb)]
  for k in poly.loop_indices:
   v=ob.data.vertices[ob.data.loops[k].vertex_index].co;ob.data.uv_layers[0].data[k].uv=uvmap(0,(v[aa]-lo[0])/32,(v[bb]-lo[1])/32)
# One shallow front lean-to, then a narrow low strip behind it. Side/rear meet at y27.
def roof_patch(name,x0,x1,y0,y1):
 z0=roofz(y0);z1=roofz(y1)
 # Roof seam spacing follows world width, not patch width.
 uv=[(0,0),((x1-x0)/38,0),((x1-x0)/38,1),(0,1)]
 mesh(name+'_Roof',[(x0,y0,z0+2),(x1,y0,z0+2),(x1,y1,z1+2),(x0,y1,z1+2)],[(0,1,2,3)],2,[uv])
 panel(name+'_Underside',(x0,y1,z1),(x1,y1,z1),(x1,y0,z0),(x0,y0,z0),8)
roof_patch('Workshop_Forward',-54,-16,-68,-27)
roof_patch('Workshop_Side',-54,-39,-27,27)
roof_patch('Workshop_Rear',-54,-18,27,39)
def fascia(name,a,b):
 panel(name,(a[0],a[1],roofz(a[1])),(b[0],b[1],roofz(b[1])),(b[0],b[1],roofz(b[1])+2),(a[0],a[1],roofz(a[1])+2),3)
for name,a,b in [('Front',(-54,-68),(-16,-68)),('Front_Right',(-16,-68),(-16,-27)),('Front_Rear',(-16,-27),(-39,-27)),('Side_Right',(-39,-27),(-39,27)),('Rear_Front',(-39,27),(-18,27)),('Rear_Right',(-18,27),(-18,39)),('Back',(-18,39),(-54,39)),('Left_Rear',(-54,39),(-54,-27)),('Left_Front',(-54,-27),(-54,-68))]:fascia('Workshop_Fascia_'+name,a,b)
review['footprint_revision']='02: unchanged main, forward work bay, side strip12, rear return8'
review.camera.data.ortho_scale=177
review.render.threads_mode='FIXED';review.render.threads=4;review.cycles.samples=24
# Rebuild independent per-module AO after the geometry changes.
for group,rect,size in [('Workshop',(1536,0,1792,256),512)]:
 selected=[o for o in meshes if o.get('module')==group]
 bpy.ops.object.select_all(action='DESELECT')
 for o in meshes:o.hide_render=o not in selected
 for o in selected:o.select_set(True);o.data.uv_layers.active_index=1
 bpy.context.view_layer.objects.active=selected[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(70),island_margin=.014,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
 ao=bpy.data.images.new(group+'_AO_v2',width=size,height=size,alpha=False);ao.colorspace_settings.name='Non-Color';old=maps['AO'].image;maps['AO'].image=ao;ns.active=maps['AO'];review.render.bake.margin=8
 restore=[(l.from_socket,l.to_socket) for slot in ('Base Color','Normal') for l in list(bs.inputs[slot].links)]
 for slot in ('Base Color','Normal'):
  for l in list(bs.inputs[slot].links):ls.remove(l)
 bpy.ops.object.bake(type='AO',uv_layer='UV2');ao.filepath_raw=str(O/'bakes'/(group+'.png'));ao.file_format='PNG';ao.save();maps['AO'].image=old
 for a,b in restore:ls.new(a,b)
 x0,y0,x1,y1=rect
 for o in selected:
  for d in o.data.uv_layers[1].data:d.uv=((x0+4+d.uv.x*(x1-x0-8))/2048,1-(y1-4-d.uv.y*(y1-y0-8))/2048)
  o.data.uv_layers.active_index=0;o.select_set(False)
for o in meshes:o.hide_render=False
for im in bpy.data.images:
 if im.source=='FILE' and im.filepath:im.filepath='//textures/'+im.filepath.replace('\\','/').split('/')[-1]
bpy.ops.wm.save_as_mainfile(filepath=str(O/'CSC_Level_2_Modern_Assembly.blend'),relative_remap=False)
print('FOOTPRINT_VARIANT_SAVED',flush=True)
