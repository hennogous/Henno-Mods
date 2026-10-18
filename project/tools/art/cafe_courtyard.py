"""Technical courtyard mask and mapping for ImageGen straight cobbles.

XY uses the generic L3 building's baked coordinate frame. No new surface painting.
"""
import json, math
from cafe_atlas import ART, SOURCE, OUT, sha

BOUNDS = (32., -42., 264., 190.)
SIZE = 512
FEATHER = 7.
TEXTURE_CLOCKWISE_DEGREES = 30.
TEXTURE_REPEAT_WORLD = 60.
BACK_WALL_V = 27.
SCREEN_RIGHT_WALL_U = -45.
RIGHT_EXTENSION_FACTOR = 2.2

def outline():
    # Rear/side arc follows the inside of the approved radius96 crescent.
    points = [(159+93*math.cos(math.radians(a)),62+93*math.sin(math.radians(a)))
              for a in range(-35,206,3)]
    # A shallower, broad forecourt meets the road between the wall ends.
    points += [(80,14),(92,2),(108,-10),(128,-20),(151,-25),
               (175,-25),(197,-20),(216,-10),(231,3)]
    fitted=[]
    for x,y in points:
        u=math.cos(math.pi/6)*(x-146)-.5*(y-77)
        v=.5*(x-146)+math.cos(math.pi/6)*(y-77)
        # In Henno's front-at-top AE view, screen right is the negative local U side.
        if u<SCREEN_RIGHT_WALL_U:
            u=SCREEN_RIGHT_WALL_U+(u-SCREEN_RIGHT_WALL_U)*RIGHT_EXTENSION_FACTOR
        # Halve only paving behind the actual rear wall, preserving the forecourt.
        if v>BACK_WALL_V:v=BACK_WALL_V+(v-BACK_WALL_V)*.5
        fitted.append((146+math.cos(math.pi/6)*u+.5*v,77-.5*u+math.cos(math.pi/6)*v))
    return fitted

def make_texture():
    import numpy as np
    from PIL import Image, ImageDraw, ImageFilter
    src=SOURCE/'textures/CSC_Cafe_Warm_Limestone_Source.png'
    rgb=Image.open(src).convert('RGB').resize((512,512),Image.Resampling.LANCZOS)
    x0,y0,x1,y1=BOUNDS
    # New straight-on painting has four slabs across and eight courses per tile.
    # A 60-unit repeat gives approximately 15 x 7.5 unit slabs, without skew/stretch.
    tiled=Image.new('RGB',(rgb.width*10,rgb.height*10))
    for y in range(10):
        for x in range(10):tiled.paste(rgb,(x*rgb.width,y*rgb.height))
    # Inverse texture-coordinate rotation, independent of the footprint. Oversample
    # before the final reduction to retain square stones and the existing world scale.
    c=math.cos(math.radians(TEXTURE_CLOCKWISE_DEGREES));s=math.sin(math.radians(TEXTURE_CLOCKWISE_DEGREES))
    resolution=2048;step=(x1-x0)/resolution;rho=rgb.width/TEXTURE_REPEAT_WORLD
    affine=(rho*c*step,rho*s*step,rho*(c*(x0-146)-s*(y1-77))+4*rgb.width,
            -rho*s*step,rho*c*step,-rho*(s*(x0-146)+c*(y1-77))+4*rgb.height)
    for px,py in [(0,0),(resolution,0),(0,resolution),(resolution,resolution)]:
        assert 0<=affine[0]*px+affine[1]*py+affine[2]<tiled.width
        assert 0<=affine[3]*px+affine[4]*py+affine[5]<tiled.height
    color=tiled.transform((resolution,resolution),Image.Transform.AFFINE,affine,Image.Resampling.BICUBIC).resize((SIZE,SIZE),Image.Resampling.LANCZOS)
    mask=Image.new('L',(SIZE,SIZE),0)
    ImageDraw.Draw(mask).polygon([((x-x0)/(x1-x0)*SIZE,(y1-y)/(y1-y0)*SIZE) for x,y in outline()],fill=255)
    inside=np.asarray(mask)>0
    yy,xx=np.mgrid[:SIZE,:SIZE]
    xx=x0+(xx+.5)*(x1-x0)/SIZE;yy=y1-(yy+.5)*(y1-y0)/SIZE
    distance=np.full((SIZE,SIZE),float('inf'))
    points=outline()
    for a,b in zip(points,points[1:]+points[:1]):
        dx,dy=b[0]-a[0],b[1]-a[1]
        f=np.clip(((xx-a[0])*dx+(yy-a[1])*dy)/(dx*dx+dy*dy),0,1)
        distance=np.minimum(distance,np.hypot(xx-a[0]-f*dx,yy-a[1]-f*dy))
    distance*=np.where(inside,1,-1)
    # Low-amplitude edge breakup, with a fixed seed for reproducible technical masks.
    noise=np.asarray(Image.fromarray(np.random.default_rng(17).integers(0,256,(SIZE,SIZE),dtype=np.uint8)).filter(ImageFilter.GaussianBlur(2.4)),dtype=float)-127.5
    noise=noise/(noise.std()+1e-10)*.65
    t=np.clip((distance+noise)/FEATHER,0,1)
    alpha=np.uint8(np.rint(255*t*t*(3-2*t)))
    assert alpha.max()==255 and np.count_nonzero((alpha>0)&(alpha<255))>1000
    assert not np.any(alpha[0]) and not np.any(alpha[-1]) and not np.any(alpha[:,0]) and not np.any(alpha[:,-1])
    previous=OUT/'before-fix/CSC_ALL_Stage_4_Cobbles_B.png'
    if previous.exists():assert np.array_equal(alpha,np.asarray(Image.open(previous).getchannel('A'))),'Courtyard shape/feather changed'
    color.putalpha(Image.fromarray(alpha))
    target=SOURCE/'textures/CSC_ALL_Stage_4_Cobbles_B.png';color.save(target)
    Image.fromarray(alpha).save(OUT/'Courtyard_Opacity.png')
    (OUT/'cobbles-provenance.json').write_text(json.dumps(dict(
        source=str(src),source_sha256=sha(src),derived_texture=str(target),derived_sha256=sha(target),
        colour_pixels_byte_identical=False,new_surface_artwork=True,imagegen='exec-8e627e2a-0495-4380-a434-d56c1f208617',shared_atlas_slot=31,
        color_process='New orthographic ImageGen warm limestone slabs; rigid 30-degree mapping along facade, 60-unit square repeat. No shear or perspective transformation.',
        previous_courtyard_alpha_byte_identical=True,
        clockwise_degrees=TEXTURE_CLOCKWISE_DEGREES,rear_wall_local_v=BACK_WALL_V,rear_depth_multiplier=.5,screen_right_extension_factor=RIGHT_EXTENSION_FACTOR,
        alpha_process='L3 courtyard polygon, inward 7-unit smoothstep distance feather, seeded sub-unit boundary variation.',
        bounds=BOUNDS,outline=outline(),size=[SIZE,SIZE],feather_world_units=FEATHER,
        placement='Identity transform in the generic L3 coordinate frame; do not add the old review translation (159,62).',
        fully_transparent_border=True,partial_alpha_pixels=int(np.count_nonzero((alpha>0)&(alpha<255))))
        ,indent=2))

if __name__=='__main__':make_texture()
