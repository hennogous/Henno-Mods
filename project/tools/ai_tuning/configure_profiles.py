"""Generate CSC AI mode criteria/actions from the reviewed RH ID registry.

Run from any directory. This edits source JSON/ModBuddy metadata only; it never
builds, deploys, loads a game or modifies Workshop files.
"""
import argparse,copy,importlib.util,json,re,uuid
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
CONTENT=[
 'Data/CSC_AI_Profile.sql','Data/CSC_AI_Basic.sql',
 'ModSupport/ModSupport_RH_AI.sql','ModSupport/ModSupport_RH_AI_Roles.lua','Lua_UI/AI/CSC_AI_OpportunityPolicy.lua',
 'Lua_UI/AI/CSC_AI_Assistance.lua','Lua_UI/AI/CSC_AI_AssistanceUI.lua',
 'Lua_UI/AI/CSC_AI_AssistanceUI.xml',
]
def criterion(name,child):return {'tag':'Criteria','attributes':{'id':name},'children':[child]}
def mod_criterion(name,mod_id,inverse=False):
 child={'tag':'ModInUse','text':mod_id}
 if inverse:child['attributes']={'inverse':'1'}
 return criterion(name,child)
def enabled_criterion():
 return criterion('CSC_AI_Enabled',{'tag':'ConfigurationValueMatches','children':[
  {'tag':'ConfigurationId','text':'CSC_AI_ASSISTANCE'},
  {'tag':'Group','text':'Game'},{'tag':'Value','text':'1'}]})
def action(kind,name,files,criteria,order,properties=None):
 result=dict(type=kind,id=name,files=files,properties={'LoadOrder':str(order),**(properties or {})})
 if criteria:result['criteria']=criteria
 return result
def generate(data,registry):
 data=copy.deepcopy(data);aliases=registry['rh']
 assert aliases and len({a['modId']for a in aliases})==len(aliases)
 for a in aliases:uuid.UUID(a['modId'])
 criteria=data['blocks']['actionCriteria']
 criteria[:]=[c for c in criteria if c.get('attributes',{}).get('id')!='CSC_AI_Enabled'
             and not c.get('attributes',{}).get('id','').startswith('CSC_AI_RH_')]
 criteria.append(enabled_criterion())
 for i,a in enumerate(aliases):
  criteria.extend([mod_criterion('CSC_AI_RH_'+str(i),a['modId']),mod_criterion('CSC_AI_RH_No_'+str(i),a['modId'],True)])
 actions=data['blocks']['inGameActions']
 old={'CSC_AI','CSC_AI_Research','CSC_AI_MaterialCare_DB','CSC_AI_MaterialCare'}
 actions[:]=[a for a in actions if a['id']not in old and not a['id'].startswith('CSC_AI_Mode_') and a['id']!='CSC_AI_Profile']
 for a in actions:
  # Other CSC tooltip/lens wrappers include this filter even with tuning off.
  # It filters only CSC's namespace and contains no gameplay tuning.
  if a['id']=='CSC_AI_UI':a.pop('criteria',None)
  if a['id']=='CSC_AI_ReportScreen':a['criteria']=['CSC_AI_Enabled']+['CSC_AI_RH_No_'+str(i)for i in range(len(aliases))]
 actions.append(action('UpdateDatabase','CSC_AI_Profile',['Data/CSC_AI_Profile.sql'],[],3499))
 profiles=[('Basic',['CSC_AI_Enabled']+['CSC_AI_RH_No_'+str(i)for i in range(len(aliases))],3500,'Data/CSC_AI_Basic.sql')]
 for i,a in enumerate(aliases):
  # If aliases are simultaneously enabled, choose the first registered release.
  # No duplicate shared SQL, script installation or funding handlers.
  gate=['CSC_AI_Enabled','CSC_AI_RH_'+str(i)]+['CSC_AI_RH_No_'+str(j)for j in range(i)]
  profiles.append(('RH_'+str(i),gate,int(a['loadAfter'])+100,'ModSupport/ModSupport_RH_AI.sql'))
 for name,gate,order,profile_file in profiles:
  prefix='CSC_AI_Mode_'+name
  actions.extend([
   action('UpdateDatabase',prefix+'_DB',['Data/CSC_AI.sql',profile_file],gate,order),
   action('AddGameplayScripts',prefix+'_Research',['Lua_UI/AI/CSC_AI_Research.lua'],gate,order+1),
   action('ImportFiles',prefix+'_Imports',['Lua_UI/AI/CSC_AI_OpportunityPolicy.lua','Lua_UI/AI/CSC_AI_AssistanceUI.lua'],gate,order+2),
   action('AddGameplayScripts',prefix+'_Assistance',['Lua_UI/AI/CSC_AI_Assistance.lua'],gate,order+3),
   action('AddUserInterfaces',prefix+'_UI',['Lua_UI/AI/CSC_AI_AssistanceUI.xml'],gate,order+4,{'Context':'InGame'}),
  ])
  if name.startswith('RH_'):
   actions.append(action('AddGameplayScripts',prefix+'_CustomerRoles',['ModSupport/ModSupport_RH_AI_Roles.lua'],gate,order+2))
 return data
def ensure_content(text):
 existing=set(re.findall(r'<Content Include="([^"]+)"',text))
 additions=[]
 for file in CONTENT:
  path=file.replace('/','\\')
  if path not in existing:
   subtype='Lua'if file.endswith('.lua')else'Content'
   additions.append('    <Content Include="'+path+'">\n      <SubType>'+subtype+'</SubType>\n    </Content>')
 if additions:
  marker='    <Content Include="Data\\CSC_AI.sql">'
  assert marker in text;text=text.replace(marker,'\n'.join(additions)+'\n'+marker,1)
 return text
def main():
 p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=ROOT);a=p.parse_args();root=a.root
 mirror=root/'project/modbuddy/CivSupplyChains.actions.json'
 registry=json.loads((root/'project/config/csc-ai-profiles.json').read_text())
 data=generate(json.loads(mirror.read_text()),registry)
 tool=root/'project/tools/modbuddy/civ6proj_actions.py'
 spec=importlib.util.spec_from_file_location('civ6proj_actions',tool);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 project=root/'Civ Supply Chains/Civ Supply Chains.civ6proj'
 text=project.read_text(encoding='utf-8-sig');after=ensure_content(module.patch_project_text(text,data))
 mirror.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
 if after!=text:project.write_text(after,encoding='utf-8')
 module.validate(project,mirror)
 print('Generated mutually exclusive Basic/RH modes; source only.')
if __name__=='__main__':main()
