from PIL import Image,ImageDraw
from pathlib import Path
O=Path.home()/'Desktop/Codex/modern-bakery-v2-20261028'
im=Image.new('RGB',(1536,1024),'#d9ceb1');d=ImageDraw.Draw(im)
# Orthographic surface templates matched to the truck body profiles.
d.rectangle((0,0,511,511),fill='#637e54');d.rectangle((45,45,467,218),fill='#354b55');d.rectangle((55,250,457,420),fill='#6c8558');d.rectangle((135,310,377,418),fill='#303d36')
for x in (66,386):d.ellipse((x,302,x+60,362),fill='#e3d5a9')
d.rectangle((32,447,480,475),fill='#a2aaa4')
d.rectangle((512,0,1023,511),fill='#637e54');d.polygon([(560,220),(624,45),(976,45),(976,235)],fill='#304a53');d.rectangle((600,263,969,455),outline='#384f38',width=6);d.rectangle((866,283,940,300),fill='#b7b79e')
d.rectangle((1024,0,1535,511),fill='#ded4b4');d.rectangle((1040,16,1520,496),outline='#789365',width=10);d.ellipse((1144,155,1414,354),fill='#b87836')
for x in (1210,1280,1350):d.line((x,204,x+20,295),fill='#efd9a9',width=20)
d.rectangle((0,512,511,1023),fill='#343b37');d.ellipse((34,546,478,990),fill='#242b28',outline='#495047',width=16);d.ellipse((127,639,385,897),fill='#a8ac9f',outline='#5f695c',width=18);d.ellipse((206,718,306,818),fill='#657d52')
b=Image.open(O/'textures/CSC_Atlas_Modern_B_BAKERS.png').convert('RGB')
for slot,pos in [(5,(512,512)),(6,(1024,512))]:
 x=512+slot%4*128;y=slot//4*128;patch=b.crop((x,y,x+128,y+128)).resize((512,512),Image.Resampling.NEAREST);im.paste(patch,pos)
im.save(O/'sources/Truck_and_Windows_Guide.png')
print('GUIDE_READY')
