"""Modern Water Mill and shared shelter finish, authored from the current kit.

Blender: build OUT. Python: pack OUT. Native publication is in water_modern_native.
"""
import sys,json,math,shutil,ast
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from modular_v9 import ROOT,ART,BASE,SILO,PMAT,BMAT,sha,dump
WATER='CSC_BAKERS_Water_Mill_Modern'
BASE_SOURCE=ART/'Level 1/modern/revision-02-blank-brick'/f'{BASE}.blend'
SILO_SOURCE=ART/'BAKERS/Wind Mill/modern/revision-09-modular'/f'{SILO}.blend'
HIST_SOURCE=ART/'BAKERS/Water Mill/CSC_BAKERS_Water_Mill.blend'
DESTS={BASE:ART/'Level 1/modern/revision-03-finished-shelter',WATER:ART/'BAKERS/Water Mill/modern/revision-01'}
LIBS={'building':ART/'Textures/CSC_Buildings_Modern','props':ART/'Textures/CSC_Props_Modern'}
RELEASES={'building':'2026-10-27_Modern_r003','props':'2026-10-27_Modern_r002'}
ALLOC={BASE:('building',[0,0,512,512]),WATER+'_Building':('building',[512,0,1024,512]),WATER+'_Machinery':('props',[256,256,512,512])}

