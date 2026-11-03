"""Inspect and migrate editable masters for the L2 placement update."""
import json
import sys
from pathlib import Path
import bpy
import math
import shutil
from mathutils import Matrix, Vector

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'project/tools/art'))
from storage_pivot_trial_blender import inventory, disable_repairs
ART=Path('C:/Users/Shadow/Desktop/Working Files/3D Art')
OUT=Path('C:/Users/Shadow/Desktop/Codex/L2-placement-20261025')

def inspect():
    disable_repairs()
    paths=list((ART/'Level 2').glob('*.blend'))
    paths=[p for p in paths if 'pre-ao' not in p.name]
    paths+=list((ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants').rglob('*.blend'))
    for folder in ['BAKERS/Bakery','TAILORS/Tailor/revision-10-vertex-budget',
                   'TAILORS/Fashion House/revision-12-garden-path']:
        paths+=list((ART/folder).glob('*.blend'))
    rows=[]
    for p in paths:
        r=inventory(p);rows.append(r)
        print(p,[(o['name'],o.get('vertices'),o.get('bounds'),o['parent']) for o in r['objects'] if o['type'] in ['MESH','ARMATURE']],flush=True)
    (OUT/'source-inventory.json').write_text(json.dumps(rows,indent=2,default=str))

def build():
    sys.path.insert(0,str(ROOT/'project/tools/blender'))
    from ae_asset_render_blender import Builder
    from csc_scene_validation import validate_current_scene
    jobs=json.loads((OUT/'geometry-jobs.json').read_text())
    materials=json.loads((OUT/'materials.json').read_text())
    variants=json.loads((OUT/'variant-sources.json').read_text())
    reports=[]
    for job in jobs:
        selected_jobs=sys.argv[sys.argv.index('--')+2:]
        if selected_jobs and job['name'] not in selected_jobs:continue
        bpy.ops.wm.read_factory_settings(use_empty=True)
        raw=json.loads(Path(job['native']).read_text())
        source=OUT/'masters'/job['name'];source.mkdir(parents=True,exist_ok=True)
        export=bpy.context.scene;export.name='Export';export['asset_id']=job['name']
        export['geometry_authority']='Editable native geometry, preserved UVs/normals and saved AE fixed-prop placements; 25 October 2026.'
        builder=Builder(dict(output=str(source),materials=materials,warnings=[]),'sv')
        export.name='Export'
        if 'placement_authority' in export:del export['placement_authority']
        data=bpy.data.armatures.new(raw['models'][0]['name']);rig=bpy.data.objects.new(raw['models'][0]['name'],data)
        export.collection.objects.link(rig);bpy.context.view_layer.objects.active=rig;rig.select_set(True)
        bpy.ops.object.mode_set(mode='EDIT')
        # The CN6 exporter creates the synthetic model root from the armature;
        # do not also create it as an editable bone.
        native_bones=raw['models'][0]['bones']
        for bone in native_bones[1:]:
            b=data.edit_bones.new(bone['name']);b.head=(0,0,0);b.tail=(0,1,0)
            inv=bone['inverseWorld'];b.matrix=Matrix([inv[i:i+4] for i in range(0,16,4)]).transposed().inverted();b.length=1
        for bone in native_bones[1:]:
            if bone['parent']>0:data.edit_bones[bone['name']].parent=data.edit_bones[native_bones[bone['parent']]['name']]
        bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
        meshes=[]
        for entry in raw['meshes']:
            verts=entry['vertices'];mesh=bpy.data.meshes.new(entry['name'])
            mesh.from_pydata([v['position'] for v in verts],[],[t[:3] for t in entry['triangles']]);mesh.update()
            for i,key in enumerate(('uv','uv2','uv3'),1):
                layer=mesh.uv_layers.new(name=f'UV{i}')
                for loop in mesh.loops:
                    u,v=verts[loop.vertex_index][key];layer.data[loop.index].uv=(u,1-v)
            mesh.polygons.foreach_set('use_smooth',[True]*len(mesh.polygons))
            mesh.normals_split_custom_set([verts[l.vertex_index]['normal'] for l in mesh.loops])
            for group in job['groups'][entry['name']]:
                key=job['materials'][entry['name']][group]
                mat=builder.material(key,3)
                # Blender material slot names are the native GEO group identities.
                if mat.name!=group:
                    mat=mat.copy();mat.name=group
                mat['ae_group']=group;mat['ae_material']=materials[key]['id']
                if 'decal' in materials[key]['shader'].lower():
                    bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
                    base=next((n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE' and n.label=='BaseColor'),None)
                    if base:mat.node_tree.links.new(base.outputs['Alpha'],bs.inputs['Alpha'])
                mesh.materials.append(mat)
            for group in entry['groups']:
                for polygon in mesh.polygons[group['first']:group['first']+group['count']]:polygon.material_index=group['material']
            ob=bpy.data.objects.new(entry['name'],mesh);export.collection.objects.link(ob);ob.parent=rig
            ob['export_role']='fixed_geometry' if entry['name'].startswith('CSC_Fixed_') else 'building_geometry'
            ob['source_asset_id']=job['name']
            ob['source_geometry_id']=job['name']
            keys=ob.vertex_groups.new(name='VERTEX_KEYS')
            mesh['originalTangentsBinormals']={str(i+1):[x for k in ['normal','tangent','binormal'] for x in v[k]] for i,v in enumerate(verts)}
            for i in range(len(verts)):keys.add([i],(i+1)/2000000,'REPLACE')
            for name in entry['boneBindings']:
                group=ob.vertex_groups.new(name=name)
                indices=[i for i,v in enumerate(verts) if any(entry['boneBindings'][bi]==name and w for bi,w in zip(v['boneIndices'],v['boneWeights']))]
                if indices:group.add(indices,1,'REPLACE')
            ob.modifiers.new('Armature','ARMATURE').object=rig
            meshes.append(ob)
        for image in builder.images.values():
            if image.packed_file:image.unpack(method='REMOVE')
            image.filepath='//textures/'+Path(image.filepath).name
        review=bpy.data.scenes.new('Review')
        for ob in [rig,*meshes]:review.collection.objects.link(ob)
        world=bpy.data.worlds.new('Review World');world.use_nodes=True
        bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.7,.8,1,1);bg.inputs['Strength'].default_value=.65
        for sc,view,exposure in [(export,'AgX',.35),(review,'Standard',-.1)]:
            sc.world=world;sc.render.engine='CYCLES';sc.view_settings.view_transform=view;sc.view_settings.exposure=exposure;sc.view_settings.gamma=1
        light=bpy.data.objects.new('Review_Key',bpy.data.lights.new('Review_Key','SUN'));review.collection.objects.link(light)
        light.data.energy=3.2;light.data.color=(1,.92,.8);light.data.angle=math.radians(6);light.data.use_shadow=True
        light.rotation_euler=(math.radians(25),math.radians(-30),math.radians(-25))
        profiles=json.loads((OUT/'staged/ae_render_camera_presets.json').read_text())['classes']
        level='L3' if any(s in job['name'] for s in ['Fashion','Cafe']) else 'L2'
        cam=bpy.data.objects.new('Review_Camera',bpy.data.cameras.new('Review_Camera'));review.collection.objects.link(cam)
        cam.matrix_world=Matrix(profiles[level]['sv']['matrix_world']);cam.data.type='ORTHO';cam.data.ortho_scale=profiles[level]['sv']['ortho_scale'];review.camera=cam
        bpy.context.window.scene=export
        path=source/(job['name']+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
        report=validate_current_scene()
        (source/'validation.json').write_text(json.dumps(report,indent=2))
        assert report['error_count']==0,(job['name'],[f for f in report['findings'] if f['severity']=='error'])
        error=0
        for entry in raw['meshes']:
            ob=bpy.data.objects[entry['name']]
            error=max(error,max((ob.matrix_world@v.co-Vector(r['position'])).length for v,r in zip(ob.data.vertices,entry['vertices'])))
        assert error<.0001
        reports.append(dict(name=job['name'],source=str(path),destination=job['source'],position_error=error,vertices=report['counts']['main_vertices'],warnings=report['warning_count']))
        for variant in variants:
            if variant['job']==job['name']:
                target=source/(Path(variant['source']).name)
                bpy.context.scene['assembly_variant']=variant['variant']
                bpy.ops.wm.save_as_mainfile(filepath=str(target),relative_remap=False)
                reports.append(dict(name=variant['variant'],source=str(target),destination=variant['source'],position_error=error,shared_geometry=job['name']))
        print('SOURCE_PASS',job['name'],report['counts']['main_vertices'],flush=True)
    if selected_jobs:
        old=json.loads((OUT/'source-build-report.json').read_text())
        reports=[r for r in old if r['name'] not in {j['name'] for j in reports}]+reports
    (OUT/'source-build-report.json').write_text(json.dumps(reports,indent=2))

def finish_sources():
    sys.path.insert(0,str(ROOT/'project/tools/blender'))
    from csc_scene_validation import validate_current_scene
    sys.path.insert(0,str(Path.home()/'AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons'))
    import io_export_cn6 as cn6
    rows=json.loads((OUT/'source-build-report.json').read_text())
    name='CSC_ALL_Stage_3_Cobble_Decals';source=OUT/'masters'/(name+'_Rectangular');source.mkdir(exist_ok=True)
    (source/'textures').mkdir(exist_ok=True)
    for p in (OUT/'cobbles/rectangular/textures').glob('*.png'):shutil.copy2(p,source/'textures'/p.name)
    bpy.ops.wm.open_mainfile(filepath=str(OUT/'masters'/name/(name+'.blend')),load_ui=False,use_scripts=False)
    for mat in bpy.data.materials:
        if not mat.use_nodes:continue
        mat['ae_material']='CSC_ALL_Stage_3_Cobble_Decals'
        for node in mat.node_tree.nodes:
            if node.type=='TEX_IMAGE' and node.label in ['BaseColor','Heightmap']:
                suffix='B' if node.label=='BaseColor' else 'H';p=source/'textures'/('CSC_ALL_Stage_3_Cobbles_02_'+suffix+'.png')
                image=bpy.data.images.load(str(p),check_existing=True);image.colorspace_settings.name='sRGB' if suffix=='B' else 'Non-Color';image.filepath='//textures/'+p.name;node.image=image
    for image in list(bpy.data.images):
        if not image.users:bpy.data.images.remove(image)
    path=source/(name+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
    rows=[r for r in rows if r['name']!=name+'_Rectangular']
    rows.append(dict(name=name+'_Rectangular',source=str(path),destination=str(ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants/rectangular'/(name+'.blend')),shared_geometry=name))
    (OUT/'source-build-report.json').write_text(json.dumps(rows,indent=2))
    checks=[]
    for row in rows:
        bpy.ops.wm.open_mainfile(filepath=row['source'],load_ui=False,use_scripts=False)
        bpy.context.window.scene=bpy.data.scenes['Export']
        report=validate_current_scene();assert not report['error_count'],(row['name'],report['findings'])
        folder=OUT/'source-export';folder.mkdir(exist_ok=True)
        target=folder/(row['name']+'.cn6')
        objects=[o for o in bpy.context.scene.objects if o.type in ['ARMATURE','MESH']]
        cn6.csc_do_export_selected(str(target),objects)
        assert target.is_file()
        checks.append(dict(name=row['name'],source=row['source'],report=report,cn6=str(target)))
        print('FINAL_SAVED_SOURCE_PASS',row['name'],flush=True)
    (OUT/'final-source-validation.json').write_text(json.dumps(checks,indent=2))

def preserve_frames():
    """Populate the installed exporter's supported native shading-frame channel."""
    jobs={j['name']:j for j in json.loads((OUT/'geometry-jobs.json').read_text())}
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        job=jobs[row.get('shared_geometry',row['name'])];raw=json.loads(Path(job['native']).read_text())
        bpy.ops.wm.open_mainfile(filepath=row['source'],load_ui=False,use_scripts=False)
        for entry in raw['meshes']:
            ob=bpy.data.objects[entry['name']];verts=entry['vertices'];ob.vertex_groups.clear()
            keys=ob.vertex_groups.new(name='VERTEX_KEYS')
            ob.data['originalTangentsBinormals']={str(i+1):[x for k in ['normal','tangent','binormal'] for x in v[k]] for i,v in enumerate(verts)}
            for i in range(len(verts)):keys.add([i],(i+1)/2000000,'REPLACE')
            for name in entry['boneBindings']:
                group=ob.vertex_groups.new(name=name)
                indices=[i for i,v in enumerate(verts) if any(entry['boneBindings'][bi]==name and w for bi,w in zip(v['boneIndices'],v['boneWeights']))]
                if indices:group.add(indices,1,'REPLACE')
        bpy.ops.wm.save_as_mainfile(filepath=row['source'],relative_remap=False)

def camera_verify():
    sys.path.insert(0,str(ROOT/'project/tools/blender'))
    from ae_asset_render_blender import Builder
    from render_ae_asset import PRESETS
    from bpy_extras.object_utils import world_to_camera_view
    profiles=[json.loads((OUT/p).read_text())['classes']['L2'] for p in ['before/project/tools/blender/ae_render_camera_presets.json','staged/ae_render_camera_presets.json']]
    native=json.loads((OUT/'native-before/CSC_TAILORS_Tailor.json').read_text())
    points=[Vector(v['position']) for m in native['meshes'] for v in m['vertices']]
    T=Matrix(json.loads((OUT/'transform.json').read_text())['wrapper']);result={}
    for mode in ['icon','sv']:
        values=[]
        for i,profile in enumerate(profiles):
            bpy.ops.wm.read_factory_settings(use_empty=True)
            builder=Builder(dict(output=str(OUT),warnings=[],settings=dict(presets=PRESETS,samples=1,resolution=1024,camera_class='L2',fixed_camera=profile)),mode)
            mesh=bpy.data.meshes.new('Landmarks');mesh.from_pydata(points if i==0 else [T@p for p in points],[],[])
            ob=bpy.data.objects.new('Landmarks',mesh);bpy.context.scene.collection.objects.link(ob);builder.objects=[ob]
            builder.setup();bpy.context.view_layer.update();scene=bpy.context.scene
            values.append([world_to_camera_view(scene,scene.camera,v.co) for v in ob.data.vertices])
        error=max(abs(a[k]-b[k])*1024 for a,b in zip(*values) for k in [0,1]);assert error<.001
        result[mode]=dict(vertices=len(points),maximum_pixel_error_at_1024=error)
    (OUT/'camera-registration.json').write_text(json.dumps(result,indent=2));print('CAMERA_REGISTRATION',result)

def shared_palette():
    """Keep the reusable starter's existing Bakers palette while fixing paths."""
    target=OUT/'masters/CSC_Level_2/CSC_Level_2.blend'
    bpy.ops.wm.open_mainfile(filepath=str(target),load_ui=False,use_scripts=False)
    with bpy.data.libraries.load(str(OUT/'masters/CSC_BAKERS_Bakery/CSC_BAKERS_Bakery.blend'),link=False) as (src,dst):
        dst.materials=[n for n in src.materials if n=='CSC_Level_2_Bldg']
    mat=dst.materials[0];assert mat.get('ae_material')=='CSC_BAKERS_E'
    ob=bpy.data.objects['CSC_Level_2_Bldg'];old=ob.data.materials[0];ob.data.materials[0]=mat
    bpy.data.materials.remove(old);mat.name='CSC_Level_2_Bldg'
    for n in mat.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image:
            p=Path(bpy.path.abspath(n.image.filepath));dest=target.parent/'textures'/p.name
            if p!=dest:shutil.copy2(p,dest)
            n.image.filepath='//textures/'+p.name
    bpy.ops.wm.save_as_mainfile(filepath=str(target),relative_remap=False)
    jobs=json.loads((OUT/'geometry-jobs.json').read_text());byname={j['name']:j for j in jobs}
    byname['CSC_Level_2']['materials']['CSC_Level_2_Bldg']=byname['CSC_BAKERS_Bakery']['materials']['CSC_Level_2_Bldg']
    (OUT/'geometry-jobs.json').write_text(json.dumps(jobs,indent=2))

def installed_verify():
    sys.path.insert(0,str(ROOT/'project/tools/blender'))
    from csc_scene_validation import validate_current_scene
    checks=[]
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        bpy.ops.wm.open_mainfile(filepath=row['destination'],load_ui=False,use_scripts=False)
        bpy.context.window.scene=bpy.data.scenes['Export'];report=validate_current_scene()
        assert report['error_count']==0,(row['name'],report['findings'])
        checks.append(dict(source=row['destination'],automated_pass=True,warnings=report['warning_count']))
    (OUT/'installed-source-validation.json').write_text(json.dumps(checks,indent=2))
    print('INSTALLED_SOURCE_PASS',len(checks))

def export_identities():
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        if row['name'] not in ['CSC_BAKERS_Cafe','CSC_BAKERS_Cafe_2','CSC_BAKERS_Bakery_PIL_Decals']:continue
        bpy.ops.wm.open_mainfile(filepath=row['source'],load_ui=False,use_scripts=False)
        rig=next(o for o in bpy.data.scenes['Export'].objects if o.type=='ARMATURE')
        rig.name=rig.data.name=row.get('shared_geometry',row['name'])
        # Both Cafe variants intentionally export the same main geometry.
        if row['name']=='CSC_BAKERS_Cafe_2':rig.name=rig.data.name='CSC_BAKERS_Cafe'
        bpy.ops.wm.save_as_mainfile(filepath=row['source'],relative_remap=False)

if __name__=='__main__':
    globals()[sys.argv[sys.argv.index('--')+1]]()
