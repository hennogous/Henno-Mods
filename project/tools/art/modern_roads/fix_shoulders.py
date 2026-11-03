"""Broaden only the Industrial underlay; retain the calibrated tarmac exactly."""
from pathlib import Path
import sys,json,math,shutil
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(Path(__file__).parent))
import raise_tarmac as z
D=z.D;A=z.A;MOD=z.MOD;O=A/'shoulders-fixed-20261029';sha=z.sha;dump=z.dump
SIZES={'roundabout':[236,236],'straight':[168,64],'connector':[168,56],'plain':[78,64],'end':[84,64],'transition':[84,64],'patch':[192,64],'bend':[168,168],'junction':[168,126],'elbow30':[64,64]}

def prepare():
 z.O=O;z.prepare()
 for p in (D/'textures').rglob('*'):
  if p.is_file():q=O/'before/source'/p.relative_to(D);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)

def paint():
 import numpy as np
 from PIL import Image
 import integrate as i
 import calibrate_shoulders as c
 import repair_height as h
 base=json.loads((O/'baseline.json').read_text());manifest=json.loads((D/'atlas-layout.json').read_text());original={ch:np.array(Image.open(D/'textures'/f'CSC_Roads_Industrial_01_{ch}.png').convert('RGBA')) for ch in ['B','H','FOW']};out={ch:a.copy() for ch,a in original.items()}
 measurements=json.loads((A/'vanilla-shoulder-calibration-20261029/measurement.json').read_text())
 row=min(measurements['native'],key=lambda r:abs(np.mean(r['0.5']['shoulder_each_side'])-3.775)+abs(np.mean(r['0.1']['shoulder_each_side'])-13.2)*.4)
 native=json.loads((A/'vanilla-width-calibration-20261029'/(row['geometry']+'.json')).read_text())['meshes'];mesh=next(m for m in native if m['name']==row['underlay']);xy,uv,_=c.unpack(mesh);coeff=np.linalg.lstsq(np.c_[xy,np.ones(len(xy))],uv,rcond=None)[0];normal=np.array(row['normal']);along=np.array([-normal[1],normal[0]]);center=np.array(row['center'])
 native_maps={ch:np.array(Image.open(A.parent/'draft-02-industrial/textures'/f'Decals_Parts_Ancient_01_{ch}.dds').convert('RGBA')) for ch in ['B','H']}
 def bilinear(img,x,y):
  x=np.clip(x,0,img.shape[1]-1.00001);y=np.clip(y,0,img.shape[0]-1.00001);ix=x.astype(int);iy=y.astype(int);fx=(x-ix)[...,None];fy=(y-iy)[...,None]
  return (img[iy,ix]*(1-fx)+img[iy,ix+1]*fx)*(1-fy)+(img[iy+1,ix]*(1-fx)+img[iy+1,ix+1]*fx)*fy
 for key,cell in manifest['cells'].items():
  x0,y0,x1,y1=cell['rect'];w=x1-x0;hh=y1-y0;sx,sy=SIZES[key];ox,oy=cell['size'];x,y=np.meshgrid((np.arange(w)+.5)/w*sx-sx/2,sy/2-(np.arange(hh)+.5)/hh*sy)
  if key=='roundabout':
   rr=np.hypot(x,y);qx=68*x/np.maximum(rr,1e-6);qy=68*y/np.maximum(rr,1e-6);dist=rr-68;arc=np.arctan2(y,x)*68;best=dist**2
   for angle in manifest['roundabout']['angles_degrees']:
    t=math.radians(angle);vx=math.cos(t);vy=math.sin(t);u=x*vx+y*vy;v=-x*vy+y*vx;cl=np.clip(u,68,104);ex=x-cl*vx;ey=y-cl*vy;d2=ex**2+ey**2;take=d2<best;best=np.minimum(best,d2);qx=np.where(take,cl*vx,qx);qy=np.where(take,cl*vy,qy);dist=np.where(take,np.sign(v+1e-9)*np.sqrt(d2),dist);arc=np.where(take,u,arc)
   oldx=qx+(x-qx)/(15/26);oldy=qy+(y-qy)/(15/26)
  elif key=='elbow30':
   angle=np.arctan2(x,y+60);cl=np.clip(angle,-math.pi/12,math.pi/12);qx=60*np.sin(cl);qy=60*np.cos(cl)-60;dist=np.sign(np.hypot(x,y+60)-60+1e-9)*np.hypot(x-qx,y-qy);arc=cl*60;oldx=x;oldy=y
  elif key=='bend':
   rr=np.hypot(x+63,y+63);dist=rr-105;arc=np.arctan2(y+63,x+63)*105;oldx=x;oldy=y
  elif key=='junction':
   d1=np.abs(y+25);d2=np.hypot(x,np.minimum(0,y+25));take=d2<d1;dist=np.where(take,x,y+25);arc=np.where(take,y,x);oldx=x;oldy=y
  else:dist=y;arc=x;oldx=x;oldy=y/(15/26)
  half=18*(15/26)/2 if key=='connector' else 7.5
  # Sample real Firaxis gravel RGB/relief with one world-scale coordinate map.
  repeat=36;u=np.mod(arc+18,repeat*2);u=np.where(u<repeat,u,repeat*2-u)-18
  points=center+u[...,None]*along+dist[...,None]*normal;st=np.concatenate([points,np.ones((*x.shape,1))],axis=2)@coeff
  gravel={ch:bilinear(a,st[:,:,0]*512-.5,st[:,:,1]*512-.5) for ch,a in native_maps.items()}
  # Native alpha modulates the calibrated envelope gently; no synthetic paint.
  variation=np.clip((gravel['B'][:,:,3]/255-.4)*1.2,-.35,.35)
  distance=np.abs(dist)-half-variation
  alpha=np.interp(distance,[-half,0,3.8,8.6,13.2,22],[1,.76,.5,.25,.1,0]);alpha=np.clip(alpha,0,1)
  edge=np.clip((half-np.abs(dist)+1.0)/1.8,0,1)
  tx=x0+.5+(oldx/ox+.5)*(w-1)-.5;ty=y0+.5+(.5-oldy/oy)*(hh-1)-.5
  tx=np.clip(tx,x0,x1-1.00001);ty=np.clip(ty,y0,y1-1.00001)
  stone={ch:bilinear(original[ch],tx,ty) for ch in ['B','H']}
  alpha=np.maximum(alpha,edge*.98)
  if key in ['end','transition','patch']:
   fade=np.clip((sx/2-x)/22,0,1) if key=='end' else np.clip((x+sx/2)/23,0,1) if key=='transition' else np.clip((sx/2-np.abs(x))/8,0,1);alpha*=fade
  if key=='elbow30':alpha*=np.clip((math.pi/12-np.abs(np.arctan2(x,y+60)))*60/1.0,0,1)
  if key=='bend':alpha*=((x>=-63)&(y>=-63))
  # Suppress atlas/card boundary outlines; only end-to-end strip joins stay open.
  if key in ['roundabout','elbow30','bend','junction']:
   border=np.minimum.reduce([x+sx/2,sx/2-x,y+sy/2,sy/2-y]);alpha*=np.clip(border/2,0,1)
  else:alpha*=np.clip((sy/2-np.abs(y))/2,0,1)
  rgb=stone['B'][:,:,:3]*edge[...,None]+gravel['B'][:,:,:3]*(1-edge[...,None]);height=stone['H'][:,:,0]*edge+gravel['H'][:,:,0]*(1-edge)
  b=np.dstack([np.rint(rgb).clip(0,255).astype('uint8'),np.rint(alpha*255).astype('uint8')]);grey=np.rint(height).clip(0,255).astype('uint8');hm=np.dstack([grey,grey,grey,b[:,:,3]])
  out['B'][y0:y1,x0:x1]=b;out['FOW'][y0:y1,x0:x1]=b;out['H'][y0:y1,x0:x1]=hm
  for ch in ['B','H','FOW']:
   data=out[ch][y0:y1,x0:x1,:3].copy();out[ch][y0-4:y1+4,x0-4:x1+4,:3]=np.pad(data,((4,4),(4,4),(0,0)),mode='edge')
  cell['industrial_world_size']=SIZES[key]
 (O/'staged/Textures').mkdir(parents=True,exist_ok=True);rows=[]
 for ch,data in out.items():
  p=D/'textures'/f'CSC_Roads_Industrial_01_{ch}.png';assert sha(p)==base[str(p)];Image.fromarray(data).save(p)
  args=[ROOT/'project/tools/directxtex/texconv.exe','-nologo','-y','-m','0','-f','R8G8B8A8_UNORM','--ignore-srgb','-o',O/'staged/Textures']
  if ch in ['B','FOW']:args+=['-srgb']
  i.run(args+[p],O/(p.stem+'-convert.log'));rows.append({'source':str(p),'sha256':sha(p)})
 bm=h.mips(O/'staged/Textures/CSC_Roads_Industrial_01_B.dds');hm=h.mips(O/'staged/Textures/CSC_Roads_Industrial_01_H.dds');assert len(bm)==10 and all(np.max(np.abs(b[:,:,3].astype(int)-hh[:,:,3].astype(int)))<=1 for b,hh in zip(bm,hm))
 manifest['shoulders']['revision']=2;manifest['shoulders']['calibrated_widths']={'alpha50':3.8,'alpha25':8.6,'alpha10':13.2};manifest['shoulders']['paint']='Existing CSC Industrial core plus native Firaxis Ancient gravel RGB/H, geometry-guided projection';manifest['shoulders']['evidence']=str(O)
 dump(D/'atlas-layout.json',manifest);dump(O/'texture-validation.json',rows);dump(O/'paint-reference.json',row);print('WIDE_SHOULDER_MAPS_READY',flush=True)

