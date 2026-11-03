"""Correct V7's over-heavy wood: green roof trim, thin wood underside, compact eaves, taller cone."""
import sys,json,math,hashlib,shutil,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];NAME='CSC_BAKERS_Wind_Mill_Modern'
SOURCE=Path.home()/'Desktop/Working Files/3D Art/BAKERS/Wind Mill/modern/revision-07-roof-intake'/f'{NAME}.blend'
def textures(out):
    from PIL import Image
    import numpy as np
    out.mkdir(parents=True,exist_ok=False);shutil.copytree(SOURCE.parent/'textures',out/'textures')
    atlas=Path.home()/'Desktop/Working Files/3D Art/Textures/CSC_Atlas_B_BAKERS_2.dds'
    src=Image.open(atlas).convert('RGB');w,h=src.size
    # Existing dark-green painted beam strip, recorded against the 1024-pixel atlas.
    bounds=tuple(round(v*w/1024) for v in (520,583,760,610))
    patch=src.crop(bounds).resize((512,128),Image.Resampling.LANCZOS)
    b=Image.open(out/'textures'/f'{NAME}_B.png').convert('RGB');b.paste(patch,(0,1408));b.save(out/'textures'/f'{NAME}_B.png')
    # Only the lower quarter of former door cell 8 is now the native green trim.
    # The upper three quarters retain the painted wood for thin underside strips.
    for ch,color in [('N',(128,128,255)),('G',(65,65,65)),('M',(0,0,0))]:
        p=out/'textures'/f'{NAME}_{ch}.png';im=Image.open(p).convert('RGB');im.paste(Image.new('RGB',(512,128),color),(0,1408));im.save(p)
    patch.save(out/'native-dark-green-reference.png')
    (out/'texture-provenance.json').write_text(json.dumps({'base':'revision-07 ImageGen atlas unchanged except native green insertion','native_green_source':str(atlas),'source_pixels':bounds,'target_pixels':[0,1408,512,1536],'native_green_rgb_median':np.median(np.asarray(patch).reshape(-1,3),axis=0).tolist(),'roof_panels':'existing Bakers_2-inspired green','wood':'existing ImageGen timber, upper 75% of cell 8','brick_window_normals':'strong revision-07 normals preserved'},indent=2))
    print('V8_TEXTURES_READY')
