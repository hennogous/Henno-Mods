"""
Civ 6 Building Geometry Inspector
Parses CN6 files directly and imports into Blender for analysis.
Run with: blender --background --python inspect_building_mesh.py

Outputs a JSON report per building with vertex-level mesh analysis.
"""

import bpy
import bmesh
import json
import os
import sys
import math
from pathlib import Path
from collections import defaultdict
from mathutils import Vector

SAMPLE_DIR = r"C:\Users\Shadow\.openclaw\workspace\csc\docs\sample-geometries"
OUTPUT_FILE = r"C:\Users\Shadow\.openclaw\workspace\csc\docs\building-mesh-analysis.json"


def parse_cn6(filepath):
    """Parse a CN6 text file into structured mesh data."""
    meshes = []
    skeleton = []
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Parse skeleton
        if line == 'skeleton':
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('meshes:'):
                parts = lines[i].strip().split()
                if len(parts) >= 24:
                    bone_idx = int(parts[0])
                    bone_name = parts[1].strip('"')
                    parent_idx = int(parts[2])
                    # Position: parts[3:6], quaternion: parts[6:10]
                    pos = [float(parts[3]), float(parts[4]), float(parts[5])]
                    quat = [float(parts[6]), float(parts[7]), float(parts[8]), float(parts[9])]
                    # Transform matrix: parts[10:23]
                    skeleton.append({
                        'index': bone_idx,
                        'name': bone_name,
                        'parent': parent_idx,
                        'position': pos,
                        'quaternion': quat
                    })
                i += 1
            continue
        
        # Parse mesh
        if line.startswith('mesh:'):
            mesh_name = line.split(':')[1].strip('"')
            mesh_data = {'name': mesh_name, 'vertices': [], 'triangles': [], 'materials': []}
            i += 1
            
            # Skip materials line
            if i < len(lines) and lines[i].strip() == 'materials':
                i += 1
            
            # Parse vertices
            if i < len(lines) and lines[i].strip() == 'vertices':
                i += 1
                while i < len(lines):
                    vline = lines[i].strip()
                    if vline in ('triangles', 'mesh:', 'end') or vline.startswith('mesh:'):
                        break
                    parts = vline.split()
                    if len(parts) >= 18:
                        vert = {
                            'pos': [float(parts[0]), float(parts[1]), float(parts[2])],
                            'normal': [float(parts[3]), float(parts[4]), float(parts[5])],
                            'tangent': [float(parts[6]), float(parts[7]), float(parts[8])],
                            'bitangent': [float(parts[9]), float(parts[10]), float(parts[11])],
                            'uv1': [float(parts[12]), float(parts[13])],
                            'uv2': [float(parts[14]), float(parts[15])],
                            'uv3': [float(parts[16]), float(parts[17])],
                        }
                        # Bone weights/indices if present
                        if len(parts) >= 26:
                            vert['bone_weights'] = [float(parts[18]), float(parts[19]), float(parts[20]), float(parts[21])]
                            vert['bone_indices'] = [int(parts[22]), int(parts[23]), int(parts[24]), int(parts[25])]
                        # Vertex colors if present
                        if len(parts) >= 30:
                            vert['color1'] = [int(parts[26]), int(parts[27]), int(parts[28]), int(parts[29])]
                        if len(parts) >= 34:
                            vert['color2'] = [int(parts[30]), int(parts[31]), int(parts[32]), int(parts[33])]
                        mesh_data['vertices'].append(vert)
                    i += 1
            
            # Parse triangles
            if i < len(lines) and lines[i].strip() == 'triangles':
                i += 1
                while i < len(lines):
                    tline = lines[i].strip()
                    if tline in ('end', '') or tline.startswith('mesh:'):
                        break
                    parts = tline.split()
                    if len(parts) >= 3:
                        tri = [int(parts[0]), int(parts[1]), int(parts[2])]
                        mat_idx = int(parts[3]) if len(parts) > 3 else 0
                        mesh_data['triangles'].append({'indices': tri, 'material': mat_idx})
                    i += 1
            
            meshes.append(mesh_data)
            continue
        
        i += 1
    
    return {'skeleton': skeleton, 'meshes': meshes}