def build():
 import bpy
 sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
 import decode_blend as dec
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 base=json.loads((O/'baseline.json').read_text());manifest=json.loads((D/'atlas-layout.json').read_text());reports=[];cx,cy=manifest['roundabout']['center']
 for p in sorted(D.rglob('*.blend')):
  assert sha(p)==base[str(p)]
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  objects={o.name:o for s in bpy.data.scenes for o in s.objects};groups={}
  for ob in objects.values():
   if ob.type=='MESH' and any(s.material and s.material.name.startswith('CSC_Roads_Industrial_01') for s in ob.material_slots):groups.setdefault(ob.data.as_pointer(),[]).append(ob)
  for obs in groups.values():
   old=obs[0].data;me=old.copy()
   for ob in obs:ob.data=me
   name=obs[0].name
   if 'Roundabout' in name:
    uv={li.vertex_index:tuple(me.uv_layers[0].data[li.index].uv) for li in me.loops};a,b,c,d=manifest['cells']['roundabout']['rect']
    for v in me.vertices:
     u,w=uv[v.index];v.co.x=cx+((u*512-a-.5)/(c-a-1)-.5)*236;v.co.y=cy+((w*512-(512-d+.5))/(d-b-1)-.5)*236
   elif 'Elbow30' in name:
    for v in me.vertices:v.co.x*=64/42;v.co.y*=64/26
   else:
    oldwidth=(30 if 'Connector' in name else 36)*(15/26);newwidth=56 if 'Connector' in name else 64
    for k in range(0,len(me.vertices),2):
     a,b=me.vertices[k:k+2];mid=(a.co+b.co)/2;a.co=mid+(a.co-mid)*newwidth/oldwidth;b.co=mid+(b.co-mid)*newwidth/oldwidth
   me.update()
  if groups:
   for s in bpy.data.scenes:s['shoulder_alpha50']=3.8;s['shoulder_alpha10']=13.2
   bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(p),relative_remap=False)
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();meshes=[]
  for ob in bpy.context.scene.objects:
   if ob.type!='MESH':continue
   m=dec.decode_mesh(ob,ob.matrix_world);m['name']=p.stem if p.parent.name=='modules' else ob.name
   for mat in m['materials']:mat['external']=mat['name']
   meshes.append(m)
  check=validate_current_scene();assert check['automated_pass'],check['findings'];dump(O/'models'/(p.stem+'.json'),{'asset_id':p.stem,'kind':'decal','meshes':meshes});reports.append({'id':p.stem,'source':str(p),'sha256':sha(p),'automated_pass':True,'industrial_meshes':sum(m['materials'][0]['name']=='CSC_Roads_Industrial_01' for m in meshes)})
 dump(O/'saved-validation.json',reports);print('WIDE_SHOULDER_SOURCES_PASS',len(reports),flush=True)

