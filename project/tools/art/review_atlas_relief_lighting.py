"""Analytical tangent-space lighting proof for representative actual packed cells."""
from bakery_props_atlas import *
from PIL import Image,ImageDraw
m=json.loads((STAGE/'atlas/manifest.json').read_text());names=['timber','masonry','bound_sackcloth','bakery_brick','bakery_round_crust','bakery_wicker'];sheet=Image.new('RGB',(1000,6*270),(224,222,216));d=ImageDraw.Draw(sheet);light=np.array([-.5,.5,.707]);light/=np.linalg.norm(light)
for row,name in enumerate(names):
 r=next(v for v in m['regions'] if v['name']==name);base=np.array(Image.open(STAGE/'textures/CSC_Props_Shared_01_B.png').crop(r['bounds']).convert('RGB'),float)/255;n=np.array(Image.open(STAGE/'textures/CSC_Props_Shared_01_N.png').crop(r['bounds']).convert('RGB'),float)/127.5-1;n/=np.maximum(np.linalg.norm(n,axis=2,keepdims=True),1e-6)
 for col,(label,color,normal) in enumerate([('B / flat',base,np.broadcast_to([0,0,1],n.shape)),('B / N strength1',base,n),('gray / flat',np.ones_like(base)*.5,np.broadcast_to([0,0,1],n.shape)),('gray / N strength1',np.ones_like(base)*.5,n)]):
  shade=.25+.75*np.maximum(0,np.sum(normal*light,axis=2));rgb=np.uint8(np.clip(color*shade[:,:,None],0,1)*255);tile=Image.fromarray(rgb).resize((240,240),Image.Resampling.NEAREST);sheet.paste(tile,(col*250,row*270+25));d.text((col*250+3,row*270+5),name+' '+label,fill='black')
sheet.save(OUT/'Representative_Normal_Lighting.jpg',quality=95)
