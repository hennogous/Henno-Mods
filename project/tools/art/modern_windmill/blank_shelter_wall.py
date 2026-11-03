"""Remove the occluded modern base window; preserve shared UVs and AE assemblies.

Modes: Blender build, Python stage/publish. Output is a new version, never V9 overwrite.
"""
import sys, json, shutil, subprocess
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from modular_v9 import ROOT, ART, BASE, OLD, sha, dump

MOD = ROOT / 'Civ Supply Chains'
SOURCE = ART / 'Level 1/modern/revision-01-modular' / (BASE+'.blend')
DEST = ART / 'Level 1/modern/revision-02-blank-brick'
LIB = ART / 'Textures/CSC_Buildings_Modern'
RELEASE = '2026-10-27_Modern_r002'
WINDOW = 'CSC_Fixed_Front_Window_22_48'

def build(out):
    import bpy
    sys.path[:0] = [str(ROOT/'project/tools/blender'), str(ROOT/'project/tools/blender/scene_export')]
    import decode_blend as dec
    from csc_scene_validation import suspend_csc_repairs, validate_current_scene
    out.mkdir(parents=True, exist_ok=True)
    dump(out/'baseline.json', {'source':sha(SOURCE), 'runtime':{str(p.relative_to(MOD)):sha(p) for folder in ('Assets','ArtDefs','Geometries','Materials','Textures','XLPs') for p in (MOD/folder).iterdir() if p.is_file()}, 'library':{str(p.relative_to(LIB/'Current')):sha(p) for p in (LIB/'Current').rglob('*') if p.is_file()}})
    with suspend_csc_repairs():
        bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
        scene = bpy.data.scenes['Export']; review = bpy.data.scenes['Review']
        bpy.context.window.scene = scene
        victim = bpy.data.objects[WINDOW]
        assert len(victim.data.vertices)==4
        before = {o.name:([list(o.matrix_world@v.co) for v in o.data.vertices], [[list(x.uv) for x in uv.data] for uv in o.data.uv_layers]) for o in scene.objects if o.type=='MESH' and o != victim}
        bpy.data.objects.remove(victim, do_unlink=True)
        keep = [o for o in scene.objects if o.type=='MESH']
        mat = bpy.data.materials['CSC_BAKERS_Modern']
        nodes=mat.node_tree.nodes; links=mat.node_tree.links
        bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
        restore=[(l.from_socket,l.to_socket) for s in ('Base Color','Normal') for l in list(bs.inputs[s].links)]
        for s in ('Base Color','Normal'):
            for l in list(bs.inputs[s].links): links.remove(l)
        ao_node=next(n for n in nodes if n.type=='TEX_IMAGE' and (n.label or n.name)=='AO')
        oldim=ao_node.image
        bake=bpy.data.images.new(BASE+'_BlankWallAO', width=1024,height=1024,alpha=False)
        bake.colorspace_settings.name='Non-Color';ao_node.image=bake;nodes.active=ao_node
        bpy.ops.object.select_all(action='DESELECT')
        for o in keep:
            o.hide_set(False);o.hide_render=False;o.select_set(True);o.data.uv_layers.active_index=1
            # Invert the existing atlas allocation only for baking; no new unwrap.
            for d in o.data.uv_layers[1].data: d.uv=((d.uv.x*1024-4)/504,(d.uv.y*1024-516)/504)
        bpy.context.view_layer.objects.active=keep[0]
        scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.bake.margin=8
        bpy.ops.object.bake(type='AO', uv_layer='UV2')
        (out/'bakes').mkdir(exist_ok=True)
        bake.filepath_raw=str(out/'bakes'/(BASE+'.png'));bake.file_format='PNG';bake.save()
        ao_node.image=oldim
        for a,b in restore:links.new(a,b)
        for o in keep:
            for uv,values in zip(o.data.uv_layers,before[o.name][1]):
                for d,v in zip(uv.data,values):d.uv=v
            o.data.uv_layers.active_index=0;o.select_set(False)
            assert [list(o.matrix_world@v.co) for v in o.data.vertices]==before[o.name][0]
        folder=out/'master';folder.mkdir(exist_ok=True)
        shutil.copytree(SOURCE.parent/'textures',folder/'textures',dirs_exist_ok=True)
        for n in nodes:
            if n.type=='TEX_IMAGE':n.image.filepath='//textures/'+n.image.filepath.replace('\\','/').rsplit('/',1)[-1]
        bpy.context.window.scene=review
        bpy.ops.wm.save_as_mainfile(filepath=str(folder/(BASE+'.blend')),relative_remap=False)
        bpy.ops.wm.open_mainfile(filepath=str(folder/(BASE+'.blend')),load_ui=False,use_scripts=False)
        report=validate_current_scene();dump(folder/'validation.json',report);assert report['automated_pass'],report
        scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;scene.view_layers[0].update()
        groups={}
        for o in scene.objects:
            if o.type!='MESH':continue
            label='SiloSideSupports' if o.get('optional_silo_side_support') else 'Shelter' if 'Shelter_' in o.name or 'Support_Foot_' in o.name else 'Building'
            groups.setdefault(label,[]).append(dec.decode_mesh(o,o.matrix_world))
        model={'asset_id':BASE,'kind':'building','meshes':[dec.merge_meshes(BASE+'_'+k,v) for k,v in groups.items()]}
        dump(out/'model.json',model)
        dump(out/'edit.json',{'removed':WINDOW,'preserved_mesh_count':len(before),'remaining_geometry_and_UVs_unchanged':True,'vertices':sum(len(x['vertices']) for x in model['meshes']),'triangles':sum(len(x['triangles']) for x in model['meshes'])})
        print('EDITED',out,flush=True)

