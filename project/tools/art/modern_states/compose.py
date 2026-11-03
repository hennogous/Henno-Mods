from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
O=Path.home()/'Desktop/Codex/modern-l1-states-20261028';W=1800;H=1940
im=Image.new('RGB',(W,H),(24,27,32));d=ImageDraw.Draw(im);font=lambda s:ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',s)
d.text((36,18),'Modern Level 1 — updated construction and pillage states',font=font(34),fill=(239,230,208))
for i,name in enumerate(('WORKED','CONSTRUCTION','PILLAGED')):d.text((i*600+36,78),name,font=font(25),fill=(187,199,205))
for j,(ident,label) in enumerate((('CSC_Level_1_S_Modern','Reusable building + complete shelter'),('CSC_BAKERS_Wind_Mill_Modern','Wind Mill — separate silo shell'),('CSC_BAKERS_Water_Mill_Modern','Water Mill — shared shell + river foundation'))):
 y=125+j*590;d.text((36,y),label,font=font(25),fill=(229,218,193))
 for i,state in enumerate(('Worked','Construction','Pillaged')):
  a=Image.open(O/'review'/ident/state/'render.png').convert('RGBA').resize((580,580),Image.Resampling.LANCZOS);im.paste(a,(i*600+10,y+25),a)
d.text((36,1900),'Saved-AST geometry review • emission off • game burn shading and effects are not simulated',font=font(21),fill=(170,179,186));im.save(O/'Modern_L1_State_Comparison.png')
# Compact visual evidence for the scaffold question.
canvas=Image.new('RGB',(1200,670),(24,27,32));d=ImageDraw.Draw(canvas)
for i,(ident,label) in enumerate((('DIS_COM_Market_Modern','Firaxis Modern Market — Construction'),('PROP_Scaffold_A','Firaxis reusable Scaffold A'))):
 a=Image.open(O/'scaffold-survey'/ident/'render.png').convert('RGBA').resize((580,580),Image.Resampling.LANCZOS);canvas.paste(a,(i*600+10,65),a);d.text((i*600+20,22),label,font=font(23),fill=(239,230,208))
canvas.save(O/'Firaxis_Modern_Scaffolds.png')
print('COMPOSED')
