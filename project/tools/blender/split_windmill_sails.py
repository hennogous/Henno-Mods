"""Two cloth panels per blade, separated and bounded by exposed timber rungs."""
import bpy,bmesh,json,sys,math,hashlib,shutil
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[3]
ART=Path.home()/'Desktop/Working Files/3D Art';SOURCE=ART/'BAKERS/Wind Mill/tower'
NAME='CSC_BAKERS_Wind_Mill_Tower';RELEASE='2026-10-24_Shared_01_r043'
RIGHT=Vector((math.sqrt(3)/2,-.5,0));BACK=Vector((.5,math.sqrt(3)/2,0));HUB=Vector((26.99117,-41.48987,63.74731))
for folder in ['masters','before','bakes','staged/Geometries']:(OUT/folder).mkdir(parents=True,exist_ok=True)
p=SOURCE/(NAME+'.blend');shutil.copy2(p,OUT/'before'/p.name)
(OUT/'inspection.json').write_text(json.dumps([dict(path=str(p),sha=hashlib.sha256(p.read_bytes()).hexdigest())],indent=2))
bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
bpy.context.window.scene=bpy.data.scenes['Export'];scene=bpy.context.scene;scene.frame_set(1);rig=bpy.data.objects[NAME]
sails=bpy.data.objects[NAME+'_Sails'];old=sails.data;group_names=[g.name for g in sails.vertex_groups]
assert len(old.vertices)==390 and len(old.polygons)==324
def signature(ob):
 return dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[list(f.vertices) for f in ob.data.polygons],uvs=[[list(v.uv) for v in u.data] for u in ob.data.uv_layers],weights=[[(g.group,g.weight) for g in v.groups] for v in ob.data.vertices])
tower=bpy.data.objects[NAME+'_Tower'];tower_before=signature(tower)
cloth=lambda i:i<328 and 64<=i%82<82
keep=[v.index for v in old.vertices if not cloth(v.index)];remap={v:i for i,v in enumerate(keep)}
vertices=[old.vertices[i].co.copy() for i in keep];faces=[];uvs={u.name:[] for u in old.uv_layers};weights=[[(g.group,g.weight) for g in old.vertices[i].groups] for i in keep]
for f in old.polygons:
 if all(cloth(i) for i in f.vertices):continue
 assert not any(cloth(i) for i in f.vertices)
 faces.append([remap[i] for i in f.vertices])
 for u in old.uv_layers:uvs[u.name].append([tuple(u.data[i].uv) for i in f.loop_indices])
panels=[];rungs=[]
for blade in range(4):
 angle=math.radians(22.5+90*blade);across=RIGHT*math.cos(angle)-Vector((0,0,1))*math.sin(angle);along=RIGHT*math.sin(angle)+Vector((0,0,1))*math.cos(angle)
 # Three structural boundaries are thicker; the other ladder rungs remain as authored.
 for rung,oldr,newr,thickness in [(1,15.8,15.8,2.2),(3,31.4,31.4,2.2),(5,47,48.2,2.2)]:
  for vi in range(blade*82+16+rung*8,blade*82+24+rung*8):
   p=old.vertices[vi].co;local=p-HUB;x=local.dot(across);r=local.dot(along);z=local.dot(BACK)
   r=newr+(r-oldr)*thickness/1.55
   half=4.5*2.025*(.6+.4*(r-5.5)/(47.8-5.5))-.825+.04
   vertices[remap[vi]]=HUB+across*math.copysign(half,x)+along*r+BACK*(z*1.3)
  rungs.append(dict(blade=blade,radius=newr,thickness=thickness))
 template=[f for f in old.polygons if all(blade*82+64<=i<blade*82+82 for i in f.vertices)]
 assert len(template)==24
 for half,(lo,hi) in enumerate([(17.2,29.9),(32.9,47.0)]):
  start=len(vertices)
  for vi in range(18):
   back=vi>=9;grid=vi%9;row=grid//3;column=grid%3;r=lo+(hi-lo)*row/2
   width=4.3*2.025*(.6+.4*(r-5.5)/(47.8-5.5));x=width*(column-1)
   # Each separate piece has a shallow billow. Front/back share exact diagonals.
   z=-1.5-(.7 if row==1 and column==1 else 0)+(.3 if back else 0)
   vertices.append(HUB+across*x+along*r+BACK*z)
   weights.append([(g.group,g.weight) for g in old.vertices[blade*82+64+vi].groups])
  for f in template:
   faces.append([start+i-(blade*82+64) for i in f.vertices])
   for u in old.uv_layers:
    values=[]
    for i in f.loop_indices:
     v=u.data[i].uv.copy()
     if u.name=='UV1':v.y=(1-636/1024)+.5*(v.y-(1-636/1024))+half*60/1024
     values.append(tuple(v))
    uvs[u.name].append(values)
  panels.append(dict(blade=blade,panel=half,inner=lo,outer=hi))
