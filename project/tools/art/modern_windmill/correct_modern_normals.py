"""Normal-only correction: explicit registered construction profiles, unchanged B/UVs."""
import sys,json,shutil,math,subprocess
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
from modular_v9 import ROOT,ART,sha,dump,texname
from refinement_native import DESTS,LIBS,IDS,MOD
O=Path.home()/'Desktop/Codex/modern-normal-correction-20261027'
OLD=Path.home()/'Desktop/Codex/modern-kit-refinement-20261027'
RELEASES={'building':'2026-10-27_Modern_r005','props':'2026-10-27_Modern_r004'}
S=512
Y,X=np.mgrid[:S,:S]/4+.125
def ramp(a):
 a=np.clip(a,0,1);return a*a*(3-2*a)
def box(x0,y0,x1,y1,bevel=.7):
 return ramp(np.minimum.reduce([X-x0,x1-X,Y-y0,y1-Y])/bevel)
def line(points,width):
 dist=np.full((S,S),1e6)
 for (x0,y0),(x1,y1) in zip(points,points[1:]):
  dx,dy=x1-x0,y1-y0;t=np.clip(((X-x0)*dx+(Y-y0)*dy)/max(dx*dx+dy*dy,.001),0,1);d=np.hypot(X-x0-t*dx,Y-y0-t*dy);dist=np.minimum(dist,d)
 return 1-ramp(dist/width)
def circle(x,y,r):return ramp(1-((X-x)**2+(Y-y)**2)/(r*r))
def normals(h,world):
 dy,dx=np.gradient(h,world[1]/S,world[0]/S);a=np.stack((-dx,dy,np.ones_like(h)),axis=-1);a/=np.linalg.norm(a,axis=2,keepdims=True)
 im=Image.fromarray(np.uint8(np.clip((a+1)*127.5,0,255))).resize((128,128),Image.Resampling.LANCZOS)
 a=np.asarray(im,dtype=float)/127.5-1;a/=np.maximum(np.linalg.norm(a,axis=2,keepdims=True),1e-8)
 return Image.fromarray(np.uint8(np.clip((a+1)*127.5,0,255)))
def masonry(kind):
 h=np.zeros((S,S));brick=kind=='brick';w,hh=(16,16) if brick else (128/6,32);depth=.28 if brick else .42
 for row in range(8 if brick else 4):
  y0=row*hh-.5;y1=(row+1)*hh-.5;offset=7 if brick and row%2==0 else -1 if brick else -1
  boundaries=[col*w+offset for col in range(-1,11)] if brick else ([-5,17,40,60,82,102,125,146] if row%2==0 else [-14,7,28,50,71,93,114,135])
  for x0,x1 in zip(boundaries,boundaries[1:]):
   h=np.maximum(h,depth*box(x0+.35,y0+.35,x1-.35,y1-.35,.85 if brick else 1.05))
 return h,(64,32) if brick else (84,32)
def roof(kind):
 # Raised folded strip lies between bright left shoulder and dark right shadow.
 centres=([5.6,16.3,27,37.6,48.3,59,69.6,80.3,91,101.6,112.3,123] if kind=='building' else [5.5,16,26.5,37.5,48,59,70.5,82,93.5,105,117.5])
 h=np.zeros((S,S))
 for c in centres:h=np.maximum(h,.54*(1-ramp((np.abs(X-c)-.28)/1.15)))
 return h,(96,32)
def window():
 h=np.zeros((S,S));h+=.18*box(0,-3,128,18,1);h+=.30*box(0,107,128,132,1.2)
 h-=.65*box(19.5,18.5,108,108,1.1)
 frame=box(27,25,101,104,1)-box(32,29,96,99,1)
 h+=.55*frame
 h+=.52*box(60,28,65,101,.8);h+=.52*box(30,61,98,66,.8)
 return h,(13.5,18.2)
def timber(pallet=False):
 h=np.zeros((S,S))
 if not pallet:
  paths=[[(0,10),(18,12),(36,11),(62,8),(84,9),(104,8),(128,6)],[(0,25),(20,24),(42,26),(68,25),(91,24),(103,21),(118,21),(128,25)],[(0,39),(24,40),(48,36),(70,38),(92,39),(111,38),(128,40)],[(0,51),(25,49),(45,48),(70,47),(95,49),(128,46)],[(0,65),(19,67),(33,65),(44,64),(59,67),(78,65),(104,61),(128,60)],[(0,83),(20,81),(29,84),(40,88),(49,88),(60,83),(82,79),(103,78),(128,75)],[(0,91),(20,90),(44,94),(68,92),(94,88),(128,87)]]
  for p in paths:h-=.025*line(p,.65)
  for cx,cy,rx,ry in [(43,79,8,5),(117,30,7,3)]:
   points=[(cx+rx*math.cos(t),cy+ry*math.sin(t)) for t in np.linspace(0,2*math.pi,33)];h-=.03*line(points,.65)
  h[Y>95]=0
  return h,(48,5)
 for c in (31,63,95):h-=.20*line([(c,-4),(c,132)],.9)
 for p in [[(7,0),(9,25),(7,48),(10,76),(8,103),(9,128)],[(23,0),(21,23),(24,46),(21,73),(23,98),(22,128)],[(40,0),(42,22),(45,35),(43,52),(40,75),(41,103),(39,128)],[(54,0),(53,23),(56,38),(54,56),(56,88),(53,112),(54,128)],[(78,0),(77,24),(80,48),(76,70),(79,97),(77,128)],[(108,0),(110,35),(107,62),(111,92),(109,128)],[(120,0),(118,23),(121,57),(117,82),(120,104),(119,128)]]:h-=.04*line(p,.65)
 return h,(22,15)
