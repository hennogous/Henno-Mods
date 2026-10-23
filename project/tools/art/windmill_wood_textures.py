"""Replace only the former plaster slot with ImageGen wood and registered PBR."""
from pathlib import Path
import sys,json,shutil,hashlib,subprocess,importlib.util
import numpy as np
from PIL import Image,ImageFilter
ROOT=Path(__file__).resolve().parents[3];OUT=Path(sys.argv[1]);ART=Path.home()/'Desktop/Working Files/3D Art';TEX=ART/'Textures';MOD=ROOT/'Civ Supply Chains'
B_NAMES=['CSC_Atlas_B_BAKERS','CSC_Atlas_B_BAKERS_2','CSC_Atlas_B_TAILORS','CSC_Atlas_B_TAILORS_2']
GENERATED=Path.home()/'.codex/generated_images/01a15cd5-8d3c-7513-9b6b-b58e5c4c9105'
for d in ['artwork','staged-textures','staged/Textures','before-textures','scalar','staged-xcf','before-xcf']:(OUT/d).mkdir(parents=True,exist_ok=True)
for name,src in [('Wood_B','exec-f220e29d-b002-4e4c-86a6-919f01f41e4f.png'),('Wood_H','exec-ce7f5706-f386-4b69-98d7-bb4b31f8c4d6.png')]:shutil.copy2(GENERATED/src,OUT/'artwork'/(name+'.png'))
color=Image.open(OUT/'artwork/Wood_B.png').convert('RGB').resize((128,128),Image.Resampling.LANCZOS)
height=Image.open(OUT/'artwork/Wood_H.png').convert('L').resize((128,128),Image.Resampling.LANCZOS).filter(ImageFilter.GaussianBlur(.45))
h=np.array(height,dtype=float)/255;gy,gx=np.gradient(h)
# Strong edge relief; the painted raised-brace height, not albedo darkness,
# determines its outward relief. Preserve the existing atlas's normal convention.
n=np.dstack((-gx*12,-gy*12,np.ones_like(h)));n/=np.linalg.norm(n,axis=2)[...,None]
normal=Image.fromarray(np.uint8(np.clip(n*.5+.5,0,1)*255))
maps={'B':color,'N':normal,'G':Image.fromarray(np.uint8(32+h*12)).convert('RGB'),'M':Image.new('RGB',(128,128),(0,0,0))}
rows=[]
for channel,im in maps.items():
    patch=Image.fromarray(np.pad(np.array(im),((2,2),(2,2),(0,0)),mode='edge'));patch.save(OUT/'artwork'/('Wood_'+channel+'_slot.png'))
for name in B_NAMES+['CSC_Atlas_N','CSC_Atlas_G','CSC_Atlas_M']:
    path=TEX/(name+'.dds');shutil.copy2(path,OUT/'before-textures'/path.name)
    old=Image.open(path).convert('RGBA');new=old.copy();channel='B' if name in B_NAMES else name.rsplit('_',1)[1]
    new.paste(Image.open(OUT/'artwork'/('Wood_'+channel+'_slot.png')).convert('RGBA'),(512,614));new.save(OUT/'staged-textures'/(name+'.png'))
    a=np.array(old);b=np.array(new);a[614:746,512:644]=b[614:746,512:644];assert np.array_equal(a,b)
    rows.append(dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
spec=importlib.util.spec_from_file_location('conv',ROOT/'project/tools/blender/scene_export/export_scene.py');conv=importlib.util.module_from_spec(spec);spec.loader.exec_module(conv)
for name in B_NAMES+['CSC_Atlas_N','CSC_Atlas_G','CSC_Atlas_M']:
    scalar=name.endswith(('_G','_M'));src=OUT/'staged-textures'/(name+'.png');fmt='R8_UNORM' if scalar else 'R8G8B8A8_UNORM'
    if scalar:
        p=OUT/'scalar'/src.name;Image.open(src).getchannel('R').save(p);src=p
    subprocess.run([str(ROOT/'project/tools/directxtex/texconv.exe'),'-nologo','-y','-m','0','-f',fmt,'--ignore-srgb','-o',str(OUT/'staged/Textures'),str(src)],check=True)
    dds=OUT/'staged/Textures'/(name+'.dds');desc=dict(size=[1024,1024],format=fmt,slot=name.rsplit('_',1)[1])
    if scalar:conv.normalize_ao_dds(dds,desc,MOD/'Textures/CSC_Atlas_AO2.dds')
    conv.validate_dds(dds,desc);shutil.copy2(MOD/'Textures'/(name+'.tex'),OUT/'staged/Textures'/(name+'.tex'))
(OUT/'texture-baseline.json').write_text(json.dumps(rows,indent=2))
(OUT/'wood-slot.json').write_text(json.dumps(dict(outer=[512,614,644,746],inner=[514,616,642,744],artwork='ImageGen albedo + registered height',normal_strength=12,brace_geometry=False,replaces='tower_plaster',outside_pixels_preserved=True),indent=2))
