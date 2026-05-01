import bpy

old_name = "CSC:Storage_L"
new_name = "Bone"

# Rename bone in armature
for arm in bpy.data.armatures:
    for bone in arm.bones:
        if bone.name == old_name:
            bone.name = new_name
            print(f"Renamed armature bone: {old_name} -> {new_name}")

# Rename vertex group on mesh to match
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for vg in obj.vertex_groups:
            if vg.name == old_name:
                vg.name = new_name
                print(f"Renamed vertex group on {obj.name}: {old_name} -> {new_name}")

bpy.ops.wm.save_mainfile()
print("Saved.")
