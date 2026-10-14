"""Inspect and rebake the existing Storage S/M shared AO allocation (Blender)."""
import bpy, json, sys, hashlib, numpy as np, math, shutil
from pathlib import Path

ROOT = Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Storage')
OUT = Path(r'C:\Users\Shadow\Desktop\Codex\CSC_Storage_SM\ao-rebake-20261012')
FILES = [ROOT / f'Storage_{s}' / f'CSC_Storage_{s}{suffix}.blend'
         for s in ('S', 'M', 'L') for suffix in ('', '_CON+PIL')]
FILES += [ROOT/'Storage_L/CSC_Storage_L_Crane.blend', ROOT.parent/'Props/CSC_Storage_LeanTo.blend']
AO = ROOT.parent/'Textures/CSC_Atlas_AO2.png'
REPO = Path(__file__).resolve().parents[3]

def signature():
    """Geometry, transforms, UV1/UV3 and assignments must not change."""
    rows=[]
    for o in bpy.data.objects:
        r=dict(name=o.name,type=o.type,matrix=[list(v) for v in o.matrix_world],parent=o.parent.name if o.parent else None)
        if o.type=='MESH':
            r.update(vertices=[list(v.co) for v in o.data.vertices],faces=[list(p.vertices) for p in o.data.polygons],
                uv={u.name:[list(d.uv) for d in u.data] for u in o.data.uv_layers if u.name!='UV2'},
                slots=[m.name if m else None for m in o.data.materials],assignments=[p.material_index for p in o.data.polygons],
                weights=[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices])
        rows.append(r)
    return hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()

def stage():
    OUT.mkdir(parents=True,exist_ok=True)
    backup=OUT/'before-rebake';backup.mkdir(exist_ok=True)
    for path in FILES[:4]+[AO,REPO/'Civ Supply Chains/Textures/CSC_Atlas_AO2.dds']:
        dest=backup/path.name
        if not dest.exists():shutil.copy2(path,dest)
        assert hashlib.sha256(dest.read_bytes()).digest()==hashlib.sha256(path.read_bytes()).digest(), 'Source changed from backup'
    records=[]
    original=json.loads((OUT/'inspection.json').read_text())
    for path in FILES[:4]:
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
        if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
        before=signature()
        source=next(r for r in original if r['path']==str(path))
        obj=next(o for o in bpy.data.objects if o.type=='MESH' and o.name.startswith('CSC_Storage'))
        uv=obj.data.uv_layers['UV2']
        coords=np.array([d.uv[:] for d in uv.data])
        lo=coords.min(axis=0);hi=coords.max(axis=0)
        rectangle=[float(lo[0]),float(hi[0]),float(lo[1]),float(hi[1])]
        if '_CON+PIL' in path.name:
            bpy.context.window.scene=bpy.data.scenes['Export']
            for ob in bpy.context.view_layer.objects:ob.select_set(False)
            obj.hide_set(False);obj.select_set(True);bpy.context.view_layer.objects.active=obj
            obj.data.uv_layers.active_index=1
            bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(angle_limit=math.radians(45),island_margin=.025,area_weight=0,
                correct_aspect=False,scale_to_bounds=True)
            bpy.ops.object.mode_set(mode='OBJECT')
            uv=obj.data.uv_layers['UV2']
            packed=np.array([d.uv[:] for d in uv.data])
            pmin=packed.min(axis=0);pmax=packed.max(axis=0)
            # Preserve the exact existing allocation; keep one texel inside its bounds.
            packed=(packed-pmin)/(pmax-pmin)*(hi-lo-2/1024)+(lo+1/1024)
            uv.data.foreach_set('uv',packed.astype(np.float32).ravel())
            obj.data.update()
            check=np.array([d.uv[:] for d in obj.data.uv_layers['UV2'].data])
            print('BOUNDS',path.name,check.min(axis=0),check.max(axis=0),flush=True)
            assert np.all(check.min(axis=0)>=lo) and np.all(check.max(axis=0)<=hi)
        assert signature()==before
        records.append(dict(source=str(path),file=path.name,signature=before,rectangle=rectangle,
            source_hash=hashlib.sha256(path.read_bytes()).hexdigest(),object=obj.name))
        for im in bpy.data.images:
            if im.source=='FILE':im.filepath=bpy.path.abspath(im.filepath)
        bpy.data.use_autopack=False
        bpy.context.window.scene=bpy.data.scenes['Review']
        bpy.ops.wm.save_as_mainfile(filepath=str(OUT/path.name))
    (OUT/'jobs.json').write_text(json.dumps(records,indent=2))
    print('STAGED',flush=True)

