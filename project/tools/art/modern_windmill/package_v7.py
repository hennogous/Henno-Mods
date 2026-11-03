"""Deliver the reviewed V7 source without overwriting Henno's V6 edits."""
import json,shutil,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path.home()/'Desktop/Codex/modern-windmill-v7-20261026';OUT=BASE/'export-final';NAME='CSC_BAKERS_Wind_Mill_Modern'
DEST=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/modern/revision-07-roof-intake'
checks=json.loads((OUT/'source-validation.json').read_text());assert checks['automated_pass']
changes=json.loads((BASE/'changes.json').read_text());assert hashlib.sha256(Path(changes['source']).read_bytes()).hexdigest()==changes['source_sha256']
assert json.loads((OUT/'installation.json').read_text())['installed']
DEST.mkdir(parents=True,exist_ok=False)
shutil.copy2(OUT/(NAME+'.blend'),DEST/(NAME+'.blend'));shutil.copytree(OUT/'textures',DEST/'textures')
for p in (BASE/'changes.json',BASE/'texture-provenance.json',OUT/'source-validation.json',OUT/'foundation-check.json',OUT/'native-parity.json'):
    shutil.copy2(p,DEST/p.name)
(DEST/'REVIEW.txt').write_text('Modern Wind Mill — revision 07\n\nBased on Henno\'s saved revision-06 model, with his silo, elevator, pipe, sacks, pallets and truck placements preserved.\n\nMain roof pitch reduced from 35.4 to 27.4 degrees. Straight roof profiles, bold timber ridge and thick timber barge boards/eave supports. Roof paint uses the Bakers_2 yellow-green palette. Open framed intake with a visible tapered hopper at the user-edited intake position. New dark timber window frames with substantial stone lintels/sills, strong registered normal relief, and stronger brick normals. Recess loading door removed. Entrance walls meet the exact tapered pier plane, internal caps removed and sharp masonry normals preserved. Geometry AO rebaked. Existing foundations still extend to -30.\n\n2,977 exported vertices / 1,933 triangles, above the advisory 2,200 target. No validation errors. Existing AE assembly preserved; intact geometry and textures updated. Earlier construction/pillaged geometry retained. Isolated cook passed; live AE/game review remains with Henno.\n\nPainted texture patches created with built-in ImageGen using the approved concept for styling and CSC_Atlas_B_BAKERS_2 for roof/timber colour; exact source and processing are recorded in texture-provenance.json.\n',encoding='utf-8')
left=Image.open(Path.home()/'Desktop/Codex/mills-modern-concepts-20261026/Wind_Mill_Modern_Flour_Mill_Concept.png').convert('RGB')
right=Image.open(OUT/'modern_v5_concept_angle.png').convert('RGB');assert left.size==right.size==(1536,1024)
sheet=Image.new('RGB',(3072,1096),'#f4f5f7');sheet.paste(left,(0,72));sheet.paste(right,(1536,72));draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',34)
draw.text((36,17),'Approved concept',font=font,fill='#28302d');draw.text((1572,17),'Revised model — Bakers_2 roof colours',font=font,fill='#28302d')
sheet.save(BASE/'concept_modern_v7_comparison.png')
details=Image.new('RGB',(2048,1090),'#f4f5f7')
for i,(filename,label) in enumerate([('modern_v7_entrance_roof.png','Roof, windows and entrance'),('modern_v7_intake.png','Open intake and tapered hopper')]):
    details.paste(Image.open(OUT/filename).convert('RGB'),(i*1024,66));ImageDraw.Draw(details).text((i*1024+28,15),label,font=font,fill='#28302d')
details.save(BASE/'modern_v7_details.png')
(BASE/'delivery.json').write_text(json.dumps({'master':str(DEST/(NAME+'.blend')),'comparison':str(BASE/'concept_modern_v7_comparison.png'),'details':str(BASE/'modern_v7_details.png'),'installed':True},indent=2))
print(DEST)
