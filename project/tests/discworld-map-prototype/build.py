"""Package the isolated disc prototype, reusing installed Firaxis ice art as a placeholder."""
import argparse, copy, hashlib, json, shutil, xml.etree.ElementTree as ET
from pathlib import Path

MOD_ID='98e2f456-2236-4bb9-a76c-4fe7cc928108'
HERE=Path(__file__).resolve().parent
GAME=Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI")
PANTRY=Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK Assets/Civ6/pantry")
def save_xml(root,path):
    ET.indent(root); ET.ElementTree(root).write(path,encoding='utf-8',xml_declaration=True)
def build(out):
    out.mkdir(parents=True,exist_ok=True); (out/'ArtDefs').mkdir(exist_ok=True)
    for name in ('Discworld_Prototype.lua','Discworld_Data.sql','Discworld_Config.xml','Discworld_Text.xml','Discworld_Rimfall.lua','Discworld_Rimfall.xml'):
        shutil.copy2(HERE/name,out/name)
    art=ET.parse(PANTRY/'ArtDefs/Features.artdef').getroot()
    collection=art.find('m_RootCollections/Element')
    for e in list(collection.findall('Element')):
        if e.find('m_Name').get('text')!='FEATURE_ICE':collection.remove(e)
        else:e.find('m_Name').set('text','FEATURE_DISC_VOID')
    save_xml(art,out/'ArtDefs/Discworld_Features.artdef')
    base=ET.parse(GAME/'Base/Civ6.dep').getroot()
    dep=ET.Element('AssetObjects..GameDependencyData'); ident=ET.SubElement(dep,'ID')
    ET.SubElement(ident,'name',text='Discworld_Prototype'); ET.SubElement(ident,'id',text=MOD_ID)
    req=ET.SubElement(dep,'RequiredGameArtIDs'); ref=ET.SubElement(req,'Element')
    for e in base.find('ID'):ref.append(copy.deepcopy(e))
    systems=ET.SubElement(dep,'SystemDependencies')
    for system in base.find('SystemDependencies'):
        paths=system.find('ArtDefDependencyPaths')
        if paths is not None and any(p.get('text')=='Features.artdef' for p in paths):
            s=copy.deepcopy(system); p=s.find('ArtDefDependencyPaths');p.clear()
            ET.SubElement(p,'Element',text='Discworld_Features.artdef');systems.append(s)
    adeps=ET.SubElement(dep,'ArtDefDependencies');a=ET.SubElement(adeps,'Element')
    ET.SubElement(a,'ArtDefPath',text='Discworld_Features.artdef')
    ET.SubElement(a,'ArtDefDependencyPaths');ET.SubElement(dep,'LibraryDependencies')
    save_xml(dep,out/'Discworld_Prototype.dep')
    mod=ET.Element('Mod',id=MOD_ID,version='1');p=ET.SubElement(mod,'Properties')
    for k,v in dict(Name='Discworld — Map Prototype',Description='Circular playable disc, snowy Hub and impassable placeholder Rim. Requires Gathering Storm.',Authors='Henno / Codex',CompatibleVersions='2.0').items():ET.SubElement(p,k).text=v
    front=ET.SubElement(mod,'FrontEndActions');game=ET.SubElement(mod,'InGameActions')
    for parent,kind,id,file in [(front,'UpdateDatabase','DiscConfig','Discworld_Config.xml'),(front,'UpdateText','DiscFrontText','Discworld_Text.xml'),(game,'UpdateDatabase','DiscData','Discworld_Data.sql'),(game,'UpdateText','DiscText','Discworld_Text.xml'),(game,'ImportFiles','DiscMap','Discworld_Prototype.lua'),(game,'UpdateArt','DiscArt','Discworld_Prototype.dep')]:
        action=ET.SubElement(parent,kind,id=id);ET.SubElement(action,'File').text=file
    # Map scripts also need to exist in the front-end VFS for selection/init data.
    action=ET.SubElement(front,'ImportFiles',id='DiscMapFront');ET.SubElement(action,'File').text='Discworld_Prototype.lua'
    action=ET.SubElement(game,'AddUserInterfaces',id='DiscRimfallPreview')
    props=ET.SubElement(action,'Properties');ET.SubElement(props,'Context').text='InGame'
    ET.SubElement(action,'File').text='Discworld_Rimfall.xml'
    action=ET.SubElement(game,'ImportFiles',id='DiscRimfallScript')
    ET.SubElement(action,'File').text='Discworld_Rimfall.lua'
    files=ET.SubElement(mod,'Files')
    for f in sorted(out.rglob('*')):
        if f.is_file() and f.suffix in ('.lua','.sql','.xml','.artdef','.dep'):ET.SubElement(files,'File').text=f.relative_to(out).as_posix()
    save_xml(mod,out/'Discworld_Prototype.modinfo')
    return {f.relative_to(out).as_posix():hashlib.sha256(f.read_bytes()).hexdigest() for f in out.rglob('*') if f.is_file()}
if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);ap.add_argument('--install',type=Path);a=ap.parse_args()
    hashes=build(a.output)
    if a.install:shutil.copytree(a.output,a.install,dirs_exist_ok=True)
    print(json.dumps(hashes,indent=2))