def bake():
    jobs=json.loads((OUT/'jobs.json').read_text())
    protected=np.load(OUT/'protected-chart-mask.npy')
    atlas_pixels=None
    union_mask=None
    for job in jobs:
        bpy.ops.wm.open_mainfile(filepath=str(OUT/job['file']),load_ui=False,use_scripts=False)
        obj=bpy.data.objects[job['object']]
        image=bpy.data.images.load(str(AO),check_existing=False);image.colorspace_settings.name='Non-Color'
        w,h=image.size
        if atlas_pixels is None:
            atlas_pixels=np.array(image.pixels[:],dtype=np.float32).reshape(h,w,4)
            original_pixels=atlas_pixels.copy();union_mask=np.zeros((h,w),dtype=bool)
        stage=bpy.data.images.new('TEMP_AO_BAKE',width=w,height=h,float_buffer=True)
        stage.colorspace_settings.name='Non-Color'
        # Alpha marks every baked texel, including padding, for exact local composition.
        stage.pixels.foreach_set(np.zeros(w*h*4,dtype=np.float32))
        scene=bpy.data.scenes.new('TEMP_AO_SCENE');bpy.context.window.scene=scene
        target=obj.copy();target.data=obj.data.copy();target.parent=None
        target.matrix_world=obj.matrix_world.copy();target.modifiers.clear();scene.collection.objects.link(target)
        target.hide_render=False;target.hide_viewport=False;target.hide_set(False)
        target.data.materials.clear()
        mat=bpy.data.materials.new('TEMP_AO_MATERIAL');mat.use_nodes=True;target.data.materials.append(mat)
        nodes=mat.node_tree.nodes;nodes.clear()
        tex=nodes.new('ShaderNodeTexImage');tex.image=stage;nodes.active=tex
        ao=nodes.new('ShaderNodeAmbientOcclusion');ao.inputs['Distance'].default_value=30;ao.samples=128
        emission=nodes.new('ShaderNodeEmission');output=nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(ao.outputs['Color'],emission.inputs['Color'])
        mat.node_tree.links.new(emission.outputs[0],output.inputs['Surface'])
        for p in target.data.polygons:p.material_index=0
        target.data.uv_layers.active_index=1;target.data.uv_layers['UV2'].active_render=True
        scene.render.engine='CYCLES';scene.cycles.samples=128;scene.cycles.device='CPU'
        scene.render.bake.use_clear=False;scene.render.bake.margin=2;scene.render.bake.use_selected_to_active=False
        target.select_set(True);bpy.context.view_layer.objects.active=target
        print('BAKING',job['file'],flush=True)
        bpy.ops.object.bake(type='EMIT')
        pixels=np.array(stage.pixels[:],dtype=np.float32).reshape(h,w,4)
        owner,_=raster(target.data,w,h)
        core=owner>=0
        assert not np.any(core & protected),'A model core overlaps unrelated AO charts'
        mask=dilate(core,2) & ~dilate(protected,1)
        # Clamp padding to this model's original rectangle, preventing nearby ownership damage.
        u0,u1,v0,v1=job['rectangle']
        allowed=np.zeros_like(mask)
        allowed[max(0,math.floor(v0*h)-2):min(h,math.ceil(v1*h)+2),
                max(0,math.floor(u0*w)-2):min(w,math.ceil(u1*w)+2)]=True
        mask &= allowed
        atlas_pixels[mask,:3]=pixels[mask,:3]
        union_mask |= mask
        stage.filepath_raw=str(OUT/(Path(job['file']).stem+'-bake.png'));stage.file_format='PNG';stage.save()
        job['baked_pixels']=int(mask.sum())
        job['ao_mean']=float(pixels[mask,0].mean());job['ao_min']=float(pixels[mask,0].min())
        bpy.context.window.scene=bpy.data.scenes['Review']
        bpy.data.objects.remove(target,do_unlink=True);bpy.data.scenes.remove(scene)
        bpy.data.images.remove(stage)
    image.pixels.foreach_set(atlas_pixels.ravel());image.file_format='PNG'
    image.filepath_raw=str(OUT/'CSC_Atlas_AO2.png');image.save()
    assert np.array_equal(original_pixels[~union_mask],atlas_pixels[~union_mask])
    np.save(OUT/'changed-region-mask.npy',union_mask)
    (OUT/'bake-report.json').write_text(json.dumps(dict(jobs=jobs,
        changed_pixels=int(np.any(original_pixels!=atlas_pixels,axis=2).sum()),
        protected_pixels=int((~union_mask).sum()),ao_sha256=hashlib.sha256(AO.read_bytes()).hexdigest()),indent=2))
    print('BAKES_DONE',flush=True)

