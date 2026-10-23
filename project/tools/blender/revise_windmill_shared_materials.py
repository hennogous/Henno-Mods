"""Preserve Henno's surface edits; adopt shared AO/materials and his scaffold mesh."""
import bpy,bmesh,json,sys,hashlib,math,shutil
from pathlib import Path
from mathutils import Vector
OUT=Path(sys.argv[sys.argv.index('--')+1]);ROOT=Path(__file__).resolve().parents[3]
ART=Path.home()/'Desktop/Working Files/3D Art';SOURCE=ART/'BAKERS/Wind Mill/tower';LIB=ART/'Textures/CSC_Props'
NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL';RELEASE='2026-10-21_Shared_01_r036'
sys.path.insert(0,str(ROOT/'project/tools/scripts'));import io_export_cn6_b4
for folder in ('masters','bakes','before','staged/Geometries'):(OUT/folder).mkdir(parents=True,exist_ok=True)
inspection=json.loads((OUT/'inspection.json').read_text());report=[]
for row in inspection:
    p=Path(row['path']);assert hashlib.sha256(p.read_bytes()).hexdigest()==row['sha'];shutil.copy2(p,OUT/'before'/p.name)

def signature(ob):
    return dict(vertices=[list(v.co) for v in ob.data.vertices],faces=[sorted(f.vertices) for f in ob.data.polygons],matrix=[list(r) for r in ob.matrix_world],uv1=[sorted((ob.data.loops[i].vertex_index,*ob.data.uv_layers['UV1'].data[i].uv) for i in f.loop_indices) for f in ob.data.polygons],uv3=[sorted((ob.data.loops[i].vertex_index,*ob.data.uv_layers['UV3'].data[i].uv) for i in f.loop_indices) for f in ob.data.polygons],weights=[[(g.group,g.weight) for g in v.groups] for v in ob.data.vertices])

def bake_material(image,distance):
    m=bpy.data.materials.new('TEMP_AO_BAKE');m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
    tex=n.new('ShaderNodeTexImage');tex.image=image;n.active=tex
    ao=n.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=distance;ao.samples=16;ao.only_local=True
    emission=n.new('ShaderNodeEmission');out=n.new('ShaderNodeOutputMaterial');l.new(ao.outputs['Color'],emission.inputs['Color']);l.new(emission.outputs[0],out.inputs[0]);return m

def bake(ob,allocations):
    # Bake an isolated copy at twice the final cell resolution. Each material
    # has its own target, so its UV2 may use the full patch without cross-talk.
    scene=bpy.context.scene;copy=ob.copy();copy.data=ob.data.copy();copy.parent=None;copy.matrix_world=ob.matrix_world.copy();copy.modifiers.clear();scene.collection.objects.link(copy)
    copy.data.materials.clear();uv=copy.data.uv_layers['UV2'];targets=[];uvs={}
    for mi,(ident,cell,size,distance) in enumerate(allocations):
        indices=[li for f in ob.data.polygons if f.material_index==mi for li in f.loop_indices]
        if not indices:raise ValueError((ob.name,mi,'No faces'))
        low=[min(uv.data[i].uv[a] for i in indices) for a in (0,1)];high=[max(uv.data[i].uv[a] for i in indices) for a in (0,1)]
        w,h=cell[2]-cell[0],cell[3]-cell[1];pad=4 if w>=128 else 2
        for i in indices:
            xy=uv.data[i].uv.copy();uv.data[i].uv=((pad+(xy.x-low[0])/(high[0]-low[0])*(w-2*pad))/w,(pad+(xy.y-low[1])/(high[1]-low[1])*(h-2*pad))/h)
        uvs[mi]=[(i,tuple(uv.data[i].uv)) for i in indices]
        im=bpy.data.images.new(ident+'_AO_Bake',width=w*2,height=h*2,alpha=False,float_buffer=True);im.generated_color=(1,1,1,1);im.colorspace_settings.name='Non-Color'
        copy.data.materials.append(bake_material(im,distance));targets.append(im)
    for f,source_face in zip(copy.data.polygons,ob.data.polygons):f.material_index=source_face.material_index
    bpy.ops.object.select_all(action='DESELECT');copy.select_set(True);bpy.context.view_layer.objects.active=copy
    for other in scene.objects:
        if other.type=='MESH':other.hide_render=other!=copy
    copy.data.uv_layers.active_index=1;uv.active_render=True
    scene.render.engine='CYCLES';scene.cycles.device='CPU';scene.cycles.samples=128
    scene.render.bake.use_clear=False;scene.render.bake.margin=4;scene.render.bake.margin_type='EXTEND';scene.render.bake.use_selected_to_active=False
    print('BAKING',ob.name,flush=True)
    bpy.ops.object.bake(type='EMIT')
    print('BAKED',ob.name,flush=True)
    for mi,((ident,cell,size,distance),im) in enumerate(zip(allocations,targets)):
        im.file_format='PNG';im.filepath_raw=str(OUT/'bakes'/(ident+'.png'));im.save()
        x,y,x1,y1=cell
        for i,(u,v) in uvs[mi]:ob.data.uv_layers['UV2'].data[i].uv=((x+u*(x1-x))/size,1-(y+(1-v)*(y1-y))/size)
        report.append(dict(id=ident,cell=cell,page_size=size,distance=distance,raw_bake=im.filepath_raw,samples=128,ao_samples=16,supersampling=2))
    bpy.data.objects.remove(copy,do_unlink=True)
    for other in scene.objects:
        if other.type=='MESH':other.hide_render=False

