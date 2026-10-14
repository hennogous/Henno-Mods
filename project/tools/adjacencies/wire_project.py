"""Register the bundled adjacency engine in CSC's source action manifest."""
import json
import re
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE='Lua_UI/Adjacencies/'


def main():
    path=ROOT/'project/modbuddy/CivSupplyChains.actions.json'
    data=json.loads(path.read_text(encoding='utf-8-sig'))
    actions=data['blocks']['inGameActions']
    actions[:]=[a for a in actions if not a['id'].startswith('CSC_Adjacency') and a['id']!='CSC_Ruivo_AdjacencyProcessor']
    for a in actions:
        if a['id']=='CSC_MAB_DB_RingFix': a['id']='CSC_UI_DynamicDatabase'
    def add(kind,key,order,files):
        actions.append({'type':kind,'id':key,'properties':{'LoadOrder':str(order)},'files':files})
    add('UpdateDatabase','CSC_AdjacencySchema',90,[BASE+'CSC_AdjacencySchema.sql',BASE+'CSC_AdjacencySources.sql'])
    add('UpdateDatabase','CSC_AdjacencyProcessor',3000,[BASE+'CSC_AdjacencyProcessor.sql'])
    add('UpdateDatabase','CSC_AdjacencyModifiers',4000,[BASE+'CSC_AdjacencyModifiers.sql'])
    add('UpdateText','CSC_AdjacencyText',4000,['Text/CSC_ADJACENCY_TEXT.sql','Text/CSC_ADJACENCY_SOURCES_TEXT.sql'])
    add('ImportFiles','CSC_AdjacencyModules',490,[BASE+'CSC_AdjacencyCore.lua',BASE+'CSC_AdjacencyPresentation.lua',
        BASE+'CSC_StockAdjacencyBonusSupport.lua'])
    add('ImportFiles','CSC_AdjacencyUI',501,[BASE+'AdjacencyBonusSupport.lua'])
    add('AddGameplayScripts','CSC_AdjacencyGameplay',501,[BASE+'CSC_AdjacencyGameplay.lua'])
    actions.append({'type':'AddUserInterfaces','id':'CSC_AdjacencyNativeReads',
        'properties':{'LoadOrder':'501','Context':'InGame'},'files':[BASE+'CSC_AdjacencyUI.xml']})
    add('ImportFiles','CSC_AdjacencyUIBridge',490,[BASE+'CSC_AdjacencyUI.lua'])
    path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    project=ROOT/data['sourceProject']
    text=project.read_text(encoding='utf-8-sig')
    text=re.sub(r'^\s*<Dependency type="Mod" title="Modular Adjacency Bonuses Core"[^>]+/>\s*$', '',text,flags=re.M)
    text=re.sub(r'^\s*<Content Include="Lua_UI\\Ruivo_Adjacencies\\[^\"]+">.*?</Content>', '',text,flags=re.M|re.S)
    text=text.replace('<Folder Include="Lua_UI\\Ruivo_Adjacencies" />','<Folder Include="Lua_UI\\Adjacencies" />')
    for retired in ['CSC_StockToolTipHelper.lua','ToolTipHelper.lua','ToolTipLoader_CSCAdjacency.lua']:
        text=re.sub(r'\s*<Content Include="'+re.escape('Lua_UI\\Adjacencies\\'+retired)+r'">.*?</Content>', '',text,flags=re.S)
    files=sorted((ROOT/'Civ Supply Chains/Lua_UI/Adjacencies').glob('*'))
    files.extend(ROOT/'Civ Supply Chains'/name for name in ['Text/CSC_ADJACENCY_TEXT.sql','Text/CSC_ADJACENCY_SOURCES_TEXT.sql'])
    for file in files:
        relative=str(file.relative_to(ROOT/'Civ Supply Chains'))
        if 'Include="'+relative+'"' not in text:
            content='    <Content Include="'+relative+'">\n      <SubType>Content</SubType>\n    </Content>\n'
            end=text.rfind('  </ItemGroup>')
            text=text[:end]+content+text[end:]
    text=text.replace('<SpecialThanks>\n    </SpecialThanks>',
        '<SpecialThanks>Ruivo, whose Modular Adjacency Bonuses inspired CSC\'s bundled adjacency engine; Zegangani for the specific-Wonder approach.</SpecialThanks>')
    project.write_text(text,encoding='utf-8')
    print('Bundled adjacency actions registered; regenerate with civ6proj_actions.py patch')


if __name__=='__main__': main()