def stage(out):
    from PIL import Image, ImageChops
    import modular_v9_native as native
    import export_scene as exp
    # Create a self-contained new canonical atlas snapshot with only AO changed.
    lib=out/'library';shutil.copytree(LIB/'Current',lib,dirs_exist_ok=True)
    shutil.copy2(out/'bakes'/(BASE+'.png'),lib/'bakes'/(BASE+'.png'))
    from rebuild_modern_atlases import rebuild
    rebuild(lib)
    for p in (lib/'textures').iterdir():
        if p.stem!='CSC_Atlas_Modern_AO':assert sha(p)==sha(LIB/'Current/textures'/p.name),p
    old=Image.open(LIB/'Current/textures/CSC_Atlas_Modern_AO.png');new=Image.open(lib/'textures/CSC_Atlas_Modern_AO.png')
    box=ImageChops.difference(old,new).getbbox();assert box and box[2]<=512 and box[3]<=512,box
    shutil.copy2(lib/'textures/CSC_Atlas_Modern_AO.png',out/'master/textures/CSC_Atlas_Modern_AO.png')
    info=json.loads((lib/'library.json').read_text());info.update(release=RELEASE,source=str(DEST/(BASE+'.blend')),source_sha256=sha(out/'master'/(BASE+'.blend')),status='Blank brickwork at shelter junction; shared UVs and other atlas cells preserved',maps={p.name:sha(p) for p in (lib/'textures').iterdir()})
    dump(lib/'library.json',info)
    dst=out/'staged'
    for d in ('Assets','Geometries','Materials','Textures','CN6'):(dst/d).mkdir(parents=True,exist_ok=True)
    # The initial reusable AST accidentally named its mesh group as its material.
    # Use the existing Bakers material used by the historical Water Mill states.
    base_ast=MOD/'Assets'/(BASE+'.ast');fixed=base_ast.read_bytes()
    assert fixed.count(b'<m_ObjectName text="CSC_BAKERS"')==5
    fixed=fixed.replace(b'<m_ObjectName text="CSC_BAKERS"',b'<m_ObjectName text="CSC_BAKERS_E"')
    (dst/'Assets'/(BASE+'.ast')).write_bytes(fixed)
    # Existing dependency closure from live runtime, including attachments/states.
    resolver=native.Resolver(MOD,native.DEFAULT_SDK)
    for ident in (BASE,OLD):
        for state in ('Worked','Unworked','Construction','Pillaged','Unbuilt'):
            native.Assembly(resolver,state).asset((dst if ident==BASE else MOD)/'Assets'/(ident+'.ast'))
    for path in resolver.inputs:
        p=Path(path)
        if p.is_relative_to(MOD):
            q=dst/p.relative_to(MOD);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
    model=json.loads((out/'model.json').read_text())
    for m in model['meshes']:
        for mat in m['materials']:
            for img in mat['images'].values():img['sha256']=sha(img['path'])
    dump(out/'model.json',model)
    cn6=dst/'CN6'/(BASE+'.cn6');fgx=dst/'Geometries'/(BASE+'.fgx')
    exp.write_cn6(cn6,model);native.save(dst/'Geometries'/(BASE+'.geo'),exp.geometry(model,native.read(MOD/'Geometries'/(BASE+'.geo'))))
    converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe'
    r=subprocess.run([str(converter),str(cn6),str(fgx),'2'],cwd=converter.parent,capture_output=True,text=True)
    (out/'conversion.log').write_text(r.stdout+r.stderr);assert r.returncode==0
    exe,_=native.helper(out/'native-reader');npath=out/'native.json'
    subprocess.run([str(exe),str(exe.parent),str(fgx),str(npath)],cwd=exe.parent,check=True,capture_output=True)
    n=json.loads(npath.read_text());assert len(n['meshes'])==len(model['meshes']);err=0
    for a,b in zip(model['meshes'],n['meshes']):
        assert a['name']==b['name'] and a['triangles']==b['triangles'] and b['boneBindings']==['Bone']
        assert len(a['vertices'])==len(b['vertices'])
        for v,w in zip(a['vertices'],b['vertices']):
            values=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3']
            err=max(err,max(abs(x-y) for x,y in zip(v,values)))
            assert err<1e-4 and w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
    scalar=out/'scalar';scalar.mkdir(exist_ok=True);Image.open(lib/'textures/CSC_Atlas_Modern_AO.png').convert('RGB').getchannel('R').save(scalar/'CSC_Atlas_Modern_AO.png')
    subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8_UNORM','--ignore-srgb','-o',str(dst/'Textures'),str(scalar/'CSC_Atlas_Modern_AO.png')],check=True,capture_output=True)
    spec={'slot':'AO','size':[1024,1024],'format':'R8_UNORM'}
    dds=dst/'Textures/CSC_Atlas_Modern_AO.dds';exp.normalize_ao_dds(dds,spec,MOD/'Textures/CSC_Props_Shared_01_AO.dds');exp.validate_dds(dds,spec)
    changed=['Geometries/'+BASE+'.fgx','Geometries/'+BASE+'.geo','Textures/CSC_Atlas_Modern_AO.dds','Assets/'+BASE+'.ast']
    # Recheck staged visibility and references against the same saved ASTs.
    for p in dst.rglob('*'):
        if p.is_file():resolver.index[p.name.casefold()]={p}
    for ident in (BASE,OLD):
        for state in ('Worked','Unworked','Construction','Pillaged','Unbuilt'):native.Assembly(resolver,state).asset(dst/'Assets'/(ident+'.ast'))
    dump(out/'staging-validation.json',{'passed':True,'native_max_component_error':err,'AO_difference_bounds':box,'publish_files':changed,'mill_AST_unchanged':True,'base_AST_only_change':'five references to nonexistent CSC_BAKERS material corrected to existing CSC_BAKERS_E; placements/state visibility preserved'})
    print('STAGED',changed)

