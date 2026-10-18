"""Final paint-only Bakery refinement; no scored topology or wicker strands."""
from bakery_props_atlas import *
from PIL import Image,ImageDraw,ImageFilter
def main():
 m=json.loads((STAGE/'atlas/manifest.json').read_text())
 for name in ['bakery_brick','bakery_wicker','bakery_round_crust','bakery_long_crust']:
  n=480;h=Image.new('L',(n,n),140);dh=ImageDraw.Draw(h)
  if name=='bakery_brick':
   b=Image.new('RGB',(n,n),(139,104,74));d=ImageDraw.Draw(b)
   for row in range(16):
    for col in range(-1,24):
     x=col*20+(row%2)*10;y=row*30;s=(row*7+col*11)%15
     d.rounded_rectangle((x+1,y+1,x+19,y+28),radius=2,fill=(165+s,82+s//2,49+s//3));dh.rectangle((x+1,y+1,x+19,y+28),fill=160)
  elif name=='bakery_wicker':
   b=Image.new('RGB',(n,n),(112,75,38));d=ImageDraw.Draw(b)
   for row in range(30):
    for col in range(32):
     x=col*15;y=row*16
     if (row+col)%2:
      d.rectangle((x+1,y+1,x+13,y+14),fill=(174,132,77));d.line((x+2,y+3,x+12,y+3),fill=(201,158,95),width=2);dh.rectangle((x+1,y+1,x+13,y+14),fill=165)
     else:d.rectangle((x+4,y,x+10,y+16),fill=(150,106,55));d.line((x+5,y,x+5,y+16),fill=(180,137,79),width=2)
  else:
   yy,xx=np.mgrid[:n,:n];rad=np.sqrt((xx-n/2)**2+(yy-n/2)**2)/(n*.7);v=-25*rad+4*np.sin(xx*.03)*np.cos(yy*.02);a=np.empty((n,n,3));a[:]=(208,143,67);a+=v[:,:,None];b=Image.fromarray(np.clip(a,0,255).astype('uint8'));d=ImageDraw.Draw(b)
   lines=[(100,160,340,270),(140,80,380,190),(80,260,320,370)] if name=='bakery_long_crust' else [(105,120,350,350),(350,110,115,350)]
   for x0,y0,x1,y1 in lines:
    dx=x1-x0;dy=y1-y0;length=math.hypot(dx,dy);nx=-dy/length;ny=dx/length
    for w,col,hh in [(15,(132,77,32),85),(10,(238,202,137),100)]:
     shape=[]
     for sign,ts in [(1,np.linspace(0,1,16)),(-1,np.linspace(1,0,16))]:
      for t in ts:
       width=w*math.sin(math.pi*t)**.65;wiggle=2*math.sin(t*29);shape.append((x0+dx*t+nx*(width*sign+wiggle),y0+dy*t+ny*(width*sign+wiggle)))
     d.polygon(shape,fill=col);dh.polygon(shape,fill=hh)
   b=b.filter(ImageFilter.GaussianBlur(.6))
  ha=np.array(h.filter(ImageFilter.GaussianBlur(.8)),dtype=float);gy,gx=np.gradient(ha/255);norm=np.dstack((-gx*1.2,-gy*1.2,np.ones_like(gx)));norm/=np.linalg.norm(norm,axis=2)[:,:,None]
  maps={'B':b,'N':Image.fromarray(((norm*.5+.5)*255).astype('uint8'))};r=next(r for r in m['regions'] if r['name']==name);x,y=r['slot']%8*128,r['slot']//8*128
  for k,im in maps.items():
   im.save(STAGE/'atlas'/r['sources'][k]);path=STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png';a=Image.open(path).convert('RGB');patch=im.resize((120,120),Image.Resampling.LANCZOS);padded=Image.fromarray(np.pad(np.array(patch),((4,4),(4,4),(0,0)),mode='edge'));a.paste(padded,(x,y));a.save(path)
 shutil.copytree(STAGE/'textures',SOURCE/'textures',dirs_exist_ok=True)
if __name__=='__main__':main()
