"""Extract Henno's revision-10 wall rack as one independently installable prop.

Run in background Blender. Leaves the source blend and existing AE assemblies intact.
"""
import bpy
import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / 'Civ Supply Chains'
SOURCE = Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\TAILORS\Tailor\revision-10-vertex-budget\CSC_TAILORS_Tailor_2.blend')
OUT = Path(r'C:\Users\Shadow\Desktop\Codex\Tailor-wall-garment-rack-20261013')
ID = 'CSC_TAILORS_Tailor_Garment_Rack'
LIBS = ROOT / 'project/tools/cn6libs'

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

def run(args, label):
    result = subprocess.run([str(a) for a in args], cwd=LIBS, capture_output=True, text=True,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    (OUT / (label + '.log')).write_text(result.stdout + result.stderr)
    assert result.returncode == 0, result.stdout + result.stderr

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    source_hash = sha(SOURCE)
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE), load_ui=False, use_scripts=False)
    controller = bpy.data.objects['Place_Wall_Garment_Rack']
    meshes = sorted([o for o in controller.children_recursive if o.type == 'MESH'], key=lambda o:o.name)
    assert len(meshes) == 25
    assert all(bpy.data.objects.get('CSC_Fixed_Hanging_%d_Body' % i) in meshes for i in (1,2,3))
    before = {o.name: [tuple(o.matrix_world @ v.co) for v in o.data.vertices] for o in meshes}
    pivot = Vector((controller.matrix_world.translation.x, controller.matrix_world.translation.y,
                    min(p[2] for points in before.values() for p in points)))
    source_matrices = {o.name:[list(r) for r in o.matrix_world] for o in meshes}
    for obj in list(bpy.data.objects):
        if obj not in meshes and obj != controller:
            bpy.data.objects.remove(obj, do_unlink=True)
    for scene in list(bpy.data.scenes):
        scene.name = 'OLD_' + scene.name
    export = bpy.data.scenes.new('Export')
    review = bpy.data.scenes.new('Review')
    bpy.context.window.scene = export
    for scene in list(bpy.data.scenes):
        if scene not in (export, review):
            bpy.data.scenes.remove(scene)
    for obj in [controller] + meshes:
        export.collection.objects.link(obj)
        review.collection.objects.link(obj)
        obj.hide_render = False
        obj.hide_viewport = False
        obj.hide_set(False)
    controller.location -= pivot
    controller.name = ID + '_Components'
    controller['source_blend'] = str(SOURCE)
    controller['source_pivot'] = list(pivot)
    controller['note'] = 'One asset: rack, three hangers and three garments; component transforms retained.'
    export.view_layers[0].update()
    parity = max((o.matrix_world @ v.co + pivot - Vector(before[o.name][i])).length
                 for o in meshes for i,v in enumerate(o.data.vertices))
    assert parity < 0.0001, parity
    rigdata = bpy.data.armatures.new(ID + '_Rig')
    rig = bpy.data.objects.new(ID + '_Rig', rigdata)
    export.collection.objects.link(rig)
    review.collection.objects.link(rig)
    bpy.context.view_layer.objects.active = rig
    rig.select_set(True)
    bpy.ops.object.mode_set(mode='EDIT')
    bone = rigdata.edit_bones.new('Bone')
    bone.head = (0,0,0); bone.tail = (0,0,1)
    bpy.ops.object.mode_set(mode='OBJECT')
    for obj in meshes:
        obj['export_role'] = 'fixed_geometry'
        obj['source_asset_id'] = ID
        obj.vertex_groups.clear()
        obj.vertex_groups.new(name='Bone').add(list(range(len(obj.data.vertices))), 1.0, 'REPLACE')
        for modifier in list(obj.modifiers):
            assert modifier.type == 'ARMATURE', (obj.name, modifier.type)
            obj.modifiers.remove(modifier)
        obj.modifiers.new('Static rig', 'ARMATURE').object = rig
    # Keep the existing shared material and portable preview images.
    textures = OUT / 'textures'; textures.mkdir(exist_ok=True)
    used_images = {n.image for o in meshes for mat in o.data.materials
                   for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image}
    for im in used_images:
        source = Path(bpy.path.abspath(im.filepath))
        assert source.is_file(), source
        dest = textures / source.name
        shutil.copy2(source, dest)
        im.filepath = str(dest)
    for scene in (export, review):
        world = bpy.data.worlds.new(scene.name + '_World'); world.use_nodes = True
        bg = next(n for n in world.node_tree.nodes if n.type == 'BACKGROUND')
        bg.inputs['Color'].default_value = (.7,.8,1,1)
        bg.inputs['Strength'].default_value = .65
        scene.world = world
        scene.render.engine = 'CYCLES'
        scene.cycles.samples = 32
        scene.view_settings.view_transform = 'AgX' if scene == export else 'Standard'
        scene.view_settings.exposure = .35 if scene == export else -.1
        scene.view_settings.gamma = 1
    sun = bpy.data.lights.new('Review_Key', 'SUN'); sun.energy = 3.2
    sun.color = (1,.92,.8); sun.angle = math.radians(6); sun.use_shadow = True
    light = bpy.data.objects.new('Review_Key', sun); review.collection.objects.link(light)
    light.rotation_euler = Vector((300,280,-500)).to_track_quat('-Z','Y').to_euler()
    camera_data = bpy.data.cameras.new('Review_Camera')
    camera = bpy.data.objects.new('Review_Camera', camera_data); review.collection.objects.link(camera)
    points = [o.matrix_world @ v.co for o in meshes for v in o.data.vertices]
    low = Vector([min(p[i] for p in points) for i in range(3)])
    high = Vector([max(p[i] for p in points) for i in range(3)])
    center = (low + high) / 2
    camera.location = center + Vector((-55,-65,42))
    camera.rotation_euler = (center-camera.location).to_track_quat('-Z','Y').to_euler()
    camera_data.type = 'ORTHO'; camera_data.ortho_scale = max(high-low)*1.45
    review.camera = camera
    review.render.resolution_x = 800; review.render.resolution_y = 800
    review.render.resolution_percentage = 100; review.render.film_transparent = True
    review.render.image_settings.file_format = 'PNG'
    review.render.filepath = str(OUT / 'rack-preview.png')
    bpy.context.window.scene = review
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / (ID+'.blend')))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(OUT / (ID+'.blend')))
    bpy.ops.render.render(write_still=True)
    # Export only a temporary, joined mesh; the saved master stays editable.
    bpy.context.window.scene = export
    for obj in bpy.context.selected_objects: obj.select_set(False)
    copies=[]
    for obj in meshes:
        mesh=obj.data.copy(); mesh.transform(obj.matrix_world)
        prepared=bpy.data.objects.new(obj.name+'_Prepared',mesh)
        export.collection.objects.link(prepared)
        prepared.select_set(True); copies.append(prepared)
    bpy.context.view_layer.objects.active=copies[0]
    bpy.ops.object.join()
    joined=copies[0]; joined.name=ID
    joined.vertex_groups.clear()
    joined.vertex_groups.new(name='Bone').add(list(range(len(joined.data.vertices))),1,'REPLACE')
    joined.modifiers.new('Static rig','ARMATURE').object=rig
    exporter=module('rack_cn6', ROOT/'project/tools/scripts/io_export_cn6_b4.py')
    cn6=OUT/(ID+'.cn6'); fgx=OUT/(ID+'.fgx'); geo=OUT/(ID+'.geo')
    exporter.csc_do_export_selected(str(cn6),[rig,joined])
    summaries,vertices,triangles=exporter.csc_write_geo(str(geo),ID,str(cn6),'LandmarkModel')
    geo.write_text(geo.read_text().replace('AssetObjects:','AssetObjects..'))
    run([LIBS/'CN6ToFGX.exe',cn6,fgx,2], 'convert')
    run([LIBS/'FGXToCN6.exe',fgx,OUT/(ID+'-roundtrip.cn6')], 'native-readback')
    # Reuse the existing TileBase schema and material/state values.
    ast=ET.parse(MOD/'Assets/CSC_TAILORS_Tailor_Dress_Form_2.ast').getroot()
    ast.find('m_Name').set('text',ID)
    ast.find('m_Description').set('text','Clothing rack with three hanging garments, extracted from Tailor revision 10.')
    models=ast.find('m_GeometrySet/m_ModelInstances')
    template=copy.deepcopy(models[0]); models.clear(); models.append(template)
    template.find('m_Name').set('text',ID); template.find('m_GeoName').set('text',ID)
    states=template.find('m_GroupStates')
    templates={e.find('m_StateName').get('text'):copy.deepcopy(e) for e in states}
    states.clear()
    for mesh in ET.parse(geo).findall('m_Meshes/Element'):
        for group in mesh.findall('m_Groups/Element'):
            for state in ('Worked','Unworked','Pillaged','Construction','Unbuilt'):
                row=copy.deepcopy(templates[state]); states.append(row)
                row.find('m_MeshName').set('text',mesh.find('m_Name').get('text'))
                row.find('m_GroupName').set('text',group.find('m_Name').get('text'))
                for value in row.findall('m_Values/m_Values/Element'):
                    param=value.find('m_ParamName').get('text')
                    if param=='Material':value.find('m_ObjectName').set('text','CSC_ALL_Props_01')
                    if param=='Visible':value.find('m_bValue').text=str(state in ('Worked','Unworked')).lower()
    for value in ast.findall('m_CookParams/m_Values/Element'):
        if value.find('m_ParamName').get('text')=='CullingMode':value.find('m_Value').set('text','PERMANENT')
    ET.indent(ast,space='  ')
    ET.ElementTree(ast).write(OUT/(ID+'.ast'),encoding='utf-8',xml_declaration=True)
    assert sha(SOURCE)==source_hash
    report=dict(asset_id=ID,source=str(SOURCE),source_sha256=source_hash,
                source_unchanged=True,source_components=list(before),source_matrices=source_matrices,
                source_pivot=list(pivot),component_position_error=parity,
                editable_vertices=sum(len(o.data.vertices) for o in meshes),
                exported_vertices=vertices,triangles=triangles,dimensions=list(high-low),
                material='CSC_ALL_Props_01',installed=False)
    (OUT/'extraction-report.json').write_text(json.dumps(report,indent=2))
    print('RACK_EXPORT='+json.dumps(report))

if __name__=='__main__':main()
