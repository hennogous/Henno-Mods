"""Isolated SDK cook of this prototype only; never build or deploy the live mod."""
import sys,shutil,subprocess,os,json
from pathlib import Path
import xml.etree.ElementTree as E
ROOT=Path(__file__).resolve().parents[4];OUT=Path(sys.argv[1]);NAME='CSC_BAKERS_Wind_Mill_Modern'
stage=OUT/'staged';pantry=OUT/'cook-pantry';pantry.mkdir(exist_ok=True)
for folder in ['Assets','Geometries','Materials','Textures']:shutil.copytree(stage/folder,pantry/folder,dirs_exist_ok=True)
x=E.parse(ROOT/'Civ Supply Chains/XLPs/CSC_Tilebases.xlp').getroot();x.find('m_Entries').clear();x.find('m_PackageName').set('text','ModernMillCheck')
identifiers=sorted(p.stem for p in (stage/'Assets').glob('*.ast')) if '--all-stage-assets' in sys.argv else [NAME]
for ident in identifiers:
    row=E.SubElement(x.find('m_Entries'),'Element')
    for tag in ('m_EntryID','m_ObjectName'):E.SubElement(row,tag,{'text':ident})
E.ElementTree(x).write(OUT/'ModernMillCheck.xlp',encoding='utf-8',xml_declaration=True)
common=Path('C:/Program Files (x86)/Steam/steamapps/common');cooker=next(common.glob('*Civilization VI SDK/AssetModTools/Cooker'));sdk=next(common.glob('*Civilization VI SDK Assets'))
target=OUT/'cook-check';target.mkdir(exist_ok=True)
cmd=[str(cooker/'Civ6AssetCooker_FinalRelease.exe'),'--absolute_paths','--no_mt','--mode','XLP','--platform','Windows','--shaders',str(cooker),'--pantry',str(pantry)]
for p in ['Civ6/pantry','Civ6/DLC/Shared/pantry','Civ6/DLC/Expansion1/pantry','Civ6/DLC/Expansion2/pantry']:cmd+=['--pantry',str(sdk/p)]
cmd+=['--stewpot',str(target/'BLPs'),'--config',str(cooker/'Civ6.cfg'),'--log_path',str(target),str(OUT/'ModernMillCheck.xlp')]
(target/'command.json').write_text(json.dumps(cmd,indent=2))
if '--capture' in sys.argv:
    cmd=[str(Path.home()/'Desktop/Codex/AE_Crash_Diagnostic_20261012/tools/procdump64.exe'),'-accepteula','-ma','-e','-g','-x',str(target),*cmd]
with (target/'stdout.log').open('w') as log:result=subprocess.run(cmd,cwd=target,stdout=log,stderr=subprocess.STDOUT,timeout=240,env=dict(os.environ,_NO_DEBUG_HEAP='1'))
report={'exit_code':result.returncode,'blps':[str(p) for p in target.rglob('*.blp')]};(target/'result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));print((target/'stdout.log').read_text(errors='replace').replace('\x00','')[-4000:]);assert result.returncode==0 and report['blps']
