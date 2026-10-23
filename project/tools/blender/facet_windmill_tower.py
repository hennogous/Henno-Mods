"""Give the wooden tower six planar braced faces, preserving the approved machinery."""
import bpy,bmesh,json,sys,math,shutil,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=Path(sys.argv[sys.argv.index('--')+1]);ART=Path.home()/'Desktop/Working Files/3D Art';SOURCE=ART/'BAKERS/Wind Mill/tower'
NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL'
RIGHT=Vector((math.sqrt(3)/2,-.5,0));BACK=Vector((.5,math.sqrt(3)/2,0));CENTER=Vector((36.99117,-24.16936192431123,0))+BACK*3
GAIN=math.cos(math.pi/12)/math.cos(math.pi/6)
for f in ['masters','before','bakes','staged/Geometries']:(OUT/f).mkdir(parents=True,exist_ok=True)
report=[];baseline=[]
source=(ROOT/'project/tools/blender/revise_windmill_shared_materials.py').read_text()
exec(compile(source[source.index('def bake_material'):source.index('def material')],'shared_ao_functions','exec'))
sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
for name in [NAME,RUIN]:
    path=SOURCE/(name+'.blend');baseline.append(dict(path=str(path),sha=hashlib.sha256(path.read_bytes()).hexdigest()));shutil.copy2(path,OUT/'before'/path.name)
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;scene.frame_set(1);rig=bpy.data.objects[name]
    tower=next(o for o in scene.objects if o.type=='MESH' and (o.name.endswith('_Tower') or o.name.endswith('_Shell')))
    assert not tower.get('hexagonal_revision')
    mesh=tower.data;old={v.index:v.co.copy() for v in mesh.vertices};indices={};radii={}
    for v in mesh.vertices:
        if (name==NAME and 216<=v.index<264) or (name==RUIN and 96<=v.index<136):continue
        p=v.co-CENTER;x=p.dot(RIGHT);y=p.dot(BACK);radius=math.hypot(x,y)
        angle=math.atan2(y,x);index=round((angle-math.pi/12)/(math.pi/6))%12
        assert abs(math.remainder(angle-(math.pi/12+index*math.pi/6),2*math.pi))<.001,(v.index,angle,index)
        indices[v.index]=index;radii[v.index]=radius
        def direction(i):return RIGHT*math.cos(i*math.pi/6)+BACK*math.sin(i*math.pi/6)
        d=direction(index) if index%2==0 else (direction(index-1)+direction(index+1))*.5
        v.co=CENTER+d*radius*GAIN;v.co.z=old[v.index].z
    wood=[]
    for face in mesh.polygons:
        uv=mesh.uv_layers['UV1'];coords=[uv.data[i].uv for i in face.loop_indices]
        if all(513/1024<=u<=643/1024 and 1-745/1024<=v<=1-615/1024 for u,v in coords):
            ids={indices[i] for i in face.vertices};assert len(ids)==2,ids
            first=11 if ids=={0,11} else min(ids);panel=first//2;theta=(panel*60+30)*math.pi/180
            tangent=-RIGHT*math.sin(theta)+BACK*math.cos(theta)
            for li in face.loop_indices:
                vi=mesh.loops[li].vertex_index;p=mesh.vertices[vi].co
                u=.5+(p-CENTER).dot(tangent)/(radii[vi]*GAIN)
                v=(p.z-14.4)/(57.3-14.4)
                assert -.0001<=u<=1.0001
                uv.data[li].uv=((514+128*u)/1024,1-744/1024+128*v/1024)
            face.use_smooth=False;wood.append((face.index,panel))
        elif all(i in indices for i in face.vertices):face.use_smooth=False
    assert len(wood)==(12 if name==NAME else 24),(name,len(wood))
    mesh.update()
    # Pairwise panels must be one physical plane, not merely flat-shaded strips.
    for panel in range(6):
        faces=[mesh.polygons[i] for i,k in wood[:12] if k==panel];assert len(faces)==2
        a,b=faces;assert a.normal.dot(b.normal)>.99999,(panel,a.normal,b.normal)
    tower['hexagonal_revision']=True;tower['wall_panels']=6;tower['brace_mapping']='One complete painted brace per planar outer face'
    cell=[516,976,580,1020] if name==NAME else [584,976,648,1020];timber=[384,0,448,128] if name==NAME else [448,0,512,128]
    bake(tower,[(name+'_Masonry',cell,1024,14),(name+'_Timber',timber,2048,9)])
    objects=[o for o in scene.objects if o.type=='MESH']
    for o in objects:o.data.uv_layers.active_index=0;o.data.uv_layers['UV1'].active_render=True
    for s in bpy.data.scenes:s['atlas_release']='2026-10-22_Shared_01_r038';s['windmill_shape']='Tapered hexagonal timber tower'
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig,*objects]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig;bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'masters'/(name+'.blend')),relative_remap=False)
    # The legacy exporter averages normals by source vertex. Split hard edges on
    # an export-only mesh so it cannot round the six corners again in the FGX.
    original=tower.data;tower.data=original.copy();bm=bmesh.new();bm.from_mesh(tower.data)
    edges=[e for e in bm.edges if len(e.link_faces)==2 and e.calc_face_angle()>.01]
    bmesh.ops.split_edges(bm,edges=edges);bm.to_mesh(tower.data);bm.free();tower.data.update()
    cn6=OUT/'staged/Geometries'/(name+'.cn6');io_export_cn6_b4.do_export(str(cn6),True,True)
    report.append(dict(asset=name,planar_outer_faces=6,full_brace_per_face=True,export_hard_edges_split=len(edges),source_vertices=len(original.vertices),prepared_vertices=len(tower.data.vertices)))
    tower.data=original
(OUT/'inspection.json').write_text(json.dumps(baseline,indent=2));(OUT/'authoring-report.json').write_text(json.dumps(dict(bakes=report,shape='hexagonal',sails_unchanged=True,scaffolds_unchanged=True),indent=2))