def silo():
 h=np.zeros((S,S))
 for y in (43,88):h-=.24*line([(-3,y),(131,y)],.85)
 for x in (11,116):h-=.16*line([(x,-3),(x,131)],.7)
 for x in (6,122):
  for y in (8,33,52,82,102,123):h+=.15*circle(x,y,2)
 return h,(48,59)
def elevator():
 h=.30*(box(-3,-3,11,131,.8)+box(115,-3,131,131,.8))
 for y0,y1 in ((26,36),(54,64),(84,95)):h=np.maximum(h,.30*box(-3,y0,131,y1,.8))
 for y in (5,30,59,89,121):
  for x in (5,64,121):
   if y in (5,121) and x==64:continue
   h+=.14*circle(x,y,1.9)
 return h,(13,96)
def sacks():
 h=np.zeros((S,S))
 for x in (7,121):h+=.10*line([(x,0),(x,128)],2.2)
 paths=[[(12,3),(32,12),(61,17),(94,11),(116,2)],[(11,125),(36,114),(67,111),(96,118),(117,126)]]
 for p in paths:h-=.12*line(p,3.6)
 return h,(11,18)
def prepare():
 O.mkdir(exist_ok=True);baseline={'runtime':{},'libraries':{},'masters':{}}
 for kind,lib in LIBS.items():
  dst=O/'libraries'/kind;shutil.copytree(lib/'Current',dst,dirs_exist_ok=True)
  baseline['libraries'][kind]={str(p.relative_to(lib/'Current')):sha(p) for p in (lib/'Current').rglob('*') if p.is_file()}
 for p in (OLD/'staged').rglob('*'):
  if p.suffix in ('.ast','.geo','.fgx','.mtl','.tex','.dds'):
   rel=p.relative_to(OLD/'staged');src=MOD/rel;assert src.is_file();dst=O/'staged'/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);baseline['runtime'][str(rel)]=sha(src)
 for ident,d in DESTS.items():
  baseline['masters'][str(d/(ident+'.blend'))]=sha(d/(ident+'.blend'))
  for p in (d/'textures').glob('*_N.png'):baseline['masters'][str(p)]=sha(p)
 dump(O/'baseline.json',baseline)
 patches={'building':{0:masonry('brick'),1:masonry('stone'),2:roof('building'),7:window(),8:timber()},'props':{0:roof('props'),8:silo(),9:elevator(),16:sacks(),17:sacks(),18:timber(True),19:masonry('stone')}}
 evidence={}
 for kind,items in patches.items():
  root=O/'libraries'/kind;target=root/'textures'/(texname(kind,'N')+'.png');im=Image.open(target).convert('RGB');b=Image.open(root/'textures'/(texname(kind,'B')+'.png'));grid=4 if kind=='building' else 8
  heights=root/'sources/normal-relief';heights.mkdir(exist_ok=True);canvas=Image.new('RGB',(len(items)*256,800),'white');draw=ImageDraw.Draw(canvas);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',16)
  for i,(slot,(h,world)) in enumerate(items.items()):
   n=normals(h,world);x,y=slot%grid*128,slot//grid*128;im.paste(n,(x,y));np.save(heights/f'{slot:02}.npy',h.astype(np.float32))
   lo,hi=float(h.min()),float(h.max());hp=Image.fromarray(np.uint8((h-lo)/max(hi-lo,1e-8)*255)).convert('RGB')
   for j,p in enumerate((b.crop((x,y,x+128,y+128)),hp,n)):canvas.paste(p.resize((256,256)),(i*256,32+j*256))
   draw.text((i*256+5,6),f'{slot} B / height / N',font=font,fill='black');evidence[f'{kind}/{slot}']={'world_coverage':world,'height_range':[lo,hi],'height_source':f'sources/normal-relief/{slot:02}.npy'}
  im.save(target);im.save(root/'sources/registered_N.png');canvas.save(O/(kind+'-registered-relief.png'))
  shutil.copy2(Path(__file__),root/'sources/normal-relief/authoring_recipe.py')
 dump(O/'normal-authoring.json',{'method':'Manually specified structural profiles measured against unchanged final B; no brightness-to-height or random noise','features':evidence,'unchanged':'B, G, M, AO, geometry, UVs, assembly'})
 print('PREPARED')
