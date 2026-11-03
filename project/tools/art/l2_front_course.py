"""Add one road-safe whole-cell course to the approved facade-aligned paving."""
import sys, shutil, json
import l2_orthographic_cobbles as layout
from l2_placement_migration import OUT, write

edges=layout.edges
PRIOR=OUT/'orthographic-running-bond'
REV=OUT/'front-road-extra-course'
layout.REV=layout.previous.REV=edges.REV=REV
edges.SOURCE_ROOT=PRIOR/'straight-paint'
edges.EXTRA_FRONT_COURSE=True

def prepare():
    REV.mkdir(exist_ok=True)
    for variant,_ in edges.VARIANTS:
        shutil.copy2(PRIOR/(variant+'-layout.json'),REV/(variant+'-layout.json'))
    layout.refit()

def publish():
    edges.publish('front_road_extra_course','''# Current paving — additional front course

One neighbouring course of complete stones fills available space along the
front road curve in both patterns. Every added cell preserves the existing
0.75-unit clearance from road03's visible dirt edge. Stone size, stagger,
facade alignment and painted faces are unchanged; colour/height alpha match.
The shared support mesh and both source/export sets follow the extended edge.
Backups and checks: Desktop/Codex/L2-placement-20261025/front-road-extra-course/.
Earlier notes below are historical where they differ.

''')

def validate():
    layout.validate()

def compare():
    import numpy as np
    from PIL import Image
    from scipy import ndimage as ndi
    from scipy.spatial import ConvexHull
    old=json.loads((REV/'before/cobble-plan.json').read_text())
    hull=ConvexHull(np.array(old['boundary']))
    inv=np.linalg.inv(np.vstack([layout.A.T,[0,0,1]]))
    road=np.load(OUT/'road03-mask.npz');rx,ry=road['x'],road['y']
    checks=[]
    for variant,base in edges.VARIANTS:
        oldalpha=np.array(Image.open(REV/'before/cobbles'/variant/'textures'/(base+'_B.png')))[:,:,3]
        newalpha=np.array(Image.open(OUT/'cobbles'/variant/'textures'/(base+'_B.png')))[:,:,3]
        assert np.all(newalpha>=oldalpha),'Existing stones must remain unchanged'
        yy,xx=np.where(newalpha>oldalpha)
        xy=np.c_[(xx+.5)/2048,(yy+.5)/2048,np.ones(len(xx))]@inv.T
        world=(layout.T@np.c_[xy[:,:2],np.full(len(xy),24.15),np.ones(len(xy))].T).T[:,:2]
        overrun=np.max(world@hull.equations[:,:2].T+hull.equations[:,2],axis=1)
        values=ndi.map_coordinates(road['alpha'],[(ry[0]-world[:,1])/abs(ry[1]-ry[0]),(world[:,0]-rx[0])/(rx[1]-rx[0])],order=1,mode='constant',cval=1)
        assert values.max()<edges.ROAD_ALPHA_THRESHOLD
        checks.append(dict(variant=variant,added_alpha_pixels=len(xx),added_pixels_outside_old_mesh=int((overrun>0).sum()),
            maximum_extension_world_units=float(overrun.max()),maximum_road_alpha=float(values.max()),existing_stones_preserved=True))
    write(REV/'addition-validation.json',checks);print(checks)

if __name__=='__main__':globals()[sys.argv[1]]()
