"""Compose actual Blender renders for review; no generated model imagery."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import json
O=Path.home()/'Desktop/Codex/modern-bakery-v2-20261028'
OLD=Path.home()/'Desktop/Codex/modern-bakery-v1-20261028'
font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',32)
small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',24)
def board(name,items,footer):
 out=Image.new('RGB',(2200,1200),(27,31,36));d=ImageDraw.Draw(out)
 for i,(label,path) in enumerate(items):
  im=Image.open(path).convert('RGBA');out.paste(im,(i*1100,60),im)
  d.text((i*1100+40,20),label,font=font,fill=(240,230,211))
 d.text((40,1162),footer,font=small,fill=(178,190,198));out.save(O/name)
board('Bakery_V2_Standard_and_Delivery.png',[
 ('BAKERY V2  /  STANDARD',O/'review/combined.png'),
 ('BAKERY V2  /  MARKET DELIVERY (_2)',O/'review/delivery.png')],
 'Actual Blender renders | same camera and scale | emission disabled')
board('Bakery_V2_Footprint_Comparison.png',[
 ('V1  /  LONG SIDE AND REAR EXTENSION',OLD/'review/top.png'),
 ('V2  /  SHORT SHELTER RETURN',O/'review/top.png')],
 'Orthographic top views | same scale | main building envelope retained')
print('REVIEW_BOARDS_READY')
