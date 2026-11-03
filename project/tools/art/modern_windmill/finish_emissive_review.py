"""Record inspected render evidence and assemble the requested dark comparison."""
from pathlib import Path
import json,hashlib
from PIL import Image,ImageDraw,ImageFont
O=Path.home()/'Desktop/Codex/modern-normal-correction-20261027'
e=O/'emissive';p=e/'review/Modern_Soft_Glow.png'
(e/'visual-review.json').write_text(json.dumps({'reviewed':True,'image':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'findings':'Warm glazing remains confined to panes; window frames and masonry stay legible. Faint emission-only halo, no bloom applied to roofs or silo. Matched historical camera maintained.','preview_only':'Blender emission strength 2 with emission-pass halo addition 0.12; engine bloom not verified.','in_game_tested':False},indent=2))
canvas=Image.new('RGBA',(2048,1100),(26,30,33,255))
for x,f in [(0,O/'images/CSC_BAKERS_Wind_Mill_Comparison.png'),(1024,p)]:
 im=Image.open(f).convert('RGBA');assert im.size==(1024,1024);canvas.alpha_composite(im,(x,60))
d=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',32)
d.text((40,20),'Historical Wind Mill',font=font,fill=(227,227,218));d.text((1064,20),'Modern Wind Mill',font=font,fill=(227,227,218));d.line((1024,16,1024,1080),fill=(65,71,74),width=1)
canvas.convert('RGB').save(O/'images/Historical_Modern_Wind_Mill_Dark.png')
