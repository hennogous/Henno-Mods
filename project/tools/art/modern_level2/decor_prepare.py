from pathlib import Path
from PIL import Image,ImageDraw
import shutil,json
O=Path.home()/'Desktop/Codex/modern-level2-v3-details-20261028';O.mkdir(exist_ok=True)
ART=Path.home()/'Desktop/Working Files/3D Art';base=ART/'Textures/CSC_Props_Modern/Current'
for d in ('textures','bakes','models','sources','review'): (O/d).mkdir(exist_ok=True)
shutil.copytree(ART/'Level 2/modern/revision-02-tailor-footprint/textures',O/'textures',dirs_exist_ok=True)
shutil.copytree(base/'textures',O/'textures',dirs_exist_ok=True)
guide=Image.new('RGB',(1024,512),(60,85,36));d=ImageDraw.Draw(guide)
d.rectangle((512,0,1023,511),fill=(65,83,60));d.rounded_rectangle((548,36,988,476),radius=24,fill=(221,209,161));guide.save(O/'Decor_Layout.png')
plan=json.loads((base/'atlas-plan.json').read_text())
occupied=set(plan['props']['slots'].values());assert not occupied.intersection({24,25})
(O/'decor-plan.json').write_text(json.dumps({'base_release':'2026-10-27_Modern_r004','surface_cells':{'24':'painted windowbox foliage and tiny yellow/ivory flowers','25':'blank cream sign face with dark green inset border'},'AO_allocations':{'CSC_ALL_Window_Box_Modern':[512,0,768,256],'CSC_ALL_Hanging_Sign_Modern':[768,0,1024,256]},'scope':'candidate props atlas only'},indent=2))
print(O)