def create_blender_mesh(cn6_data, asset_name):
    """Create Blender mesh objects from parsed CN6 data and analyze."""
    results = {
        'asset_name': asset_name,
        'meshes': [],
        'skeleton': {
            'bone_count': len(cn6_data['skeleton']),
            'bones': [b['name'] for b in cn6_data['skeleton']],
            'hierarchy_depth': 0
        },
        'totals': {
            'total_vertices': 0,
            'total_triangles': 0,
            'total_edges': 0,
        }
    }
    
    # Calculate skeleton hierarchy depth
    if cn6_data['skeleton']:
        depths = {}
        for bone in cn6_data['skeleton']:
            depth = 0
            parent = bone['parent']
            visited = set()
            while parent >= 0 and parent not in visited:
                depth += 1
                visited.add(parent)
                parent_bone = next((b for b in cn6_data['skeleton'] if b['index'] == parent), None)
                if parent_bone:
                    parent = parent_bone['parent']
                else:
                    break
            depths[bone['index']] = depth
        results['skeleton']['hierarchy_depth'] = max(depths.values()) if depths else 0
    
    for mesh_data in cn6_data['meshes']:
        verts = mesh_data['vertices']
        tris = mesh_data['triangles']
        
        if not verts or not tris:
            continue
        
        # Create Blender mesh
        mesh = bpy.data.meshes.new(mesh_data['name'])
        obj = bpy.data.objects.new(mesh_data['name'], mesh)
        bpy.context.collection.objects.link(obj)
        
        # Set vertices and faces
        positions = [v['pos'] for v in verts]
        faces = [t['indices'] for t in tris]
        
        mesh.from_pydata(positions, [], faces)
        mesh.update()
        
        # Create BMesh for analysis
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bm.edges.ensure_lookup_table()
        bm.verts.ensure_lookup_table()
        bm.faces.ensure_lookup_table()
        
        # === TOPOLOGY ANALYSIS ===
        vert_count = len(bm.verts)
        edge_count = len(bm.edges)
        face_count = len(bm.faces)
        
        # Valence distribution (faces per vertex)
        valences = [len(v.link_faces) for v in bm.verts]
        avg_valence = sum(valences) / len(valences) if valences else 0
        valence_dist = defaultdict(int)
        for v in valences:
            valence_dist[v] += 1
        
        # Boundary edges (edges with only 1 face = mesh boundary)
        boundary_edges = sum(1 for e in bm.edges if len(e.link_faces) == 1)
        
        # Non-manifold edges (edges with 0 or >2 faces)
        non_manifold_edges = sum(1 for e in bm.edges if len(e.link_faces) != 2)
        
        # Loose vertices (not connected to any face)
        loose_verts = sum(1 for v in bm.verts if len(v.link_faces) == 0)
        
        # === CONNECTIVITY (mesh islands) ===
        visited = set()
        islands = 0
        island_sizes = []
        for v in bm.verts:
            if v.index not in visited:
                islands += 1
                # BFS to find connected component
                queue = [v]
                island_verts = 0
                while queue:
                    current = queue.pop()
                    if current.index in visited:
                        continue
                    visited.add(current.index)
                    island_verts += 1
                    for e in current.link_edges:
                        other = e.other_vert(current)
                        if other.index not in visited:
                            queue.append(other)
                island_sizes.append(island_verts)
        
        # === BOUNDING BOX ===
        xs = [v.co.x for v in bm.verts]
        ys = [v.co.y for v in bm.verts]
        zs = [v.co.z for v in bm.verts]
        
        bbox = {
            'min': [min(xs), min(ys), min(zs)],
            'max': [max(xs), max(ys), max(zs)],
            'size': [max(xs) - min(xs), max(ys) - min(ys), max(zs) - min(zs)],
            'center': [(max(xs) + min(xs)) / 2, (max(ys) + min(ys)) / 2, (max(zs) + min(zs)) / 2]
        }
        
        # Surface area estimation
        total_area = sum(f.calc_area() for f in bm.faces)
        
        # === UV ANALYSIS ===
        uv_analysis = analyze_uvs(verts, tris)
        
        # === EDGE LENGTH ANALYSIS ===
        edge_lengths = [e.calc_length() for e in bm.edges]
        avg_edge_len = sum(edge_lengths) / len(edge_lengths) if edge_lengths else 0
        min_edge_len = min(edge_lengths) if edge_lengths else 0
        max_edge_len = max(edge_lengths) if edge_lengths else 0
        
        # === NORMAL ANALYSIS ===
        # Check if normals are smooth or flat
        face_normals = [tuple(round(c, 4) for c in f.normal) for f in bm.faces]
        unique_normals = len(set(face_normals))
        
        # Check for custom normals from CN6 data
        has_custom_normals = True  # CN6 always has per-vertex normals
        
        # === MATERIAL ANALYSIS ===
        material_groups = defaultdict(int)
        for tri in tris:
            material_groups[tri['material']] += 1
        
        # === BONE WEIGHT ANALYSIS ===
        bone_usage = defaultdict(int)
        single_bone_verts = 0
        multi_bone_verts = 0
        for v in verts:
            if 'bone_weights' in v:
                active_bones = sum(1 for w in v['bone_weights'] if w > 0.01)
                if active_bones <= 1:
                    single_bone_verts += 1
                else:
                    multi_bone_verts += 1
                for idx, w in zip(v.get('bone_indices', []), v.get('bone_weights', [])):
                    if w > 0.01:
                        bone_usage[idx] += 1
        
        mesh_result = {
            'name': mesh_data['name'],
            'topology': {
                'vertices': vert_count,
                'edges': edge_count,
                'faces': face_count,
                'triangles': len(tris),
                'quads': 0,  # CN6 is always triangulated
                'avg_valence': round(avg_valence, 2),
                'valence_distribution': dict(sorted(valence_dist.items())),
                'boundary_edges': boundary_edges,
                'non_manifold_edges': non_manifold_edges,
                'loose_vertices': loose_verts,
            },
            'connectivity': {
                'island_count': islands,
                'island_sizes': sorted(island_sizes, reverse=True),
                'is_single_mesh': islands == 1,
            },
            'dimensions': {
                'bounding_box': bbox,
                'surface_area': round(total_area, 2),
                'verts_per_unit_area': round(vert_count / total_area, 4) if total_area > 0 else 0,
            },
            'edges': {
                'avg_length': round(avg_edge_len, 4),
                'min_length': round(min_edge_len, 4),
                'max_length': round(max_edge_len, 4),
            },
            'normals': {
                'unique_face_normals': unique_normals,
                'has_custom_normals': has_custom_normals,
                'is_mostly_hard_edge': unique_normals > face_count * 0.5,
            },
            'materials': {
                'slot_count': len(material_groups),
                'faces_per_material': dict(material_groups),
            },
            'bone_weights': {
                'single_bone_verts': single_bone_verts,
                'multi_bone_verts': multi_bone_verts,
                'bones_used': len(bone_usage),
                'bone_usage': {str(k): v for k, v in sorted(bone_usage.items())},
            },
            'uv': uv_analysis,
        }
        
        results['meshes'].append(mesh_result)
        results['totals']['total_vertices'] += vert_count
        results['totals']['total_triangles'] += len(tris)
        results['totals']['total_edges'] += edge_count
        
        bm.free()
    
    return results


