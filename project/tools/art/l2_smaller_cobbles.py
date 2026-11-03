"""25%-smaller paving with complete-stone exclusion from road03."""
import sys,json,shutil
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage as ndi
import l2_stone_edges as edges
from l2_placement_migration import OUT,ART,write

REV=OUT/'smaller-stones-road-clearance'
edges.REV=REV
edges.SOURCE_ROOT=REV/'scaled-paint'
edges.UV_ORIGIN_SHIFT=[0,0]
edges.ROAD_CLEARANCE=.75
edges.ROAD_ALPHA_THRESHOLD=.35

def quilt():
    """Lay existing whole painted stones into a denser continuous field.

    Reusing individually isolated source stones avoids joins through stone faces.
    Every map uses identical donor selection, transforms and coverage masks.
    """
    from skimage.segmentation import watershed
    REV.mkdir(exist_ok=True);rng=np.random.default_rng(251025)
    for variant,base in edges.VARIANTS:
        source=OUT/'stone-edge-revision/before/cobbles'/variant/'textures'
        dest=edges.SOURCE_ROOT/variant/'textures';dest.mkdir(parents=True,exist_ok=True)
        paths=list(source.glob('*.png'));originals={p.name:np.array(Image.open(p).convert('RGBA')) for p in paths}
        b=originals[base+'_B.png'];h=originals[base+'_H.png'][:,:,0]
        cores,count=ndi.label(ndi.binary_erosion(h>=98,iterations=2));sizes=np.bincount(cores.ravel())
        keep=np.where(sizes>=180)[0];keep=keep[keep!=0];lookup=np.zeros(count+1,np.int32);lookup[keep]=np.arange(1,len(keep)+1)
        labels=watershed(99-ndi.gaussian_filter(h.astype(float),.6),lookup[cores])
        areas=np.bincount(labels.ravel());median=np.median(areas[1:]);border=set(np.unique(np.r_[labels[0],labels[-1],labels[:,0],labels[:,-1]]))
        donors=[];widths=[];heights=[]
        for label in range(1,len(keep)+1):
            if label in border or not .90*median<areas[label]<1.10*median:continue
            yy,xx=np.where(labels==label);xy=np.c_[xx,yy].astype(np.float32)
            hull=cv2.convexHull(xy)
            if areas[label]/max(cv2.contourArea(hull),1)<.96:continue
            rect=cv2.minAreaRect(xy);corners=cv2.boxPoints(rect)
            # Choose the upward-right long side; the other side goes down-right.
            sides=np.roll(corners,-1,axis=0)-corners
            index=max(range(4),key=lambda i: (sides[i,0]>0 and sides[i,1]<0)*100000+np.linalg.norm(sides[i]))
            corners=np.roll(corners,-index,axis=0)
            a=corners[1]-corners[0];v=corners[3]-corners[0]
            if v[0]<0:corners=corners[[1,0,3,2]];a=corners[1]-corners[0];v=corners[3]-corners[0]
            width,height=np.linalg.norm(a),np.linalg.norm(v)
            if variant=='rectangular' and width<height:continue
            matrix=cv2.getPerspectiveTransform(corners,np.float32([[0,0],[95,0],[95,95],[0,95]]))
            whole=np.zeros_like(labels,dtype='uint8');cv2.fillConvexPoly(whole,hull.astype('int32'),255)
            mask=cv2.warpPerspective(whole,matrix,(96,96),flags=cv2.INTER_LINEAR)
            maps={name:cv2.warpPerspective(im,matrix,(96,96),flags=cv2.INTER_LINEAR) for name,im in originals.items()}
            donors.append((mask,maps));widths.append(width);heights.append(height)
        assert len(donors)>40,(variant,len(donors))
        # Preserve each variant's original aspect ratio and orientation, at .75
        # of its median source dimensions. Slight stone variation stays in paint.
        width,height=np.median(widths)*.75,np.median(heights)*.75
        u=np.array([.78,-.625])*width;v=np.array([.78,.625])*height
        results={name:np.zeros((1024,2048,4),np.uint8) for name in originals}
        for name,im in results.items():
            original=originals[name];im[:,:,:3]=np.median(original[h<=88,:3],axis=0);im[:,:,3]=255
        basis=np.column_stack([u,v]);limit=np.array([[0,0],[2048,0],[2048,1024],[0,1024]])@np.linalg.inv(basis).T
        cells=0
        for i in range(int(np.floor(limit[:,0].min()))-2,int(np.ceil(limit[:,0].max()))+2):
            for j in range(int(np.floor(limit[:,1].min()))-2,int(np.ceil(limit[:,1].max()))+2):
                anchor=i*u+j*v+np.array([13,7]);quad=np.float32([anchor,anchor+u,anchor+u+v,anchor+v])
                x0=max(0,int(np.floor(quad[:,0].min())));x1=min(2048,int(np.ceil(quad[:,0].max()))+1)
                y0=max(0,int(np.floor(quad[:,1].min())));y1=min(1024,int(np.ceil(quad[:,1].max()))+1)
                if x0>=x1 or y0>=y1:continue
                mask,maps=donors[rng.integers(len(donors))]
                matrix=cv2.getPerspectiveTransform(np.float32([[0,0],[95,0],[95,95],[0,95]]),np.float32(quad-[x0,y0]))
                weight=cv2.warpPerspective(mask,matrix,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR)[:,:,None]/255
                for name,im in results.items():
                    patch=cv2.warpPerspective(maps[name],matrix,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR)
                    region=im[y0:y1,x0:x1,:3];region[:]=np.rint(region*(1-weight)+patch[:,:,:3]*weight).astype('uint8')
                cells+=1
        for name,im in results.items():Image.fromarray(im).save(dest/name)
        write(REV/(variant+'-quilt.json'),dict(linear_stone_scale=.75,donor_stones=len(donors),laid_stones=cells,
            grid_vectors=[u.tolist(),v.tolist()],channels_share_exact_donor_mapping=True,output_size=[2048,1024]))
        print('WHOLE STONE FIELD',variant,len(donors),cells,flush=True)

