import json,math
from pathlib import Path
O=Path.home()/'Desktop/Codex/modern-cafe-v1-20261029';m=json.loads((O/'historical-mesh.json').read_text());c=math.cos(math.radians(28.26));s=math.sin(math.radians(28.26))
def loc(p):x,y,z=p;return [round(c*x-s*y,2),round(s*x+c*y,2),round(z,2)]
for f in m['faces']:
 uv=f['uv'];u=sum(p[0] for p in uv)/len(uv)*2048;v=(.5-sum(p[1] for p in uv)/len(uv))*2048
 if 448<u<594 and 752<v<937 and f['area']>30:
  print('ARCH GLASS',round(f['area']),[loc(m['vertices'][i]) for i in f['v']],[(round(a*2048),round((.5-b)*2048)) for a,b in uv])
print('large roof')
for f in m['faces']:
 uv=f['uv'];u=sum(p[0] for p in uv)/len(uv)*2048;v=(.5-sum(p[1] for p in uv)/len(uv))*2048
 if 420<u<850 and 0<v<410 and f['area']>400:print(round(f['area']),[loc(m['vertices'][i]) for i in f['v']])