def analyze_uvs(verts, tris):
    """Analyze UV mapping patterns."""
    uv_channels = {}
    
    for ch_idx, ch_name in enumerate(['uv1', 'uv2', 'uv3']):
        uvs = [v[ch_name] for v in verts if ch_name in v]
        if not uvs:
            continue
        
        us = [uv[0] for uv in uvs]
        vs = [uv[1] for uv in uvs]
        
        # Check if UV channel is actually used (not all zeros or tiny)
        u_range = max(us) - min(us)
        v_range = max(vs) - min(vs)
        
        if u_range < 0.0001 and v_range < 0.0001:
            # UV channel not really used
            uv_channels[ch_name] = {'used': False}
            continue
        
        # UV space bounds
        u_min, u_max = min(us), max(us)
        v_min, v_max = min(vs), max(vs)
        
        # Check for UVs outside 0-1 (tiled/wrapped)
        outside_01 = sum(1 for u, v in uvs if u < 0 or u > 1 or v < 0 or v > 1)
        
        # Estimate UV space utilization
        # Quantize to grid and count occupied cells
        grid_size = 64
        occupied = set()
        for u, v in uvs:
            gu = int(min(max(u, 0), 0.999) * grid_size)
            gv = int(min(max(v, 0), 0.999) * grid_size)
            occupied.add((gu, gv))
        utilization = len(occupied) / (grid_size * grid_size)
        
        # Check for overlapping UVs (same UV position, different vertex)
        uv_set = set()
        overlaps = 0
        for u, v in uvs:
            key = (round(u, 6), round(v, 6))
            if key in uv_set:
                overlaps += 1
            uv_set.add(key)
        
        # UV island detection via triangle adjacency in UV space
        # (simplified — count connected components in UV)
        uv_islands = estimate_uv_islands(verts, tris, ch_name)
        
        uv_channels[ch_name] = {
            'used': True,
            'bounds': {
                'u_range': [round(u_min, 4), round(u_max, 4)],
                'v_range': [round(v_min, 4), round(v_max, 4)],
            },
            'outside_01_count': outside_01,
            'outside_01_pct': round(outside_01 / len(uvs) * 100, 1),
            'space_utilization_pct': round(utilization * 100, 1),
            'overlap_count': overlaps,
            'unique_uv_positions': len(uv_set),
            'estimated_islands': uv_islands,
        }
    
    return uv_channels


