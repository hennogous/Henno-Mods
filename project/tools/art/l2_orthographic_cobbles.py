"""True orthogonal paving with half-stone running bond and road03 clearance."""
import json,sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.segmentation import watershed
import l2_smaller_cobbles as previous
import l2_stone_edges as edges
from l2_placement_migration import OUT,ART,write

REV=OUT/'orthographic-running-bond'
edges.REV=previous.REV=REV
edges.SOURCE_ROOT=REV/'straight-paint'
edges.UV_ORIGIN_SHIFT=[0,0]
edges.ROAD_CLEARANCE=.75
edges.ROAD_ALPHA_THRESHOLD=.35
SIZE=2048
WORLD_SPAN=184.
T=np.array(json.loads((OUT/'transform.json').read_text())['wrapper'])
center=np.linalg.inv(T)@np.array([-170,-45,24.15,1])
# Recover the kit's baked facade orientation from area-weighted vertical faces.
# Fourfold averaging treats the four walls as one orthogonal frame and rejects
# the small hand-shaped deviations in individual beams and plaster triangles.
raw=json.loads((OUT/'native-before/CSC_TAILORS_Tailor.json').read_text())['meshes'][0]
verts=np.array([v['position'] for v in raw['vertices']]);tri=np.array([t[:3] for t in raw['triangles']])
normals=np.cross(verts[tri[:,1]]-verts[tri[:,0]],verts[tri[:,2]]-verts[tri[:,0]])
areas=np.linalg.norm(normals,axis=1);normals/=np.maximum(areas[:,None],1e-10)
vertical=(abs(normals[:,2])<.1)&(areas>2)
angles=np.arctan2(normals[vertical,1],normals[vertical,0]);weights=areas[vertical]
theta=np.angle(np.sum(weights*np.exp(4j*angles)))/4
row_axis=np.array([np.cos(theta),np.sin(theta)]);cross_axis=np.array([-np.sin(theta),np.cos(theta)])
A=np.column_stack([row_axis,-cross_axis])/WORLD_SPAN
A=np.vstack([A,[.5-center[:2]@row_axis/WORLD_SPAN,.5+center[:2]@cross_axis/WORLD_SPAN]])
edges.UV_AFFINE_OVERRIDE=A.tolist()

def donor_faces(variant,base):
    """Rectify existing stone-face paint; discard all old tilted edge shapes."""
    folder=OUT/'stone-edge-revision/before/cobbles'/variant/'textures'
    b=np.array(Image.open(folder/(base+'_B.png')).convert('RGB'))
    h=np.array(Image.open(folder/(base+'_H.png')))[:,:,0]
    core,n=ndi.label(ndi.binary_erosion(h>=98,iterations=2));sz=np.bincount(core.ravel())
    keep=np.where(sz>=180)[0];keep=keep[keep!=0];lookup=np.zeros(n+1,np.int32);lookup[keep]=np.arange(1,len(keep)+1)
    labels=watershed(99-ndi.gaussian_filter(h.astype(float),.6),lookup[core])
    area=np.bincount(labels.ravel());med=np.median(area[1:]);border=set(np.unique(np.r_[labels[0],labels[-1],labels[:,0],labels[:,-1]]))
    donors=[]
    for i in range(1,len(keep)+1):
        if i in border or not .9*med<area[i]<1.1*med:continue
        yy,xx=np.where(labels==i);rect=cv2.minAreaRect(np.c_[xx,yy].astype('float32'))
        corners=cv2.boxPoints(rect)
        matrix=cv2.getPerspectiveTransform(corners,np.float32([[0,0],[95,0],[95,95],[0,95]]))
        paint=cv2.warpPerspective(b,matrix,(96,96),flags=cv2.INTER_LINEAR)[16:80,16:80]
        high=cv2.warpPerspective(h,matrix,(96,96),flags=cv2.INTER_LINEAR)[16:80,16:80]
        valid=high>=96
        if valid.mean()<.80:continue
        # Old bevels/joints cannot introduce false slanted borders into the face.
        indices=ndi.distance_transform_edt(~valid,return_distances=False,return_indices=True)
        paint=paint[indices[0],indices[1]]
        donors.append(paint)
    assert len(donors)>30,(variant,len(donors))
    return donors,np.median(b[h<=88],axis=0)

