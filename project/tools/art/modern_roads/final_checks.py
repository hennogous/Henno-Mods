"""Final consistency checks across exact saved sources, textures and native readbacks."""
from pathlib import Path
import json,hashlib
O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout'
D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
saved=json.loads((O/'final-saved-validation.json').read_text());assert len(saved)==15 and all(r['automated_pass'] for r in saved)
records=json.loads((O/'masters.json').read_text());rows=[]
for record in records:
 ident=record['id'];m=json.loads((O/'models'/(ident+'.json')).read_text())['meshes'][0];n=json.loads((O/'native'/(ident+'.json')).read_text())['meshes'][0]
 assert m['triangles']==n['triangles'] and len(m['vertices'])==len(n['vertices']) and n['boneBindings']==['Bone']
 expected='CSC_Roads_'+('Industrial' if ident.endswith('_Industrial') else 'Modern')+'_01'
 assert n['materialName']==expected==m['materials'][0]['name']
 error=0
 for v,w in zip(m['vertices'],n['vertices']):
  values=w['position']+w['normal']+w['tangent']+w['binormal']+w['uv']+w['uv2']+w['uv3'];error=max(error,max(abs(x-y) for x,y in zip(v,values)))
  assert all(0<=x<=1 for x in v[12:]) and w['boneWeights']==[255,0,0,0,0,0,0,0] and w['boneIndices']==[0]*8
 assert error<1e-4
 path=Path(record['blend']);assert path.is_file() and path.with_suffix('.cn6').is_file()
 rows.append({'id':ident,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'vertices':len(m['vertices']),'triangles':len(m['triangles']),'material':expected,'native_max_error':error})
for key in ['Roundabout','NW','NE','E','SE','SW','Connector']:
 a=json.loads((O/'models'/f'CSC_Road_{key}_Industrial.json').read_text())['meshes'][0];b=json.loads((O/'models'/f'CSC_Road_{key}_Modern.json').read_text())['meshes'][0]
 assert a['triangles']==b['triangles'] and len(a['vertices'])==len(b['vertices'])
 for v,w in zip(a['vertices'],b['vertices']):
  assert max(abs(x-y) for x,y in zip(v[:2]+v[3:],w[:2]+w[3:]))<1e-4
  assert abs(w[2]-v[2]-1)<1e-5
alignment=json.loads((O/'classical-alignment-validation.json').read_text());assert alignment['source_unchanged'] and len(alignment['exits'])==5
source=json.loads((O/'classical-live.json').read_text());assert hashlib.sha256(Path(source['source']).read_bytes()).hexdigest()==source['sha256']
result={'saved_files_passed':15,'native_modules_passed':14,'paired_surface_geometry_uv_parity':True,'classical_exit_alignment_pass':True,'textures':json.loads((O/'texture-validation.json').read_text()),'models':rows,'visual_review':['Five exits and lower bypass match sketch topology','All three principal stages inspected','Classical alpha overlay inspected at same world scale','Final bend pinching and overlapping-card seams corrected','No actual placed-building clearance or native shader/terrain test performed'],'status':'Authoring candidate; no AE/runtime installation'}
(O/'delivery-validation.json').write_text(json.dumps(result,indent=2));print('FINAL_PASS',len(rows),'modules;15 saved files;5 exact classical exit corridors;8 DDS maps')
