"""Geometry-contract painting guide and registered technical maps; no procedural B artwork."""
import json,sys,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
OUT=Path(sys.argv[2]);S=512;N=S*4
names=['BUFF BRICK','GREY BLOCK','GREEN ROOF','SILO WRAP','GREEN METAL','IVORY TRIM','DARK IRON','WINDOW','LOADING DOOR','FLOUR SACK','TIMBER','CONCRETE','IVORY PANEL','DARK RECESS','ELEVATOR PANEL','SACK END']
contract=json.loads((OUT/'uv_contract.json').read_text())

def relief(tile):
    h=Image.new('L',(S,S),160);d=ImageDraw.Draw(h)
    def line(points,width=3,fill=100):d.line(points,fill=fill,width=width)
    a=.025*S;b=.975*S;span=b-a
    if tile in (0,1):
        rows=8 if tile==0 else 5;cols=4 if tile==0 else 3
        for r in range(rows+1):line([(a,a+r*span/rows),(b,a+r*span/rows)],4)
        for r in range(rows):
            for c in range(cols+1):
                x=a+(c+(r%2)*.5)*span/cols
                if x<b:line([(x,a+r*span/rows),(x,a+(r+1)*span/rows)],4)
    elif tile==2:
        for i in range(1,6):line([(a+i*span/6,a),(a+i*span/6,b)],6,210)
    elif tile==3:
        for i in (1,2):line([(a,a+i*span/3),(b,a+i*span/3)],3,100)
        for i in (0,4,8,12,16):
            x=a+i*span/16;line([(x,a),(x,b)],2,115)
    elif tile==7:
        d.rectangle((a+20,a+18,b-20,b-18),fill=80)
        d.rectangle((a+36,a+34,b-36,b-34),fill=30)
        line([(S/2,a+20),(S/2,b-20)],18,180);line([(a+20,S/2),(b-20,S/2)],18,180)
    elif tile==8:
        for i in range(1,7):line([(a+i*span/7,a),(a+i*span/7,b)],2,125)
    elif tile==9:
        line([(a+15,a+12),(a+15,b-12)],5,130);line([(b-15,a+12),(b-15,b-12)],5,130)
        line([(a+15,a+12),(b-15,a+12)],5,140);line([(a+15,b-12),(b-15,b-12)],5,140)
    elif tile==10:
        for i in (1,2,3):line([(a+i*span/4,a),(a+i*span/4,b)],5,110)
    elif tile==14:
        for i in (1,2,3):line([(a,a+i*span/4),(b,a+i*span/4)],3,115)
        line([(a+12,a),(a+12,b)],3,115);line([(b-12,a),(b-12,b)],3,115)
    return h.filter(ImageFilter.GaussianBlur(1.5))

if sys.argv[1]=='guide':
    guide=Image.new('RGB',(N,N));d=ImageDraw.Draw(guide)
    for t in range(16):
        color=tuple(int(v*255) for v in contract['palette'][t]);x=(t%4)*S;y=(t//4)*S
        patch=Image.new('RGB',(S,S),color);p=ImageDraw.Draw(patch)
        a=int(.025*S);b=int(.975*S)
        # Project the exact first polygon of the UV-defined surface into each cell.
        surfaces=[s for s in contract['surfaces'] if s['tile']==t]
        if surfaces:
            for s in surfaces[:16 if t==3 else 1]:
                xy=[(int(u*N)-x,int((1-v)*N)-y) for u,v in s['polygon']]
                p.line(xy+[xy[0]],fill=(235,218,179),width=2)
        h=np.asarray(relief(t));base=np.asarray(patch).astype(float);base+=((h.astype(float)-160)*.27)[:,:,None]
        patch=Image.fromarray(np.clip(base,0,255).astype('uint8'));p=ImageDraw.Draw(patch)
        p.rectangle((0,0,S-1,S-1),outline=(95,90,80),width=2)
        p.text((18,18),f'{t+1}: {names[t]}',fill=(255,255,255),stroke_fill=(30,30,25),stroke_width=1)
        if t in (3,9):
            p.line([(S*.5,S*.36),(S*.5,S*.68)],fill=(190,145,57),width=9)
            for k in range(4):
                cy=S*(.40+k*.065)
                p.ellipse((S*.40,cy-20,S*.49,cy+6),fill=(190,145,57));p.ellipse((S*.51,cy-20,S*.60,cy+6),fill=(190,145,57))
        guide.paste(patch,(x,y))
    guide.save(OUT/'02_geometry_atlas_guide.png')
elif sys.argv[1]=='maps':
    source=Path(sys.argv[3]);im=Image.open(source).convert('RGB');assert im.width==im.height
    # Exact pixel resampling only. All final colour is from the supplied ImageGen painting.
    im.resize((1024,1024),Image.Resampling.LANCZOS).save(OUT/'textures'/'CSC_BAKERS_Wind_Mill_Modern_B.png')
    height=Image.new('L',(N,N));gloss=Image.new('L',(N,N));metal=Image.new('L',(N,N))
    for t in range(16):
        xy=((t%4)*S,(t//4)*S)
        # Registered seam landmarks measured from the returned painting. Keep other
        # materials neutral rather than inventing depth from their painted colour.
        h=Image.new('L',(S,S),160);hd=ImageDraw.Draw(h)
        if t==2:
            for x in (.025,.23,.42,.62,.80):hd.line((int(x*S),0,int(x*S),S),fill=195,width=5)
        if t==3:
            for y in (.38,.79):hd.line((0,int(y*S),S,int(y*S)),fill=125,width=3)
            for x in (.28,.73):hd.line((int(x*S),0,int(x*S),S),fill=135,width=2)
        if t==14:
            for y in (.25,.54,.83):hd.line((0,int(y*S),S,int(y*S)),fill=125,width=3)
        height.paste(h.filter(ImageFilter.GaussianBlur(1.2)),xy)
        gloss.paste(Image.new('L',(S,S),[45,38,90,80,85,70,110,145,65,30,35,35,75,20,85,25][t]),xy)
        # Painted metal is dielectric; bare iron alone gets meaningful metalness.
        metal.paste(Image.new('L',(S,S),140 if t==6 else 0),xy)
    height=height.resize((1024,1024),Image.Resampling.LANCZOS);height.save(OUT/'textures'/'AUTHORED_RELIEF.png')
    h=np.array(height).astype(float)/255;gy,gx=np.gradient(h);strength=1.15
    norm=np.stack([-gx*strength,gy*strength,np.ones_like(h)],axis=-1);norm/=np.linalg.norm(norm,axis=-1,keepdims=True)
    Image.fromarray(np.uint8(np.clip((norm*.5+.5)*255,0,255))).save(OUT/'textures'/'CSC_BAKERS_Wind_Mill_Modern_N.png')
    for key,im in [('G',gloss),('M',metal)]:im.resize((1024,1024),Image.Resampling.LANCZOS).convert('RGB').save(OUT/'textures'/f'CSC_BAKERS_Wind_Mill_Modern_{key}.png')
    Image.new('RGB',(16,16)).save(OUT/'textures'/'CSC_BAKERS_Wind_Mill_Modern_E.png')
    (OUT/'texture_provenance.json').write_text(json.dumps({'base_colour':'ImageGen painting, exact square registration and downsample only','source':str(source),'normal':'Authored metal seams registered to measured painted landmarks; neutral normal on masonry/cloth/window/timber, never derived from B luminance','gloss_metalness':'Semantic material masks','AO':'Geometry UV2 bake'},indent=2))
