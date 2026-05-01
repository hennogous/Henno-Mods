"""Extract mesh-to-material mappings from CN6 files."""

def get_mesh_materials(filepath):
    current_mesh = None
    section = None
    mesh_materials = {}
    
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('mesh:"'):
                current_mesh = line.split('"')[1]
                mesh_materials[current_mesh] = []
                section = None
            elif line == 'materials':
                section = 'mats'
            elif line in ('end',) or line.startswith(('mesh:', 'skeleton', 'meshes:')):
                if line.startswith('mesh:'):
                    current_mesh = line.split('"')[1]
                    mesh_materials[current_mesh] = []
                section = None
            elif section == 'mats' and current_mesh and line.startswith('"'):
                mat_name = line.strip('"')
                mesh_materials[current_mesh].append(mat_name)
    
    return mesh_materials

import os
base = r"C:\Users\Shadow\.openclaw\workspace\test_pipeline"

print("=== DIS_PRD (IZ base) ===")
for mesh, mats in get_mesh_materials(os.path.join(base, "DIS_PRD_Classical_Base_01_Decals.cn6")).items():
    if any(k in mesh for k in ['Elbow006', 'Elbow011', 'FadeOut001', 'FadeOut005', 'Organic_Patch_Sm_A001', 'Organic_Patch_C032']):
        print(f"  {mesh}: {mats}")

print()
print("=== DIS_COM (ComHub base) ===")
for mesh, mats in get_mesh_materials(os.path.join(base, "DIS_COM_Classical_Base_Decal_01.cn6")).items():
    if any(k in mesh for k in ['Object302', 'Object304']):
        print(f"  {mesh}: {mats}")

print()
print("=== ALL unique materials ===")
all_mats = set()
for f in ["DIS_PRD_Classical_Base_01_Decals.cn6", "DIS_COM_Classical_Base_Decal_01.cn6"]:
    for mesh, mats in get_mesh_materials(os.path.join(base, f)).items():
        all_mats.update(mats)
for m in sorted(all_mats):
    print(f"  {m}")
