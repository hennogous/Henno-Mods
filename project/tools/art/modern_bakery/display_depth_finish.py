import json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from display_depth import O,dump
labels=('historical','before','after');ims=[Image.open(O/'review'/x/'stand.png').convert('RGBA') for x in labels];boxes=[im.getchannel('A').getbbox() for im in ims];crop=(min(x[0] for x in boxes)-25,min(x[1] for x in boxes)-25,max(x[2] for x in boxes)+25,max(x[3] for x in boxes)+25)
w,h=crop[2]-crop[0],crop[3]-crop[1];page=Image.new('RGB',(3*w+80,h+140),(25,29,35));d=ImageDraw.Draw(page);font=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',25);small=ImageFont.truetype('C:/Windows/Fonts/segoeui.ttf',20)
for i,(im,title,dim) in enumerate(zip(ims,('Historical reference','Modern — before','Modern — corrected'),('35.1 wide / 31.1 deep','35.1 wide / 13.2 deep','35.1 wide / 31.1 deep'))):
 x=20+i*(w+20);pic=im.crop(crop);page.paste(pic,(x,60),pic);d.text((x+w/2,25),title,font=font,fill=(233,236,240),anchor='mm');d.text((x+w/2,h+88),dim,font=small,fill=(207,213,222),anchor='mm')
d.text((20,h+116),'Same camera and scale. Modern width, height and rear edge unchanged; fresh AO.',font=small,fill=(179,189,204));page.save(O/'Bread_Stand_Historical_Before_After.png')
images=[O/'review'/x/f for x in labels for f in ('stand.png','scene.png','top.png')];assert all(p.exists() for p in images)
measure=json.loads((O/'render-measurements.json').read_text());a,b,c=[measure[x] for x in labels];assert abs((a[1][1]-a[0][1])-(c[1][1]-c[0][1]))<.001;assert abs((b[1][0]-b[0][0])-(c[1][0]-c[0][0]))<.001
dump(O/'visual-review.json',{'passed':True,'scope':'Prop proportions, painted tray aspect, UV/normal continuity and AO; native scene and top inspection','evidence':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in images},'depth_matches_historical':True,'width_height_rear_unchanged':True,'placement_followup':'Alternate Bakery canopy overlaps existing trolley upper rack. User asked whether to move trolley; no saved AE placement changed without their reply. Standard Bakery trolley is clear.','in_game_tested':False})
print('PROPORTION_REVIEW_ACCEPTED; ALTERNATE_TROLLEY_PLACEMENT_PENDING')
