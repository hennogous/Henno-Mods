"""Stage coach additions on the live atlas, preserving Henno's pixel edits."""
from pathlib import Path
import json, hashlib, shutil, subprocess, sys
from PIL import Image
import numpy as np

ROOT = Path(__file__).resolve().parents[3]
LIB = Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Textures\CSC_Props')
OUT = Path(r'C:\Users\Shadow\Desktop\Codex\Fashion-coach-20261013')
STAGE = OUT/'atlas-release'
GEN = Path(r'C:\Users\Shadow\.codex\generated_images\01a1364e-bf69-7d52-975a-263678e15aa4\exec-71590507-1cea-4697-b7d6-b0e511595306.png')

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def prepare():
    OUT.mkdir(parents=True, exist_ok=True)
    assert not STAGE.exists(), 'Do not overwrite a working revision'
    shutil.copytree(LIB/'Current',STAGE)
    shutil.copy2(GEN,OUT/'coach-paint-source.png')
    baseline={str(p.relative_to(LIB/'Current')):sha(p) for p in (LIB/'Current').rglob('*') if p.is_file()}
    (OUT/'live-atlas-baseline.json').write_text(json.dumps(baseline,indent=2))
    m=json.loads((STAGE/'atlas/quarter-ao-manifest.json').read_text())
    edits=[]
    for page in m['pages']:
        im=Image.open(STAGE/'textures'/(page['id']+'.png')).convert('RGB')
        for q in page['quarters']:
            for f in q['families']:
                for c in f.get('allocations',[]):
                    p=STAGE/c['source']; crop=im.crop(c['cell'])
                    if Image.open(p).convert('RGB').tobytes()!=crop.tobytes():
                        shutil.copy2(p,p.with_stem(p.stem+'_BeforeHenno20261013'))
                        crop.save(p); c['source_sha256']=sha(p)
                        c['live_edit_reconciled']='2026-10-13: exact crop of Henno-edited canonical production AO'
                        edits.append(c['id'])
    (STAGE/'atlas/quarter-ao-manifest.json').write_text(json.dumps(m,indent=2))
    subprocess.run([sys.executable,ROOT/'project/tools/blender/pack_csc_prop_ao.py',STAGE],check=True)
    for k in ('01','02'):
        name=f'CSC_Props_Shared_{k}_AO.png'
        assert Image.open(STAGE/'textures'/name).tobytes()==Image.open(LIB/'Current/textures'/name).tobytes()
    im=Image.open(GEN).convert('RGB'); w,h=im.size
    am=json.loads((STAGE/'atlas/manifest.json').read_text())
    specs=[('coach_claret_panel',5,(0,0,w//2,h//2),70,0),
           ('coach_black_leather',6,(w//2,0,w,h//2),55,0),
           ('coach_curtained_window',7,(0,h//2,w//2,h),45,0),
           ('antique_brass',50,(w//2,h//2,w,h),115,200)]
    for name,slot,box,g,metal in specs:
        assert slot in am['reserved_slots']
        sources={}
        for k in 'BNGM':
            p=STAGE/'atlas/sources'/f'{name}_{k}.png';sources[k]=str(p.relative_to(STAGE/'atlas')).replace('\\','/')
            patch=im.crop(box) if k=='B' else Image.new('RGB',(256,256), {'N':(128,128,255),'G':(g,)*3,'M':(metal,)*3}[k])
            patch.save(p)
        x,y=slot%8*128,slot//8*128
        am['regions'].append(dict(id=max(r['id'] for r in am['regions'])+1,name=name,family='metal' if slot==50 else 'coach',slot=slot,bounds=[x+4,y+4,x+124,y+124],sources=sources))
    (STAGE/'atlas/manifest.json').write_text(json.dumps(am,indent=2))
    subprocess.run([sys.executable,STAGE/'scripts/pack_atlas.py'],check=True)
    for k in 'BNGM':
        a=Image.open(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB')
        b=Image.open(LIB/'Current/textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB')
        for r in am['regions'][:-4]:
            x,y=r['slot']%8*128,r['slot']//8*128
            assert a.crop((x,y,x+128,y+128)).tobytes()==b.crop((x,y,x+128,y+128)).tobytes(),(k,r['name'])
    (OUT/'atlas-prepare-report.json').write_text(json.dumps(dict(reconciled_edits=edits,new_slots=[s[1] for s in specs],previous_regions_preserved=True,original_current_unchanged=True),indent=2))
    print('STAGED',edits)

if __name__=='__main__': prepare()
