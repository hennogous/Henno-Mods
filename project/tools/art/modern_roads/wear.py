"""Historical one-off shoulder paint fit, retained for provenance only.

Keep geometry, UV allocations, road centers and the entire Modern atlas unchanged.
The generated image supplies painted detail; distance fields only constrain and
feather the coverage to the available shoulders of the existing projection cards.
"""
raise SystemExit('Historical one-off script: its height-channel assumptions were superseded by repair_height.py. Preserve the current painted atlas; do not rerun.')
from pathlib import Path
import json,shutil,hashlib,math
import numpy as np
from PIL import Image,ImageFilter,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[4]
O=Path.home()/'Desktop/Codex/Quarter-Roads-Modern/draft-03-roundabout'
D=Path.home()/'Desktop/Working Files/3D Art/Decals/CSC_ALL_Modern_Roads'
generated=Path.home()/'.codex/generated_images/01a17705-552a-7272-bb5e-272856a3d4c2/exec-1977abf0-5979-487c-9cf5-56806c36e795.png'
archive=O/'history/before-worn-shoulders';archive.mkdir(parents=True,exist_ok=False);shutil.copytree(D/'textures',archive/'textures')
for name in ['01_Stone.png','02_First_building.png','04_All_tarmac.png','Roundabout_Progression.png','delivery-validation.json']:shutil.copy2(O/name,archive/name)
shutil.copy2(generated,O/'sources/Stone_Shoulder_ImageGen.png')
shutil.copy2(ROOT/'project/tools/art/modern_roads/shoulder-paint-prompt.txt',O/'sources/Stone_Shoulder_ImageGen_Prompt.txt')
manifest=json.loads((D/'atlas-layout.json').read_text());tex=D/'textures';original=Image.open(tex/'CSC_Roads_Industrial_01_B.png').convert('RGBA');old=np.asarray(original).copy();gen=np.asarray(Image.open(generated).convert('RGBA').resize((512,512),Image.Resampling.LANCZOS));hmap=np.asarray(Image.open(tex/'CSC_Roads_Industrial_01_H.png').convert('RGBA')).copy();result=old.copy();stats=[]
def distance_to(mask,maxpx):
 h,w=mask.shape;best=np.full((h,w),maxpx+1,dtype=float)
 for dy in range(-maxpx,maxpx+1):
  for dx in range(-maxpx,maxpx+1):
   dist=math.hypot(dx,dy)
   if dist>maxpx:continue
   sy0=max(0,-dy);sy1=min(h,h-dy);sx0=max(0,-dx);sx1=min(w,w-dx)
   if sy1<=sy0 or sx1<=sx0:continue
   dst=best[sy0+dy:sy1+dy,sx0+dx:sx1+dx];np.minimum(dst,np.where(mask[sy0:sy1,sx0:sx1],dist,maxpx+1),out=dst)
 return best
