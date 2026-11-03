"""Editable combined Wind Mill masters and native-motion authoring validation."""
import sys,json,math,importlib
from pathlib import Path
import bpy,numpy as np
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'project/tools/blender'));sys.path.insert(0,str(ROOT/'project/tools/art'))
sys.path.insert(0,str(Path.home()/'AppData/Roaming/Blender Foundation/Blender/5.1/scripts/addons'))
sys.path.insert(0,str(Path.home()/'.codex/skills/civ6-art/scripts'))
import io_import_cn6,io_export_cn6
from civ6_animation import core
from ae_asset_render_blender import Builder
from csc_scene_validation import validate_current_scene
from migrate_legacy_prop_atlas_blender import frame
OUT=Path('C:/Users/Shadow/Desktop/Codex/Windmill-bundled-tower-20261026')

def build():
    jobs=json.loads((OUT/'geometry-jobs.json').read_text());materials=json.loads((OUT/'materials.json').read_text());reports=[]
    for job in jobs:
        name=job['name'];bpy.ops.wm.read_factory_settings(use_empty=True)
        io_import_cn6.do_import(str(OUT/'staged/Geometries'/(name+'.cn6')),True)
        if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
        for ob in bpy.data.objects:
            if ob.type=='MESH':ob.name=ob.name.removesuffix('#M');ob.data.materials.clear()
        for mat in list(bpy.data.materials):bpy.data.materials.remove(mat)
        raw=json.loads(Path(job['native']).read_text());rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
        rig.name=raw['models'][0]['name'];rig['civ6_root_name']=rig.name
        folder=OUT/'masters'/name;folder.mkdir(parents=True,exist_ok=True)
        export=bpy.context.scene;builder=Builder(dict(output=str(folder),materials=materials,warnings=[]),'sv');export.name='Export'
        del export['placement_authority'];export['asset_id']=name
        export['geometry_authority']='Forked saved CSC Level 1 S and tower geometry; regular Wind Mill placement shared by both variants.'
        export['animation_contract']='Reuse CSC_BAKERS_Wind_Mill_Tower_Turn unchanged; preserve internal model identity, Root/Sails bones and static mount/pivot offset.'
        group_materials={}
        for entry in raw['meshes']:
            ob=bpy.data.objects[entry['name']];ob['export_role']='building_geometry';ob['source_asset_id']=name;ob['source_geometry_id']=name
            # The legacy importer repeats the last triangle at each mesh boundary.
            # Retain its bone-axis conversion, but build exact native mesh topology.
            mesh=bpy.data.meshes.new(entry['name']);mesh.from_pydata([v['position'] for v in entry['vertices']],[],[t[:3] for t in entry['triangles']]);mesh.update();ob.data=mesh
            for i,key in enumerate(['uv','uv2','uv3']):
                layer=mesh.uv_layers.new(name=f'UV{i+1}')
                for loop in mesh.loops:
                    u,v=entry['vertices'][loop.vertex_index][key];layer.data[loop.index].uv=(u,1-v)
            mesh.polygons.foreach_set('use_smooth',[True]*len(mesh.polygons));mesh.normals_split_custom_set([entry['vertices'][l.vertex_index]['normal'] for l in mesh.loops])
            for group in entry['groups']:
                for p in mesh.polygons[group['first']:group['first']+group['count']]:p.material_index=group['material']
            ob.vertex_groups.clear()
            for bi,bone in enumerate(entry['boneBindings']):
                vg=ob.vertex_groups.new(name=bone)
                for i,v in enumerate(entry['vertices']):
                    weight=sum(w for j,w in zip(v['boneIndices'],v['boneWeights']) if j==bi)/255
                    if weight:vg.add([i],weight,'REPLACE')
            ob.data.materials.clear()
            for group in job['groups'][entry['name']]:
                key=job['materials'][entry['name']][group]
                if (group,key) not in group_materials:
                    template=builder.material(key,3);template.name='_input_'+key
                    mat=template.copy();mat.name=group;mat['ae_group']=group;mat['ae_material']=materials[key]['id'];group_materials[group,key]=mat
                ob.data.materials.append(group_materials[group,key])
            # Positive native-frame keys avoid the importer's zero-key special case.
            if ob.vertex_groups.get('VERTEX_KEYS'):ob.vertex_groups.remove(ob.vertex_groups['VERTEX_KEYS'])
            keys=ob.vertex_groups.new(name='VERTEX_KEYS');ob.data['originalTangentsBinormals']={str(i+1):[x for k in ['normal','tangent','binormal'] for x in v[k]] for i,v in enumerate(entry['vertices'])}
            for i in range(len(entry['vertices'])):keys.add([i],(i+1)/2000000,'REPLACE')
        for image in builder.images.values():
            if image.packed_file:image.unpack(method='REMOVE')
            image.filepath='//textures/'+Path(image.filepath).name
        world=bpy.data.worlds.new('Review World');world.use_nodes=True
        bg=next(n for n in world.node_tree.nodes if n.type=='BACKGROUND');bg.inputs['Color'].default_value=(.7,.8,1,1);bg.inputs['Strength'].default_value=.65
        review=bpy.data.scenes.new('Review')
        for ob in export.objects:review.collection.objects.link(ob)
        for sc,view,exp in [(export,'AgX',.35),(review,'Standard',-.1)]:
            sc.world=world;sc.render.engine='CYCLES';sc.view_settings.view_transform=view;sc.view_settings.exposure=exp;sc.view_settings.gamma=1
        light=bpy.data.objects.new('Review_Key',bpy.data.lights.new('Review_Key','SUN'));review.collection.objects.link(light)
        light.data.energy=3.2;light.data.color=(1,.92,.8);light.data.angle=math.radians(6);light.rotation_euler=tuple(map(math.radians,(25,-30,-25)))
        cam=bpy.data.objects.new('Review_Camera',bpy.data.cameras.new('Review_Camera'));review.collection.objects.link(cam);cam.data.type='ORTHO';review.camera=cam;frame(review);review.render.resolution_x=review.render.resolution_y=800
        bpy.context.window.scene=export
        if not name.endswith('_CON+PIL'):
            core.import_na2(OUT/'motion-after/clip.na2',rig,action_name='Wind Mill — original eight-second turn')
            motion=core.parse_na2(OUT/'motion-after/clip.na2')[0];maximum=0
            nativebones={b['name']:b for b in raw['models'][0]['bones']}
            for f in range(motion['count']):
                export.frame_set(f+1)
                for entry in raw['meshes']:
                    bone=entry['boneBindings'][0];points=np.array([[*v['position'],1] for v in entry['vertices']]).T
                    native=np.array(motion['tracks'][bone][f]).reshape(4,4).T@np.array(nativebones[bone]['inverseWorld']).reshape(4,4).T
                    authored=np.array(rig.matrix_world@rig.pose.bones[bone].matrix@rig.data.bones[bone].matrix_local.inverted())
                    maximum=max(maximum,float(np.max(abs((native-authored)@points))))
            assert maximum<.001,maximum
            (OUT/'authoring-motion.json').write_text(json.dumps(dict(frames=241,max_vertex_error=maximum)))
            export.frame_set(1)
        path=folder/(name+'.blend');bpy.context.preferences.filepaths.save_version=0
        bpy.ops.wm.save_as_mainfile(filepath=str(path),relative_remap=False)
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export']
        report=validate_current_scene();(folder/'validation.json').write_text(json.dumps(report,indent=2))
        assert report['error_count']==0,[f for f in report['findings'] if f['severity']=='error']
        target=OUT/'source-export'/(name+'.cn6');target.parent.mkdir(exist_ok=True)
        io_export_cn6.csc_do_export_selected(str(target),[o for o in bpy.context.scene.objects if o.type in ['MESH','ARMATURE']])
        reports.append(dict(name=name,source=str(path),destination=job['source'],warnings=report['warning_count']))
        bpy.context.window.scene=bpy.data.scenes['Review'];review=bpy.context.scene
        if not name.endswith('_CON+PIL'):
            for f in [1,31]:
                review.frame_set(f);review.render.filepath=str(OUT/f'combined-frame-{f}.png');bpy.ops.render.render(write_still=True)
        else:
            bpy.data.objects['Scaffolding'].hide_render=True
            for state in ['Construction','Pillaged']:
                for ob in review.objects:
                    if ob.type=='MESH' and 'Scaffolding' in ob.name and ob.name!='Scaffolding':ob.hide_render=state=='Pillaged'
                review.render.filepath=str(OUT/f'combined-{state}.png');bpy.ops.render.render(write_still=True)
    (OUT/'source-build-report.json').write_text(json.dumps(reports,indent=2))

def verify():
    reports=[]
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        bpy.ops.wm.open_mainfile(filepath=row['destination'],load_ui=False,use_scripts=False);bpy.context.window.scene=bpy.data.scenes['Export']
        report=validate_current_scene();assert not report['error_count'],report
        reports.append(dict(name=row['name'],errors=report['error_count'],warnings=report['warning_count']))
    (OUT/'installed-source-validation.json').write_text(json.dumps(reports,indent=2))
if __name__=='__main__':globals()[sys.argv[sys.argv.index('--')+1]]()
