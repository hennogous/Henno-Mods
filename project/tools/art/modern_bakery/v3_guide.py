from pathlib import Path
from PIL import Image,ImageDraw
O=Path.home()/'Desktop/Codex/modern-bakery-v3-20261028'
im=Image.new('RGB',(1536,1024),'#c3b08a');d=ImageDraw.Draw(im)
for col in range(3):
 x=col*512;d.rectangle((x+8,8,x+503,503),fill='#383d3f');d.rectangle((x+25,25,x+486,486),fill='#655642')
 if col==0:
  for a,b,r in [(140,165,90),(355,180,105),(220,365,94)]:d.ellipse((x+a-r,b-r,x+a+r,b+r),fill='#c78a43',outline='#9c602b',width=6)
 elif col==1:
  for a in (95,255,415):d.rounded_rectangle((x+a-52,55,x+a+52,457),radius=49,fill='#cd984d')
 else:
  for a in (115,285,425):
   for b in (140,355):d.ellipse((x+a-59,b-75,x+a+59,b+75),fill='#c28337')
for c,color in enumerate(('#b98f58','#8d997b','#927452')):
 x=c*512;d.rectangle((x,512,x+511,1023),fill=color)
 if c==0:
  for y in (635,785,935):d.rectangle((x+12,y,x+499,y+14),fill='#644c35')
 elif c==1:
  for y in range(560,1024,80):d.line((x,y,x+511,y),fill='#747e64',width=3)
 else:
  for y in range(550,1024,64):d.line((x,y,x+511,y),fill='#66533e',width=3)
im.save(O/'sources/Bread_Interior_Guide.png')
print(O/'sources/Bread_Interior_Guide.png')
