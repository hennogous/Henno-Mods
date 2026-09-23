"""Stage approved source props, build with Blender, then install verified additions.

Normal Python: this.py prepare|install. Blender: --python this.py -- build|verify-live.
The explicit intake selection is the user's reviewed shortlist minus camp racks/fish.
"""
import json,pathlib,sys,shutil,hashlib
ROOT=pathlib.Path(__file__).resolve().parents[3]
REVIEW=pathlib.Path('C:/Users/Shadow/Desktop/Codex/pantry-candidate-review')
SOURCE=REVIEW/'work/CSC_Prop_Library'
STAGE=REVIEW/'approved-library-intake'
LIVE=pathlib.Path('C:/Users/Shadow/Desktop/Working Files/3D Art/Props/CSC_Prop_Library')
TOOLS=ROOT/'project/tools/blender'
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else sys.argv[1]
def read(p):return json.loads(p.read_text())
def write(p,d):p.write_text(json.dumps(d,indent=2)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def rejected(aid):return ('camp_' in aid.lower() and 'rack' in aid.lower()) or 'fish' in aid.lower()
def strings(value):
 if isinstance(value,str):yield value
 elif isinstance(value,dict):
  for v in value.values():yield from strings(v)
 elif isinstance(value,list):
  for v in value:yield from strings(v)
if MODE=='prepare':
 data=read(SOURCE/'catalogue.json');index=read(REVIEW/'candidate-index.json')
 approved={r['asset_id']:r for r in index['candidates'] if not rejected(r['asset_id'])}
 data['assets']=[r for r in data['assets'] if r['asset_id'] in approved]
 for r in data['assets']:
  review=approved[r['asset_id']]
  for k in ['state_behaviour','native_bindings','visual_review_note','flags']:
   if k in review:r[k]=review[k]
  r['intake_note']='Approved from pantry contact sheets; animal hide racks and fish excluded.'
 mids={m for r in data['assets'] for m in r['material_ids']}
 data['materials']={k:v for k,v in data['materials'].items() if k in mids}
 STAGE.mkdir(exist_ok=True)
 paths={s for s in strings(data) if s.startswith(('sources/','textures/')) and (SOURCE/s).is_file()}
 for r in data['assets']:
  for tid,dds in r['textures'].items():
   for p in [pathlib.Path(dds).with_suffix('.png'),pathlib.Path('sources/textures')/(tid+'.tex')]:
    if (SOURCE/p).is_file():paths.add(p.as_posix())
 for rel in paths:
  target=STAGE/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(SOURCE/rel,target)
 write(STAGE/'catalogue.json',data)
 write(REVIEW/'intake-selection.json',dict(approved=list(approved),excluded=[r['asset_id'] for r in index['candidates'] if rejected(r['asset_id'])],blocked=[r['asset_id'] for r in index['blocked']]))
 print('STAGED',len(data['assets']),'assets',len(paths),'dependencies',flush=True)
elif MODE=='build':
 import bpy
 sys.argv=['intake','--',str(STAGE)]
 source=TOOLS/'build_prop_library_blends.py'
 code=source.read_text(encoding='utf-8').split("for row in data['assets']:")[0]
 code=code.replace("s['state']=='Worked'","s['state']==row.get('preview_state','Worked')").replace("obj['default_state']='Worked'","obj['default_state']=row.get('preview_state','Worked')")
 ns={'__file__':str(source),'__name__':'intake_builder'};exec(compile(code,str(source),'exec'),ns)
 base_material=ns['material']
 def material(name,row):
  mat=base_material(name,row);nodes,links=mat.node_tree.nodes,mat.node_tree.links
  # Same source-channel interpretation as the approved contact previews.
  for channel in ('AO','Gloss','Metalness','Opacity'):
   tex=nodes.get(channel)
   if not tex:continue
   outgoing=list(tex.outputs['Color'].links)
   if not outgoing:continue
   split=nodes.new('ShaderNodeSeparateColor');split.mode='RGB';links.new(tex.outputs['Color'],split.inputs['Color'])
   for link in outgoing:
    dest=link.to_socket;links.remove(link);links.new(split.outputs['Red'],dest)
  if mat.get('source_shader')=='DecalMaterial' and nodes.get('BaseColor'):
   links.new(nodes['BaseColor'].outputs['Alpha'],nodes['Principled BSDF'].inputs['Alpha'])
  return mat
 ns['material']=material
 for row in ns['data']['assets']:
  ns['build'](row)
  row['state_behavior']=row['state_behaviour']
  row['dimension_units']='Source geometry units; identical Blender units; visible '+row['preview_state']+'-state asset-local bounds'
  row['material_conversion_notes']=['Original texture bindings retained. Blender scalar maps use red and decals use source alpha, as in approved contact sheets. Civ VI burn/snow/FOW effects remain metadata.']+row['issues']
  row['source_model_transforms']={m['geometry']:read(STAGE/m['extracted'])['models'] for m in row['models']}
  row['pivot']=[0,0,0]
 write(STAGE/'catalogue.json',ns['data'])
 exec(compile((TOOLS/'verify_prop_library.py').read_text(),str(TOOLS/'verify_prop_library.py'),'exec'),{'__name__':'intake_verify'})
elif MODE=='install':
 data=read(STAGE/'catalogue.json');live=read(LIVE/'catalogue.json')
 assert all(r['verification']['status']=='passed' for r in data['assets'])
 ids={r['asset_id'] for r in data['assets']}
 assert not ids&{r['asset_id'] for r in live['assets']},'Already installed or ID conflict'
 conflicts=[]
 for p in STAGE.rglob('*'):
  if not p.is_file() or p.name in ['catalogue.json','verification.json']:continue
  dest=LIVE/p.relative_to(STAGE)
  if dest.exists() and digest(p)!=digest(dest):conflicts.append(str(dest))
 for k,v in data['materials'].items():
  if k in live['materials'] and live['materials'][k]!=v:conflicts.append('material '+k)
 assert not conflicts,conflicts
 backup=REVIEW/'pre-intake-live-metadata';backup.mkdir(exist_ok=False)
 for name in ['catalogue.json','verification.json','README.md','STATE_BEHAVIOR.md']:
  if (LIVE/name).exists():shutil.copy2(LIVE/name,backup/name)
 before={p.name:digest(p) for p in LIVE.glob('*.blend')}
 # Retired CSC_Attached names no longer have files; the later Narrow entry
 # carries the current corrected material/UV notes. Preserve the originals in
 # the metadata snapshot, without touching any existing blend or dependency.
 stale=[r['asset_id'] for r in live['assets'] if not (LIVE/r['blend_path']).is_file()]
 current={}
 duplicates=[]
 for r in live['assets']:
  if not (LIVE/r['blend_path']).is_file():continue
  if r['asset_id'] in current:duplicates.append(r['asset_id'])
  current[r['asset_id']]=r
 live['assets']=list(current.values())
 for p in STAGE.rglob('*'):
  if not p.is_file() or p.name in ['catalogue.json','verification.json']:continue
  dest=LIVE/p.relative_to(STAGE);dest.parent.mkdir(parents=True,exist_ok=True)
  if not dest.exists():shutil.copy2(p,dest)
 live['assets'].extend(data['assets']);live['materials'].update(data['materials'])
 write(LIVE/'catalogue.json',live)
 old={r['asset_id']:r for r in read(LIVE/'verification.json') if r['asset_id'] in current}
 for aid,r in current.items():
  if 'verification' in r:old[aid]=r['verification']
 write(LIVE/'verification.json',list(old.values())+read(STAGE/'verification.json'))
 with (LIVE/'STATE_BEHAVIOR.md').open('w',encoding='utf-8') as f:
  f.write('# CSC prop state behaviour\n\nSource metadata only; runtime behaviour has not been verified by this intake. Construction-state previews are labelled in the catalogue.\n\n| Asset | Construction | Pillaged |\n|---|---|---|\n')
  for r in live['assets']:
   states=r.get('state_behavior',{})
   def note(key):
    value=states.get(key,{});return value.get('note','See catalogue source/state metadata.') if isinstance(value,dict) else str(value)
   f.write('| '+r['asset_id']+' | '+note('Construction')+' | '+note('Pillaged')+' |\n')
 with (LIVE/'README.md').open('a',encoding='utf-8') as f:
  f.write('\n## Pantry material intake\n\nAdded '+str(len(ids))+' approved material/storage/work props. Five camp hide racks and the fish bin were excluded. Eleven additions open in Construction state because they are native construction-stock assets; consult their source state notes before reuse. Original source materials, transforms and all state components are retained. Scalar red-channel and decal-alpha Blender interpretation matches the approved contact sheets. See catalogue.json for the current inventory; eight unrendered candidates remain outside the library.\n')
 assert all(digest(LIVE/n)==h for n,h in before.items())
 write(REVIEW/'intake-install-report.json',dict(added=sorted(ids),existing_blends_preserved=len(before),catalogue_entries=len(live['assets']),blend_files=len(list(LIVE.glob('*.blend'))),stale_catalogue_entries_removed=stale,duplicate_catalogue_entries_resolved=duplicates))
 print('INSTALLED',len(ids),'preserved',len(before),'existing blends',flush=True)
elif MODE=='verify-live':
 # Verify only these additions against live dependencies; preserve existing reports.
 data=read(LIVE/'catalogue.json');ids=set(read(REVIEW/'intake-selection.json')['approved'])
 source=(TOOLS/'verify_prop_library.py').read_text()
 source=source.replace("data=json.loads((LIB/'catalogue.json').read_text())","data=json.loads((LIB/'catalogue.json').read_text()); data['assets']=[r for r in data['assets'] if r['asset_id'] in "+repr(ids)+"]")
 source=source.replace("(LIB/'verification.json').write_text(json.dumps(reports,indent=2))","(pathlib.Path("+repr(str(REVIEW))+ ")/'intake-live-verification.json').write_text(json.dumps(reports,indent=2))")
 source=source.replace("(LIB/'catalogue.json').write_text(json.dumps(data,indent=2))",'')
 sys.argv=['verify-live','--',str(LIVE)]
 exec(compile(source,str(TOOLS/'verify_prop_library.py'),'exec'),{'__name__':'intake_live_verify'})
else:raise ValueError(MODE)