def publish(out):
    import modular_v9_native as native
    report=json.loads((out/'staging-validation.json').read_text());assert report['passed']
    assert json.loads((out/'master/validation.json').read_text())['automated_pass']
    cook=json.loads((out/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
    baseline=json.loads((out/'baseline.json').read_text());assert sha(SOURCE)==baseline['source']
    assert all(sha(MOD/k)==v for k,v in baseline['runtime'].items()),'Concurrent runtime edit'
    assert all(sha(LIB/'Current'/k)==v for k,v in baseline['library'].items()),'Concurrent library edit'
    assert not DEST.exists() and not (LIB/'Releases'/RELEASE).exists()
    payload={}
    for p in (out/'master').rglob('*'):
        if p.is_file() and p.suffix!='.blend1':payload[DEST/p.relative_to(out/'master')]=p.read_bytes()
    payload[DEST/(BASE+'.cn6')]=(out/'staged/CN6'/(BASE+'.cn6')).read_bytes()
    for p in (out/'library').rglob('*'):
        if p.is_file():
            for directory in (LIB/'Current',LIB/'Releases'/RELEASE):payload[directory/p.relative_to(out/'library')]=p.read_bytes()
    payload[LIB/'CURRENT.json']=json.dumps({'release':RELEASE,'current':'Current','snapshot':'Releases/'+RELEASE,'manifest':'Current/library.json'},indent=2).encode()
    for rel in report['publish_files']:payload[MOD/rel]=(out/'staged'/rel).read_bytes()
    backup=out/'publication-backup';backup.mkdir();rows=[]
    for i,(p,data) in enumerate(payload.items()):
        row={'destination':str(p),'before':sha(p) if p.exists() else None}
        if p.exists():q=backup/f'{i:04}-{p.name}';shutil.copy2(p,q);row['backup']=str(q)
        rows.append(row)
    dump(backup/'manifest.json',rows)
    for row,(p,data) in zip(rows,payload.items()):
        assert (sha(p) if p.exists() else None)==row['before'];p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data);row['after']=sha(p)
    changed=set(report['publish_files']);assert all(sha(MOD/k)==v for k,v in baseline['runtime'].items() if Path(k).as_posix() not in changed)
    dump(out/'publication-report.json',{'installed':True,'files':rows,'source':str(DEST/(BASE+'.blend')),'placements_ArtDefs_and_mill_AST_unchanged':True,'base_AST_material_references_repaired':True,'in_game_tested':False})
    native.cache(out)
    print('PUBLISHED',len(rows),'files')

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    mode,path=args;globals()[mode](Path(path))