def stage():
 import narrow_roads as n
 n.O=O;n.STAGE_IDS={r['id'] for r in json.loads((O/'saved-validation.json').read_text()) if r['industrial_meshes'] and r['id']!='CSC_ALL_Modern_Roundabout_Kit'};n.stage()

def fix_turns():
 import bpy
 from collections import Counter
 sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
 import decode_blend as dec
 from csc_scene_validation import suspend_csc_repairs,validate_current_scene
 rows=json.loads((O/'saved-validation.json').read_text());changes=[]
 for row in rows:
  if not row['industrial_meshes']:continue
  p=Path(row['source']);assert sha(p)==row['sha256']
  with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
  seen=set();edits=0
  for ob in {o.name:o for s in bpy.data.scenes for o in s.objects}.values():
   if ob.type!='MESH' or not any(s.material and s.material.name.startswith('CSC_Roads_Industrial_01') for s in ob.material_slots) or 'Roundabout' in ob.name or 'Elbow30' in ob.name or ob.data.as_pointer() in seen:continue
   me=ob.data;seen.add(me.as_pointer());centers=[(me.vertices[k].co+me.vertices[k+1].co)/2 for k in range(0,len(me.vertices),2)];aliases={}
   for v in me.vertices:aliases.setdefault(tuple(round(q,3) for q in v.co),[]).append(v.index)
   group={idx:ids for ids in aliases.values() for idx in ids}
   for iteration in range(80):
    me.calc_loop_triangles();bad=[]
    for tri in me.loop_triangles:
     a,b,c=[me.vertices[k].co for k in tri.vertices]
     if (b-a).cross(c-a).z<=1e-6:bad.append(tuple(tri.vertices))
    if not bad:break
    affected=set()
    for tri in bad:
     parity=Counter(k%2 for k in tri).most_common(1)[0][0]
     for k in tri:
      if k%2==parity:affected.update(group[k])
    for k in affected:
     v=me.vertices[k];mid=centers[k//2];v.co=mid+(v.co-mid)*.90
    me.update();edits+=len(affected)
   assert not bad,(p,ob.name,'unresolved fold')
  if edits:
   bpy.context.preferences.filepaths.save_version=0;bpy.ops.wm.save_as_mainfile(filepath=str(p),relative_remap=False)
   with suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(p),load_ui=False,use_scripts=False)
   row['sha256']=sha(p);changes.append({'source':str(p),'vertex_relaxations':edits})
  bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();meshes=[]
  for ob in bpy.context.scene.objects:
   if ob.type!='MESH':continue
   m=dec.decode_mesh(ob,ob.matrix_world);m['name']=p.stem if p.parent.name=='modules' else ob.name
   for mat in m['materials']:mat['external']=mat['name']
   meshes.append(m)
  check=validate_current_scene();assert check['automated_pass'],check['findings'];dump(O/'models'/(p.stem+'.json'),{'asset_id':p.stem,'kind':'decal','meshes':meshes})
 dump(O/'saved-validation.json',rows);dump(O/'tight-turn-repair.json',changes);print('TIGHT_TURN_FOLDS_REMOVED',len(changes),flush=True)