def build(out):
    import bpy,bmesh
    from mathutils import Matrix,Vector
    sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
    import decode_blend as dec
    from csc_scene_validation import suspend_csc_repairs,validate_current_scene
    out.mkdir(parents=True,exist_ok=True)
    (out/'bakes').mkdir(exist_ok=True);(out/'models').mkdir(exist_ok=True)
    mod=ROOT/'Civ Supply Chains'
    baseline={'sources':{str(p):sha(p) for p in (BASE_SOURCE,SILO_SOURCE,HIST_SOURCE)},'runtime':{str(p.relative_to(mod)):sha(p) for d in ('Assets','Geometries','Materials','Textures','ArtDefs','XLPs') for p in (mod/d).iterdir() if p.is_file()},'project':sha(mod/'Civ Supply Chains.civ6proj'),'libraries':{kind:{str(p.relative_to(lib)):sha(p) for p in lib.rglob('*') if p.is_file() and 'Releases' not in p.parts} for kind,lib in LIBS.items()}}
    dump(out/'baseline.json',baseline)
    frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))
    water_frame=Matrix.Translation(Vector((-34,20.5,6.15)))
    active_id=BASE
    def uv(slot,u,v,kind='building'):
        # Both surface sheets use 128px patches on 1024px pages.
        grid=4 if kind=='building' else 8
        return ((slot%grid+.025+.95*max(0,min(1,u)))/8,1-(slot//grid+.025+.95*(1-max(0,min(1,v))))/8)
    def link(o):
        for sc in (scene,review):
            if o.name not in sc.objects:sc.collection.objects.link(o)
        o['export_role']='building_geometry';o['source_asset_id']=active_id
        o.parent=rig
        for m in list(o.modifiers):
            if m.type=='ARMATURE':o.modifiers.remove(m)
        o.vertex_groups.clear();g=o.vertex_groups.new(name='Bone');g.add(list(range(len(o.data.vertices))),1,'REPLACE')
        m=o.modifiers.new('Static Bone','ARMATURE');m.object=rig
        for name in ('UV2','UV3'):
            if name not in o.data.uv_layers:o.data.uv_layers.new(name=name)
        for d in o.data.uv_layers['UV3'].data:d.uv=(.02,.02)
        return o
    def mesh(name,vs,fs,slot,kind='building',custom=None):
        me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.update();me.materials.append(mats[kind])
        o=bpy.data.objects.new('CSC_Fixed_'+name,me);layer=me.uv_layers.new(name='UV1')
        for p in me.polygons:
            axis=max(range(3),key=lambda a:abs(p.normal[a]));axes=([1,2] if axis==0 else [0,2] if axis==1 else [0,1])
            pts=[me.vertices[i].co for i in p.vertices];lo=[min(v[a] for v in pts) for a in axes];hi=[max(v[a] for v in pts) for a in axes]
            for li in p.loop_indices:
                q=me.vertices[me.loops[li].vertex_index].co
                u,v=[(q[a]-lo[j])/max(.01,hi[j]-lo[j]) for j,a in enumerate(axes)]
                t=slot[p.index] if isinstance(slot,list) else slot
                layer.data[li].uv=custom(p,q) if custom else uv(t,u,v,kind)
        link(o);return o
    def box(name,c,s,t,kind='building'):
        x,y,z=c;a,b,h=[v/2 for v in s]
        return mesh(name,[(x+i*a,y+j*b,z+k*h) for i,j,k in [(-1,-1,-1),(1,-1,-1),(1,1,-1),(-1,1,-1),(-1,-1,1),(1,-1,1),(1,1,1),(-1,1,1)]],[(0,3,2,1),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7),(4,5,6,7)],t,kind)
    def beam(name,a,b,width,thickness=None,wood=False):
        a,b=Vector(a),Vector(b);axis=(b-a).normalized();cross=Vector((0,1,0)) if abs(axis.y)<.1 else Vector((1,0,0));normal=axis.cross(cross).normalized()
        if normal.z<0:normal=-normal
        thick=thickness or width;vs=[]
        for c in (a,b):vs += [c+cross*u*width/2+normal*v*thick/2 for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]]
        def mapping(p,q):
            along=(q-a).dot(axis)/max(32,(b-a).length);across=.5+(q-(a+b)/2).dot(cross)/12
            return uv(8,.04+.92*along,.35+.55*across if wood else .025+.16*across)
        return mesh(name,vs,[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],8,custom=mapping)
    def cylinder(name,x,y,rings,n=12,slot=53):
        vs=[(x+r*math.cos(i*2*math.pi/n),y+r*math.sin(i*2*math.pi/n),z) for z,r in rings for i in range(n)]
        fs=[(j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i) for j in range(len(rings)-1) for i in range(n)]
        fs += [tuple(reversed(range(n))),tuple(range((len(rings)-1)*n,len(rings)*n))]
        o=mesh(name,vs,fs,slot,'props')
        for p in o.data.polygons:p.use_smooth=p.index<len(fs)-2
        return o
    def remove(name):bpy.data.objects.remove(bpy.data.objects['CSC_Fixed_'+name],do_unlink=True)
    def save_master(ident):
        keep=[o for o in scene.objects if o.type=='MESH']
        # Every model gets its own self AO; reusable flour props are not included.
        bpy.ops.object.select_all(action='DESELECT')
        for o in keep:o.hide_set(False);o.hide_render=False;o.select_set(True);o.data.uv_layers.active_index=1
        bpy.context.view_layer.objects.active=keep[0]
        bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(75),island_margin=.012,area_weight=.8,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
        bake=bpy.data.images.new(ident+'_SelfAO',width=1024,height=1024,alpha=False);bake.colorspace_settings.name='Non-Color'
        restores=[]
        for mat in {o.data.materials[0] for o in keep}:
            ns=mat.node_tree.nodes;ls=mat.node_tree.links;bs=next(n for n in ns if n.type=='BSDF_PRINCIPLED');n=next(n for n in ns if n.type=='TEX_IMAGE' and (n.label or n.name)=='AO')
            old=n.image;edges=[(l.from_socket,l.to_socket) for s in ('Base Color','Normal') for l in list(bs.inputs[s].links)]
            for s in ('Base Color','Normal'):
                for l in list(bs.inputs[s].links):ls.remove(l)
            n.image=bake;ns.active=n;restores.append((mat,n,old,edges))
        scene.render.engine='CYCLES';scene.cycles.samples=32;scene.render.bake.margin=8
        bpy.ops.object.bake(type='AO',uv_layer='UV2');bake.filepath_raw=str(out/'bakes'/(ident+'.png'));bake.file_format='PNG';bake.save()
        for mat,n,old,edges in restores:
            n.image=old
            for a,b in edges:mat.node_tree.links.new(a,b)
        for o in keep:
            k=ident if ident==BASE else ident+('_Building' if o.data.materials[0].name==BMAT else '_Machinery')
            kind,rect=ALLOC[k];x0,y0,x1,y1=rect
            for d in o.data.uv_layers[1].data:d.uv=((x0+4+d.uv.x*(x1-x0-8))/2048,1-(y1-4-d.uv.y*(y1-y0-8))/2048)
            o.data.uv_layers.active_index=0;o.select_set(False)
        folder=out/'masters'/ident;folder.mkdir(parents=True,exist_ok=True)
        for kind,mat in mats.items():
            (folder/'textures').mkdir(exist_ok=True)
            for n in mat.node_tree.nodes:
                if n.type=='TEX_IMAGE':
                    source=Path(bpy.path.abspath(n.image.filepath));name=source.name
                    shutil.copy2(source,folder/'textures'/name);n.image.filepath='//textures/'+name
        bpy.context.window.scene=review
        bpy.ops.wm.save_as_mainfile(filepath=str(folder/(ident+'.blend')),relative_remap=False)
        bpy.ops.wm.open_mainfile(filepath=str(folder/(ident+'.blend')),load_ui=False,use_scripts=False)
        report=validate_current_scene();dump(folder/'validation.json',report);assert report['automated_pass'],report
        bpy.context.window.scene=bpy.data.scenes['Export'];bpy.context.view_layer.update();groups={}
        for o in bpy.context.scene.objects:
            if o.type!='MESH':continue
            label=('SiloSideSupports' if o.get('optional_silo_side_support') else 'Shelter' if 'Shelter_' in o.name or 'Support_Foot_' in o.name else 'Building') if ident==BASE else ('Building' if o.data.materials[0].name==BMAT else 'Machinery')
            groups.setdefault(label,[]).append(dec.decode_mesh(o,o.matrix_world))
        model={'asset_id':ident,'kind':'building','meshes':[dec.merge_meshes(ident+'_'+k,v) for k,v in groups.items()]}
        dump(out/'models'/(ident+'.json'),model);print('SAVED',ident,sum(len(m['vertices']) for m in model['meshes']),flush=True)
    with suspend_csc_repairs():
        bpy.ops.wm.open_mainfile(filepath=str(BASE_SOURCE),load_ui=False,use_scripts=False)
        scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');mats={'building':bpy.data.materials[BMAT]}
        # New pieces are made in the kit frame, then placed in its exact source frame.
        original_names={o.name for o in scene.objects}
        for n in ('Shelter_Roof','Shelter_Gable'):remove(n)
        xl,xr,cx,yb,yf=-.5,44.5,22,-24,-69
        vs=[(xl,yb,40),(cx,yb,52.5),(xr,yb,40),(xl,yf,40),(cx,yf,52.5),(xr,yf,40),(xl,yb,37.7),(cx,yb,50.2),(xr,yb,37.7),(xl,yf,37.7),(cx,yf,50.2),(xr,yf,37.7)]
        fs=[(0,1,4,3),(1,2,5,4),(6,9,10,7),(7,10,11,8),(0,3,9,6),(2,8,11,5),(3,4,10,9),(4,5,11,10),(0,6,7,1),(1,7,8,2)]
        def roofuv(p,q):return uv(2,(q.y+69)/96,abs(q.x-22)/32) if p.index<2 else uv(8,.08+(q.y+69)/64*.85,.06+.10*((q.x+.5)/45))
        mesh('Shelter_Roof',vs,fs,2,custom=roofuv)
        # Closed gable with warm timber, matching the thin wood under the main roof.
        mesh('Shelter_Gable',[(x,y,z) for y in (-68.45,-67.25) for x,z in [(1,40.0),(43,40.0),(22,50.0)]],[(0,2,1),(3,4,5),(0,1,4,3),(1,2,5,4),(2,0,3,5)],8,custom=lambda p,q:uv(8,(q.x-1)/64,.35+.55*(q.z-40)/14))
        for x in (3,41):
            beam(f'Shelter_Side_Bearer_{x}',(x,-27,38.2),(x,-65,38.2),3.6,3.6)
        for side in (-1,1):
            a=Vector((22+side*22.5,-69.0,39.45));b=Vector((22,-69,51.95))
            beam(f'Shelter_Barge_Green_{side}',a,b,1.8,1.8)
            beam(f'Shelter_Barge_Wood_{side}',a-Vector((0,0,1.22)),b-Vector((0,0,1.22)),1.4,.6,True)
        for o in list(scene.objects):
            if o.type!='MESH':continue
            if o.name not in original_names or o.name in ('CSC_Fixed_Shelter_Roof','CSC_Fixed_Shelter_Gable'):o.data.transform(frame)
            elif any(s in o.name for s in ('Shelter_Support','Shelter_Brace','Shelter_Header')):
                pts=[frame.inverted()@o.matrix_world@v.co for v in o.data.vertices]
                lo=[min(v[i] for v in pts) for i in range(3)];hi=[max(v[i] for v in pts) for i in range(3)]
                for p in o.data.polygons:
                    for li in p.loop_indices:
                        q=pts[o.data.loops[li].vertex_index]
                        along=(q.z-lo[2])/max(45,hi[2]-lo[2]);cross=(q.x-lo[0])/max(8,hi[0]-lo[0])
                        if 'Header' in o.name:along=(q.x-lo[0])/64;cross=(q.z-lo[2])/8
                        o.data.uv_layers[0].data[li].uv=uv(8,.04+.92*along,.035+.15*cross)
        for o in scene.objects:
            if o.type=='MESH' and ('Shelter_' in o.name):
                bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        save_master(BASE)
        # Derive Water Mill from the corrected master; geometry dimensions stay unchanged.
        active_id=WATER
        bpy.ops.wm.open_mainfile(filepath=str(out/'masters'/BASE/(BASE+'.blend')),load_ui=False,use_scripts=False)
        scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene;rig=next(o for o in scene.objects if o.type=='ARMATURE');rig.name=WATER;rig.data.name=WATER;scene['asset_id']=WATER;review['asset_id']=WATER
        mats={'building':bpy.data.materials[BMAT]}
        for o in list(scene.objects):
            if o.type=='MESH':
                o.matrix_world=water_frame@frame.inverted()@o.matrix_world;o['source_asset_id']=WATER
                if 'optional_silo_side_support' in o:del o['optional_silo_side_support']
        remove('Front_Window_-21_17')
        with bpy.data.libraries.load(str(SILO_SOURCE),link=False) as (a,b):
            b.objects=[n for n in a.objects if n.startswith('CSC_Fixed_Intake_')]
        # Appended objects must be linked/evaluated before reading world transforms.
        # In particular the user-moved intake roof has a nonidentity object matrix.
        for o in b.objects:scene.collection.objects.link(o)
        bpy.context.view_layer.update()
        measured={r['name']:r for r in json.loads((out/'inspection/silo.json').read_text())}
        for o in b.objects:
            old=o.matrix_world.copy();o.parent=None
            expected=Matrix(measured[o.name]['matrix'])
            assert max(abs(old[i][j]-expected[i][j]) for i in range(4) for j in range(4))<1e-4,('Unevaluated source transform',o.name)
            o.matrix_world=water_frame@Matrix.Translation(Vector((-26-51.22226,-35+105.25947,0)))@frame.inverted()@old
            mats['props']=o.data.materials[0];link(o)
        # Use the canonical props image sources after library append.
        for n in mats['props'].node_tree.nodes:
            if n.type=='TEX_IMAGE':n.image.filepath=str(LIBS['props']/'Current/textures'/n.image.filepath.replace('\\','/').rsplit('/',1)[-1])
        with bpy.data.libraries.load(str(HIST_SOURCE),link=False) as (a,b):b.objects=['DIS_CTY_Watermill_AN_Base','Water_Mill_Floor']
        foundation_before={o.name:[list(o.matrix_world@v.co) for v in o.data.vertices] for o in b.objects}
        # Retain native foundation vertices/topology; retexture broad dressed blocks.
        for o in b.objects:
            old=o.matrix_world.copy();o.parent=None;o.data=o.data.copy();o.data.materials.clear();o.data.materials.append(mats['props']);o.matrix_world=old;link(o)
            for p in o.data.polygons:p.material_index=0
            uv1=o.data.uv_layers[0]
            for p in o.data.polygons:
                normal=o.matrix_world.to_3x3()@p.normal;axis=max(range(3),key=lambda i:abs(normal[i]));axes=([1,2] if axis==0 else [0,2] if axis==1 else [0,1])
                for li in p.loop_indices:
                    q=o.matrix_world@o.data.vertices[o.data.loops[li].vertex_index].co
                    u=(q[axes[0]]+85)/105 if axes[0]==0 else (q[axes[0]]+52)/105
                    v=(q[2]+66.8)/73 if axes[1]==2 else (q[1]+52)/105
                    uv1.data[li].uv=uv(32,u,v,'props')
            assert [list(o.matrix_world@v.co) for v in o.data.vertices]==foundation_before[o.name]
        # A compact enclosed vertical drive drops into the former wheel envelope.
        box('Turbine_Bearing_Housing',(23,20.5,28),(22,18,13),[53,7,7,7,7,53],'props')
        box('Turbine_Wall_Coupling',(10.5,20.5,27),(9,11,8),48,'props')
        cylinder('Turbine_Vertical_Shaft',28,20.5,[(-21,3.8),(23,3.8)],12,48)
        cylinder('Turbine_Lower_Housing',28,20.5,[(-26,5.8),(-23,8),(-15,8),(-12,5.8)],12,53)
        cylinder('Turbine_Upper_Bearing',28,20.5,[(17,6),(22,6)],12,54)
        # Bold outlet and intake mouths are simple forms; seams/fasteners stay in paint.
        box('Turbine_Outlet',(33.5,20.5,-21),(12,10,8),53,'props')
        box('Turbine_Outlet_Mouth',(39.55,20.5,-21),(0.35,7,5),48,'props')
        for o in scene.objects:
            if o.type=='MESH' and o.name.startswith('CSC_Fixed_Turbine_'):
                bm=bmesh.new();bm.from_mesh(o.data);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bm.to_mesh(o.data);bm.free()
        target=Vector((-22,0,13));cam=review.camera;cam.data.type='ORTHO';cam.data.ortho_scale=200;cam.data.shift_x=cam.data.shift_y=0
        cam.location=target+Vector((175,-255,170));cam.rotation_euler=(target-cam.location).to_track_quat('-Z','Y').to_euler()
        save_master(WATER)
    placements=[{'asset_id':'CSC_BAKERS_Flour_Pallet_Modern','instance_id':'Flour_Pallet','position':[-12,-27,6.15],'rotation_degrees':[0,0,0],'scale':[1,1,1],'support':'ground','terrain_follow':'pivot'}, {'asset_id':'CSC_BAKERS_Flour_Trolley_Modern','instance_id':'Flour_Trolley','position':[-42,-34,6.15],'rotation_degrees':[0,0,-18],'scale':[1,1,1],'support':'ground','terrain_follow':'pivot'}]
    dump(out/'placements.json',placements)
    dump(out/'design.json',{'foundation_source':str(HIST_SOURCE),'foundation_vertices_unchanged':True,'kit_transform':{'translation':[-34,20.5,6.15],'dimensions':'unscaled modern reusable base'},'intake':'exact reused Wind Mill intake geometry/UV1, moved left of shelter','removed_water_window':'lower front window only, behind intake; generic base retains it','turbine_water_datum':-23,'water_datum_basis':'approximate original wheel lowest extent -22.78; in-game river level check pending','concept':'inspiration only; existing kit and historical footprint are authoritative','fx_candidate':'FX_Watermill_Wheel_CW_01'} )

