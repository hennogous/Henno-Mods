#!/usr/bin/env python3
"""Decode CSC Blender scenes and stage Civ VI assets. Standard Python, no third-party deps.

Commands: decode JOB --blender EXE; build JOB; convert JOB --converter EXE --texconv EXE;
install JOB; uninstall JOB [--dry-run] [--purge].
Build always writes a review report; exits 2 if any placement cannot be represented.
Source blends are never edited. Only the explicit install command changes the live project.
"""
import argparse
import copy
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

STATES = ('Worked', 'Unworked', 'Pillaged', 'Construction', 'Unbuilt')
SLOTS = {'B':'BaseColor','N':'Normal','AO':'AO','G':'Gloss','M':'Metalness','E':'Emissive','O':'Opacity','T':'TintMask'}
POINTS = 'm_BehaviorData/m_behaviorDataSets/m_attachmentPoints/m_Points'
MODELS = 'm_GeometrySet/m_ModelInstances'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_xml(path):
    # SDK XML uses a literal unbound AssetObjects: prefix in some versions.
    return ET.fromstring(re.sub(r'(<\/?)([\w.]+):', r'\1\2.', Path(path).read_text(encoding='utf-8-sig')))


def txt(node, path, default=''):
    n = node.find(path)
    return n.get('text', default) if n is not None else default


def set_text(node, path, value):
    n = node.find(path)
    if n is None:
        raise ValueError(f'Missing template field {path}')
    n.set('text', str(value))


def elem(parent, name, value=None, **attrs):
    e = ET.SubElement(parent, name, attrs)
    if value is not None:
        e.text = str(value)
    return e


def write_xml(path, root):
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space='  ')
    ET.ElementTree(root).write(path, encoding='utf-8', xml_declaration=True)


def identifier(value):
    if not re.fullmatch(r'[A-Za-z0-9_+.-]+',value) or value in ('.','..'):
        raise ValueError(f'Unsafe asset identifier: {value!r}')
    return value


def existing_material(mat, job, mod):
    """Resolve authored identities explicitly; never guess an atlas from a mesh name."""
    target = mat.get('external') or job.get('material_bindings', {}).get(mat['name'])
    if not target and (mod / 'Materials' / (mat['name'] + '.mtl')).is_file():
        target = mat['name']
    if target:
        if target.startswith('CSC_') and not (mod / 'Materials' / (target + '.mtl')).is_file():
            raise ValueError(f'{mat["name"]}: existing CSC material not found: {target}')
        return target
    if job.get('material_policy') == 'reuse_existing':
        raise ValueError(f'{mat["name"]}: no existing material binding; set civ_material in Blender or material_bindings in the exporter defaults')
    return None


def stage_ao_binding(mat, existing, mod, stage, textures, source_inputs, ao_policy='stage_explicit'):
    """Keep surface bindings; stage an explicitly authored AO map and resolve its material.

    Native attachment assets never enter this path. An AO-only material variant is
    necessary when another asset still uses the base material's original AO layout.
    """
    ident = mat.get('ao_texture')
    if not ident:
        return existing
    if ao_policy == 'reuse_existing':
        if not existing:
            raise ValueError(f'{mat["name"]}: AO reuse needs an existing material binding')
        return existing
    if not ident.startswith('CSC_') or any(c not in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for c in ident):
        raise ValueError(f'Invalid explicit AO texture identity: {ident}')
    im = mat.get('images', {}).get('AO')
    if not im:
        raise ValueError(f'{mat["name"]}: explicit AO binding has no AO source image')
    src = Path(im['path'])
    if sha(src) != im['sha256']:
        raise ValueError(f'Changed AO texture {src}')
    if ident in textures and textures[ident]['sha256'] != im['sha256']:
        raise ValueError(f'Conflicting AO source images for {ident}')
    source_inputs[str(src)] = im['sha256']
    dest = stage / 'TextureSources' / (ident + src.suffix.lower())
    dest.parent.mkdir(parents=True, exist_ok=True)
    if ident not in textures:
        shutil.copy2(src, dest)
        textures[ident] = {'source':str(dest.relative_to(stage)), 'slot':'AO',
            'size':im['size'], 'sha256':im['sha256'], 'format':'R8_UNORM'}
    if not existing:
        return None
    path = mod / 'Materials' / (existing + '.mtl')
    if not path.is_file():
        raise ValueError(f'{mat["name"]}: explicit AO requires an inspectable material: {path}')
    root = read_xml(path)
    ao = [v for v in root.findall('m_CookParams/m_Values/Element') if txt(v,'m_ParamName') == 'AO']
    if len(ao) != 1:
        raise ValueError(f'{existing}: expected one material AO slot')
    if txt(ao[0], 'm_ObjectName') == ident:
        return existing
    # Stable identities: changes to AO pixels don't introduce more material names.
    name = existing + '__AO_' + ident
    set_text(root, 'm_Name', name)
    set_text(ao[0], 'm_ObjectName', ident)
    write_xml(stage / 'Materials' / (name + '.mtl'), root)
    return name


def value(parent, name, value, kind='Object'):
    e = elem(parent, 'Element', **{'class':f'AssetObjects..{kind}Value'})
    if kind == 'Object':
        elem(e, 'm_ObjectName', text=value)
        elem(e, 'm_eObjectType', 'MATERIAL')
    elif kind == 'Bool':
        elem(e, 'm_bValue', str(value).lower())
    else:
        elem(e, 'm_Value', text=value)
    elem(e, 'm_ParamName', text=name)
    return e


def groups(model):
    for mesh in model['meshes']:
        for i, mat in enumerate(mesh['materials']):
            count = sum(t[3] == i for t in mesh['triangles'])
            if count:
                yield mesh, i, mat, count


