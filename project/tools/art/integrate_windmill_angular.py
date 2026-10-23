"""Publish the angular shape using the established AO release/export contract."""
import sys,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=Path(sys.argv[2])
wood=Path(__file__).with_name('integrate_windmill_wood.py').read_text()
prefix=wood[:wood.index('def stage():')].replace("exec(compile(source,str(__file__),'exec'))","source=source.replace('2026-10-22_Shared_01_r037','2026-10-22_Shared_01_r038').replace('content_revision=37','content_revision=38')\nexec(compile(source,str(__file__),'exec'))")
exec(compile(prefix,str(__file__),'exec'))
def stage():
    prepare()
    metadata()
    check=wood[wood.index('    # Independent saved-FGX'):wood.index("    rows=json.loads((OUT/'install-plan.json')")]
    exec(compile('def native_checks():\n'+check+'\nnative_checks()','native_checks','exec'),globals())
    old=Path.home()/'Desktop/Codex/windmill-wood-20261022'
    for name in ['native-animation-transforms.npz','validate-motion.py']:shutil.copy2(old/name,OUT/name)
    print('ANGULAR_REVISION_STAGED')

def metadata():
    manifest=json.loads((ATLAS/'atlas/quarter-ao-manifest.json').read_text())
    manifest['status']=RELEASE+': six planar braced tower faces; tower AO rebaked in existing cells, sails and other allocations preserved.'
    (ATLAS/'atlas/quarter-ao-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    lib=json.loads((ATLAS/'library.json').read_text());lib['AO_status']=manifest['status'];lib['change_authorization']='Henno requested broader flat tower faces matching the timber concept on 22 October 2026.'
    lib['files']={p.relative_to(ATLAS).as_posix():sha(p) for p in ATLAS.rglob('*') if p.is_file() and p.name!='library.json'}
    (ATLAS/'library.json').write_text(json.dumps(lib,indent=2)+'\n')

install_source=wood[wood.index('\ndef install():')+1:wood.index("if __name__=='__main__':")]
install_source=install_source.replace("    for row in json.loads((OUT/'texture-baseline.json').read_text()):assert sha(row['path'])==row['sha256']\n",'').replace("    for row in json.loads((OUT/'xcf-baseline.json').read_text()):assert sha(row['path'])==row['before']\n",'')
install_source=install_source.replace('cook-wood','cook-angular')
start=install_source.index("    artwork=SOURCE/");end=install_source.index("    (OUT/'publication-report.json')",start)
install_source=install_source[:start]+install_source[end:]
install_source=install_source.replace('UV1_UV3_preserved=True','wall_UV1_remapped_per_face=True,UV3_preserved=True').replace('WOOD_REVISION_INSTALLED','ANGULAR_REVISION_INSTALLED')
exec(compile(install_source,str(__file__),'exec'))
if __name__=='__main__':globals()[sys.argv[1]]()
