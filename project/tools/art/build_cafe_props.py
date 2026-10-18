"""Individual editable Cafe masters, isolated AO, native exports and review assembly."""
import bpy, math, json, sys, shutil, copy, subprocess, importlib.util
from pathlib import Path
from mathutils import Vector, Matrix
sys.path.insert(0,str(Path(__file__).parent))
from cafe_atlas import ROOT,ART,OUT,STAGE,SOURCE,RELEASE,PYTHON,sha
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
V=module('cafe_validator',ROOT/'project/tools/blender/csc_scene_validation.py')
E=module('cafe_cn6',ROOT/'project/tools/scripts/io_export_cn6_b4.py')
REGIONS={r['name']:r['bounds'] for r in json.loads(((STAGE if STAGE.exists() else ART/'Textures/CSC_Props/Current')/'atlas/manifest.json').read_text())['regions']}
IDS=['CSC_BAKERS_Cafe_Chair','CSC_BAKERS_Cafe_Counter','CSC_BAKERS_Cafe_Brewing_Set','CSC_BAKERS_Cafe_Pastry_Tray','CSC_BAKERS_Cafe_Table_Service','CSC_BAKERS_Cafe_Reading_Set','CSC_ALL_Garden_Wall_Curve','CSC_ALL_Stage_4_Cobble_Decals','CSC_ALL_Oval_Table','CSC_ALL_Flour_Sack_Closed']
def setup(ident):
    global export,review,mat,rig,PARTS,ID
    ID=ident;PARTS=[];bpy.ops.wm.read_factory_settings(use_empty=True);export=bpy.context.scene;export.name='Export';review=bpy.data.scenes.new('Review')
    mat=bpy.data.materials.new('CSC_ALL_Props_01');mat['civ_material']='CSC_ALL_Props_01';mat.use_nodes=True
    nt=mat.node_tree;nt.nodes.clear();bs=nt.nodes.new('ShaderNodeBsdfPrincipled');out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(bs.outputs[0],out.inputs[0]);nodes={}
    for k in ['B','N','G','M','AO','O']:
        im=bpy.data.images.load(str(SOURCE/'textures'/f'CSC_Props_Shared_01_{k}.png'),check_existing=True);im.colorspace_settings.name='sRGB' if k=='B' else 'Non-Color'
        node=nt.nodes.new('ShaderNodeTexImage');node.image=im;node.label=k;uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='UV2' if k=='AO' else 'UV1';nt.links.new(uv.outputs[0],node.inputs[0]);nodes[k]=node
    mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MULTIPLY';mix.inputs[0].default_value=.5;nt.links.new(nodes['B'].outputs[0],mix.inputs[1]);nt.links.new(nodes['AO'].outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],bs.inputs['Base Color'])
    normal=nt.nodes.new('ShaderNodeNormalMap');nt.links.new(nodes['N'].outputs[0],normal.inputs['Color']);nt.links.new(normal.outputs[0],bs.inputs['Normal'])
    inv=nt.nodes.new('ShaderNodeMath');inv.operation='SUBTRACT';inv.inputs[0].default_value=1;nt.links.new(nodes['G'].outputs[0],inv.inputs[1]);nt.links.new(inv.outputs[0],bs.inputs['Roughness']);nt.links.new(nodes['M'].outputs[0],bs.inputs['Metallic']);nt.links.new(nodes['O'].outputs[0],bs.inputs['Alpha'])
    rd=bpy.data.armatures.new(ident+'_Rig');rig=bpy.data.objects.new(ident+'_Rig',rd);export.collection.objects.link(rig);review.collection.objects.link(rig)
    bpy.context.view_layer.objects.active=rig;rig.select_set(True);bpy.ops.object.mode_set(mode='EDIT');bone=rd.edit_bones.new('Bone');bone.head=(0,0,0);bone.tail=(0,0,1);bpy.ops.object.mode_set(mode='OBJECT');rig.select_set(False)
    for scene in [export,review]:
        scene.render.engine='CYCLES';scene.cycles.samples=64;scene.cycles.use_denoising=True;scene.world=bpy.data.worlds.new(scene.name+'_World');scene.world.use_nodes=True;bg=scene.world.node_tree.nodes.get('Background');bg.inputs[0].default_value=(.7,.8,1,1);bg.inputs[1].default_value=.65
        scene.view_settings.view_transform='AgX' if scene==export else 'Standard';scene.view_settings.exposure=.35 if scene==export else -.1;scene['atlas_release']=RELEASE
    light=bpy.data.lights.new('Review_Key','SUN');light.energy=3.2;light.angle=math.radians(6);light.color=(1,.92,.8);ob=bpy.data.objects.new('Review_Key',light);review.collection.objects.link(ob);ob.rotation_euler=Vector((300,280,-500)).to_track_quat('-Z','Y').to_euler()
    cam=bpy.data.cameras.new('Review_Camera');ob=bpy.data.objects.new('Review_Camera',cam);review.collection.objects.link(ob);cam.type='ORTHO';review.camera=ob;review.render.resolution_x=700;review.render.resolution_y=700;review.render.resolution_percentage=100;review.render.film_transparent=True
