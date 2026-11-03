"""Pack ImageGen artwork; derive registered semantic relief and material-response maps."""
import sys,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
def distance_transform_edt(mask):
    # Bounded pixel distance is sufficient for the eight-pixel bevel profile.
    layer=Image.fromarray(mask.astype('uint8')*255);result=np.zeros(mask.shape)
    for _ in range(10):
        result+=np.asarray(layer)>0;layer=layer.filter(ImageFilter.MinFilter(3))
    return result
def gaussian_filter(array,radius):
    lo,hi=float(array.min()),float(array.max())
    if hi-lo<1e-8:return array
    im=Image.fromarray(np.uint8(np.clip((array-lo)/(hi-lo)*255,0,255)))
    return np.asarray(im.filter(ImageFilter.GaussianBlur(radius))).astype(float)/255*(hi-lo)+lo
OUT=Path(sys.argv[1]);src=Path(sys.argv[2]);ASSET='CSC_BAKERS_Wind_Mill_Modern';S=512
(OUT/'textures').mkdir(parents=True,exist_ok=True);shutil.copy2(src,OUT/'ImageGen_material_source.png')
im=Image.open(src).convert('RGB');assert im.size==(1254,1254)
xs=[0,314,629,943,1254];ys=[0,315,626,930,1254]
atlas=Image.new('RGB',(2048,2048));patches=[]
for t in range(16):
    col,row=t%4,t//4;bounds=(xs[col],ys[row],xs[col+1],ys[row+1])
    # Whole repeat periods measured from the returned artwork, not assumed prompt counts.
    if t==0:bounds=(58,50,229,119)  # Two brick lengths x two courses: 16 x 8 world units.
    if t==1:bounds=(330,92,594,250) # Two dressed blocks x two courses: 28 x 16 units.
    if t==2:bounds=(637,2,914,313) # Four standing seams across 32 units.
    p=im.crop(bounds).resize((S,S),Image.Resampling.LANCZOS);patches.append(p)
