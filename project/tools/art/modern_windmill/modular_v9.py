"""Extract the approved V8 mill into reusable masters and shared modern atlases.

Run textures/pack with Python; build with Blender. Never rebuild or overwrite V8.
"""
import sys, json, hashlib, math, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
ART = Path.home() / 'Desktop/Working Files/3D Art'
SOURCE = ART / 'BAKERS/Wind Mill/modern/revision-08-concept-roof/CSC_BAKERS_Wind_Mill_Modern.blend'
OLD = 'CSC_BAKERS_Wind_Mill_Modern'
BASE = 'CSC_Level_1_S_Modern'
SILO = 'CSC_BAKERS_Mill_Silo_Modern'
TROLLEY = 'CSC_BAKERS_Flour_Trolley_Modern'
PALLET = 'CSC_BAKERS_Flour_Pallet_Modern'
BMAT = 'CSC_BAKERS_Modern'
PMAT = 'CSC_Props_Modern_01'
BTEX = 'CSC_Atlas_Modern'
PTEX = 'CSC_Props_Modern_01'
# Original 4x4 tiles -> modern shared 8x8 surface slots. Keep historical material families.
PSLOTS = {1:32, 2:51, 3:52, 4:53, 5:54, 6:48, 9:19, 10:2, 11:35, 12:55, 14:7, 15:27}
BNAMES = {0:'brick',1:'battered_stone',2:'green_roof',4:'green_trim',5:'ivory_trim',7:'window',8:'wood_and_dark_green',11:'concrete',13:'recess'}
PNAMES = {1:'stone',2:'green_roof',3:'wheat_silo',4:'green_trim',5:'ivory_trim',6:'dark_iron',9:'flour_sack',10:'pallet',11:'concrete',12:'cream',14:'elevator',15:'sack_ends'}
AO = {BASE:('building',[0,0,512,512]),SILO:('props',[0,0,512,256]),TROLLEY:('props',[0,256,128,384]),PALLET:('props',[128,256,256,384])}

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p, d): Path(p).write_text(json.dumps(d,indent=2),encoding='utf-8')
def texname(kind,ch):
    return (BTEX + ('_B_BAKERS' if ch=='B' else '_'+ch)) if kind=='building' else PTEX+'_'+ch

