"""Non-destructive revision-08 source delivery and concept comparison."""
import json,shutil,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
BASE=Path.home()/'Desktop/Codex/modern-windmill-v8-20261026';OUT=BASE/'export';NAME='CSC_BAKERS_Wind_Mill_Modern'
DEST=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/modern/revision-08-concept-roof'
checks=json.loads((OUT/'source-validation.json').read_text());assert checks['automated_pass']
changes=json.loads((BASE/'changes.json').read_text());assert hashlib.sha256(Path(changes['source']).read_bytes()).hexdigest()==changes['source_sha256']
assert json.loads((OUT/'installation.json').read_text())['installed']
DEST.mkdir(parents=True,exist_ok=False)
shutil.copy2(OUT/(NAME+'.blend'),DEST/(NAME+'.blend'));shutil.copytree(OUT/'textures',DEST/'textures')
for p in (BASE/'changes.json',BASE/'texture-provenance.json',OUT/'source-validation.json',OUT/'foundation-check.json',OUT/'native-parity.json'):shutil.copy2(p,DEST/p.name)
(DEST/'REVIEW.txt').write_text('Modern Wind Mill — revision 08\n\nCorrects revision 07: roof-coloured bargeboards with only a 0.6-unit timber underside, native darker Bakers_2 green ridge, reduced main/shelter/intake overhangs, and a taller silo cone (apex 88 to 95) with a smaller lip. The upper elevator and spout rise 7 units to keep the connection intact. Existing strong brick/window normals, intake, door removal and repaired masonry corners retained. User stock/silo-body placements and buried foundations preserved.\n\n'+str(checks['counts']['main_vertices'])+' exported vertices, above the advisory 2200 target. No validation errors. Native conversion parity and isolated cook passed. AE assembly/wiring and previous construction/pillaged geometry preserved. Live AE and game appearance remain to be reviewed.\n',encoding='utf-8')
left=Image.open(Path.home()/'Desktop/Codex/mills-modern-concepts-20261026/Wind_Mill_Modern_Flour_Mill_Concept.png').convert('RGB');right=Image.open(OUT/'modern_v8_concept_angle.png').convert('RGB')
sheet=Image.new('RGB',(3072,1096),'#f4f5f7');sheet.paste(left,(0,72));sheet.paste(right,(1536,72));draw=ImageDraw.Draw(sheet);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',34)
draw.text((36,17),'Concept reference',font=font,fill='#28302d');draw.text((1572,17),'Revision 08 — corrected roof trim and silo cap',font=font,fill='#28302d');sheet.save(BASE/'concept_modern_v8_comparison.png')
details=Image.new('RGB',(2048,1090),'#f4f5f7')
for i,(filename,label) in enumerate([('modern_v8_roof_detail.png','Green trim with a thin timber underside'),('modern_v8_silo_detail.png','Taller cone and connected spout')]):
    details.paste(Image.open(OUT/filename).convert('RGB'),(i*1024,66));ImageDraw.Draw(details).text((i*1024+28,15),label,font=font,fill='#28302d')
details.save(BASE/'modern_v8_details.png')
(BASE/'delivery.json').write_text(json.dumps({'master':str(DEST/(NAME+'.blend')),'comparison':str(BASE/'concept_modern_v8_comparison.png'),'details':str(BASE/'modern_v8_details.png'),'installed':True},indent=2));print(DEST)
