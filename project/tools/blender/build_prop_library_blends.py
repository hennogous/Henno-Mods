"""Run in Blender: source-local meshes, external textures, explicit identities."""
import bpy, json, pathlib, sys, xml.etree.ElementTree as ET, re
from mathutils import Matrix, Vector
LIB=pathlib.Path(sys.argv[sys.argv.index('--')+1]).resolve()
CAT=LIB/'catalogue.json'
data=json.loads(CAT.read_text())
def txt(e,path,default=''):
    n=e.find(path)
    return n.get('text',n.text or default) if n is not None else default
def vals(e):
    result={}
    for n in e.findall('.//Element'):
        p=txt(n,'m_ParamName')
        if p: result[p]=txt(n,'m_ObjectName') or txt(n,'m_bValue') or txt(n,'m_fValue')
    return result
def identity(obj,aid,role):
    obj['source_asset_id']=aid;obj['export_role']=role
def image_for(name,relative,channel):
    path=LIB/relative
    png=path.with_suffix('.png')
    color='sRGB' if channel in ('BaseColor','Emissive','FOWColor') else 'Non-Color'
    if not png.exists():
        src=bpy.data.images.load(str(path),check_existing=False)
        src.colorspace_settings.name=color
        pixels=list(src.pixels[:]);w,h=src.size
        assert w and h and pixels, str(path)
        im=bpy.data.images.new(name+'_decode',width=w,height=h,alpha=True)
        im.colorspace_settings.name=color;im.pixels[:]=pixels
        im.filepath_raw=str(png);im.file_format='PNG';im.save()
        bpy.data.images.remove(im);bpy.data.images.remove(src)
    im=bpy.data.images.load(str(png),check_existing=False)
    im.name=name+'__'+color;im.colorspace_settings.name=color
    assert all(im.size) and len(im.pixels)>0
    im.filepath='//textures/'+png.name
    return im