def estimate_uv_islands(verts, tris, uv_channel):
    """Estimate UV island count by checking UV discontinuities at shared edges."""
    # Build edge -> triangle adjacency
    edge_tris = defaultdict(list)
    for tri_idx, tri in enumerate(tris):
        indices = tri['indices']
        for j in range(3):
            e = tuple(sorted([indices[j], indices[(j + 1) % 3]]))
            edge_tris[e].append(tri_idx)
    
    # Two triangles sharing an edge are in the same UV island only if their
    # shared vertices have the same UV coords
    visited = set()
    islands = 0
    
    for tri_idx in range(len(tris)):
        if tri_idx in visited:
            continue
        islands += 1
        queue = [tri_idx]
        while queue:
            current = queue.pop()
            if current in visited:
                continue
            visited.add(current)
            
            indices = tris[current]['indices']
            for j in range(3):
                e = tuple(sorted([indices[j], indices[(j + 1) % 3]]))
                for neighbor in edge_tris[e]:
                    if neighbor not in visited:
                        # Check UV continuity
                        v1_idx = indices[j]
                        v2_idx = indices[(j + 1) % 3]
                        n_indices = tris[neighbor]['indices']
                        
                        # Find matching verts in neighbor
                        uv_match = True
                        for vi in [v1_idx, v2_idx]:
                            if vi in n_indices:
                                # Same vertex index = same UV (in CN6 format verts are split at UV seams)
                                pass
                            else:
                                uv_match = False
                        
                        if uv_match:
                            queue.append(neighbor)
    
    return islands


def main():
    # Clear scene
    bpy.ops.wm.read_factory_settings(use_empty=True)
    
    all_results = {}
    cn6_files = sorted(Path(SAMPLE_DIR).glob('*.cn6'))
    
    print(f"\n{'='*80}")
    print(f"Civ 6 Building Geometry Inspector")
    print(f"Processing {len(cn6_files)} CN6 files from {SAMPLE_DIR}")
    print(f"{'='*80}\n")
    
    for cn6_file in cn6_files:
        asset_name = cn6_file.stem
        print(f"\n--- Processing: {asset_name} ---")
        
        # Clear scene between files
        bpy.ops.wm.read_factory_settings(use_empty=True)
        
        try:
            cn6_data = parse_cn6(str(cn6_file))
            print(f"  Parsed: {len(cn6_data['skeleton'])} bones, {len(cn6_data['meshes'])} meshes")
            
            if cn6_data['meshes']:
                result = create_blender_mesh(cn6_data, asset_name)
                all_results[asset_name] = result
                
                # Print summary
                print(f"  Total verts: {result['totals']['total_vertices']}")
                print(f"  Total tris:  {result['totals']['total_triangles']}")
                print(f"  Meshes: {len(result['meshes'])}")
                for m in result['meshes']:
                    print(f"    {m['name']}: {m['topology']['vertices']}v {m['topology']['faces']}f "
                          f"| {m['connectivity']['island_count']} islands "
                          f"| bbox {[round(s,1) for s in m['dimensions']['bounding_box']['size']]}")
            else:
                print(f"  SKELETON ONLY (no mesh data)")
                all_results[asset_name] = {
                    'asset_name': asset_name,
                    'skeleton_only': True,
                    'skeleton': {
                        'bone_count': len(cn6_data['skeleton']),
                        'bones': [b['name'] for b in cn6_data['skeleton']],
                    }
                }
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
            all_results[asset_name] = {'asset_name': asset_name, 'error': str(e)}
    
    # Write results
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Results written to: {OUTPUT_FILE}")
    print(f"Processed {len(all_results)} assets")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
