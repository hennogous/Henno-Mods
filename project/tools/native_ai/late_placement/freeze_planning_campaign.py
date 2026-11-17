"""Freeze an observational campaign without sweeping unrelated workspace edits in.

The accepted previous full-run gameplay/art package supplies content. Only the
main CSC AI modules, passive UI fact bridge and named AI coverage SQL are overlaid.
Workshop content stays installed/read-only and is separately pinned by the
controller. This script does not launch a game or install a mod.
"""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET


def register_material_transactions(package):
    """Add only the reviewed gameplay repair to the accepted runtime manifest.

    The source ModBuddy manifest may contain unrelated work in progress. Keep
    the accepted package's actions and criteria, particularly the CE-gated AI
    connectors. Material payouts are ordinary gameplay and must load without
    that criterion. The actual mod loader needs both action and Files entries.
    """
    manifests=list(package.glob('*.modinfo'))
    if len(manifests)!=1:
        raise ValueError('Expected one accepted CSC runtime manifest')
    path=manifests[0]
    tree=ET.parse(path);root=tree.getroot()
    actions=root.find('InGameActions');files=root.find('Files')
    if actions is None or files is None:
        raise ValueError('Accepted package has no gameplay actions or file list')
    # Historical packages can predate the shared schema. Input-host DDL now
    # lives there, so the isolated host repair must register it too. Current
    # packages already load it at95 and need no additional action.
    schema='Data/CSC_Q_ALL_Schema.sql'
    if not any(file.text==schema for action in actions for file in action.findall('File')):
        action=ET.SubElement(actions,'UpdateDatabase',id='CSC_MaterialHostSchema')
        ET.SubElement(ET.SubElement(action,'Properties'),'LoadOrder').text='94'
        ET.SubElement(action,'File').text=schema
    if not any(file.text==schema for file in files):
        ET.SubElement(files,'File').text=schema
    existing=[a for a in actions if a.get('id')=='CSC_MaterialTransactions']
    for action in existing:
        actions.remove(action)
    action=ET.SubElement(actions,'UpdateDatabase',id='CSC_MaterialTransactions')
    ET.SubElement(ET.SubElement(action,'Properties'),'LoadOrder').text='800010'
    relative='Data/CSC_Q_ALL_MaterialHosts.sql'
    ET.SubElement(action,'File').text=relative
    if not any(f.text==relative for f in files):
        ET.SubElement(files,'File').text=relative
    tree.write(path,encoding='utf-8',xml_declaration=True)
    return path


def register_ai_modules(package):
    """Import reviewed AI modules added since the accepted content package.

    Keep its gameplay/actions intact. This only registers the Lua files already
    overlaid by freeze(), so new shared policy modules ship inside main CSC.
    """
    path, = package.glob('*.modinfo')
    tree=ET.parse(path);root=tree.getroot()
    actions=root.find('InGameActions');files=root.find('Files')
    action=next((a for a in actions if a.get('id')=='CSC_AI_PlacementModules'),None)
    if action is None:
        action=ET.SubElement(actions,'ImportFiles',id='CSC_AI_PlacementModules')
        ET.SubElement(ET.SubElement(action,'Properties'),'LoadOrder').text='490'
    for module in sorted((package/'Lua_UI/AI').glob('*.lua')):
        relative=module.relative_to(package).as_posix()
        if not any(f.text==relative for f in action.findall('File')):
            ET.SubElement(action,'File').text=relative
        if not any(f.text==relative for f in files):ET.SubElement(files,'File').text=relative
    tree.write(path,encoding='utf-8',xml_declaration=True)