def mesh(name,vs,fs,patch,uvs=None,smooth=False):
    data=bpy.data.meshes.new(name);data.from_pydata(vs,[],fs);data.update();ob=bpy.data.objects.new(name,data);export.collection.objects.link(ob);review.collection.objects.link(ob);data.materials.append(mat);ob['export_role']='fixed_geometry';ob['source_asset_id']=ID
    for n in ['UV1','UV2','UV3']:data.uv_layers.new(name=n)
    x,y,x1,y1=REGIONS[patch]
    for poly in data.polygons:
        poly.use_smooth=smooth
        for j,li in enumerate(poly.loop_indices):
            u,v=uvs[data.loops[li].vertex_index] if uvs else [(.015,.015),(.985,.015),(.985,.985),(.015,.985)][j%4]
            data.uv_layers[0].data[li].uv=((x+(x1-x)*u)/1024,1-(y+(y1-y)*(1-v))/1024);data.uv_layers[1].data[li].uv=(u,v);data.uv_layers[2].data[li].uv=(.01,.01)
    PARTS.append(ob);return ob
def box(name,c,size,patch):
    x,y,z=c;a,b,d=[s/2 for s in size];vs=[(x+sx*a,y+sy*b,z+sz*d) for sz in [-1,1] for sy in [-1,1] for sx in [-1,1]]
    return mesh(name,vs,[(0,2,3,1),(4,5,7,6),(0,1,5,4),(2,6,7,3),(0,4,6,2),(1,3,7,5)],patch)
def rod(name,a,b,r,patch,n=6):
    a,b=Vector(a),Vector(b);z=(b-a).normalized();v=z.cross(Vector((0,0,1)))
    if v.length<.01:v=z.cross(Vector((0,1,0)))
    v.normalize();w=z.cross(v);vs=[tuple(p+r*(math.cos(i*2*math.pi/n)*v+math.sin(i*2*math.pi/n)*w)) for p in [a,b] for i in range(n)]
    return mesh(name,vs,[tuple(reversed(range(n))),tuple(range(n,2*n))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)],patch)
def lathe(name,profiles,patch,loc=(0,0,0),n=10):
    vs=[];uv=[]
    for j,(r,z) in enumerate(profiles):
        for i in range(n+1):
            t=2*math.pi*i/n;vs.append((loc[0]+r*math.cos(t),loc[1]+r*math.sin(t),loc[2]+z));uv.append((i/n,j/(len(profiles)-1)))
    fs=[(j*(n+1)+i,j*(n+1)+i+1,(j+1)*(n+1)+i+1,(j+1)*(n+1)+i) for j in range(len(profiles)-1) for i in range(n)]
    return mesh(name,vs,fs,patch,uv,True)
def handle(name,loc,r,scale=1,patch='cafe_copper'):
    # Three stout structural sides read as a loop at game camera scale.
    x,y,z=loc
    for i,(a,b) in enumerate([((0,0,-r),(r,0,-r)),((r,0,-r),(r*1.2,0,r*.7)),((r*1.2,0,r*.7),(0,0,r))]):rod(name+str(i),Vector(loc)+Vector(a),Vector(loc)+Vector(b),.35*scale,patch,5)
