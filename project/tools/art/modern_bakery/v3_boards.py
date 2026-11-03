from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
O=Path.home()/'Desktop/Codex/modern-bakery-v3-20261028';font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',31);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',23)
def board(name,pairs,footer):
 out=Image.new('RGB',(2200,1200),(27,31,36));d=ImageDraw.Draw(out)
 for i,(label,file) in enumerate(pairs):
  im=Image.open(O/'review'/file).convert('RGBA');out.paste(im,(1100*i,60),im);d.text((1100*i+35,18),label,font=font,fill=(240,230,211))
 d.text((35,1164),footer,font=small,fill=(178,190,198));out.save(O/name)
board('Bakery_V3_Historical_Comparison.png',[('HISTORICAL L2 REFERENCE','historical.png'),('MODERN BAKERY V3','combined.png')],'Same camera, ground datum and scale | ridge height matched | your dormer and chimney edits retained')
board('Bakery_V3_Window_Depth_Trial.png',[('FLAT PAINTED WINDOW','windows-flat.png'),('INSET INTERIOR + GLOSS / OPACITY','windows-depth.png')],'Blender comparison, emission disabled | native opacity coverage still needs AE / in-game review')
board('Bakery_V3_Bread_Display.png',[('PAINTED BREAD TRAYS / FINAL MATERIAL','display-combined.png'),('RELIEF ONLY / SAME GEOMETRY','display-normal-A.png')],'Round loaves, baguettes, rolls and croissants | shallow tray geometry + painted colour, normals and contact AO')
print('V3_BOARDS_READY')
