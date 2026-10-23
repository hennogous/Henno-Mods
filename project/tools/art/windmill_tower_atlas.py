"""Stage a translation-only repack of audited storage UV islands and tower plaster.

No live files are modified. Existing swatches keep their pixel density and orientation.
ImageGen supplies the plaster artwork; map math only derives technical companions.
"""
import argparse
import json
import math
from pathlib import Path
import shutil
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

SOURCE = Path.home()/'Desktop/Working Files/3D Art/Textures'
B_NAMES = ['CSC_Atlas_B_BAKERS','CSC_Atlas_B_BAKERS_2','CSC_Atlas_B_TAILORS','CSC_Atlas_B_TAILORS_2']

def pack(items):
    free=[(512,512,512,512)]; placed={}
    for name,w,h in sorted(items,key=lambda p:(max(p[1:]),p[1]*p[2]),reverse=True):
        options=[(min(r[2]-w,r[3]-h),max(r[2]-w,r[3]-h),r[1],r[0],r) for r in free if r[2]>=w and r[3]>=h]
        assert options, ('Atlas capacity',name,w,h)
        r=min(options)[-1];x,y=r[:2];placed[name]=[x,y,x+w,y+h]
        new=[]
        for a,b,c,d in free:
            if x>=a+c or x+w<=a or y>=b+d or y+h<=b:new.append((a,b,c,d));continue
            if x>a:new.append((a,b,x-a,d))
            if x+w<a+c:new.append((x+w,b,a+c-x-w,d))
            if y>b:new.append((a,b,c,y-b))
            if y+h<b+d:new.append((a,y+h,c,b+d-y-h))
        free=[r for i,r in enumerate(new) if not any(i!=j and r[0]>=s[0] and r[1]>=s[1] and r[0]+r[2]<=s[0]+s[2] and r[1]+r[3]<=s[1]+s[3] and (r!=s or i>j) for j,s in enumerate(new))]
    return placed

def main():
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('plaster',type=Path);a=p.parse_args();out=a.output
    boxes=json.loads((out/'uv-island-bounds.json').read_text());regions=[]
    for i,b in enumerate(boxes):
        rect=[max(512,math.floor(b[0]-.001)-2),max(512,math.floor(b[1]-.001)-2),min(1024,math.ceil(b[2]+.001)+2),min(1024,math.ceil(b[3]+.001)+2)]
        regions.append({'id':f'storage_{i:02}','uv_bounds':b,'source':rect})
    placements=pack([(r['id'],r['source'][2]-r['source'][0],r['source'][3]-r['source'][1]) for r in regions]+[('tower_plaster',132,132)])
    for r in regions:
        r['destination']=placements[r['id']]
        r['delta']=[r['destination'][j]-r['source'][j] for j in (0,1)]
    patch_rect=placements['tower_plaster'];inner=[patch_rect[0]+2,patch_rect[1]+2,patch_rect[2]-2,patch_rect[3]-2]
    manifest={'layout':'storage-tower-v3','atlas_size':1024,'quadrant':[512,512,1024,1024],'regions':regions,'tower_plaster':{'outer':patch_rect,'inner':inner,'source':str(a.plaster)},'normal_xy_strength':1.65,'preserves':'Pixel density, UV orientation, other three quadrants; no existing surface artwork regenerated.'}
    (out/'atlas-migration.json').write_text(json.dumps(manifest,indent=2))
    stage=out/'staged-textures';stage.mkdir(exist_ok=True)
    (out/'before-textures').mkdir(exist_ok=True)
    plaster=Image.open(a.plaster).convert('RGB').resize((128,128),Image.Resampling.LANCZOS)
    # Registered micro-relief only; broad albedo shading is removed before differentiation.
    lum=np.asarray(plaster.convert('L'),dtype=float)/255
    blurred=np.asarray(plaster.convert('L').filter(ImageFilter.GaussianBlur(5)),dtype=float)/255
    gy,gx=np.gradient(lum-blurred);n=np.dstack((-gx*2,-gy*2,np.ones_like(gx)));n/=np.linalg.norm(n,axis=2)[...,None]
    plaster_maps={'B':plaster,'N':Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255)), 'G':Image.new('RGB',(128,128),(28,28,28)), 'M':Image.new('RGB',(128,128),(0,0,0)), 'O':Image.new('RGB',(128,128),(255,255,255))}
    for name in B_NAMES+['CSC_Atlas_N','CSC_Atlas_G','CSC_Atlas_M','CSC_Atlas_O']:
        path=SOURCE/(name+('.png' if name=='CSC_Atlas_O' else '.dds'))
        shutil.copy2(path,out/'before-textures'/path.name)
        old=Image.open(path).convert('RGBA');new=old.copy()
        channel='B' if name in B_NAMES else name.rsplit('_',1)[1]
        new.paste({'B':(128,128,128,255),'N':(128,128,255,255),'G':(0,0,0,255),'M':(0,0,0,255),'O':(255,255,255,255)}[channel],(512,512,1024,1024))
        for r in regions:
            patch=old.crop(r['source'])
            if channel=='N':
                v=np.asarray(patch).astype(float);norm=v[:,:,:3]/127.5-1;norm[:,:,:2]*=1.65;norm/=np.maximum(np.linalg.norm(norm,axis=2)[...,None],1e-6)
                v[:,:,:3]=np.clip((norm*.5+.5)*255,0,255);patch=Image.fromarray(v.astype('uint8'))
            new.paste(patch,r['destination'][:2])
        ar=np.asarray(plaster_maps[channel].convert('RGBA'));padded=np.pad(ar,((2,2),(2,2),(0,0)),mode='edge')
        new.paste(Image.fromarray(padded),patch_rect[:2])
        assert np.array_equal(np.asarray(old)[:512],np.asarray(new)[:512])
        assert np.array_equal(np.asarray(old)[512:,:512],np.asarray(new)[512:,:512])
        new.save(stage/(name+'.png'))
    review=Image.open(stage/'CSC_Atlas_B_BAKERS.png').convert('RGB');draw=ImageDraw.Draw(review)
    for r in regions:
        draw.rectangle(r['destination'],outline=(255,0,255));draw.text(r['destination'][:2],r['id'],fill='white')
    draw.rectangle(patch_rect,outline='cyan');draw.text(patch_rect[:2],'tower plaster',fill='black')
    review.save(out/'atlas-layout-review.png')
    print('STAGED',len(regions),'retained UV regions + plaster;',sum((b[2]-b[0])*(b[3]-b[1]) for b in placements.values()),'of 262144 pixels')

if __name__=='__main__':main()
