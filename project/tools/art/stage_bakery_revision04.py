from bakery_props_atlas import *
assert RELEASE=='2026-10-17_Shared_01_r028';assert json.loads((LIB/'CURRENT.json').read_text())['release']=='2026-10-16_Shared_01_r027'
OUT.mkdir(parents=True,exist_ok=True);assert not STAGE.exists();shutil.copytree(LIB/'Current',STAGE);shutil.copytree(SOURCE.parent/'revision-03-prop-kit',SOURCE)
for p in (OUT.parent/'revision03').glob('*'):
 if p.is_file() and p.name.startswith('CSC_BAKERS_') and (p.suffix in ['.cn6','.fgx','.geo','.ast'] or p.name.endswith(('-export.json','-validation.json'))):shutil.copy2(p,OUT/p.name)
print('STAGED R028; no old review images copied')
