"""Deploy only the material-map delta, using Firaxis' manifest generation task.

Canonical ModBuddy JSON/project are already wired. Preserve the installed build's
other actions/assets so unrelated unfinished source changes stay out of this test.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'project/tools/modbuddy'))
from civ6proj_actions import action_from_json, json_to_node
FILES=['Lua_UI/MapGeneration/CSC_MaterialMap.lua','Lua_UI/MapGeneration/CSC_MaterialMapCore.lua','Lua_UI/MapGeneration/CSC_MaterialMapDefinitions.lua','Settings/Settings.xml','Settings/Settings_Text.xml','ModSupport/ModSupport_TAR_MAP.sql']
ACTION_IDS={'CSC_MaterialMapModules','CSC_MaterialMap','CSC_MaterialMap_TAR'}
REMOVE_ACTION_IDS=set()
REMOVE_FILES=set()


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--installed',type=Path,required=True);a=p.parse_args()
    a.output.mkdir(parents=True,exist_ok=True);backup=a.output/'installed-backup';backup.mkdir(exist_ok=True)
    manifest=a.installed/'Civ Supply Chains.modinfo';old=ET.parse(manifest).getroot()
    inventory={str(f.relative_to(a.installed)).replace('\\','/'):sha(f) for f in a.installed.rglob('*') if f.is_file() and f.suffix in ('.lua','.xml','.sql','.modinfo')}
    lock=a.output/'original-installed-hashes.json'
    if not lock.exists():lock.write_text(json.dumps(inventory,indent=2))
    for name in FILES+sorted(REMOVE_FILES)+['Civ Supply Chains.modinfo']:
        dest=backup/name
        if (a.installed/name).exists() and not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(a.installed/name,dest)
    mirror=json.loads((ROOT/'project/modbuddy/CivSupplyChains.actions.json').read_text())
    ingame=copy.deepcopy(old.find('InGameActions'))
    for existing in list(ingame):
        if existing.get('id') in REMOVE_ACTION_IDS:ingame.remove(existing)
    actions=[x for x in mirror['blocks']['inGameActions'] if x['id'] in ACTION_IDS];assert len(actions)==len(ACTION_IDS)
    for action in actions:
        for existing in list(ingame):
            if existing.get('id')==action['id']:ingame.remove(existing)
        ingame.append(action_from_json(action))
    for name in FILES:
        dest=a.installed/name;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists() and sha(dest)==sha(ROOT/'Civ Supply Chains'/name):continue
        try:shutil.copy2(ROOT/'Civ Supply Chains'/name,dest)
        except OSError as exc:raise OSError('Focused deploy failed for '+name+': '+str(exc)) from exc
    # Generate the installed .modinfo with the SDK task, not a hand-edited build
    # artifact. This target does not invoke Clean, Build, or the asset cooker.
    ns='http://schemas.microsoft.com/developer/msbuild/2003';ET.register_namespace('',ns)
    tag=lambda x:'{'+ns+'}'+x
    project=ET.Element(tag('Project'),{'ToolsVersion':'4.0','DefaultTargets':'Generate'})
    task_dll=Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK/ModBuddy/Extensions/Application/Civ6.Tasks.dll")
    ET.SubElement(project,tag('UsingTask'),{'TaskName':'Firaxis.VisualStudio.Tasks.Civ6.GenerateModInfo','AssemblyFile':str(task_dll)})
    props=ET.SubElement(project,tag('PropertyGroup'))
    values={'Guid':old.get('id'),'ModVersion':old.get('version')}
    for name in ('Name','Description','Teaser','Authors','SpecialThanks','CompatibleVersions'):
        values[name]=old.findtext('Properties/'+name) or ''
    source=ET.parse(ROOT/'Civ Supply Chains/Civ Supply Chains.civ6proj').getroot()
    for name in ('AffectsSavedGames','SupportsSinglePlayer','SupportsMultiplayer','SupportsHotSeat','ModProperties','AssociationData'):
        values[name]=source.findtext('.//'+tag(name)) or ''
    criteria=copy.deepcopy(old.find('ActionCriteria'))
    for original in list(criteria):
        if original.get('id')=='ModSupport_TAR':criteria.remove(original)
    criteria.append(json_to_node(next(c for c in mirror['blocks']['actionCriteria'] if c.get('attributes',{}).get('id')=='ModSupport_TAR')))
    values.update(ActionCriteriaData=ET.tostring(criteria,encoding='unicode'),FrontEndActionData=ET.tostring(old.find('FrontEndActions'),encoding='unicode'),InGameActionData=ET.tostring(ingame,encoding='unicode'))
    for k,v in values.items():ET.SubElement(props,tag(k)).text=v
    item_group=ET.SubElement(project,tag('ItemGroup'))
    files={f.text.replace('\\','/') for f in old.find('Files')};files.update(FILES);files.difference_update(REMOVE_FILES)
    for name in sorted(files):
        assert (a.installed/name).is_file(),name
        ET.SubElement(item_group,tag('ModFiles'),{'Include':str((a.installed/name).resolve())})
    target=ET.SubElement(project,tag('Target'),{'Name':'Generate'})
    params={k:'$('+v+')' for k,v in {'ID':'Guid','Version':'ModVersion','Name':'Name','Description':'Description','Teaser':'Teaser','Authors':'Authors','SpecialThanks':'SpecialThanks','CompatibleVersions':'CompatibleVersions','AffectsSavedGames':'AffectsSavedGames','SupportsSinglePlayer':'SupportsSinglePlayer','SupportsMultiplayer':'SupportsMultiplayer','SupportsHotSeat':'SupportsHotSeat','CustomProperties':'ModProperties','AssociationData':'AssociationData','ActionCriteriaData':'ActionCriteriaData','FrontEndActionData':'FrontEndActionData','InGameActionData':'InGameActionData'}.items()}
    params.update(Files='@(ModFiles)',TargetPath=str(manifest.resolve()))
    ET.SubElement(target,tag('GenerateModInfo'),params)
    build=a.output/'GenerateMaterialMap.proj';ET.ElementTree(project).write(build,encoding='utf-8',xml_declaration=True)
    run=subprocess.run(['C:/Windows/Microsoft.NET/Framework/v4.0.30319/MSBuild.exe',str(build.resolve()),'/nologo','/verbosity:minimal'],capture_output=True,text=True)
    (a.output/'manifest-build.log').write_text(run.stdout+run.stderr)
    if run.returncode:raise RuntimeError('SDK manifest task failed: '+(run.stdout+run.stderr)[-3000:])
    actual=ET.parse(manifest).getroot();ids={x.get('id') for x in actual.find('InGameActions')}
    assert ACTION_IDS<=ids
    assert not REMOVE_ACTION_IDS.intersection(ids)
    assert actual.find("ActionCriteria/Criteria[@id='ModSupport_TAR']/ModInUse").text=='960c7ce4-c961-43c8-90bf-282eb7b260ea'
    assert all(not Path(x.text).is_absolute() for x in actual.find('Files'))
    # Existing action trees are preserved byte-semantically, excluding just the
    # new helper's two IDs; namespace/formatting are irrelevant.
    def normalize(node):return (node.tag,node.attrib,(node.text or '').strip(),[normalize(c) for c in node])
    for original in old.find('InGameActions'):
        if original.get('id') in ACTION_IDS|REMOVE_ACTION_IDS:continue
        current=next(x for x in actual.find('InGameActions') if x.get('id')==original.get('id'))
        assert normalize(current)==normalize(original),original.get('id')
    changed=[name for name,digest in inventory.items() if sha(a.installed/name)!=digest]
    assert set(changed)<=set(FILES+['Civ Supply Chains.modinfo'])
    (a.output/'deployment.json').write_text(json.dumps({'sdk_manifest_generated':True,'installed':str(a.installed),'files':{name:sha(a.installed/name) for name in FILES+['Civ Supply Chains.modinfo']},'changed_existing_files':changed,'unrelated_actions_preserved':True},indent=2)+'\n')
    print(json.dumps({'deployed':FILES,'manifest_generated_by':'Firaxis Civ6.Tasks.GenerateModInfo','unrelated_actions_preserved':True}))


if __name__=='__main__':main()