def paint():
    REV.mkdir(exist_ok=True);rng=np.random.default_rng(251026)
    for variant,base in edges.VARIANTS:
        donors,grout=donor_faces(variant,base)
        dest=edges.SOURCE_ROOT/variant/'textures';dest.mkdir(parents=True,exist_ok=True)
        width,height=(50,50) if variant=='square' else (88,44)
        pitchx,pitchy=width+2,height+2
        color=np.empty((SIZE,SIZE,3),np.uint8);color[:]=grout
        relief=np.zeros((SIZE,SIZE),np.float32);rows=[];stones=0
        for row,y in enumerate(range(-pitchy,SIZE+pitchy,pitchy)):
            offset=(row%2)*pitchx//2
            rows.append(dict(row=row,y=y,offset=offset))
            for x in range(-pitchx+offset,SIZE+pitchx,pitchx):
                x0,x1=max(x,0),min(x+width,SIZE);y0,y1=max(y,0),min(y+height,SIZE)
                if x0>=x1 or y0>=y1:continue
                face=cv2.resize(donors[rng.integers(len(donors))],(width,height),interpolation=cv2.INTER_AREA)
                yy,xx=np.mgrid[:height,:width]
                # Exact rectangle, parallel sides and right angles. Tiny rounded
                # bevel corners retain the painted kit's softness without taper.
                dx=np.minimum(xx+.5,width-xx-.5);dy=np.minimum(yy+.5,height-yy-.5)
                ramp=np.clip(np.minimum(dx,dy)/2.,0,1);ramp=ramp*ramp*(3-2*ramp)
                coverage=np.clip(np.minimum(dx,dy),0,1)
                patch=np.rint(face*coverage[:,:,None]+grout*(1-coverage[:,:,None])).astype('uint8')
                color[y0:y1,x0:x1]=patch[y0-y:y1-y,x0-x:x1-x]
                relief[y0:y1,x0:x1]=ramp[y0-y:y1-y,x0-x:x1-x];stones+=1
        alpha=np.full((SIZE,SIZE),255,np.uint8)
        def output(name,rgb):
            if rgb.ndim==2:rgb=np.repeat(rgb[:,:,None],3,axis=2)
            Image.fromarray(np.dstack([rgb.astype('uint8'),alpha])).save(dest/name)
        output(base+'_B.png',color)
        output(base+'_H.png',np.rint(86+13*relief))
        extra='CSC_ALL_Stage_3_Cobbles_03' if variant=='square' else base
        if variant=='square':output(extra+'_H.png',np.rint(86+13*relief))
        gy,gx=np.gradient(relief);normal=np.dstack([-gx*.65,gy*.65,np.ones_like(relief)])
        normal/=np.linalg.norm(normal,axis=2,keepdims=True)
        output(extra+'_N.png',np.rint((normal*.5+.5)*255))
        for suffix,value in [('AO',255),('G',30),('M',0),('O',255)]:output(extra+'_'+suffix+'.png',np.full_like(relief,value))
        record=dict(variant=variant,projection='orthographic',stone_pixels=[width,height],pitch_pixels=[pitchx,pitchy],
            stone_world_units=[width*WORLD_SPAN/SIZE,height*WORLD_SPAN/SIZE],row_offset_fraction=.5,
            rows=rows,stones=stones,donor_faces=len(donors),texture_size=[SIZE,SIZE],world_span=[WORLD_SPAN,WORLD_SPAN],
            orthogonal_axes=True,parallel_stone_sides=True,all_maps_registered=True)
        write(REV/(variant+'-layout.json'),record);print('ORTHOGONAL_LAYOUT',variant,record['stone_world_units'],stones,flush=True)

def prepare():
    paint();refit()

def refit():
    edges.prepare()
    plan=json.loads((OUT/'cobble-plan.json').read_text());plan.update(layout='Orthogonal running bond',row_offset_fraction=.5,texture_size=[SIZE,SIZE],world_span=[WORLD_SPAN,WORLD_SPAN],facade_source_degrees=float(np.degrees(theta)),rows_parallel_to_front_facade=True)
    write(OUT/'cobble-plan.json',plan);write(REV/'report.json',plan)
    print('FACADE_ALIGNED_ROWS',np.degrees(theta),'source degrees')

def publish():
    edges.publish('orthographic_running_bond','''# Current paving — straight squares/rectangles, staggered rows

The square stones are true 4.49 x 4.49 world-unit squares; rectangular stones
are 7.91 x 3.95 units. Alternate rows are offset by half a stone course.
All texture edges are orthogonal, with no baked perspective, diamond shear or
taper. Both 2048-square atlases map to equal 184 x 184 world-unit extents.
The UV frame rotates rigidly to align rows with the front facade. The game
camera alone supplies perspective. Whole stones stay clear of the
visible road03 edge; colour and height outlines match exactly.

Current sources, exports and runtime files are updated. Backups and checks:
Desktop/Codex/L2-placement-20261025/orthographic-running-bond/.
Earlier notes below are historical where they differ.

''')

def validate():
    previous.validate()
    checks=[]
    for variant,base in edges.VARIANTS:
        record=json.loads((REV/(variant+'-layout.json')).read_text());w,h=record['stone_world_units']
        assert abs(w/h-(1 if variant=='square' else 2))<1e-9
        pitch=record['pitch_pixels'][0]
        assert all(r['offset']==(r['row']%2)*pitch/2 for r in record['rows'])
        inv=np.linalg.inv(np.vstack([A.T,[0,0,1]]));u=inv[:2,0]/SIZE;v=inv[:2,1]/SIZE
        assert abs(u@v)<1e-12 and abs(np.linalg.norm(u)-np.linalg.norm(v))<1e-12
        assert abs(u/np.linalg.norm(u)@row_axis-1)<1e-12
        checks.append(dict(variant=variant,world_aspect=w/h,orthogonal_uv_axes=True,equal_texel_density=True,half_course_offset=True,rows_parallel_to_front_facade=True,facade_source_degrees=float(np.degrees(theta))))
    write(REV/'installed-layout-validation.json',checks);print('ORTHOGONAL_RUNNING_BOND_PASS',checks)

if __name__=='__main__':globals()[sys.argv[1]]()
