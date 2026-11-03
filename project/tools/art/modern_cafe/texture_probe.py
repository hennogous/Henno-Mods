from pathlib import Path
from PIL import Image,ImageDraw
import numpy as np
O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029'
im=Image.open(O/'sources/L3_Modern_Painted.png').convert('RGB').resize((1024,1024));a=np.array(im);profile=a[140:360,420:865].mean(axis=(0,2));peaks=[i for i in range(15,len(profile)-15) if profile[i]==max(profile[i-15:i+16])];print('main roof highlights',[i+420 for i in peaks])
d=ImageDraw.Draw(im)
for n in range(0,1024,64):d.line((n,0,n,1024),fill='#ff0033',width=1);d.line((0,n,1024,n),fill='#ff0033',width=1);d.text((n+2,685),str(n),fill='white');d.text((422,n+2),str(n),fill='white')
im.save(O/'sources/L3_Coordinate_Diagnostic.png')
