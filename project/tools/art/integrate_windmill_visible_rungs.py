"""Publish the removal of the cloth-covered rungs using the checked sail pipeline."""
from pathlib import Path
source=Path(__file__).with_name('integrate_windmill_split_sails.py').read_text()
source=source.replace('2026-10-24_Shared_01_r043','2026-10-24_Shared_01_r044').replace('2026-10-22_Shared_01_r042','2026-10-24_Shared_01_r043')
source=source.replace('content_revision=43','content_revision=44')
source=source.replace('split sail cloth and exposed rungs rebaked','cloth-covered rear rungs removed and sail self-AO rebaked')
source=source.replace('two separate cloth panels and three exposed thick rungs per blade','two separate cloth panels; four rungs per blade visible from both sides, including three thicker boundary rungs')
source=source.replace('panels_per_blade=2,exposed_structural_rungs_per_blade=3','panels_per_blade=2,exposed_structural_rungs_per_blade=3,total_rungs_per_blade=4,hidden_rungs_removed=8')
exec(compile(source,str(__file__),'exec'))