def dilate(mask,radius):
    result=mask.copy();h,w=mask.shape
    for dy in range(-radius,radius+1):
        for dx in range(-radius,radius+1):
            y0=max(0,dy);y1=min(h,h+dy);x0=max(0,dx);x1=min(w,w+dx)
            result[y0:y1,x0:x1] |= mask[y0-dy:y1-dy,x0-dx:x1-dx]
    return result

def raster(me,w=1024,h=1024):
    me.calc_loop_triangles();uv=me.uv_layers['UV2']
    owner=np.full((h,w),-1,dtype=np.int32);conflicts=set()
    for t in me.loop_triangles:
        pts=np.array([uv.data[i].uv[:] for i in t.loops])*[w,h]
        lo=np.maximum(np.floor(pts.min(axis=0)).astype(int),0)
        hi=np.minimum(np.ceil(pts.max(axis=0)).astype(int),[w,h])
        if np.any(hi<=lo):continue
        yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]];x=xx+.5;y=yy+.5;a,b,c=pts
        den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
        if abs(den)<1e-12:continue
        w0=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
        w1=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
        mask=(w0>1e-6)&(w1>1e-6)&(w0+w1<1-1e-6)
        tile=owner[lo[1]:hi[1],lo[0]:hi[0]]
        for prev in np.unique(tile[mask & (tile>=0) & (tile!=t.polygon_index)]):
            conflicts.add(tuple(sorted((int(prev),t.polygon_index))))
        tile[mask]=t.polygon_index
    return owner,sorted(conflicts)

