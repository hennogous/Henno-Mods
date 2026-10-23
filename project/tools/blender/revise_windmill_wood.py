"""Revise saved masters without regenerating the user's UV edits or AE assembly."""
import bpy,bmesh,json,sys,math,shutil,hashlib
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[3];OUT=Path(sys.argv[sys.argv.index('--')+1])
ART=Path.home()/'Desktop/Working Files/3D Art';SOURCE=ART/'BAKERS/Wind Mill/tower'
NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL'
CENTER=Vector((36.99117,-24.16936192431123,0));HUB=Vector((26.99117,-41.48987,63.74731))
RIGHT=Vector((math.sqrt(3)/2,-.5,0));BACK=Vector((.5,math.sqrt(3)/2,0));UP=Vector((0,0,1))
for f in ['masters','before','bakes','staged/Geometries']:(OUT/f).mkdir(parents=True,exist_ok=True)
report=[];baseline=[]
# Reuse the established isolated, supersampled AO bake with the same allocations.
source=(ROOT/'project/tools/blender/revise_windmill_shared_materials.py').read_text()
exec(compile(source[source.index('def bake_material'):source.index('def material')],'shared_ao_functions','exec'))
sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
def taper(r):return .6+.4*(r-5.5)/(47.8-5.5)
def uv_signature(ob,key):return [[tuple(ob.data.uv_layers[key].data[i].uv) for i in p.loop_indices] for p in ob.data.polygons]
for name in [NAME,RUIN]:
    path=SOURCE/(name+'.blend');baseline.append(dict(path=str(path),sha=hashlib.sha256(path.read_bytes()).hexdigest()))
    shutil.copy2(path,OUT/'before'/path.name)
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;scene.frame_set(1);rig=bpy.data.objects[name]
    tower=next(o for o in scene.objects if o.type=='MESH' and ('_Tower'==o.name[-6:] or o.name.endswith('_Shell')))
    assert not tower.get('wood_revision_20261022'),'Already revised'
    before=[uv_signature(tower,k) for k in ['UV1','UV3']]
    # Increase radial proportions in mesh coordinates, anchoring the front of the
    # foundation. Keep the existing axle and skeleton/animation in their frame.
    for v in tower.data.vertices:
        if name==NAME and 256<=v.index<264:continue
        z=v.co.z;v.co=CENTER+(v.co-CENTER)*Vector((1.15,1.15,1))+BACK*3;v.co.z=z
    tower.data.update();tower['wood_revision_20261022']=True
    assert before==[uv_signature(tower,k) for k in ['UV1','UV3']]
    cell=[516,976,580,1020] if name==NAME else [584,976,648,1020]
    timber=[384,0,448,128] if name==NAME else [448,0,512,128]
    bake(tower,[(name+'_Masonry',cell,1024,14),(name+'_Timber',timber,2048,9)])
    if name==NAME:
        sails=bpy.data.objects[NAME+'_Sails'];before=[uv_signature(sails,k) for k in ['UV1','UV3']]
        assert len(sails.data.vertices)==518
        for blade in range(4):
            a=math.radians(22.5+blade*90);across=RIGHT*math.cos(a)-UP*math.sin(a);along=RIGHT*math.sin(a)+UP*math.cos(a)
            for local in range(114):
                v=sails.data.vertices[blade*114+local];r=(v.co-HUB).dot(along);x=(v.co-HUB).dot(across)
                if local<16:
                    side=-1 if local<8 else 1;v.co+=across*(side*4.5*1.35*taper(r)*.5)
                elif local<64:v.co+=across*x*.5
                elif local<82:
                    new_r=14.2+(r-29.8)*(47.8-14.2)/(47.8-29.8)
                    v.co+=along*(new_r-r)+across*(x*1.5*taper(new_r)/taper(r)-x)
                else:
                    old_r=30.3 if local<98 else 47.2;new_r=14.7 if local<98 else 47.2
                    side=-1 if ((local-82)//8)%2==0 else 1
                    v.co+=along*(new_r-old_r)+across*(side*4.5*1.35*(1.5*taper(new_r)-taper(old_r)))
        sails.data.update();sails['sail_width_factor']=2.025;sails['cloth_inner_radius']=14.2
        assert before==[uv_signature(sails,k) for k in ['UV1','UV3']]
        bake(sails,[(NAME+'_Sails',[0,128,512,512],2048,10)])
    else:
        sc=bpy.data.objects[RUIN+'_Scaffolding'];bm=bmesh.new();bm.from_mesh(sc.data)
        rear=[v for v in bm.verts if v.co.x>CENTER.x]
        assert rear and all(all(v in rear for v in f.verts) or all(v not in rear for v in f.verts) for f in bm.faces)
        bmesh.ops.delete(bm,geom=rear,context='VERTS');bm.to_mesh(sc.data);bm.free();sc.data.update()
        sc['rear_section_removed']=True;report.append(dict(scaffold_remaining_vertices=len(sc.data.vertices),scaffold_remaining_faces=len(sc.data.polygons)))
    objects=[o for o in scene.objects if o.type=='MESH']
    for o in objects:o.data.uv_layers.active_index=0;o.data.uv_layers['UV1'].active_render=True
    for s in bpy.data.scenes:s['windmill_wood_revision']='2026-10-22';s['atlas_release']='2026-10-22_Shared_01_r037'
    for im in bpy.data.images:
        if im.source=='FILE':im.filepath=str(Path(bpy.path.abspath(im.filepath)).resolve())
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig,*objects]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig;bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'masters'/(name+'.blend')),relative_remap=False)
    cn6=OUT/'staged/Geometries'/(name+'.cn6');io_export_cn6_b4.do_export(str(cn6),True,True)
    # Enforce the latest CivNexus inactive-influence padding rule on the prepared
    # CN6, without altering source weights. All intended real influences remain.
    lines=cn6.read_text().splitlines();in_vertices=False;count=0
    for i,line in enumerate(lines):
        if line=='vertices':in_vertices=True;continue
        if line=='triangles':in_vertices=False
        if not in_vertices:continue
        fields=line.split();assert len(fields)==34,(len(fields),line)
        ids=list(map(int,fields[18:26]));weights=list(map(int,fields[26:34]));active=[b for b,w in zip(ids,weights) if w>0]
        assert active and sum(weights)==255
        new=[b if w>0 else active[0] for b,w in zip(ids,weights)]
        count+=ids!=new;fields[18:26]=map(str,new);lines[i]=' '.join(fields)
    cn6.write_text('\n'.join(lines)+'\n');report.append(dict(asset=name,zero_influence_padding_corrected_vertices=count))
(OUT/'inspection.json').write_text(json.dumps(baseline,indent=2))
(OUT/'authoring-report.json').write_text(json.dumps(dict(bakes=report,tower_width=1.15,tower_back_offset=3,sail_width_multiplier=1.5,cloth_extra_rungs=2,brace_geometry_added=False,original_UV1_UV3_preserved=True),indent=2))
