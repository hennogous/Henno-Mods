"""UV-only roof seam orientation pass; geometry/AO remain identical."""
import bpy,sys,json,shutil,math,ast
from pathlib import Path
from mathutils import Matrix,Vector
ROOT=Path(__file__).resolve().parents[4];OUT=Path(sys.argv[sys.argv.index('--')+1]);ASSET='CSC_BAKERS_Wind_Mill_Modern'
sys.path[:0]=[str(ROOT/'project/tools/blender'),str(ROOT/'project/tools/blender/scene_export')]
from csc_scene_validation import suspend_csc_repairs
import decode_blend as dec
with suspend_csc_repairs():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/(ASSET+'.blend')),load_ui=False,use_scripts=False)
    scene=bpy.data.scenes['Export'];bpy.context.window.scene=scene;mat=bpy.data.materials[ASSET]
    tree=ast.parse((Path(__file__).parent/'build_model.py').read_text());exec(compile(ast.Module(body=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='tileuv'],type_ignores=[]),'<UV helper>','exec'))
    inv=(Matrix.Rotation(math.radians(42.3),4,'Z')@Matrix.Translation(Vector((-101,-126,0)))).inverted()
    for o in scene.objects:
        if o.type!='MESH' or not any(n in o.name for n in ('Main_Roof','Shelter_Roof','Intake_Roof','Silo_Cap','Elevator_Cap')):continue
        local=[inv@o.matrix_world@v.co for v in o.data.vertices]
        for p in o.data.polygons:
            uv=o.data.uv_layers[0];us=[uv.data[li].uv.copy() for li in p.loop_indices]
            tile=int(sum(u.x for u in us)/len(us)*4)%4+4*min(3,int((1-sum(u.y for u in us)/len(us))*4))
            # Edge faces use a quiet space between the registered seams.
            local_normal=(inv@o.matrix_world).to_3x3()@p.normal
            if 'Intake_Roof' in o.name and local_normal.z>.5:
                cx=sum(v.x for v in local)/len(local);cy=sum(v.y for v in local)/len(local)
                for li in p.loop_indices:
                    v=local[o.data.loops[li].vertex_index];uv.data[li].uv=tileuv(2,.25+(v.x-cx+8)/96,(v.y-cy+9)/32)
            elif tile==2 and abs(local_normal.z)<.45 and 'Silo_Cap' not in o.name:
                for li,u in zip(p.loop_indices,us):uv.data[li].uv=tileuv(2,.012+.006*(u.x*4%1),.05+.9*(u.y*4%1))
    for ch in ('B','N','G','M','E'):
        shutil.copy2(OUT.parent/'textures'/f'{ASSET}_{ch}.png',OUT/'textures'/f'{ASSET}_{ch}.png')
    for n in mat.node_tree.nodes:
        if n.type=='TEX_IMAGE' and n.image:n.image.reload()
    bpy.context.window.scene=bpy.data.scenes['Review'];bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ASSET+'.blend')),relative_remap=False)
    bpy.context.window.scene=scene
    decoded=[dec.decode_mesh(o,o.matrix_world) for o in scene.objects if o.type=='MESH' and o.get('export_role') in ('building_geometry','fixed_geometry')]
    parts=[dec.merge_meshes(ASSET+'_'+label,[m for m in decoded if m['role']==role]) for role,label in [('building_geometry','Building'),('fixed_geometry','Stock')]]
    (OUT/'model.json').write_text(json.dumps({'asset_id':ASSET,'kind':'building','meshes':parts}))
    (OUT/'roof-uv-final.json').write_text(json.dumps({'intake_seams':'downhill; 8-unit pitch','atlas_seams':12,'geometry_and_AO_unchanged':True,'vertices':sum(len(p['vertices']) for p in parts),'triangles':sum(len(p['triangles']) for p in parts)},indent=2))
    print('ROOF_UV_CORRECTED')