def pot(name,loc,scale=1,tall=False):
    x,y,z=loc;s=scale;p='cafe_copper'
    prof=[(.05,0),(1.6,0),(2,1),(2.1,4.7 if tall else 3),(1.4,6 if tall else 4),(1.5,6.4 if tall else 4.4),(.7,6.8 if tall else 4.8),(.05,7.2 if tall else 5.2)]
    lathe(name,[(r*s,h*s) for r,h in prof],p,loc)
    h=5 if tall else 3;handle(name+'_Handle',(x+1.8*s,y,z+h*s*.6),1.5*s,s)
    rod(name+'_Spout',(x-1.7*s,y,z+1.5*s),(x-3.4*s,y,z+4*s),.55*s,p,6)
    lathe(name+'_Knob',[(.05,0),(.4,.25),(.25,.7),(.05,.8)],p,(x,y,z+prof[-1][1]*s),8)
def cup(name,loc):
    x,y,z=loc;p='cafe_ivory_ceramic'
    lathe(name+'_Saucer',[(.05,0),(1.9,0),(2.1,.3),(1.8,.5),(.05,.35)],p,loc,10)
    lathe(name,[(.05,.4),(1,.4),(1.35,2.4),(1.1,2.4),(.9,.8),(.05,.8)],p,loc,10)
    handle(name+'_Handle',(x+1.1,y,z+1.45),.7,.65,p)
