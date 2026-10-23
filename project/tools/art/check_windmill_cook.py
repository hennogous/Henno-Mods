"""Cook only the windmill assemblies from an isolated pantry; no mod build/deploy."""
import sys,json,shutil,subprocess,os
from pathlib import Path
import xml.etree.ElementTree as E
from windmill_tower_integrate import ROOT,MOD,NAME,read_xml,save,field,Resolver,Assembly,DEFAULT_SDK
OUT=Path(sys.argv[1]);mode=sys.argv[2]
COOKER=next(Path('C:/Program Files (x86)/Steam/steamapps/common').glob('*Civilization VI SDK/AssetModTools/Cooker'))
pantry=OUT/'cook-pantry';pantry.mkdir(exist_ok=True)
if mode=='prepare':
    resolver=Resolver(MOD,DEFAULT_SDK)
    for p in (OUT/'staged').rglob('*'):
        if p.suffix.lower() in ['.ast','.geo','.fgx','.dds','.tex','.mtl','.anm']:resolver.index[p.name.casefold()]={p}
    assembly=Assembly(resolver)
    for name in [NAME,'CSC_BAKERS_Wind_Mill','CSC_BAKERS_Wind_Mill_2']:
        assembly.asset(resolver.resolve(name,'.ast'))
    files={Path(p) for p in resolver.inputs}
    # The visual renderer selects Worked. The native cook also needs every other
    # state's geometry/materials and each wrapper's binary payload.
    pending=list(files);seen=set()
    while pending:
        p=pending.pop()
        if p in seen or p.suffix not in ['.ast','.geo','.mtl','.tex','.anm']:continue
        seen.add(p);root=read_xml(p);extra=[]
        for node in root.findall('.//m_GeoName'):
            if node.get('text'):extra.append(resolver.resolve(node.get('text'),'.geo',p))
        for node in root.findall('.//Element'):
            kind=node.find('m_eObjectType');name=node.find('m_ObjectName')
            kind_value=kind.get('text',kind.text) if kind is not None else None
            if kind is not None and name is not None and name.get('text') and kind_value in ['TEXTURE','MATERIAL']:
                extra.append(resolver.resolve(name.get('text'),'.tex' if kind_value=='TEXTURE' else '.mtl',p))
        for node in root.findall('.//m_DataFiles/Element/m_RelativePath'):
            payload=p.parent/node.get('text')
            if payload.exists():extra.append(payload)
            else:extra.append(resolver.resolve(node.get('text'),Path(node.get('text')).suffix,p))
        for f in extra:
            if f not in files:files.add(f);pending.append(f)
    for p in list(files):
        if p.suffix=='.ast':
            root=read_xml(p)
            for n in root.findall('.//m_AnimationName'):
                if n.get('text'):
                    ap=OUT/'staged/Animations'/(n.get('text')+'.anm')
                    if not ap.exists():ap=MOD/'Animations'/(n.get('text')+'.anm')
                    if not ap.exists():ap=resolver.resolve(n.get('text'),'.anm',p)
                    files.add(ap)
                    for f in read_xml(ap).findall('.//m_DataFiles/Element/m_RelativePath'):files.add(ap.parent/f.get('text'))
    # Copy local dependencies. Base-game dependencies are resolved from read-only SDK pantries.
    folder={'.ast':'Assets','.geo':'Geometries','.mtl':'Materials','.tex':'Textures','.dds':'Textures','.xlp':'XLPs','.anm':'Animations'}
    for p in files:
        if not p.is_relative_to(MOD) and not p.is_relative_to(OUT):continue
        sub=folder.get(p.suffix,p.parent.name);dest=pantry/sub/p.name;dest.parent.mkdir(exist_ok=True);shutil.copy2(p,dest)
    xlp=read_xml(MOD/'XLPs/CSC_Tilebases.xlp');xlp.find('m_Entries').clear();xlp.find('m_PackageName').set('text','WindmillRepairCheck')
    for name in [NAME,'CSC_BAKERS_Wind_Mill','CSC_BAKERS_Wind_Mill_2']:
        row=E.SubElement(xlp.find('m_Entries'),'Element');field(row,'m_EntryID',name);field(row,'m_ObjectName',name)
    save(xlp,OUT/'WindmillRepairCheck.xlp')
    (OUT/'cook-inputs.json').write_text(json.dumps(sorted(str(p) for p in files),indent=2))
    print('Isolated pantry prepared',len(files))
else:
    geo=pantry/'Geometries'/(NAME+'.geo')
    native=OUT/('before-group-cleanup' if mode.startswith('groups-control') else 'staged/Geometries')/(NAME+'.fgx')
    shutil.copy2(native,pantry/'Geometries'/native.name)
    correct=(OUT/'staged/Geometries'/(NAME+'.geo')).read_bytes()
    geo.write_bytes(correct.replace(b'AssetObjects..GeometryInstance',b'AssetObjects.GeometryInstance') if mode=='before' else correct)
    target=OUT/('cook-'+mode);target.mkdir(exist_ok=True)
    cmd=[str(COOKER/'Civ6AssetCooker_FinalRelease.exe'),'--absolute_paths','--no_mt','--mode','XLP','--platform','Windows',
         '--shaders',str(COOKER),'--pantry',str(pantry)]
    sdk=next(Path('C:/Program Files (x86)/Steam/steamapps/common').glob('*Civilization VI SDK Assets'))
    for p in [sdk/'Civ6/pantry',sdk/'Civ6/DLC/Shared/pantry',sdk/'Civ6/DLC/Expansion1/pantry',sdk/'Civ6/DLC/Expansion2/pantry']:
        cmd+=['--pantry',str(p)]
    cmd+=['--stewpot',str(target/'BLPs'),'--config',str(COOKER/'Civ6.cfg'),'--log_path',str(target),str(OUT/'WindmillRepairCheck.xlp')]
    (target/'command.json').write_text(json.dumps(cmd,indent=2))
    if mode.startswith('capture'):
        procdump=Path.home()/'Desktop/Codex/AE_Crash_Diagnostic_20261012/tools/procdump64.exe'
        cmd=[str(procdump),'-accepteula','-ma','-e','-g','-x',str(target),*cmd]
    with (target/'stdout.log').open('w') as f:
        result=subprocess.run(cmd,cwd=target,stdout=f,stderr=subprocess.STDOUT,timeout=180,env=dict(os.environ,_NO_DEBUG_HEAP='1'))
    (target/'result.json').write_text(json.dumps(dict(exit_code=result.returncode,blps=[str(p) for p in target.rglob('*.blp')]),indent=2))
    print('Cook',mode,'exit',result.returncode);print((target/'stdout.log').read_text(errors='replace').replace('\x00','')[-3000:])
