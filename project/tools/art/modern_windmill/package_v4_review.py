"""Store the validated entrance/silo revision as a portable editable source."""
import json, shutil, hashlib
from pathlib import Path
root=Path.home()/'Desktop'
out=root/'Codex/modern-windmill-v4-20261026'
dest=root/'Working Files/3D Art/BAKERS/Wind Mill/modern/revision-04-silo'
asset='CSC_BAKERS_Wind_Mill_Modern'
validation=json.loads((out/'source-validation.json').read_text())
assert validation['automated_pass'] and validation['error_count']==0
dest.mkdir(parents=True,exist_ok=True)
for name in (asset+'.blend','source-validation.json','assembly-review-report.json'):
    target=dest/name
    if target.exists():assert target.read_bytes()==(out/name).read_bytes(),'Existing revision differs'
    shutil.copy2(out/name,target)
shutil.copytree(out/'textures',dest/'textures',dirs_exist_ok=True)
(dest/'REVIEW.txt').write_text(
    'Modern Wind Mill revision 04 — entrance and silo\n\n'
    'Rebuilt arch surround with continuous masonry UV mapping and non-overlapping infill. '
    'Integrated cream silo, green conical cap, grain elevator and stock under the shelter. '
    'Major foundations extend 24 units below ground. Rivets, seams, block joints and '
    'window details remain painted/normal mapped.\n\n'
    'This is an assembly review master, not a new runtime installation. '
    'ImageGen base-color atlas reused from the approved material library; AO newly baked '
    'for this geometry. Front, entrance, rear and top views were checked.\n',encoding='utf-8')
(out/'review-package.json').write_text(json.dumps({'master':str(dest/(asset+'.blend')),'sha256':hashlib.sha256((dest/(asset+'.blend')).read_bytes()).hexdigest(),'runtime_updated':False},indent=2))
print(dest)