def author(ident):
    timber='bakery_cart_timber'
    if ident.endswith('Cafe_Chair'):
        box('Seat',(0,0,6.7),(8.5,8.2,1.2),timber)
        for x in [-3.2,3.2]:
            box('Front_Leg',(x,-3,3.1),(1.25,1.25,6.2),timber);box('Back_Post',(x,3,8.4),(1.25,1.25,16.8),timber)
        box('Top_Rail',(0,3,15.8),(8.5,1.4,1.8),timber)
        for x in [-1.5,1.5]:box('Back_Slat',(x,3,11.6),(1.0,1.0,6.5),timber)
        for x in [-3.2,3.2]:box('Low_Rail',(x,0,2.7),(1,6,1),timber)
    elif ident.endswith('Cafe_Counter'):
        box('Cabinet',(0,0,8.1),(24,13,16.2),timber);box('Countertop',(0,0,17),(26,15,1.6),'dark_timber');box('Foot_Rail',(0,-7,1),(25,1.5,2),'dark_timber')
        for x in [-11.4,0,11.4]:box('Front_Stile',(x,-6.7,8.4),(1, .6,15.5),'dark_timber')
    elif ident.endswith('Cafe_Brewing_Set'):
        pot('Coffee_Urn',(-6,1,17.8),1.9,True);pot('Small_Pot',(.8,2.5,17.8),.7)
        cup('Cup_1',(-1,-4,17.8));cup('Cup_2',(4,-3,17.8))
    elif ident.endswith('Cafe_Pastry_Tray'):
        box('Tray',(0,0,.5),(10,10,1),timber)
        for x in [-5,5]:box('Tray_Rim',(x,0,1.2),(.6,10,1.4),timber)
        for y in [-5,5]:box('Tray_Rim',(0,y,1.2),(10,.6,1.4),timber)
        # Existing artwork supplies individual bread forms; one broad carrier only.
        vs=[(-4.6,-4.6,1),(4.6,-4.6,1),(4.6,4.6,1),(-4.6,4.6,1),(-3.7,-3.7,3),(3.7,-3.7,3),(3.7,3.7,3),(-3.7,3.7,3)]
        mesh('Painted_Bread_Pile',vs,[(4,5,6,7),(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)],'bakery_round_crust',[(.02,.02),(.98,.02),(.98,.98),(.02,.98)]*2)
    elif ident.endswith('Cafe_Table_Service'):
        pot('Serving_Pot',(0,1.5,13),1.05);cup('Left_Cup',(-6,-1,13));cup('Right_Cup',(6,-1,13))
    elif ident.endswith('Cafe_Reading_Set'):
        box('Chessboard',(4,1,13.4),(9,9,.8),'cafe_chessboard')
        # Faceted open book, same supplied painted spread over its entire top.
        vs=[(-9,-4,13.25),(-4.5,-4,13.4),(0,-4,13.25),(-9,2,13.25),(-4.5,2,13.4),(0,2,13.25),(-9,-4,13.8),(-4.5,-4,13.45),(0,-4,13.8),(-9,2,13.8),(-4.5,2,13.45),(0,2,13.8)]
        uv=[(0,0),(.5,0),(1,0),(0,1),(.5,1),(1,1)]*2
        mesh('Open_Book',vs,[(6,7,10,9),(7,8,11,10),(0,6,9,3),(2,5,11,8),(0,1,7,6),(1,2,8,7),(3,9,10,4),(4,10,11,5)],'cafe_open_book',uv)
        for i,(x,y) in enumerate([(1.4,-1.3),(3.6,2),(6,3),(6,-2.5)]):lathe('Chess_Piece',[(.05,0),(.48,0),(.25,.5),(.4,.9),(.05,1.2)],'cafe_ivory_ceramic' if i<2 else 'dark_timber',(x,y,13.8),6)
    elif ident.endswith('Garden_Wall_Curve'):
        # A 30-degree segment. Eight instances form a crescent; local ground pivot per segment.
        R=96;n=6
        for name,w,z0,z1,patch in [('Wall',5,-4,17,'cafe_limestone_courses'),('Coping',6.5,17,20,'cafe_limestone_coping')]:
            vs=[];uv=[]
            for i in range(n+1):
                a=math.radians(-15+30*i/n)
                for radius,z in [(R-w/2,z0),(R+w/2,z0),(R-w/2,z1),(R+w/2,z1)]:vs.append((radius*math.sin(a),radius*math.cos(a)-R,z));uv.append((i/n,0 if z==z0 else 1))
            fs=[]
            for i in range(n):
                j=i*4;k=j+4;fs +=[(j,k,k+2,j+2),(j+1,j+3,k+3,k+1),(j+2,k+2,k+3,j+3),(j,j+1,k+1,k)]
            fs +=[(0,2,3,1),(n*4,n*4+1,n*4+3,n*4+2)]
            ob=mesh(name,vs,fs,patch,uv)
            # Faces along the wall share a continuous paint panel, cap faces get full stone patch.
            for poly in ob.data.polygons:
                if poly.index%4==2 or poly.index>=n*4:
                    for li,(u,v) in zip(poly.loop_indices,[(0,0),(1,0),(1,1),(0,1)]):
                        x,y,x1,y1=REGIONS['cafe_limestone_coping'];ob.data.uv_layers[0].data[li].uv=((x+(x1-x)*u)/1024,1-(y+(y1-y)*(1-v))/1024)
    elif ident.endswith('Cobble_Decals'):
        # Existing square-cobble painting, with a new technical courtyard alpha.
        from cafe_courtyard import BOUNDS
        subprocess.run([str(PYTHON),str(ROOT/'project/tools/art/cafe_atlas.py'),'cobbles-mask'],check=True)
        target=SOURCE/'textures/CSC_ALL_Stage_4_Cobbles_B.png'
        material=bpy.data.materials.new('CSC_ALL_Stage_4_Cobble_Decals');material['civ_material']=material.name;material.use_nodes=True
        nt=material.node_tree;bs=nt.nodes.get('Principled BSDF');bs.inputs['Roughness'].default_value=.9
        uv=nt.nodes.new('ShaderNodeUVMap');uv.uv_map='UV1';tex=nt.nodes.new('ShaderNodeTexImage');tex.image=bpy.data.images.load(str(target),check_existing=True);tex.extension='CLIP';nt.links.new(uv.outputs[0],tex.inputs[0]);nt.links.new(tex.outputs['Color'],bs.inputs['Base Color']);nt.links.new(tex.outputs['Alpha'],bs.inputs['Alpha'])
        x0,y0,x1,y1=BOUNDS
        # A single registered alpha card; vertices share L3 coordinates at identity transform.
        poly=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
        data=bpy.data.meshes.new('Courtyard_Cobbles');data.from_pydata([(x,y,0) for x,y in poly],[],[(0,1,2,3)]);data.materials.append(material)
        for name in ['UV1','UV2','UV3']:data.uv_layers.new(name=name)
        for loop in data.loops:
            x,y=poly[loop.vertex_index];data.uv_layers[0].data[loop.index].uv=((x-x0)/(x1-x0),(y-y0)/(y1-y0));data.uv_layers[1].data[loop.index].uv=(.001,.999);data.uv_layers[2].data[loop.index].uv=(.001,.999)
        ob=bpy.data.objects.new('Courtyard_Cobbles',data);export.collection.objects.link(ob);review.collection.objects.link(ob);ob['export_role']='fixed_geometry';ob['geometry_class']='DecalGeometry';ob['source_asset_id']=ID;PARTS.append(ob)
    elif ident in ['CSC_ALL_Oval_Table','CSC_ALL_Flour_Sack_Closed']:
        srcpath=ART/('Props/CSC_Prop_Library/CSC_ALL_Oval_Table.blend' if ident.endswith('Table') else 'Props/Bakers/Bakers_Flour_FINAL/CSC_ALL_Flour_Sack_Closed.blend')
        with bpy.data.libraries.load(str(srcpath),link=False) as (src,dst):dst.objects=list(src.objects)
        for o in dst.objects:
            if o and o.type=='MESH':
                export.collection.objects.link(o);review.collection.objects.link(o);world=o.matrix_world.copy();o.parent=None;o.matrix_world=world;o.modifiers.clear();o.vertex_groups.clear();o.data.materials.clear();o.data.materials.append(mat);o['export_role']='fixed_geometry';o['source_asset_id']=ID;PARTS.append(o)
        (OUT/(ident+'-reuse.json')).write_text(json.dumps(dict(source=str(srcpath),source_sha256=sha(srcpath),geometry_and_uvs_preserved=True),indent=2))
