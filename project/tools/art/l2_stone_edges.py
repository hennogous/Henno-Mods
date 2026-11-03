"""Stone-aware road-edge revision of the dated L2 migration; no RGB repainting."""
import sys, json, shutil, copy, hashlib
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from scipy.spatial import Delaunay, ConvexHull
from skimage.segmentation import watershed
import cv2
from l2_placement_migration import OUT, ART, MOD, ROOT, write, parse, save

REV=OUT/'stone-edge-revision'
NAME='CSC_ALL_Stage_3_Cobble_Decals'
VARIANTS=[('square','CSC_ALL_Stage_3_Cobbles_Sq'),('rectangular','CSC_ALL_Stage_3_Cobbles_02')]
SOURCE_ROOT=None
UV_ORIGIN_SHIFT=[-.015,-.10]
ROAD_CLEARANCE=None
ROAD_ALPHA_THRESHOLD=.05
UV_AFFINE_OVERRIDE=None
EXTRA_FRONT_COURSE=False

def inspect():
    c=json.loads((OUT/'staged/ae_render_camera_presets.json').read_text())['classes']['L2']['sv']
    print(c)
    M=np.array(c['matrix_world']);s=c['ortho_scale']
    for x,y in [(238,747),(299,779),(352,788),(435,778),(544,724),(607,705),(658,676),(691,650),(700,603)]:
        q=M[:3,3]+M[:3,0]*((x/900-.5+c.get('shift_x',0))*s)+M[:3,1]*((.5-y/900+c.get('shift_y',0))*s)
        q=q-M[:3,2]*q[2]/M[2,2]
        print('red',tuple(np.round(q[:2],2)))
        A=np.array(json.loads((OUT/'cobble-plan.json').read_text())['uv_affine'])
        T=np.array(json.loads((OUT/'transform.json').read_text())['wrapper'])
        old=np.linalg.inv(T)@np.r_[q[:2],24.15,1]
        print('uv',np.r_[old[:2],1]@A)
    for variant,base in VARIANTS:
        h=np.array(Image.open(OUT/'cobbles'/variant/'textures'/(base+'_H.png')))[:,:,0]
        print(variant,'H',np.unique(h,return_counts=True))
        for threshold in [90,92,94,96]:
            a,k=ndi.label(h>threshold);sz=np.bincount(a.ravel())
            print(threshold,k,'large',sum(sz[1:]>300),sorted(sz)[-6:])

