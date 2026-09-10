import bpy, math, json, os, bmesh, importlib.util
from mathutils import Vector
from collections import defaultdict

OUT='/Users/henno.gous/Play/Henno-Mods/output/blacksmith-v2'
NAME='CSC_BLACKSMITH_Workshop_v2'
# New scene preserves the user's original scene and its objects.
old=bpy.data.scenes.get(NAME)
if old:
    bpy.context.window.scene=next(s for s in bpy.data.scenes if s!=old)
    for ob in list(old.objects):
        if len(ob.users_scene)==1:bpy.data.objects.remove(ob,do_unlink=True)
    bpy.data.scenes.remove(old)
scene=bpy.data.scenes.new(NAME)
bpy.context.window.scene=scene
asset=bpy.data.collections.new('BLACKSMITH | primitive source')
scene.collection.children.link(asset)
studio=bpy.data.collections.new('PREVIEW | cameras and lighting')
scene.collection.children.link(studio)
materials=[]
parts=[]

def mat(name,color,rough=.8,metal=0,emission=0):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF')
    p.inputs['Base Color'].default_value=(*color,1)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metal
    if emission:
        p.inputs['Emission Color'].default_value=(*color,1); p.inputs['Emission Strength'].default_value=emission
    materials.append(m); return m

plaster=mat('Preview | warm lime plaster',(.48,.34,.20))
wood=mat('Preview | oak structure',(.065,.030,.013))
roof=mat('Preview | clay roof',(.49,.16,.065))
stone=mat('Preview | warm grey masonry',(.36,.34,.28))
dark=mat('Preview | forge recess',(.025,.018,.014))
iron=mat('Preview | forged iron',(.115,.145,.16),.38,.65)
cutwood=mat('Preview | cut timber',(.38,.24,.105))
embers=mat('Preview | hot coals',(1,.16,.008),.9,0,3)
banner=mat('Preview | ochre leather sign',(.45,.12,.045))

# Preview-only broad material pattern; does not add a single vertex.
def brick_shader(m,c1,c2,mortar,scale,width,height):
    ns=m.node_tree.nodes; ls=m.node_tree.links; p=ns.get('Principled BSDF')
    uv=ns.new('ShaderNodeUVMap'); uv.uv_map='UV1'
    t=ns.new('ShaderNodeTexBrick'); t.offset=.5; t.offset_frequency=2
    t.inputs['Color1'].default_value=(*c1,1); t.inputs['Color2'].default_value=(*c2,1)
    t.inputs['Mortar'].default_value=(*mortar,1)
    t.inputs['Scale'].default_value=scale; t.inputs['Mortar Size'].default_value=.013
    t.inputs['Mortar Smooth'].default_value=.01
    t.inputs['Brick Width'].default_value=width; t.inputs['Row Height'].default_value=height
    ls.new(uv.outputs['UV'],t.inputs['Vector']); ls.new(t.outputs['Color'],p.inputs['Base Color'])
    bump=ns.new('ShaderNodeBump'); bump.inputs['Strength'].default_value=.22; bump.inputs['Distance'].default_value=.025
    ls.new(t.outputs['Fac'],bump.inputs['Height']); ls.new(bump.outputs['Normal'],p.inputs['Normal'])
brick_shader(roof,(.30,.072,.025),(.49,.165,.055),(.19,.062,.023),1,.43,.31)
brick_shader(stone,(.16,.15,.125),(.28,.255,.205),(.13,.12,.098),1,.51,.32)

