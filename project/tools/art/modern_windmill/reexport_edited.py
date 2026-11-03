"""Prepare a selective export from Henno's edited modern-mill master, never rebuild it."""
import sys, json, hashlib, shutil, math
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
NAME='CSC_BAKERS_Wind_Mill_Modern'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def prepare(source,out):
    import bpy
    sys.path[:0]=[str(ROOT/'project/tools/blender/scene_export'),str(ROOT/'project/tools/blender')]
    import decode_blend as dec
    from csc_scene_validation import suspend_csc_repairs
    out.mkdir(parents=True,exist_ok=False);(out/'textures').mkdir()
    source_hash=sha(source)
    mod=ROOT/'Civ Supply Chains'
    protected=list((mod/'Assets').glob(NAME+'*.ast'))+list((mod/'ArtDefs').glob('*.artdef'))+list((mod/'XLPs').glob('*.xlp'))+list(mod.glob('*.civ6proj'))
    destinations=list((mod/'Geometries').glob(NAME+'.*'))+list((mod/'Textures').glob(NAME+'_*.dds'))+list((mod/'Textures').glob(NAME+'_*.tex'))
    baseline={str(p.relative_to(mod)):sha(p) for p in set(protected+destinations)}
    (out/'baseline.json').write_text(json.dumps({'source':str(source),'source_sha256':source_hash,'files':baseline,'protected':[str(p.relative_to(mod)) for p in protected]},indent=2))
    with suspend_csc_repairs():
        bpy.ops.wm.open_mainfile(filepath=str(source),load_ui=False,use_scripts=False)
        scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review']
        added=[]
        for ob in list(review.objects):
            if ob.type=='MESH' and ob.get('export_role') in ('building_geometry','fixed_geometry') and not ob.get('csc_export_exclude') and ob.name not in scene.objects:
                scene.collection.objects.link(ob);added.append(ob.name)
        bpy.context.window.scene=scene;scene.view_layers[0].update()
        meshes=[o for o in scene.objects if o.type=='MESH' and o.get('export_role') in ('building_geometry','fixed_geometry') and not o.get('csc_export_exclude')]
        assert meshes and all(not o.hide_render for o in meshes)
        def unchanged_signature(o):
            return {'vertices':[list(v.co) for v in o.data.vertices],'faces':[list(p.vertices) for p in o.data.polygons],
                    'matrix':[list(r) for r in o.matrix_world],
                    'uv1':[list(d.uv) for d in o.data.uv_layers[0].data],
                    'uv3':[list(d.uv) for d in o.data.uv_layers[2].data]}
        signatures={o.name:unchanged_signature(o) for o in meshes}
        materials={m for o in meshes for m in o.data.materials};assert len(materials)==1
        mat=next(iter(materials));assert mat.name==NAME
        nodes={n.label or n.name:n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'}
        info=dec.material(mat)
        for ch in ('B','N','G','M','E'):
            dest=out/'textures'/f'{NAME}_{ch}.png';shutil.copy2(info['images'][ch]['path'],dest)
            im=bpy.data.images.load(str(dest),check_existing=False);im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';nodes[ch].image=im
        bpy.ops.object.select_all(action='DESELECT')
        for o in meshes:
            if o.data.users>1:o.data=o.data.copy()
            o.hide_set(False);o.select_set(True);o.data.uv_layers.active_index=1
        bpy.context.view_layer.objects.active=meshes[0]
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.008,area_weight=.8,scale_to_bounds=True)
        bpy.ops.object.mode_set(mode='OBJECT')
        links=mat.node_tree.links;bs=next(n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED')
        restore=[(l.from_socket,l.to_socket) for slot in ('Base Color','Normal') for l in list(bs.inputs[slot].links)]
        for slot in ('Base Color','Normal'):
            for l in list(bs.inputs[slot].links):links.remove(l)
        links.new(nodes['B'].outputs['Color'],bs.inputs['Base Color'])
        ao=bpy.data.images.new(NAME+'_AO_reexport',width=2048,height=2048,alpha=False);ao.colorspace_settings.name='Non-Color'
        nodes['AO'].image=ao;mat.node_tree.nodes.active=nodes['AO']
        scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.bake.margin=6
        bpy.ops.object.bake(type='AO',uv_layer='UV2')
        ao.filepath_raw=str(out/'textures'/f'{NAME}_AO.png');ao.file_format='PNG';ao.save()
        for a,b in restore:links.new(a,b)
        for o in meshes:
            assert unchanged_signature(o)==signatures[o.name],o.name
            o.data.uv_layers.active_index=0;o.select_set(False)
        for ch in ('B','N','G','M','E','AO'):nodes[ch].image.filepath='//textures/'+f'{NAME}_{ch}.png'
        bpy.context.window.scene=review
        bpy.ops.wm.save_as_mainfile(filepath=str(out/(NAME+'.blend')),relative_remap=False)
        for ch in ('B','N','G','M','E','AO'):nodes[ch].image.reload()
        bpy.context.window.scene=scene;scene.view_layers[0].update()
        decoded=[dec.decode_mesh(o,o.matrix_world) for o in meshes]
        parts=[dec.merge_meshes(NAME+'_'+label,[m for m in decoded if m['role']==role]) for role,label in [('building_geometry','Building'),('fixed_geometry','Stock')]]
        assert all(p['vertices'] for p in parts)
        (out/'model.json').write_text(json.dumps({'asset_id':NAME,'kind':'building','meshes':parts}))
        report={'source':str(source),'source_unchanged':sha(source)==source_hash,'added_review_objects':added,'geometry_and_uv1_uv3_preserved':True,
                'objects':[{'name':o.name,'role':o.get('export_role'),'matrix_world':signatures[o.name]['matrix']} for o in meshes],
                'vertices':sum(len(p['vertices']) for p in parts),'triangles':sum(len(p['triangles']) for p in parts)}
        assert report['source_unchanged'];(out/'prepared-report.json').write_text(json.dumps(report,indent=2));print('PREPARED',report['vertices'],report['triangles'],added,flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:]
    prepare(Path(args[0]),Path(args[1]))
