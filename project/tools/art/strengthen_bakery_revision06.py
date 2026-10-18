"""Semantic relief and material-specific slope strengthening for canonical shared atlas r030.
No basecolour luminance-to-height conversion: new H uses traced structural masks;
existing relief uses registered normals, or pixel-matched legacy B/N crop pairs.
"""
from bakery_props_atlas import *
from PIL import Image,ImageDraw,ImageFilter
import subprocess
old=LIB/'Releases/2026-10-17_Shared_01_r029';m=json.loads((STAGE/'atlas/manifest.json').read_text());n=480
Y,X=np.mgrid[:n,:n];U=(X+.5)/n;V=(Y+.5)/n
relief=STAGE/'atlas/sources/relief-r030';relief.mkdir(parents=True,exist_ok=True)
def blur(a,r):return np.array(Image.fromarray(np.float32(a),'F').filter(ImageFilter.GaussianBlur(r))) if False else np.array(Image.fromarray(np.uint8(np.clip(a,0,1)*255)).filter(ImageFilter.GaussianBlur(r)),float)/255

def slopes(im):
 a=np.array(im.convert('RGB'),float);v=(a-127.5)/127.5;v[:,:,:2][abs(a[:,:,:2]-127.5)<=.51]=0
 return v[:,:,:2]/np.maximum(v[:,:,2:3],.12)
def encode(s):
 magnitude=np.linalg.norm(s,axis=2);s=s*np.minimum(1,np.tan(np.deg2rad(60))/np.maximum(magnitude,1e-8))[:,:,None];v=np.dstack((s,np.ones(s.shape[:2])));v/=np.linalg.norm(v,axis=2)[:,:,None];return Image.fromarray(np.uint8(np.clip(np.rint((v*.5+.5)*255),0,255)))
def metrics(im):
 a=slopes(im);tilt=np.degrees(np.arctan(np.linalg.norm(a,axis=2)));return dict(median=round(float(np.median(tilt)),2),p90=round(float(np.percentile(tilt,90)),2),max=round(float(tilt.max()),2))
def height_normal(name,H,target):
 H=blur((H-H.min())/max(float(H.max()-H.min()),1e-8),.65)
 Image.fromarray(np.uint16(H*65535),'I;16').save(relief/(name+'_H16.png'))
 small=np.array(Image.fromarray(np.float32(H),'F').resize((120,120),Image.Resampling.LANCZOS));gy,gx=np.gradient(small);s=np.dstack((-gx,gy));p=float(np.percentile(np.linalg.norm(s,axis=2),90));gain=np.tan(np.deg2rad(target))/max(p,.00001)
 return encode(s*gain),dict(height_source='atlas/sources/relief-r030/'+name+'_H16.png',runtime_gradient_gain=gain,target_p90_degrees=target,gradient_convention='negative dH/dU, positive image dH/dY (UV V points upward)')
def line_mask(paths,width):
 im=Image.new('L',(n,n));d=ImageDraw.Draw(im)
 for pts in paths:d.line([(int(x*n),int(y*n)) for x,y in pts],fill=255,width=width,joint='curve')
 return np.array(im,float)/255