def review():
 import numpy as np,ast
 from PIL import Image,ImageDraw,ImageFont
 import integrate as i
 import calibrate_shoulders as c
 c.O=O;c.MODEL_DIR=O/'models';c.measure()
 report=json.loads((O/'measurement.json').read_text())
 measured=report['summary']['CSC'];assert 3<=measured['0.5']['median_shoulder']<=5 and 12<=measured['0.1']['median_shoulder']<=14.5,measured
 # Reuse the existing orthographic UV renderer for consistent comparison.
 tree=ast.parse(Path(__file__).with_name('calibrate_width.py').read_text());board=next(f for f in tree.body if isinstance(f,ast.FunctionDef) and f.name=='board');raster=next(f for f in board.body if isinstance(f,ast.FunctionDef) and f.name=='raster');scope={'np':np,'Image':Image,'size':900,'extent':700,'textures':{},'i':i};exec(compile(ast.Module(body=[raster],type_ignores=[]),'<road-raster>','exec'),scope)
 font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',26);image=Image.new('RGB',(1800,980),(27,31,35));draw=ImageDraw.Draw(image)
 for j,(label,path,texpath) in enumerate([('Before: tight shoulders',A/'layout-variants-20261029/models/CSC_ALL_Modern_Base_05_Road_Decals.json',O/'before/source/textures'),('Fixed: vanilla-width gravel fade',O/'models/CSC_ALL_Modern_Base_05_Road_Decals.json',D/'textures')]):
  scope['textures']={name:np.array(Image.open(texpath/(name+'_B.png')).convert('RGBA'))/255 for name in ['CSC_Roads_Industrial_01','CSC_Roads_Modern_01']}
  meshes=json.loads(path.read_text())['meshes'];meshes.sort(key=lambda m:'Modern' in m['materials'][0]['name']);im,alpha=scope['raster'](meshes);image.paste(im,(j*900,80));draw.text((j*900+22,18),label,font=font,fill='white')
 image.save(O/'Shoulders_Before_After.png')
 # Actual alpha overlay includes the widened stone/gravel underlay.
 source=Path(__file__).with_name('coverage.py');prefix=source.read_text().split("j=json.loads((O/'classical-live.json').read_text())")[0];cov={'__file__':str(source)};exec(compile(prefix,str(source),'exec'),cov)
 classical=json.loads((A/'classical-live.json').read_text());assert sha(classical['source'])==classical['sha256'];old=cov['raster'](classical['objects'])
 def objs(era):
  out=[]
  for key in ['Roundabout','NW','NE','E','SE','SW','Connector']:
   m=json.loads((O/'models'/f'CSC_Road_{key}_{era}.json').read_text())['meshes'][0];vs=m['vertices'];fs=[f[:3] for f in m['triangles']];out.append({'vertices':[v[:3] for v in vs],'faces':fs,'uvs':[[vs[k][12],1-vs[k][13]] for f in fs for k in f]})
  return out
 paved=cov['raster'](objs('Modern'),True);exec(compile(prefix.replace('CSC_Roads_Modern_01_B.png','CSC_Roads_Industrial_01_B.png'),str(source),'exec'),cov);under=cov['raster'](objs('Industrial'),True);current=1-(1-under)*(1-paved)
 rgb=np.zeros((*old.shape,3))+[29,34,38];rgb+=old[...,None]*[173,103,22];rgb+=current[...,None]*[24,132,175];im=Image.fromarray(rgb.clip(0,255).astype('uint8'));draw=ImageDraw.Draw(im)
 draw.text((24,18),'Same world scale | amber: classical | cyan: fixed modern roads + shoulders',font=font,fill='white')
 for key,v in classical['anchors'].items():
  p=cov['pixel'](*v['outer']);draw.ellipse((p[0]-5,p[1]-5,p[0]+5,p[1]+5),fill='white');draw.text((p[0]+8,p[1]-8),key,font=font,fill='white')
 im.save(O/'Classical_Fixed_Modern_Overlay.png')
 # Existing modern paint and all tarmac vertices/UVs stay identical within export precision.
 for p in (O/'models').glob('*.json'):
  model=json.loads(p.read_text());oldpath=A/'models'/p.name if p.stem.startswith('CSC_Road_') else A/'combined-layout-20261029/model.json' if p.stem=='CSC_ALL_Modern_Base_Road_Decals' else A/'layout-variants-20261029/models'/p.name
  if not oldpath.exists():continue
  oldm={m['name']:m for m in json.loads(oldpath.read_text())['meshes']}
  for m in model['meshes']:
   if m['materials'][0]['name']!='CSC_Roads_Modern_01':continue
   a=oldm[m['name']];assert a['triangles']==m['triangles'] and np.max(np.abs(np.array(a['vertices'])-np.array(m['vertices'])))<.001
 dump(O/'visual-and-width-validation.json',{'shoulder_medians':measured,'tarmac_meshes_unchanged':True,'classical_source_unchanged':True,'same_world_scale_overlay':True});print('SHOULDERS_MEASURED_AND_REVIEW_READY',flush=True)