def model_instance(model, material_ids, visible, state_template=None):
    e = ET.Element('Element')
    elem(e,'m_Name',text=model['asset_id']); elem(e,'m_GeoName',text=model['asset_id'])
    gs = elem(e,'m_GroupStates')
    for mesh, _, mat, _ in groups(model):
        material_id = material_ids.get((mesh['name'], mat['name']), material_ids.get(mat['name']))
        if material_id is None:
            raise ValueError(f'{model["asset_id"]}/{mesh["name"]}: missing material binding for {mat["name"]}')
        mesh_visible = visible.get(mesh['name'], ()) if isinstance(visible, dict) else visible
        for state in STATES:
            # Preserve shader/FOW/burn settings from a chosen original mesh where supplied.
            template = state_template.get(state) if state_template else None
            if template is not None:
                row = copy.deepcopy(template)
                gs.append(row)
                vals = row.find('m_Values/m_Values')
                for p in vals:
                    param = txt(p,'m_ParamName')
                    if param == 'Material': set_text(p,'m_ObjectName',material_id)
                    if param == 'Visible': p.find('m_bValue').text = str(state in mesh_visible).lower()
            else:
                row = elem(gs,'Element'); vals = elem(elem(row,'m_Values'),'m_Values')
                value(vals,'Material',material_id)
                value(vals,'Visible',state in mesh_visible,'Bool')
                value(vals,'FOWMaterial','FOW/DefaultMaterial')
                value(vals,'BurnMaterial','')
                value(vals,'SnowMaterial','DefaultSnowMaterial')
                value(vals,'EmissiveEnabled',state == 'Worked','Bool')
                value(vals,'FOWVisibleOnly',False,'Bool')
                for tag in ('m_GroupName','m_MeshName','m_StateName'): elem(row,tag,text='')
            set_text(row,'m_GroupName',mat['name']); set_text(row,'m_MeshName',mesh['name']); set_text(row,'m_StateName',state)
    return e


def write_cn6(path, model):
    # Static skeleton: identity root and identity Bone. Model coordinates are already
    # in their asset frame; placement roots never enter the vertex stream.
    ident = '1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1'
    lines = ['// CivNexus6 CN6 - CSC scene decoder','skeleton',
             f'0 "{model["asset_id"]}" -1 0 0 0 0 0 0 1 {ident}',
             f'1 "Bone" 0 0 0 0 0 0 0 1 {ident}', f'meshes:{len(model["meshes"])}']
    for mesh in model['meshes']:
        if any('"' in x or '\n' in x for x in [mesh['name']] + [m['name'] for m in mesh['materials']]):
            raise ValueError('CN6 names cannot contain quotes or newlines')
        lines += [f'mesh:"{mesh["name"]}"', 'materials'] + [f'"{m["name"]}"' for m in mesh['materials']] + ['vertices']
        for v in mesh['vertices']:
            if len(v)!=18 or not all(math.isfinite(n) for n in v): raise ValueError('Invalid CN6 vertex')
            lines.append(' '.join(f'{n:.8f}' for n in v) + ' 1 1 1 1 1 1 1 1 255 0 0 0 0 0 0 0')
        lines += ['triangles'] + [' '.join(map(str,t)) for t in mesh['triangles']]
    lines += ['end']
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text('\n'.join(lines)+'\n')


def geometry(model, template):
    r = copy.deepcopy(template)
    r.tag = 'AssetObjects..GeometryInstance'
    meshes = r.find('m_Meshes'); meshes.clear()
    for mesh in model['meshes']:
        e=elem(meshes,'Element'); elem(e,'m_Name',text=mesh['name']); gr=elem(e,'m_Groups')
        first=0
        for i,m in enumerate(mesh['materials']):
            count=sum(t[3]==i for t in mesh['triangles'])
            g=elem(gr,'Element'); elem(g,'m_Name',text=m['name']); elem(g,'m_nFirstPrim',first); elem(g,'m_nPrims',count)
            first+=count
        elem(e,'m_nBoundBoneCount',1); elem(e,'m_nPrimitiveCount',len(mesh['triangles'])); elem(e,'m_nVertexCount',len(mesh['vertices']))
    b=r.find('m_Bones'); b.clear(); elem(b,'Element',text=model['asset_id']); elem(b,'Element',text='Bone')
    for tag in ('m_ModelName','m_Name'): set_text(r,tag,model['asset_id'])
    for tag in ('m_SourceFilePath','m_SourceObjectName'): set_text(r,tag,'')
    cl='DecalGeometry' if model['kind']=='decal' else 'LandmarkModel'
    set_text(r,'m_ClassName',cl); r.find('m_Tags').clear(); elem(r.find('m_Tags'),'Element',text=cl)
    df=r.find('m_DataFiles'); df.clear(); e=elem(df,'Element'); elem(e,'m_ID',text='GR2'); elem(e,'m_RelativePath',text=model['asset_id']+'.fgx')
    return r


def shared_model_from_geo(mod, ident, material_for_group, visible_for_group):
    """Build a state model from an installed or newly staged shared GEO."""
    geo = read_xml(mod / 'Geometries' / (ident + '.geo'))
    meshes, bindings, visibility = [], {}, {}
    for source_mesh in geo.findall('m_Meshes/Element'):
        mesh_name = txt(source_mesh, 'm_Name')
        group_names = [txt(group, 'm_Name') for group in source_mesh.findall('m_Groups/Element')]
        if not mesh_name or not group_names or len(set(group_names)) != len(group_names):
            raise ValueError(f'{ident}: invalid shared GEO mesh/groups')
        meshes.append({'name': mesh_name, 'materials': [{'name': name} for name in group_names],
                       'triangles': [[0, 1, 2, i] for i in range(len(group_names))]})
        for name in group_names:
            bindings[(mesh_name, name)] = material_for_group(name)
            visibility[(mesh_name, name)] = visible_for_group(name)
    model = {'asset_id': ident, 'meshes': meshes}
    root = ET.Element('Element')
    elem(root, 'm_Name', text=ident); elem(root, 'm_GeoName', text=ident)
    state_rows = elem(root, 'm_GroupStates')
    for mesh, _, mat, _ in groups(model):
        name = mat['name']
        for state in STATES:
            row = elem(state_rows, 'Element'); values = elem(elem(row, 'm_Values'), 'm_Values')
            value(values, 'Material', bindings[(mesh['name'], name)])
            value(values, 'Visible', state in visibility[(mesh['name'], name)], 'Bool')
            value(values, 'FOWMaterial', 'FOW/DefaultMaterial')
            value(values, 'BurnMaterial', 'DefaultBurnMaterial' if state == 'Pillaged' else '')
            value(values, 'SnowMaterial', 'DefaultSnowMaterial')
            value(values, 'EmissiveEnabled', state == 'Worked', 'Bool')
            value(values, 'FOWVisibleOnly', False, 'Bool')
            for tag, val in [('m_GroupName', name), ('m_MeshName', mesh['name']), ('m_StateName', state)]:
                elem(row, tag, text=val)
    return root