def finish(ident,index,ao_index=None):
    parts=PARTS;bpy.context.window.scene=export
    for o in bpy.context.selected_objects:o.select_set(False)
    for o in parts:
        o.vertex_groups.clear();o.vertex_groups.new(name='Bone').add(list(range(len(o.data.vertices))),1,'REPLACE');o.modifiers.clear();o.modifiers.new('Static rig','ARMATURE').object=rig;o.select_set(True)
    cell=None
    if index<7 or ao_index is not None:
        for o in parts:o.data.uv_layers.active_index=1
        bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(78),island_margin=.035,area_weight=.5,correct_aspect=False);bpy.ops.object.mode_set(mode='OBJECT')
        for o in parts:
            for d in o.data.uv_layers[1].data:d.uv=(.035+d.uv.x*.93,.035+d.uv.y*.93)
        image=bpy.data.images.new('Raw_Self_AO',width=256,height=256,alpha=False);image.generated_color=(1,1,1,1);image.colorspace_settings.name='Non-Color';node=mat.node_tree.nodes.new('ShaderNodeTexImage');node.image=image;mat.node_tree.nodes.active=node
        bpy.ops.object.bake(type='AO',use_clear=False,margin=5);image.filepath_raw=str(OUT/(ident+'-AO.png'));image.file_format='PNG';image.save();mat.node_tree.nodes.remove(node);bpy.data.images.remove(image)
        ai=index if ao_index is None else ao_index
        cell=[(ai%4)*128,512+(ai//4)*128,(ai%4+1)*128,640+(ai//4)*128]
        for o in parts:
            for d in o.data.uv_layers[1].data:d.uv=((cell[0]+d.uv.x*128)/2048,1-(cell[1]+(1-d.uv.y)*128)/2048)
        subprocess.run([str(PYTHON),str(ROOT/'project/tools/art/cafe_atlas.py'),'ao',ident,json.dumps(cell)],check=True)
    for o in parts:o.data.uv_layers.active_index=0;o.data.uv_layers[0].active_render=True
    for im in bpy.data.images:
        if im.source=='FILE':im.reload()
    bpy.context.view_layer.update();points=[o.matrix_world@v.co for o in parts for v in o.data.vertices];lo=Vector([min(p[i] for p in points) for i in range(3)]);hi=Vector([max(p[i] for p in points) for i in range(3)]);center=(lo+hi)*.5;size=max(hi-lo)
    cam=review.camera;cam.location=center+Vector((1.2,-1.6,1.1))*size;cam.rotation_euler=(center-cam.location).to_track_quat('-Z','Y').to_euler();cam.data.ortho_scale=size*1.45
    bpy.context.window.scene=review;path=SOURCE/(ident+'.blend');bpy.ops.wm.save_as_mainfile(filepath=str(path));bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(path))
    with V.suspend_csc_repairs():bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    report=V.validate_current_scene();report['source_sha256']=sha(path);(OUT/(ident+'-validation.json')).write_text(json.dumps(report,indent=2));assert report['automated_pass'],V.format_report(report)
    rev=bpy.data.scenes['Review'];bpy.context.window.scene=rev;rev.render.filepath=str(OUT/(ident+'-preview.png'));bpy.ops.render.render(write_still=True)
    exp=bpy.data.scenes['Export'];bpy.context.window.scene=exp;parts=[o for o in exp.objects if o.type=='MESH'];arm=next(o for o in exp.objects if o.name==ident+'_Rig')
    for o in bpy.context.selected_objects:o.select_set(False)
    copies=[]
    for o in parts:
        c=bpy.data.objects.new(o.name+'_Prepared',o.data.copy());c.data.transform(o.matrix_world);exp.collection.objects.link(c);c.select_set(True);copies.append(c)
    bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=copies[0];joined.name=ident;joined.vertex_groups.new(name='Bone').add(list(range(len(joined.data.vertices))),1,'REPLACE');joined.modifiers.new('Static rig','ARMATURE').object=arm
    cn6=OUT/(ident+'.cn6');geo=OUT/(ident+'.geo');fgx=OUT/(ident+'.fgx');E.csc_do_export_selected(str(cn6),[arm,joined]);summary,vertices,triangles=E.csc_write_geo(str(geo),ident,str(cn6),'DecalGeometry' if index==7 else 'LandmarkModel');geo.write_text(geo.read_text().replace('AssetObjects:','AssetObjects..'))
    lib=ROOT/'project/tools/cn6libs'
    for args,label in [([lib/'CN6ToFGX.exe',cn6,fgx,2],'conversion'),([lib/'FGXToCN6.exe',fgx,OUT/(ident+'-roundtrip.cn6')],'roundtrip')]:
        r=subprocess.run([str(a) for a in args],cwd=lib,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW);(OUT/(ident+'-'+label+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==0 and (fgx.stat().st_size>100)
    import xml.etree.ElementTree as ET
    ast=ET.parse(ROOT/'Civ Supply Chains/Assets/CSC_TAILORS_Tailor_Garment_Rack.ast').getroot();ast.find('m_Name').set('text',ident);ast.find('m_Description').set('text','Individual editable Cafe/shared model; atlas '+RELEASE+'.')
    model=ast.find('m_GeometrySet/m_ModelInstances/Element');model.find('m_Name').set('text',ident);model.find('m_GeoName').set('text',ident);states=model.find('m_GroupStates');templates={e.find('m_StateName').get('text'):copy.deepcopy(e) for e in states};states.clear()
    for gm in ET.parse(geo).findall('m_Meshes/Element'):
        for group in gm.findall('m_Groups/Element'):
            for state in ('Worked','Unworked','Pillaged','Construction','Unbuilt'):
                row=copy.deepcopy(templates[state]);states.append(row);row.find('m_MeshName').set('text',gm.find('m_Name').get('text'));row.find('m_GroupName').set('text',group.find('m_Name').get('text'))
                if index==7:
                    values=row.find('m_Values/m_Values')
                    for val in list(values):
                        param=val.find('m_ParamName').get('text')
                        if param=='Material':val.find('m_ObjectName').set('text','CSC_ALL_Stage_4_Cobble_Decals')
                        elif param!='Visible':values.remove(val)
    ET.indent(ast,space='  ');ET.ElementTree(ast).write(OUT/(ident+'.ast'),encoding='utf-8',xml_declaration=True)
    (OUT/(ident+'-export.json')).write_text(json.dumps(dict(asset_id=ident,vertices=vertices,triangles=triangles,ao_cell=cell,source=str(path),source_sha256=sha(path),bounds=[list(lo),list(hi)]),indent=2));print('CAFE EXPORTED',ident,vertices,triangles,flush=True)
if __name__=='__main__':
    wanted=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else IDS
    for i,ident in enumerate(IDS):
        if ident in wanted:setup(ident);author(ident);finish(ident,i)