def pack(out):
    from PIL import Image
    for kind,library in LIBS.items():
        dest=out/'libraries'/kind;shutil.copytree(library/'Current',dest,dirs_exist_ok=True)
        plan=json.loads((dest/'atlas-plan.json').read_text())
        allocations=plan.get('AO_allocations',plan['props']['AO_allocations'])
        allocations.update(ALLOC);plan['AO_allocations']=allocations
        plan['building']['AO_size']=2048;plan['building']['AO_quadrants']={'stage_2':[0,0,1024,1024],'stage_3':[1024,0,2048,1024],'stage_4':[0,1024,1024,2048],'storage':[1024,1024,2048,2048]}
        dump(dest/'atlas-plan.json',plan)
        shutil.copy2(Path(__file__).with_name('rebuild_modern_atlases.py'),dest/'scripts/rebuild_modern_atlases.py')
        for name,(page,rect) in ALLOC.items():
            if page==kind:shutil.copy2(out/'bakes'/((BASE if name==BASE else WATER)+'.png'),dest/'bakes'/(name+'.png'))
        info=json.loads((dest/'library.json').read_text());info.update(release=RELEASES[kind],source=str(DESTS[WATER]/(WATER+'.blend')),source_sha256=sha(out/'masters'/WATER/(WATER+'.blend')),status='Finished shared shelter and derived Water Mill; preserved surface artwork; expanded building AO to 2048 for separate Stage 2 bakes')
        dump(dest/'library.json',info)
        from rebuild_modern_atlases import rebuild
        rebuild(dest)
        info['maps']={p.name:sha(p) for p in (dest/'textures').iterdir()};dump(dest/'library.json',info)
        # All artistic surface maps are exact; only geometry-derived AO changed.
        for p in (dest/'textures').iterdir():
            if not p.stem.endswith('_AO'):assert sha(p)==sha(library/'Current/textures'/p.name)
    for ident in (BASE,WATER):
        for kind in ('building','props'):
            for p in (out/'libraries'/kind/'textures').iterdir():
                target=out/'masters'/ident/'textures'/p.name
                if target.exists():shutil.copy2(p,target)
    print('ATLAS_SNAPSHOTS_READY')

if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    mode,path=args;globals()[mode](Path(path))
