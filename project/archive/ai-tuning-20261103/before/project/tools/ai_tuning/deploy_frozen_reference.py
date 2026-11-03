"""Stage the exact tested AI-only delta of a frozen reference.

Never rolls back art or unrelated installed work. The complete current pretest
manifest must equal the reference's pretest manifest before staging.
"""
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inventory(root):return {str(p.relative_to(root)):{'sha256':sha(p),'size':p.stat().st_size}for p in root.rglob('*')if p.is_file()}
def write(p,v):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8')
def stage(reference,output,installed):
 assert not output.exists(),'Preserve earlier deployment output'
 audit=read(reference/'independent-audit.json');assert audit['verified_observed_contracts']and audit['profile']=='BASIC'and audit['native_endpoint']==150
 native=subprocess.run(['powershell','-NoProfile','-Command',"Get-CimInstance Win32_Process | Where-Object { $_.Name -like 'CivilizationVI*' } | Select-Object ProcessId | ConvertTo-Json"],capture_output=True,text=True)
 assert native.returncode==0 and not native.stdout.strip(),'Civ must be absent'
 old=read(reference/'deployment/deployment.json');original=read(reference/'deployment/original-installed-manifest.json');expected=read(reference/'deployment/expected-installed-manifest.json')
 before=inventory(installed);assert before==original,'Unrelated installed changes: reconcile, never overwrite'
 allowed={'Civ Supply Chains.modinfo','Lua_UI/AI/CSC_AI_Assistance.lua','Lua_UI/AI/CSC_AI_AssistanceUI.lua'}
 assert {p.replace('\\','/')for p in old['changed']}<=allowed
 pins=read(reference/'executed-source-pins.json');archive={str(Path(name).resolve()).casefold():reference/'source-version'/f'{i:04d}-{Path(name).name}'for i,name in enumerate(pins)}
 prepared=[]
 for relative in old['changed']:
  target=installed/relative;target.resolve().relative_to(installed.resolve())
  source=archive.get(str(target.resolve()).casefold());assert source and source.is_file(),relative
  assert sha(source)==expected[relative]['sha256'],relative
  prepared.append((relative,target,source))
 output.mkdir(parents=True);write(output/'original-installed-manifest.json',before)
 for relative,target,source in prepared:
  backup=output/'backup'/relative;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
 for relative,target,source in prepared:shutil.copy2(source,target)
 assert inventory(installed)==expected,'Exact frozen runtime required'
 write(output/'expected-installed-manifest.json',expected)
 write(output/'deployment.json',dict(verified=True,changed=old['changed'],new_files=[],installed=str(installed),frozen_reference=str(reference),AI_only=True,non_AI_actions_preserved=True,art_unchanged=True,Firaxis_generated_manifest_preserved=True))
 return dict(verified=True,reference=str(reference),files=len(expected),AI_only_delta=len(prepared))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--reference',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--installed',type=Path,required=True);a=p.parse_args();print(json.dumps(stage(a.reference,a.output,a.installed)))