def prepare():
    quilt();edges.prepare()
    plan=json.loads((OUT/'cobble-plan.json').read_text());plan['linear_stone_scale']=.75
    write(OUT/'cobble-plan.json',plan);write(REV/'report.json',plan)

def refit():
    edges.prepare()
    plan=json.loads((OUT/'cobble-plan.json').read_text());plan['linear_stone_scale']=.75
    write(OUT/'cobble-plan.json',plan);write(REV/'report.json',plan)

def publish():
    edges.publish('smaller_stones_road_clearance','''# Current paving revision — smaller stones, road clearance

Both square and rectangular stones are 25% smaller in linear dimensions.
Their complete contours stay clear of road03's visible dirt footprint, with a
0.75-unit clearance from its 35% opacity edge (the faint grass halo is excluded).
Colour and height maps share identical alpha
and use the same texture reconstruction. Only grout edges are antialiased.
The shaped support mesh and both Blender/CN6/FGX/GEO exports are updated.

Current report and backups: Desktop/Codex/L2-placement-20261025/smaller-stones-road-clearance/.
Earlier notes below are historical and superseded where they differ.

''')

def validate():
    edges.validate_edges()
    road=np.load(OUT/'road03-mask.npz');rx,ry=road['x'],road['y']
    plan=json.loads((OUT/'cobble-plan.json').read_text());A=np.array(plan['uv_affine'])
    invuv=np.linalg.inv(np.vstack([A.T,[0,0,1]]));T=np.array(json.loads((OUT/'transform.json').read_text())['wrapper'])
    checks=[]
    for variant,base in edges.VARIANTS:
        p=ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants'/variant/'textures'/(base+'_B.png')
        alpha=np.array(Image.open(p))[:,:,3];yy,xx=np.where(alpha>0)
        xy=np.c_[(xx+.5)/alpha.shape[1],(yy+.5)/alpha.shape[0],np.ones(len(xx))]@invuv.T
        world=(T@np.c_[xy[:,:2],np.full(len(xy),24.15),np.ones(len(xy))].T).T[:,:2]
        values=ndi.map_coordinates(road['alpha'],[(ry[0]-world[:,1])/abs(ry[1]-ry[0]),(world[:,0]-rx[0])/(rx[1]-rx[0])],order=1,mode='constant',cval=1)
        assert values.max()<edges.ROAD_ALPHA_THRESHOLD,(variant,values.max())
        checks.append(dict(variant=variant,linear_stone_scale=.75,visible_dirt_road_overlap_pixels=0,road_threshold=edges.ROAD_ALPHA_THRESHOLD,maximum_road_alpha_under_visible_cobbles=float(values.max())))
    write(REV/'installed-road-validation.json',checks);print('ROAD_CLEARANCE_PASS',checks)

def fix_gutter():
    """Remove five AA-only texels at the atlas rim; opaque stones are unchanged."""
    import hashlib
    from l2_placement_migration import textures,MOD
    report=json.loads((OUT/'install-report.json').read_text());changed=[]
    candidates=[p for folder in [OUT/'cobbles/square/textures',OUT/'masters'/edges.NAME/'textures',
        OUT/'masters'/(edges.NAME+'_Rectangular')/'textures'] for p in folder.glob('*.png')]
    candidates += [__import__('pathlib').Path(r['destination']) for r in report['files'] if r['destination'].endswith('.png')]
    for p in set(candidates):
        im=np.array(Image.open(p).convert('RGBA'));alpha=im[:,:,3]
        rim=np.r_[alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]]
        if np.count_nonzero(rim)!=5 or rim.max()!=42:continue
        backup=REV/'gutter-backup'/(hashlib.sha256(str(p).encode()).hexdigest()[:12]+'-'+p.name)
        assert not backup.exists();backup.parent.mkdir(exist_ok=True);shutil.copy2(p,backup)
        alpha[[0,-1],:]=0;alpha[:,[0,-1]]=0;Image.fromarray(im).save(p);changed.append(str(p))
    assert changed
    textures()
    for variant,base in edges.VARIANTS:
        for channel in ['B','H']:
            filename=base+'_'+channel+'.dds';src=OUT/'staged/Textures'/filename
            for dest in [MOD/'Textures'/filename,ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants'/variant/'textures'/filename]:
                backup=REV/'gutter-backup'/(hashlib.sha256(str(dest).encode()).hexdigest()[:12]+'-'+filename)
                shutil.copy2(dest,backup);shutil.copy2(src,dest);changed.append(str(dest))
    for row in report['files']:
        if row['destination'] in changed:row['sha256']=hashlib.sha256(__import__('pathlib').Path(row['destination']).read_bytes()).hexdigest()
    report['gutter_fix']=changed;write(OUT/'install-report.json',report)
    print('GUTTER_FIXED',len(changed))

if __name__=='__main__':globals()[sys.argv[1]]()
