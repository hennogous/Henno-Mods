"""
Inspect the blend file - list objects, their locations and bounds.
Run with: blender --background file.blend --python blend_inspect.py
"""
import bpy, json

scene = bpy.context.scene
objects = []

for obj in scene.objects:
    if obj.type == 'MESH':
        # Get world bounding box
        bb = [obj.matrix_world @ v for v in [bpy.data.objects[obj.name].matrix_world.inverted() @ obj.matrix_world @ v.co for v in obj.data.vertices[:1]]] if obj.data.vertices else []
        objects.append({
            "name": obj.name,
            "type": obj.type,
            "location": list(obj.location),
            "dimensions": list(obj.dimensions),
            "visible": not obj.hide_viewport
        })

# Also list cameras
cameras = [{"name": o.name, "location": list(o.location), "rotation": list(o.rotation_euler)} 
           for o in scene.objects if o.type == 'CAMERA']

result = {
    "objects": objects[:30],
    "cameras": cameras,
    "scene_unit_scale": scene.unit_settings.scale_length,
    "render_resolution": [scene.render.resolution_x, scene.render.resolution_y],
}
print("BLEND_INFO:" + json.dumps(result, indent=2))
