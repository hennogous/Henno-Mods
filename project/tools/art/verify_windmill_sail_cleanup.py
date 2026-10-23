"""Verify narrowly scoped sail repair, shared AO protection and cooked format."""
import sys,json,hashlib,struct
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
OUT=Path(sys.argv[1]);OLD=OUT.parent/'windmill-angular-20261022'
NAME='CSC_BAKERS_Wind_Mill_Tower';RUIN=NAME+'_CON+PIL'
LIB=Path.home()/'Desktop/Working Files/3D Art/Textures/CSC_Props'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
report={}
for name in [NAME,RUIN]:
    before=json.loads((OLD/(name+'-native.json')).read_text());after=json.loads((OUT/(name+'-native.json')).read_text())
    assert before['models']==after['models'];old={m['name']:m for m in before['meshes']}
    for m in after['meshes']:
        a=old[m['name']]
        if not m['name'].endswith('_Sails'):assert m==a,m['name'];continue
        assert len(m['vertices'])==len(a['vertices'])==1554
        assert len(m['triangles'])==len(a['triangles'])==816
        assert m['boneBindings']==a['boneBindings']==['Sails']
        def preserved(mesh):return sorted(tuple(tuple(v[k]) for k in ['position','uv','uv3','boneIndices','boneWeights']) for v in mesh['vertices'])
        assert preserved(m)==preserved(a),'Positions, UV1/3 or skinning changed'
    report[name]=dict(skeleton_preserved=True,other_meshes_preserved=True)
code=Path(__file__).with_name('verify_windmill_wood.py').read_text()
code=code[code.index('def fnv(s):'):code.index('if installed:')].replace('cook-wood','cook-sails')
exec(compile(code,'cooked_format_check','exec'));report['cooked_formats']=cooked
old=np.array(Image.open(LIB/'Current/textures/CSC_Props_Shared_01_AO.png').convert('RGB'))
if '--installed' in sys.argv:old=np.array(Image.open(OUT/'before-library/textures/CSC_Props_Shared_01_AO.png').convert('RGB'))
new=np.array(Image.open(OUT/'atlas-release/textures/CSC_Props_Shared_01_AO.png').convert('RGB'))
mask=np.zeros((2048,2048),bool);mask[128:512,:512]=True;assert np.array_equal(old[~mask],new[~mask])
# Quantify the unoccluded front cloth interiors in their retained UV2 charts.
d=json.loads((OUT/'sail-source.json').read_text());im=Image.new('L',(2048,2048));draw=ImageDraw.Draw(im)
for p in d['polygons']:
    if all(i<456 and 64<=i%114<73 for i in p['verts']):draw.polygon([(u*2048,(1-v)*2048) for u,v in p['uv2']],fill=255)
interior=np.array(im.filter(ImageFilter.MinFilter(5)))>0
before_dark=int((old[:,:,0][interior]<128).sum());after_dark=int((new[:,:,0][interior]<128).sum())
assert before_dark>50 and after_dark==0,(before_dark,after_dark)
report['cloth_front_dark_pixels']=dict(before=before_dark,after=after_dark,sampled=int(interior.sum()))
report['other_AO_pixels_preserved']=True
for p,h in json.loads((OUT/'baseline.json').read_text()).items():
    if Path(p).suffix in ['.ast','.fgx']:assert sha(p)==h,p
if '--installed' in sys.argv:
    pub=json.loads((OUT/'publication-report.json').read_text())
    for r in pub['files']:
        if sha(r['source'])!=sha(r['destination']):
            assert Path(r['destination']).suffix=='.dds'
            assert np.array_equal(np.array(Image.open(r['source']).convert('RGB'))[:,:,0],np.array(Image.open(r['destination']).convert('RGB'))[:,:,0])
    for p in (OUT/'atlas-release').rglob('*'):
        if p.is_file():assert sha(p)==sha(LIB/'Current'/p.relative_to(OUT/'atlas-release'))==sha(LIB/'Releases/2026-10-22_Shared_01_r039'/p.relative_to(OUT/'atlas-release'))
    report['installed_verified']=True
(OUT/('final-verification.json' if '--installed' in sys.argv else 'prepublication-verification.json')).write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
