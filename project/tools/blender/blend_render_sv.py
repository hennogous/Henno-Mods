"""
Sets up an isometric orthographic camera and renders the scene
as a transparent PNG suitable for ControlNet canny edge input.

Run with:
  blender --background file.blend --python blend_render_sv.py

Output: C:/Users/Shadow/.openclaw/workspace/sv_render_output/sv_render.png
"""
import bpy
import math
import os

OUTPUT_PATH = "C:/Users/Shadow/.openclaw/workspace/sv_render_output/sv_render.png"
RENDER_SIZE = 512  # higher res for better canny edges

os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

scene = bpy.context.scene

# --- Find the mesh and get its center + dimensions ---
mesh_obj = None
for obj in scene.objects:
    if obj.type == 'MESH' and obj.visible_get():
        mesh_obj = obj
        break

if not mesh_obj:
    print("ERROR: No visible mesh found")
    raise SystemExit(1)

loc = mesh_obj.location
dims = mesh_obj.dimensions
print(f"Mesh: {mesh_obj.name}, location={list(loc)}, dims={list(dims)}")

# Center of mesh in world space
cx = loc.x
cy = loc.y
cz = loc.z + dims.z * 0.5  # vertical center

# --- Remove existing cameras ---
for obj in list(scene.objects):
    if obj.type == 'CAMERA':
        bpy.data.objects.remove(obj, do_unlink=True)

# --- Create orthographic camera ---
cam_data = bpy.data.cameras.new("SV_Camera")
cam_data.type = 'ORTHO'

# Ortho scale: fit the largest dimension + 20% padding
max_dim = max(dims.x, dims.y) * 1.2
cam_data.ortho_scale = max_dim

cam_obj = bpy.data.objects.new("SV_Camera", cam_data)
scene.collection.objects.link(cam_obj)
scene.camera = cam_obj

# --- Position camera: isometric angle ---
# Civ 6 SV uses roughly 30deg elevation, 45deg rotation
# In Blender: rotation_euler = (X=60deg from top = 30deg elevation, Y=0, Z=45deg)
elevation_deg = 60   # from vertical (90 = side-on, 0 = top-down); 60 = 30deg elevation
azimuth_deg   = 45   # rotate around Z

elev_rad = math.radians(elevation_deg)
azim_rad = math.radians(azimuth_deg)

# Distance doesn't matter much for ortho, but needs to be far enough to not clip
dist = max(dims.x, dims.y, dims.z) * 3

import mathutils
cam_obj.rotation_euler = (elev_rad, 0, azim_rad)

# Position: above and offset from center
cam_obj.location = (
    cx + dist * math.sin(elev_rad) * math.sin(azim_rad),
    cy - dist * math.sin(elev_rad) * math.cos(azim_rad),
    cz + dist * math.cos(elev_rad)
)

print(f"Camera: location={[round(x,2) for x in cam_obj.location]}, rotation_euler={[round(math.degrees(x),1) for x in cam_obj.rotation_euler]}")
print(f"Ortho scale: {cam_data.ortho_scale:.2f}")

# --- Render settings ---
render = scene.render
render.resolution_x = RENDER_SIZE
render.resolution_y = RENDER_SIZE
render.resolution_percentage = 100
render.film_transparent = True   # transparent background
render.image_settings.file_format = 'PNG'
render.image_settings.color_mode = 'RGBA'
render.filepath = OUTPUT_PATH

# Use EEVEE for speed
scene.render.engine = 'BLENDER_EEVEE'

# Rotate building 90° anti-clockwise (viewed from top = +90° around Z)
import mathutils
for obj in scene.objects:
    if obj.type == 'MESH':
        obj.rotation_euler[2] += math.radians(90)
        print(f"  Rotated {obj.name} 90° CCW")

# Hide Foundation vertex group
for obj in scene.objects:
    if obj.type == 'MESH' and 'Foundation' in obj.vertex_groups:
        mask = obj.modifiers.new(name="HideFoundation", type='MASK')
        mask.vertex_group = 'Foundation'
        mask.invert_vertex_group = True
        print(f"  Masked Foundation on {obj.name}")
    elif obj.type == 'MESH':
        vgs = [vg.name for vg in obj.vertex_groups]
        print(f"  {obj.name} vertex groups: {vgs}")

# Boost lighting — add strong sun lights without touching materials
for obj in list(scene.objects):
    if obj.type == 'LIGHT':
        bpy.data.objects.remove(obj, do_unlink=True)

for name, energy, rx, rz in [
    ("Key",  5.0, 45, 45),
    ("Fill", 3.0, 70, 180),
    ("Rim",  2.0, 30, -90),
]:
    ld = bpy.data.lights.new(name, type='SUN')
    ld.energy = energy
    lo = bpy.data.objects.new(name, ld)
    scene.collection.objects.link(lo)
    lo.rotation_euler = (math.radians(rx), 0, math.radians(rz))

print(f"Rendering to {OUTPUT_PATH}...")
bpy.ops.render.render(write_still=True)
print("Done!")
