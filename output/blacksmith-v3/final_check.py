import bpy,os,json,importlib.util
ROOT='/Users/henno.gous/Play/Henno-Mods';OUT=ROOT+'/output/blacksmith-v3'
sc=bpy.data.scenes['CSC_BLACKSMITH_Workshop_v3'];bpy.context.window.scene=sc
obj=next(o for o in sc.objects if o.type=='MESH' and o.name.endswith('_Bldg'));me=obj.data
# Correct a small UV issue revealed by the render: endgrain belongs on the top
# of the broad stump, while its vertical sides use lengthwise oak grain.
fixed=0
for poly in me.polygons:
    p=poly.center/30
    if .50<p.x<1.34 and -1.76<p.y<-.92 and 0<p.z<.64 and abs(poly.normal.z)<.7:
        uv=me.uv_layers['UV1'].data[poly.loop_start].uv
        if .63<uv.x<.744 and .19<uv.y<.31:
            horizontal=1 if abs(poly.normal.x)>abs(poly.normal.y) else 0
            coords=[me.vertices[me.loops[li].vertex_index].co/30 for li in poly.loop_indices]
            lo=min(p[horizontal] for p in coords)
            for li,p in zip(poly.loop_indices,coords):
                mapped=(.012+.476*(.08+(p[horizontal]-lo)*.22),1-(.51+.475*(.025+p.z*.27)))
                me.uv_layers['UV1'].data[li].uv=mapped;me.uv_layers['UV3'].data[li].uv=mapped
            fixed+=1
maps=[]
for node in me.materials[0].node_tree.nodes:
    if node.type=='TEX_IMAGE':
        path=bpy.path.abspath(node.image.filepath)
        assert os.path.isfile(path),path
        assert not node.image.packed_file,path
        assert tuple(node.image.size)==(1024,1024),(path,tuple(node.image.size))
        maps.append(path)
assert len(me.uv_layers)==3
assert len(me.materials)==1
spec=importlib.util.spec_from_file_location('cn6_export',ROOT+'/project/tools/scripts/io_export_cn6_b4.py');ex=importlib.util.module_from_spec(spec);spec.loader.exec_module(ex)
bpy.ops.object.select_all(action='DESELECT');obj.select_set(True);obj.parent.select_set(True);bpy.context.view_layer.objects.active=obj
ex.do_export(OUT+'/CSC_BLACKSMITH_Workshop_v3.cn6',True,True)
lines=open(OUT+'/CSC_BLACKSMITH_Workshop_v3.cn6').read().splitlines();v=lines.index('triangles')-lines.index('vertices')-1;t=lines.index('end')-lines.index('triangles')-1
assert v==1491 and t==781,(v,t)
json.dump({'external_maps_verified':maps,'cn6_vertices':v,'cn6_triangles':t,'material_count':1,'uv_layers':[u.name for u in me.uv_layers],'stump_side_faces_corrected':fixed},open(OUT+'/validation.json','w'),indent=2)
sc.render.resolution_x=sc.render.resolution_y=1200;sc.cycles.samples=64;sc.render.filepath=OUT+'/blacksmith-render-v3.png'
bpy.ops.wm.save_as_mainfile(filepath=OUT+'/CSC_BLACKSMITH_Workshop_v3.blend',relative_remap=False)
bpy.ops.render.render(write_still=True)
sc.render.resolution_x=sc.render.resolution_y=256;sc.render.filepath=OUT+'/blacksmith-thumbnail-v3.png'
bpy.ops.render.render(write_still=True)
print('FINAL VERIFIED',v,t,'maps',len(maps),'stump faces',fixed,flush=True)