# Irregularity stays in the preview shader; the mesh carries only large forms.
for material in [roof,stone]:
    ns=material.node_tree.nodes;ls=material.node_tree.links
    tex=next(n for n in ns if n.type=='TEX_BRICK')
    tex.inputs['Mortar Size'].default_value=.006
    tex.inputs['Mortar Smooth'].default_value=.007
    uv=next(n for n in ns if n.type=='UVMAP')
    noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.7;noise.inputs['Detail'].default_value=2
    ls.new(uv.outputs['UV'],noise.inputs['Vector'])
    center=ns.new('ShaderNodeVectorMath');center.operation='SUBTRACT';center.inputs[1].default_value=(.5,.5,.5)
    ls.new(noise.outputs['Color'],center.inputs[0])
    amp=ns.new('ShaderNodeVectorMath');amp.operation='SCALE';amp.inputs[3].default_value=.030 if material==roof else .050
    ls.new(center.outputs[0],amp.inputs[0])
    warped=ns.new('ShaderNodeVectorMath');warped.operation='ADD';ls.new(uv.outputs[0],warped.inputs[0]);ls.new(amp.outputs[0],warped.inputs[1]);ls.new(warped.outputs[0],tex.inputs['Vector'])
    variation=ns.new('ShaderNodeMixRGB');variation.blend_type='MULTIPLY';variation.inputs[0].default_value=.22
    ls.new(tex.outputs['Color'],variation.inputs[1]);ls.new(noise.outputs['Fac'],variation.inputs[2])
    ls.new(variation.outputs[0],ns.get('Principled BSDF').inputs['Base Color'])
for material,lo,hi in [(wood,(.033,.016,.007),(.12,.062,.025)),(plaster,(.34,.23,.13),(.57,.42,.25)),(cutwood,(.18,.086,.032),(.35,.20,.076))]:
    ns=material.node_tree.nodes;ls=material.node_tree.links;p=ns.get('Principled BSDF')
    uv=ns.new('ShaderNodeUVMap');uv.uv_map='UV1'
    scale=ns.new('ShaderNodeVectorMath');scale.operation='MULTIPLY';scale.inputs[1].default_value=(32,1.6,1) if material!=plaster else (3,3,3)
    ls.new(uv.outputs[0],scale.inputs[0])
    noise=ns.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1;noise.inputs['Detail'].default_value=2.5;ls.new(scale.outputs[0],noise.inputs['Vector'])
    ramp=ns.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=.20;ramp.color_ramp.elements[0].color=(*lo,1);ramp.color_ramp.elements[1].position=.8;ramp.color_ramp.elements[1].color=(*hi,1)
    ls.new(noise.outputs['Fac'],ramp.inputs[0]);ls.new(ramp.outputs[0],p.inputs['Base Color'])
    bump=ns.new('ShaderNodeBump');bump.inputs['Strength'].default_value=.16;bump.inputs['Distance'].default_value=.022
    ls.new(noise.outputs['Fac'],bump.inputs['Height']);ls.new(bump.outputs[0],p.inputs['Normal'])

def mesh(name,vs,fs,m):
    me=bpy.data.meshes.new(name); me.from_pydata(vs,[],fs); me.update()
    ob=bpy.data.objects.new(name,me); asset.objects.link(ob); me.materials.append(m)
    bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(me); bm.free()
    parts.append(ob); return ob

