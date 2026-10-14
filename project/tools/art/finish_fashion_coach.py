"""Bake coach self-AO, save portable master and stage checked CN6/FGX/GEO/AST."""
import bpy, math, json, sys, subprocess, shutil, copy, xml.etree.ElementTree as ET
from pathlib import Path
from mathutils import Vector
sys.path.insert(0,str(Path(__file__).parent))
from build_fashion_coach import ROOT,OUT,STAGE,ID,module

def main():
    bpy.ops.wm.open_mainfile(filepath=str(OUT/(ID+'.blend')),load_ui=False,use_scripts=False)
    export=bpy.data.scenes['Export'];review=bpy.data.scenes['Review'];bpy.context.window.scene=export
    parts=[o for o in export.objects if o.type=='MESH'];rig=next(o for o in export.objects if o.type=='ARMATURE')
    for o in bpy.context.selected_objects:o.select_set(False)
    for o in parts:o.select_set(True);o.data.uv_layers.active_index=1
    bpy.context.view_layer.objects.active=parts[0]
    bake=bpy.data.images.new('Coach_Raw_Self_AO',width=1024,height=512,alpha=False)
    bake.colorspace_settings.name='Non-Color';bake.generated_color=(1,1,1,1)
    material=parts[0].data.materials[0];nodes=material.node_tree.nodes
    target=nodes.new('ShaderNodeTexImage');target.image=bake;nodes.active=target
    export.cycles.samples=128;export.render.bake.margin=8;export.render.bake.use_clear=False
    bpy.ops.object.bake(type='AO',use_clear=False,margin=8)
    bake.filepath_raw=str(OUT/'coach-raw-AO1024x512.png');bake.file_format='PNG';bake.save()
    nodes.remove(target);bpy.data.images.remove(bake)
    subprocess.run([r'C:\Users\Shadow\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe',ROOT/'project/tools/art/publish_fashion_coach.py','--pack-ao'],check=True)
    shutil.copy2(STAGE/'textures/CSC_Props_Shared_01_AO.png',OUT/'textures/CSC_Props_Shared_01_AO.png')
    for im in bpy.data.images:
        if im.source=='FILE':im.reload()
    for o in parts:
        for loop in o.data.uv_layers[1].data:loop.uv=((1280+loop.uv.x*256)/2048,.5+loop.uv.y*128/2048)
        o.data.uv_layers.active_index=0;o.data.uv_layers[0].active_render=True
        o['reuse_scope']='quarter'
    export['main_geometry_maximum']=1000
    export['atlas_release']='2026-10-13_Shared_01_r023'
    review['atlas_release']='2026-10-13_Shared_01_r023'
    bpy.context.window.scene=review
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ID+'.blend')))
    bpy.ops.file.make_paths_relative();bpy.ops.wm.save_as_mainfile(filepath=str(OUT/(ID+'.blend')))
    review.render.filepath=str(OUT/'coach-preview.png');bpy.ops.render.render(write_still=True)
    # Additional read-only review images with identical lighting.
    camera=review.camera;pos=camera.location.copy();rot=camera.rotation_euler.copy();center=Vector((2,0,8))
    for name,direction in [('rear',(-40,48,28)),('side',(0,-65,12)),('top',(0,-1,70))]:
        camera.location=center+Vector(direction);camera.rotation_euler=(center-camera.location).to_track_quat('-Z','Y').to_euler()
        review.render.filepath=str(OUT/('coach-'+name+'.png'));bpy.ops.render.render(write_still=True)
    camera.location=pos;camera.rotation_euler=rot
    # Clay and mapped AO, keeping material override changes out of saved source.
    clay=bpy.data.materials.new('REVIEW_Clay');clay.diffuse_color=(.45,.45,.45,1);clay.use_nodes=True
    cb=next(n for n in clay.node_tree.nodes if n.type=='BSDF_PRINCIPLED');cb.inputs['Base Color'].default_value=(.45,.45,.45,1)
    review.view_layers[0].material_override=clay;review.render.filepath=str(OUT/'coach-clay.png');bpy.ops.render.render(write_still=True)
    review.view_layers[0].material_override=None
    output=next(n for n in nodes if n.type=='OUTPUT_MATERIAL');old=output.inputs['Surface'].links[0].from_socket
    emit=nodes.new('ShaderNodeEmission');ao=next(n for n in nodes if n.type=='TEX_IMAGE' and n.label=='AO')
    material.node_tree.links.new(ao.outputs['Color'],emit.inputs['Color']);material.node_tree.links.new(emit.outputs[0],output.inputs['Surface'])
    review.render.filepath=str(OUT/'coach-mapped-AO.png');bpy.ops.render.render(write_still=True)
    nodes.remove(emit);material.node_tree.links.new(old,output.inputs['Surface'])
    # Temporary joined geometry, source components remain independent in saved file.
    bpy.context.window.scene=export
    for o in bpy.context.selected_objects:o.select_set(False)
    copies=[]
    for o in parts:
        c=bpy.data.objects.new(o.name+'_Prepared',o.data.copy());export.collection.objects.link(c);c.select_set(True);copies.append(c)
    bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join();joined=copies[0];joined.name=ID
    joined.vertex_groups.new(name='Bone').add(list(range(len(joined.data.vertices))),1,'REPLACE')
    joined.modifiers.new('Static rig','ARMATURE').object=rig
    exporter=module('coach_cn6',ROOT/'project/tools/scripts/io_export_cn6_b4.py')
    cn6=OUT/(ID+'.cn6');geo=OUT/(ID+'.geo');fgx=OUT/(ID+'.fgx')
    exporter.csc_do_export_selected(str(cn6),[rig,joined])
    summaries,vertices,triangles=exporter.csc_write_geo(str(geo),ID,str(cn6),'LandmarkModel')
    assert vertices<=1000,vertices
    geo.write_text(geo.read_text().replace('AssetObjects:','AssetObjects..'))
    lib=ROOT/'project/tools/cn6libs'
    for args,label in [([lib/'CN6ToFGX.exe',cn6,fgx,2],'conversion'),([lib/'FGXToCN6.exe',fgx,OUT/(ID+'-roundtrip.cn6')],'native-readback')]:
        r=subprocess.run([str(a) for a in args],cwd=lib,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        (OUT/(label+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stderr
    ast=ET.parse(ROOT/'Civ Supply Chains/Assets/CSC_TAILORS_Tailor_Garment_Rack.ast').getroot()
    ast.find('m_Name').set('text',ID);ast.find('m_Description').set('text','Burgundy and gold fashion coach with open door, gown, lanterns and driver seat.')
    model=ast.find('m_GeometrySet/m_ModelInstances/Element');model.find('m_Name').set('text',ID);model.find('m_GeoName').set('text',ID)
    states=model.find('m_GroupStates');templates={e.find('m_StateName').get('text'):copy.deepcopy(e) for e in states};states.clear()
    for gm in ET.parse(geo).findall('m_Meshes/Element'):
        for group in gm.findall('m_Groups/Element'):
            for state in ('Worked','Unworked','Pillaged','Construction','Unbuilt'):
                row=copy.deepcopy(templates[state]);states.append(row)
                row.find('m_MeshName').set('text',gm.find('m_Name').get('text'));row.find('m_GroupName').set('text',group.find('m_Name').get('text'))
    ET.indent(ast,space='  ');ET.ElementTree(ast).write(OUT/(ID+'.ast'),encoding='utf-8',xml_declaration=True)
    report=dict(asset_id=ID,exported_vertices=vertices,triangles=triangles,editable_vertices=sum(len(o.data.vertices) for o in parts),components=len(parts),material='CSC_ALL_Props_01',ao_cell=[1280,896,1536,1024],pivot=[0,0,0],front='+X',atlas_release='2026-10-13_Shared_01_r023',converted=True)
    (OUT/'export-report.json').write_text(json.dumps(report,indent=2));print('COACH_EXPORTED',json.dumps(report))

if __name__=='__main__':main()
