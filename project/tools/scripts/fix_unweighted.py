import bpy

obj = [o for o in bpy.data.objects if o.type == 'MESH'][0]
mesh = obj.data
vg = obj.vertex_groups.get("Bone")

if not vg:
    print("ERROR: No 'Bone' vertex group found")
else:
    fixed = 0
    for v in mesh.vertices:
        if len(v.groups) == 0:
            vg.add([v.index], 1.0, 'ADD')
            fixed += 1
    print(f"Assigned {fixed} unweighted vertices to 'Bone' group (weight 1.0)")

bpy.ops.wm.save_mainfile()
print("Saved.")