def bread(name,B):
 # Artistically meaningful dome bounds fitted to the accepted ImageGen loaf silhouettes.
 if name=='bakery_round_crust':
  ell=[(.27,.27,.31,.31,-20),(.79,.24,.25,.25,0),(.53,.62,.40,.34,-8)]
  paths=[[(.07,.07),(.27,.18),(.48,.37)],[(.39,.03),(.25,.23),(.07,.45)],[(.60,.05),(.81,.17),(.98,.35)],[(.94,.03),(.80,.21),(.66,.42)],[(.28,.39),(.53,.54),(.79,.70)],[(.76,.37),(.54,.60),(.35,.84)]]
 elif name=='bakery_oval_bread':
  ell=[(.56,.20,.44,.19,18),(.28,.46,.30,.22,50),(.66,.66,.38,.24,-42)]
  paths=[[(.25,.04),(.55,.17),(.86,.32)],[(.06,.25),(.24,.32),(.43,.43)],[(.10,.48),(.25,.53),(.40,.59)],[(.45,.83),(.63,.62),(.89,.41)]]
 elif name=='bakery_long_crust':
  ell=[(.19,.49,.16,.49,-9),(.49,.50,.17,.50,5),(.81,.48,.18,.49,9)]
  paths=[]
  for x in [.18,.49,.81]:
   for y in ([.14,.39,.68] if x==.18 else [.14,.44,.75]):
    direction=1 if x==.18 else -1
    paths.append([(x-.13,y-direction*.14),(x,y),(x+.13,y+direction*.14)])
 else:
  ell=[(.54,.27,.57,.27,-8),(.52,.68,.60,.29,-3)]
  paths=[[(.08,.30),(.22,.14),(.40,.03)],[(.32,.31),(.52,.13),(.78,.01)],[(.12,.70),(.29,.56),(.46,.47)],[(.26,.81),(.49,.61),(.74,.48)],[(.68,.68),(.83,.58),(.97,.56)]]
 H=np.zeros((n,n));coverage=np.zeros((n,n));records=[]
 for cx,cy,rx,ry,angle in ell:
  a=math.radians(angle);dx=U-cx;dy=V-cy;xx=dx*math.cos(a)+dy*math.sin(a);yy=-dx*math.sin(a)+dy*math.cos(a);r=(xx/rx)**2+(yy/ry)**2;inside=r<1;dome=np.sqrt(np.clip(1-r,0,1));H[inside]=(.06+.65*dome)[inside];coverage[inside]=1;records.append([cx,cy,rx,ry,angle])
 # Cream scoring identification is colour-based inside hand-fitted score corridors,
 # not illumination height; ridged crust highlights outside these corridors are excluded.
 a=np.array(B.resize((n,n)).convert('RGB'),float)/255
 crumb=(a[:,:,0]>.72)&(a[:,:,1]>.64)&(a[:,:,2]>.35)&((a[:,:,0]-a[:,:,2])<.49)
 corridor=line_mask(paths,65);score=blur(crumb.astype(float)*corridor*coverage,3.5);H-=score*.09
 Image.fromarray(np.uint8(score*255)).save(relief/(name+'_ScoringMask.png'));Image.fromarray(np.uint8(coverage*255)).save(relief/(name+'_LoafMask.png'))
 return H,dict(loaf_ellipses=records,scoring_paths=paths,method='overlapping semantic loaf domes; recessed cream scores within manually fitted scoring corridors')

def wicker(B):
 # Trace horizontal woven reed centres from their expected bands in the ImageGen artwork.
 b=np.array(B.resize((n,n)).convert('RGB'),float);profile=b[:,:,1].mean(axis=1);centres=[]
 for expected in range(8,n,24):
  lo=max(0,expected-5);hi=min(n,expected+6);centres.append(lo+int(np.argmax(profile[lo:hi])))
 H=np.zeros((n,n))
 for j,cy in enumerate(centres):
  dy=(Y-cy)/9;strip=np.cos(np.clip(dy,-1,1)*math.pi/2)**2;strip[abs(dy)>1]=0
  H=np.maximum(H,.5*strip)
  # Short upright reeds occupy the gaps, staggered in alternate rows.
  for cx in np.arange(36+(j%2)*36,n,72):
   dist=((X-cx)/9)**2+((Y-cy-12)/14)**2;H=np.maximum(H,.34*np.sqrt(np.clip(1-dist,0,1)))
 return H,dict(method='ImageGen horizontal reed band centres and staggered upright interlace masks',reed_centres_y=centres)
def timber(B):
 b=np.array(B.resize((n,n)).convert('RGB').filter(ImageFilter.GaussianBlur(2)),float);grooves=Image.new('L',(n,n));d=ImageDraw.Draw(grooves);traces=[]
 for expected in [8,39,68,97,127,154,185,216,247,276,305,337,369,402,435,466]:
  pts=[]
  for y in range(0,n,8):
   lo=max(0,expected-9);hi=min(n,expected+10);x=lo+int(np.argmin(b[y,lo:hi,:2].mean(axis=1)));pts.append((x,y))
  d.line(pts,fill=255,width=3,joint='curve');traces.append(pts)
 H=1-blur(np.array(grooves,float)/255,1.8)*.65
 # Knot rings follow the three visible grain knots; no random pores/noise.
 for cx,cy,rx,ry in [(169,153,22,35),(371,352,20,28),(119,334,10,18)]:
  r=np.sqrt(((X-cx)/rx)**2+((Y-cy)/ry)**2);H-=.22*np.exp(-((r-1)/.12)**2)+.18*np.exp(-(r/.38)**2)
 return H,dict(method='traced narrow grain grooves and hand-fitted ImageGen knot rings',groove_traces=traces)