def validate_support(attachments):
    index={a['instance_id']:a for a in attachments}
    if len(index)!=len(attachments): raise ValueError('Duplicate attachment instance_id')
    for ident,a in index.items():
        seen={ident}; support=a['support']
        while support not in ('ground','building'):
            if support in seen: raise ValueError(f'Support cycle at {ident}')
            if support not in index: raise ValueError(f'Missing support {support}')
            seen.add(support); support=index[support]['support']
        mode = a.get('terrain_follow', 'pivot')
        if mode not in ('pivot', 'shared-support-pivot'):
            raise ValueError(f'{ident}: unknown terrain-follow mode {mode}')
        if mode == 'shared-support-pivot':
            parent = index.get(a['support'])
            if parent is None:
                raise ValueError(f'{ident}: shared support pivot needs an attachment support')
            if any(abs(x-y) > 1e-4 for x,y in zip(a['position'], parent['position'])):
                raise ValueError(f'{ident}: shared support pivot must coincide with {a["support"]} in XYZ')


def attachment_transform(a, policies):
    problems=[]; scale=a['scale']; rot=a['rotation_degrees']
    if a.get('shear_error',0)>1e-5: problems.append('world transform contains shear')
    if min(scale)<=0: problems.append('mirrored/singular placement')
    nonuniform=max(scale)-min(scale)>max(1,max(scale))*1e-5
    if nonuniform:
        problems.append('nonuniform scale; fix the Blender placement or publish a distinct proportion variant (AE has scalar m_scale)')
    if (a['support']!='ground' and a.get('terrain_follow') != 'shared-support-pivot'
            and policies.get('supported_props','reject')!='independent-pivot'):
        problems.append(f'support {a["support"]} requires shared elevation; independent pivots can separate')
    scalar = sum(scale)/3
    if abs(scalar - 1.0) <= 1e-6:
        scalar = 1.0
    # AE displays degrees, but AST m_orientation serializes radians.
    # The AE orientation fields are radians. X/Y retain Blender's direction;
    # the established CSC Z convention is reversed. Combined-axis visual parity
    # remains an AE review item until calibrated against a known reference asset.
    return {'position':[v/10 for v in a['position']],
            'rotation':[math.radians(rot[0]),math.radians(rot[1]),math.radians(-rot[2])],
            'scale':scalar}, problems


def attachment(a, binding, owner, policies):
    transform, problems=attachment_transform(a,policies)
    if problems:
        return None, problems
    e=ET.Element('Element'); vals=elem(elem(e,'m_CookParams'),'m_Values'); vals.append(copy.deepcopy(binding))
    value(vals,'ConnectionType','NONE','String')
    v=elem(vals,'Element',**{'class':'AssetObjects..ArtDefReferenceValue'})
    for k,s in [('m_ElementName',"DON'T CARE"),('m_RootCollectionName','ResourceTags'),('m_ArtDefPath','Landmarks.artdef'),('m_TemplateName','Landmarks'),('m_ParamName','ResourceType')]: elem(v,k,text=s)
    elem(v,'m_CollectionIsLocked','true')
    value(vals,'TerrainFollowMode','Pivot Height','String'); value(vals,'Cull Mode','OPTIONAL','String'); value(vals,'RandomizeAnims',True,'Bool')
    for name,arr in [('m_position',transform['position']),('m_orientation',transform['rotation'])]:
        node=elem(e,name)
        for axis,v in zip('xyz',arr): elem(node,axis,f'{v:.8f}')
    elem(e,'m_Name',text='CSC_Attach_'+a['instance_id']); elem(e,'m_BoneName',text=owner); elem(e,'m_ModelInstanceName',text=owner); elem(e,'m_scale',f'{transform["scale"]:.8f}')
    return e,problems


def csc_binding(ident, xlp):
    e=ET.Element('Element',{'class':'AssetObjects..BLPEntryValue'})
    for k,v in [('m_EntryName',ident),('m_XLPClass','TileBase'),('m_XLPPath',xlp.name.lower()),('m_BLPPackage','Landmarks/CSC_Tilebases'),('m_LibraryName','TileBase'),('m_ParamName','Asset')]: elem(e,k,text=v)
    return e


def merge_xlp(root, identifiers):
    entries=root.find('m_Entries'); known={txt(e,'m_EntryID'):txt(e,'m_ObjectName') for e in entries}
    if len(known)!=len(entries): raise ValueError('Duplicate pre-existing XLP entries')
    for ident in sorted(set(identifiers)):
        if ident in known:
            if known[ident]!=ident: raise ValueError(f'Conflicting XLP identity {ident}')
        else:
            e=elem(entries,'Element'); elem(e,'m_EntryID',text=ident); elem(e,'m_ObjectName',text=ident)
    return root


def load_job(path):
    path=path.resolve(); job=json.loads(path.read_text()); base=path.parent
    for key in ('library','mod_root','output'):
        job[key]=str((base/Path(job[key])).resolve())
    allowed={'nonuniform_scale':{'reject'},'supported_props':{'reject','independent-pivot'},'reused_states':{'reject','native'}}
    for k,v in job.get('policies',{}).items():
        if k not in allowed or v not in allowed[k]: raise ValueError(f'Unknown policy {k}={v}')
    for section in ('buildings','props','decals','shared_geometries'):
        for item in job.get(section,[]):
            item['blend']=str((base/Path(item['blend'])).resolve())
            identifier(item.get('asset_id',item.get('geometry_id')))
    if Path(job['output']).is_relative_to(Path(job['mod_root'])):
        raise ValueError('Output must be outside live ModBuddy content')
    return job


