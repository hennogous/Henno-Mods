from bakery_props_atlas import *
assert RELEASE=='2026-10-17_Shared_01_r030';assert json.loads((LIB/'CURRENT.json').read_text())['release']=='2026-10-17_Shared_01_r029'
OUT.mkdir(parents=True,exist_ok=True);assert not STAGE.exists();shutil.copytree(LIB/'Current',STAGE);shutil.copytree(SOURCE.parent/'revision-05-prop-kit',SOURCE)
for p in (OUT.parent/'revision05').glob('*'):
 if p.is_file() and p.name.startswith('CSC_BAKERS_') and (p.suffix in ['.cn6','.fgx','.geo','.ast'] or p.name.endswith(('-export.json','-validation.json'))):shutil.copy2(p,OUT/p.name)
print('STAGED R030; no old review images copied')
