"""ImageGen-backed r027 patches, with immutable originals and deterministic panel crops."""
from bakery_props_atlas import *
from PIL import Image,ImageFilter
import subprocess

def main():
 assert RELEASE.endswith('r027')
 if not STAGE.exists():
  OUT.mkdir(parents=True,exist_ok=True);shutil.copytree(LIB/'Current',STAGE);shutil.copytree(SOURCE.parent/'revision-02-prop-kit',SOURCE)
  prior=OUT.parent/'revision02'
  for p in prior.glob('*'):
   if p.is_file() and (p.name.startswith('CSC_BAKERS_') or p.name=='oven-remap.json'):shutil.copy2(p,OUT/p.name)
 m=json.loads((STAGE/'atlas/manifest.json').read_text());provenance=[]
 for source,kind in [(Path(sys.argv[1]),'bread'),(Path(sys.argv[2]),'materials')]:
  dest=STAGE/'atlas/sources/imagegen-r027'/source.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,dest)
  image=Image.open(source).convert('RGB');w,h=image.size
  specs=[('bakery_round_crust',61,0,0),('bakery_oval_bread',30,1,0),('bakery_long_crust',62,0,1),('bakery_bread_stack_side',10,1,1)] if kind=='bread' else [('bakery_cart_timber',9,0,0),('bakery_wicker',8,1,0),('bakery_canopy',29,0,1)]
  for name,slot,col,row in specs:
   r=next((r for r in m['regions'] if r['name']==name),None)
   if r is None:
    assert slot not in [r['slot'] for r in m['regions']];x,y=slot%8*128,slot//8*128
    r=dict(id=max(r['id'] for r in m['regions'])+1,name=name,family='bakery',slot=slot,bounds=[x+4,y+4,x+124,y+124],sources={k:f'sources/{name}_{k}.png' for k in 'BNGM'});m['regions'].append(r)
    if slot in m['reserved_slots']:m['reserved_slots'].remove(slot)
   crop=(col*w//2,row*h//2,(col+1)*w//2,(row+1)*h//2);b=image.crop(crop).resize((480,480),Image.Resampling.LANCZOS)
   # Calm normals avoid mistaking painted highlights/shadows for physical relief.
   maps={'B':b,'N':Image.new('RGB',(480,480),(128,128,255)),'G':Image.new('RGB',(480,480),(24,)*3),'M':Image.new('RGB',(480,480),(0,)*3)}
   for k,im in maps.items():im.save(STAGE/'atlas'/r['sources'][k])
   provenance.append(dict(region=name,slot=slot,source=dest.relative_to(STAGE).as_posix(),source_sha256=sha(dest),source_dimensions=[w,h],crop=list(crop),basecolour='ImageGen original crop and resample; no procedural repaint',normal='calm flat tangent-space normal; painted lighting not interpreted as height',metal='0',gloss='24'))
 (STAGE/'atlas/manifest.json').write_text(json.dumps(m,indent=2));(STAGE/'atlas/sources/imagegen-r027/provenance.json').write_text(json.dumps(provenance,indent=2))
 subprocess.run([sys.executable,STAGE/'scripts/pack_bakery_additions.py'],check=True)
 shutil.copytree(STAGE/'textures',SOURCE/'textures',dirs_exist_ok=True);shutil.copytree(STAGE/'atlas/sources/imagegen-r027',SOURCE/'imagegen-sources',dirs_exist_ok=True)
 print('R027 IMAGEGEN PANELS STAGED')
if __name__=='__main__':main()