def publish():
 import integrate as i
 assert json.loads((O/'cook-check/result.json').read_text())['exit_code']==0
 base=json.loads((O/'baseline.json').read_text());rows=json.loads((O/'staging-validation.json').read_text());files=[]
 for r in rows:
  assert sha(r['source'])==r['sha256']
  for ext in ['.geo','.fgx']:assert sha(MOD/'Geometries'/(r['id']+ext))==base[str(MOD/'Geometries'/(r['id']+ext))]
 for r in rows:
  for ext in ['.geo','.fgx']:
   p=MOD/'Geometries'/(r['id']+ext);backup=O/'before/Geometries'/p.name;backup.parent.mkdir(exist_ok=True);shutil.copy2(p,backup);shutil.copy2(O/'staged/Geometries'/p.name,p);files.append({'destination':str(p),'before':base[str(p)],'after':sha(p)})
  shutil.copy2(O/'staged/CN6'/(r['id']+'.cn6'),Path(r['source']).with_suffix('.cn6'))
 for r in json.loads((O/'texture-validation.json').read_text()):
  assert sha(r['source'])==r['sha256'];p=MOD/'Textures'/(Path(r['source']).stem+'.dds');assert sha(p)==base[str(p)];backup=O/'before/Textures'/p.name;backup.parent.mkdir(exist_ok=True);shutil.copy2(p,backup);shutil.copy2(O/'staged/Textures'/p.name,p);shutil.copy2(p,D/'textures/native'/p.name);files.append({'destination':str(p),'before':base[str(p)],'after':sha(p)})
 for path,digest in base.items():
  if Path(path).parent in [MOD/'Assets',MOD/'ArtDefs',MOD/'XLPs',MOD/'Materials'] or 'CSC_Roads_Modern_01' in Path(path).name:assert sha(path)==digest,path
 dump(O/'publication-report.json',{'installed':True,'files':files,'tarmac_textures_preserved':True,'AE_assembly_preserved':True,'shoulder_expansion_applied':True});i.n.cache(O);i.OUT=O;i.verify()
 z.O=O;z.maintain();print('WIDE_SHOULDERS_INSTALLED',flush=True)

if __name__=='__main__':
 mode=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else sys.argv[1];globals()[mode]()