def stage():
 import modular_v9_native as native
 exp=native.exp
 for kind in LIBS:
  p=O/'libraries'/kind/'textures'/(texname(kind,'N')+'.png');dst=O/'staged/Textures'
  r=subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-o',str(dst),str(p)],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr
  exp.validate_dds(dst/(p.stem+'.dds'),{'slot':'N','size':[1024,1024],'format':'R8G8B8A8_UNORM'})
  assert Image.open(dst/(p.stem+'.dds')).convert('RGB').tobytes()==Image.open(p).convert('RGB').tobytes()
 print('STAGED_TWO_NORMAL_MAPS')
def publish():
 import modular_v9_native as native
 baseline=json.loads((O/'baseline.json').read_text());review=json.loads((O/'visual-review.json').read_text());assert review['reviewed']
 cook=json.loads((O/'cook-check/result.json').read_text());assert cook['exit_code']==0 and cook['blps']
 log=(O/'cook-check/stdout.log').read_text(errors='replace').replace('\x00','');assert '(ERRORS!!)' not in log and 'I/O error' not in log
 for rel,h in baseline['runtime'].items():assert sha(MOD/rel)==h,('Concurrent runtime edit',rel)
 for path,h in baseline['masters'].items():assert sha(path)==h,('Concurrent authoring edit',path)
 payload={};normals={texname(kind,'N')+'.png':O/'libraries'/kind/'textures'/(texname(kind,'N')+'.png') for kind in LIBS}
 for kind,lib in LIBS.items():
  assert all(sha(lib/'Current'/p)==h for p,h in baseline['libraries'][kind].items());assert not (lib/'Releases'/RELEASES[kind]).exists()
  root=O/'libraries'/kind
  for p in (root/'textures').iterdir():
   if p.name!=texname(kind,'N')+'.png':assert sha(p)==sha(lib/'Current/textures'/p.name)
  info=json.loads((root/'library.json').read_text());info.update(release=RELEASES[kind],status='Normal-only corrective pass; registered structural profiles, neutral multi-light review; colour/UVs/geometry unchanged',maps={p.name:sha(p) for p in (root/'textures').iterdir() if p.is_file()});dump(root/'library.json',info)
  shutil.copy2(O/'normal-authoring.json',root/'sources/normal-relief/manifest.json');shutil.copy2(O/'visual-review.json',root/'sources/normal-relief/visual-review.json')
  for p in root.rglob('*'):
   if p.is_file():
    for dest in (lib/'Current',lib/'Releases'/RELEASES[kind]):payload[dest/p.relative_to(root)]=p
  ptr=O/(kind+'-CURRENT.json');dump(ptr,{'release':RELEASES[kind],'current':'Current','snapshot':'Releases/'+RELEASES[kind],'manifest':'Current/library.json'});payload[lib/'CURRENT.json']=ptr
  n=texname(kind,'N')+'.dds';payload[MOD/'Textures'/n]=O/'staged/Textures'/n
 for folder in DESTS.values():
  for name,p in normals.items():
   if (folder/'textures'/name).exists():payload[folder/'textures'/name]=p
 backup=O/'publication-backup';backup.mkdir(exist_ok=True);rows=[]
 for i,(dest,p) in enumerate(payload.items()):
  row={'destination':str(dest),'before':sha(dest) if dest.exists() else None,'source':str(p)}
  if dest.exists():q=backup/f'{i:04}-{dest.name}';shutil.copy2(dest,q);row['backup']=str(q)
  rows.append(row)
 dump(backup/'manifest.json',rows)
 for row,(dest,p) in zip(rows,payload.items()):
  assert (sha(dest) if dest.exists() else None)==row['before'];dest.parent.mkdir(exist_ok=True,parents=True);shutil.copy2(p,dest);row['after']=sha(dest);assert row['after']==sha(p)
 allowed={'Textures/'+texname(k,'N')+'.dds' for k in LIBS}
 for rel,h in baseline['runtime'].items():
  if Path(rel).as_posix() not in allowed:assert sha(MOD/rel)==h,rel
 for p,h in baseline['masters'].items():
  if Path(p).suffix=='.blend':assert sha(p)==h,p
 cache=[str(MOD/'Assets'/(i+'.ast')) for i in (*IDS,'CSC_BAKERS_Wind_Mill_Modern')]+[str(MOD/'Materials'/(m+'.mtl')) for m in ('CSC_BAKERS_Modern','CSC_Props_Modern_01')]
 dump(O/'publication-report.json',{'installed':True,'files':rows,'runtime_changes':sorted(allowed),'geometry_blends_UVs_B_AO_and_AST_unchanged':True,'cache_inputs':cache,'in_game_tested':False});native.cache(O);print('PUBLISHED_NORMALS',len(rows))
if __name__=='__main__':globals()[sys.argv[1]]()
