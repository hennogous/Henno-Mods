"""Record upstairs-only emissive review; comparison deliberately excludes emission."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
O=Path.home()/'Desktop/Codex/modern-normal-correction-20261027';E=O/'emissive-r007'
im=Image.open(E/'library/textures/CSC_Atlas_Modern_E.png').convert('RGB')
panes=[im.getpixel((x,y)) for x,y in [(107,43),(116,43),(107,52),(116,52)]]
assert panes==[(205,140,60)]*4,panes
assert im.getpixel((5,250))==(0,0,0)
for ident in ('CSC_Level_1_S_Modern','CSC_BAKERS_Water_Mill_Modern'):
 r=json.loads((E/'masters'/ident/'uv3-check.json').read_text());assert len(r['upstairs_lit'])==5
 assert len(r['ground_floor_dark'])==(1 if ident=='CSC_Level_1_S_Modern' else 0)
p=E/'review/Modern_Soft_Glow.png'
(E/'visual-review.json').write_text(json.dumps({'reviewed':True,'image':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'findings':'All four upstairs panes have equal warm emission. Ground-floor window is dark. Frames remain dark. Separate diagnostic only; final comparison has all emission disabled.','pane_samples':panes,'in_game_tested':False},indent=2))
canvas=Image.new('RGBA',(2048,1100),(26,30,33,255))
for x,ident in [(0,'CSC_BAKERS_Wind_Mill'),(1024,'CSC_BAKERS_Wind_Mill_Modern')]:
 im=Image.open(O/'images'/(ident+'_Comparison.png')).convert('RGBA');assert im.size==(1024,1024);canvas.alpha_composite(im,(x,60))
d=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',32)
d.text((40,20),'Historical Wind Mill',font=font,fill=(227,227,218));d.text((1064,20),'Modern Wind Mill',font=font,fill=(227,227,218));d.line((1024,16,1024,1080),fill=(65,71,74),width=1)
canvas.convert('RGB').save(O/'images/Historical_Modern_Wind_Mill_Dark_No_Emission.png')
