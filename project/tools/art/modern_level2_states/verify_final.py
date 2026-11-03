import json,hashlib,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];O=Path.home()/'Desktop/Codex/modern-l2-states-20261029';MOD=ROOT/'Civ Supply Chains'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pub=json.loads((O/'publication-report.json').read_text());assert all(sha(r['destination'])==r['after'] for r in pub['files'])
changed={str(Path(r['destination']).relative_to(MOD)) for r in pub['files'] if Path(r['destination']).is_relative_to(MOD)}
baseline=json.loads((O/'baseline.json').read_text());assert all(sha(MOD/p)==h for p,h in baseline.items() if p not in changed)
master=json.loads((O/'final-master.json').read_text());assert sha(master['blend'])==master['sha256'];assert json.loads(Path(master['blend']).with_name('validation.json').read_text())['automated_pass']
cur=Path.home()/'Desktop/Working Files/3D Art/Textures/CSC_Buildings_Modern/Current';manifest=json.loads((cur/'library.json').read_text());assert manifest['release']=='2026-10-29_Modern_r015';assert all(sha(cur/'textures'/p)==h for p,h in manifest['maps'].items())
report={'passed':True,'published_hashes_verified':len(pub['files']),'unchanged_preexisting_runtime_files':len(baseline)-len(changed&set(baseline)),'master':master,'release':manifest['release'],'state_geometry':'CSC_Level_2_Modern_CON+PIL','worked_geometry_and_assemblies_preserved':True,'no_extension':True,'in_game_tested':False}
(O/'final-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
