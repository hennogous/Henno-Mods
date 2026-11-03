"""Current calibrated road coverage against the unchanged classical layout."""
from pathlib import Path
import json,hashlib
import numpy as np
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[4]
source=Path(__file__).with_name('coverage.py')
# Reuse the proven raster definitions without running its legacy report writer.
scope={'__file__':str(source)};exec(compile(source.read_text().split("j=json.loads((O/'classical-live.json').read_text())")[0],str(source),'exec'),scope)
A=scope['O'];D=scope['D'];O=A/'vanilla-shoulder-calibration-20261029'
j=json.loads((A/'classical-live.json').read_text());assert hashlib.sha256(Path(j['source']).read_bytes()).hexdigest()==j['sha256'],'Classical source changed; refresh its live geometry first'
old=scope['raster'](j['objects']);objects=[]
for key in ['Roundabout','NW','NE','E','SE','SW','Connector']:
 m=json.loads((A/'models'/f'CSC_Road_{key}_Modern.json').read_text())['meshes'][0];vs=m['vertices'];faces=[f[:3] for f in m['triangles']];objects.append({'vertices':[v[:3] for v in vs],'faces':faces,'uvs':[[vs[i][12],1-vs[i][13]] for f in faces for i in f]})
new=scope['raster'](objects,True);rgb=np.zeros((*old.shape,3))+[29,34,38];rgb+=old[...,None]*[173,103,22];rgb+=new[...,None]*[24,132,175];im=Image.fromarray(rgb.clip(0,255).astype('uint8'));dr=ImageDraw.Draw(im);font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',23);small=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',20)
for name,a in j['anchors'].items():
 p=a['inner'];q=a['outer'];dr.line([scope['pixel'](*p),scope['pixel'](*q)],fill='white',width=2);x,y=scope['pixel'](*q);dr.ellipse((x-5,y-5,x+5,y+5),fill='white');dr.text((x+9,y-5),name,font=font,fill='white')
dr.text((24,18),'Same world scale | amber: classical | cyan: current 15-unit tarmac',font=font,fill='white');dr.text((24,52),'Pale: overlap | five exit centre lines fixed | wider gravel shoulders not yet applied',font=small,fill=(210,215,220));im.save(O/'Classical_Current_Modern_Overlay.png')
routes=json.loads((D/'layout-modules.json').read_text())['routes'];checks=[]
for name,a in j['anchors'].items():
 pts=np.array(routes[name])[-13:];p=np.array(a['inner']);q=np.array(a['outer']);d=q-p;d/=np.linalg.norm(d);error=float(np.max(np.abs((pts[:,0]-p[0])*d[1]-(pts[:,1]-p[1])*d[0])));end=float(np.linalg.norm(pts[-1]-q));assert error<1e-4 and end<1e-4;checks.append({'exit':name,'centerline_error':error,'endpoint_error':end})
(O/'classical-overlay-validation.json').write_text(json.dumps({'classical_source_unchanged':True,'world_scale':1,'exits':checks,'current_tarmac_width':15,'proposed_shoulder_expansion_not_applied':True},indent=2));print('CLASSICAL_OVERLAY_AND_FIVE_EXIT_ALIGNMENT_PASS')