def build(job):
    out=Path(job['output']); decoded=json.loads((out/'decoded.json').read_text()); mod=Path(job['mod_root'])
    # Never reuse a successful stage with new partial outputs.
    stage=out/'stage'
    if stage.exists():
        previous=out/'manifest.json'
        if not previous.exists():
            raise ValueError(f'{stage} has no exporter manifest; choose a clean output folder')
        owned=json.loads(previous.read_text())['files']
        actual={str(p.relative_to(stage)):sha(p) for p in stage.rglob('*') if p.is_file()}
        if owned != actual:
            raise ValueError('Stage was edited or converted since build; choose another output folder to preserve it')
        shutil.rmtree(stage)
    stage.mkdir(parents=True)
    report={'status':'draft', 'blockers':[], 'placements':[], 'assets':[], 'geometry_only':[],
            'validation_boundary':'Blender/CN6/XML only; Windows conversion, cooking and in-game states are separate checks.'}
    templates=job['templates']
    geo_template=read_xml(mod/templates['geometry']); mtl_template=read_xml(mod/templates['material']); tex_template=read_xml(mod/templates['texture'])
    xlp_path=mod/job.get('xlp','XLPs/CSC_Tilebases.xlp')
    bindings={}
    for p in read_xml(mod/templates['attachment_library']).findall(POINTS+'/Element'):
        for v in p.findall('m_CookParams/m_Values/Element'):
            if txt(v,'m_ParamName')=='Asset' and txt(v,'m_EntryName'): bindings[txt(v,'m_EntryName')]=v
    catalogue={a['asset_id']:a for a in json.loads((Path(job['library'])/'catalogue.json').read_text())['assets']}
    references={item['asset_id'] for item in job.get('references', [])}
    models=decoded['models']; materials={}; model_materials={}; textures={}; source_inputs={}
    contracts={e['asset_id']:e['contract'] for e in job['buildings'] if e.get('contract')}
    report['scene_geometry_edits'] = [m['scene_geometry_edit'] for m in models.values()
                                      if m.get('scene_geometry_edit')]
    for ident,entry in decoded.get('library_sources',{}).items():
        if sha(entry['source']) != entry['sha256']: raise ValueError(f'Library asset changed; redecode {ident}')
        source_inputs[entry['source']]=entry['sha256']
    expected={e['asset_id']:e['blend'] for e in job['buildings']}
    expected.update({e['asset_id']:e['blend'] for e in job.get('props',[])})
    expected.update({e['geometry_id']:e['blend'] for e in job.get('decals',[])})
    expected.update({e['geometry_id']:e['blend'] for e in job.get('shared_geometries',[])})
    for ident,source in expected.items():
        if ident not in models or Path(models[ident]['source']).resolve()!=Path(source).resolve():
            raise ValueError('Job inputs changed; rerun decode')
    for model in models.values():
        if sha(model['source'])!=model['source_sha256']: raise ValueError(f'Redecode changed source {model["source"]}')
        source_inputs[model['source']]=model['source_sha256']
        model_materials[model['asset_id']]={}
        for mesh in model['meshes']:
            for mat in mesh['materials']:
                contract=contracts.get(model['asset_id'])
                if contract:
                    from asset_contract import material_for_mesh
                    target=material_for_mesh(mesh,mat,contract,job)
                    model_materials[model['asset_id']][(mesh['name'],mat['name'])]=target
                    materials[f'{model["asset_id"]}/{mesh["name"]}/{mat["name"]}']=target
                    continue
                ext=existing_material(mat,job,mod)
                ext=stage_ao_binding(mat,ext,mod,stage,textures,source_inputs,job.get('ao_policy','stage_explicit'))
                if ext:
                    materials[mat['name']]=ext; continue
                ims=mat['images']
                if not {'B','N','AO','G','M'}<=ims.keys(): raise ValueError(f'{mat["name"]}: provide image nodes labelled B/N/AO/G/M or explicit material_bindings')
                signature=json.dumps({k:v['sha256'] for k,v in ims.items()},sort_keys=True)
                name='CSC_Mat_'+hashlib.sha256(signature.encode()).hexdigest()[:12]
                if mat['name'] in materials and materials[mat['name']]!=name: raise ValueError(f'Material name collision {mat["name"]}')
                materials[mat['name']]=name
                mr=copy.deepcopy(mtl_template); set_text(mr,'m_Name',name)
                for v in mr.findall('m_CookParams/m_Values/Element'):
                    if v.find('m_eObjectType') is not None and v.find('m_eObjectType').text=='TEXTURE':
                        key=next((k for k,s in SLOTS.items() if s==txt(v,'m_ParamName')),None)
                        ti=''
                        if key in ims:
                            im=ims[key]; src=Path(im['path'])
                            if sha(src)!=im['sha256']: raise ValueError(f'Changed texture {src}')
                            ti=mat['ao_texture'] if key == 'AO' and mat.get('ao_texture') else 'CSC_Tex_'+im['sha256'][:12]+'_'+key
                            if ti not in textures:
                                dest=stage/'TextureSources'/(ti+src.suffix.lower()); dest.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(src,dest)
                                textures[ti]={'source':str(dest.relative_to(stage)), 'slot':key, 'size':im['size'], 'sha256':im['sha256'], 'format':'R8_UNORM' if key in ('AO','G','M','O','T') else 'R8G8B8A8_UNORM'}
                        set_text(v,'m_ObjectName',ti)
                write_xml(stage/'Materials'/(name+'.mtl'),mr)
        write_cn6(stage/'CN6'/(model['asset_id']+'.cn6'),model)
        write_xml(stage/'Geometries'/(model['asset_id']+'.geo'),geometry(model,geo_template))
        if model['kind'] in ('decal','shared_geometry'): report['geometry_only'].append(model['asset_id'])
    for name,im in textures.items():
        tr=copy.deepcopy(tex_template); set_text(tr,'m_Name',name)
        # Use R8 for scalar maps and RGBA8 for colour/normal maps.
        for e in tr.iter():
            if e.tag=='ePixelformat': e.text='PF_'+im['format']
            if e.tag=='m_Width': e.text=str(im['size'][0])
            if e.tag=='m_Height': e.text=str(im['size'][1])
            if e.tag=='m_NumMipMaps':
                # Firaxis AO TEX stores the highest mip index (2048 -> 11),
                # while its DDS header stores the number of levels (12).
                e.text=str(int(math.log2(max(im['size'])))) if im['slot']=='AO' else str(1+int(math.log2(max(im['size']))))
        set_text(tr,'m_SourceFilePath',str((stage/im['source']).resolve()))
        set_text(tr,'m_DataFiles/Element/m_RelativePath',name+'.dds')
        # Clone the class/export settings belonging to this slot where available.
        slot_template=mod/'Textures'/('CSC_Props_Shared_01_'+im['slot']+'.tex')
        if slot_template.exists():
            sr=read_xml(slot_template); set_text(tr,'m_ClassName',txt(sr,'m_ClassName'))
            for tag in ('m_ExportSettings','m_Tags'):
                old=tr.find(tag); replacement=sr.find(tag)
                if old is not None and replacement is not None:
                    tr.remove(old); tr.append(copy.deepcopy(replacement))
            for e in tr.iter():
                if e.tag=='ePixelformat': e.text='PF_'+im['format']
        write_xml(stage/'Textures'/(name+'.tex'),tr)
    for entry in job['buildings']:
        ident=entry['asset_id']; model=models[ident]
        root=read_xml(mod/entry.get('template_asset',templates.get('asset','')))
        set_text(root,'m_Name',ident)
        ms=root.find(MODELS); base_name=entry['replace_model']; old=next((m for m in ms if txt(m,'m_Name')==base_name),None)
        if old is None: raise ValueError(f'Missing main model {base_name}')
        states={txt(r,'m_StateName'):r for r in old.findall('m_GroupStates/Element') if txt(r,'m_MeshName')==entry['state_template_mesh']}
        if set(states)!=set(STATES): raise ValueError('State template must contain all five states')
        contract=entry.get('contract')
        selected_materials={**materials, **model_materials.get(ident,{})}
        visibility={mesh['name']: ('Worked',) for mesh in model['meshes']} if contract else ('Worked','Unworked','Unbuilt')
        index=list(ms).index(old); ms.remove(old); ms.insert(index,model_instance(model,selected_materials,visibility,states))
        if contract:
            from asset_contract import COBBLE_MATERIAL
            shared_ids=[contract['ruin_geometry']]
            if 'cobble_geometry' in contract:
                shared_ids.append(contract['cobble_geometry'])
            for shared_id in shared_ids:
                for previous in [m for m in ms if txt(m,'m_GeoName')==shared_id]:
                    ms.remove(previous)
            ruin=shared_model_from_geo(stage if contract.get('authored_ruin_geometry') else mod,contract['ruin_geometry'],
                lambda group: 'Pillage_Construction_01' if group=='Pillage_Construction_01' else contract['ruin_material'],
                lambda group: ('Construction',) if group=='Pillage_Construction_01' else ('Construction','Pillaged'))
            ms.append(ruin)
            if 'cobble_geometry' in contract:
                cobble=shared_model_from_geo(mod,contract['cobble_geometry'],
                    lambda group: COBBLE_MATERIAL, lambda group: ('Worked','Construction'))
                ms.append(cobble)
        for decal_id in entry.get('decals',[]):
            if models[decal_id]['kind']!='decal': raise ValueError('Expected decal geometry')
            old_decals=[m for m in ms if txt(m,'m_GeoName')==decal_id or txt(m,'m_Name')==decal_id]
            if len(old_decals)>1: raise ValueError(f'Duplicate decal model {decal_id}')
            if old_decals: ms.remove(old_decals[0])
            decal_states = entry.get('decal_states', {}).get(decal_id, ['Pillaged'])
            if not decal_states or any(state not in STATES for state in decal_states):
                raise ValueError(f'{ident}/{decal_id}: invalid decal visibility states')
            ms.append(model_instance(models[decal_id],materials,tuple(decal_states)))
        for required in entry.get('preserve_models',[]):
            if len([m for m in ms if txt(m,'m_Name')==required])!=1: raise ValueError(f'Missing/duplicate auxiliary model {required}')
        points=root.find(POINTS)
        remove=set(entry.get('replace_attachment_assets',[]))
        for p in list(points):
            refs=[txt(v,'m_EntryName') for v in p.findall('m_CookParams/m_Values/Element')]
            owned=entry.get('replace_owned_attachments',False) and txt(p,'m_ModelInstanceName') in (base_name,ident)
            if owned or remove.intersection(refs): points.remove(p)
        validate_support(model['attachments'])
        for a in model['attachments']:
            asset=a['source_asset_id']
            source=({'source_pack':'CSC','origin':'authored_blender'} if asset in models and models[asset]['kind']=='prop'
                    else {'source_pack':'CSC','origin':'existing_mod_asset'} if asset in references else catalogue[asset])
            if source.get('source_pack') not in ('Base game','Rise and Fall','Gathering Storm','CSC'):
                raise ValueError(f'{asset}: ineligible or unknown source pack')
            custom=source.get('origin')=='authored_blender'
            binding=csc_binding(asset,xlp_path) if custom or asset in references else bindings.get(asset)
            if binding is None: raise ValueError(f'Missing exact pantry XLP binding for {asset}')
            point,problems=attachment(a,binding,ident,job.get('policies',{}))
            if not custom and job.get('policies',{}).get('reused_states','reject')!='native':
                problems.append('reused asset keeps native state behavior; per-instance state gating is unverified')
            if point is not None: points.append(point)
            converted, _ = attachment_transform(a,job.get('policies',{}))
            row={'building':ident, **a, 'ae_transform':converted,
                 'placement_changed_by_exporter':False, 'binding_status':'blocked' if problems else 'representable', 'issues':problems}
            report['placements'].append(row)
            for problem in problems: report['blockers'].append(f'{ident}/{a["instance_id"]}: {problem}')
        if contract:
            for instance in ms:
                for state_row in instance.findall('m_GroupStates/Element'):
                    if txt(state_row,'m_StateName') in ('Unworked','Unbuilt'):
                        for parameter in state_row.findall('m_Values/m_Values/Element'):
                            if txt(parameter,'m_ParamName')=='Visible':
                                parameter.find('m_bValue').text='false'
        write_xml(stage/'Assets'/(ident+'.ast'),root); report['assets'].append(ident)
    # New props have their own state table and are registered once across all variants.
    for ident,model in models.items():
        if model['kind']!='prop': continue
        # Start from the empty behavior schema of a plain prop, not workshop FX.
        prop_template=read_xml(mod/templates['prop_asset'])
        root=copy.deepcopy(prop_template); set_text(root,'m_Name',ident)
        root.find(MODELS).clear(); root.find(MODELS).append(model_instance(model,materials,('Worked',)))
        root.find(POINTS).clear()
        for tag in ('m_animationBindings/m_Bindings','m_timelineBindings/m_Bindings','m_timelines/m_Timelines'):
            node=root.find('m_BehaviorData/m_behaviorDataSets/'+tag)
            if node is not None: node.clear()
        write_xml(stage/'Assets'/(ident+'.ast'),root); report['assets'].append(ident)
    write_xml(stage/'XLPs'/xlp_path.name,merge_xlp(read_xml(xlp_path),report['assets']))
    report['status']='blocked' if report['blockers'] else 'ready_for_windows_conversion'
    report['counts']={'custom_assets':len(report['assets']), 'geometry_only':len(report['geometry_only']),
                      'placements':len(report['placements']), 'materials':len(set(materials.values())), 'textures':len(textures)}
    report['preserved_models']={e['asset_id']:e.get('preserve_models',[]) for e in job['buildings']}
    report['material_bindings']=materials
    report['material_policy']=job.get('material_policy','generate_unbound')
    if contracts:
        from asset_contract import validate_stage
        report['contract_validation']=validate_stage(job,decoded,stage)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    destinations=[p.relative_to(stage) for p in stage.rglob('*') if p.is_file() and p.parts[-2]!='CN6']
    destinations += [Path('Geometries')/(ident+'.fgx') for ident in models]
    destinations += [Path('Textures')/(ident+'.dds') for ident in textures]
    manifest={'destination_baseline':{str(p):sha(mod/p) if (mod/p).exists() else None for p in destinations}, 'models':list(models), 'textures':textures, 'inputs':source_inputs,
              'files':{str(p.relative_to(stage)):sha(p) for p in sorted(stage.rglob('*')) if p.is_file()}}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':report['status'],'counts':report['counts'],'blockers':len(report['blockers']),'report':str(out/'report.json')},indent=2))
    return 2 if report['blockers'] else 0


