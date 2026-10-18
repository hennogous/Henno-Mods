"""User-directed r026: smaller bricks, 40% larger dough; peel stays independent."""
from bakery_props_atlas import *
from PIL import Image,ImageDraw,ImageFilter
import subprocess,importlib.util,xml.etree.ElementTree as ET
def prepare():
 assert RELEASE.endswith('r026');OUT.mkdir(parents=True,exist_ok=True);assert not STAGE.exists();shutil.copytree(LIB/'Current',STAGE)
 prior=SOURCE.parent/'revision-01-prop-kit';shutil.copytree(prior,SOURCE)
 for name in ['CSC_BAKERS_Peel','CSC_BAKERS_Bread_Basket_Round','CSC_BAKERS_Bread_Basket_Oval','CSC_BAKERS_Bread_Basket_Long','CSC_BAKERS_Bread_Cart','CSC_BAKERS_Oven_v2']:
  for suffix in ['.cn6','.fgx','.geo','.ast','-roundtrip.cn6','-export.json','-validation.json']:
   src=OUT.parent/(name+suffix)
   if src.exists():shutil.copy2(src,OUT/src.name)
 m=json.loads((STAGE/'atlas/manifest.json').read_text());r=next(r for r in m['regions'] if r['name']=='bakery_brick');n=480;b=Image.new('RGB',(n,n),(139,104,74));d=ImageDraw.Draw(b);h=Image.new('L',(n,n),140);dh=ImageDraw.Draw(h)
 # 40 columns x 24 courses: 1.67x horizontal and 1.5x vertical density.
 for row in range(24):
  for col in range(-1,40):
   x=col*12+(row%2)*6;y=row*20;s=(row*7+col*11)%15
   d.rounded_rectangle((x+1,y+1,x+11,y+18),radius=1,fill=(165+s,82+s//2,49+s//3));dh.rectangle((x+1,y+1,x+11,y+18),fill=160)
 ha=np.array(h.filter(ImageFilter.GaussianBlur(.5)),dtype=float);gy,gx=np.gradient(ha/255);normal=np.dstack((-gx*1.2,-gy*1.2,np.ones_like(gx)));normal/=np.linalg.norm(normal,axis=2)[:,:,None]
 for k,im in {'B':b,'N':Image.fromarray(((normal*.5+.5)*255).astype('uint8'))}.items():
  im.save(STAGE/'atlas'/r['sources'][k]);a=Image.open(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB');patch=im.resize((120,120),Image.Resampling.LANCZOS);a.paste(Image.fromarray(np.pad(np.array(patch),((4,4),(4,4),(0,0)),mode='edge')),(r['slot']%8*128,r['slot']//8*128));a.save(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png')
 shutil.copytree(STAGE/'textures',SOURCE/'textures',dirs_exist_ok=True)
 print('R026 STAGED')
def paint_stock():
 m=json.loads((STAGE/'atlas/manifest.json').read_text())
 specs=[('bakery_round_crust','round'),('bakery_long_crust','long'),('bakery_oval_bread','oval')]
 for name,kind in specs:
  r=next((r for r in m['regions'] if r['name']==name),None)
  if r is None:
   slot=30;assert slot not in [r['slot'] for r in m['regions']];x,y=slot%8*128,slot//8*128
   r=dict(id=max(r['id'] for r in m['regions'])+1,name=name,family='bakery',slot=slot,bounds=[x+4,y+4,x+124,y+124],sources={k:f'sources/{name}_{k}.png' for k in 'BNGM'});m['regions'].append(r);m['reserved_slots'].remove(slot)
  n=480;yy,xx=np.mgrid[:n,:n]
  wicker=Image.open(STAGE/'atlas/sources/bakery_wicker_B.png').convert('RGB').resize((n,n),Image.Resampling.LANCZOS)
  a=np.array(wicker,dtype=float)*.46;height=np.zeros((n,n),float)
  positions=[(150,170,94,94),(330,170,94,94),(240,330,98,94)] if kind=='round' else [(140,240,58,165 if kind=='long' else 118),(240,230,58,165 if kind=='long' else 118),(340,240,58,165 if kind=='long' else 118)]
  for cx,cy,rx,ry in positions:
   shadow=((xx-cx-7)/(rx*1.05))**2+((yy-cy-12)/(ry*1.05))**2
   dark=(np.clip(1-shadow,0,1)*.7);a*=1-dark[:,:,None]
   nx=(xx-cx)/rx;ny=(yy-cy)/ry;rad=nx**2+ny**2;inside=rad<1;dome=np.sqrt(np.clip(1-rad,0,1))
   lit=np.clip(-.34*nx-.44*ny+.78*dome,0,1);rim=np.clip((1-rad)*10,0,1)
   for k,(base,gain) in enumerate([(118,122),(51,132),(16,83)]):a[:,:,k][inside]=((base+gain*lit)*(.7+.3*rim))[inside]
   height[inside]=np.maximum(height[inside],dome[inside]*.18)
  b=Image.fromarray(np.clip(a,0,255).astype('uint8'));d=ImageDraw.Draw(b)
  for cx,cy,rx,ry in positions:
   lines=[(cx-rx*.58,cy-ry*.55,cx+rx*.55,cy+ry*.55),(cx+rx*.55,cy-ry*.55,cx-rx*.55,cy+ry*.55)] if kind=='round' else [(cx-rx*.6,cy+q*ry,cx+rx*.6,cy+(q+.22)*ry) for q in [-.55,-.05,.45]]
   for x0,y0,x1,y1 in lines:
    dx=x1-x0;dy=y1-y0;length=math.hypot(dx,dy);nx=-dy/length;ny=dx/length
    for width,color in [(7,(117,63,23)),(4,(240,204,139))]:
     pts=[]
     for sign,ts in [(1,np.linspace(0,1,12)),(-1,np.linspace(1,0,12))]:
      for t in ts:w=width*math.sin(math.pi*t)**.7;pts.append((x0+t*dx+nx*w*sign,y0+t*dy+ny*w*sign))
     d.polygon(pts,fill=color)
  b=b.filter(ImageFilter.GaussianBlur(.5));gy,gx=np.gradient(height);normal=np.dstack((-gx,-gy,np.ones_like(gx)));normal/=np.linalg.norm(normal,axis=2)[:,:,None]
  maps={'B':b,'N':Image.fromarray(((normal*.5+.5)*255).astype('uint8')),'G':Image.new('RGB',(n,n),(24,)*3),'M':Image.new('RGB',(n,n),(0,)*3)}
  for k,im in maps.items():
   im.save(STAGE/'atlas'/r['sources'][k]);path=STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png';atlas=Image.open(path).convert('RGB');patch=im.resize((120,120),Image.Resampling.LANCZOS);atlas.paste(Image.fromarray(np.pad(np.array(patch),((4,4),(4,4),(0,0)),mode='edge')),(r['slot']%8*128,r['slot']//8*128));atlas.save(path)
 (STAGE/'atlas/manifest.json').write_text(json.dumps(m,indent=2));shutil.copytree(STAGE/'textures',SOURCE/'textures',dirs_exist_ok=True)
 print('BREAD STOCK PAINTED: all three arrangements are textures only')
if __name__=='__main__':
 if '--stock' in sys.argv:paint_stock()
 else:prepare()
