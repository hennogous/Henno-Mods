"""Stage ImageGen B changes and complete raw/guide/prompt provenance for r030."""
from bakery_props_atlas import *
from PIL import Image
import subprocess
m=json.loads((STAGE/'atlas/manifest.json').read_text());d=STAGE/'atlas/sources/imagegen-r030';d.mkdir(parents=True,exist_ok=True);rows=[]
items=[(Path(sys.argv[1]),[('bakery_round_crust',0,0),('bakery_oval_bread',1,0),('bakery_long_crust',0,1),('bakery_bread_stack_side',1,1)]),(Path(sys.argv[2]),[('bakery_brick',None,None)])]
for raw,specs in items:
 shutil.copy2(raw,d/raw.name);im=Image.open(raw).convert('RGB');w,h=im.size
 for name,c,r in specs:
  crop=(0,0,w,h) if c is None else (c*w//2,r*h//2,(c+1)*w//2,(r+1)*h//2);region=next(v for v in m['regions'] if v['name']==name);im.crop(crop).resize((480,480),Image.Resampling.LANCZOS).save(STAGE/'atlas'/region['sources']['B']);rows.append(dict(region=name,slot=region['slot'],source=(d/raw.name).relative_to(STAGE).as_posix(),sha256=sha(raw),dimensions=[w,h],crop=crop))
for p in [OUT/'Brick_24x12_Layout_Guide.png']+[Path(v) for v in sys.argv[3:]]:shutil.copy2(p,d/p.name)
(d/'provenance.json').write_text(json.dumps(rows,indent=2));(d/'source-hashes.json').write_text(json.dumps({p.name:sha(p) for p in d.iterdir() if p.is_file() and p.name!='source-hashes.json'},indent=2));shutil.copytree(d,SOURCE/'art-provenance/imagegen-r030',dirs_exist_ok=True)
subprocess.run([sys.executable,STAGE/'scripts/pack_bakery_additions.py'],check=True);shutil.copytree(STAGE/'textures',SOURCE/'textures',dirs_exist_ok=True)
