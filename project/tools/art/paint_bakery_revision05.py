"""Pack revised ImageGen bread basecolour only; no technical-map or other surface changes."""
from bakery_props_atlas import *
from PIL import Image
import subprocess
source=Path(sys.argv[1]);dest=STAGE/'atlas/sources/imagegen-r029';dest.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest/source.name)
for arg in sys.argv[2:]:shutil.copy2(Path(arg),dest/Path(arg).name)
m=json.loads((STAGE/'atlas/manifest.json').read_text());image=Image.open(source).convert('RGB');w,h=image.size;provenance=[]
for name,col,row in [('bakery_round_crust',0,0),('bakery_oval_bread',1,0),('bakery_long_crust',0,1),('bakery_bread_stack_side',1,1)]:
 r=next(r for r in m['regions'] if r['name']==name);crop=(col*w//2,row*h//2,(col+1)*w//2,(row+1)*h//2);image.crop(crop).resize((480,480),Image.Resampling.LANCZOS).save(STAGE/'atlas'/r['sources']['B']);provenance.append(dict(region=name,slot=r['slot'],source=(dest/source.name).relative_to(STAGE).as_posix(),source_sha256=sha(source),source_dimensions=[w,h],crop=list(crop),basecolour='ImageGen quadrant crop and resample; no procedural repaint',technical_maps='unchanged from r028'))
(dest/'provenance.json').write_text(json.dumps(provenance,indent=2));(dest/'source-hashes.json').write_text(json.dumps({p.name:sha(p) for p in dest.iterdir() if p.is_file() and p.name!='source-hashes.json'},indent=2))
subprocess.run([sys.executable,STAGE/'scripts/pack_bakery_additions.py'],check=True)
shutil.copytree(STAGE/'textures',SOURCE/'textures',dirs_exist_ok=True);shutil.copytree(dest,SOURCE/'art-provenance/imagegen-r029',dirs_exist_ok=True)
print('R029 FOUR BREAD B PANELS PACKED')
