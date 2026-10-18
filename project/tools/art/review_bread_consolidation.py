from bakery_props_atlas import *
from PIL import Image,ImageDraw
m=json.loads((STAGE/'atlas/manifest.json').read_text());sheet=Image.new('RGB',(1000,540),(226,224,218));draw=ImageDraw.Draw(sheet)
for i,slot in enumerate([61,10,30,62]):
 x,y=slot%8*128,slot//8*128;tile=Image.open(STAGE/'textures/CSC_Props_Shared_01_B.png').crop((x,y,x+128,y+128)).resize((240,240));sheet.paste(tile,(i*250,25));draw.text((i*250+5,5),str(slot)+(' mixed bread' if slot==61 else ' FREE'),fill='black')
normal=Image.open(STAGE/'textures/CSC_Props_Shared_01_N.png');x,y=61%8*128,61//8*128;sheet.paste(normal.crop((x,y,x+128,y+128)).resize((240,240)),(0,290));draw.text((5,270),'61 aligned N, runtime strength1',fill='black');draw.text((260,290),'One occupied bread cell. Three reclaimed cells.',fill='black');draw.text((260,315),'Top75%: mixed crown. Lower25%: stacked shoulder loaves.',fill='black');draw.text((260,340),'410 native triangles across three trays and cart.',fill='black');sheet.save(OUT/'Bread_Atlas_Consolidation.jpg',quality=95)
shutil.copy2(OUT/'native-bread-atlas-usage.json',OUT/'native-bread-atlas-usage-before.json')