def material(name,row):
    mat=bpy.data.materials.new(name);mat.use_nodes=True;mat.use_fake_user=True
    spec=data['materials'][name];bindings=dict(spec['textures'])
    bindings.update(row['asset_texture_overrides'])
    mat['source_material_id']=name;mat['source_shader']=spec['shader']
    mat['effective_texture_bindings']=json.dumps(bindings,sort_keys=True)
    ns=mat.node_tree.nodes;links=mat.node_tree.links;bs=ns.get('Principled BSDF')
    uvnodes={}
    for i in range(1,4):
        u=ns.new('ShaderNodeUVMap');u.uv_map='UV'+str(i);u.location=(-1000,200-i*220);uvnodes[i]=u
    tex={}
    for i,(channel,tid) in enumerate(bindings.items()):
        node=ns.new('ShaderNodeTexImage');node.name=channel;node.label=channel+': '+tid
        node.image=image_for(tid,row['textures'][tid],channel);node.location=(-700,400-i*200)
        links.new(uvnodes[2 if channel=='AO' else 3 if channel=='Emissive' else 1].outputs['UV'],node.inputs['Vector']);tex[channel]=node
    if 'BaseColor' in tex:
        color=tex['BaseColor'].outputs['Color']
        if 'AO' in tex:
            mul=ns.new('ShaderNodeMixRGB');mul.blend_type='MULTIPLY';mul.inputs[0].default_value=1
            links.new(color,mul.inputs[1]);links.new(tex['AO'].outputs['Color'],mul.inputs[2]);color=mul.outputs[0]
        links.new(color,bs.inputs['Base Color'])
    if 'Normal' in tex:
        normal=ns.new('ShaderNodeNormalMap');normal.uv_map='UV1'
        links.new(tex['Normal'].outputs['Color'],normal.inputs['Color']);links.new(normal.outputs['Normal'],bs.inputs['Normal'])
    if 'Gloss' in tex:
        inv=ns.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1
        links.new(tex['Gloss'].outputs['Color'],inv.inputs[1]);links.new(inv.outputs[0],bs.inputs['Roughness'])
    if 'Metalness' in tex: links.new(tex['Metalness'].outputs['Color'],bs.inputs['Metallic'])
    if 'Emissive' in tex:
        links.new(tex['Emissive'].outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=1
    if 'Opacity' in tex: links.new(tex['Opacity'].outputs['Color'],bs.inputs['Alpha'])
    return mat
def build(row):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    aid=row['asset_id'];scene=bpy.context.scene;scene.name=aid
    scene['source_asset_id']=aid;scene['export_role']='reused_asset'
    scene['placement_contract']='AE XYZ = Blender XYZ / 10; AE Z rotation reverses sign; retain scale and parent transforms. Not applied to this library.'
    scene['import_notes']='FGX vertex XYZ unchanged, 1 Blender unit = 1 source geometry unit; UV V converted to 1-V. Source authoring InitialPlacement recorded, not used as asset placement.'
    mats={name:material(name,row) for name in row['material_ids']}
    uvcounts=[sum(v['name'].startswith('TextureCoordinates') for v in mesh['vertexStructInfos']) for m in row['models'] for mesh in json.loads((LIB/m['extracted']).read_text())['meshes']]
    if min(uvcounts)<3:
        for mat in mats.values():
            if 'Emissive' in mat.node_tree.nodes:
                mat.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].default_value=0
                mat['preview_note']='Source emissive texture retained. Preview emission disabled: source has fewer than 3 UV channels; shader UV routing requires destination verification.'
                if mat['preview_note'] not in row['issues']: row['issues'].append(mat['preview_note'])
    total=sum(len(json.loads((LIB/m['extracted']).read_text())['meshes']) for m in row['models'])
    root=None
    if total>1:
        root=bpy.data.objects.new(aid,None);scene.collection.objects.link(root);identity(root,aid,'reused_asset')
    components=[]
    for model in row['models']:
        raw=json.loads((LIB/model['extracted']).read_text())
        inst=ET.fromstring(model['xml'])
        states=[dict(mesh=txt(s,'m_MeshName'),group=txt(s,'m_GroupName'),state=txt(s,'m_StateName'),values=vals(s)) for s in inst.findall('m_GroupStates/Element')]
        model['states']=states
        geo=ET.fromstring(re.sub(r'(<\/?)([\w.]+):',r'\1\2.',(LIB/model['geo_copy']).read_text(encoding='utf-8-sig')))
        for mi,m in enumerate(raw['meshes']):
            name=aid if total==1 else aid+'__'+model['instance']+'__'+str(mi)
            # Blender names can be limited by version; component mapping is authoritative.
            mesh=bpy.data.meshes.new(name);obj=bpy.data.objects.new(name,mesh);scene.collection.objects.link(obj)
            identity(obj,aid,'reused_asset');mesh['source_asset_id']=aid
            obj['source_mesh_name']=m['name'];obj['source_geometry_id']=model['geometry'];obj['source_instance_name']=model['instance']
            obj['source_model_metadata']=json.dumps(raw['models']);obj['source_group_states']=json.dumps(states)
            if root: obj.parent=root
            mesh.from_pydata([v['position'] for v in m['vertices']],[],[t[:3] for t in m['triangles']]);mesh.update()
            uvcount=sum(v['name'].startswith('TextureCoordinates') for v in m['vertexStructInfos'])
            for i,key in enumerate(['uv','uv2','uv3'][:uvcount]):
                uv=mesh.uv_layers.new(name='UV'+str(i+1))
                for loop in mesh.loops:
                    u,v=m['vertices'][loop.vertex_index][key];uv.data[loop.index].uv=(u,1-v)
            mesh.polygons.foreach_set('use_smooth',[True]*len(mesh.polygons))
            mesh.normals_split_custom_set([m['vertices'][l.vertex_index]['normal'] for l in mesh.loops])
            if any(abs(sum(x*x for x in v['normal'])-1)>0.001 for v in m['vertices']):
                note='Source normals are not all unit length. Blender normalizes shading normals; raw values are retained in source_normal mesh attribute and extracted source JSON.'
                if note not in row['issues']:row['issues'].append(note)
            for attr,key in [('source_normal','normal'),('source_tangent','tangent'),('source_binormal','binormal')]:
                a=mesh.attributes.new(attr,'FLOAT_VECTOR','POINT')
                for i,v in enumerate(m['vertices']): a.data[i].vector=v[key]
            for i,bname in enumerate(m['boneBindings'] or []):
                group=obj.vertex_groups.new(name=bname)
                for vi,v in enumerate(m['vertices']):
                    w=sum(w for bi,w in zip(v['boneIndices'],v['boneWeights']) if bi==i)/255
                    if w: group.add([vi],w,'REPLACE')
            geome=next(g for g in geo.findall('m_Meshes/Element') if txt(g,'m_Name')==m['name'])
            groups=geome.findall('m_Groups/Element');visible=[];bindingmap=[]
            for gi,g in enumerate(groups):
                gname=txt(g,'m_Name')
                gs=[s for s in states if s['mesh']==m['name'] and s['group']==gname]
                state=next((s for s in gs if s['state']=='Worked'),gs[0] if gs else None)
                matname=state['values'].get('Material') if state else m['materialName']
                if matname not in mats: raise ValueError((aid,m['name'],gname,matname))
                mesh.materials.append(mats[matname]);visible.append(state is None or state['values'].get('Visible','true')=='true')
                first=int(txt(g,'m_nFirstPrim'));count=int(txt(g,'m_nPrims'))
                for poly in list(mesh.polygons)[first:first+count]: poly.material_index=gi
                bindingmap.append(dict(group=gname,material=matname,first=first,count=count))
            obj.hide_render=not any(visible);obj.hide_set(not any(visible))
            obj['default_state']='Worked';obj['source_group_bindings']=json.dumps(bindingmap)
            components.append(dict(object=obj.name,mesh_datablock=mesh.name,source_mesh=m['name'],geometry=model['geometry'],vertices=len(mesh.vertices),triangles=len(mesh.polygons),uv_layers=uvcount,default_visible=any(visible),materials=bindingmap))
        # Retain source bind skeleton as named transform references. Meshes are already in bind-pose model space.
        refs=bpy.data.collections.new(model['instance']+'__source_skeleton');scene.collection.children.link(refs)
        refs.hide_render=True;refs.hide_viewport=True
        for rm in raw['models']:
            bones=[]
            for b in rm['bones']:
                ob=bpy.data.objects.new(b['name']+'__bind',None);refs.objects.link(ob)
                identity(ob,aid,'source_transform_reference');ob['source_bone_name']=b['name'];ob['source_bone_metadata']=json.dumps(b)
                inv=b['inverseWorld'];world=Matrix([inv[i:i+4] for i in range(0,16,4)]).transposed().inverted()
                if b['parent']>=0: ob.parent=bones[b['parent']]
                ob.matrix_world=world;bones.append(ob)
    bpy.context.view_layer.update()
    points=[o.matrix_world@v.co for o in scene.objects if o.type=='MESH' and not o.hide_render for v in o.data.vertices]
    row['dimensions']=[max(v[i] for v in points)-min(v[i] for v in points) for i in range(3)]
    row['bounds']=[[min(v[i] for v in points) for i in range(3)],[max(v[i] for v in points) for i in range(3)]]
    row['components']=components;row['blend_path']=aid+'.blend';row['pivot_import_notes']=scene['import_notes']
    for o in scene.objects:
        if o.type=='MESH' and not o.hide_render: o.select_set(True);bpy.context.view_layer.objects.active=o
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='VIEW_3D':
                area.spaces.active.shading.type='MATERIAL'
                area.spaces.active.region_3d.view_distance=max(row['dimensions'])*2
                area.spaces.active.region_3d.view_location=Vector([(a+b)/2 for a,b in zip(*row['bounds'])])
    bpy.context.preferences.filepaths.save_version=0
    bpy.ops.wm.save_as_mainfile(filepath=str(LIB/row['blend_path']))
    row['status']='exported'
    print('EXPORTED',aid,flush=True)
for row in data['assets']:
    try: build(row)
    except Exception as exc:
        import traceback;traceback.print_exc();row['status']='incomplete';row['issues'].append(str(exc))
    CAT.write_text(json.dumps(data,indent=2))
print('BUILD_COMPLETE',flush=True)
