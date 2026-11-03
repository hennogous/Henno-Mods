"""Pack ImageGen roof/window/timber patches and registered strong relief for revision 7."""
import sys,json,shutil
from pathlib import Path
import numpy as np
from PIL import Image,ImageFilter,ImageDraw
OUT=Path(sys.argv[1]);SOURCE=Path(sys.argv[2]);NAME='CSC_BAKERS_Wind_Mill_Modern';S=512
OLD=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/modern/revision-06-concept-refinement/textures'
(OUT/'textures').mkdir(parents=True,exist_ok=True)
shutil.copy2(SOURCE,OUT/'ImageGen_v7_material_source.png')
maps={ch:Image.open(OLD/f'{NAME}_{ch}.png').convert('RGB') for ch in ('B','N','G','M','E','AO')}
art=Image.open(SOURCE).convert('RGB');assert art.size==(1254,1254)
patches={7:art.crop((627,0,1254,627)).resize((S,S),Image.Resampling.LANCZOS),8:art.crop((0,627,627,1254)).resize((S,S),Image.Resampling.LANCZOS)}
# One complete period bounded halfway between adjacent painted seams (113,189,256).
# Twelve seams per 96-unit atlas period preserve the authored 8-unit pitch.
roof=art.crop((151,0,222,627));rp=Image.new('RGB',(S,S))
for i in range(12):
    l,r=round(i*S/12),round((i+1)*S/12);rp.paste(roof.resize((r-l,S),Image.Resampling.LANCZOS),(l,0))
patches[2]=rp
def put(ch,t,im):maps[ch].paste(im,((t%4)*S,(t//4)*S))
def normal(h,world):
    # Derive only from authored structural height, never generic colour luminance.
    lo,hi=float(h.min()),float(h.max());a=np.asarray(Image.fromarray(np.uint8((h-lo)/(hi-lo)*255)).filter(ImageFilter.GaussianBlur(2.2))).astype(float)/255*(hi-lo)+lo
    gy,gx=np.gradient(a);n=np.stack((-gx*S/world[0],gy*S/world[1],np.ones_like(a)),axis=-1);n/=np.linalg.norm(n,axis=2,keepdims=True)
    return Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255))
yy,xx=np.mgrid[:S,:S]/S
# Measured generated window boundaries: raised lintel/sill and stone side reveals,
# deep glazing with a bold timber frame and cross mullion.
h=np.ones((S,S))*1.1
h[(xx>.182)&(xx<.822)&(yy>.158)&(yy<.846)]=-.5
h[(xx>.218)&(xx<.788)&(yy>.198)&(yy<.805)]=.2
for x0,x1 in ((.242,.475),(.523,.766)):
    for y0,y1 in ((.222,.482),(.531,.777)):h[(xx>x0)&(xx<x1)&(yy>y0)&(yy<y1)]=-2.0
h[yy>.846]=1.5
put('N',7,normal(h,(13.5,18.2)))
# Roof seams: infer exact painted ridge positions from the aligned generated patch.
lum=np.asarray(rp).astype(float).mean(2).mean(0);smooth=np.convolve(lum,np.ones(5)/5,mode='same')
peaks=[]
for i in range(5,S-5):
    if smooth[i]>smooth.mean()+12 and smooth[i]==max(smooth[max(0,i-9):min(S,i+10)]) and (not peaks or i-peaks[-1]>19):peaks.append(i)
rh=np.zeros((S,S))
for i in peaks:rh+=.55*np.exp(-((np.arange(S)[None,:]-i)/1.8)**2)
put('N',2,normal(rh,(96,32)))
# Broad timber grain is restrained; reuse the generated side-grain artwork, no modeled grooves.
wh=.045*np.sin(yy*35+np.sin(xx*9));put('N',8,normal(wh,(48,5)))
for t,p in patches.items():put('B',t,p);put('M',t,Image.new('RGB',(S,S),(0,0,0)))
for t,g in ((2,78),(7,90),(8,34)):put('G',t,Image.new('RGB',(S,S),(g,g,g)))
# Existing brick relief stays registered to its source artwork but receives stronger slopes.
n=np.asarray(maps['N'].crop((0,0,S,S))).astype(float)/255*2-1
n[:,:,:2]*=2.1;n/=np.maximum(np.linalg.norm(n,axis=2,keepdims=True),1e-8)
put('N',0,Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255)))
for ch,im in maps.items():im.save(OUT/'textures'/f'{NAME}_{ch}.png')
(OUT/'texture-provenance.json').write_text(json.dumps({'generator':'Built-in ImageGen','source':str(SOURCE),'palette':'CSC_Atlas_B_BAKERS_2.dds','replaced_cells':{'2':'12-seam bright Bakers_2 green roof','7':'dark timber window, stone lintel and sill, deep glass','8':'continuous warm timber replacing unused door cell'},'normal_notes':'Brick slopes 2.1x; window authored glass depth -2, lintel 1.1, sill 1.5 world units; measured roof seams. AO rebaked from geometry.','roof_seam_centres_pixels':peaks},indent=2))
print('MATERIALS_READY',peaks)
