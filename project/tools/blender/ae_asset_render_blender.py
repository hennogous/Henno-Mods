"""Background Blender worker for render_ae_asset.py; not an authoring exporter."""
import hashlib
import json
import math
from pathlib import Path
import sys

import bpy
import bmesh
from mathutils import Euler, Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view


def bone_world(raw, name):
    bones = [bone for model in raw["models"] for bone in model["bones"] if bone["name"] == name]
    if len(bones) != 1:
        raise ValueError(f"Expected one bind bone {name}, found {len(bones)}")
    inv = bones[0]["inverseWorld"]
    return Matrix([inv[i:i + 4] for i in range(0, 16, 4)]).transposed().inverted()


def attachment_matrix(attachment):
    x, y, z = attachment["rotation"]
    return (Matrix.Translation(Vector(attachment["position"]) * 10.0)
            @ Euler((x, y, -z), "XYZ").to_matrix().to_4x4()
            @ Matrix.Scale(attachment["scale"], 4))


class Builder:
    def __init__(self, job, mode):
        self.job, self.mode = job, mode
        self.out = Path(job["output"])
        self.raw, self.images, self.materials = {}, {}, {}
        self.objects, self.mapping, self.warnings = [], [], list(job["warnings"])
        self.scene = bpy.context.scene
        self.scene.name = "AE_" + mode
        self.scene["placement_authority"] = "Saved AE AST; disposable render snapshot. Never export assembly back to AE."

    def geometry(self, key):
        if key not in self.raw:
            self.raw[key] = json.loads(Path(self.job["geometries"][key]["extracted"]).read_text())
        return self.raw[key]

    def image(self, texture, channel):
        source = texture.get("icon_override", texture["source"]) if self.mode == "icon" else texture["source"]
        color = "sRGB" if channel in ("BaseColor", "Emissive") else "Non-Color"
        key = (source, color)
        if key not in self.images:
            image = bpy.data.images.load(source, check_existing=False)
            image.colorspace_settings.name = color
            image.alpha_mode = "CHANNEL_PACKED"
            if not all(image.size) or not len(image.pixels):
                raise ValueError("DDS could not be decoded: " + source)
            # Preserve deterministic, portable PNG sources; the mod DDS stays untouched.
            name = hashlib.sha256((source + color).encode()).hexdigest()[:16] + ".png"
            target = self.out / "textures" / name
            target.parent.mkdir(exist_ok=True)
            decoded = bpy.data.images.new(texture["id"] + "_" + color, width=image.size[0], height=image.size[1], alpha=True)
            decoded.colorspace_settings.name = color
            decoded.alpha_mode = "CHANNEL_PACKED"
            decoded.pixels[:] = image.pixels[:]
            decoded.filepath_raw = str(target)
            decoded.file_format = "PNG"
            decoded.save()
            bpy.data.images.remove(image)
            decoded.filepath = str(target)
            decoded.pack()
            self.images[key] = decoded
        return self.images[key]

    def material(self, key, uvcount):
        cachekey = (key, uvcount)
        if cachekey in self.materials:
            return self.materials[cachekey]
        spec = self.job["materials"][key]
        mat = bpy.data.materials.new(spec["id"] + "_" + key + "_UV" + str(uvcount))
        mat.use_nodes = True
        mat["ae_material"] = spec["id"]
        bindings = {channel: texture for channel, texture in spec["textures"].items()
                    if channel not in ("Emissive", "EmissionMap", "EmissiveMap")}
        mat["effective_texture_bindings"] = json.dumps(bindings, sort_keys=True)
        mat["render_emission_enabled"] = False
        nodes, links = mat.node_tree.nodes, mat.node_tree.links
        bs = next(n for n in nodes if n.type == "BSDF_PRINCIPLED")
        bs.inputs["Roughness"].default_value = 0.7
        bs.inputs["Emission Strength"].default_value = 0
        bs.inputs["Emission Color"].default_value = (0, 0, 0, 1)
        textures = {}
        scalar = {}
        for channel, spec_texture in sorted(bindings.items()):
            uv = nodes.new("ShaderNodeUVMap")
            uvindex = 2 if channel == "AO" else 1
            uv.uv_map = "UV" + str(min(uvindex, uvcount))
            if uvindex > uvcount and channel == "AO":
                self.warnings.append(f"{spec['id']}: single-UV native AO preview uses UV1")
            image = nodes.new("ShaderNodeTexImage")
            image.label, image.name = channel, channel
            image.image = self.image(spec_texture, channel)
            links.new(uv.outputs["UV"], image.inputs["Vector"])
            textures[channel] = image
            if channel in ("AO", "Gloss", "Metalness", "Opacity"):
                split = nodes.new("ShaderNodeSeparateColor")
                split.mode = "RGB"
                links.new(image.outputs["Color"], split.inputs["Color"])
                scalar[channel] = split.outputs["Red"]
        if "BaseColor" in textures:
            color = textures["BaseColor"].outputs["Color"]
            if "AO" in textures:
                multiply = nodes.new("ShaderNodeMixRGB")
                multiply.blend_type = "MULTIPLY"
                multiply.inputs[0].default_value = 0.5
                links.new(color, multiply.inputs[1])
                links.new(scalar["AO"], multiply.inputs[2])
                color = multiply.outputs[0]
            links.new(color, bs.inputs["Base Color"])
        if "Normal" in textures:
            normal = nodes.new("ShaderNodeNormalMap")
            normal.uv_map = "UV1"
            links.new(textures["Normal"].outputs["Color"], normal.inputs["Color"])
            links.new(normal.outputs["Normal"], bs.inputs["Normal"])
        if "Gloss" in textures:
            inverse = nodes.new("ShaderNodeMath")
            inverse.operation = "SUBTRACT"
            inverse.inputs[0].default_value = 1
            links.new(scalar["Gloss"], inverse.inputs[1])
            links.new(inverse.outputs[0], bs.inputs["Roughness"])
        if "Metalness" in textures:
            links.new(scalar["Metalness"], bs.inputs["Metallic"])
        if "Opacity" in textures:
            links.new(scalar["Opacity"], bs.inputs["Alpha"])
        ignored = set(textures) - {"BaseColor", "AO", "Normal", "Gloss", "Metalness", "Opacity", "Emissive"}
        if ignored:
            self.warnings.append(f"{spec['id']}: retained but not simulated shader channels {sorted(ignored)}")
        self.materials[cachekey] = mat
        return mat

    def mesh(self, raw, group, transform, asset, path, model, root):
        selected = raw["triangles"][group["first"]:group["first"] + group["count"]]
        if len(selected) != group["count"]:
            raise ValueError(f"GEO triangle range exceeds FGX: {group}")
        indices = sorted({i for triangle in selected for i in triangle[:3]})
        remap = {old: new for new, old in enumerate(indices)}
        verts = [raw["vertices"][i] for i in indices]
        semantic = f"{path}/{model['id']}/{group['mesh']}/{group['group']}"
        name = group["mesh"][:35] + "_" + hashlib.sha256(semantic.encode()).hexdigest()[:12]
        mesh = bpy.data.meshes.new(name)
        mesh.from_pydata([v["position"] for v in verts], [], [[remap[i] for i in t[:3]] for t in selected])
        mesh.update()
        uvcount = sum(v["name"].startswith("TextureCoordinates") for v in raw["vertexStructInfos"])
        if not 1 <= uvcount <= 3:
            raise ValueError(f"Unsupported UV count {uvcount}: {group['mesh']}")
        for index, key in enumerate(("uv", "uv2", "uv3")[:uvcount], 1):
            uv = mesh.uv_layers.new(name="UV" + str(index))
            for loop in mesh.loops:
                u, v = verts[loop.vertex_index][key]
                uv.data[loop.index].uv = (u, 1 - v)
        mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))
        mesh.normals_split_custom_set([verts[loop.vertex_index]["normal"] for loop in mesh.loops])
        mesh.materials.append(self.material(group["material"], uvcount))
        obj = bpy.data.objects.new(name, mesh)
        self.scene.collection.objects.link(obj)
        obj.matrix_world = transform
        obj.pass_index = len(self.objects) + 1
        if obj.pass_index > 32767:
            raise ValueError("Too many objects for Blender IndexOB")
        obj["ae_semantic_path"] = semantic
        obj["ae_asset"] = asset["id"]
        obj["ae_group"] = group["group"]
        obj["render_snapshot_only"] = True
        self.objects.append(obj)
        self.mapping.append({"index": obj.pass_index, "object": obj.name, "semantic_path": semantic,
                             "asset": asset["id"], "model": model["id"], "group": group["group"],
                             "source_vertices": len(indices), "triangles": len(selected),
                             "matrix_world": [list(row) for row in transform], "root": root,
                             "material": self.job["materials"][group["material"]]["id"]})

    def assemble(self, key, transform=None, path=None, root=False):
        transform = transform if transform is not None else Matrix.Identity(4)
        asset = self.job["assets"][key]
        path = path or asset["id"]
        owners = {}
        for model in asset["models"]:
            owners[model["id"]] = model
            if model["geometry"] is None:
                continue
            raw = self.geometry(model["geometry"])
            meshes = {m["name"]: m for m in raw["meshes"]}
            for group in model["groups"]:
                if group["mesh"] not in meshes:
                    raise ValueError("AST/GEO mesh absent from FGX: " + group["mesh"])
                self.mesh(meshes[group["mesh"]], group, transform, asset, path, model, root)
        for attachment in asset["attachments"]:
            owner = owners[attachment["owner"]]
            if owner["geometry"]:
                bone = bone_world(self.geometry(owner["geometry"]), attachment["bone"])
            elif attachment["bone"] == attachment["owner"]:
                bone = Matrix.Identity(4)
            else:
                raise ValueError("Cannot resolve bone on hidden owner: " + attachment["bone"])
            self.assemble(attachment["asset"], transform @ bone @ attachment_matrix(attachment),
                          path + "/" + attachment["id"])

    def clip_foundation(self):
        # Clip only main-building surfaces, leaving attachment pivots/geometry untouched.
        roots = [obj for obj, record in zip(self.objects, self.mapping)
                 if record["root"] and record["material"].startswith("CSC_")
                 and not record["material"].startswith("CSC_ALL_")]
        if not roots:
            roots = [max((o for o, r in zip(self.objects, self.mapping) if r["root"]),
                         key=lambda o: len(o.data.polygons))]
        for obj in roots:
            bm = bmesh.new()
            bm.from_mesh(obj.data)
            normal = (obj.matrix_world.transposed().to_3x3() @ Vector((0, 0, 1))).normalized()
            bmesh.ops.bisect_plane(bm, geom=list(bm.verts) + list(bm.edges) + list(bm.faces),
                                  plane_co=obj.matrix_world.inverted() @ Vector((0, 0, 0)),
                                  plane_no=normal, clear_inner=True)
            bm.to_mesh(obj.data)
            bm.free()
            obj.data.update()

    def setup(self):
        scene = self.scene
        settings, preset = self.job["settings"], self.job["settings"]["presets"][self.mode]
        points = [obj.matrix_world @ v.co for obj in self.objects for v in obj.data.vertices]
        if not points:
            raise ValueError("Assembly has no visible Worked geometry")
        low = Vector([min(p[i] for p in points) for i in range(3)])
        high = Vector([max(p[i] for p in points) for i in range(3)])
        scene_span = max(high - low)
        locked = settings.get("fixed_camera")
        target = Vector(locked["target"]) if locked else (low + high) * 0.5
        span = locked["frame_span"] if locked else scene_span
        camera = bpy.data.objects.new("CSC_" + self.mode + "_Camera", bpy.data.cameras.new("CSC_Camera"))
        scene.collection.objects.link(camera)
        camera.data.type = preset["projection"]
        turn = math.radians(preset["turn"])
        direction = Vector((math.sin(turn), -math.cos(turn), math.tan(math.radians(preset["elevation"])))).normalized()
        if self.mode == "icon":
            camera.data.lens = preset["lens"]
            distance = preset["distance_span"] * span
        else:
            camera.data.ortho_scale = preset["ortho_span"] * span
            distance = 800
        if locked:
            fixed = locked[self.mode]
            camera.data.type = fixed["projection"]
            camera.data.lens = fixed.get("lens", 50.0)
            camera.data.sensor_width = fixed.get("sensor_width", 36.0)
            camera.data.sensor_fit = "AUTO"
            camera.data.shift_x = fixed.get("shift_x", 0.0)
            camera.data.shift_y = fixed.get("shift_y", 0.0)
            if self.mode == "sv":
                camera.data.ortho_scale = fixed["ortho_scale"]
            camera.matrix_world = Matrix(fixed["matrix_world"])
            camera.data.clip_start, camera.data.clip_end = 0.1, 5000
        else:
            camera.location = target + direction * distance
            camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
            camera.data.clip_end = max(5000, distance + span * 3)
        scene.camera = camera
        world = bpy.data.worlds.new("CSC_" + self.mode + "_World")
        world.use_nodes = True
        background = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
        background.inputs["Color"].default_value = (*preset["world_color"], 1)
        background.inputs["Strength"].default_value = preset["world_strength"]
        scene.world = world
        sun = bpy.data.objects.new("CSC_" + self.mode + "_Key", bpy.data.lights.new("CSC_Key", "SUN"))
        scene.collection.objects.link(sun)
        sun.data.energy, sun.data.angle = preset["sun_energy"], math.radians(preset["sun_angle"])
        sun.location = target + Vector(preset["sun_direction"])
        sun.rotation_euler = (target - sun.location).to_track_quat("-Z", "Y").to_euler()
        scene.view_settings.view_transform = preset["view_transform"]
        scene.view_settings.exposure, scene.view_settings.gamma = preset["exposure"], 1
        scene.view_settings.look = "None"
        scene.render.engine = "CYCLES"
        scene.cycles.device = "CPU"
        scene.cycles.samples, scene.cycles.seed = settings["samples"], 0
        scene.cycles.use_animated_seed = False
        scene.cycles.use_adaptive_sampling = False
        scene.cycles.use_denoising = True
        scene.cycles.denoiser = "OPENIMAGEDENOISE"
        scene.render.resolution_x = scene.render.resolution_y = settings["resolution"]
        scene.render.resolution_percentage = 100
        scene.render.film_transparent = True
        scene.render.image_settings.color_mode = "RGBA"
        scene.render.threads_mode, scene.render.threads = "FIXED", 4
        scene.frame_set(1)
        layer = scene.view_layers[0]
        layer.use_pass_normal = layer.use_pass_z = layer.use_pass_object_index = True
        # The ID PNG contains numeric IndexOB/65535 with no display transform.
        group = bpy.data.node_groups.new("CSC_Index_Output", "CompositorNodeTree")
        scene.compositing_node_group = group
        render = group.nodes.new("CompositorNodeRLayers")
        render.scene = scene
        layer.update_render_passes()
        divisor = group.nodes.new("ShaderNodeMath")
        divisor.operation = "DIVIDE"
        divisor.inputs[1].default_value = 65535
        index_socket = render.outputs.get("Object Index") or render.outputs.get("IndexOB")
        if index_socket is None:
            raise ValueError("Object index pass unavailable in this Blender build")
        group.links.new(index_socket, divisor.inputs[0])
        output = group.nodes.new("CompositorNodeOutputFile")
        output.directory, output.file_name = str(self.out / self.mode), "ObjectIndex"
        output.format.media_type = "IMAGE"
        output.format.file_format, output.format.color_mode, output.format.color_depth = "PNG", "BW", "16"
        output.save_as_render = False
        output.file_output_items.new("FLOAT", "ID")
        group.links.new(divisor.outputs[0], output.inputs[0])
        # A compositor group output preserves beauty as the main render result.
        group.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
        main = group.nodes.new("NodeGroupOutput")
        group.links.new(render.outputs["Image"], main.inputs["Image"])
        bpy.context.view_layer.update()
        outside = []
        if locked:
            for obj in self.objects:
                for vertex in obj.data.vertices:
                    point = world_to_camera_view(scene, camera, obj.matrix_world @ vertex.co)
                    if point.z <= 0 or not (0 <= point.x <= 1 and 0 <= point.y <= 1):
                        outside.append(obj.name)
                        break
            if outside:
                self.warnings.append(f"{len(outside)} mesh groups extend beyond the fixed {settings['camera_class']} frame; camera registration retained")
        return {"bounds": [list(low), list(high)], "target": list(target), "span": span,
                "scene_span": scene_span, "camera_class": settings.get("camera_class", "auto"),
                "framing": "fixed" if locked else "automatic", "outside_frame_objects": outside,
                "lens_mm": camera.data.lens, "sensor_width": camera.data.sensor_width,
                "camera_shift": [camera.data.shift_x, camera.data.shift_y],
                "ortho_scale": camera.data.ortho_scale if self.mode == "sv" else None,
                "camera_matrix": [list(row) for row in camera.matrix_world],
                "preset": preset, "objects": len(self.objects)}

    def render(self):
        self.assemble(self.job["root"], root=True)
        bpy.context.view_layer.update()
        self.clip_foundation()
        bpy.context.view_layer.update()
        report = self.setup()
        folder = self.out / self.mode
        folder.mkdir(exist_ok=True)
        scene = self.scene
        previous_mask = folder / "ObjectIndex.png"
        if previous_mask.is_file():
            previous_mask.unlink()
        scene.render.image_settings.media_type = "MULTI_LAYER_IMAGE"
        scene.render.image_settings.file_format = "OPEN_EXR_MULTILAYER"
        scene.render.image_settings.color_depth = "32"
        scene.render.image_settings.exr_codec = "ZIP"
        scene.render.filepath = str(folder / "Geometry.exr")
        bpy.context.preferences.filepaths.save_version = 0
        snapshot = folder / (self.job["assets"][self.job["root"]]["id"] + "_" + self.mode + ".blend")
        bpy.ops.wm.save_as_mainfile(filepath=str(snapshot))
        bpy.ops.render.render(write_still=True)
        scene.render.image_settings.media_type = "IMAGE"
        scene.render.image_settings.file_format = "PNG"
        scene.render.image_settings.color_mode, scene.render.image_settings.color_depth = "RGBA", "8"
        image = folder / (self.job["assets"][self.job["root"]]["id"] + "_Input.png")
        bpy.data.images["Render Result"].save_render(str(image), scene=scene)
        ids = sorted(folder.glob("ObjectIndex*.png"))
        if len(ids) != 1:
            raise ValueError(f"Expected one object-ID mask, found {ids}")
        ids[0].replace(folder / "ObjectIndex.png") if ids[0].name != "ObjectIndex.png" else None
        report.update({"image": str(image), "blend": str(snapshot), "object_ids": self.mapping,
                       "warnings": sorted(set(self.warnings)), "foundation_clip_z": 0,
                       "mask_encoding": "16-bit grayscale PNG: pixel integer = IndexOB; background 0. Non-antialiased labels.",
                       "geometry_passes": "32-bit multilayer EXR: Combined, Normal (world), Depth (distance), IndexOB"})
        (folder / "objects.json").write_text(json.dumps(report, indent=2))
        print("RENDERED", self.mode, image, flush=True)
        return report


def main():
    job = json.loads(Path(sys.argv[sys.argv.index("--") + 1]).read_text())
    reports = {}
    for mode in job["settings"]["modes"]:
        bpy.ops.wm.read_factory_settings(use_empty=True)
        reports[mode] = Builder(job, mode).render()
    (Path(job["output"]) / "render-report.json").write_text(json.dumps(reports, indent=2))


if __name__ == "__main__":
    main()