def validate_dds(path, texture):
    import struct
    raw=Path(path).read_bytes()
    if len(raw)<128 or raw[:4]!=b'DDS ' or struct.unpack_from('<I',raw,4)[0]!=124:
        raise ValueError(f'Invalid DDS header: {path}')
    height,width=struct.unpack_from('<II',raw,12)
    mips=struct.unpack_from('<I',raw,28)[0] or 1
    expected=1+int(math.log2(max(texture['size'])))
    if [width,height]!=texture['size'] or mips!=expected:
        raise ValueError(f'DDS dimensions/mip count disagree with TEX: {path}')
    bpp=1 if texture['format']=='R8_UNORM' else 4
    offset=128
    if raw[84:88]==b'DX10':
        if len(raw)<148: raise ValueError(f'Truncated DDS: {path}')
        dxgi=struct.unpack_from('<I',raw,128)[0]
        if dxgi!=(61 if bpp==1 else 28): raise ValueError(f'DDS format disagrees with TEX: {path} (DXGI {dxgi})')
        offset=148
    elif struct.unpack_from('<I',raw,88)[0] != bpp*8:
        raise ValueError(f'DDS pixel size disagrees with TEX: {path}')
    if texture.get('slot')=='AO' and (raw[84:88]==b'DX10' or struct.unpack_from('<I',raw,80)[0]!=0x40):
        raise ValueError(f'AO DDS must use Firaxis-compatible 8-bit luminance header: {path}')
    needed=sum(max(1,width>>i)*max(1,height>>i)*bpp for i in range(mips))
    if len(raw)<offset+needed: raise ValueError(f'Truncated DDS pixel data: {path}')


