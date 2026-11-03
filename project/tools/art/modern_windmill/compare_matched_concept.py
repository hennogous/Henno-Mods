"""Place unaltered concept and camera-matched model render on equal-size panels."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
root=Path.home()/'Desktop/Codex';out=root/'modern-windmill-v5-20261026'
left=Image.open(root/'mills-modern-concepts-20261026/Wind_Mill_Modern_Flour_Mill_Concept.png').convert('RGB')
right=Image.open(out/'modern_v5_concept_angle.png').convert('RGB')
assert left.size==right.size==(1536,1024)
sheet=Image.new('RGB',(3072,1096),'#f4f5f7');sheet.paste(left,(0,72));sheet.paste(right,(1536,72))
d=ImageDraw.Draw(sheet);f=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',36)
d.text((40,14),'Approved concept',font=f,fill='#28302d');d.text((1576,14),'Modern model — matched concept angle',font=f,fill='#28302d')
sheet.save(out/'concept_model_matched_camera.png')