def textures(out):
    from PIL import Image
    import numpy as np
    out.mkdir(parents=True,exist_ok=False)
    target=out/'textures'; target.mkdir()
    maps={ch:Image.open(SOURCE.parent/'textures'/f'{OLD}_{ch}.png').convert('RGB') for ch in ('B','N','G','M')}
    def resize(im,size,ch):
        im=im.resize(size,Image.Resampling.LANCZOS)
        if ch=='N':
            a=np.asarray(im,dtype=float)/127.5-1;a/=np.maximum(np.linalg.norm(a,axis=2,keepdims=True),1e-8)
            im=Image.fromarray(np.uint8(np.clip((a+1)*127.5,0,255)))
        return im
    defaults={'B':(128,128,128),'N':(128,128,255),'G':(0,0,0),'M':(0,0,0)}
    for kind,alloc in [('building',{i:i for i in BNAMES}),('props',PSLOTS)]:
        for ch,src in maps.items():
            im=Image.new('RGB',(1024,1024),defaults[ch])
            for tile,slot in alloc.items():
                x,y=tile%4*512,tile//4*512
                # Reuse full approved tile, including its existing padded boundary.
                patch=resize(src.crop((x,y,x+512,y+512)),(128,128),ch)
                grid=4 if kind=='building' else 8
                im.paste(patch,(slot%grid*128,slot//grid*128))
            im.save(target/(texname(kind,ch)+'.png'))
        Image.new('RGB',(16,16),'black').save(target/(texname(kind,'E')+'.png'))
        size=1024 if kind=='building' else 2048
        Image.new('RGB',(size,size),'white').save(target/(texname(kind,'AO')+'.png'))
    dump(out/'atlas-plan.json',{'building':{'size':1024,'quadrants':{'stage_2':[0,0,512,512],'stage_3':[512,0,1024,512],'stage_4':[0,512,512,1024],'storage':[512,512,1024,1024]},'used_tiles':BNAMES,'UV1':'V8 UV scaled into top-left quadrant; texture repeat scale unchanged'},'props':{'size':1024,'grid':8,'cell_size':128,'padding':'source tile padding retained; 3.2px equivalent','slots':PSLOTS,'names':PNAMES,'historical_layout_source':str(ART/'Textures/CSC_Props/Current/atlas/manifest.json'),'AO_size':2048,'AO_quarters':'Bakers TL, Tailors TR, Apothecaries BL, Stonemasons BR; other quarter page deferred','AO_allocations':AO},'artwork':'Repacked accepted V8 ImageGen/native artwork; no new procedural artwork','source':str(SOURCE),'source_sha256':sha(SOURCE),'source_maps':{ch:sha(SOURCE.parent/'textures'/f'{OLD}_{ch}.png') for ch in maps}})
    print('TEXTURES_READY',flush=True)

def build(out):
    import bpy
    from mathutils import Vector,Matrix
    sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
    import decode_blend as dec
    from csc_scene_validation import suspend_csc_repairs,validate_current_scene
    before=sha(SOURCE); records=[]
    frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
    def group(o):
        n=o.name.removeprefix('CSC_Fixed_')
        if n.startswith('Truck_'):return TROLLEY
        if n=='Visible_Pallet' or n.startswith('Visible_Stack_'):return PALLET
        if n.startswith(('Silo_','Elevator','Rounded_Transfer','Intake_','Sack_','Visible_Pallet.')):return SILO
        return BASE
    with suspend_csc_repairs():
        for ident in (BASE,SILO,TROLLEY,PALLET):
            bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
            scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene
            scene['asset_id']=ident;review['asset_id']=ident
            # Promote source meshes already added to Export by the preceding verified revision.
            keep=[o for o in scene.objects if o.type=='MESH' and group(o)==ident]
            original={o.name:[list(o.matrix_world@v.co) for v in o.data.vertices] for o in keep}
            for o in list(bpy.data.objects):
                if o.type=='MESH' and o not in keep and not o.get('review_only') and not o.name.startswith('REVIEW_'):
                    bpy.data.objects.remove(o,do_unlink=True)
            rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.name=ident;rig.data.name=ident
            added=[]
            if ident==BASE:
                # Full four-corner shelter in reusable master. Optional group hidden only in mill AST.
                for old,new in [('Shelter_Support_41_-65','Shelter_Support_3_-65'),('Support_Foot_41_-65','Support_Foot_3_-65'),('Shelter_Brace_41','Shelter_Brace_3')]:
                    a=bpy.data.objects['CSC_Fixed_'+old];o=a.copy();o.data=a.data.copy();o.name='CSC_Fixed_'+new
                    scene.collection.objects.link(o);review.collection.objects.link(o)
                    delta=frame.to_3x3()@Vector((-38,0,0));m=o.matrix_world.copy();m.translation+=delta;o.matrix_world=m
                    o['optional_silo_side_support']=True;keep.append(o);added.append(o.name)
            pivot=Vector((0,0,0));rotation=0
            if ident in (TROLLEY,PALLET):
                pts=[o.matrix_world@v.co for o in keep for v in o.data.vertices]
                pivot=Vector(((min(v.x for v in pts)+max(v.x for v in pts))/2,(min(v.y for v in pts)+max(v.y for v in pts))/2,min(v.z for v in pts)))
                rotation=42.3 if ident==PALLET else -32.3
            placement=Matrix.Translation(pivot)@Matrix.Rotation(math.radians(rotation),4,'Z');inv=placement.inverted()
            mat0=bpy.data.materials[OLD];mats={}
            kinds=['building'] if ident==BASE else ['props']
            for kind in kinds:
                mat=mat0.copy();mat.name=BMAT if kind=='building' else PMAT
                for n in mat.node_tree.nodes:
                    if n.type=='TEX_IMAGE' and (n.label or n.name) in ('B','N','G','M','E','AO'):
                        ch=n.label or n.name;im=bpy.data.images.load(str(out/'textures'/(texname(kind,ch)+'.png')),check_existing=False)
                        im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';n.image=im
                mats[kind]=mat
            kind=kinds[0];mat=mats[kind]
            for o in keep:
                # Preserve source object transforms for architecture; new standalone prop frames are explicit.
                if ident in (TROLLEY,PALLET):o.matrix_world=inv@o.matrix_world
                o['export_role']='building_geometry' if ident==BASE else 'fixed_geometry';o['source_asset_id']=ident
                o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(mat)
                for p in o.data.polygons:p.material_index=0
                uvdata=o.data.uv_layers[0].data
                if kind=='building':
                    for uv in uvdata:uv.uv=(uv.uv.x*.5,.5+uv.uv.y*.5)
                else:
                    for poly in o.data.polygons:
                        # Select each face's source patch as a unit. The approved cone
                        # has one corner 0.000009 UV beyond its roof-cell boundary;
                        # per-loop classification would send it to the stone cell.
                        us=[uvdata[i].uv.copy() for i in poly.loop_indices]
                        col=min(3,int(sum(u.x for u in us)/len(us)*4))
                        row=min(3,int((1-sum(u.y for u in us)/len(us))*4));t=row*4+col
                        assert t in PSLOTS,(o.name,t)
                        slot=PSLOTS[t]
                        for i,uv in zip(poly.loop_indices,us):
                            u,v=uv.x*4-col,(1-uv.y)*4-row
                            assert -.001<=u<=1.001 and -.001<=v<=1.001,(o.name,poly.index,u,v)
                            u=max(.025,min(.975,u));v=max(.025,min(.975,v))
                            uvdata[i].uv=((slot%8+u)/8,1-(slot//8+v)/8)
                for mod in o.modifiers:
                    if mod.type=='ARMATURE':mod.object=rig
            # Bake geometry self-AO with only this independent model present.
            bpy.ops.object.select_all(action='DESELECT')
            for o in keep:o.hide_set(False);o.hide_render=False;o.select_set(True);o.data.uv_layers.active_index=1
            bpy.context.view_layer.objects.active=keep[0]
            bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.012,area_weight=.8,scale_to_bounds=True)
            bpy.ops.object.mode_set(mode='OBJECT')
            nodes=mat.node_tree.nodes;links=mat.node_tree.links;bs=next(n for n in nodes if n.type=='BSDF_PRINCIPLED')
            restore=[(l.from_socket,l.to_socket) for slot in ('Base Color','Normal') for l in list(bs.inputs[slot].links)]
            for slot in ('Base Color','Normal'):
                for l in list(bs.inputs[slot].links):links.remove(l)
            ao_node=next(n for n in nodes if n.type=='TEX_IMAGE' and (n.label or n.name)=='AO');oldim=ao_node.image
            size=1024 if ident==BASE else 512
            ao=bpy.data.images.new(ident+'_SelfAO',width=size,height=size,alpha=False);ao.colorspace_settings.name='Non-Color';ao_node.image=ao;nodes.active=ao_node
            scene.render.engine='CYCLES';scene.cycles.samples=24;scene.render.bake.margin=8
            bpy.ops.object.bake(type='AO',uv_layer='UV2')
            (out/'bakes').mkdir(exist_ok=True);ao.filepath_raw=str(out/'bakes'/(ident+'.png'));ao.file_format='PNG';ao.save()
            ao_node.image=oldim
            for a,b in restore:links.new(a,b)
            page,rect=AO[ident];w=1024 if page=='building' else 2048;x0,y0,x1,y1=rect
            for o in keep:
                for d in o.data.uv_layers[1].data:d.uv=((x0+4+d.uv.x*(x1-x0-8))/w,1-(y1-4-d.uv.y*(y1-y0-8))/w)
                o.data.uv_layers.active_index=0;o.select_set(False)
            # Exact geometric reconstruction check excludes only the explicitly added supports.
            err=max((abs(a-b) for o in keep if o.name in original for v,p in zip(o.data.vertices,original[o.name]) for a,b in zip(placement@o.matrix_world@v.co,p)),default=0)
            assert err<.0002,(ident,err)
            folder=out/'masters'/ident;folder.mkdir(parents=True,exist_ok=True)
            shutil.copytree(out/'textures',folder/'textures',dirs_exist_ok=True)
            for m in mats.values():
                for n in m.node_tree.nodes:
                    if n.type=='TEX_IMAGE':n.image.filepath='//textures/'+Path(n.image.filepath).name
            bpy.context.window.scene=review
            bpy.ops.wm.save_as_mainfile(filepath=str(folder/(ident+'.blend')),relative_remap=False)
            # Decode uses relative paths after save. Export consists of three independently selectable base meshes.
            bpy.context.window.scene=scene;scene.view_layers[0].update()
            groups={}
            for o in keep:
                label='SiloSideSupports' if o.get('optional_silo_side_support') else 'Shelter' if ident==BASE and ('Shelter_' in o.name or 'Support_Foot_' in o.name) else 'Building' if ident==BASE else 'Stock' if ident==SILO and o.get('surface_tiles') and any(x in o.name for x in ('Sack_','Visible_Pallet.')) else 'Geometry'
                groups.setdefault(label,[]).append(dec.decode_mesh(o,o.matrix_world))
            model={'asset_id':ident,'kind':'building' if ident in (BASE,SILO) else 'prop','meshes':[dec.merge_meshes(ident+'_'+label,ms) for label,ms in groups.items()]}
            (out/'models').mkdir(exist_ok=True);dump(out/'models'/(ident+'.json'),model)
            bpy.context.window.scene=review
            # Validate the actual saved file, including its standalone geometry and image bindings.
            bpy.ops.wm.open_mainfile(filepath=str(folder/(ident+'.blend')),load_ui=False,use_scripts=False)
            report=validate_current_scene();dump(folder/'validation.json',report);assert report['error_count']==0,report['findings']
            records.append({'asset_id':ident,'source':str(folder/(ident+'.blend')),'position':list(pivot),'rotation_degrees':[0,0,rotation],'scale':[1,1,1],'support':'ground','terrain_follow':'pivot','instance_id':ident,'added_supports':added,'geometry_reconstruction_max_error':err,'vertices':sum(len(m['vertices']) for m in model['meshes']),'triangles':sum(len(m['triangles']) for m in model['meshes'])})
            print('MASTER_READY',ident,records[-1]['vertices'],flush=True)
    assert sha(SOURCE)==before
    dump(out/'masters.json',records)

def pack(out):
    from PIL import Image
    pages={'building':Image.new('RGB',(1024,1024),'white'),'props':Image.new('RGB',(2048,2048),'white')}
    for ident,(page,rect) in AO.items():
        x0,y0,x1,y1=rect;im=Image.open(out/'bakes'/(ident+'.png')).convert('RGB').resize((x1-x0-8,y1-y0-8),Image.Resampling.LANCZOS)
        pages[page].paste(im,(x0+4,y0+4))
        # Edge extension supplies mip padding around the independently baked cell.
        pages[page].paste(im.crop((0,0,1,im.height)).resize((4,im.height)),(x0,y0+4))
        pages[page].paste(im.crop((im.width-1,0,im.width,im.height)).resize((4,im.height)),(x1-4,y0+4))
        pages[page].paste(im.crop((0,0,im.width,1)).resize((im.width,4)),(x0+4,y0))
        pages[page].paste(im.crop((0,im.height-1,im.width,im.height)).resize((im.width,4)),(x0+4,y1-4))
    for page,im in pages.items():im.save(out/'textures'/(texname(page,'AO')+'.png'))
    for folder in (out/'masters').iterdir():shutil.copytree(out/'textures',folder/'textures',dirs_exist_ok=True)
    print('SHARED_AO_PACKED',flush=True)

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    mode,dest=args;globals()[mode](Path(dest))
