"""Fit the shared L2 paving to road03; preserve painted RGB and matched B/H alpha."""
import json
from pathlib import Path
import sys
import copy
import shutil
import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import map_coordinates
from scipy.spatial import Delaunay, ConvexHull
from l2_placement_migration import OUT,ROOT,MOD,ART,native,parse,txt,POINTS,MODELS,binding,point_matrix,write,save,before
sys.path.insert(0,str(ROOT/'project/tools/blender'))
from render_ae_asset import Resolver,DEFAULT_SDK,read_xml,texture_bindings

def sample_mesh(mesh,texture,xx,yy,transform=None):
    out=np.zeros((*xx.shape,4),np.float32)
    for tri in mesh['triangles']:
        vs=[mesh['vertices'][i] for i in tri[:3]]
        pos=np.array([v['position'] for v in vs])
        if transform is not None:pos=(transform@np.c_[pos,np.ones(3)].T).T[:,:3]
        a,b,c=pos[:,:2];matrix=np.array([b-a,c-a]).T
        if abs(np.linalg.det(matrix))<1e-8:continue
        hit=(xx>=pos[:,0].min())&(xx<=pos[:,0].max())&(yy>=pos[:,1].min())&(yy<=pos[:,1].max())
        ys,xs=np.where(hit)
        if not len(xs):continue
        sl=np.s_[ys.min():ys.max()+1,xs.min():xs.max()+1]
        bx,by=np.einsum('ij,jkl->ikl',np.linalg.inv(matrix),np.array([xx[sl]-a[0],yy[sl]-a[1]]))
        mask=(bx>=-1e-6)&(by>=-1e-6)&(bx+by<=1+1e-6)
        uv=np.array([v['uv'] for v in vs]);u=uv[0,0]+bx*(uv[1,0]-uv[0,0])+by*(uv[2,0]-uv[0,0]);v=uv[0,1]+bx*(uv[1,1]-uv[0,1])+by*(uv[2,1]-uv[0,1])
        sampled=np.stack([map_coordinates(texture[:,:,ch], [v*(texture.shape[0]-1),u*(texture.shape[1]-1)],order=1,mode='nearest') for ch in range(4)],axis=-1)
        take=mask&(sampled[:,:,3]>out[sl][:,:,3]);out[sl][take]=sampled[take]
    return out