def register_economy_contract(package, specs, read_content):
    """Register reviewed economic migrations from committed gameplay actions.

    Keep accepted art/UI and existing action criteria. Schema/Quarter headers
    and processors use their real source action order; importing AI Lua alone
    would leave its new shared gameplay tables or route modules unavailable.
    read_content supplies committed bytes, avoiding unrelated workspace edits.
    """
    # Select economic files rather than former action IDs: actions can now
    # contain several Quarters or shared imports. Keep art/Pedia/UI files out
    # of this deliberately scoped historical-package upgrade.
    selected={'Data/CSC_Q_ALL_Schema.sql','Data/CSC_Q_ALL_Common.sql',
              'Data/CSC_Q_ALL_TransactionProcessor.sql','Data/CSC_Q_ALL_TradeRouteReader.sql',
              'Lua_UI/TradeRoutes/CSC_TradeRouteCore.lua','Lua_UI/TradeRoutes/CSC_TradeRouteFacts.lua'}
    selected|={f'Data/CSC_Q_{q}{suffix}.sql'for q in ('BAKERS','TAILORS')
               for suffix in ('','_GOLD','_MC_MODE','_MC_MODE_GOLD')}
    retired={'Data/'+name for name in ('CSC_Q_ALL.sql','CSC_BuildingTransactionSchema.sql',
        'CSC_TradeRouteSchema.sql','CSC_MaterialTransactionProcessor.sql',
        'CSC_FixedBuildingTransactionProcessor.sql','CSC_BuildingTransactionProcessor.sql',
        'CSC_TradeRouteProcessor.sql')}
    retired|={f'Data/CSC_Q_{q}_TRANSACTIONS{suffix}.sql'for q in ('BAKERS','TAILORS')for suffix in ('','_GOLD')}
    path,=package.glob('*.modinfo')
    tree=ET.parse(path);root=tree.getroot();actions=root.find('InGameActions');files=root.find('Files')
    copied={};found=set();previous_criteria={}
    for action in list(actions):
        for file in list(action.findall('File')):
            if file.text in selected:
                previous_criteria[file.text]=tuple(c.text for c in action.findall('Criteria'))
            if file.text in selected|retired:action.remove(file)
        if not action.findall('File')and action.tag in ('UpdateDatabase','ImportFiles'):
            actions.remove(action)
    for file in list(files):
        if file.text in retired:files.remove(file)
    def copy(relative):
        data=read_content(relative);target=package/relative
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        copied[relative]=hashlib.sha256(data).hexdigest()
        if not any(f.text==relative for f in files):ET.SubElement(files,'File').text=relative
    for spec in specs:
        relevant=[f for f in spec.get('files',[])if f in selected]
        if not relevant:continue
        groups={}
        for relative in relevant:
            criteria=previous_criteria.get(relative,tuple(spec.get('criteria',[])))
            groups.setdefault(criteria,[]).append(relative)
        for index,(criteria,paths)in enumerate(groups.items()):
            identity=spec['id']if len(groups)==1 else spec['id']+'_'+str(index+1)
            # An accepted consolidated action can retain unrelated files after
            # the selected ones were removed. Preserve it and avoid a duplicate
            # action ID when adding this scoped economic portion back.
            if any(a.get('id')==identity for a in actions):identity+='_Economic'
            if any(a.get('id')==identity for a in actions):raise ValueError('Ambiguous economic action '+identity)
            action=ET.SubElement(actions,spec['type'],id=identity)
            props=ET.SubElement(action,'Properties')
            for name,value in spec.get('properties',{}).items():ET.SubElement(props,name).text=str(value)
            for criterion in criteria:ET.SubElement(action,'Criteria').text=criterion
            for relative in paths:
                found.add(relative);copy(relative);ET.SubElement(action,'File').text=relative
    if found!=selected:raise ValueError('Missing reviewed economic files: '+str(selected-found))
    for relative in ('Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua',
                     'Lua_UI/TradeRoutes/CSC_TradeRouteInteractions.lua'):
        copy(relative)
    tree.write(path,encoding='utf-8',xml_declaration=True)
    return copied


def freeze(base, source, output, *, economy_registry=False, ce_dll=None):
    base, source, output = (Path(p).resolve() for p in (base, source, output))
    if output.exists() or not all((base / name).is_dir() for name in ('CE', 'CSC')):
        raise ValueError('Require accepted CE/CSC base and a new output directory')
    output.mkdir(parents=True)
    for name in ('CE', 'CSC'):
        shutil.copytree(base / name, output / name)
    overlays = list((source / 'Lua_UI/AI').glob('*.lua'))
    overlays.append(source / 'Lua_UI/Adjacencies/CSC_AdjacencyUI.lua')
    overlays.extend(source / 'Data' / name for name in
                    ('CSC_Q_ALL_AI_Connectors.sql','CSC_Q_ALL_MaterialHosts.sql','CSC_Q_ALL_Schema.sql'))
    hashes = {}
    for path in overlays:
        relative = path.relative_to(source)
        (output / 'CSC' / relative).parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path, output / 'CSC' / relative)
        hashes[relative.as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    runtime_manifest=register_material_transactions(output/'CSC')
    register_ai_modules(output/'CSC')
    contract={}
    if economy_registry:
        repo=source.parent
        def committed(relative):
            return subprocess.check_output(['git','-C',str(repo),'show','HEAD:Civ Supply Chains/'+relative])
        action_data=json.loads(subprocess.check_output(['git','-C',str(repo),'show',
            'HEAD:project/modbuddy/CivSupplyChains.actions.json']))
        contract=register_economy_contract(output/'CSC',action_data['blocks']['inGameActions'],committed)
    ce_overlay=None
    if ce_dll:
        proxy,=(output/'CE/Binaries/Win64').glob('GameCore_XP2_CE*.dll')
        shutil.copyfile(ce_dll,proxy);ce_overlay=hashlib.sha256(proxy.read_bytes()).hexdigest()
    (output / 'freeze.json').write_text(json.dumps(dict(
        base=str(base), source=str(source), overlays=hashes,
        runtime_manifest_sha256=hashlib.sha256(runtime_manifest.read_bytes()).hexdigest(),
        committed_economic_contract=contract,ce_overlay_sha256=ce_overlay,
        unrelated_workspace_content_included=False), indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('base', 'source', 'output'):
        parser.add_argument('--'+name, type=Path, required=True)
    parser.add_argument('--economy-registry',action='store_true',help='Include the reviewed committed shared-economy action/files migration')
    parser.add_argument('--ce-dll',type=Path,help='Copy an explicit locally built CE API candidate into the frozen CE package')
    args = parser.parse_args()
    freeze(args.base,args.source,args.output,economy_registry=args.economy_registry,ce_dll=args.ce_dll)
