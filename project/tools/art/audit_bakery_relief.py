from bakery_props_atlas import *
from PIL import Image,ImageDraw
m=json.loads((STAGE/'atlas/manifest.json').read_text());r=next(v for v in m['regions'] if v['name']=='bakery_brick');im=Image.open(STAGE/'textures/CSC_Props_Shared_01_B.png').crop(r['bounds']).convert('RGB');a=np.array(im,float);chroma=a[:,:,0]-a[:,:,1];rows=[]
def locate(profile,expected):
 indices=np.arange(max(0,int(expected)-2),min(120,int(expected)+3));i=int(indices[np.argmin(profile[indices])]);delta=0
 if 0<i<119:
  l,c,r=profile[i-1:i+2];den=l-2*c+r
  if den>0:delta=float(np.clip(.5*(l-r)/den,-.5,.5))
 return i+delta
for y in range(10,120,10):
 observed=locate(chroma.mean(axis=1),y-.5);rows.append(dict(axis='horizontal',expected=y-.5,observed=observed,error=observed-(y-.5)))
for row in range(12):
 profile=chroma[row*10+3:row*10+7].mean(axis=0)
 for x in np.arange(5 if row%2==0 else 2.5,118,5):
  observed=locate(profile,x-.5);rows.append(dict(axis='vertical',course=row,expected=x-.5,observed=observed,error=observed-(x-.5)))
report=dict(method='Locate minimum red-minus-green chroma (tan mortar versus red clay), quadratic subpixel fit; joint searches within 2px of guide; horizontal row-average and vertical course-centre samples.',resolution=120,columns=24,courses=12,mean_absolute_error_px=float(np.mean([abs(r['error']) for r in rows])),p95_absolute_error_px=float(np.percentile([abs(r['error']) for r in rows],95)),max_absolute_error_px=max(abs(r['error']) for r in rows),samples=rows)
(OUT/'brick-grid-alignment.json').write_text(json.dumps(report,indent=2));print({k:v for k,v in report.items() if k!='samples'})
regions=['bakery_brick','bakery_round_crust','bakery_cart_timber','masonry','bound_sackcloth','bakery_wicker'];sheet=Image.new('RGB',(960, len(regions)*265),(225,223,218));d=ImageDraw.Draw(sheet)
for i,name in enumerate(regions):
 candidates=[v for v in m['regions'] if v['name']==name]
 if not candidates:continue
 r=candidates[0];y=i*265;d.text((5,y+3),name,fill='black')
 for j,k in enumerate(['B','N']):
  tile=Image.open(STAGE/'textures'/('CSC_Props_Shared_01_'+k+'.png')).crop(r['bounds']).convert('RGB').resize((240,240),Image.Resampling.NEAREST);sheet.paste(tile,(j*240,y+22))
 h=STAGE/'atlas/sources/relief-r030'/(name+'_H16.png')
 if h.exists():
  v=np.array(Image.open(h),float);v=np.uint8(v/65535*255);sheet.paste(Image.fromarray(v).convert('RGB').resize((240,240)),(480,y+22))
 mask=STAGE/'atlas/sources/relief-r030'/(name+'_ScoringMask.png')
 if mask.exists():sheet.paste(Image.open(mask).convert('RGB').resize((240,240)),(720,y+22))
sheet.save(OUT/'Normal_Atlas_Diagnostics.jpg',quality=95)

