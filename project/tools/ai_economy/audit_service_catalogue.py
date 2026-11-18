"""Read the real Service catalogue from a gameplay SQLite snapshot; launch nothing.

The production Lua compiler follows loaded attachments and requirements. This
offline report exposes its coverage/omissions without hand-authored Service data.
Requires the same isolated lupa dependency as the economy regression suite.
"""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3
from lupa.lua51 import LuaRuntime

ROOT=Path(__file__).resolve().parents[3]
TABLES={'CSC_QuarterFlowBuildings':None,'BuildingModifiers':None,
        'Modifiers':'ModifierId','DynamicModifiers':'ModifierType',
        'ModifierArguments':None,'Requirements':'RequirementId',
        'RequirementSets':'RequirementSetId','RequirementArguments':None,
        'RequirementSetRequirements':None,'BuildingReplaces':None,
        'GreatPersonClasses':'GreatPersonClassType'}


def audit(database):
    database=Path(database).resolve(strict=True)
    vm=LuaRuntime(unpack_returned_tuples=True)
    vm.execute('''GameInfo={}
function info(rows,key)
 local result={};for _,r in ipairs(rows)do if key then result[r[key]]=r end end
 return setmetatable(result,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end''')
    with sqlite3.connect('file:'+database.as_posix()+'?mode=ro',uri=True) as connection:
        connection.row_factory=sqlite3.Row
        connection.execute('BEGIN')
        for name,key in TABLES.items():
            rows=[dict(r) for r in connection.execute('SELECT * FROM '+name)]
            vm.globals().GameInfo[name]=vm.globals().info(vm.table_from(rows,recursive=True),key)
    source=ROOT/'Civ Supply Chains/Lua_UI/AI/CSC_AI_EconomyFacts.lua'
    vm.execute(source.read_text(encoding='utf-8'))
    catalogue=vm.globals().CSC_AI_EconomyFacts.ServiceCatalogue()
    rows=[];counts=Counter()
    for _,entries in catalogue['byProducer'].items():
        for _,r in entries.items():
            counts[f"{r['quarter']}:{int(r['stage'])}:{r['kind']}"]+=1
            rows.append(dict(source=r['source'],root=r['root'],leaf=r['leaf'],kind=r['kind'],
                             amount=r['amount'],pseudo_yield=r['pseudoYield'],
                             materials=dict(r['owner']['tags']),civics=sorted(r['owner']['civics']),
                             customers=sorted(r['subject']['buildings'])))
    return dict(database=str(database),database_sha256=hashlib.sha256(database.read_bytes()).hexdigest(),
                facts_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),counts=dict(sorted(counts.items())),
                effects=sorted(rows,key=lambda r:(r['source'],r['root'])),
                omissions=sorted(catalogue['omissions'].values()))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database',type=Path,required=True)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args();result=audit(args.database)
    if args.output:
        args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='effects'},indent=2))
