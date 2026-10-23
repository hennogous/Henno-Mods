"""Compare UV2 sample footprints with the installed shared AO cell."""
import json,sys
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw
out=Path(sys.argv[1]);d=json.loads((out/'sail-source.json').read_text())
lib=Path.home()/'Desktop/Working Files/3D Art/Textures/CSC_Props/Current'
im=Image.open(lib/'textures/CSC_Props_Shared_01_AO.png').convert('RGB').crop((0,128,512,512));draw=ImageDraw.Draw(im)
for p in d['polygons']:
    if all(i<456 and 64<=i%114<82 for i in p['verts']):
        xy=[(u*2048,(1-v)*2048-128) for u,v in p['uv2']]
        draw.line(xy+[xy[0]],fill=(255,0,0),width=1)
        if p['id']<52:draw.text(xy[0],str(p['id']),fill=(0,0,255))
im.resize((1024,768)).save(out/'AO-cloth-overlay.png')
hits=[]
for t in d['triangles']:
    xy=np.array([(u*2048,(1-v)*2048-128) for u,v in t['uv']]);lo=np.maximum(np.floor(xy.min(0)).astype(int),0);hi=np.minimum(np.ceil(xy.max(0)).astype(int),[512,384])
    x,y=np.meshgrid(np.arange(lo[0],hi[0])+.5,np.arange(lo[1],hi[1])+.5);q=np.stack((x,y),axis=-1)
    a,b,c=xy;cross=lambda u,v:u[...,0]*v[...,1]-u[...,1]*v[...,0]
    den=cross(b-a,c-a)
    if abs(den)<1e-8:continue
    v=cross(q-a,c-a)/den;w=cross(b-a,q-a)/den;inside=(v>.03)&(w>.03)&(v+w<.97)
    hits.extend((int(xx),int(yy),t['face']) for xx,yy in zip(x[inside],y[inside]))
from collections import defaultdict
pixels=defaultdict(set)
for x,y,f in hits:pixels[x,y].add(f)
overlap={str(k):list(v) for k,v in pixels.items() if len(v)>1}
(out/'overlap.json').write_text(json.dumps(overlap));print('Overlapping interior pixel samples:',len(overlap));print(list(overlap.items())[:8])
