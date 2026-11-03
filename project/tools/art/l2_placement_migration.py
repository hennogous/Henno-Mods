"""Backed-up L2 placement and fixed-prop migration from saved AE assemblies."""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
import copy
import hashlib
import math
import os
import time
import numpy as np

from storage_pivot_trial import (ROOT, MOD, POINTS, MODELS, parse, txt,
    point_matrix, set_point_matrix, save, helper)

ART = Path('C:/Users/Shadow/Desktop/Working Files/3D Art')
OUT = Path('C:/Users/Shadow/Desktop/Codex/L2-placement-20261025')
BUILDINGS = ['CSC_TAILORS_Tailor', 'CSC_BAKERS_Bakery',
             'CSC_TAILORS_Fashion_House', 'CSC_BAKERS_Cafe']

def write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding='utf-8')

def binding(point):
    return next(txt(e, 'm_EntryName') for e in point.findall('m_CookParams/m_Values/Element')
                if txt(e, 'm_ParamName') == 'Asset')

def snapshot():
    assert not (OUT/'baseline.json').exists(), 'Never overwrite the baseline'
    assets = set()
    geos = {'CSC_Level_2', 'CSC_Level_2_CON+PIL', 'CSC_Level_2_PIL_Decals',
            'CSC_ALL_District_Base', 'CSC_ALL_Classical_Base_03_Road_Decals'}
    report = {}
    def visit(name):
        if name in assets: return
        p = MOD/'Assets'/(name+'.ast')
        if not p.exists(): return
        assets.add(name)
        root = parse(p)
        models = [dict(name=txt(m,'m_Name'),geo=txt(m,'m_GeoName')) for m in root.findall(MODELS+'/Element')]
        geos.update(m['geo'] for m in models)
        points = [dict(name=txt(p,'m_Name'),asset=binding(p),owner=txt(p,'m_ModelInstanceName'),
                       bone=txt(p,'m_BoneName'),matrix=point_matrix(p).tolist()) for p in root.findall(POINTS+'/Element')]
        report[name] = dict(models=models,points=points)
        for row in points: visit(row['asset'])
    for name in BUILDINGS:
        visit(name);visit(name+'_2')
    visit('CSC_TEST_Tailor_Wrapper')
    paths = [MOD/'Assets'/(n+'.ast') for n in sorted(assets)]
    paths += [MOD/'Geometries'/(n+e) for n in sorted(geos) for e in ('.fgx','.geo')]
    paths += [ROOT/'project/tools/blender/ae_render_camera_presets.json']
    import hashlib
    baseline = {}
    for p in paths:
        if not p.exists(): continue
        dst=OUT/'before'/p.relative_to(ROOT)
        dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dst)
        baseline[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    write(OUT/'baseline.json',baseline)
    write(OUT/'assembly-inventory.json',report)
    exe,_=helper(OUT/'cache')
    summary={}
    for name in sorted(geos):
        p=MOD/'Geometries'/(name+'.fgx')
        if not p.exists(): continue
        dest=OUT/'native-before'/(name+'.json');dest.parent.mkdir(exist_ok=True)
        subprocess.run([str(exe),str(exe.parent),str(p),str(dest)],cwd=exe.parent,check=True,capture_output=True)
        raw=json.loads(dest.read_text())
        summary[name]=dict(models=raw['models'],meshes=[dict(name=m['name'],vertices=len(m['vertices']),
            groups=m['groups'],bindings=m['boneBindings'],bounds=[[min(v['position'][i] for v in m['vertices']) for i in range(3)],
            [max(v['position'][i] for v in m['vertices']) for i in range(3)]]) for m in raw['meshes']])
    write(OUT/'native-summary.json',summary)
    print('Snapshot:',len(assets),'assets;',len(summary),'native geometries')
    for name in report:
        if name in BUILDINGS or name.removesuffix('_2') in BUILDINGS:
            print(name,json.dumps(report[name]))

def before(name, folder='Assets', ext='.ast'):
    return OUT/'before/Civ Supply Chains'/folder/(name+ext)

def native(name):
    return json.loads((OUT/'native-before'/(name+'.json')).read_text())

def transform_mesh(mesh, matrix):
    result=copy.deepcopy(mesh)
    rotation=matrix[:3,:3]
    scale=np.linalg.norm(rotation[:,0]);rotation=rotation/scale
    for v in result['vertices']:
        v['position']=(matrix @ [*v['position'],1])[:3].tolist()
        for key in ('normal','tangent','binormal'):
            v[key]=(rotation @ v[key]).tolist()
    return result

def state_values(row):
    return {txt(e,'m_ParamName'):e for e in row.findall('m_Values/m_Values/Element')}

def plan():
    from render_ae_asset import Resolver, Assembly, DEFAULT_SDK, texture_bindings, PRESETS
    roots={n:parse(before(n)) for name in BUILDINGS for n in (name,name+'_2')}
    wrapper=parse(before('CSC_TEST_Tailor_Wrapper')).find(POINTS+'/Element')
    T=point_matrix(wrapper)
    # The editable shared L2 and saved Tailor already coincide. The old generic
    # runtime/Bakery intact mesh still carries a former XY offset.
    source=native('CSC_TAILORS_Tailor')['meshes'][0]
    old=native('CSC_BAKERS_Bakery')['meshes'][0]
    a=np.array([v['position'] for v in source['vertices']]);b=np.array([v['position'] for v in old['vertices']])
    shift=a.min(axis=0)-b.min(axis=0)
    assert np.max(np.min(np.linalg.norm(a[:,None,:]-(b[None,:,:]+shift),axis=2),axis=1))<.00004
    D=np.eye(4);D[:3,3]=shift
    transforms={'CSC_TAILORS_Tailor':T,'CSC_BAKERS_Bakery':T@D}
    write(OUT/'transform.json',dict(wrapper=T.tolist(),bakery_old_to_kit=D.tolist(),
        bakery_old_to_new=(T@D).tolist(),blender_rotation_degrees=math.degrees(.203275)))
    resolver=Resolver(MOD,DEFAULT_SDK);assembly=Assembly(resolver)
    geometry_jobs=[]
    source_plan=[]
    def geometry(name,raw,geo,states,sourcepath):
        geo.find('m_Name').set('text',name)
        if raw['models'][0]['name']!=name:
            oldroot=raw['models'][0]['name'];raw['models'][0]['name']=name
            raw['models'][0]['bones'][0]['name']=name
            geo.find('m_ModelName').set('text',name)
            for b in geo.findall('m_Bones/Element'):
                if b.get('text')==oldroot:b.set('text',name)
        for f in geo.findall('m_DataFiles/Element/m_RelativePath'):f.set('text',name+'.fgx')
        material_keys={}
        for mesh in raw['meshes']:
            row=next(m for m in geo.find('m_Meshes') if txt(m,'m_Name')==mesh['name'])
            material_keys[mesh['name']]={}
            for g in row.find('m_Groups'):
                group=txt(g,'m_Name')
                matching=[s for s in states if txt(s,'m_MeshName')==mesh['name'] and txt(s,'m_GroupName')==group]
                preferred=next((s for s in matching if txt(s,'m_StateName')=='Worked' and state_values(s)['Visible'].findtext('m_bValue')=='true'),None)
                if preferred is None:preferred=next((s for s in matching if state_values(s)['Visible'].findtext('m_bValue')=='true'),None)
                if preferred is None: preferred=matching[0] if matching else None
                if preferred is not None:
                    vals=state_values(preferred);mat=txt(vals['Material'],'m_ObjectName')
                elif 'Scaffold' in mesh['name']:mat='Pillage_Construction_01'
                elif 'PIL_Decals' in name: mat='Pillage_Decal_01'
                else:mat='CSC_TAILORS_E'
                enabled=preferred is not None and state_values(preferred).get('EmissiveEnabled') is not None and state_values(preferred)['EmissiveEnabled'].findtext('m_bValue')=='true'
                material_keys[mesh['name']][group]=assembly.material(mat,{},MOD/'Assets',enabled)
        raw['models'][0]['meshBindings']=[m['name'] for m in raw['meshes']]
        path=OUT/'staged/Geometries'/(name+'.json');write(path,raw)
        save(geo,OUT/'staged/Geometries'/(name+'.geo'))
        job=dict(name=name,native=str(path),groups={txt(m,'m_Name'):[txt(g,'m_Name') for g in m.find('m_Groups')] for m in geo.find('m_Meshes')},materials=material_keys,source=str(sourcepath))
        geometry_jobs.append(job)
        return job
    # Common masters and existing Tailor state geometry all receive the wrapper.
    common=[('CSC_Level_2',ART/'Level 2/CSC_Level_2.blend'),
      ('CSC_Level_2_CON+PIL',ART/'Level 2/CSC_Level_2_CON+PIL.blend'),
      ('CSC_Level_2_PIL_Decals',ART/'Level 2/CSC_Level_2_PIL_Decals.blend'),
      ('CSC_TAILORS_Tailor_CON+PIL',ART/'TAILORS/Tailor/revision-11-l2-placement/CSC_TAILORS_Tailor_CON+PIL.blend'),
      ('CSC_TAILORS_Tailor_PIL_Decals',ART/'TAILORS/Tailor/revision-11-l2-placement/CSC_TAILORS_Tailor_PIL_Decals.blend'),
      ('CSC_BAKERS_Bakery_PIL_Decals',ART/'BAKERS/Bakery/revision-09-l2-placement/CSC_BAKERS_Bakery_PIL_Decals.blend')]
    for name,path in common:
        raw=native(name);geo=parse(before(name,'Geometries','.geo'))
        if name=='CSC_Level_2':
            raw['meshes'][0]=copy.deepcopy(source)
        raw['meshes']=[transform_mesh(m,T) for m in raw['meshes']]
        state_roots=[roots['CSC_TAILORS_Tailor'],roots['CSC_BAKERS_Bakery']]
        states=[s for root in state_roots for m in root.findall(MODELS+'/Element') if txt(m,'m_GeoName')==name for s in m.findall('m_GroupStates/Element')]
        if name=='CSC_Level_2':states=[s for s in roots['CSC_BAKERS_Bakery'].findall(MODELS+'/Element/m_GroupStates/Element') if txt(s,'m_MeshName')=='CSC_Level_2_Bldg']
        if name=='CSC_Level_2_PIL_Decals':states=[s for s in roots['CSC_BAKERS_Bakery'].findall(MODELS+'/Element/m_GroupStates/Element') if txt(s,'m_MeshName') in [m['name'] for m in raw['meshes']]]
        geometry(name,raw,geo,states,path)
    wanted={'CSC_BAKERS_Bakery':{'CSC_BAKERS_Oven_v2','CSC_BAKERS_Peel'},
            'CSC_TAILORS_Fashion_House':{'CSC_TAILORS_Fashion_House_Fitting'},
            'CSC_BAKERS_Cafe':{'CSC_BAKERS_Cafe_Counter','CSC_BAKERS_Cafe_Brewing_Set','CSC_BAKERS_Cafe_Pastry_Tray'},
            'CSC_TAILORS_Tailor':set()}
    folders={'CSC_BAKERS_Bakery':'BAKERS/Bakery/revision-09-l2-placement',
      'CSC_TAILORS_Tailor':'TAILORS/Tailor/revision-11-l2-placement',
      'CSC_TAILORS_Fashion_House':'TAILORS/Fashion House/revision-13-fixed-fitting',
      'CSC_BAKERS_Cafe':'BAKERS/Cafe/revision-01-fixed-counters'}
    bundle_report=[]
    for name in BUILDINGS:
        basegeo='CSC_Level_3' if name=='CSC_BAKERS_Cafe' else name
        main=next(m for m in roots[name].find(MODELS) if txt(m,'m_GeoName')==basegeo)
        raw=native(basegeo);geo=parse(before(basegeo,'Geometries','.geo'))
        # This old oven is invisible in every state; avoid keeping obsolete art
        # alongside the explicitly requested current Oven_v2.
        if name=='CSC_BAKERS_Bakery':
            raw['meshes']=[m for m in raw['meshes'] if m['name']!='CSC_BAKERS_Oven_Bldg']
            for m in list(geo.find('m_Meshes')):
                if txt(m,'m_Name')=='CSC_BAKERS_Oven_Bldg':geo.find('m_Meshes').remove(m)
        if name in transforms:raw['meshes']=[transform_mesh(m,transforms[name]) for m in raw['meshes']]
        points=[p for p in roots[name].findall(POINTS+'/Element') if binding(p) in wanted[name]]
        states=list(main.findall('m_GroupStates/Element'))
        slots=[]
        for idx,p in enumerate(points):
            prop=binding(p);prop_root=parse(before(prop));prop_model=prop_root.find(MODELS+'/Element')
            prop_geo=txt(prop_model,'m_GeoName');prop_native=native(prop_geo)
            assert len(prop_native['models'])==1
            matrix=transforms.get(name,np.eye(4))@point_matrix(p)
            # All selected attachment owners bind to the identity model root.
            owner=next(m for m in roots[name].find(MODELS) if txt(m,'m_Name')==txt(p,'m_ModelInstanceName'))
            owner_raw=native(txt(owner,'m_GeoName'))
            bone=next(b for b in owner_raw['models'][0]['bones'] if b['name']==txt(p,'m_BoneName'))
            assert np.max(abs(np.array(bone['inverseWorld']).reshape(4,4)-np.eye(4)))<1e-5
            names={}
            for pm in prop_native['meshes']:
                mesh=transform_mesh(pm,matrix);newname=f"CSC_Fixed_{prop.removeprefix('CSC_')}_{idx+1:02}_{len(names)}"
                names[pm['name']]=newname;mesh['name']=newname;mesh['boneBindings']=['Bone']
                for v in mesh['vertices']:v['boneIndices']=[0]*8;v['boneWeights']=[255]+[0]*7
                raw['meshes'].append(mesh)
                pg=parse(before(prop_geo,'Geometries','.geo'))
                g=copy.deepcopy(next(m for m in pg.find('m_Meshes') if txt(m,'m_Name')==pm['name']))
                g.find('m_Name').set('text',newname);geo.find('m_Meshes').append(g)
            slot=dict(point=txt(p,'m_Name'),asset=prop,matrix=matrix.tolist(),meshes=names)
            slots.append(slot)
            for s in prop_model.findall('m_GroupStates/Element'):
                r=copy.deepcopy(s);r.find('m_MeshName').set('text',names[txt(s,'m_MeshName')]);states.append(r)
        for variant in (name,name+'_2'):
            root=roots[variant];model=next(m for m in root.find(MODELS) if txt(m,'m_GeoName')==basegeo)
            model.find('m_GeoName').set('text',name)
            groupstates=model.find('m_GroupStates')
            if name=='CSC_BAKERS_Bakery':
                for s in list(groupstates):
                    if txt(s,'m_MeshName')=='CSC_BAKERS_Oven_Bldg':groupstates.remove(s)
            for slot in slots:
                p=next(p for p in root.find(POINTS) if txt(p,'m_Name')==slot['point'])
                # AE serialisation differs by <0.001 source units for the
                # Fashion House copy; preserve a single practically coincident model.
                error=float(np.max(abs(transforms.get(name,np.eye(4))@point_matrix(p)-slot['matrix'])))
                assert error<.001,(variant,slot['point'],error)
                prop_root=parse(before(slot['asset']))
                for s in prop_root.find(MODELS+'/Element/m_GroupStates'):
                    row=copy.deepcopy(s);row.find('m_MeshName').set('text',slot['meshes'][txt(s,'m_MeshName')]);groupstates.append(row)
                root.find(POINTS).remove(p)
            if name in transforms:
                for p in root.findall(POINTS+'/Element'):set_point_matrix(p,transforms[name]@point_matrix(p))
            # Alternate Bakery had lost its shared construction/pillage models.
            if variant=='CSC_BAKERS_Bakery_2':
                for m in roots[name].find(MODELS):
                    if txt(m,'m_GeoName') in ['CSC_Level_2_CON+PIL','CSC_BAKERS_Bakery_PIL_Decals']:
                        root.find(MODELS).append(copy.deepcopy(m))
            normalize_model_owners(root)
            save(root,OUT/'staged/Assets'/(variant+'.ast'))
        job=geometry(name,raw,geo,states,ART/folders[name]/(name+'.blend'))
        source_plan.append(dict(job=name,source=str(ART/folders[name]/(name+'_2.blend')),variant=name+'_2'))
        bundle_report.append(dict(asset=name,slots=slots,vertices=sum(len(m['vertices']) for m in raw['meshes'])))
    profiles=json.loads((OUT/'before/project/tools/blender/ae_render_camera_presets.json').read_text())
    l2=profiles['classes']['L2']
    for mode in ['icon','sv']:
        l2[mode]['matrix_world']=(T@np.array(l2[mode]['matrix_world'])).tolist()
        l2[mode]['sun_direction']=(T[:3,:3]@PRESETS[mode]['sun_direction']).tolist()
    l2['target']=(T@[*l2['target'],1])[:3].tolist()
    l2['reference']+='; 25 October 2026: camera and target follow tested Tailor wrapper, preserving building pixel registration'
    l2['geometry_transform']=T.tolist()
    write(OUT/'staged/ae_render_camera_presets.json',profiles)
    write(OUT/'geometry-jobs.json',geometry_jobs);write(OUT/'variant-sources.json',source_plan)
    write(OUT/'materials.json',assembly.materials);write(OUT/'bundle-plan.json',bundle_report)
    print('Prepared',len(geometry_jobs),'geometry masters and eight saved assemblies')

def convert():
    reports=[];exe,_=helper(OUT/'cache')
    for job in json.loads((OUT/'geometry-jobs.json').read_text()):
        if len(sys.argv)>2 and job['name'] not in sys.argv[2].split(','):continue
        raw=json.loads(Path(job['native']).read_text());model=raw['models'][0]
        descriptor=parse(Path(job['native']).with_suffix('.geo'))
        rows=['// CSC L2 migration; exact native UV and influence preservation','skeleton']
        bones={b['name']:i for i,b in enumerate(model['bones'])}
        for i,b in enumerate(model['bones']):
            f=[*b['local']['position'],*b['local']['orientation'],*b['inverseWorld']]
            rows.append(f'{i} "{b["name"]}" {b["parent"]} '+' '.join(f'{x:.9f}' for x in f))
        rows.append(f'meshes:{len(raw["meshes"])}')
        for m in raw['meshes']:
            rows += [f'mesh:"{m["name"]}"','materials',*[f'"{g}"' for g in job['groups'][m['name']]],'vertices']
            for v in m['vertices']:
                active=[bones[m['boneBindings'][i]] for i,w in zip(v['boneIndices'],v['boneWeights']) if w]
                assert active
                indices=[bones[m['boneBindings'][i]] if w else active[0] for i,w in zip(v['boneIndices'],v['boneWeights'])]
                floats=[x for k in ['position','normal','tangent','binormal','uv','uv2','uv3'] for x in v[k]]
                rows.append(' '.join([*[f'{x:.9f}' for x in floats],*map(str,indices),*map(str,v['boneWeights'])]))
            rows+=['triangles',*[' '.join(map(str,t)) for t in m['triangles']]]
        rows.append('end');cn6=Path(job['native']).with_suffix('.cn6');cn6.write_text('\n'.join(rows)+'\n')
        converter=ROOT/'project/tools/cn6libs/CN6ToFGX.exe'
        result=subprocess.run([str(converter),str(cn6),str(cn6.with_suffix('.fgx')),'2'],cwd=converter.parent,capture_output=True,text=True)
        (OUT/(job['name']+'-conversion.log')).write_text(result.stdout+result.stderr)
        assert result.returncode==0,result.stdout+result.stderr
        dest=OUT/'native-after'/(job['name']+'.json');dest.parent.mkdir(exist_ok=True)
        subprocess.run([str(exe),str(exe.parent),str(cn6.with_suffix('.fgx')),str(dest)],cwd=exe.parent,check=True,capture_output=True)
        after=json.loads(dest.read_text());assert len(after['meshes'])==len(raw['meshes'])
        # Converter rewrites GEO: restore the source class, groups, names and
        # descriptor settings, updating counts only from actual FGX readback.
        geo=parse(cn6.with_suffix('.geo'))
        for m,b in zip(raw['meshes'],after['meshes']):
            assert m['name']==b['name'] and m['triangles']==b['triangles']
            active_bindings={m['boneBindings'][i] for v in m['vertices'] for i,w in zip(v['boneIndices'],v['boneWeights']) if w}
            assert active_bindings==set(b['boneBindings']),(m['name'],active_bindings,b['boneBindings'])
            assert len(m['vertices'])==len(b['vertices'])
            errors={k:float(np.max(abs(np.array([v[k] for v in m['vertices']])-np.array([v[k] for v in b['vertices']])))) for k in ['position','normal','tangent','binormal','uv','uv2','uv3']}
            assert max(errors.values())<.0001,errors
            g=next(g for g in geo.find('m_Meshes') if txt(g,'m_Name')==m['name'])
            dg=next(g for g in descriptor.find('m_Meshes') if txt(g,'m_Name')==m['name'])
            for key,val in [('m_nBoundBoneCount',len(b['boneBindings'])),('m_nVertexCount',len(b['vertices'])),('m_nPrimitiveCount',len(b['triangles']))]:dg.find(key).text=str(val)
            reports.append(dict(geometry=job['name'],mesh=m['name'],vertices=len(b['vertices']),errors=errors,bones=b['boneBindings']))
        save(descriptor,cn6.with_suffix('.geo'))
    if len(sys.argv)>2:
        previous=json.loads((OUT/'native-validation.json').read_text());changed=set(sys.argv[2].split(','))
        reports=[r for r in previous if r['geometry'] not in changed]+reports
    write(OUT/'native-validation.json',reports)
    print('Native round-trip passed:',len(reports),'meshes')

def textures():
    from publish_cafe_courtyard import rgba_dds
    from PIL import Image
    folder=OUT/'staged/Textures';folder.mkdir(exist_ok=True)
    copies=[]
    for variant,base in [('square','CSC_ALL_Stage_3_Cobbles_Sq'),('rectangular','CSC_ALL_Stage_3_Cobbles_02')]:
        for channel in ['B','H']:
            name=base+'_'+channel;source=OUT/'cobbles'/variant/'textures'/(name+'.png')
            result=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','-o',str(folder),'--ignore-srgb',*(['-srgb'] if channel=='B' else []),str(source)],capture_output=True,text=True)
            assert result.returncode==0,result.stdout+result.stderr
            expected=np.array(Image.open(source).convert('RGBA'));actual=rgba_dds(folder/(name+'.dds'))
            assert np.array_equal(actual,expected),(name,'DDS mismatch')
            original=MOD/'Textures'/(name+'.tex');descriptor=parse(original)
            descriptor.find('m_Width').text=str(expected.shape[1]);descriptor.find('m_Height').text=str(expected.shape[0])
            descriptor.find('m_SourceFilePath').set('text',str(ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants'/variant/'textures'/(name+'.png')))
            save(descriptor,folder/original.name)
            copies.append(dict(source=str(folder/(name+'.dds')),destination=str(ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants'/variant/'textures'/(name+'.dds'))))
    write(OUT/'source-dds-plan.json',copies)
    print('Four B/H DDS maps validated pixel-for-pixel')

def reviews():
    from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,prepare_geometry,PRESETS,read_xml
    from render_ae_asset import txt as rt
    alljobs=[];checks=[]
    for phase in ['before','after']:
        resolver=Resolver(MOD,DEFAULT_SDK)
        overlay=OUT/'before/Civ Supply Chains' if phase=='before' else OUT/'staged'
        for path in overlay.rglob('*'):
            if path.suffix in ['.ast','.fgx','.geo','.tex','.dds']:resolver.index[path.name.casefold()]={path}
        cameras=json.loads((OUT/('before/project/tools/blender/ae_render_camera_presets.json' if phase=='before' else 'staged/ae_render_camera_presets.json')).read_text())['classes']
        for name in [n for b in BUILDINGS for n in (b,b+'_2')]:
            path=overlay/'Assets'/(name+'.ast')
            for state in ['Worked','Unworked','Construction','Pillaged','Unbuilt']:
                assembly=Assembly(resolver,state);key=assembly.asset(path)
                checks.append(dict(phase=phase,asset=name,state=state,assets=len(assembly.assets),groups=sum(len(m['groups']) for a in assembly.assets.values() for m in a['models'])))
                if state!='Worked':continue
                out=OUT/'reviews'/phase/name;out.mkdir(parents=True,exist_ok=True)
                prepare_geometry(assembly,OUT/'cache',out)
                level='L2' if any(s in name for s in ['Tailor','Bakery']) and 'Fashion' not in name else 'L3'
                for material in assembly.materials.values():
                    base=material['textures'].get('BaseColor')
                    if base and base['id'].startswith('CSC_Atlas_B_') and not base['id'].endswith('_2'):
                        alternate=base['id']+'_2';tex=resolver.resolve(alternate,'.tex');f=rt(read_xml(tex),'m_DataFiles/Element/m_RelativePath',alternate+'.dds')
                        base['icon_override']=str(resolver.resolve(f,'.dds',tex))
                settings=dict(modes=['icon','sv'],presets=PRESETS,resolution=768,samples=24,camera_class=level,fixed_camera=cameras[level],seed=0)
                job=dict(root=key,assets=assembly.assets,geometries=assembly.geometries,materials=assembly.materials,warnings=assembly.warnings,settings=settings,output=str(out))
                write(out/'job.json',job);alljobs.append(str(out/'job.json'))
    write(OUT/'review-jobs.json',alljobs);write(OUT/'state-checks.json',checks)
    print('Resolved 80 state assemblies and prepared',len(alljobs),'paired icon/SV render jobs')

def render_reviews():
    from concurrent.futures import ThreadPoolExecutor
    selected=[]
    for path in map(Path,json.loads((OUT/'review-jobs.json').read_text())):
        job=json.loads(path.read_text());name=path.parent.name;phase=path.parent.parent.name
        if phase=='before' and name!='CSC_TAILORS_Tailor':continue
        job['settings']['modes']=['icon','sv'] if name=='CSC_TAILORS_Tailor' else ['sv']
        job['settings']['resolution']=640;job['settings']['samples']=16
        write(path,job);selected.append(path)
    def run(path):
        with (path.parent/'render.log').open('w') as log:
            result=subprocess.run(['C:/Program Files/Blender Foundation/Blender 5.1/blender.exe','--background','--factory-startup','--threads','4','--python-exit-code','1','--python',str(ROOT/'project/tools/blender/ae_asset_render_blender.py'),'--',str(path)],stdout=log,stderr=subprocess.STDOUT)
        assert result.returncode==0,str(path)
        print('REVIEW_RENDERED',path.parent.parent.name,path.parent.name,flush=True)
        return str(path.parent/'render-report.json')
    with ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(run,selected))
    write(OUT/'rendered-reviews.json',results)

def audit():
    from scipy.spatial import cKDTree
    transforms=json.loads((OUT/'transform.json').read_text())
    def matrix(a):
        x,y,z=a['rotation'];cx,sx,cy,sy,c,s=math.cos(x),math.sin(x),math.cos(y),math.sin(y),math.cos(-z),math.sin(-z)
        m=np.eye(4);m[:3,:3]=np.array([[c,-s,0],[s,c,0],[0,0,1]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])*a['scale'];m[:3,3]=np.array(a['position'])*10
        return m
    def cloud(job,extra):
        out={};raw={g:json.loads(Path(v['extracted']).read_text()) for g,v in job['geometries'].items()}
        def walk(key,M):
            asset=job['assets'][key]
            for model in asset['models']:
                if not model['geometry']:continue
                lookup={m['name']:m for m in raw[model['geometry']]['meshes']}
                for group in model['groups']:
                    m=lookup[group['mesh']];indices=sorted({i for t in m['triangles'][group['first']:group['first']+group['count']] for i in t[:3]})
                    points=(M@np.array([[*m['vertices'][i]['position'],1] for i in indices]).T).T[:,:3]
                    material=job['materials'][group['material']]
                    signature=json.dumps([material['id'],material['emission_enabled'],{c:v['id'] for c,v in material['textures'].items()}],sort_keys=True)
                    out.setdefault(signature,[]).append(points)
            for a in asset['attachments']:
                model=next(m for m in asset['models'] if m['id']==a['owner'])
                if model['geometry']:
                    bones=[b for m in raw[model['geometry']]['models'] for b in m['bones'] if b['name']==a['bone']];assert len(bones)==1
                    anchor=np.linalg.inv(np.array(bones[0]['inverseWorld']).reshape(4,4).T)
                else:anchor=np.eye(4)
                walk(a['asset'],M@anchor@matrix(a))
        walk(job['root'],extra)
        return {k:np.vstack(v) for k,v in out.items()}
    checks=[]
    for name in [n for b in BUILDINGS for n in (b,b+'_2')]:
        transform=np.array(transforms['wrapper'] if name.startswith('CSC_TAILORS_Tailor') else transforms['bakery_old_to_new'] if name.startswith('CSC_BAKERS_Bakery') else np.eye(4))
        a=cloud(json.loads((OUT/'reviews/before'/name/'job.json').read_text()),transform)
        b=cloud(json.loads((OUT/'reviews/after'/name/'job.json').read_text()),np.eye(4))
        assert a.keys()==b.keys(),(name,'effective material bindings changed')
        maximum=0
        for key in a:
            assert a[key].shape==b[key].shape,(name,key,a[key].shape,b[key].shape)
            error=max(cKDTree(a[key]).query(b[key])[0].max(),cKDTree(b[key]).query(a[key])[0].max())
            maximum=max(maximum,float(error));assert error<.001,(name,error)
        checks.append(dict(asset=name,world_geometry_error=maximum,material_and_emission_bindings_preserved=True))
    # The real installed add-on must be able to reproduce the saved source.
    sources=[];jobs={j['name']:j for j in json.loads((OUT/'geometry-jobs.json').read_text())}
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        job=jobs[row.get('shared_geometry',row['name'])]
        original=json.loads(Path(job['native']).read_text())
        text=(OUT/'source-export'/(row['name']+'.cn6')).read_text()
        parts=text.split('mesh:"')[1:]
        assert len(parts)==len(original['meshes'])
        maximum=0
        for part in parts:
            name,body=part.split('"',1);vertices=body.split('vertices\n',1)[1].split('triangles\n',1)[0]
            a=np.array([[float(x) for x in line.split()[:18]] for line in vertices.strip().splitlines()])
            mesh=next(m for m in original['meshes'] if m['name']==name)
            b=np.array([[x for k in ['position','normal','tangent','binormal','uv','uv2','uv3'] for x in v[k]] for v in mesh['vertices']])
            columns=list(range(18))
            assert len(a)==len(b),(row['name'],name,len(a),len(b))
            error=max(cKDTree(a[:,columns]).query(b[:,columns])[0].max(),cKDTree(b[:,columns]).query(a[:,columns])[0].max())
            maximum=max(maximum,float(error));assert error<.0002,(row['name'],name,error)
        sources.append(dict(source=row['name'],exported_position_normal_uv_error=maximum))
    write(OUT/'assembly-parity.json',checks);write(OUT/'saved-source-export-parity.json',sources)
    print('Verified eight complete assemblies and',len(sources),'saved-source CN6 exports')

def context_reviews():
    from render_ae_asset import Resolver,Assembly,DEFAULT_SDK,prepare_geometry,PRESETS
    resolver=Resolver(MOD,DEFAULT_SDK)
    for p in (OUT/'staged').rglob('*'):
        if p.suffix in ['.ast','.geo','.fgx','.tex','.dds']:resolver.index[p.name.casefold()]={p}
    road=parse(MOD/'Assets/CSC_TAILORS_Classical_Base_03.ast')
    for m in list(road.find(MODELS)):
        if txt(m,'m_GeoName')!='CSC_ALL_Classical_Base_03_Road_Decals':road.find(MODELS).remove(m)
    road.find(POINTS).clear();road.find('m_Name').set('text','CSC_REVIEW_Road03')
    path=OUT/'context/road.ast';save(road,path)
    for name in ['CSC_TAILORS_Tailor','CSC_BAKERS_Bakery']:
        assembly=Assembly(resolver);assembly.is_decal=lambda *args:False
        key=assembly.asset(OUT/'staged/Assets'/(name+'.ast'));roadkey=assembly.asset(path)
        assembly.assets[key]['models'].extend(assembly.assets[roadkey]['models'])
        out=OUT/'context'/name;out.mkdir(parents=True,exist_ok=True);prepare_geometry(assembly,OUT/'cache',out)
        settings=dict(modes=['sv'],presets=PRESETS,resolution=900,samples=32,camera_class='L2',fixed_camera=json.loads((OUT/'staged/ae_render_camera_presets.json').read_text())['classes']['L2'])
        write(out/'job.json',dict(root=key,assets=assembly.assets,geometries=assembly.geometries,materials=assembly.materials,warnings=assembly.warnings,settings=settings,output=str(out)))
    print('Road03 context jobs prepared')

def install():
    assert not (OUT/'install-report.json').exists(),'Migration already installed'
    assert len(json.loads((OUT/'assembly-parity.json').read_text()))==8
    assert len(json.loads((OUT/'saved-source-export-parity.json').read_text()))==16
    assert len(json.loads((OUT/'final-source-validation.json').read_text()))==16
    assert len(json.loads((OUT/'native-validation.json').read_text()))==55
    baseline=json.loads((OUT/'baseline.json').read_text())
    payload=[]
    for folder in ['Assets','Geometries','Textures']:
        for p in (OUT/'staged'/folder).iterdir():
            if p.suffix in ['.ast','.geo','.fgx','.dds','.tex']:payload.append((p,MOD/folder/p.name))
    for source,dest in payload:
        if str(dest) in baseline:assert hashlib.sha256(dest.read_bytes()).hexdigest()==baseline[str(dest)],str(dest)+' changed during migration'
        elif source.parent.name!='Textures':assert not dest.exists(),str(dest)+' unexpectedly exists'
    # Back up the exact current source assets and dependent descriptors before
    # publishing; source inventory hashes protect the explicitly named originals.
    inventory={r['source']:r['sha256'] for r in json.loads((OUT/'source-inventory.json').read_text())}
    sources=[]
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        src,dst=Path(row['source']),Path(row['destination'])
        if str(dst) in inventory:assert hashlib.sha256(dst.read_bytes()).hexdigest()==inventory[str(dst)],dst
        elif dst.exists():raise AssertionError('New revision destination already exists: '+str(dst))
        sources.append((src,dst))
        sources.extend((p,dst.parent/'textures'/p.name) for p in (src.parent/'textures').glob('*.png'))
        cn6=OUT/'source-export'/(row['name']+'.cn6')
        sources.append((cn6,dst.with_suffix('.cn6')))
    for row in json.loads((OUT/'cobble-plan.json').read_text())['files']+json.loads((OUT/'source-dds-plan.json').read_text()):sources.append((Path(row['source']),Path(row['destination'])))
    for variant in ['square','rectangular']:
        folder=ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants'/variant/'exports'
        sources.extend((OUT/'staged/Geometries'/('CSC_ALL_Stage_3_Cobble_Decals'+e),folder/('CSC_ALL_Stage_3_Cobble_Decals'+e)) for e in ['.cn6','.geo','.fgx'])
    presets=ROOT/'project/tools/blender/ae_render_camera_presets.json'
    assert hashlib.sha256(presets.read_bytes()).hexdigest()==baseline[str(presets)]
    payload.append((OUT/'staged/ae_render_camera_presets.json',presets))
    artdef=MOD/'ArtDefs/CSC_Landmarks.artdef';artdef_raw=artdef.read_bytes()
    assert artdef_raw.count(b'<m_EntryName text="CSC_TEST_Tailor_Wrapper"/>')==1
    artdef_new=artdef_raw.replace(b'<m_EntryName text="CSC_TEST_Tailor_Wrapper"/>',b'<m_EntryName text="CSC_TAILORS_Tailor"/>')
    project=MOD/'Civ Supply Chains.civ6proj';project_raw=project.read_bytes()
    project_new=project_raw
    newitems=[]
    for ext in ['fgx','geo']:
        item='Geometries\\CSC_BAKERS_Cafe.'+ext
        if ('Include="'+item+'"').encode() not in project_new:newitems.append(f'    <Content Include="{item}">\r\n      <SubType>Content</SubType>\r\n    </Content>')
    if newitems:
        block=('  <ItemGroup>\r\n'+'\r\n'.join(newitems)+'\r\n  </ItemGroup>\r\n').encode()
        assert project_new.count(b'</Project>')==1;project_new=project_new.replace(b'</Project>',block+b'</Project>')
    # Update AE's dependency inventory from only the changed files. Existing
    # records, unrelated placements and the canonical prop atlas stay intact.
    cache_path=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
    cache_raw=cache_path.read_bytes();cache=json.loads(cache_raw.decode('utf-8-sig'))
    index={(Path(e['Filename']).suffix.lower(),Path(e['Filename']).stem.casefold()):e['Filename'].replace('\\','/') for e in cache['Files']}
    for folder in ['Assets','Geometries','Materials','Textures','Animations']:
        for p in (MOD/folder).glob('*'):
            if p.is_file():index[(p.suffix.lower(),p.stem.casefold())]=p.relative_to(ROOT).as_posix()
    for src,dst in payload:
        if dst.is_relative_to(MOD):index[(dst.suffix.lower(),dst.stem.casefold())]=dst.relative_to(ROOT).as_posix()
    records={e['Filename'].replace('\\','/'):e for e in cache['Files']};now=int(time.time()*10000000)+116444736000000000
    dependencies={}
    for src,dst in payload:
        if not dst.is_relative_to(MOD):continue
        key=dst.relative_to(ROOT).as_posix()
        if key not in records:
            example=records['Civ Supply Chains/Geometries/CSC_Level_3'+src.suffix]
            record=copy.deepcopy(example);record['Filename']=key;cache['Files'].append(record);records[key]=record
        record=records[key];record.update(Timestamp=now,Filesize=src.stat().st_size)
        if src.suffix in ['.fgx','.dds']:continue
        root=parse(src)
        refs={str(Path(key).parent/e.get('text')).replace('\\','/') for e in root.findall('.//m_DataFiles/Element/m_RelativePath')}
        for tag,ext in [('m_GeoName','.geo'),('m_AnimationName','.anm'),('m_EntryName','.ast'),('m_dsgName','.dsg')]:
            for e in root.findall('.//'+tag):
                if e.get('text'):refs.add(index[(ext,Path(e.get('text').replace('\\','/')).name.casefold())])
        for e in root.findall('.//Element'):
            obj,kind=e.find('m_ObjectName'),e.find('m_eObjectType')
            if obj is not None and kind is not None and obj.get('text'):
                ext={'MATERIAL':'.mtl','TEXTURE':'.tex','GEOMETRY':'.geo'}.get(kind.text)
                if ext:refs.add(index[(ext,Path(obj.get('text').replace('\\','/')).name.casefold())])
        cache['Dependencies'][key]=dependencies[key]=sorted(refs)
        if src.suffix=='.geo':
            record['Stats']={'Vertices':sum(int(m.findtext('m_nVertexCount')) for m in root.findall('m_Meshes/Element')),'Faces':sum(int(m.findtext('m_nPrimitiveCount')) for m in root.findall('m_Meshes/Element')),'Bones':len(root.findall('m_Bones/Element')),'Bound Bones':sum(int(m.findtext('m_nBoundBoneCount')) for m in root.findall('m_Meshes/Element'))}
    cache['Timestamp']=now
    assert artdef.read_bytes()==artdef_raw and project.read_bytes()==project_raw and cache_path.read_bytes()==cache_raw
    records_out=[]
    def publish(dst,data):
        if dst.exists():
            label='workspace' if dst.is_relative_to(ROOT) else 'sources' if dst.is_relative_to(ART) else 'AssetCloud'
            rel=dst.relative_to(ROOT) if label=='workspace' else dst.relative_to(ART) if label=='sources' else Path(dst.name)
            backup=OUT/'install-backup'/label/rel;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,backup)
        else:backup=None
        dst.parent.mkdir(parents=True,exist_ok=True);temporary=dst.with_name(dst.name+'.l2-migration-tmp');temporary.write_bytes(data);os.replace(temporary,dst)
        records_out.append(dict(destination=str(dst),sha256=hashlib.sha256(data).hexdigest(),backup=str(backup) if backup else None))
    # Deduplicate identical supporting textures shared by the variant blends.
    unique={}
    for src,dst in [*payload,*sources]:
        if dst in unique:assert unique[dst].read_bytes()==src.read_bytes(),dst
        unique[dst]=src
    for dst,src in unique.items():publish(dst,src.read_bytes())
    publish(artdef,artdef_new);publish(project,project_new)
    # Avoid replacing a live AE cache that changed during the file copy.
    assert cache_path.read_bytes()==cache_raw,'AE dependency cache changed during publication; update it separately'
    publish(cache_path,json.dumps(cache,separators=(',',':')).encode())
    for r in records_out:assert hashlib.sha256(Path(r['destination']).read_bytes()).hexdigest()==r['sha256'],r['destination']
    write(OUT/'install-report.json',dict(files=records_out,dependencies=dependencies,live_wrapper_reference_removed=True,cook_tested=False,in_game_tested=False))
    print('Installed',len(records_out),'files with recoverable backups; AE dependencies updated')

def source_links():
    """Point all paving TEX files at the requested authoritative variant folders."""
    report=[]
    for variant,base in [('square','CSC_ALL_Stage_3_Cobbles_Sq'),('rectangular','CSC_ALL_Stage_3_Cobbles_02')]:
        for channel in ['B','H']:
            name=base+'_'+channel;path=MOD/'Textures'/(name+'.tex');root=parse(path)
            expected=ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants'/variant/'textures'/(name+'.png')
            assert expected.exists()
            backup=OUT/'source-links-backup'/path.name;backup.parent.mkdir(exist_ok=True)
            if not backup.exists():shutil.copy2(path,backup)
            root.find('m_SourceFilePath').set('text',str(expected));save(root,path)
            save(root,OUT/'staged/Textures'/path.name)
            report.append(dict(texture=name,source=str(expected)))
    write(OUT/'texture-source-links.json',report)
    print('Four texture descriptors linked to the updated variant sources')

def verify_install(texture_reference=None):
    from publish_cafe_courtyard import rgba_dds
    texture_reference=Path(texture_reference) if texture_reference else OUT/'staged/Textures'
    report=json.loads((OUT/'install-report.json').read_text());changes=[]
    for row in report['files']:
        path=Path(row['destination']);actual=hashlib.sha256(path.read_bytes()).hexdigest()
        if actual==row['sha256']:continue
        if path.suffix=='.dds':
            stage=texture_reference/path.name
            assert np.array_equal(rgba_dds(path),rgba_dds(stage)),path
            changes.append(dict(file=str(path),reason='AE regenerated encoding/mips; top-level RGBA exactly matches'))
        elif path.suffix=='.tex':
            a=parse(path);b=parse(texture_reference/path.name)
            for r in [a,b]:
                for tag in ['m_ExportedTime','m_ImportedTime']:
                    if r.find(tag) is not None:r.find(tag).text='timestamp'
            assert [(e.tag,(e.text or '').strip(),dict(e.attrib)) for e in a.iter()]==[(e.tag,(e.text or '').strip(),dict(e.attrib)) for e in b.iter()],path
            changes.append(dict(file=str(path),reason='Canonical source link and/or AE export timestamp updated'))
        elif path.name=='mod-Civ Supply Chains-asset-deps.json':
            cache=json.loads(path.read_text(encoding='utf-8-sig'))
            for key,value in report['dependencies'].items():assert set(value)<=set(cache['Dependencies'][key]),key
            files={r['Filename'].replace('\\','/'):r for r in cache['Files']}
            assert 'Civ Supply Chains/Geometries/CSC_BAKERS_Cafe.geo' in files
            changes.append(dict(file=str(path),reason='AE refreshed timestamps, FX and texture-source dependencies; expected dependencies retained'))
        else:raise AssertionError('Unexpected post-install change: '+str(path))
    write(OUT/'installed-verification.json',dict(installed_files=len(report['files']),allowed_watcher_changes=changes,source_count=16,native_meshes=55,game_tested=False))
    print('Installed files verified; allowed AE watcher updates:',len(changes))

def normalize_model_owners(root):
    for model in root.findall(MODELS+'/Element'):
        name=txt(model,'m_GeoName')
        if name not in ['CSC_BAKERS_Cafe','CSC_BAKERS_Bakery_PIL_Decals']:continue
        old=txt(model,'m_Name');model.find('m_Name').set('text',name)
        for point in root.findall(POINTS+'/Element'):
            if txt(point,'m_ModelInstanceName')==old:
                point.find('m_ModelInstanceName').set('text',name)
                if txt(point,'m_BoneName')==old:point.find('m_BoneName').set('text',name)

def prepare_export_identities():
    for name in ['CSC_BAKERS_Cafe','CSC_BAKERS_Bakery_PIL_Decals']:
        p=OUT/'staged/Geometries'/(name+'.json');raw=json.loads(p.read_text());old=raw['models'][0]['name']
        raw['models'][0]['name']=name;raw['models'][0]['bones'][0]['name']=name;write(p,raw)
        g=OUT/'staged/Geometries'/(name+'.geo');geo=parse(g);geo.find('m_ModelName').set('text',name)
        for b in geo.findall('m_Bones/Element'):
            if b.get('text')==old:b.set('text',name)
        save(geo,g)
    for name in ['CSC_BAKERS_Cafe','CSC_BAKERS_Cafe_2','CSC_BAKERS_Bakery','CSC_BAKERS_Bakery_2']:
        path=OUT/'staged/Assets'/(name+'.ast');root=parse(path);normalize_model_owners(root);save(root,path)
    print('Prepared safe per-file export identities')

def publish_export_identities():
    report=json.loads((OUT/'install-report.json').read_text());records={r['destination']:r for r in report['files']}
    pairs=[]
    for name in ['CSC_BAKERS_Cafe','CSC_BAKERS_Bakery_PIL_Decals']:
        for e in ['.fgx','.geo']:pairs.append((OUT/'staged/Geometries'/(name+e),MOD/'Geometries'/(name+e)))
    for name in ['CSC_BAKERS_Cafe','CSC_BAKERS_Cafe_2','CSC_BAKERS_Bakery','CSC_BAKERS_Bakery_2']:pairs.append((OUT/'staged/Assets'/(name+'.ast'),MOD/'Assets'/(name+'.ast')))
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        if row['name'] not in ['CSC_BAKERS_Cafe','CSC_BAKERS_Cafe_2','CSC_BAKERS_Bakery_PIL_Decals']:continue
        pairs.append((Path(row['source']),Path(row['destination'])))
        pairs.append((OUT/'source-export'/(row['name']+'.cn6'),Path(row['destination']).with_suffix('.cn6')))
    for src,dst in pairs:assert hashlib.sha256(dst.read_bytes()).hexdigest()==records[str(dst)]['sha256'],dst
    for i,(src,dst) in enumerate(pairs):
        backup=OUT/'export-identity-backup'/str(i)/dst.name;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(dst,backup)
        shutil.copy2(src,dst);records[str(dst)]['sha256']=hashlib.sha256(dst.read_bytes()).hexdigest()
    report['export_identity_correction']=[str(d) for s,d in pairs];write(OUT/'install-report.json',report)
    print('Published per-file exporter identities; shared L3 cannot be overwritten by the Cafe master')

if __name__=='__main__':
    globals()[sys.argv[1]]()