def box(name,center,size,m,top=True,bottom=False,taper=1):
    x,y,z=center; a,b,c=(q/2 for q in size)
    vs=[(x+dx*a,y+dy*b,z-c) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    vs += [(x+dx*a*taper,y+dy*b*taper,z+c) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
    fs=[(0,1,5,4),(1,2,6,5),(2,3,7,6),(3,0,4,7)]
    if top:fs.append((4,5,6,7))
    if bottom:fs.append((3,2,1,0))
    return mesh(name,vs,fs,m)

def beam(name,a,b,width,depth=None,m=wood):
    a,b=Vector(a),Vector(b); d=b-a
    ob=box(name,(0,0,0),(width,depth or width,d.length),m,bottom=True)
    q=d.to_track_quat('Z','Y'); mid=(a+b)/2
    for v in ob.data.vertices:v.co=q@v.co+mid
    return ob

def cylinder(name,center,rings,n,m,cap=True):
    x,y,z=center
    vs=[(x+r*math.cos(2*math.pi*i/n),y+r*math.sin(2*math.pi*i/n),z+h) for h,r in rings for i in range(n)]
    fs=[]
    for j in range(len(rings)-1):
        for i in range(n):fs.append((j*n+i,j*n+(i+1)%n,(j+1)*n+(i+1)%n,(j+1)*n+i))
    if cap:fs.append(tuple((len(rings)-1)*n+i for i in range(n)))
    return mesh(name,vs,fs,m)

def profile_prism(name,profile,y0,y1,m,back=True):
    n=len(profile);vs=[(x,y,z) for y in (y0,y1) for x,z in profile]
    fs=[tuple(range(n-1,-1,-1))]
    if back:fs.append(tuple(range(n,n*2)))
    fs += [(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    return mesh(name,vs,fs,m)

# House gable: broad mass, very steep roof, flared feet at the eaves.
profile=[(-2,0.15),(.35,.15),(.35,2.65),(-.1,3.02),(-.53,3.7),(-.88,4.65),(-1.3,3.7),(-1.72,3.04),(-2,2.67)]
profile_prism('01 | main plaster volume',profile,-1.3,1.35,plaster)
box('02 | stone sill',(-.825,0,.17),(2.45,2.7,.34),stone)
roofline=[(-2.34,2.63),(-1.87,2.94),(-1.39,3.64),(-.88,4.75),(-.42,3.64),(.08,2.96),(.66,2.66)]
def roof_sheet(name,line,y0,y1):
    ys=[y0,(y0+y1)/2,y1] if name.startswith('03') else [y0,y1]
    n=len(line)
    vs=[(x,y,z+(.10 if j in (0,len(ys)-1) else -.10)*max(0,(z-2.6)/2.15)) for j,y in enumerate(ys) for x,z in line]
    fs=[(j*n+i,j*n+i+1,(j+1)*n+i+1,(j+1)*n+i) for j in range(len(ys)-1) for i in range(n-1)]
    return mesh(name,vs,fs,roof)
roof_sheet('03 | six-plane sweeping roof',roofline,-1.62,1.58)
# Swept gable trim needs only a narrow strip, not individual bevelled beams.
def trim(name,line,y0,y1,thick):
    prof=line+[(x,z-thick) for x,z in reversed(line)]
    return profile_prism(name,prof,y0,y1,wood)
trim('04 | front sweeping bargeboard',roofline,-1.69,-1.53,.16)
trim('05 | rear sweeping bargeboard',roofline,1.51,1.64,.16)
vs=[]
for y,z in [(-1.73,4.92),(0,4.72),(1.72,4.92)]:
    vs.extend([(-.99,y,z-.12),(-.77,y,z-.12),(-.77,y,z+.12),(-.99,y,z+.12)])
fs=[(j*4+i,j*4+(i+1)%4,(j+1)*4+(i+1)%4,(j+1)*4+i) for j in range(2) for i in range(4)]+[(3,2,1,0),(8,9,10,11)]
mesh('06 | bowed ridge cap',vs,fs,wood)
for y in [-1.6,1.59]:
    box('07 | ridge terminal',(-.88,y,4.95),(.36,.30,.37),wood,taper=.82)

# Framing, door, and loft opening. Texture will provide joinery and fine lines.
for x in [-1.96,.29]:
    beam('10 | front corner post',(x,-1.34,.28),(x,-1.34,2.7),.19)
beam('11 | front cross beam',(-2.03,-1.36,2.66),(.40,-1.36,2.66),.21)
beam('12 | front floor beam',(-1.98,-1.36,1.92),(.30,-1.36,1.92),.15)
mesh('13 | door opening',[(-1.80,-1.39,.18),(-1.16,-1.39,.18),(-1.16,-1.39,1.64),(-1.80,-1.39,1.64)],[(0,1,2,3)],dark)
box('14 | oak door',(-1.48,-1.40,.9),(.56,.065,1.34),wood)
for z in [.43,1.27]:mesh('15 | door strap',[(-1.72,-1.444,z-.0275),(-1.24,-1.444,z-.0275),(-1.24,-1.444,z+.0275),(-1.72,-1.444,z+.0275)],[(0,1,2,3)],iron)
box('16 | door handle',(-1.31,-1.47,.87),(.055,.04,.13),iron)
box('17 | lower step',(-1.48,-1.70,.105),(.91,.58,.21),stone)
box('18 | upper step',(-1.48,-1.53,.23),(.77,.38,.25),stone)
roof_sheet('19 | door hood',[(-1.92,1.65),(-1.86,1.95),(-1.06,1.95),(-1.02,1.65)],-1.72,-1.34)
mesh('20 | loft dark opening',[(-1.105,-1.39,2.875),(-.655,-1.39,2.875),(-.655,-1.39,3.485),(-1.105,-1.39,3.485)],[(0,1,2,3)],dark)
for x in [-1.13,-.63]:beam('21 | loft jamb',(x,-1.40,2.86),(x,-1.40,3.51),.095)
beam('22 | loft lintel',(-1.2,-1.42,3.5),(-.56,-1.42,3.5),.13)
beam('23 | loft sill',(-1.19,-1.44,2.85),(-.56,-1.44,2.85),.14)

# Low, open working bay set forward of the chimney so anvil stays visible.
roof_sheet('30 | sloping forge canopy',[(.29,2.70),(1.15,2.38),(2.25,2.24)],-1.22,1.38)
beam('31 | front canopy fascia',(.29,-1.24,2.56),(2.30,-1.24,2.19),.17)
beam('32 | side canopy fascia',(2.25,-1.31,2.18),(2.25,1.45,2.18),.16)
for y in [-1.13,1.19]:
    box('33 | post stone foot',(2.03,y,.20),(.39,.39,.4),stone,taper=.84)
    beam('34 | canopy upright',(2.03,y,.32),(2.03,y,2.27),.22)
    beam('35 | diagonal knee brace',(2.03,y,1.65),(1.49,y,2.35),.13)

# Chimney is the second primary silhouette: taper, oversize, a sloped open cap.
box('40 | forge chimney shaft',(1.13,.87,2.58),(1.42,1.19,5.16),stone,top=False,taper=.57)
box('41 | chimney collar',(1.13,.87,4.79),(.94,.87,.25),stone,top=False)
for x in [.78,1.48]:
    for y in [.54,1.20]:box('42 | chimney cap support',(x,y,5.12),(.17,.17,.50),stone)
# A ring between two rectangles forms the marble-safe hood; inner hole remains open.
vs=[]
for z,rx,ry in [(5.20,.67,.60),(5.70,.39,.35),(5.70,.25,.22),(5.26,.25,.22)]:
    vs += [(1.13+dx*rx,.87+dy*ry,z) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
fs=[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
fs +=[(i+4,(i+1)%4+4,(i+1)%4+8,i+8) for i in range(4)]
fs +=[(i+8,(i+1)%4+8,(i+1)%4+12,i+12) for i in range(4)]
mesh('43 | sloped hollow chimney hood',vs,fs,stone)

# Forge: genuine polygonal arch opening; recessed dark throat and hot hearth.
cx=1.13; cy=.23; spring=.97; ri=.40; ro=.61; seg=6
vs=[]
for y in [cy-.15,cy+.15]:
    for r in [ri,ro]:
        vs += [(cx+r*math.cos(math.pi*i/seg),y,spring+r*math.sin(math.pi*i/seg)) for i in range(seg+1)]
n=seg+1
fs=[]
for i in range(seg):
    fs += [(i,i+1,n+i+1,n+i),(i,i+2*n,i+2*n+1,i+1),(n+i,n+i+1,3*n+i+1,3*n+i)]
mesh('50 | six-segment forge arch',vs,fs,stone)
for x in [cx-.505,cx+.505]:box('51 | forge jamb',(x,cy,.69),(.21,.30,.56),stone)
profile_prism('52 | soot-black firebox',[(cx-ri,.39),(cx+ri,.39)]+[(cx+ri*math.cos(math.pi*i/seg),spring+ri*math.sin(math.pi*i/seg)) for i in range(seg+1)],.29,.32,dark)
box('53 | projecting hearth',(cx,-.02,.40),(1.34,.90,.24),stone)
box('54 | live coal bed',(cx,.05,.56),(.70,.42,.075),embers)
# Low faceted coal pile reads more naturally than a flat glowing rectangle.
cylinder('55 | embers',(cx,.08,.56),[(0,.26),(.17,.16),(.22,.045)],5,embers)

# Anvil on a broad stump: minimal sectional geometry, distinctive horn silhouette.
cylinder('60 | anvil stump',(1.02,-1.10,.05),[(0,.36),(.57,.32)],8,cutwood)
box('61 | anvil foot',(1.02,-1.10,.65),(.57,.35,.13),iron,taper=.72)
box('62 | anvil waist',(1.02,-1.10,.80),(.26,.21,.22),iron,taper=.78)
box('63 | anvil face',(1.00,-1.10,.98),(.61,.35,.20),iron,taper=1.05)
mesh('64 | anvil pointed horn',[(1.30,-1.275,1.08),(1.30,-.925,1.08),(1.30,-.97,.90),(1.30,-1.23,.90),(1.78,-1.10,1.04)],[(0,1,4),(1,2,4),(2,3,4),(3,0,4)],iron)

# Restrained secondary props and an unlettered smith's banner.
cylinder('70 | barrel',(-.43,-1.60,.08),[(0,.23),(.30,.28),(.62,.22)],8,wood)
# Barrel hoops belong in the final texture, saving 64 seam-split vertices.
mesh('72 | hanging ochre banner',[(-.58,-1.40,1.82),(-.06,-1.40,1.82),(-.06,-1.40,.82),(-.29,-1.42,.68),(-.58,-1.40,.82)],[(0,1,2,3,4)],banner)
# Flat iron anvil emblem on the banner, geometric marking rather than text.
mesh('73 | anvil emblem',[(-.49,-1.432,1.33),(-.12,-1.432,1.33),(-.19,-1.432,1.23),(-.27,-1.432,1.20),(-.27,-1.432,1.08),(-.18,-1.432,1.04),(-.45,-1.432,1.04),(-.36,-1.432,1.10),(-.36,-1.432,1.22)], [tuple(range(9))],iron)

# Open quenching trough: four exterior walls, four interior walls, rim and water.
tx,ty=2.16,-.06
vs=[]
for z,rx,ry in [(0,.25,.34),(.53,.32,.41),(.53,.26,.35),(.10,.21,.28)]:
    vs +=[(tx+dx*rx,ty+dy*ry,z) for dx,dy in [(-1,-1),(1,-1),(1,1),(-1,1)]]
fs=[(i,(i+1)%4,(i+1)%4+4,i+4) for i in range(4)]
fs +=[(i+4,(i+1)%4+4,(i+1)%4+8,i+8) for i in range(4)]
fs +=[(i+8,(i+1)%4+8,(i+1)%4+12,i+12) for i in range(4)]
mesh('74 | open wooden quench trough',vs,fs,wood)
water=mat('Preview | still quench water',(.033,.095,.10),.24,.2)
mesh('75 | water surface',[(tx-.25,ty-.34,.43),(tx+.25,ty-.34,.43),(tx+.25,ty+.34,.43),(tx-.25,ty+.34,.43)],[(0,1,2,3)],water)


# Shape pass: apply changes to source pieces before rebuilding export geometry.
for ob in parts:
    if ob.name.startswith('70 |'):
        for v in ob.data.vertices:v.co.z-=.08
    if ob.name[:2] in ['60','61','62','63','64']:
        for v in ob.data.vertices:
            v.co=Vector((1.02,-1.1,.05))+(v.co-Vector((1.02,-1.1,.05)))*1.12+Vector((-.10,-.24,-.05))
    if ob.name[:2] in ['04','05']:
        for v in ob.data.vertices:v.co.z+=.10*max(0,(v.co.z-2.6)/2.15)
    # Slightly splayed bay supports, keeping their feet planted.
    if ob.name.startswith('34 |'):
        for v in ob.data.vertices:v.co.x+=.08*(1-v.co.z/2.3)
    # Delete only rear surfaces buried against the front wall.
    if ob.name[:2] in ['10','11','12','21','22','23']:
        bm=bmesh.new();bm.from_mesh(ob.data);bm.normal_update()
        buried=[f for f in bm.faces if f.normal.y>.99]
        bmesh.ops.delete(bm,geom=buried,context='FACES');bm.to_mesh(ob.data);bm.free()

# Each face owns its AO slot. This deliberately captures the seam-split budget.
face_total=sum(len(o.data.polygons) for o in parts); grid=math.ceil(math.sqrt(face_total));face_id=0
for ob in parts:
    me=ob.data
    for name in ['UV1','UV2','UV3']:me.uv_layers.new(name=name)
    for poly in me.polygons:
        normal=poly.normal; axis=max(range(3),key=lambda k:abs(normal[k]));axes=[k for k in range(3) if k!=axis]
        if me.materials[0] in [wood,cutwood]:
            # Grain follows the longest physical direction of each wooden face.
            spans={k:max(me.vertices[i].co[k] for i in poly.vertices)-min(me.vertices[i].co[k] for i in poly.vertices) for k in axes}
            axes.sort(key=lambda k:spans[k])
        coords=[]
        for li in poly.loop_indices:
            p=me.vertices[me.loops[li].vertex_index].co
            uv=(p.y,p.x*1.2) if me.materials[0]==roof else (p[axes[0]],p[axes[1]])
            if ob.name.startswith('03'):
                # Arc-length along the roof avoids stretching tiles on steep faces.
                distance=0
                for (xa,za),(xb,zb) in zip(roofline,roofline[1:]):
                    t=max(0,min(1,(p.x-xa)/(xb-xa)))
                    distance+=t*math.hypot(xb-xa,zb-za)
                uv=(p.y,distance)
            me.uv_layers['UV1'].data[li].uv=uv;me.uv_layers['UV3'].data[li].uv=(0,0)
            coords.append((p[axes[0]],p[axes[1]]))
        mins=[min(c[k] for c in coords) for k in range(2)];span=[max(c[k] for c in coords)-mins[k] for k in range(2)]
        for li,co in zip(poly.loop_indices,coords):
            me.uv_layers['UV2'].data[li].uv=((face_id%grid+.08+.84*(co[0]-mins[0])/max(span[0],.00001))/grid,(face_id//grid+.08+.84*(co[1]-mins[1])/max(span[1],.00001))/grid)
        face_id+=1

# Make an export-check duplicate, retaining editable primitive sources.
export_col=bpy.data.collections.new('EXPORT CHECK | joined mesh and armature');scene.collection.children.link(export_col)
bpy.ops.object.select_all(action='DESELECT')
copies=[]
for ob in parts:
    cp=ob.copy();cp.data=ob.data.copy();export_col.objects.link(cp);cp.select_set(True);copies.append(cp)
bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=bpy.context.object;joined.name=NAME+'_Bldg'
# Apply hard face splits before CN6 because this exporter averages vertex normals.
bm=bmesh.new();bm.from_mesh(joined.data);bmesh.ops.split_edges(bm,edges=list(bm.edges));bm.to_mesh(joined.data);bm.free()
armdata=bpy.data.armatures.new('Armature');arm=bpy.data.objects.new(NAME,armdata);export_col.objects.link(arm)
bpy.context.view_layer.objects.active=arm;arm.select_set(True);joined.select_set(False);bpy.ops.object.mode_set(mode='EDIT')
bone=armdata.edit_bones.new('Bone');bone.head=(0,0,0);bone.tail=(0,0,1);bpy.ops.object.mode_set(mode='OBJECT')
joined.parent=arm;mod=joined.modifiers.new('Armature','ARMATURE');mod.object=arm
vg=joined.vertex_groups.new(name='Bone');vg.add(list(range(len(joined.data.vertices))),1,'REPLACE')
# Scale mesh data into Civ building units; source and preview remain at convenient scale.
for v in joined.data.vertices:v.co*=30
joined.data.calc_loop_triangles()
stats={'source_vertices':sum(len(o.data.vertices) for o in parts),'split_vertices':len(joined.data.vertices),'triangles':len(joined.data.loop_triangles),'primitive_objects':len(parts),'note':'Preview materials; not texture-baked or FGX/cooked. CN6 measured separately.'}
with open(os.path.join(OUT,'budget.json'),'w') as f:json.dump(stats,f,indent=2)
print('BUDGET',json.dumps(stats))
spec=importlib.util.spec_from_file_location('cn6_export','/Users/henno.gous/Play/Henno-Mods/project/tools/scripts/io_export_cn6_b4.py')
ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
bpy.ops.object.select_all(action='DESELECT');arm.select_set(True);joined.select_set(True);bpy.context.view_layer.objects.active=joined
ex.do_export(os.path.join(OUT,NAME+'.cn6'),True,True)
export_col.hide_render=True;export_col.hide_viewport=True

# Orthographic studio preview. These helpers are not in the export selection.
def studio_obj(ob):
    for col in list(ob.users_collection):col.objects.unlink(ob)
    studio.objects.link(ob)
bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.035));floor=bpy.context.object;floor.name='Preview ground';studio_obj(floor)
floor.data.materials.append(mat('Preview | ivory backdrop',(.74,.69,.59)))
def aim(ob,point):ob.rotation_euler=(Vector(point)-ob.location).to_track_quat('-Z','Y').to_euler()
bpy.ops.object.camera_add(location=(9,-14,10));cam=bpy.context.object;studio_obj(cam);cam.name='Preview camera';aim(cam,(0,0,2.60));cam.data.type='ORTHO';cam.data.ortho_scale=8.45;scene.camera=cam
for name,loc,power,size in [('Key',(-3,-4,9),1250,6),('Fill',(5,-1,6),650,5),('Rim',(0,5,8),1000,4)]:
    bpy.ops.object.light_add(type='AREA',location=loc);li=bpy.context.object;li.name=name;studio_obj(li);li.data.energy=power;li.data.shape='DISK';li.data.size=size;aim(li,(0,0,2))
bpy.ops.object.light_add(type='POINT',location=(cx,-.15,.9));li=bpy.context.object;studio_obj(li);li.name='Forge glow';li.data.energy=9;li.data.color=(1,.23,.035);li.data.shadow_soft_size=.3
scene.world=bpy.data.worlds.new('Blacksmith studio');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.64,.70,.8,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.4
scene.render.engine='CYCLES';scene.cycles.samples=56;scene.cycles.use_denoising=True
scene.render.resolution_x=1200;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
scene.view_settings.view_transform='AgX';scene.view_settings.look='AgX - Medium High Contrast';scene.view_settings.exposure=-.30
scene.render.image_settings.file_format='PNG';scene.render.filepath=os.path.join(OUT,'blacksmith-render-v2.png')
bpy.ops.object.select_all(action='DESELECT')
for area in bpy.context.screen.areas:
    if area.type=='VIEW_3D':
        area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.overlay.show_overlays=False
        area.spaces.active.shading.type='MATERIAL'
        area.spaces.active.region_3d.view_camera_zoom=5
        area.spaces.active.show_region_ui=False
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,NAME+'.blend'))
print('SAVED',bpy.data.filepath)
