"""Package the validated main-house review separately from the installed v1 asset."""
import json,sys,shutil,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
OUT=Path(sys.argv[1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
report=json.loads((OUT/'house-review-report.json').read_text());validation=json.loads((OUT/'source-validation.json').read_text())
assert validation['automated_pass'] and validation['error_count']==0
original=Path(report['original_source']);assert hashlib.sha256(original.read_bytes()).hexdigest()==report['original_sha256']
dest=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/modern/revision-02-house'
dest.mkdir(parents=True,exist_ok=True)
for p in [OUT/(ASSET+'.blend'),OUT/'house-review-report.json',OUT/'source-validation.json',OUT/'texture-provenance-v2.json']:
    target=dest/p.name
    if target.exists():assert target.read_bytes()==p.read_bytes(),'Existing revision differs: '+str(target)
    shutil.copy2(p,target)
shutil.copytree(OUT/'textures',dest/'textures',dirs_exist_ok=True)
(dest/'REVIEW.txt').write_text('Modern Wind Mill — revision 02: main building review\n\nOriginal silhouette and footprint guide: '+str(original)+'\n\nRebuilt architectural shell: full projecting gabled shelter, regular lower masonry, concrete arched opening, buff-brick upper storey, green sheet roofs and structural supports. Small details are painted and use aligned technical maps. No modeled roof seams, masonry joints, rivets or window mullions.\n\nSilo and stock composition are deferred until this house direction is reviewed. This file is not the installed runtime asset; the prior v1 installation has not been replaced.\n\nExport count: '+str(report['export_vertices'])+' vertices. Saved-source validation passed.\n',encoding='utf-8')
# Layout only: unaltered actual Blender renders, identical camera and scale.
left=Image.open(OUT/'original_house.png').convert('RGB');right=Image.open(OUT/'modern_v2_house.png').convert('RGB')
sheet=Image.new('RGB',(2048,1100),'#f4f5f7');sheet.paste(left,(0,76));sheet.paste(right,(1024,76));draw=ImageDraw.Draw(sheet)
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',32)
draw.text((48,18),'Original building',font=font,fill='#28302d');draw.text((1072,18),'Modern revision — main building',font=font,fill='#28302d')
sheet.save(OUT/'main_building_comparison.png')
(OUT/'review-package.json').write_text(json.dumps({'master':str(dest/(ASSET+'.blend')),'comparison':str(OUT/'main_building_comparison.png'),'original_unchanged':True,'source_validation_passed':True,'runtime_updated':False},indent=2))
print('V2_REVIEW_PACKAGED',dest)
