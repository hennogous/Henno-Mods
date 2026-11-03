"""Focused reversible AI-profile installation; preserve current non-AI build."""
import argparse,copy,hashlib,json,shutil,subprocess,sys,xml.etree.ElementTree as E
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'project/tools/modbuddy'))
from civ6proj_actions import action_from_json,json_to_node

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest(root):return {str(p.relative_to(root)):{'sha256':sha(p),'size':p.stat().st_size}for p in root.rglob('*')if p.is_file()}
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--installed',type=Path,required=True);a=p.parse_args()
 assert not a.output.exists(),'Do not overwrite an earlier deployment'
 check=subprocess.run(['powershell','-NoProfile','-Command',"Get-Process CivilizationVI,CivilizationVI_DX12 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id"],capture_output=True,text=True)
 assert not check.stdout.strip(),'Close Civ before installing source'
 a.output.mkdir(parents=True);old=E.parse(a.installed/'Civ Supply Chains.modinfo').getroot();original=manifest(a.installed)
 write(a.output/'original-installed-manifest.json',original)
 mirror=json.loads((ROOT/'project/modbuddy/CivSupplyChains.actions.json').read_text());ai_actions=[x for x in mirror['blocks']['inGameActions']if x['id'].startswith('CSC_AI')]
 ingame=copy.deepcopy(old.find('InGameActions'))
 for node in list(ingame):
  if node.get('id','').startswith('CSC_AI'):ingame.remove(node)
 for action in ai_actions:ingame.append(action_from_json(action))
 criteria=copy.deepcopy(old.find('ActionCriteria'))
 for node in list(criteria):
  if node.get('id','').startswith('CSC_AI_'):criteria.remove(node)
 for node in mirror['blocks']['actionCriteria']:
  if node.get('attributes',{}).get('id','').startswith('CSC_AI_'):criteria.append(json_to_node(node))
 files={'Settings/Settings.xml','Settings/Settings_Text.xml'}
 for action in ai_actions:files.update(action.get('files',[]))
 files.update({'Data/CSC_AI_Basic.sql','Data/CSC_AI_Profile.sql','ModSupport/ModSupport_RH_AI.sql','Lua_UI/AI/CSC_AI_Assistance.lua','Lua_UI/AI/CSC_AI_AssistanceUI.lua','Lua_UI/AI/CSC_AI_AssistanceUI.xml','Lua_UI/AI/CSC_AI_OpportunityPolicy.lua','Lua_UI/AI/CSC_AI_Research.lua'})
 for relative in sorted(files|{'Civ Supply Chains.modinfo'}):
  target=a.installed/relative
  if target.exists():dest=a.output/'backup'/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,dest)
 for relative in sorted(files):
  src=ROOT/'Civ Supply Chains'/relative;assert src.is_file(),relative
  target=a.installed/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
 ns='http://schemas.microsoft.com/developer/msbuild/2003';E.register_namespace('',ns);tag=lambda x:'{'+ns+'}'+x
 project=E.Element(tag('Project'),{'ToolsVersion':'4.0','DefaultTargets':'Generate'})
 E.SubElement(project,tag('UsingTask'),{'TaskName':'Firaxis.VisualStudio.Tasks.Civ6.GenerateModInfo','AssemblyFile':"C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK/ModBuddy/Extensions/Application/Civ6.Tasks.dll"})
 props=E.SubElement(project,tag('PropertyGroup'));values={'Guid':old.get('id'),'ModVersion':old.get('version')}
 for name in ('Name','Description','Teaser','Authors','SpecialThanks','CompatibleVersions'):values[name]=old.findtext('Properties/'+name)or''
 source=E.parse(ROOT/'Civ Supply Chains/Civ Supply Chains.civ6proj').getroot()
 for name in ('AffectsSavedGames','SupportsSinglePlayer','SupportsMultiplayer','SupportsHotSeat','ModProperties','AssociationData'):values[name]=source.findtext('.//'+tag(name))or''
 values.update(ActionCriteriaData=E.tostring(criteria,encoding='unicode'),FrontEndActionData=E.tostring(old.find('FrontEndActions'),encoding='unicode'),InGameActionData=E.tostring(ingame,encoding='unicode'))
 for k,v in values.items():E.SubElement(props,tag(k)).text=v
 group=E.SubElement(project,tag('ItemGroup'))
 allfiles={f.text.replace('\\','/')for f in old.find('Files')}|files
 for relative in sorted(allfiles):
  assert(a.installed/relative).is_file(),relative
  E.SubElement(group,tag('ModFiles'),{'Include':str((a.installed/relative).resolve())})
 target=E.SubElement(project,tag('Target'),{'Name':'Generate'})
 params={k:'$('+v+')'for k,v in {'ID':'Guid','Version':'ModVersion','Name':'Name','Description':'Description','Teaser':'Teaser','Authors':'Authors','SpecialThanks':'SpecialThanks','CompatibleVersions':'CompatibleVersions','AffectsSavedGames':'AffectsSavedGames','SupportsSinglePlayer':'SupportsSinglePlayer','SupportsMultiplayer':'SupportsMultiplayer','SupportsHotSeat':'SupportsHotSeat','CustomProperties':'ModProperties','AssociationData':'AssociationData','ActionCriteriaData':'ActionCriteriaData','FrontEndActionData':'FrontEndActionData','InGameActionData':'InGameActionData'}.items()}
 params.update(Files='@(ModFiles)',TargetPath=str(a.installed/'Civ Supply Chains.modinfo'));E.SubElement(target,tag('GenerateModInfo'),params)
 build=a.output/'GenerateAIProfile.proj';E.ElementTree(project).write(build,encoding='utf-8',xml_declaration=True)
 run=subprocess.run(['C:/Windows/Microsoft.NET/Framework/v4.0.30319/MSBuild.exe',str(build),'/nologo','/verbosity:minimal'],capture_output=True,text=True)
 (a.output/'manifest-build.log').write_text(run.stdout+run.stderr,encoding='utf-8');assert run.returncode==0,run.stdout+run.stderr
 current=manifest(a.installed);changed=sorted(k for k in original.keys()|current.keys()if original.get(k)!=current.get(k));assert {name.replace('\\','/')for name in changed}<=files|{'Civ Supply Chains.modinfo'}
 actual=E.parse(a.installed/'Civ Supply Chains.modinfo').getroot()
 def normalized(n):return n.tag,n.attrib,(n.text or'').strip(),[normalized(x)for x in n]
 for node in old.find('InGameActions'):
  if not node.get('id','').startswith('CSC_AI'):assert normalized(node)==normalized(next(n for n in actual.find('InGameActions')if n.get('id')==node.get('id')))
 write(a.output/'expected-installed-manifest.json',current);write(a.output/'deployment.json',dict(verified=True,changed=changed,new_files=sorted(set(current)-set(original)),non_AI_actions_preserved=True,art_unchanged=True,manifest_generated_by_Firaxis=True,installed=str(a.installed)))
 print(json.dumps(dict(verified=True,files=len(current),changed=len(changed),art_unchanged=True)))
if __name__=='__main__':main()
