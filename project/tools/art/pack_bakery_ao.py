from pathlib import Path
import sys,json,shutil
from PIL import Image
from bakery_props_atlas import OUT,STAGE,SOURCE,sha
ident=sys.argv[1];cell=json.loads(sys.argv[2]);p=STAGE/'atlas/sources'/(ident+'_AO128.png')
Image.open(OUT/(ident+'-AO.png')).convert('RGB').resize((128,128),Image.Resampling.LANCZOS).save(p)
atlas=STAGE/'textures/CSC_Props_Shared_01_AO.png';im=Image.open(atlas).convert('RGB');im.paste(Image.open(p),cell[:2]);im.save(atlas);shutil.copy2(atlas,SOURCE/'textures'/atlas.name)
m=json.loads((STAGE/'atlas/quarter-ao-manifest.json').read_text());f=m['pages'][0]['quarters'][0]['families'][1]
assert f['family']=='Stage3';f['allocations']=[a for a in f.get('allocations',[]) if a['id']!=ident]
f['allocations'].append(dict(id=ident,cell=cell,source=p.relative_to(STAGE).as_posix(),source_sha256=sha(p),bake='Cycles CPU 32 samples, isolated self AO, 256px raw, 5px dilation, 3.5% inset'))
(STAGE/'atlas/quarter-ao-manifest.json').write_text(json.dumps(m,indent=2))