def prepare():
    REV.mkdir(exist_ok=True)
    if not (REV/'before').exists():
        for rel in ['cobbles','cobble-plan.json','staged/Geometries','staged/Textures','context','install-report.json']:
            src=OUT/rel;dst=REV/'before'/rel;dst.parent.mkdir(parents=True,exist_ok=True)
            if src.is_dir():shutil.copytree(src,dst)
            else:shutil.copy2(src,dst)
    plan=json.loads((REV/'before/cobble-plan.json').read_text())
    A=np.array(plan['uv_affine']);T=np.array(json.loads((OUT/'transform.json').read_text())['wrapper'])
    # Translate the texture origin towards the road without changing stone size.
    # The previous front edge ran beyond V=1; moving its mapping by twelve world
    # units supplies complete donor courses rather than clipping border stones.
    A[2,:]+=UV_ORIGIN_SHIFT
    if UV_AFFINE_OVERRIDE is not None:A=np.array(UV_AFFINE_OVERRIDE,float)
    invuv=np.linalg.inv(np.vstack([A.T,[0,0,1]]))
    def uv_world(uv):
        xy=np.c_[uv,np.ones(len(uv))]@invuv.T
        return (T@np.c_[xy[:,:2],np.full(len(xy),24.15),np.ones(len(xy))].T).T[:,:2]
    # Front/right traced from the user's red annotation via the saved orthographic
    # ground-plane camera. The river-side and rear extent remain close to v1.
    poly=np.array([[-216,-17],[-196,4],[-121,19],[-89,-9],[-89,-15],[-87,-36],
        [-94,-49],[-105,-65],[-121,-78],[-146,-107],[-167,-116],[-183,-115],
        [-202,-104],[-215,-98],[-228,-84],[-233,-67],[-232,-45]],float)
    target=poly[ConvexHull(poly).vertices]
    for _ in range(2):
        nxt=np.roll(target,-1,axis=0)
        target=np.stack([.75*target+.25*nxt,.25*target+.75*nxt],axis=1).reshape(-1,2)
    eq=ConvexHull(target).equations
    reports=[];masks=[]
    for variant,base in VARIANTS:
        directory=OUT/'cobbles'/variant/'textures'
        texture_source=(SOURCE_ROOT or REV/'before/cobbles')/variant/'textures'
        b=np.array(Image.open(texture_source/(base+'_B.png')).convert('RGBA'))
        h=np.array(Image.open(texture_source/(base+'_H.png')).convert('RGBA'))
        if SOURCE_ROOT:
            for p in texture_source.glob('*.png'):shutil.copy2(p,directory/p.name)
        H,W=b.shape[:2]
        # High flat parts seed individual stones; existing height-map valleys
        # supply the grout boundaries. Discard tiny painted details as seeds.
        cores,count=ndi.label(ndi.binary_erosion(h[:,:,0]>=98,iterations=2))
        sizes=np.bincount(cores.ravel());keep=np.where(sizes>=180)[0];keep=keep[keep!=0]
        lookup=np.zeros(count+1,np.int32);lookup[keep]=np.arange(1,len(keep)+1)
        markers=lookup[cores]
        labels=watershed(99-ndi.gaussian_filter(h[:,:,0].astype(float),.6),markers)
        ids=np.arange(1,len(keep)+1)
        centers=np.array(ndi.center_of_mass(np.ones((H,W)),labels,ids))
        world=uv_world(np.c_[(centers[:,1]+.5)/W,(centers[:,0]+.5)/H])
        road_side=((world[:,1]<-95)&(world[:,0]>-210))|(world[:,0]>-125)
        selected=np.max(world@eq[:,:2].T+eq[:,2],axis=1)<=np.where(road_side,1.4,0)
        # Do not include texture-boundary fragments. The courtyard fits inside
        # the original mapping and retains only complete cells.
        border=np.unique(np.r_[labels[0],labels[-1],labels[:,0],labels[:,-1]])
        selected[border[border>0]-1]=False
        if ROAD_CLEARANCE is not None:
            road=np.load(OUT/'road03-mask.npz');rx,ry=road['x'],road['y']
            forbidden=road['alpha']>=ROAD_ALPHA_THRESHOLD
            distance=ndi.distance_transform_edt(~forbidden,sampling=(abs(ry[1]-ry[0]),abs(rx[1]-rx[0])))
            yy,xx=np.mgrid[:H,:W];allworld=uv_world(np.c_[(xx.ravel()+.5)/W,(yy.ravel()+.5)/H])
            clear=ndi.map_coordinates(distance,[(ry[0]-allworld[:,1])/abs(ry[1]-ry[0]),(allworld[:,0]-rx[0])/(rx[1]-rx[0])],order=1,mode='constant',cval=0).reshape(H,W)
            bad=np.unique(labels[clear<ROAD_CLEARANCE]);selected[bad[bad>0]-1]=False
        added_count=0
        if EXTRA_FRONT_COURSE:
            # Exactly one shared-edge neighbour ring, only along the front road
            # curve. The complete cells must pass the existing road exclusion.
            original=selected.copy()
            adjacent=ndi.binary_dilation(np.r_[False,original][labels])
            neighbours=np.unique(labels[adjacent]);candidate=np.zeros_like(selected)
            candidate[neighbours[neighbours>0]-1]=True
            minimum_clear=ndi.minimum(clear,labels,ids)
            candidate &= ~original & (world[:,1]<-55) & (minimum_clear<10)
            candidate[border[border>0]-1]=False
            candidate[bad[bad>0]-1]=False
            selected |= candidate
            added_count=int(candidate.sum())
        chosen=np.r_[False,selected][labels]
        regions,_=ndi.label(chosen);areas=np.bincount(regions.ravel());areas[0]=0
        chosen=regions==areas.argmax()
        # Subpixel antialiasing at the grout boundary, not a stone-wide fade.
        dist=ndi.distance_transform_edt(chosen)-ndi.distance_transform_edt(~chosen)
        alpha=np.uint8(np.rint(255*np.clip((dist+1.5)/3,0,1)))
        alpha[[0,-1],:]=0;alpha[:,[0,-1]]=0
        b[:,:,3]=alpha;h[:,:,3]=alpha
        Image.fromarray(b).save(directory/(base+'_B.png'));Image.fromarray(h).save(directory/(base+'_H.png'))
        if variant=='square':Image.fromarray(h).save(directory/'CSC_ALL_Stage_3_Cobbles_03_H.png')
        masks.append(alpha>0)
        bg=np.full_like(b[:,:,:3],(83,105,48));aa=alpha[:,:,None]/255
        preview=np.uint8(b[:,:,:3]*aa+bg*(1-aa))
        Image.fromarray(preview).save(REV/(variant+'-whole-stones.png'))
        np.savez_compressed(REV/(variant+'-labels.npz'),labels=labels,selected=selected)
        reports.append(dict(variant=variant,detected_stones=len(keep),retained_stones=int(selected.sum()),
            added_front_stones=added_count,
            rgb_unchanged=SOURCE_ROOT is None,matched_height_alpha=True,edge='Whole stone cells; 3-pixel grout antialiasing'))
    # One shared support mesh encloses the union of both patterns, including
    # their intact outermost stones. Its tight convex outline avoids the old
    # rectangular projection sheet and leaves no opaque stone outside support.
    support=ndi.binary_dilation(np.logical_or.reduce(masks),iterations=5)
    contours,_=cv2.findContours(support.astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    pixels=np.concatenate(contours).reshape(-1,2)
    boundary_world=uv_world((pixels+.5)/[W,H]);hull=ConvexHull(boundary_world)
    boundary=boundary_world[hull.vertices]
    inside=lambda p:np.max(p@hull.equations[:,:2].T+hull.equations[:,2],axis=1)<=1e-7
    grid=np.array([(x,y) for x in np.arange(-240,-75,10) for y in np.arange(-125,25,10)])
    points=np.vstack([boundary,grid[inside(grid)]]);tri=Delaunay(points).simplices
    oldxy=(np.linalg.inv(T)@np.c_[points,np.full(len(points),24.15),np.ones(len(points))].T).T[:,:2]
    uvs=np.c_[oldxy,np.ones(len(points))]@A
    raw=json.loads((REV/'before/staged/Geometries'/(NAME+'.json')).read_text())
    mesh=raw['meshes'][0];template=copy.deepcopy(mesh['vertices'][0]);mesh['vertices']=[]
    for p,uv in zip(points,uvs):
        v=copy.deepcopy(template);v['position']=[*p,24.15];v['uv']=uv.tolist();mesh['vertices'].append(v)
    mesh['triangles']=[[*map(int,t),0] for t in tri];mesh['groups'][0]['count']=len(tri)
    write(OUT/'staged/Geometries'/(NAME+'.json'),raw)
    geo=parse(OUT/'staged/Geometries'/(NAME+'.geo'));m=geo.find('m_Meshes/Element')
    m.find('m_nVertexCount').text=str(len(points));m.find('m_nPrimitiveCount').text=str(len(tri));m.find('m_Groups/Element/m_nPrims').text=str(len(tri))
    save(geo,OUT/'staged/Geometries'/(NAME+'.geo'))
    plan.update(boundary=boundary.tolist(),vertices=len(points),triangles=len(tri),mesh_area=float(hull.volume),
        feather_world_units=0,edge='Whole stones with grout-only antialiasing',stone_reports=reports,
        uv_affine=A.tolist(),texture_origin_uv_shift=UV_ORIGIN_SHIFT,stone_density_unchanged=SOURCE_ROOT is None,
        road_alpha_exclusion_threshold=ROAD_ALPHA_THRESHOLD if ROAD_CLEARANCE else None,road_clearance_world_units=ROAD_CLEARANCE)
    write(OUT/'cobble-plan.json',plan);write(REV/'report.json',plan)
    print('STONE EDGES',reports,'MESH',len(points),len(tri),'AREA',hull.volume)

def publish(revision_key='stone_edge_revision',introduction=None):
    from l2_placement_migration import verify_install
    import os,time
    verify_install(REV/'before/staged/Textures')
    report=json.loads((OUT/'install-report.json').read_text())
    assert revision_key not in report,'Already published'
    pairs=[]
    for ext in ['.fgx','.geo']:
        pairs.append((OUT/'staged/Geometries'/(NAME+ext),MOD/'Geometries'/(NAME+ext)))
    for variant,base in VARIANTS:
        dest=ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants'/variant
        for ch in ['B','H']:
            for ext in ['.dds','.tex']:
                pairs.append((OUT/'staged/Textures'/(base+'_'+ch+ext),MOD/'Textures'/(base+'_'+ch+ext)))
            pairs.append((OUT/'staged/Textures'/(base+'_'+ch+'.dds'),dest/'textures'/(base+'_'+ch+'.dds')))
        for p in (OUT/'cobbles'/variant/'textures').glob('*.png'):
            pairs.append((p,dest/'textures'/p.name))
        for ext in ['.cn6','.fgx','.geo']:
            pairs.append((OUT/'staged/Geometries'/(NAME+ext),dest/'exports'/(NAME+ext)))
    for row in json.loads((OUT/'source-build-report.json').read_text()):
        if not row['name'].startswith(NAME):continue
        src,dst=Path(row['source']),Path(row['destination'])
        pairs.extend([(src,dst),(OUT/'source-export'/(row['name']+'.cn6'),dst.with_suffix('.cn6'))])
        pairs.extend((p,dst.parent/'textures'/p.name) for p in (src.parent/'textures').glob('*.png'))
    records={r['destination']:r for r in report['files']};changed=[]
    def put(dst,data):
        if dst.exists():
            relative=dst.relative_to(ROOT) if dst.is_relative_to(ROOT) else dst.relative_to(ART) if dst.is_relative_to(ART) else Path(dst.name)
            label='workspace' if dst.is_relative_to(ROOT) else 'sources' if dst.is_relative_to(ART) else 'cache'
            backup=REV/'install-backup'/label/relative;backup.parent.mkdir(parents=True,exist_ok=True)
            assert not backup.exists(),backup
            shutil.copy2(dst,backup)
        dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(data)
        row=records.get(str(dst),dict(destination=str(dst),backup=None))
        row['sha256']=hashlib.sha256(data).hexdigest();records[str(dst)]=row;changed.append(str(dst))
    unique={}
    for src,dst in pairs:
        if dst in unique:assert src.read_bytes()==unique[dst].read_bytes(),dst
        unique[dst]=src
    for dst,src in unique.items():put(dst,src.read_bytes())
    cachepath=Path(os.environ['APPDATA'])/'AssetCloud/mod-Civ Supply Chains-asset-deps.json'
    cache=json.loads(cachepath.read_text(encoding='utf-8-sig'));now=int(time.time()*1e7)+116444736000000000
    shape=json.loads((OUT/'cobble-plan.json').read_text())
    for row in cache['Files']:
        if row['Filename'].replace('\\','/')=='Civ Supply Chains/Geometries/'+NAME+'.geo':
            row['Stats']['Vertices']=shape['vertices'];row['Stats']['Faces']=shape['triangles']
            row['Filesize']=(MOD/'Geometries'/(NAME+'.geo')).stat().st_size;row['Timestamp']=now
    cache['Timestamp']=now;put(cachepath,json.dumps(cache,separators=(',',':')).encode())
    readme=ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants/README.md'
    current='''# Shared Stage 3 cobbles — current masters, 25 October 2026

The square and rectangular subfolders now contain the relocated L2 paving.
Both use a tight shared support mesh, extending
to road layout 03 along the approved front/right outline. Each material ends
at complete painted stones: only the grout boundary has a three-pixel
antialiased transition. B/H alpha matches; painted RGB, stone density and
projection height are preserved. The texture origin moves slightly towards
the road to provide complete courses at the front. Exported CN6/FGX/GEO files
are current; see the migration report for mesh counts.

Runtime B/H TEX descriptors watch these subfolders' canonical PNGs. The square
height source is CSC_ALL_Stage_3_Cobbles_Sq_H.png; its legacy 03_H copy is synced.
The old review blend and ZIP packages below are historical, not current masters.

Migration record: project/docs/art/l2-placement-and-fixed-props.md in Henno Mods.
Backups and reviews: Desktop/Codex/L2-placement-20261025/stone-edge-revision/.

## Historical notes before the L2 relocation

'''
    put(readme,((introduction or current)+readme.read_text(encoding='utf-8')).encode('utf-8'))
    report['files']=list(records.values());report[revision_key]=changed
    write(OUT/'install-report.json',report)
    print('PUBLISHED STONE EDGE REVISION',len(changed),'files')

def validate_edges():
    plan=json.loads((OUT/'cobble-plan.json').read_text());A=np.array(plan['uv_affine'])
    invuv=np.linalg.inv(np.vstack([A.T,[0,0,1]]))
    T=np.array(json.loads((OUT/'transform.json').read_text())['wrapper'])
    hull=ConvexHull(np.array(plan['boundary']));results=[]
    for variant,base in VARIANTS:
        source=ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants'/variant/'textures'
        b=np.array(Image.open(source/(base+'_B.png')).convert('RGBA'))
        h=np.array(Image.open(source/(base+'_H.png')).convert('RGBA'))
        assert np.array_equal(b[:,:,3],h[:,:,3])
        for suffix,actual in [('B',b),('H',h)]:
            original=np.array(Image.open((SOURCE_ROOT or REV/'before/cobbles')/variant/'textures'/(base+'_'+suffix+'.png')).convert('RGBA'))
            assert np.array_equal(actual[:,:,:3],original[:,:,:3])
        alpha=b[:,:,3];H,W=alpha.shape
        assert not any(np.any(a) for a in [alpha[0],alpha[-1],alpha[:,0],alpha[:,-1]])
        contours,_=cv2.findContours((alpha>0).astype('uint8'),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
        pixels=np.concatenate(contours).reshape(-1,2);uv=(pixels+.5)/[W,H]
        xy=np.c_[uv,np.ones(len(uv))]@invuv.T
        world=(T@np.c_[xy[:,:2],np.full(len(xy),24.15),np.ones(len(xy))].T).T[:,:2]
        assert np.max(world@hull.equations[:,:2].T+hull.equations[:,2])<0
        results.append(dict(variant=variant,base_height_alpha_identical=True,
            painted_rgb_preserved=True,complete_transparent_texture_border=True,
            all_visible_stone_edges_inside_support_mesh=True))
    write(REV/'installed-edge-validation.json',results);print('INSTALLED_STONE_EDGES_PASS',results)

if __name__=='__main__':globals()[sys.argv[1]]()
