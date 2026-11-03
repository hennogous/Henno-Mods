"""Rebuild a published Modern r001 library from its preserved sources and bakes.

Usage: python scripts/rebuild_modern_atlases.py [library snapshot root]
Writes only the snapshot's textures/ directory. Existing allocations are fixed.
"""
import json,sys
from pathlib import Path
from PIL import Image
import numpy as np

def rebuild(root):
    info=json.loads((root/'library.json').read_text());plan=json.loads((root/'atlas-plan.json').read_text())
    building=info['library']=='CSC_Buildings_Modern';kind='building' if building else 'props'
    old='CSC_BAKERS_Wind_Mill_Modern';target=root/'textures';target.mkdir(exist_ok=True)
    def name(ch):return ('CSC_Atlas_Modern'+('_B_BAKERS' if ch=='B' else '_'+ch)) if building else 'CSC_Props_Modern_01_'+ch
    alloc={int(i):int(i) for i in plan['building']['used_tiles']} if building else {int(i):v for i,v in plan['props']['slots'].items()}
    for ch,color in [('B',(128,128,128)),('N',(128,128,255)),('G',(0,0,0)),('M',(0,0,0))]:
        registered=root/'sources'/('registered_'+ch+'.png')
        if registered.is_file():
            Image.open(registered).save(target/(name(ch)+'.png'))
            continue
        src=Image.open(root/'sources'/f'{old}_{ch}.png').convert('RGB');im=Image.new('RGB',(1024,1024),color)
        for tile,slot in alloc.items():
            x,y=tile%4*512,tile//4*512;p=src.crop((x,y,x+512,y+512)).resize((128,128),Image.Resampling.LANCZOS)
            if ch=='N':
                a=np.asarray(p,dtype=float)/127.5-1;a/=np.maximum(np.linalg.norm(a,axis=2,keepdims=True),1e-8);p=Image.fromarray(np.uint8(np.clip((a+1)*127.5,0,255)))
            grid=4 if building else 8;im.paste(p,(slot%grid*128,slot//grid*128))
        im.save(target/(name(ch)+'.png'))
    emissive=root/'sources/registered_E.png'
    (Image.open(emissive) if emissive.is_file() else Image.new('RGB',(16,16),'black')).save(target/(name('E')+'.png'))
    size=plan['building'].get('AO_size',1024) if building else 2048;ao=Image.new('RGB',(size,size),'white')
    for ident,(page,rect) in plan.get('AO_allocations',plan['props']['AO_allocations']).items():
        if page!=kind:continue
        x0,y0,x1,y1=rect;p=Image.open(root/'bakes'/(ident+'.png')).convert('RGB').resize((x1-x0-8,y1-y0-8),Image.Resampling.LANCZOS);ao.paste(p,(x0+4,y0+4))
        ao.paste(p.crop((0,0,1,p.height)).resize((4,p.height)),(x0,y0+4));ao.paste(p.crop((p.width-1,0,p.width,p.height)).resize((4,p.height)),(x1-4,y0+4))
        ao.paste(p.crop((0,0,p.width,1)).resize((p.width,4)),(x0+4,y0));ao.paste(p.crop((0,p.height-1,p.width,p.height)).resize((p.width,4)),(x0+4,y1-4))
    ao.save(target/(name('AO')+'.png'))
    print('Rebuilt',info['library'])

if __name__=='__main__':rebuild(Path(sys.argv[1]) if len(sys.argv)>1 else Path(__file__).resolve().parents[1])