def plot():
    after=len(sys.argv)>2 and sys.argv[2]=='after'
    T=np.array(json.loads((OUT/'transform.json').read_text())['wrapper'])
    bounds=(-285,-60,-165,45);size=900
    x=np.linspace(bounds[0],bounds[1],size);y=np.linspace(bounds[3],bounds[2],size);xx,yy=np.meshgrid(x,y)
    resolver=Resolver(MOD,DEFAULT_SDK)
    road=native('CSC_ALL_Classical_Base_03_Road_Decals');textures={}
    for mat in ['Decal_Parts_Ancient_01','Decal_Parts_Classical_01']:
        mt=resolver.resolve(mat,'.mtl');bind=texture_bindings(read_xml(mt));tex=resolver.resolve(bind['BaseColor'],'.tex')
        textures[mat]=np.asarray(Image.open(resolver.resolve(bind['BaseColor'],'.dds')).convert('RGBA')).astype(float)/255
    canvas=np.ones((size,size,4));canvas[:,:,:3]=(.35,.44,.24)
    roadrgba=np.zeros_like(canvas)
    for mesh in road['meshes']:
        material='Decal_Parts_Classical_01' if '_CLA' in mesh['name'] else 'Decal_Parts_Ancient_01'
        r=sample_mesh(mesh,textures[material],xx,yy)
        alpha=r[:,:,3:4];canvas[:,:,:3]=canvas[:,:,:3]*(1-alpha)+r[:,:,:3]*alpha
        roadrgba[:,:,3]=np.maximum(roadrgba[:,:,3],r[:,:,3])
    source=(OUT/'cobbles/square/textures' if after else ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants/square/textures')/'CSC_ALL_Stage_3_Cobbles_Sq_B.png'
    cobbles=np.asarray(Image.open(source).convert('RGBA')).astype(float)/255
    cm=(json.loads((OUT/'staged/Geometries/CSC_ALL_Stage_3_Cobble_Decals.json').read_text()) if after else native('CSC_ALL_Stage_3_Cobble_Decals'))['meshes'][0]
    r=sample_mesh(cm,cobbles,xx,yy,None if after else T);alpha=r[:,:,3:4]
    canvas[:,:,:3]=canvas[:,:,:3]*(1-alpha)+r[:,:,:3]*alpha
    im=Image.fromarray(np.clip(canvas*255,0,255).astype('uint8'));draw=ImageDraw.Draw(im)
    def pixel(p):return ((p[0]-bounds[0])/(bounds[1]-bounds[0])*(size-1),(bounds[3]-p[1])/(bounds[3]-bounds[2])*(size-1))
    for name,color,matrix in [('CSC_TAILORS_Tailor','#b48ad1',T),('CSC_TAILORS_Tailor_LeanTo','#9272b4',None)]:
        if matrix is None:
            root=parse(OUT/'staged/Assets/CSC_TAILORS_Tailor.ast');p=next(p for p in root.findall(POINTS+'/Element') if binding(p)==name);matrix=point_matrix(p)
        for m in native(name)['meshes']:
            points=(matrix@np.array([[*v['position'],1] for v in m['vertices']]).T).T[:,:2]
            for t in m['triangles']:draw.polygon([pixel(points[i]) for i in t[:3]],fill=color)
    root=parse(OUT/'staged/Assets/CSC_TAILORS_Tailor.ast')
    for p in root.findall(POINTS+'/Element'):
        if 'LeanTo' in binding(p):continue
        M=point_matrix(p);px,py=pixel(M[:2,3]);draw.ellipse((px-3,py-3,px+3,py+3),fill='yellow');draw.text((px+4,py),binding(p).replace('CSC_','').replace('TAILORS_Tailor_',''),fill='white')
    for xg in range(-280,-59,20):
        px,py=pixel((xg,bounds[2]));draw.text((px,py-15),str(xg),fill='white')
    for yg in range(-160,45,20):
        px,py=pixel((bounds[0],yg));draw.text((px,py),str(yg),fill='white')
    im.save(OUT/('Cobble_After_Top.png' if after else 'Cobble_Before_Top.png'))
    np.savez_compressed(OUT/'road03-mask.npz',x=x,y=y,alpha=roadrgba[:,:,3])
    print(OUT/('Cobble_After_Top.png' if after else 'Cobble_Before_Top.png'))

def prepare():
    from render_ae_asset import Assembly
    T=np.array(json.loads((OUT/'transform.json').read_text())['wrapper'])
    raw=native('CSC_ALL_Stage_3_Cobble_Decals');old=raw['meshes'][0]
    oldpos=np.array([v['position'] for v in old['vertices']]);olduv=np.array([v['uv'] for v in old['vertices']])
    # Texture-coordinate affine mapping is unchanged: stone scale and orientation
    # follow the relocated building. The support mesh now follows the edge.
    A=np.linalg.lstsq(np.c_[oldpos[:,:2],np.ones(4)],olduv,rcond=None)[0]
    polygon=np.array([[-216,-17],[-196,4],[-121,19],[-89,-9],[-96,-42],[-110,-69],
        [-127,-94],[-146,-109],[-171,-113],[-195,-109],[-215,-98],[-228,-84],[-233,-67],[-232,-45]],dtype=float)
    polygon=polygon[ConvexHull(polygon).vertices]
    # Two Chaikin passes give a rounded boundary without a dense terrain sheet.
    for _ in range(2):
        nxt=np.roll(polygon,-1,axis=0)
        polygon=np.stack([.75*polygon+.25*nxt,.25*polygon+.75*nxt],axis=1).reshape(-1,2)
    oldxy=(np.linalg.inv(T)@np.c_[polygon,np.full(len(polygon),24.15),np.ones(len(polygon))].T).T[:,:2]
    uv=np.c_[oldxy,np.ones(len(oldxy))]@A
    uv=np.clip(uv,.005,.995)
    oldxy=np.c_[uv,np.ones(len(uv))]@np.linalg.inv(np.vstack([A.T,[0,0,1]])).T
    polygon=(T@np.c_[oldxy[:,:2],np.full(len(uv),24.15),np.ones(len(uv))].T).T[:,:2]
    hull=ConvexHull(polygon)
    def inside(points):return np.max(points@hull.equations[:,:2].T+hull.equations[:,2],axis=-1)<=1e-7
    grid=np.array([(x,y) for x in np.arange(-235,-85,10) for y in np.arange(-115,25,10)])
    grid=grid[inside(grid)]
    points=np.vstack([polygon,grid]);tri=Delaunay(points).simplices
    assert inside(points[tri].mean(axis=1)).all()
    inv=np.linalg.inv(T);oldxy=(inv@np.c_[points,np.full(len(points),24.15),np.ones(len(points))].T).T[:,:2]
    uvs=np.c_[oldxy,np.ones(len(points))]@A
    mesh=copy.deepcopy(old);mesh['vertices']=[]
    for p,uv in zip(points,uvs):
        v=copy.deepcopy(old['vertices'][0]);v['position']=[*p,24.15];v['uv']=uv.tolist()
        for key in ['normal','tangent','binormal']:v[key]=(T[:3,:3]@v[key]).tolist()
        mesh['vertices'].append(v)
    mesh['triangles']=[[*map(int,t),0] for t in tri]
    mesh['groups'][0]['count']=len(tri);raw['meshes']=[mesh]
    geo=parse(before('CSC_ALL_Stage_3_Cobble_Decals','Geometries','.geo'))
    m=geo.find('m_Meshes/Element');m.find('m_nVertexCount').text=str(len(points));m.find('m_nPrimitiveCount').text=str(len(tri));m.find('m_Groups/Element/m_nPrims').text=str(len(tri))
    name='CSC_ALL_Stage_3_Cobble_Decals'
    write(OUT/'staged/Geometries'/(name+'.json'),raw);save(geo,OUT/'staged/Geometries'/(name+'.geo'))
    directory=ART/'Decals/CSC_Stage_3_Cobbles_Two_Variants'
    files=[]
    for variant,base in [('square','CSC_ALL_Stage_3_Cobbles_Sq'),('rectangular','CSC_ALL_Stage_3_Cobbles_02')]:
        source=directory/variant/'textures';dest=OUT/'cobbles'/variant/'textures';dest.mkdir(parents=True,exist_ok=True)
        bpath=source/(base+'_B.png');b=np.array(Image.open(bpath).convert('RGBA'))
        H,W=b.shape[:2]
        # Signed distance in world units, with subtle deterministic irregularity
        # restricted to a narrow edge. The retained RGB painting is byte-exact.
        u,v=np.meshgrid((np.arange(W)+.5)/W,(np.arange(H)+.5)/H)
        source_xy=np.c_[u.ravel(),v.ravel(),np.ones(W*H)]@np.linalg.inv(np.vstack([A.T,[0,0,1]])).T
        world=(T@np.c_[source_xy[:,:2],np.full(W*H,24.15),np.ones(W*H)].T).T[:,:2]
        distance=np.full(W*H,np.inf)
        # Convex edge halfplanes give inward distance, including curved corners.
        for eq in hull.equations:distance=np.minimum(distance,-(world@eq[:2]+eq[2]))
        wiggle=.4*np.sin(world[:,0]*.7+world[:,1]*.39)*np.sin(world[:,1]*.87)
        ramp=np.clip((distance+wiggle)/5.0,0,1);alpha=np.round((ramp*ramp*(3-2*ramp)).reshape(H,W)*255).astype('uint8')
        b[:,:,3]=alpha;Image.fromarray(b).save(dest/bpath.name)
        hpath=source/(base+'_H.png')
        if not hpath.exists():hpath=source/'CSC_ALL_Stage_3_Cobbles_03_H.png'
        h=np.array(Image.open(hpath).convert('RGBA'));h[:,:,3]=alpha
        Image.fromarray(h).save(dest/(base+'_H.png'))
        # Keep the legacy height-source PNG synchronized as well.
        if hpath.name!=base+'_H.png':Image.fromarray(h).save(dest/hpath.name)
        files.extend([dict(source=str(f),destination=str(source/f.name)) for f in dest.glob('*.png')])
        for f in source.glob('*.png'):
            if not (dest/f.name).exists():shutil.copy2(f,dest/f.name)
        write(OUT/'cobbles'/variant/'mask-report.json',dict(size=[W,H],rgb_unchanged=True,matched_height_alpha=True,feather_world_units=5))
    resolver=Resolver(MOD,DEFAULT_SDK);assembly=Assembly(resolver)
    key=assembly.material('CSC_ALL_Stage_3_Cobbles_Sq',{},MOD/'Assets',False)
    material=assembly.materials[key]
    for channel,suffix in [('BaseColor','B'),('Heightmap','H')]:material['textures'][channel]['source']=str(OUT/'cobbles/square/textures'/('CSC_ALL_Stage_3_Cobbles_Sq_'+suffix+'.png'))
    materials=json.loads((OUT/'materials.json').read_text());materials.update(assembly.materials);write(OUT/'materials.json',materials)
    jobs=json.loads((OUT/'geometry-jobs.json').read_text());jobs=[j for j in jobs if j['name']!=name]
    jobs.append(dict(name=name,native=str(OUT/'staged/Geometries'/(name+'.json')),groups={mesh['name']:[txt(g,'m_Name') for g in m.find('m_Groups')]},materials={mesh['name']:{txt(g,'m_Name'):key for g in m.find('m_Groups')}},source=str(directory/'square'/(name+'.blend'))))
    write(OUT/'geometry-jobs.json',jobs)
    write(OUT/'cobble-plan.json',dict(boundary=polygon.tolist(),vertices=len(points),triangles=len(tri),files=files,mesh_area=float(hull.volume),previous_mesh_area=184*120,feather_world_units=5,uv_affine=A.tolist()))
    print('Tight cobble mesh:',len(points),'vertices,',len(tri),'triangles;',round(hull.volume/(184*120)*100),'percent of original support area')

if __name__=='__main__':globals()[sys.argv[1]]()
