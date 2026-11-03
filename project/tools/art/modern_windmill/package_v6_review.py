import json,shutil
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path.home()/'Desktop';out=root/'Codex/modern-windmill-v6-20261026'
dest=root/'Working Files/3D Art/BAKERS/Wind Mill/modern/revision-06-concept-refinement';asset='CSC_BAKERS_Wind_Mill_Modern'
v=json.loads((out/'source-validation.json').read_text());assert v['automated_pass'] and v['error_count']==0
report=json.loads((out/'assembly-review-report.json').read_text());report['export_vertices']=v['counts']['main_vertices']
(out/'assembly-review-report.json').write_text(json.dumps(report,indent=2))
shutil.copy2(out/'modern_v5_concept_angle.png',out/'modern_v6_concept_angle.png')
dest.mkdir(parents=True,exist_ok=True)
for name in (asset+'.blend','source-validation.json','assembly-review-report.json','texture-provenance.json','placement-foundation-check.json'):
    target=dest/name
    if target.exists():assert target.read_bytes()==(out/name).read_bytes(),'Existing revision differs'
    shutil.copy2(out/name,target)
shutil.copytree(out/'textures',dest/'textures',dirs_exist_ok=True)
(dest/'REVIEW.txt').write_text('Modern Wind Mill — revision 06\n\nStraight lighter roofs without sweep; broader silo at the exact historical tower position; flatter silo cap; rounded transfer pipe and texture-authored elevator casing. Visible sack/pallet/hand-truck loading scene and compact intake housing.\n\nBattered structural foundations extend to -30. Painted material repeats use consistent 8x4 bricks, 14x8 foundation blocks and 8-unit roof seam spacing. Fresh built-in ImageGen artwork; registered structural normals, material masks and geometry-baked AO. No modeled joints, rivets, roof seams or window mullions.\n\n'+str(report['export_vertices'])+' exported vertices / 1769 triangles: above the 2200 advisory target, no validation errors. This remains a review master; runtime installation has not been replaced.\n',encoding='utf-8')
left=Image.open(root/'Codex/mills-modern-concepts-20261026/Wind_Mill_Modern_Flour_Mill_Concept.png').convert('RGB');right=Image.open(out/'modern_v5_concept_angle.png').convert('RGB')
assert left.size==right.size==(1536,1024)
sheet=Image.new('RGB',(3072,1096),'#f4f5f7');sheet.paste(left,(0,72));sheet.paste(right,(1536,72))
d=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',36)
d.text((40,14),'Approved concept',font=font,fill='#28302d');d.text((1576,14),'Refined modern model — revision 6',font=font,fill='#28302d')
sheet.save(out/'concept_modern_v6_comparison.png')
(out/'review-package.json').write_text(json.dumps({'master':str(dest/(asset+'.blend')),'comparison':str(out/'concept_modern_v6_comparison.png'),'runtime_installed':False},indent=2));print(dest)
