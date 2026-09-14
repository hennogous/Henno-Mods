"""Reopen every delivered blend and compare it against extracted source data."""
import bpy,json,pathlib,sys,math,struct
from mathutils import Matrix
LIB=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
data=json.loads((LIB/'catalogue.json').read_text())
reports=[]
for row in data['assets']:
    report=dict(asset_id=row['asset_id'],checks=[],errors=[])
    try:
        bpy.ops.wm.open_mainfile(filepath=str(LIB/row['blend_path']))
        if row.get('origin')=='authored_blender':
            meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
            rigs=[o for o in bpy.context.scene.objects if o.type=='ARMATURE']
            assert len(meshes)==len(rigs)==1
            o=meshes[0];rig=rigs[0]
            assert o.name==o.data.name==row['asset_id']
            assert o['source_asset_id']==row['asset_id'] and o['export_role']=='custom_attachment'
            assert o.matrix_world==Matrix.Identity(4) and rig.matrix_world==Matrix.Identity(4)
            assert [u.name for u in o.data.uv_layers]==['UV1','UV2','UV3']
            assert [b.name for b in rig.data.bones]==['Bone'] and o.parent==rig
            assert min(v.co.z for v in o.data.vertices)>-0.0001
            assert all(abs(o.vertex_groups['Bone'].weight(v.index)-1)<1e-6 for v in o.data.vertices)
            textures=[]
            for im in bpy.data.images:
                if im.source!='FILE':continue
                p=pathlib.Path(bpy.path.abspath(im.filepath)).resolve()
                assert im.filepath.startswith('//') and not im.packed_file
                assert p.is_relative_to(LIB) and p.is_file(),str(p)
                im.reload();assert min(im.size)>0
                textures.append(dict(path=p.relative_to(LIB).as_posix(),resolution=list(im.size)))
            report.update(status='passed',textures=textures,checks=['Authored blend reopened; exact asset identity','Local contact pivot; identity transforms; static Bone binding','Three UV channels and external portable textures','Windows registration remains explicitly pending; no FGX-source comparison claimed'])
            row['status']='verified_blender';row['verification']=report;reports.append(report)
            print('PASSED',row['asset_id'],flush=True)
            continue
        assert bpy.context.scene.name==row['asset_id']
        assert len([o for o in bpy.context.scene.objects if o.type=='MESH'])==len(row['components'])
        for c in row['components']:
            o=bpy.data.objects[c['object']];me=o.data
            assert o['source_asset_id']==row['asset_id'] and o['export_role']=='reused_asset'
            assert me.name==c['mesh_datablock']
            if len(row['components'])==1: assert o.name==me.name==row['asset_id']
            assert o.matrix_basis==Matrix.Identity(4) and o.matrix_world==Matrix.Identity(4)
            assert len(me.vertices)==c['vertices'] and len(me.polygons)==c['triangles']
            assert len(me.uv_layers)==c['uv_layers']
            model=next(m for m in row['models'] if m['geometry']==c['geometry'])
            raw=json.loads((LIB/model['extracted']).read_text())
            src=next(m for m in raw['meshes'] if m['name']==c['source_mesh'])
            for v,s in zip(me.vertices,src['vertices']):
                assert max(abs(a-b) for a,b in zip(v.co,s['position']))<0.0001
            for p,t in zip(me.polygons,src['triangles']): assert list(p.vertices)==t[:3]
            for layer,key in zip(me.uv_layers,['uv','uv2','uv3']):
                for loop in me.loops:
                    u,v=src['vertices'][loop.vertex_index][key]
                    assert max(abs(layer.data[loop.index].uv[0]-u),abs(layer.data[loop.index].uv[1]-(1-v)))<0.00001
            for binding in c['materials']:
                for p in list(me.polygons)[binding['first']:binding['first']+binding['count']]:
                    assert me.materials[p.material_index]['source_material_id']==binding['material']
            assert me.has_custom_normals
            for loop in me.loops:
                source_normal=src['vertices'][loop.vertex_index]['normal']
                n=me.corner_normals[loop.index].vector
                dot=sum(a*b for a,b in zip(n,source_normal))
                length=math.sqrt(sum(a*a for a in source_normal))
                if length>0.0001: assert dot/length>0.999, (o.name,'normal',dot/length)
                original=me.attributes['source_normal'].data[loop.vertex_index].vector
                assert max(abs(a-b) for a,b in zip(original,source_normal))<0.00001
            assert o.hide_render != c['default_visible']
        for mat in bpy.data.materials:
            if 'source_material_id' not in mat:continue
            expected=dict(data['materials'][mat['source_material_id']]['textures']);expected.update(row['asset_texture_overrides'])
            assert json.loads(mat['effective_texture_bindings'])==expected
        report['checks']=['Saved scene reopened','Exact asset IDs and single-mesh names','Component counts and mapping','Vertex coordinates and triangle topology match FGX extraction','UV channels match source with documented V conversion','Object and parent transforms retained; no placement baked','Per-group material assignments','Custom normals retained']
        textures=[]
        for im in bpy.data.images:
            if im.source!='FILE':continue
            assert im.filepath.startswith('//') and not im.packed_file
            p=pathlib.Path(bpy.path.abspath(im.filepath)).resolve()
            assert p.is_relative_to(LIB) and p.is_file(),str(p)
            im.reload();size=list(im.size);assert min(size)>0 and len(im.pixels)>0
            dds=p.with_suffix('.dds')
            raw=dds.read_bytes();h,w=struct.unpack_from('<II',raw,12)
            assert size==[w,h],(p,size,[w,h])
            textures.append(dict(path=p.relative_to(LIB).as_posix(),resolution=size,color_space=im.colorspace_settings.name))
        report['textures']=textures;report['checks'].append('All external relative textures reopened and decoded at original DDS resolution; effective asset overrides match source; corner normals match source')
        report['status']='passed';row['status']='verified_blender'
    except Exception as e:
        import traceback;traceback.print_exc();report['status']='failed';report['errors'].append(str(e));row['status']='verification_failed'
    row['verification']=report
    reports.append(report)
    print(report['status'].upper(),row['asset_id'],flush=True)
(LIB/'verification.json').write_text(json.dumps(reports,indent=2))
(LIB/'catalogue.json').write_text(json.dumps(data,indent=2))
assert all(r['status']=='passed' for r in reports)
print('VERIFICATION_COMPLETE',len(reports),flush=True)