def audit(final=False):
    sys.path.insert(0,str(REPO/'project/tools/blender'))
    import csc_scene_validation as validator
    jobs=json.loads((OUT/'jobs.json').read_text());report=[]
    occupied=np.zeros((1024,1024),dtype=bool)
    for job in jobs:
        path=Path(job['source']) if final else OUT/job['file']
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
        assert signature()==job['signature'], 'Unintended source changes'
        obj=bpy.data.objects[job['object']];owner,overlaps=raster(obj.data)
        coords=np.array([d.uv[:] for d in obj.data.uv_layers['UV2'].data])
        print('SAVED_BOUNDS',coords.min(axis=0),coords.max(axis=0),flush=True)
        print('OVERLAPS',job['file'],overlaps,flush=True)
        assert not overlaps,(job['file'],overlaps)
        assert not np.any(occupied & (owner>=0)), 'Models overlap each other'
        occupied |= owner>=0
        bad=[];subpixel=[]
        for p in obj.data.polygons:
            pts=np.array([obj.data.uv_layers['UV2'].data[i].uv[:] for i in p.loop_indices])
            area=abs(np.dot(pts[:,0],np.roll(pts[:,1],-1))-np.dot(pts[:,1],np.roll(pts[:,0],-1)))/2*1024**2
            if p.area>.01 and area<1e-5:bad.append(p.index)
            if p.area>1 and area<.5:subpixel.append([p.index,p.area,float(area)])
        assert not bad,(job['file'],'collapsed faces',bad)
        print('AUDIT',job['file'],'overlaps',len(overlaps),'collapsed',bad,'subpixel',subpixel,flush=True)
        result=validator.validate_current_scene()
        if '_CON+PIL' in job['file']:
            # This validator is designed for intact compositions. Its intact-only
            # rule cannot apply to an explicitly separate construction/pillage source.
            result['inapplicable_intact_findings']=[f for f in result['findings'] if f['code']=='STATE_GEOMETRY_IN_INTACT']
            result['findings']=[f for f in result['findings'] if f['code']!='STATE_GEOMETRY_IN_INTACT']
            result['error_count']=sum(f['severity']=='error' for f in result['findings'])
            if not result['error_count']:result['status']='review_required'
            result['scope_note']='Separate authored CON+PIL model: intact-only state-geometry rule is inapplicable.'
        assert result['error_count']==0, result
        result['source_sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
        (OUT/(Path(job['file']).stem+('-final-validation.json' if final else '-validation.json'))).write_text(json.dumps(result,indent=2))
        print(validator.format_report(result),flush=True)
        report.append(dict(file=job['file'],overlaps=overlaps,collapsed=bad,subpixel=subpixel,
            scene_errors=result['error_count'],pixel_coverage=int((owner>=0).sum())))
    # Shared-AO consumers outside this task must retain all their mapped pixels.
    protected=np.zeros_like(occupied)
    for path in FILES[4:]:
        if not path.exists():continue
        bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
        for obj in bpy.data.objects:
            if obj.type!='MESH':continue
            if not any(m and m.use_nodes and any(n.type=='TEX_IMAGE' and n.image and 'CSC_Atlas_AO2' in n.image.name
                   for n in m.node_tree.nodes) for m in obj.data.materials):continue
            owner,_=raster(obj.data);protected |= owner>=0
    np.save(OUT/'protected-chart-mask.npy',protected)
    if (OUT/'changed-region-mask.npy').exists():
        changed=np.load(OUT/'changed-region-mask.npy')
        collision=int((changed & protected).sum())
        assert collision==0, ('Protected atlas chart collision',collision)
    else:collision=None
    (OUT/('final-audit.json' if final else 'audit.json')).write_text(json.dumps(dict(models=report,
        protected_chart_collisions=collision),indent=2))

def preview():
    from mathutils import Vector
    jobs=json.loads((OUT/'jobs.json').read_text())
    for job in jobs:
        bpy.ops.wm.open_mainfile(filepath=str(OUT/job['file']),load_ui=False,use_scripts=False)
        obj=bpy.data.objects[job['object']]
        scene=bpy.data.scenes['Review'];bpy.context.window.scene=scene
        for ob in scene.objects:
            if ob.type=='MESH':ob.hide_render=ob!=obj
        for im in bpy.data.images:
            if im.source=='FILE' and 'CSC_Atlas_AO2' in im.name:
                im.filepath=str(OUT/'CSC_Atlas_AO2.png');im.colorspace_settings.name='Non-Color';im.reload()
        corners=[obj.matrix_world@Vector(p) for p in obj.bound_box]
        center=sum(corners,Vector())/8
        size=max(max(v[i] for v in corners)-min(v[i] for v in corners) for i in range(3))
        camera=scene.camera;camera.data.type='ORTHO';camera.data.ortho_scale=size*1.45
        camera.location=center+Vector((-.95,-1.25,.95))*size*3
        camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
        camera.data.clip_end=10000
        scene.render.engine='CYCLES';scene.cycles.samples=32;scene.cycles.device='CPU'
        scene.render.resolution_x=700;scene.render.resolution_y=700;scene.render.resolution_percentage=100
        scene.render.image_settings.file_format='PNG';scene.render.film_transparent=False
        stem=Path(job['file']).stem
        scene.render.filepath=str(OUT/(stem+'-material.png'));bpy.ops.render.render(write_still=True)
        mat=bpy.data.materials.new('TEMP_AO_PREVIEW');mat.use_nodes=True;nodes=mat.node_tree.nodes;nodes.clear()
        image=nodes.new('ShaderNodeTexImage');image.image=bpy.data.images.load(str(OUT/'CSC_Atlas_AO2.png'),check_existing=False)
        image.image.colorspace_settings.name='Non-Color'
        uv=nodes.new('ShaderNodeUVMap');uv.uv_map='UV2'
        em=nodes.new('ShaderNodeEmission');out=nodes.new('ShaderNodeOutputMaterial')
        mat.node_tree.links.new(uv.outputs[0],image.inputs['Vector']);mat.node_tree.links.new(image.outputs['Color'],em.inputs['Color'])
        mat.node_tree.links.new(em.outputs[0],out.inputs['Surface'])
        obj.data.materials.clear();obj.data.materials.append(mat)
        for p in obj.data.polygons:p.material_index=0
        scene.view_settings.view_transform='Standard';scene.view_settings.exposure=0;scene.view_settings.look='None'
        scene.render.filepath=str(OUT/(stem+'-ao.png'));bpy.ops.render.render(write_still=True)

def publish():
    jobs=json.loads((OUT/'jobs.json').read_text())
    report=json.loads((OUT/'bake-report.json').read_text())
    checked=json.loads((OUT/'audit.json').read_text())
    assert checked['protected_chart_collisions']==0
    assert all(m['scene_errors']==0 and not m['collapsed'] and not m['overlaps'] for m in checked['models'])
    assert hashlib.sha256(AO.read_bytes()).hexdigest()==report['ao_sha256'],'Atlas changed since bake'
    for job in jobs:
        assert hashlib.sha256(Path(job['source']).read_bytes()).hexdigest()==job['source_hash'],'Source changed since bake'
    shutil.copy2(OUT/'CSC_Atlas_AO2.png',AO)
    for job in jobs:
        bpy.ops.wm.open_mainfile(filepath=str(OUT/job['file']),load_ui=False,use_scripts=False)
        assert signature()==job['signature']
        for im in bpy.data.images:
            if im.source=='FILE' and 'CSC_Atlas_AO2' in im.name:
                im.filepath=str(AO);im.colorspace_settings.name='Non-Color';im.reload()
        obj=bpy.data.objects[job['object']]
        obj.data.uv_layers.active_index=0;obj.data.uv_layers['UV1'].active_render=True
        bpy.data.use_autopack=False;bpy.context.window.scene=bpy.data.scenes['Review']
        bpy.ops.wm.save_as_mainfile(filepath=job['source'])
        print('PUBLISHED',job['source'],flush=True)

def export_check():
    import io_export_cn6 as cn6
    jobs=json.loads((OUT/'jobs.json').read_text());report=[]
    dest=OUT/'export-check';dest.mkdir(exist_ok=True)
    for job in jobs:
        bpy.ops.wm.open_mainfile(filepath=job['source'],load_ui=False,use_scripts=False)
        bpy.context.window.scene=bpy.data.scenes['Export']
        obj=bpy.data.objects[job['object']]
        assert [u.name for u in obj.data.uv_layers]==['UV1','UV2','UV3']
        assert signature()==job['signature']
        for im in bpy.data.images:
            if im.source=='FILE':assert Path(bpy.path.abspath(im.filepath)).exists(),im.filepath
        rig=next(o for o in bpy.context.scene.objects if o.type=='ARMATURE')
        meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
        output=dest/(Path(job['file']).stem+'.cn6')
        cn6.csc_do_export_selected(str(output),[rig]+meshes)
        assert output.is_file() and output.stat().st_size>1000
        lines=output.read_text().splitlines();start=lines.index('vertices')+1
        end=lines.index('triangles',start)
        exported=np.array([[float(line.split()[14]),1-float(line.split()[15])] for line in lines[start:end]])
        expected=np.array([d.uv[:] for d in obj.data.uv_layers['UV2'].data])
        distance=np.max(np.abs(exported[:,None,:]-expected[None,:,:]),axis=2)
        residual=max(float(distance.min(axis=0).max()),float(distance.min(axis=1).max()))
        assert residual<1e-6,('UV2 export mismatch',residual)
        report.append(dict(source=job['source'],cn6=str(output),bytes=output.stat().st_size,
            uv2_max_residual=residual,source_sha256=hashlib.sha256(Path(job['source']).read_bytes()).hexdigest()))
    (OUT/'export-check.json').write_text(json.dumps(report,indent=2))
    print('EXPORT_CHECK_PASS',flush=True)

def inspect():
    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    for path in FILES:
        if not path.exists():
            continue
        bpy.ops.wm.open_mainfile(filepath=str(path), load_ui=False, use_scripts=False)
        if bpy.context.object and bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        row = dict(path=str(path), scenes=[s.name for s in bpy.data.scenes], meshes=[], images=[])
        for o in bpy.data.objects:
            if o.type != 'MESH':
                continue
            me=o.data
            me.calc_loop_triangles()
            uv=me.uv_layers['UV2']
            owner=np.full((1024,1024),-1,dtype=np.int32)
            conflicts=set()
            degenerate=[]
            for p in me.polygons:
                pts=np.array([uv.data[i].uv[:] for i in p.loop_indices])
                area=abs(np.dot(pts[:,0],np.roll(pts[:,1],-1))-np.dot(pts[:,1],np.roll(pts[:,0],-1)))/2
                if area<1e-10: degenerate.append(p.index)
            for t in me.loop_triangles:
                pts=np.array([uv.data[i].uv[:] for i in t.loops])*1024
                lo=np.maximum(np.floor(pts.min(axis=0)).astype(int),0)
                hi=np.minimum(np.ceil(pts.max(axis=0)).astype(int),1024)
                if np.any(hi<=lo): continue
                yy,xx=np.mgrid[lo[1]:hi[1],lo[0]:hi[0]]
                x=xx+.5;y=yy+.5
                a,b,c=pts
                den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
                if abs(den)<1e-12: continue
                w0=((b[1]-c[1])*(x-c[0])+(c[0]-b[0])*(y-c[1]))/den
                w1=((c[1]-a[1])*(x-c[0])+(a[0]-c[0])*(y-c[1]))/den
                mask=(w0>1e-6)&(w1>1e-6)&(w0+w1<1-1e-6)
                tile=owner[lo[1]:hi[1],lo[0]:hi[0]]
                for prev in np.unique(tile[mask & (tile>=0) & (tile!=t.polygon_index)]):
                    conflicts.add(tuple(sorted((int(prev),t.polygon_index))))
                tile[mask]=t.polygon_index
            print(path.name,o.name,'degenerate',degenerate,'conflicts',len(conflicts),sorted(conflicts)[:40],flush=True)
            row['meshes'].append(dict(name=o.name, matrix=[list(r) for r in o.matrix_world],
                materials=[m.name if m else None for m in me.materials],
                vertices=[list(v.co) for v in me.vertices],
                faces=[dict(index=p.index, verts=list(p.vertices), area=p.area,
                    uv={u.name:[list(u.data[i].uv) for i in p.loop_indices] for u in me.uv_layers})
                    for p in me.polygons], triangles=[dict(face=t.polygon_index,loops=list(t.loops),
                    uv=[list(uv.data[i].uv) for i in t.loops]) for t in me.loop_triangles],
                degenerate=degenerate, overlaps=sorted(conflicts)))
        for im in bpy.data.images:
            if im.source=='FILE':
                row['images'].append(dict(name=im.name, path=bpy.path.abspath(im.filepath),
                    size=list(im.size), packed=bool(im.packed_file), colorspace=im.colorspace_settings.name))
        report.append(row)
    (OUT/'inspection.json').write_text(json.dumps(report,indent=2))
    print('INSPECTION', str(OUT/'inspection.json'))

if __name__=='__main__':
    action=sys.argv[-1]
    if action=='stage':stage()
    elif action=='bake':bake()
    elif action=='audit':audit()
    elif action=='audit-final':audit(True)
    elif action=='preview':preview()
    elif action=='publish':publish()
    elif action=='export-check':export_check()
    else:inspect()
