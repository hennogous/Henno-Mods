"""Publish saved garment-rack edits without replacing its AE asset definition."""
import bpy
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[3]
MOD=ROOT/'Civ Supply Chains'
ID='CSC_TAILORS_Tailor_Garment_Rack'
SOURCE=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Props\Tailors')/(ID+'.blend')
OUT=Path(r'C:\Users\Shadow\Desktop\Codex\Tailor-wall-garment-rack-20261013\black-r023')
ATLAS=Path(r'C:\Users\Shadow\Desktop\Working Files\3D Art\Textures\CSC_Props\Current\textures')
LIBS=ROOT/'project/tools/cn6libs'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,p):
    spec=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def snapshot(meshes):
    return {o.name:dict(matrix=[list(r) for r in o.matrix_world],vertices=[list(v.co) for v in o.data.vertices],
        polygons=[list(p.vertices) for p in o.data.polygons],uvs=[[list(d.uv) for d in u.data] for u in o.data.uv_layers]) for o in meshes}
def run(args,label):
    r=subprocess.run([str(a) for a in args],cwd=LIBS,capture_output=True,text=True,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    (OUT/(label+'.log')).write_text(r.stdout+r.stderr);assert r.returncode==0,r.stdout+r.stderr
def parse(p):
    name,body=p.read_text().split('mesh:"')[1].split('"',1)
    _,body=body.split('vertices\n');v,body=body.split('triangles\n')
    return name,[[float(x) for x in l.split()[:18]] for l in v.strip().splitlines()],body.split('\nend')[0].strip()

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    backup=OUT/'before-update';backup.mkdir(exist_ok=True)
    assert not (OUT/'update-report.json').exists(),'Already published; inspect before rerunning'
    if not (backup/SOURCE.name).exists():shutil.copy2(SOURCE,backup/SOURCE.name)
    protected={p:sha(p) for folder in ('Assets','Materials','Textures','XLPs','ArtDefs') for p in (MOD/folder).rglob('*') if p.is_file()}
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
    meshes=sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:o.name)
    assert len(meshes)==25
    before=snapshot(meshes)
    for obj in meshes:
        obj.vertex_groups.clear()
        obj.vertex_groups.new(name='Bone').add(list(range(len(obj.data.vertices))),1,'REPLACE')
    changes=[]
    for mat in {m for o in meshes for m in o.data.materials}:
        for node in mat.node_tree.nodes:
            if node.type!='TEX_IMAGE' or not node.image:continue
            im=node.image;filename=Path(bpy.path.abspath(im.filepath)).name
            if filename.startswith('CSC_Props_Shared_01_'):
                target=ATLAS/filename;assert target.is_file(),target
                changes.append(dict(image=im.name,before=im.filepath,after=str(target)))
                im.filepath=str(target);im.reload()
    assert before==snapshot(meshes)
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE))
    # Validate the saved artifact, after flushing the edit-mode UV changes.
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE),load_ui=False,use_scripts=False)
    validator=module('rack_validation',ROOT/'project/tools/blender/csc_scene_validation.py')
    validation=validator.validate_current_scene()
    (OUT/'saved-validation.json').write_text(json.dumps(validation,indent=2))
    assert validation['automated_pass'],validation['findings']
    meshes=sorted([o for o in bpy.data.objects if o.type=='MESH'],key=lambda o:o.name)
    assert before==snapshot(meshes),'Geometry, transforms or UVs changed'
    review=bpy.data.scenes['Review'];bpy.context.window.scene=review
    review.render.filepath=str(OUT/'black-rack-preview.png')
    bpy.ops.render.render(write_still=True)
    export=bpy.data.scenes['Export'];bpy.context.window.scene=export
    for o in bpy.context.selected_objects:o.select_set(False)
    copies=[]
    for o in meshes:
        data=o.data.copy();data.transform(o.matrix_world)
        obj=bpy.data.objects.new(o.name+'_Prepared',data);export.collection.objects.link(obj)
        obj.select_set(True);copies.append(obj)
    bpy.context.view_layer.objects.active=copies[0];bpy.ops.object.join()
    joined=copies[0];joined.name=ID
    rig=next(o for o in export.objects if o.type=='ARMATURE')
    joined.vertex_groups.clear();joined.vertex_groups.new(name='Bone').add(list(range(len(joined.data.vertices))),1,'REPLACE')
    joined.modifiers.new('Static rig','ARMATURE').object=rig
    exporter=module('rack_export',ROOT/'project/tools/scripts/io_export_cn6_b4.py')
    cn6=OUT/(ID+'.cn6');fgx=OUT/(ID+'.fgx');geo=OUT/(ID+'.geo')
    exporter.csc_do_export_selected(str(cn6),[rig,joined])
    _,vertices,triangles=exporter.csc_write_geo(str(geo),ID,str(cn6),'LandmarkModel')
    geo.write_text(geo.read_text().replace('AssetObjects:','AssetObjects..'))
    run([LIBS/'CN6ToFGX.exe',cn6,fgx,2],'convert')
    readback=OUT/(ID+'-roundtrip.cn6');run([LIBS/'FGXToCN6.exe',fgx,readback],'native-readback')
    a,va,ta=parse(cn6);b,vb,tb=parse(readback)
    assert a==b==ID and len(va)==len(vb)==312 and ta==tb
    errors=[max(abs(x[i]-y[i]) for x,y in zip(va,vb)) for i in range(18)]
    assert max(errors)<1e-4,errors
    # Native geometry must keep all AST mesh/group bindings valid.
    ast=ET.parse(MOD/'Assets'/(ID+'.ast'))
    groups={(m.find('m_Name').get('text'),g.find('m_Name').get('text')) for m in ET.parse(geo).findall('m_Meshes/Element') for g in m.findall('m_Groups/Element')}
    assert all((r.find('m_MeshName').get('text'),r.find('m_GroupName').get('text')) in groups for r in ast.findall('.//m_GroupStates/Element'))
    for staged in (fgx,geo):
        dest=MOD/'Geometries'/staged.name;shutil.copy2(dest,backup/dest.name);shutil.copy2(staged,dest)
        assert sha(staged)==sha(dest)
    assert all(sha(p)==h for p,h in protected.items())
    report=dict(source=str(SOURCE),source_sha256=sha(SOURCE),image_links=changes,
        saved_uvs_geometry_transforms_preserved=True,exported_vertices=vertices,triangles=triangles,
        native_readback_max_error=max(errors),installed=True,ae_asset_material_texture_placements_preserved=True)
    (OUT/'update-report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
