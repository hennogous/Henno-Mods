"""Technical paving mask fitted to Henno's saved AE wall and road layout."""
import json,math
from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
from cafe_atlas import ROOT,OUT,SOURCE,sha
CONTRACT=Path(__file__).with_name('cafe_courtyard_fit.json')

def prepare():
    job=json.loads((OUT/'ae-job.json').read_text())
    wall=next(a for a in job['assets'].values() if a['id']=='CSC_ALL_Stage_4_Wall')
    byid={a['id']:a for a in wall['attachments']}
    order=[20,21,22,26,14,24,25,16,27,28,29]
    points=[]
    for n in order:
        a=byid['newAttachmentPoint_'+str(n)]
        shallow=job['assets'][a['asset']]['id'].endswith('_2')
        radius,angle=(192,15) if shallow else (96,30)
        c,s=math.cos(-a['rotation'][2]),math.sin(-a['rotation'][2]);scale=a['scale']
        for theta in np.linspace(-angle/2,angle/2,13):
            t=math.radians(theta);x=radius*math.sin(t)*scale;y=(radius*math.cos(t)-radius)*scale
            points.append([a['position'][0]*10+c*x-s*y,a['position'][1]*10+s*x+c*y])
    wall_count=len(points)
    # Gentle front apron between the saved wall ends; road opacity below supplies
    # the final five-unit setback. The stone painting and card UVs are untouched.
    points += [[206,-1],[197,-10],[175,-17],[151,-17],[128,-12],[108,-2],[92,12],[78,33]]
    contract=dict(points=points,wall_point_count=wall_count,wall_feather=2.5,front_feather=7,road_clearance=5,
                  inputs={p:h for p,h in job['inputs'].items() if p.endswith('.ast')},road_model='CSC_ALL_Classical_Base_05_Road_Decals')
    CONTRACT.write_text(json.dumps(contract,indent=2))
    print('Fit contract:',wall_count,'wall samples; saved ASTs retained')

def make_texture():
    from cafe_courtyard import BOUNDS,SIZE
    cfg=json.loads(CONTRACT.read_text());points=cfg['points'];x0,y0,x1,y1=BOUNDS
    yy,xx=np.mgrid[:SIZE,:SIZE];xx=x0+(xx+.5)*(x1-x0)/SIZE;yy=y1-(yy+.5)*(y1-y0)/SIZE
    mask=Image.new('L',(SIZE,SIZE),0);ImageDraw.Draw(mask).polygon([((x-x0)/(x1-x0)*SIZE,(y1-y)/(y1-y0)*SIZE) for x,y in points],fill=255)
    inside=np.asarray(mask)>0;distance=np.full((SIZE,SIZE),np.inf);feather=np.full((SIZE,SIZE),7.)
    for i,(a,b) in enumerate(zip(points,points[1:]+points[:1])):
        dx,dy=b[0]-a[0],b[1]-a[1];den=dx*dx+dy*dy
        if den<1e-10:continue
        t=np.clip(((xx-a[0])*dx+(yy-a[1])*dy)/den,0,1);d=np.hypot(xx-a[0]-t*dx,yy-a[1]-t*dy)
        nearer=d<distance;feather[nearer]=cfg['wall_feather'] if i<cfg['wall_point_count']-1 else cfg['front_feather'];distance=np.minimum(distance,d)
    t=np.clip(distance*np.where(inside,1,-1)/feather,0,1);alpha=np.uint8(np.rint(255*t*t*(3-2*t)))
    # Rasterize native road triangle UVs into the exact same XY frame.
    records=json.loads((OUT/'ae-world-geometry.json').read_text());job=json.loads((OUT/'ae-job.json').read_text());road=np.zeros((SIZE,SIZE),float)
    textures={m['id']:np.array(Image.open(m['textures']['BaseColor']['source']).convert('RGBA')) for m in job['materials'].values() if m['id'].startswith('Decal_Parts_')}
    for r in records:
        if r['model']!=cfg['road_model']:continue
        tex=textures[r['material']];verts=np.asarray(r['vertices'])
        for face,uv in zip(r['faces'],r['uv']):
            a,b,c=verts[face,:2];den=(b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den)<1e-9:continue
            u=((b[1]-c[1])*(xx-c[0])+(c[0]-b[0])*(yy-c[1]))/den
            v=((c[1]-a[1])*(xx-c[0])+(a[0]-c[0])*(yy-c[1]))/den;w=1-u-v;hit=(u>=0)&(v>=0)&(w>=0)
            uv=np.asarray(uv);tu=u*uv[0,0]+v*uv[1,0]+w*uv[2,0];tv=u*uv[0,1]+v*uv[1,1]+w*uv[2,1]
            ix=np.clip((tu*tex.shape[1]).astype(int),0,tex.shape[1]-1);iy=np.clip(((1-tv)*tex.shape[0]).astype(int),0,tex.shape[0]-1)
            road[hit]=np.maximum(road[hit],tex[iy[hit],ix[hit],3])
    # Smooth texture noise before finding the road's visible edge; individual
    # dirt flecks must not cut jagged notches into the paving perimeter.
    road_smooth=np.asarray(Image.fromarray(np.uint8(road)).filter(ImageFilter.GaussianBlur(5)))
    road_core=road_smooth>=96
    radius=math.ceil(cfg['road_clearance']*SIZE/(x1-x0))
    blocked=Image.fromarray(np.uint8(road_core)*255).filter(ImageFilter.MaxFilter(radius*2+1))
    allowed=Image.fromarray(255-np.asarray(blocked.filter(ImageFilter.MaxFilter(9)))).filter(ImageFilter.GaussianBlur(4))
    alpha=np.minimum(alpha,np.asarray(allowed));alpha[np.asarray(blocked)>0]=0
    src=OUT/'before-fix/CSC_ALL_Stage_4_Cobbles_B.png';base=Image.open(src).convert('RGBA');old=np.array(base)
    base.putalpha(Image.fromarray(alpha));target=OUT/'CSC_ALL_Stage_4_Cobbles_B.png';base.save(target)
    assert np.array_equal(np.array(base)[:,:,:3],old[:,:,:3]);assert not np.any(alpha[road_core])
    assert not any(np.any(a) for a in [alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
    Image.fromarray(alpha).save(OUT/'Courtyard_Opacity.png');Image.fromarray(np.uint8(road)).save(OUT/'Road_Opacity.png')
    report=dict(contract=cfg,base_rgb_unchanged=True,old_alpha_sha256=sha(src),source=str(target),shape_changed=True,road_edge='Native UV alpha smoothed5px, threshold96; five-unit clear band plus soft fade',road_overlap_pixels=int(np.count_nonzero(alpha[road_core])),partial_alpha_pixels=int(np.count_nonzero((alpha>0)&(alpha<255))))
    (OUT/'cobbles-provenance.json').write_text(json.dumps(report,indent=2))

if __name__=='__main__':
    import sys
    if len(sys.argv)>1 and sys.argv[1]=='mask':make_texture()
    else:prepare()