def normalize_ao_dds(path, texture, template_path):
    """Keep texconv mip pixels, but use the installed Firaxis R8 AO header."""
    import struct
    source=Path(path).read_bytes()
    template=Path(template_path).read_bytes()
    if (len(source)<128 or len(template)<128 or source[:4]!=b'DDS ' or template[:4]!=b'DDS '
            or source[84:88]==b'DX10' or template[84:88]==b'DX10'
            or struct.unpack_from('<I',source,88)[0]!=8
            or struct.unpack_from('<I',template,88)[0]!=8
            or struct.unpack_from('<I',template,80)[0]!=0x40):
        raise ValueError('AO DDS conversion needs an installed Firaxis 8-bit luminance template')
    width,height=texture['size']
    levels=1+int(math.log2(max(width,height)))
    header=bytearray(template[:128])
    struct.pack_into('<II',header,12,height,width)
    struct.pack_into('<I',header,28,levels)
    payload=source[128:]
    needed=sum(max(1,width>>i)*max(1,height>>i) for i in range(levels))
    if len(payload)!=needed:
        raise ValueError(f'AO DDS mip payload has unexpected size: {path}')
    Path(path).write_bytes(header+payload)


def convert(job,converter,texconv):
    out=Path(job['output']); stage=out/'stage'; report=json.loads((out/'report.json').read_text()); manifest=json.loads((out/'manifest.json').read_text())
    if report['blockers']: raise ValueError('Resolve report.json blockers and rebuild before Windows conversion')
    for rel,h in manifest['files'].items():
        if sha(stage/rel)!=h: raise ValueError(f'Staged file changed: {rel}; rebuild')
    converter=Path(converter).resolve(); texconv=Path(texconv).resolve()
    logs=out/'logs'; logs.mkdir(exist_ok=True)
    for ident in manifest['models']:
        dest=stage/'Geometries'/(ident+'.fgx')
        if dest.exists(): dest.unlink()
        with (logs/(ident+'.log')).open('w') as log:
            subprocess.run([str(converter),str(stage/'CN6'/(ident+'.cn6')),str(dest),'2'],cwd=converter.parent,stdout=log,stderr=subprocess.STDOUT,check=True)
        if not dest.is_file() or dest.stat().st_size<100: raise ValueError(f'Converter produced no valid-sized output for {ident}; see full log')
    for ident,tex in manifest['textures'].items():
        dest=stage/'Textures'/(ident+'.dds')
        if dest.exists(): dest.unlink()
        cmd=[str(texconv),'-nologo','-y','-m','0','-f',tex['format'],'-o',str(stage/'Textures')]
        cmd += ['--ignore-srgb']
        if tex['slot'] in ('B','E'): cmd+=['-srgb']
        cmd+=[str(stage/tex['source'])]
        with (logs/(ident+'.log')).open('w') as log: subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
        dest=stage/'Textures'/(ident+'.dds')
        if tex['slot']=='AO':
            normalize_ao_dds(dest,tex,Path(job['mod_root'])/'Textures'/'CSC_Props_Shared_01_AO.dds')
        validate_dds(dest,tex)
    manifest['converted_files']={str(p.relative_to(stage)):sha(p) for p in stage.rglob('*') if p.is_file()}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    report['status']='converted_pending_asset_editor_and_game_review'
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Windows conversion complete. Stage is ready for Asset Editor review; no live project files changed.')


