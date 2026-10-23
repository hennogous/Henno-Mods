import bpy,json,sys,hashlib
from pathlib import Path
OUT=Path(sys.argv[sys.argv.index('--')+1]);OUT.mkdir(parents=True,exist_ok=True)
ART=Path.home()/'Desktop/Working Files/3D Art';NAME='CSC_BAKERS_Wind_Mill_Tower'
files=[ART/'BAKERS/Wind Mill/tower'/(n+'.blend') for n in (NAME,NAME+'_CON+PIL')]+[ART/'Level 1/CSC_Level_1_S_CON+PIL.blend']
result=[]
for path in files:
    bpy.ops.wm.open_mainfile(filepath=str(path),load_ui=False,use_scripts=False)
    models=[]
    for ob in bpy.data.objects:
        if ob.type!='MESH':continue
        uv={l.name:dict(min=[min(x.uv[i] for x in l.data) for i in (0,1)],max=[max(x.uv[i] for x in l.data) for i in (0,1)],sha=hashlib.sha256(str([tuple(x.uv) for x in l.data]).encode()).hexdigest()) for l in ob.data.uv_layers}
        models.append(dict(name=ob.name,vertices=len(ob.data.vertices),faces=len(ob.data.polygons),matrix=[list(r) for r in ob.matrix_world],bounds=[[min((ob.matrix_world@v.co)[i] for v in ob.data.vertices) for i in range(3)],[max((ob.matrix_world@v.co)[i] for v in ob.data.vertices) for i in range(3)]],materials=[m.name for m in ob.data.materials],groups=[g.name for g in ob.vertex_groups],uv=uv,props=dict(ob.items())))
    mats={m.name:[dict(name=n.name,image=n.image.name,path=n.image.filepath) for n in m.node_tree.nodes if n.type=='TEX_IMAGE' and n.image] for m in bpy.data.materials if m.use_nodes}
    result.append(dict(path=str(path),sha=hashlib.sha256(path.read_bytes()).hexdigest(),scenes=[s.name for s in bpy.data.scenes],models=models,materials=mats))
(OUT/'inspection.json').write_text(json.dumps(result,indent=2,default=str));print(json.dumps(result,indent=2,default=str))
