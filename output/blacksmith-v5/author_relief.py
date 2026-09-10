"""Derive an aligned, editable structural height map from selected atlas seams.

This is technical map authoring, not a base-color repaint. Thresholds are specific
to this inspected atlas. Broad distance bevels replace luminance bumps; grain uses
only selected dark grooves, and plaster/soot remain almost flat.
"""
from pathlib import Path
import json, shutil
import numpy as np
from PIL import Image, ImageFilter

OUT=Path(__file__).resolve().parent
TEX=OUT/'Textures'
PREFIX='CSC_BLACKSMITH_Workshop'
base=Image.open(TEX/f'{PREFIX}_B.png').convert('RGB')
rgb=np.asarray(base,dtype=float)/255
lum=rgb@np.array([.2126,.7152,.0722])
h,w=lum.shape
definitions=[
 ('roof',[0,0,.5,.5],1,.17,0),
 ('stone',[.5,0,1,.5],1,.10,0),
 ('wood',[0,.5,.5,1],.8,.19,0),
 ('plaster',[.5,.5,1,.68],.22,.07,0),
 ('iron',[.5,.68,.625,.815],.5,.28,.85),
 ('endgrain',[.625,.68,.75,.815],.7,.18,0),
 ('cloth',[.75,.68,.875,.815],.35,.07,0),
 ('coals',[.875,.68,1,.815],.65,.10,0),
 ('soot',[.5,.815,.625,1],0,.04,0),
 ('water',[.625,.815,.75,1],.35,.60,0),
 ('leather',[.75,.815,.875,1],.35,.16,0),
 ('steel',[.875,.815,1,1],.45,.44,.95),
]
regions=[dict(name=n,bounds=b,normal=a,gloss=g,metalness=m) for n,b,a,g,m in definitions]
(OUT/'material-regions.json').write_text(json.dumps(regions,indent=2)+'\n')

def blur(a,r):
    return np.asarray(Image.fromarray(np.uint8(np.clip(a,0,1)*255)).filter(ImageFilter.GaussianBlur(r)),dtype=float)/255

def bevel(mask,radius):
    # Close pinholes in painted faces, then use an eight-neighbour distance ramp.
    # Unlike repeated square erosion, this avoids conspicuous square bevel fans.
    im=Image.fromarray(np.uint8(mask)*255).filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))
    clean=np.asarray(im.filter(ImageFilter.GaussianBlur(.8)))>127
    hh,ww=clean.shape
    d=np.pad(np.where(clean,float(radius+2),0),1,mode='edge')
    diagonal=2**.5
    for yy in range(1,hh+1):
        for xx in range(1,ww+1):
            d[yy,xx]=min(d[yy,xx],d[yy-1,xx]+1,d[yy,xx-1]+1,d[yy-1,xx-1]+diagonal,d[yy-1,xx+1]+diagonal)
    for yy in range(hh,0,-1):
        for xx in range(ww,0,-1):
            d[yy,xx]=min(d[yy,xx],d[yy+1,xx]+1,d[yy,xx+1]+1,d[yy+1,xx+1]+diagonal,d[yy+1,xx-1]+diagonal)
    return blur(np.minimum(d[1:-1,1:-1]/radius,1),1.0)

height=np.full((h,w),.5)
emissive=np.zeros((h,w,3))
for region in regions:
    x0,y0,x1,y1=[round(v*(w if i%2==0 else h)) for i,v in enumerate(region['bounds'])]
    a=lum[y0:y1,x0:x1]; name=region['name']
    if name=='stone':
        # Mortar darks only; colored brush facets stay on the same stone face.
        field=.22+.52*bevel(blur(a,.65)>.47,6)
    elif name=='roof':
        field=.20+.48*bevel(blur(a,.55)>.235,7)
    elif name in ['wood','endgrain']:
        grooves=np.maximum(blur(a,4)-blur(a,.6)-.009,0)
        field=.55-np.clip(grooves*3.8,0,.24)
    elif name=='plaster':
        field=.5+(blur(a,2)-blur(a,9))*.10
    elif name=='cloth':
        field=.5+(blur(a,.65)-blur(a,3))*.35
    elif name=='coals':
        # Orange fissures are gaps, not the highest surface.
        field=.3+.3*bevel(a<.30,4)
        colors=rgb[y0:y1,x0:x1]
        mask=np.clip((colors[:,:,0]-colors[:,:,2]-.22)*2.8,0,1)
        emissive[y0:y1,x0:x1]=colors*mask[:,:,None]
    elif name=='water':
        field=.5+(blur(a,3)-blur(a,12))*.45
    elif name=='soot':field=np.full_like(a,.5)
    else:field=.5+(blur(a,1)-blur(a,5))*.35
    height[y0:y1,x0:x1]=field
Image.fromarray(np.uint8(np.clip(height,0,1)*255)).save(TEX/f'{PREFIX}_H.png')
Image.fromarray(np.uint8(np.clip(emissive,0,1)*255)).save(TEX/f'{PREFIX}_E.png')
shutil.copy2(OUT.parent/'blacksmith-v4/Textures'/f'{PREFIX}_AO.png',TEX/f'{PREFIX}_AO.png')
print('Authored height, semantic regions and emissive; reused unchanged geometry AO.')