def material(old,name,ao_path):
    old.name=name;old['external']=name;n=old.node_tree.nodes
    im=bpy.data.images.load(str(ao_path),check_existing=True);im.colorspace_settings.name='Non-Color';n.get('AO bake target').image=im
    return old

for asset in (NAME,RUIN):
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE/(asset+'.blend')),load_ui=False,use_scripts=False)
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;scene.frame_set(1);rig=bpy.data.objects[asset]
    objects=[o for o in scene.objects if o.type=='MESH'];before={o.name:signature(o) for o in objects}
    tower=next(o for o in objects if not o.name.endswith('_Sails'))
    # Preserve UV1/UV3, topology, weights and positions. Only AO coordinates change.
    tower_cell=[516,976,580,1020] if asset==NAME else [584,976,648,1020]
    wood_cell=[384,0,448,128] if asset==NAME else [448,0,512,128]
    bake(tower,[(asset+'_Masonry',tower_cell,1024,14),(asset+'_Timber',wood_cell,2048,9)])
    material(tower.data.materials[0],'CSC_BAKERS_E',ART/'Textures/CSC_Atlas_AO2.png')
    props=material(tower.data.materials[1],'CSC_ALL_Props_01',LIB/'Current/textures/CSC_Props_Shared_01_AO.png')
    if asset==NAME:
        sails=next(o for o in objects if o.name.endswith('_Sails'));sails.data.materials[0]=props
        bm=bmesh.new();bm.from_mesh(sails.data);normals=[f.normal.copy() for f in bm.faces]
        bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.normal_update()
        flipped=sum(a.dot(f.normal)<-.9 for a,f in zip(normals,bm.faces));bm.to_mesh(sails.data);bm.free();sails.data.update()
        report.append(dict(sail_faces_corrected_outward=flipped));print('SAIL_NORMALS_CORRECTED',flipped,flush=True)
        # Repack the existing sail charts alone; this avoids new seams and gives
        # them the full 512x384 cell instead of sharing a small private bake.
        bpy.ops.object.select_all(action='DESELECT');sails.select_set(True);bpy.context.view_layer.objects.active=sails;sails.data.uv_layers.active_index=1
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.select_all(action='SELECT');bpy.ops.uv.pack_islands(rotate=True,scale=True,margin=.012);bpy.ops.object.mode_set(mode='OBJECT')
        bake(sails,[(NAME+'_Sails',[0,128,512,512],2048,10)])
    else:
        source=ART/'Level 1/CSC_Level_1_S_CON+PIL.blend'
        with bpy.data.libraries.load(str(source),link=False) as (src,dst):dst.objects=['Scaffolding']
        scaffold=dst.objects[0];scene.collection.objects.link(scaffold);bpy.data.scenes['Review'].collection.objects.link(scaffold)
        scaffold.name=RUIN+'_Scaffolding';scaffold.data=scaffold.data.copy();scaffold.modifiers.clear();scaffold.parent=None
        original=signature(scaffold);lo=Vector((2.6851577758789062,-227.5590057373047,0));hi=Vector((102.86904907226562,-150.65550231933594,0));center=(lo+hi)/2
        destination=Vector((36.99117,-24.16936192431123,0));scale=.70
        for v in scaffold.data.vertices:v.co=(v.co-center)*scale+destination
        scaffold.parent=rig;scaffold.vertex_groups.clear();g=scaffold.vertex_groups.new(name='Root');g.add(list(range(len(scaffold.data.vertices))),1,'REPLACE')
        mod=scaffold.modifiers.new('Tower skeleton','ARMATURE');mod.object=rig
        scaffold['role']='building_geometry';scaffold['export_role']='building_geometry';scaffold['source_asset_id']=asset
        scaffold['source_mesh']='Scaffolding';scaffold['source_blend']=str(source);scaffold['source_uniform_scale']=scale
        scaffold.data.materials[0]['external']='Pillage_Construction_01'
        # This native material is resolved by identity in AE. Give Blender the same
        # visible base texture for an editable source preview without changing UVs.
        mat=scaffold.data.materials[0];mat.use_nodes=True
        import xml.etree.ElementTree as E
        pantry=Path('C:/Program Files (x86)/Steam/steamapps/common/Sid Meier\'s Civilization VI SDK Assets/Civ6/pantry')
        mpath=next(pantry.rglob('Pillage_Construction_01.mtl'));data=mpath.read_text().replace('AssetObjects:','AssetObjects.');root=E.fromstring(data)
        entry=next(n for n in root.findall('.//Element') if n.find('m_ParamName') is not None and n.find('m_ParamName').get('text')=='BaseColor')
        texname=entry.find('m_ObjectName').get('text');dds=next(pantry.rglob(texname+'.dds'))
        n=mat.node_tree.nodes;bs=n.get('Principled BSDF');tex=n.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(dds));uv=n.new('ShaderNodeUVMap');uv.uv_map='UV1';mat.node_tree.links.new(uv.outputs[0],tex.inputs[0]);mat.node_tree.links.new(tex.outputs[0],bs.inputs['Base Color'])
        assert original['uv1']==signature(scaffold)['uv1'] and original['uv3']==signature(scaffold)['uv3']
        report.append(dict(scaffold_source=str(source),scaffold_uvs_preserved=True,uniform_scale=scale,position=list(destination),original_center=list(center)))
        objects.append(scaffold)
    for ob in objects:
        if ob.name in before:assert signature(ob)==before[ob.name],ob.name
        ob.data.uv_layers.active_index=0;ob.data.uv_layers['UV1'].active_render=True
    for s in bpy.data.scenes:
        if s.name in ('Export','Review'):s['atlas_release']=RELEASE;s['windmill_shared_material_revision']=True
    for im in bpy.data.images:
        if im.source=='FILE':im.filepath=str(Path(bpy.path.abspath(im.filepath)).resolve())
    bpy.ops.object.select_all(action='DESELECT')
    for ob in [rig,*objects]:ob.select_set(True)
    bpy.context.view_layer.objects.active=rig;bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/'masters'/(asset+'.blend')),relative_remap=False)
    io_export_cn6_b4.do_export(str(OUT/'staged/Geometries'/(asset+'.cn6')),True,True)
(OUT/'authoring-report.json').write_text(json.dumps(dict(bakes=report,user_geometry_UV1_UV3_weights_preserved=True),indent=2));print('SHARED_REVISION_AUTHORED',flush=True)