me=bpy.data.meshes.new(old.name+'_SplitPanels');me.from_pydata(vertices,[],faces);me.update()
for mat in old.materials:me.materials.append(mat)
for name,rows in uvs.items():
 u=me.uv_layers.new(name=name)
 for f,values in zip(me.polygons,rows):
  for i,value in zip(f.loop_indices,values):u.data[i].uv=value
sails.data=me
sails.vertex_groups.clear()
for name in group_names:sails.vertex_groups.new(name=name)
for vi,values in enumerate(weights):
 for group,weight in values:sails.vertex_groups[group].add([vi],weight,'REPLACE')
assert len(me.vertices)==462 and len(me.polygons)==420
# Repack self-AO for the changed contacts and newly separate cloth panels.
bpy.ops.object.select_all(action='DESELECT');sails.select_set(True);bpy.context.view_layer.objects.active=sails
me.uv_layers.active_index=1;me.uv_layers['UV2'].active_render=True
bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.select_all(action='SELECT')
bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.018,correct_aspect=True,scale_to_bounds=True)
bpy.ops.object.mode_set(mode='OBJECT')
report=[];source=(ROOT/'project/tools/blender/revise_windmill_shared_materials.py').read_text()
exec(compile(source[source.index('def bake_material'):source.index('def material')],'shared_bake','exec'))
bake(sails,[(NAME+'_Sails',[0,128,512,512],2048,10)])
assert signature(tower)==tower_before
sails['cloth_panels_per_blade']=2;sails['exposed_cross_rungs']='Inner 15.8, middle 31.4, tip 48.2; thickness 2.2'
for s in bpy.data.scenes:s['atlas_release']=RELEASE
objects=[o for o in scene.objects if o.type=='MESH']
for ob in objects:ob.data.uv_layers.active_index=0;ob.data.uv_layers['UV1'].active_render=True
bpy.ops.object.select_all(action='DESELECT')
for ob in [rig,*objects]:ob.select_set(True)
bpy.context.view_layer.objects.active=rig;bpy.context.preferences.filepaths.save_version=0
bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'masters'/(NAME+'.blend')),relative_remap=False)
tower.data=tower.data.copy();bm=bmesh.new();bm.from_mesh(tower.data);bmesh.ops.split_edges(bm,edges=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle()>.01]);bm.to_mesh(tower.data);bm.free()
sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
cn6=OUT/'staged/Geometries'/(NAME+'.cn6');io_export_cn6_b4.do_export(str(cn6),True,True)
lines=cn6.read_text().splitlines();inside=False
for i,line in enumerate(lines):
 if line=='vertices':inside=True;continue
 if line=='triangles':inside=False
 if not inside:continue
 fields=line.split();assert len(fields)==34;ids=list(map(int,fields[18:26]));ws=list(map(int,fields[26:34]));active=[b for b,w in zip(ids,ws) if w>0];assert active
 fields[18:26]=[str(b if w else active[0]) for b,w in zip(ids,ws)];lines[i]=' '.join(fields)
cn6.write_text('\n'.join(lines)+'\n')
(OUT/'authoring-report.json').write_text(json.dumps(dict(bakes=report,panels=panels,rungs=rungs,sail_vertices=462,sail_faces=420,tower_exactly_preserved=True,retained_frame_and_hub_UV1_UV3_preserved=True),indent=2))
print('SPLIT_SAILS_AUTHORED',flush=True)
