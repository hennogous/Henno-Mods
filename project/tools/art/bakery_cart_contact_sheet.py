from PIL import Image,ImageDraw
from bakery_props_atlas import OUT
canvas=Image.new('RGB',(1200,1320),(223,221,215));d=ImageDraw.Draw(canvas)
for i,label in enumerate(['hero','top','rear','side']):
 im=Image.open(OUT/f'cart-{label}.png').convert('RGB');canvas.paste(im,((i%2)*600,(i//2)*630));d.text(((i%2)*600+20,(i//2)*630+602),label.title(),fill='black')
small=Image.open(OUT/'cart-hero.png').convert('RGB').resize((110,110),Image.Resampling.LANCZOS);canvas.paste(small,(1020,1190));d.text((860,1250),'Reduced scale',fill='black');canvas.save(OUT/'Cart_Review_Sheet.jpg',quality=95)