for name,cell in manifest['cells'].items():
 x0,y0,x1,y1=cell['rect'];sx,sy=cell['size'];w=x1-x0;h=y1-y0;density=w/sx;src=old[y0:y1,x0:x1].astype(float);art=gen[y0:y1,x0:x1].astype(float)
 a=src[:,:,3]/255;inside=a>.45;outside_distance=distance_to(inside,12)/density;inside_distance=distance_to(~inside,12)/density
 # All silhouettes stay inside existing cell/card bounds. Typical shoulder is
 # 3-4 units of visible broken paving/dirt plus a low-opacity feather to 4.5.
 maxwidth=5.5 if name in ('roundabout','bend','junction') else 4.5
 luminance=art[:,:,:3].mean(2);smooth=np.asarray(Image.fromarray(luminance.astype('uint8')).filter(ImageFilter.GaussianBlur(1.4))).astype(float)
 detail=np.clip((luminance-smooth+22)/44,0,1)
 radius=maxwidth*(.65+.35*detail)
 feather=np.clip((radius-outside_distance+.2)/radius,0,1)**1.35
 paintalpha=art[:,:,3]/255
 fringe=feather*(.55+.45*detail)*paintalpha
 # Keep the middle of the original native paving exact; confine paint edits to
 # its outside 2 units and the newly exposed fringe.
 wear=np.clip((2.2-inside_distance)/2.2,0,1);wear=np.where(inside,wear,1)
 color=src[:,:,:3]*(1-wear[...,None])+art[:,:,:3]*wear[...,None]
 alpha=np.where(inside,np.maximum(a,fringe),np.maximum(a*.8,fringe))
 # Restore longitudinal fade semantics from the corresponding existing cells.
 if name in ('end','transition','patch'):
  xx=(np.arange(w)+.5)/w*sx-sx/2
  longitudinal=np.clip((sx/2-xx)/22,0,1) if name=='end' else np.clip((xx+sx/2)/23,0,1) if name=='transition' else np.clip((sx/2-np.abs(xx))/8,0,1)
  alpha=np.minimum(alpha,longitudinal[None,:])
 # Atlas limits are a technical safety envelope, not new painted material.
 if name in ('straight','connector','plain','end','transition','patch'):
  edge=np.minimum(np.arange(h)+.5,h-np.arange(h)-.5)/density
  alpha*=np.clip(edge[:,None]/1.2,0,1)
 chunk=np.dstack([color.clip(0,255),alpha*255]).astype('uint8');result[y0:y1,x0:x1]=chunk
 # New small chips/dirt relief is derived only from this painted fringe. Keep
 # existing Firaxis height unchanged in the retained central paving.
 oldh=hmap[y0:y1,x0:x1,3].astype(float);newh=np.clip(190+(luminance-smooth)*1.8+detail*32,150,240);height=(oldh*(1-wear)+newh*wear).clip(0,255).astype('uint8')
 pad=np.pad(height,((4,4),(4,4)),mode='edge');hmap[y0-4:y1+4,x0-4:x1+4,3]=pad
 stats.append({'cell':name,'original_alpha_area':float(a.sum()),'new_alpha_area':float(alpha.sum()),'maximum_fringe_world_units':maxwidth})
painted=Image.fromarray(result);painted.save(tex/'CSC_Roads_Industrial_01_B.png');painted.save(tex/'CSC_Roads_Industrial_01_FOW.png');Image.fromarray(hmap).save(tex/'CSC_Roads_Industrial_01_H.png')
board=Image.new('RGB',(1024,1090),(31,35,39));board.paste(painted.resize((1024,1024)),(0,48),painted.resize((1024,1024)));dr=ImageDraw.Draw(board);dr.text((16,12),'INDUSTRIAL | worn stone and dirt shoulders | 512 px',font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23),fill='white')
for name,c in manifest['cells'].items():
 a,b,cc,dd=c['rect'];dr.rectangle((a*2,b*2+48,cc*2,dd*2+48),outline=(90,105,116));dr.text((a*2+4,b*2+49),name,fill=(247,194,93))
board.save(O/'Atlas_Industrial.png')
provenance={'method':'Built-in ImageGen paint; deterministic cell/coverage fitting and fringe-only height derivation','generated_source':str(generated),'generated_sha256':hashlib.sha256(generated.read_bytes()).hexdigest(),'prompt':str(O/'sources/Stone_Shoulder_ImageGen_Prompt.txt'),'cells':stats,'geometry_and_uvs':'unchanged','modern_textures':'unchanged','backup':str(archive)}
(O/'shoulder-paint-provenance.json').write_text(json.dumps(provenance,indent=2));manifest['shoulders']={'revision':1,'paint':'ImageGen','retained_center':'Firaxis Industrial','coverage':'broken stone and subdued dirt, feathered within original cells','provenance':str(O/'shoulder-paint-provenance.json')}
for path in [D/'atlas-layout.json',O/'atlas-layout.json']:path.write_text(json.dumps(manifest,indent=2))
print('WORN_SHOULDERS_READY',stats)