normal=Image.new('RGB',(2048,2048),(128,128,255));height=Image.new('L',(2048,2048));gloss=Image.new('RGB',(2048,2048));metal=Image.new('RGB',(2048,2048))
for t,p in enumerate(patches):
    a=np.asarray(p).astype(float)/255;lum=a.mean(2);sat=a.max(2)-a.min(2);h=np.zeros((S,S));world=(32,32)
    if t==0:
        # Beige low-saturation mortar mask, not brightness-to-height conversion.
        mortar=(sat<.29)&(lum>.37)
        h=np.clip(distance_transform_edt(~mortar)/7,0,1)*.28;world=(16,8)
    elif t==1:
        mortar=(lum<.39)
        h=np.clip(distance_transform_edt(~mortar)/8,0,1)*.60;world=(28,16)
    elif t==2:
        # Vertical standing-seam landmarks measured from the actual painted patch.
        h[:]=.04
        for x in (0,.225,.48,.735,.99):h+=.48*np.exp(-((np.arange(S)[None,:]-x*S)/4.2)**2)
        world=(32,32)
    elif t==3:
        h[:]=.12
        for y in (.35,.71):h-=.32*np.exp(-((np.arange(S)[:,None]-y*S)/2.5)**2)
        for x in (.10,.91):h-=.22*np.exp(-((np.arange(S)[None,:]-x*S)/2.3)**2)
        world=(48,59)
    elif t==7:
        # Painted frame surrounds a recessed window; mullions retain raised relief.
        hh=Image.new('L',(S,S),170);d=ImageDraw.Draw(hh)
        d.rectangle((S*.13,S*.12,S*.87,S*.86),fill=110)
        d.rectangle((S*.20,S*.19,S*.80,S*.79),fill=20)
        d.rectangle((S*.48,S*.19,S*.53,S*.79),fill=135)
        d.rectangle((S*.20,S*.46,S*.80,S*.51),fill=135)
        h=np.asarray(hh).astype(float)/255*2.4;world=(13.5,19.5)
    elif t==8:
        h[:]=.1
        for x in (.11,.22,.34,.48,.52,.67,.79,.90):h-=.2*np.exp(-((np.arange(S)[None,:]-x*S)/2.6)**2)
        world=(20,26)
    elif t==9 or t==15:
        # Soft edge folds only; no weave embossed across canvas.
        yy,xx=np.mgrid[:S,:S]/S;h=.18*np.sin(xx*np.pi)*np.sin(yy*np.pi)
        world=(11,18)
    elif t==10:
        h[:]=.1
        for x in (.245,.5,.755):h-=.32*np.exp(-((np.arange(S)[None,:]-x*S)/3.2)**2)
        world=(22,15)
    elif t==14:
        # Green casing bands isolated by hue, then given one consistent shallow height.
        band=(a[:,:,1]>a[:,:,0]*1.07)&(a[:,:,2]<a[:,:,1]*.83)
        h=band.astype(float)*.55;world=(13,96)
    h=gaussian_filter(h,1.4)
    gy,gx=np.gradient(h);gx*=S/world[0];gy*=S/world[1]
    n=np.stack((-gx,gy,np.ones_like(h)),axis=-1);n/=np.linalg.norm(n,axis=-1,keepdims=True)
    ni=Image.fromarray(np.uint8(np.clip((n*.5+.5)*255,0,255)))
    # Pack multiple measured repeats into one cell to avoid excessive UV-boundary topology.
    rx,ry={0:(4,4),1:(3,2),2:(3,1)}.get(t,(1,1))
    if (rx,ry)!=(1,1):
        base_repeat=p;normal_repeat=ni;p=Image.new('RGB',(S,S));ni=Image.new('RGB',(S,S))
        for yy in range(ry):
            for xx in range(rx):
                x0,x1=round(xx*S/rx),round((xx+1)*S/rx);y0,y1=round(yy*S/ry),round((yy+1)*S/ry)
                p.paste(base_repeat.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),(x0,y0))
                ni.paste(normal_repeat.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),(x0,y0))
        normals=np.asarray(ni).astype(float)/255*2-1;normals/=np.maximum(np.linalg.norm(normals,axis=2,keepdims=True),1e-8)
        ni=Image.fromarray(np.uint8(np.clip((normals*.5+.5)*255,0,255)))
    xy=((t%4)*S,(t//4)*S);normal.paste(ni,xy);atlas.paste(p,xy)
    hp=Image.fromarray(np.uint8(np.clip(h/2.4*200+30,0,255)))
    if (rx,ry)!=(1,1):
        hr=hp;hp=Image.new('L',(S,S))
        for yy in range(ry):
            for xx in range(rx):
                x0,x1=round(xx*S/rx),round((xx+1)*S/rx);y0,y1=round(yy*S/ry),round((yy+1)*S/ry)
                hp.paste(hr.resize((x1-x0,y1-y0),Image.Resampling.LANCZOS),(x0,y0))
    height.paste(hp,xy)
    g=[38,32,85,76,72,65,100,145,65,25,35,32,75,15,75,25][t]
    gloss.paste(Image.new('RGB',(S,S),(g,g,g)),xy);m=110 if t==6 else 0;metal.paste(Image.new('RGB',(S,S),(m,m,m)),xy)
for ch,img in [('B',atlas),('N',normal),('G',gloss),('M',metal),('RELIEF',height)]:img.save(OUT/'textures'/f'{ASSET}_{ch}.png')
Image.new('RGB',(16,16)).save(OUT/'textures'/f'{ASSET}_E.png')
(OUT/'texture-provenance.json').write_text(json.dumps({'B':'Built-in ImageGen edit; measured whole-repeat crops and fixed 4x4 repacking only','source':str(src),'N':'Semantic mortar masks and registered construction landmarks; height in model units, not generic B luminance conversion; repeated and resized normals renormalized','sampling':{'brick_period':[64,32],'brick_size':[8,4],'stone_period':[84,32],'stone_size':[14,8],'roof_period':[96,32],'roof_seam_pitch':8},'AO':'New geometry UV2 bake'},indent=2))
print('Material atlas and aligned relief maps ready')
