"""Remove inherited roof/window relief; register structural normals to new paint."""
import json,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029';T=O/'textures';A=Path.home()/'Desktop/Working Files/3D Art'
paint=Image.open(O/'sources/L3_Modern_Painted.png').convert('RGB').resize((1024,1024));h=Image.new('L',(1024,1024),70);d=ImageDraw.Draw(h)
# Roof seams traced on the final generated art, not the guide positions.
for x in (449,504,559,614,668,721,770,823):d.line((x,45,x,410),fill=200,width=4)
for x in (92,131,190,235,279):d.line((x,150 if x not in (190,) else 120,x,304),fill=200,width=4)
for x in (872,915,956,996):d.line((x,507,x,891),fill=200,width=4)
# Main plaster, cornices and individual quoins use broad shallow bevels.
for rect in ((4,353,412,369),(1,618,414,640),(414,444,852,460),(418,469,810,481),(10,1002,411,1012),(420,15,863,40)):
 d.rectangle(rect,fill=150)
for row,y in enumerate(range(387,1000,58)):
 d.rounded_rectangle((359 if row%2==0 else 377,y,411,y+46),radius=3,fill=135)
# Entire windows are rebuilt so obsolete dense historical grids cannot remain.
for rect,xs,ys in [((60,438,143,553),(101,),(465,501,540)),((217,438,303,553),(261,),(465,501,540)),((322,62,386,124),(349,),(91,119))]:
 d.rectangle(rect,fill=0);d.rectangle(rect,outline=205,width=7)
 for x in xs:d.line((x,rect[1],x,rect[3]),fill=205,width=5)
 for y in ys:d.line((rect[0],y,rect[2],y),fill=205,width=5)
for x0,x1 in ((467,577),(637,757)):
 center=(x0+x1)//2;top=716 if x0==467 else 730;spring=766
 d.rectangle((x0,spring,x1,962 if x0==467 else 834),fill=0);d.pieslice((x0,top,x1,top+2*(spring-top)),180,360,fill=0)
 d.line((x0,spring,x0,958 if x0==467 else 834),fill=205,width=5);d.line((x1,spring,x1,958 if x0==467 else 834),fill=205,width=5)
 d.arc((x0,top,x1,top+2*(spring-top)),180,360,fill=205,width=5)
 for x in ((501,540) if x0==467 else (698,)):d.line((x,top,x,960 if x0==467 else 834),fill=205,width=5)
 for y in ((786,858,944) if x0==467 else (785,833)):d.line((x0,y,x1,y),fill=205,width=5)
for rect in ((640,840,753,964),(595,597,784,620),(206,529,314,550),(449,500,789,541)):d.rectangle(rect,outline=145,width=5)
# Use the actual painted green frame masks, restricted to known window patches.
# This is semantic shape registration, not luminance/noise converted into bump.
rgb=np.asarray(paint,float);green=(rgb[:,:,1]>rgb[:,:,0]*1.07)&(rgb[:,:,1]>rgb[:,:,2]*1.07)
ha=np.array(h)
for x0,y0,x1,y1 in ((44,420,152,567),(207,420,313,566),(308,52,392,129),(456,704,583,969),(632,718,763,839)):
 piece=rgb[y0:y1,x0:x1];light=piece.mean(axis=2);patch=np.full(light.shape,70,dtype=np.uint8);patch[light<140]=25;patch[green[y0:y1,x0:x1]]=205;ha[y0:y1,x0:x1]=patch
h=Image.fromarray(ha)
a=np.asarray(h.filter(ImageFilter.GaussianBlur(1.3)),float)/255*1.0;dy,dx=np.gradient(a,100/1024,100/1024);n=np.stack((-dx,dy,np.ones_like(dx)),axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True);normal=Image.fromarray(np.uint8((n*.5+.5)*255))
base=Image.open(T/'CSC_Atlas_Modern_N.png').convert('RGB');base.paste(normal.resize((512,512),Image.Resampling.LANCZOS),(0,512));base.save(T/'CSC_Atlas_Modern_N.png');h.save(O/'sources/L3_Final_Registered_Relief.png')
# Glass opacity uses colour-classified glass only, preserving green mullions.
p=np.asarray(paint,float);glass=(p[:,:,2]>p[:,:,1]*.94)&(p[:,:,1]>p[:,:,0]*1.03)&(p.mean(axis=2)>65)
mask=Image.new('L',(1024,1024));md=ImageDraw.Draw(mask);md.rectangle((460,705,582,964),fill=255);mask=np.asarray(mask)>0
o=np.full((1024,1024),255,dtype=np.uint8);o[glass&mask]=24
# Door upper pane is amber; explicitly keep the painted green frame intact.
for x0,x1 in ((650,692),(704,743)):
 o[756:779,x0:x1]=24;o[792:830,x0:x1]=24
op=Image.open(T/'CSC_Atlas_Modern_O.png').convert('RGB');op.paste(Image.fromarray(o).convert('RGB').resize((512,512)),(0,512));op.save(T/'CSC_Atlas_Modern_O.png')
# Exterior upper lights stay on the established quarter E; rooms own their new E.
e=np.zeros((1024,1024,3),dtype=np.uint8)
for rect in ((76,456,127,540),(235,456,286,535),(334,72,374,115)):
 x0,y0,x1,y1=rect;src=p[y0:y1,x0:x1]/255;light=(src[:,:,0]>src[:,:,1]*.96)&(src[:,:,0]>src[:,:,2]*1.15);e[y0:y1,x0:x1]=np.uint8(src*np.array([.6,.48,.31])*light[:,:,None]*255)
ep=Image.open(T/'CSC_Atlas_Modern_E_BAKERS.png').convert('RGB');ep.paste(Image.fromarray(e).resize((256,256)),(0,256));ep.save(T/'CSC_Atlas_Modern_E_BAKERS.png')
for ch in ('B','N','G','M'):
 prop=Image.open(T/f'CSC_Props_Modern_01_{ch}.png').convert('RGB')
 for slot,rect in ((44,(653,852,674,885)),(45,(550,810,568,844))):
  crop=paint.crop(rect).resize((128,128)) if ch=='B' else Image.new('RGB',(128,128),(128,128,255) if ch=='N' else (185,)*3 if ch=='G' and slot==45 else (45,)*3 if ch=='G' else (0,)*3)
  prop.paste(crop,(slot%8*128,slot//8*128))
 prop.save(T/f'CSC_Props_Modern_01_{ch}.png')
for folder in (A/'Level 3/modern/revision-01-garden',A/'BAKERS/Cafe/modern/revision-01-garden'):
 for name in ('CSC_Atlas_Modern_N.png','CSC_Atlas_Modern_O.png','CSC_Atlas_Modern_E_BAKERS.png'):shutil.copy2(T/name,folder/'textures'/name)
print('REGISTERED_NORMALS_AND_GLASS_REFINED')