def brick():
 # Exactly matches the 960px24x12 running-bond guide used by ImageGen.
 row=np.floor(Y/40).astype(int);xx=(X-(row%2)*10)%20;yy=Y%40;edge=np.minimum.reduce([xx-1.5,18.5-xx,yy-1.5,38.5-yy]);H=np.clip(edge/2.5,0,1)
 return H,dict(method='exact24x12 guide-aligned mortar and beveled face masks',columns=24,courses=12,mortar_halfwidth_at480=1.5,bevel_width_at480=2.5)

oldN=Image.open(old/'textures/CSC_Props_Shared_01_N.png').convert('RGB');results=[]
legacy=LIB.parent;cropboxes={'bakery_light_stone':(205,256,368,465),'bakery_dark_stone':(0,256,205,465),'bakery_logs':(607,0,785,253)}
for r in m['regions']:
 name=r['name'];B=Image.open(STAGE/'atlas'/r['sources']['B']).convert('RGB');before=oldN.crop(tuple(r['bounds']));normal=before;info={};method='calm material preserved'
 if name in ['bakery_round_crust','bakery_oval_bread','bakery_long_crust','bakery_bread_stack_side']:
  H,info=bread(name,B);normal,params=height_normal(name,H,36);info.update(params);method='semantic bread height'
 elif name=='bakery_brick':H,info=brick();normal,params=height_normal(name,H,38);info.update(params);method='guide-aligned beveled masonry'
 elif name=='bakery_wicker':H,info=wicker(B);normal,params=height_normal(name,H,28);info.update(params);method='aligned woven reed height'
 elif name=='bakery_cart_timber':H,info=timber(B);normal,params=height_normal(name,H,22);info.update(params);method='aligned wood grooves and knots'
 elif name in cropboxes:
  box=cropboxes[name];legacyB=Image.open(legacy/'CSC_Atlas_Props_B.png').convert('RGB').crop(box).resize(B.size,Image.Resampling.LANCZOS);assert np.array_equal(legacyB,B)
  original=Image.open(legacy/'CSC_Atlas_Props_N.png').convert('RGB').crop(box).resize((120,120),Image.Resampling.LANCZOS);normal=encode(slopes(original)*3);method='pixel-matched existing B/N crop; slope gain3';info=dict(legacy_B_sha256=sha(legacy/'CSC_Atlas_Props_B.png'),legacy_N_sha256=sha(legacy/'CSC_Atlas_Props_N.png'),crop=box)
 elif metrics(before)['p90']>1:
  gain={'wood':4,'stone_clay':3,'textile_rope':5,'processing':2}.get(r['family'],2);normal=encode(slopes(before)*gain);method='existing registered relief slope amplification';info=dict(slope_gain=gain)
 # Flat metal/glass/cloth/dye/flour are intentionally kept calm; no invented detail.
 normal.save(STAGE/'atlas'/r['sources']['N'])
 results.append(dict(slot=r['slot'],region=name,family=r['family'],method=method,before_tilt_degrees=metrics(before),after_tilt_degrees=metrics(normal),details=info))
m['normal_source']='r030: strengthened registered relief, pixel-matched legacy N crops, and semantic ImageGen-aligned H/scoring/reed/grain masks; calm materials preserved. Runtime strength1; tilt capped60degrees.';(STAGE/'atlas/manifest.json').write_text(json.dumps(m,indent=2));(relief/'normal-relief-manifest.json').write_text(json.dumps(results,indent=2));(OUT/'normal-strength-report.json').write_text(json.dumps(results,indent=2))
packer=STAGE/'scripts/pack_bakery_additions.py';s=packer.read_text().replace("if not r['name'].startswith('bakery_'):continue","if k!='N' and not r['name'].startswith('bakery_'):continue");packer.write_text(s);subprocess.run([sys.executable,packer],check=True)
Image.open(STAGE/'textures/CSC_Props_Shared_01_N.png').resize((2048,2048),Image.Resampling.NEAREST).save(STAGE/'atlas/CSC_Props_Shared_01_v2_N_Master2048.png')
shutil.copytree(STAGE/'textures',SOURCE/'textures',dirs_exist_ok=True);shutil.copytree(relief,SOURCE/'art-provenance/relief-r030',dirs_exist_ok=True)
print('R030 RELIEF BUILT',[(r['region'],r['after_tilt_degrees']['p90']) for r in results])