def install(job):
    """Explicit Windows deployment, with preflight, backups and rollback; merge live XLP."""
    out=Path(job['output']); stage=out/'stage'; mod=Path(job['mod_root'])
    report=json.loads((out/'report.json').read_text()); manifest=json.loads((out/'manifest.json').read_text())
    if report['status']!='converted_pending_asset_editor_and_game_review' or not manifest.get('converted_files'):
        raise ValueError('Successful Windows conversion is required before install')
    for rel,h in manifest['converted_files'].items():
        if sha(stage/rel)!=h: raise ValueError(f'Converted stage changed: {rel}')
    predecessor=None
    for prior_path in sorted(out.parent.glob('*/job.json'), reverse=True):
        if prior_path.parent == out or prior_path.parent.name >= out.name:
            continue
        prior_report_path=prior_path.parent/'report.json'
        prior_receipt_path=prior_path.parent/'install-receipt.json'
        if not prior_report_path.is_file() or not prior_receipt_path.is_file():
            continue
        prior_job=json.loads(prior_path.read_text())
        prior_report=json.loads(prior_report_path.read_text())
        if Path(prior_job.get('mod_root','')).resolve()!=mod.resolve():
            continue
        if prior_report.get('status') in ('purged','uninstalled'):
            # A deliberate removal ends this folder's ownership chain. Older
            # receipts no longer describe the live files after that boundary.
            break
        if prior_report.get('status')=='installed_pending_asset_editor_and_game_review':
            predecessor=(prior_path,prior_report_path,prior_report,json.loads(prior_receipt_path.read_text()))
            break
    previous_files={}; retired_ids=set(); owned_ids=set()
    if predecessor:
        prior_path,_,prior_report,prior_receipt=predecessor
        old_files=prior_receipt.get('installed_sha256',{})
        current_files={rel for rel in manifest['converted_files'] if Path(rel).parts[0]!='CN6'}
        for rel,expected_hash in old_files.items():
            p=Path(rel)
            if str(p) in current_files or p.is_absolute() or '..' in p.parts or len(p.parts)!=2 or p.parts[0] not in (
                    'Assets','Geometries','Materials','Textures','TextureSources'):
                continue
            target=mod/p
            if not target.is_file() or sha(target)!=expected_hash:
                raise ValueError(f'Prior run output changed; cannot retire {rel}')
            previous_files[p]=expected_hash
        owned_ids=set(prior_receipt.get('owned_xlp_ids',prior_receipt.get('xlp_added_ids',[])))
        retired_ids=owned_ids-set(report['assets'])
    payload={}
    for rel in manifest['converted_files']:
        p=Path(rel)
        if p.parts[0]=='CN6': continue
        if p.parts[0]=='XLPs':
            root=merge_xlp(read_xml(mod/p),report['assets'])
            entries=root.find('m_Entries')
            found={txt(e,'m_EntryID') for e in entries if txt(e,'m_EntryID') in retired_ids and txt(e,'m_ObjectName')==txt(e,'m_EntryID')}
            if found!=retired_ids:
                raise ValueError(f'Prior run XLP entries changed; cannot retire {sorted(retired_ids-found)}')
            for e in list(entries):
                if txt(e,'m_EntryID') in retired_ids: entries.remove(e)
            ET.indent(root,space='  ')
            payload[p]=ET.tostring(root,encoding='utf-8',xml_declaration=True)
            continue
        current=sha(mod/p) if (mod/p).exists() else None
        if current != manifest['destination_baseline'].get(rel):
            raise ValueError(f'Live destination changed since staging: {rel}; rebuild against current project')
        if p.suffix=='.tex':
            r=read_xml(stage/p); texture=manifest['textures'][p.stem]
            set_text(r,'m_SourceFilePath',str((mod/texture['source']).resolve())); ET.indent(r,space='  ')
            payload[p]=ET.tostring(r,encoding='utf-8',xml_declaration=True)
        else: payload[p]=(stage/p).read_bytes()
    # Keep an exact pre-install copy. No cache deletion, ArtDef rewriting, or cook here.
    import datetime
    backup=out/'backups'/datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True); created=[]; changed=[]
    xlp_added=[]
    for p in payload:
        if p.parts[0]=='XLPs':
            before={txt(e,'m_EntryID') for e in read_xml(mod/p).find('m_Entries')}
            xlp_added.extend(sorted(set(report['assets'])-before))
    try:
        for p,data in payload.items():
            dest=mod/p; dest.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():
                old=backup/p; old.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(dest,old)
            else: created.append(str(p))
            changed.append(p); dest.write_bytes(data)
        for p in previous_files:
            dest=mod/p; old=backup/p; old.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(dest,old); changed.append(p); dest.unlink()
    except Exception:
        for p in reversed(changed):
            old=backup/p
            if old.exists(): shutil.copy2(old,mod/p)
            elif str(p) in created: (mod/p).unlink(missing_ok=True)
        raise
    (backup/'created-files.json').write_text(json.dumps(created,indent=2)+'\n')
    receipt={'backup':str(backup),'installed_sha256':{str(p):hashlib.sha256(data).hexdigest()
             for p,data in payload.items() if p.parts[0]!='XLPs'},'xlp_added_ids':xlp_added,
             'owned_xlp_ids':sorted((owned_ids|set(xlp_added))-retired_ids),
             'retired_files':[str(p) for p in previous_files], 'retired_xlp_ids':sorted(retired_ids),
             'predecessor_job':str(predecessor[0]) if predecessor else None}
    (out/'install-receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    report['status']='installed_pending_asset_editor_and_game_review'; report['backup']=str(backup)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if predecessor:
        _,prior_report_path,prior_report,_=predecessor
        prior_report['status']='superseded'
        (prior_report_path).write_text(json.dumps(prior_report,indent=2)+'\n')
    print(f'Installed {len(payload)} files; backup: {backup}. Refresh AE dependencies, cook, and verify in game.')


def uninstall(job, dry_run=False, purge=False, force=False):
    """Undo one installed folder export, preserving later edits and prior assets."""
    import datetime
    if force and not purge:
        raise ValueError('Force is supported only with purge')
    out=Path(job['output']); mod=Path(job['mod_root'])
    report=json.loads((out/'report.json').read_text())
    manifest=json.loads((out/'manifest.json').read_text())
    if report['status']!='installed_pending_asset_editor_and_game_review':
        raise ValueError('This export run is not currently installed')
    backup=Path(report['backup']).resolve()
    if not backup.is_relative_to((out/'backups').resolve()) or not (backup/'created-files.json').is_file():
        raise ValueError('Missing or invalid pre-install backup')
    created=set(json.loads((backup/'created-files.json').read_text()))
    receipt_path=out/'install-receipt.json'
    receipt=json.loads(receipt_path.read_text()) if receipt_path.is_file() else None
    if receipt and Path(receipt['backup']).resolve()!=backup:
        raise ValueError('Install receipt and backup disagree')
    files={}
    forced=[]
    for rel in manifest['converted_files']:
        p=Path(rel)
        if p.parts and p.parts[0]=='CN6': continue
        if p.is_absolute() or '..' in p.parts or len(p.parts)!=2 or p.parts[0] not in (
                'Assets','Geometries','Materials','Textures','TextureSources','XLPs'):
            raise ValueError(f'Invalid installed output path: {rel}')
        dest=mod/p
        if dest.is_symlink() or any(a.is_symlink() for a in dest.parents if a.is_relative_to(mod)):
            raise ValueError(f'Symlink in installed output path: {rel}')
        if p.parts[0]=='XLPs': continue
        if receipt:
            expected=receipt['installed_sha256'].get(rel)
            if not expected: raise ValueError(f'Missing install receipt for {rel}')
        elif p.suffix=='.tex':
            r=read_xml(out/'stage'/p)
            texture=manifest['textures'][p.stem]
            set_text(r,'m_SourceFilePath',str((mod/texture['source']).resolve()))
            ET.indent(r,space='  ')
            expected=hashlib.sha256(ET.tostring(r,encoding='utf-8',xml_declaration=True)).hexdigest()
        else:
            expected=sha(out/'stage'/p)
        if not dest.is_file() or sha(dest)!=expected:
            if not force:
                raise ValueError(f'Installed output changed or missing: {rel}; review it before uninstalling')
            forced.append((p, 'missing' if not dest.is_file() else 'changed'))
        old=backup/p
        if purge:
            files[p]='delete'
        elif rel in created:
            if old.exists(): raise ValueError(f'Unexpected backup for created file: {rel}')
            files[p]='delete'
        else:
            if not old.is_file(): raise ValueError(f'Missing original file backup: {rel}')
            files[p]='restore'
    if receipt and not purge:
        for rel in receipt.get('retired_files',[]):
            p=Path(rel)
            if p.is_absolute() or '..' in p.parts or len(p.parts)!=2 or p.parts[0] not in (
                    'Assets','Geometries','Materials','Textures','TextureSources'):
                raise ValueError(f'Invalid retired output path: {rel}')
            if not (backup/p).is_file() or (mod/p).exists():
                raise ValueError(f'Retired output cannot be restored safely: {rel}')
            files[p]='restore'
    xlp_paths=[Path(rel) for rel in manifest['converted_files'] if Path(rel).parts[0]=='XLPs']
    xlp_updates={}
    xlp_removals={}
    for p in xlp_paths:
        old=backup/p
        if not old.is_file(): raise ValueError(f'Missing original XLP backup: {p}')
        prior={txt(e,'m_EntryID') for e in read_xml(old).find('m_Entries')}
        added=set(report['assets'] if purge else
                  (receipt['xlp_added_ids'] if receipt else report['assets']))
        if not purge: added-=prior
        if not (mod/p).is_file():
            if not force:
                raise ValueError(f'Installed XLP changed or missing: {p}')
            forced.append((p, 'missing'))
            xlp_removals[p]=[]
            continue
        root=read_xml(mod/p); entries=root.find('m_Entries')
        matching=[e for e in entries if txt(e,'m_EntryID') in added]
        found={txt(e,'m_EntryID') for e in matching}
        if found!=added or any(txt(e,'m_ObjectName')!=txt(e,'m_EntryID') for e in matching):
            if not force:
                raise ValueError(f'Installed XLP entries changed or missing: {p}')
            forced.append((p, 'entries changed or missing'))
        for e in matching: entries.remove(e)
        if not purge and receipt:
            prior_entries={txt(e,'m_EntryID'):e for e in read_xml(old).find('m_Entries')}
            for ident in receipt.get('retired_xlp_ids',[]):
                if ident not in prior_entries or any(txt(e,'m_EntryID')==ident for e in entries):
                    raise ValueError(f'Retired XLP entry cannot be restored safely: {ident}')
                entries.append(copy.deepcopy(prior_entries[ident]))
        ET.indent(root,space='  ')
        xlp_updates[p]=ET.tostring(root,encoding='utf-8',xml_declaration=True)
        xlp_removals[p]=sorted(added)
    xlp_removed=sum(len(ids) for ids in xlp_removals.values())
    deletions=sum(v=='delete' for v in files.values())
    restorations=sum(v=='restore' for v in files.values())
    print(f'Uninstall plan: {deletions} file{"s" if deletions!=1 else ""} to delete, '
          f'{restorations} prior file{"s" if restorations!=1 else ""} to restore, '
          f'{xlp_removed} XLP entries to remove.')
    for p,reason in forced:
        print(f'  force purge ({reason}): {mod/p}')
    for p,action in sorted(files.items()): print(f'  {action}: {mod/p}')
    for p in xlp_paths:
        for ident in xlp_removals[p]: print(f'  remove XLP entry: {mod/p} :: {ident}')
        if not xlp_removals[p]: print(f'  no XLP entries to remove: {mod/p}')
    if dry_run: return
    undo=out/'backups'/('uninstall-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
    undo.mkdir(parents=True)
    changed=[]
    try:
        for p in [*files,*xlp_updates]:
            dest=mod/p; saved=undo/p; saved.parent.mkdir(parents=True,exist_ok=True)
            if dest.exists():
                shutil.copy2(dest,saved); changed.append(p)
            if p in xlp_updates: dest.write_bytes(xlp_updates[p])
            elif files[p]=='restore': shutil.copy2(backup/p,dest)
            else: dest.unlink(missing_ok=True)
    except Exception:
        for p in reversed(changed): shutil.copy2(undo/p,mod/p)
        raise
    report['status']='purged' if purge else 'uninstalled'; report['uninstall_backup']=str(undo)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    if receipt and receipt.get('predecessor_job') and not purge:
        prior_report_path=Path(receipt['predecessor_job']).parent/'report.json'
        prior_report=json.loads(prior_report_path.read_text())
        if prior_report.get('status')!='superseded':
            raise ValueError('Predecessor report changed; review restored run status')
        prior_report['status']='installed_pending_asset_editor_and_game_review'
        prior_report_path.write_text(json.dumps(prior_report,indent=2)+'\n')
    print(f'Uninstalled export run; previous live files backed up at {undo}.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=['decode','build','convert','install','uninstall']); parser.add_argument('job',type=Path)
    parser.add_argument('--blender'); parser.add_argument('--converter'); parser.add_argument('--texconv')
    parser.add_argument('--dry-run',action='store_true')
    parser.add_argument('--purge',action='store_true')
    parser.add_argument('--force',action='store_true')
    args=parser.parse_args(); job=load_job(args.job); out=Path(job['output']); out.mkdir(parents=True,exist_ok=True)
    if args.force and (args.command!='uninstall' or not args.purge):
        parser.error('--force requires uninstall with --purge')
    if args.command=='decode':
        if not args.blender: parser.error('decode requires --blender')
        resolved=out/'resolved-job.json'; resolved.write_text(json.dumps(job,indent=2)+'\n')
        subprocess.run([args.blender,'--background','--factory-startup','--python-exit-code','1','--python',str(Path(__file__).with_name('decode_blend.py')),'--',str(resolved),str(out/'decoded.json')],check=True)
        return 0
    if args.command=='build': return build(job)
    if args.command=='install':
        install(job); return 0
    if args.command=='uninstall':
        uninstall(job,args.dry_run,args.purge,args.force); return 0
    if not args.converter or not args.texconv: parser.error('convert requires --converter and --texconv')
    convert(job,args.converter,args.texconv); return 0

if __name__=='__main__':
    try: sys.exit(main())
    except (ValueError,KeyError,OSError,subprocess.CalledProcessError) as error:
        print(f'ERROR: {error}',file=sys.stderr); sys.exit(1)
