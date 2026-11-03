import bpy,sys
bpy.ops.wm.open_mainfile(filepath=sys.argv[sys.argv.index('--')+1])
m=bpy.data.materials['CSC_BAKERS_Wind_Mill_Modern']
for n in m.node_tree.nodes:
 print(n.name,n.type,getattr(n,'uv_map',''),n.image.filepath if n.type=='TEX_IMAGE' and n.image else '')
for l in m.node_tree.links:print(l.from_node.name,l.from_socket.name,'->',l.to_node.name,l.to_socket.name)
o=bpy.data.objects['CSC_Fixed_Main_Roof']
for uv in o.data.uv_layers:print(uv.name,uv.active_render,[list(v.uv) for v in uv.data][:8])
