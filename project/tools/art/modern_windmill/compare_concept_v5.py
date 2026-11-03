"""Arrange the approved concept and latest actual render without altering their content."""
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont,ImageOps
root=Path.home()/'Desktop/Codex'
sources=[root/'mills-modern-concepts-20261026/Wind_Mill_Modern_Flour_Mill_Concept.png',root/'modern-windmill-v5-20261026/modern_v5_icon_angle.png']
canvas=Image.new('RGB',(2560,1352),'#f4f5f7')
for index,path in enumerate(sources):
    im=Image.open(path).convert('RGB')
    im=ImageOps.contain(im,(1280,1280),Image.Resampling.LANCZOS)
    canvas.paste(im,(index*1280+(1280-im.width)//2,72+(1280-im.height)//2))
draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',34)
draw.text((36,14),'Approved concept',font=font,fill='#28302d')
draw.text((1316,14),'Modern model — revision 5',font=font,fill='#28302d')
dest=root/'modern-windmill-v5-20261026/concept_and_modern_model.png'
canvas.save(dest);print(dest)
