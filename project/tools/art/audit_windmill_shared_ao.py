import sys,json,subprocess,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFilter
import numpy as np
from windmill_tower_integrate import *
OUT=Path(sys.argv[1]);exe,_=helper(OUT/'cache');resolver=Resolver(MOD,DEFAULT_SDK)
ao_mats=set()
for p in (MOD/'Materials').glob('*.mtl'):
    if any(txt(n,'m_ParamName')=='AO' and txt(n,'m_ObjectName')=='CSC_Atlas_AO2' for n in read_xml(p).findall('.//Element')):ao_mats.add(p.stem)
groups={}
for p in (MOD/'Assets').glob('*.ast'):
    for model in read_xml(p).findall('.//m_ModelInstances/Element'):
        geo=txt(model,'m_GeoName')
        for state in model.findall('m_GroupStates/Element'):
            if any(txt(n,'m_ParamName')=='Material' and txt(n,'m_ObjectName') in ao_mats for n in state.findall('.//Element')):
                groups.setdefault(geo,set()).add((txt(state,'m_MeshName'),txt(state,'m_GroupName')))
mask=Image.new('L',(1024,1024));draw=ImageDraw.Draw(mask);done=[]
for geo,bindings in groups.items():
    p=resolver.resolve(geo,'.geo');descriptor=read_xml(p);fgx=resolver.resolve(txt(descriptor.find('m_DataFiles/Element'),'m_RelativePath'),'.fgx',p)
    dest=OUT/'cache'/(hashlib.sha256(fgx.read_bytes()).hexdigest()+'.json')
    if not dest.exists():subprocess.run([str(exe),str(exe.parent),str(fgx),str(dest)],cwd=exe.parent,check=True,capture_output=True)
    raw=json.loads(dest.read_text())
    for d in descriptor.findall('m_Meshes/Element'):
        mesh=next((m for m in raw['meshes'] if m['name']==txt(d,'m_Name')),None)
        if mesh is None:continue
        for g in d.findall('m_Groups/Element'):
            if (mesh['name'],txt(g,'m_Name')) not in bindings:continue
            start=int(g.findtext('m_nFirstPrim'));end=start+int(g.findtext('m_nPrims'))
            for t in mesh['triangles'][start:end]:
                # Granny stores top-origin V already (the Blender renderer flips it).
                xy=[(mesh['vertices'][i]['uv2'][0]*1024,mesh['vertices'][i]['uv2'][1]*1024) for i in t[:3]]
                draw.polygon(xy,fill=255)
            done.append([geo,mesh['name'],txt(g,'m_Name')])
mask=mask.filter(ImageFilter.MaxFilter(7));mask.save(OUT/'AO2-occupied.png');free=np.array(mask)==0
height=np.zeros(1024,dtype=int);rects=[]
for y in range(1024):
    height=np.where(free[y],height+1,0);stack=[]
    for x in range(1025):
        h=height[x] if x<1024 else 0;left=x
        while stack and stack[-1][1]>h:
            left,prev=stack.pop();rects.append(((x-left)*prev,[left,y-prev+1,x,y+1]))
        stack.append((left,h))
rects.sort(reverse=True);print('Largest free AO2 rectangles',rects[:12])
lib=ART/'Textures/CSC_Props/Current';m=json.loads((lib/'atlas/quarter-ao-manifest.json').read_text());quarter=m['pages'][0]['quarters'][0]
print('Bakers allocations',[(f['family'],[a['cell'] for a in f.get('allocations',[])]) for f in quarter['families']])
(OUT/'ao-allocation-audit.json').write_text(json.dumps(dict(AO2_consumers=done,free_rectangles=rects[:30],Bakers=quarter),indent=2,default=int))
