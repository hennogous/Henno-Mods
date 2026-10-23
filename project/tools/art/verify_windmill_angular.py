"""Confirm planar export normals, preserved moving parts, native bindings and cooked formats."""
import sys,json,hashlib,struct
from pathlib import Path
import numpy as np
from PIL import Image
OUT=Path(sys.argv[1]);OLD=OUT.parent/'windmill-wood-20261022';NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={}
for name in [NAME,RUIN]:
    before=json.loads((OLD/(name+'-native.json')).read_text());after=json.loads((OUT/(name+'-native.json')).read_text())
    assert before['models']==after['models'],'Skeleton changed'
    a={m['name']:m for m in before['meshes']};dots=[];count=0
    for m in after['meshes']:
        assert m['boneBindings']==(['Sails'] if m['name'].endswith('_Sails') else ['Root'])
        if m['name'].endswith('_Sails') or 'Scaffolding' in m['name']:assert m==a[m['name']],m['name'];continue
        for tri in m['triangles']:
            vs=[m['vertices'][i] for i in tri[:3]]
            if not all(513/1024<=v['uv'][0]<=643/1024 and 615/1024<=v['uv'][1]<=745/1024 for v in vs):continue
            p=np.array([v['position'] for v in vs]);n=np.cross(p[1]-p[0],p[2]-p[0]);n/=np.linalg.norm(n)
            for v in vs:
                normal=np.array(v['normal']);dots.append(float(n@normal/np.linalg.norm(normal)))
            count+=1
    assert min(dots)>.9999,(name,min(dots))
    report[name]=dict(wood_triangles=count,min_export_normal_dot_face=min(dots),skeleton_unchanged=True,other_meshes_unchanged=True)
# Reuse the independent cooked-record decoder from the preceding revision.
code=Path(__file__).with_name('verify_windmill_wood.py').read_text()
code=code[code.index('def fnv(s):'):code.index('if installed:')].replace('cook-wood','cook-angular')
exec(compile(code,'cooked_format_check','exec'))
report['cooked_formats']=cooked
if '--installed' in sys.argv:
    pub=json.loads((OUT/'publication-report.json').read_text())
    for r in pub['files']:
        if sha(r['source'])!=sha(r['destination']):
            assert Path(r['destination']).suffix=='.dds'
            assert np.array_equal(np.array(Image.open(r['source']).convert('RGB'))[:,:,0],np.array(Image.open(r['destination']).convert('RGB'))[:,:,0])
    for p,h in json.loads((OUT/'baseline.json').read_text()).items():
        if Path(p).suffix in ['.ast','.fgx']:assert sha(p)==h,p
    lib=Path.home()/'Desktop/Working Files/3D Art/Textures/CSC_Props'
    for p in (OUT/'atlas-release').rglob('*'):
        if p.is_file():assert sha(p)==sha(lib/'Current'/p.relative_to(OUT/'atlas-release'))==sha(lib/'Releases/2026-10-22_Shared_01_r038'/p.relative_to(OUT/'atlas-release'))
    report['installed_verified']=True
(OUT/('final-verification.json' if '--installed' in sys.argv else 'prepublication-verification.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
