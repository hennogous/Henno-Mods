from bakery_props_atlas import *
m=json.loads((STAGE/'atlas/manifest.json').read_text());m['normal_source']='r030 relief retained except r031 guide-aligned8x16 masonry and one mixed bread semantic height/score mask; reclaimed10/30/62 flat. Runtime strength1.';m['production_sha256']={k:sha(STAGE/'textures'/('CSC_Props_Shared_01_'+k+'.png')) for k in 'BNGM'};(STAGE/'atlas/manifest.json').write_text(json.dumps(m,indent=2))
for name in ['paint_bakery_revision07.py','paint_bread_revision07.py','remap_bakery_revision07.py','remap_bread_revision07.py']:
 for target in [STAGE/'atlas/sources/imagegen-r031',SOURCE/'art-provenance/imagegen-r031']:shutil.copy2(ROOT/'project/tools/art'/name,target/name)