def build(out):
    import bpy,bmesh
    from mathutils import Matrix,Vector
    sys.path.insert(0,str(ROOT/'project/tools/blender'));from csc_scene_validation import suspend_csc_repairs
    with suspend_csc_repairs():
        digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest();bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
        scene=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=scene
        rig=bpy.data.objects[NAME];mat=bpy.data.materials[NAME]
        frame=Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)));inv=frame.inverted()
        def tileuv(t,u,v):return ((t%4+.025+.95*u)/4,1-(t//4+.025+.95*(1-v))/4)
        def get(n):return bpy.data.objects['CSC_Fixed_'+n]
        def sig(o):return {'matrix':[list(r) for r in o.matrix_world],'vertices':[list(v.co) for v in o.data.vertices]}
        kept={o.name:sig(o) for o in scene.objects if o.type=='MESH' and not any(k in o.name for k in ('Roof','Ridge','Barge','Eave','Silo_Cap','Silo_Neck','Elevator','Rounded_Transfer'))}
        def local(o):
            m=inv@o.matrix_world;o.data=o.data.copy();o.data.transform(m);return m.inverted()
        def change(n,fn):
            o=get(n);back=local(o)
            for v in o.data.vertices:fn(v.co)
            o.data.transform(back);return o
        def roof(v):
            oldy=v.y;v.x*=44.5/47.5;v.y*=25/26
            v.z+=(abs(oldy)-abs(v.y))*13.5/26
        change('Main_Roof',roof)
        change('Main_Ridge',lambda v:setattr(v,'x',v.x*90.6/100))
        # Secondary roofs retain their supporting structures but lose unnecessary projection.
        change('Shelter_Roof',lambda v:(setattr(v,'x',22+(v.x-22)*45/48),setattr(v,'y',-46.5+(v.y+46.5)*45/47)))
        change('Shelter_Ridge',lambda v:setattr(v,'y',-46.5+(v.y+46.5)*46/52.5))
        intake=get('Intake_Roof');pts=[inv@intake.matrix_world@v.co for v in intake.data.vertices]
        cx=(min(v.x for v in pts)+max(v.x for v in pts))/2;cy=(min(v.y for v in pts)+max(v.y for v in pts))/2
        change('Intake_Roof',lambda v:(setattr(v,'x',cx+(v.x-cx)*14/16),setattr(v,'y',cy+(v.y-cy)*16/18)))
        # Taller cone, smaller lip, same silo centre and base. Preserve the user's placement.
        cap=get('Silo_Cap');pts=[inv@cap.matrix_world@v.co for v in cap.data.vertices]
        sx=(min(v.x for v in pts)+max(v.x for v in pts))/2;sy=(min(v.y for v in pts)+max(v.y for v in pts))/2
        def cone(v):
            factor=25.5/27 if v.z<78 else 3.5/4
            v.x=sx+(v.x-sx)*factor;v.y=sy+(v.y-sy)*factor
            if v.z>77:v.z=77+(v.z-77)*18/11
        change('Silo_Cap',cone)
        change('Silo_Neck',lambda v:setattr(v,'z',v.z+7))
        change('Rounded_Transfer_Pipe',lambda v:setattr(v,'z',v.z+7))
        change('Elevator',lambda v:setattr(v,'z',6+(v.z-6)*105/98))
        change('Elevator_Cap',lambda v:setattr(v,'z',v.z+7))
        for o in list(scene.objects):
            if o.type=='MESH' and any(k in o.name for k in ('Barge_Timber','Eave_Timber')):bpy.data.objects.remove(o,do_unlink=True)
        def board(name,a,b,width,thickness,tile,wood=False):
            # Width crosses the board in plan; thickness is perpendicular to its slope.
            a,b=Vector(a),Vector(b);axis=(b-a).normalized();cross=Vector((1,0,0)) if abs(axis.x)<.1 else Vector((0,1,0));normal=axis.cross(cross).normalized()
            if normal.z<0:normal=-normal
            vs=[]
            for c in (a,b):
                vs.extend([c+cross*u*width/2+normal*v*thickness/2 for u,v in [(-1,-1),(1,-1),(1,1),(-1,1)]])
            fs=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
            me=bpy.data.meshes.new(name);me.from_pydata(vs,[],fs);me.materials.append(mat);me.update();uv=me.uv_layers.new(name='UV1')
            for p in me.polygons:
                facing=max(range(3),key=lambda i:abs(p.normal.dot([axis,cross,normal][i])))
                ua,va=(cross,normal) if facing==0 else (axis,normal if facing==1 else cross)
                for li in p.loop_indices:
                    q=me.vertices[me.loops[li].vertex_index].co-(a+b)/2
                    if wood:
                        u=max(.02,min(.98,(q.dot(ua)+(b-a).length/2)/128)) if facing else .5+q.dot(ua)/8
                        v=.35+.55*(.5+q.dot(va)/8)
                    else:u=.01+.008*(.5+q.dot(ua)/max(1,(b-a).length));v=.1+.8*(.5+q.dot(va)/8)
                    uv.data[li].uv=tileuv(tile,u,v)
            o=bpy.data.objects.new('CSC_Fixed_'+name,me);scene.collection.objects.link(o);review.collection.objects.link(o)
            o['export_role']='building_geometry';o['source_asset_id']=NAME;o.parent=rig
            me.transform(frame);g=o.vertex_groups.new(name='Bone');g.add(list(range(len(me.vertices))),1,'REPLACE');m=o.modifiers.new('Static Bone','ARMATURE');m.object=rig
            me.uv_layers.new(name='UV2');uv3=me.uv_layers.new(name='UV3')
            for d in uv3.data:d.uv=(.02,.02)
            bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces));bmesh.ops.split_edges(bm,edges=list(bm.edges));bm.to_mesh(me);bm.free()
        # Green bargeboard face, with a thin wood strip tucked underneath it.
        for x in (-44.1,44.1):
            for side in (-1,1):
                a=Vector((x,side*24.9,62.65));b=Vector((x,0,75.58));d=(b-a).normalized();n=d.cross(Vector((1,0,0))).normalized()
                if n.z<0:n=-n
                board(f'Barge_Green_{x}_{side}',a-n*.65,b-n*.65,1.6,2.1,2)
                board(f'Barge_Wood_Underside_{x}_{side}',a-n*2.0,b-n*2.0,1.35,.6,8,True)
        for y in (-24.85,24.85):
            board('Eave_Green_'+str(y),(-44.5,y,62.2),(44.5,y,62.2),1.7,1.8,2)
            board('Eave_Wood_Underside_'+str(y),(-44.3,y,61.0),(44.3,y,61.0),1.4,.6,8,True)
        # Native dark green on the main ridge and the smaller shelter ridge.
        for n in ('Main_Ridge','Shelter_Ridge'):
            o=get(n);back=local(o);vs=[v.co for v in o.data.vertices];mins=[min(v[i] for v in vs) for i in range(3)];maxs=[max(v[i] for v in vs) for i in range(3)]
            for p in o.data.polygons:
                axis=max(range(3),key=lambda i:abs(p.normal[i]));axes=[i for i in range(3) if i!=axis]
                if n=='Main_Ridge' and 0 in axes:axes=[0,next(i for i in axes if i!=0)]
                for li in p.loop_indices:
                    q=o.data.vertices[o.data.loops[li].vertex_index].co;u=(q[axes[0]]-mins[axes[0]])/max(.01,maxs[axes[0]]-mins[axes[0]]);v=(q[axes[1]]-mins[axes[1]])/max(.01,maxs[axes[1]]-mins[axes[1]])
                    o.data.uv_layers[0].data[li].uv=tileuv(8,.04+.92*u,.02+.18*v)
            o.data.transform(back)
        nodes={n.label or n.name:n for n in mat.node_tree.nodes if n.type=='TEX_IMAGE'}
        for ch in ('B','N','G','M','E','AO'):
            im=bpy.data.images.load(str(out/'textures'/f'{NAME}_{ch}.png'),check_existing=False);im.colorspace_settings.name='sRGB' if ch in ('B','E') else 'Non-Color';nodes[ch].image=im
        for name,s in kept.items():assert sig(bpy.data.objects[name])==s,name
        bpy.context.window.scene=review;(out/'authoring').mkdir();bpy.ops.wm.save_as_mainfile(filepath=str(out/'authoring'/f'{NAME}.blend'))
        assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==digest
        (out/'changes.json').write_text(json.dumps({'source':str(SOURCE),'source_sha256':digest,'source_preserved':True,'main_roof_width_before_after':[95,89],'main_roof_depth_before_after':[52,50],'overall_barge_width_before_after':[98.1,89.8],'barge_green_thickness':2.1,'wood_underside_thickness':.6,'cap_apex_before_after':[88,95],'cap_radius_before_after':[27,25.5],'upper_elevator_and_spout_rise':7,'preserved_objects':list(kept),'small_details':'existing strong B/N/AO; no added seam, rivet or grain geometry'},indent=2))
        print('V8_AUTHORED')
if __name__=='__main__':
    args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else sys.argv[1:]
    {'textures':textures,'build':build}[args[0]](Path(args[1]))
