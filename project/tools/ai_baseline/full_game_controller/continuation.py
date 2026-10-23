"""Reusable exact-save provenance and observer-record restoration helpers.

These restore diagnostic Lua tables only. Native world state must come from the
verified save and pass separate physical/production/database/package checks.
"""
import json

FIELDS={
 'CSCBASE':{'events'},'CSC_BUILDERS':{'events'},
 'CSC_SERIES_RESEARCH':{'history','completions','defeats','errors','duplicate_callbacks','seen'},
 'CSC_FOUNDATION_PROBE':{'targets','history','events','scans','skips','errors'},
 'CSC_FOUNDATION_UI':{'history'},
}

def restore_observer(r,state,namespace,field,value,serialize):
 assert namespace in FIELDS and field in FIELDS[namespace],'Observer records only'
 target=namespace+'['+json.dumps(field)+']'
 if isinstance(value,list):
  r.cmd(target+'={};',state,'inherit-'+namespace+'-'+field+'-init')
  for offset in range(0,len(value),60):
   r.cmd('local v='+serialize(value[offset:offset+60])+';for _,row in ipairs(v)do table.insert('+target+',row)end;',state,'inherit-'+namespace+'-'+field+'-'+str(offset))
 else:r.cmd(target+'='+serialize(value)+';',state,'inherit-'+namespace+'-'+field)

def world_signature(s):
 cities=[]
 for c in s['cities']:
  cities.append((c['player'],c['id'],c['name'],c['x'],c['y'],c['population'],
   sorted((b['type'],b['plot'],b['pillaged'])for b in c['buildings']),
   sorted((d['type'],d['plot'],d['complete'],d['pillaged'])for d in c['districts'])))
 return {'turn':s['turn'],'width':s['width'],'height':s['height'],'cities':sorted(cities),
  'players':sorted((p['id'],p['leader'],sorted(p['techs']),sorted(p['civics']))for p in s['players']),
  'plots':sorted(tuple((k,p.get(k))for k in('index','x','y','owner','resource','improvement','feature','pillaged','terrain','district'))for p in s['plots'])}


def read_research_export(root, *, turn):
 """Resolve maintained exporter names by actual clock and schema.

 preserve_telemetry writes failure-preserved-research.json; supplemental exports
 write research-latest.json. A valid restoration must not depend on which reader
 published the file. Conflicting same-turn exports stay an error.
 """
 from pathlib import Path
 root=Path(root);matches=[]
 for name in ('research-latest.json','failure-preserved-research.json'):
  path=root/name
  if not path.exists():continue
  data=json.loads(path.read_text(encoding='utf-8-sig'))
  if data.get('turn')!=turn:continue
  assert all(k in data for k in ('history','completions','defeats','errors','duplicate_callbacks')),('Incomplete research export',str(path))
  keys=[(x['turn'],x['player'])for x in data['history']]
  assert len(keys)==len(set(keys)),('Duplicate research observations',str(path))
  matches.append((path,data))
 if not matches:raise FileNotFoundError('No maintained research export at exact native turn '+str(turn))
 assert all(data==matches[0][1]for path,data in matches), 'Conflicting same-turn research exports'
 return matches[0][1],matches[0][0]
