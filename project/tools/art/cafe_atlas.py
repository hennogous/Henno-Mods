"""Stage Cafe ImageGen artwork in vacant shared-atlas cells; preserve occupied pixels."""
from pathlib import Path
import json, hashlib, shutil, sys, os
ROOT=Path(__file__).resolve().parents[3]
ART=Path('C:/Users/Shadow/Desktop/Working Files/3D Art')
OUT=Path(os.environ.get('CSC_CAFE_OUTPUT','C:/Users/Shadow/Desktop/Codex/Cafe/revision-02-production'))
SHARED=ART/'Textures/CSC_Props'
STAGE=OUT/'atlas-release'
SOURCE=ART/'Props/Bakers/Cafe_Regular_20261017'
RELEASE=os.environ.get('CSC_CAFE_RELEASE','2026-10-17_Shared_01_r032')
PYTHON=Path('C:/Users/Shadow/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def prepare():
    from PIL import Image, ImageFilter
    import numpy as np
    assert not STAGE.exists(), 'Refuse to reset a staged atlas'
    current=json.loads((SHARED/'CURRENT.json').read_text())
    shutil.copytree(SHARED/'Current',STAGE)
    (SOURCE/'textures').mkdir(parents=True,exist_ok=True)
    baseline={str(p.relative_to(SHARED/'Current')):sha(p) for p in (SHARED/'Current').rglob('*') if p.is_file()}
    (OUT/'atlas-baseline.json').write_text(json.dumps(dict(pointer=current,files=baseline),indent=2))
    src=Path('C:/Users/Shadow/.codex/generated_images/01a149b7-e357-7eb1-b5f3-f085ee00cccf/exec-a09d90e9-14a7-4a2c-a275-ed96fbf2d2cd.png')
    shutil.copy2(src,STAGE/'atlas/sources/cafe_imagegen_six_surfaces.png')
    sheet=Image.open(src).convert('RGB');assert sheet.size==(1536,1024)
    manifest=json.loads((STAGE/'atlas/manifest.json').read_text())
    occupied={r['slot'] for r in manifest['regions']}
    names=['cafe_copper','cafe_ivory_ceramic','cafe_limestone_courses','cafe_chessboard','cafe_open_book','cafe_limestone_coping']
    maps={k:Image.open(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png').convert('RGB') for k in ['B','N','G','M']}
    for i,name in enumerate(names):
        slot=10+i;assert slot not in occupied
        crop=sheet.crop(((i%3)*512,(i//3)*512,(i%3+1)*512,(i//3+1)*512))
        crop.save(STAGE/'atlas/sources'/f'{name}_B.png')
        b=crop.resize((120,120),Image.Resampling.LANCZOS)
        # Technical normal derives gently from the generated artwork; no new painted pattern.
        h=np.asarray(b.convert('L').filter(ImageFilter.GaussianBlur(1.2)),dtype=float)/255
        dy,dx=np.gradient(h);strength=1.1 if i==2 else .25
        norm=np.stack((-dx*strength,dy*strength,np.ones_like(h)),axis=2);norm/=np.linalg.norm(norm,axis=2,keepdims=True)
        normal=Image.fromarray(np.uint8(np.clip((norm*.5+.5)*255,0,255)))
        patches={'B':b,'N':normal,'G':Image.new('RGB',(120,120),(100 if i==0 else 65 if i==1 else 20,)*3),'M':Image.new('RGB',(120,120),(210 if i==0 else 0,)*3)}
        x=(slot%8)*128;y=(slot//8)*128
        for k,patch in patches.items():
            tile=Image.fromarray(np.pad(np.asarray(patch),((4,4),(4,4),(0,0)),mode='edge'))
            maps[k].paste(tile,(x,y))
        manifest['regions'].append(dict(id=slot,slot=slot,name=name,family='cafe',bounds=[x+4,y+4,x+124,y+124],sources={'B':f'sources/{name}_B.png'},provenance='ImageGen exec-a09d90e9; crop and Lanczos resize only for colour; derived technical normal and scalar maps'))
    manifest['reserved_slots']=[x for x in manifest.get('reserved_slots',[]) if x not in range(10,16)]
    manifest['cafe_revision']=RELEASE
    for k,im in maps.items():im.save(STAGE/'textures'/f'CSC_Props_Shared_01_{k}.png')
    (STAGE/'atlas/manifest.json').write_text(json.dumps(manifest,indent=2))
    for p in (STAGE/'textures').glob('*.png'):shutil.copy2(p,SOURCE/'textures'/p.name)
    print('Prepared',RELEASE,'slots 10..15')
def pack_ao(ident,cell):
    from PIL import Image
    p=STAGE/'atlas/sources'/(ident+'_AO128.png')
    Image.open(OUT/(ident+'-AO.png')).convert('RGB').resize((128,128),Image.Resampling.LANCZOS).save(p)
    atlas=STAGE/'textures/CSC_Props_Shared_01_AO.png';im=Image.open(atlas).convert('RGB');im.paste(Image.open(p),cell[:2]);im.save(atlas);shutil.copy2(atlas,SOURCE/'textures'/atlas.name)
    m=json.loads((STAGE/'atlas/quarter-ao-manifest.json').read_text());f=next(f for f in m['pages'][0]['quarters'][0]['families'] if f['family']=='Stage4')
    f['allocations']=[a for a in f.get('allocations',[]) or [] if a['id']!=ident]
    f['allocations'].append(dict(id=ident,cell=cell,source=p.relative_to(STAGE).as_posix(),source_sha256=sha(p),bake='Cycles isolated self AO; 64 samples, 256px raw; 5px dilation, 3.5% inset'))
    (STAGE/'atlas/quarter-ao-manifest.json').write_text(json.dumps(m,indent=2))
def cobbles_mask():
    from cafe_courtyard import make_texture
    make_texture()
if __name__=='__main__':
    if sys.argv[1]=='prepare':prepare()
    elif sys.argv[1]=='ao':pack_ao(sys.argv[2],json.loads(sys.argv[3]))
    elif sys.argv[1]=='cobbles-mask':cobbles_mask()
