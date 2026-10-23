"""Publish the matched cloth triangulation and its canonical shared AO release."""
import sys,json
from pathlib import Path
source=Path(__file__).with_name('integrate_windmill_angular.py').read_text()
source=source[:source.rindex("if __name__=='__main__':")]
source=source.replace('2026-10-22_Shared_01_r038','2026-10-22_Shared_01_r039').replace('content_revision=38','content_revision=39')
source=source.replace('six planar braced tower faces; tower AO rebaked in existing cells, sails and other allocations preserved.','matched front/back cloth triangles; sail AO rebaked without self-intersection marks, all other cells preserved.')
source=source.replace('Henno requested broader flat tower faces matching the timber concept on 22 October 2026.','Henno requested removal of the unnatural black sail marks on 22 October 2026.')
source=source.replace('cook-angular','cook-sails').replace('ANGULAR_REVISION','SAIL_CLEANUP')
source=source.replace('wall_UV1_remapped_per_face=True,UV3_preserved=True','cloth_triangulation_repaired=True,UV1_UV3_preserved=True')
exec(compile(source,str(__file__),'exec'))
original_stage=stage
def stage():
    original_stage()
    # Unchanged files are review inputs only, not installation writes.
    path=OUT/'install-plan.json';rows=json.loads(path.read_text())
    rows=[r for r in rows if sha(r['source'])!=r['before']]
    path.write_text(json.dumps(rows,indent=2));print('Changed files to install:',len(rows))
if __name__=='__main__':globals()[sys.argv[1]]()
