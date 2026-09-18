"""
CN6 Export for Blender 4.x/5.x â€” ported from Deliverator/Sukritact's io_export_cn6.py
Changes from 3.x version:
  - mesh.use_auto_smooth removed (custom normals are implicit in 4.1+)
  - mesh.calc_tangents() still works in 4.x
  - StringProperty annotation style updated
  - bl_info blender version bumped
  - unpack_list/unpack_face_list still exist in 4.x bpy_extras but may deprecate â€” kept for now
"""

bl_info = {
	"name": "Export CivNexus6 (.cn6)",
	"author": "Deliverator, Sukritact (Blender 4+ port: Bill/CSC)",
	"version": (2, 5),
	"blender": (4, 0, 0),
	"location": "File > Export > CivNexus6 (.cn6)",
	"description": "Export CivNexus6 (.cn6), with optional CSC FGX/GEO deployment",
	"warning": "",
	"wiki_url": "",
	"category": "Import-Export"}

import bpy
import bmesh
import os
import shutil
import subprocess
import tempfile
from mathutils import Vector, Quaternion, Matrix
from bpy_extras.io_utils import ExportHelper
import math
import array
from bpy.props import (
		BoolProperty,
		FloatProperty,
		StringProperty,
		EnumProperty,
		)

CSC_REPO_ROOT = r"C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods"
CSC_CN6_TO_FGX = os.path.join(CSC_REPO_ROOT, "project", "tools", "cn6libs", "CN6ToFGX.exe")
CSC_CN6_LIBS_DIR = os.path.dirname(CSC_CN6_TO_FGX)
CSC_GEOMETRIES_DIR = os.path.join(CSC_REPO_ROOT, "Civ Supply Chains", "Geometries")
CSC_BAD_BONE_CHARS = ':/<>|'
CSC_BAD_OBJECT_CHARS = ':/<>|#'

def getTranslationOrientation(ob):
	if isinstance(ob, bpy.types.Bone):

		ob_matrix_local = ob.matrix_local.copy()
		ob_matrix_local.transpose()
		t = ob_matrix_local
		ob_matrix_local = Matrix([[-t[2][0], -t[2][1], -t[2][2], -t[2][3]],
								[t[1][0], t[1][1], t[1][2], t[1][3]],
								[t[0][0], t[0][1], t[0][2], t[0][3]],
								[t[3][0], t[3][1], t[3][2], t[3][3]]])

		rotMatrix_z90_4x4 = Matrix.Rotation(math.radians(90.0), 4, 'Z')
		rotMatrix_z90_4x4.transpose()

		t = rotMatrix_z90_4x4 @ ob_matrix_local
		matrix = Matrix([[t[0][0], t[0][1], t[0][2], t[0][3]],
								[t[1][0], t[1][1], t[1][2], t[1][3]],
								[t[2][0], t[2][1], t[2][2], t[2][3]],
								[t[3][0], t[3][1], t[3][2], t[3][3]]])

		parent = ob.parent
		if parent:
			parent_matrix_local = parent.matrix_local.copy()
			parent_matrix_local.transpose()
			t = parent_matrix_local
			parent_matrix_local = Matrix([[-t[2][0], -t[2][1], -t[2][2], -t[2][3]],
									[t[1][0], t[1][1], t[1][2], t[1][3]],
									[t[0][0], t[0][1], t[0][2], t[0][3]],
									[t[3][0], t[3][1], t[3][2], t[3][3]]])
			par_matrix = rotMatrix_z90_4x4 @ parent_matrix_local
			par_matrix_cpy = par_matrix.copy()
			par_matrix_cpy.invert()
			matrix = matrix @ par_matrix_cpy

		matrix.transpose()
		loc, rot, sca = matrix.decompose()
	else:
		matrix = ob.matrix_world
		if matrix:
			loc, rot, sca = matrix.decompose()
		else:
			raise RuntimeError("No matrix_world on object")
	return loc, rot

def getBoneTreeDepth(bone, currentCount):
	if (bone.parent):
		currentCount = currentCount + 1
		return getBoneTreeDepth(bone.parent, currentCount)
	else:
		return currentCount


def BPyMesh_meshWeight2List(ob, me):
	groupNames = [g.name for g in ob.vertex_groups]
	len_groupNames = len(groupNames)

	if not len_groupNames:
		return [[] for i in range(len(me.vertices))], []
	else:
		vWeightList = [[0.0] * len_groupNames for i in range(len(me.vertices))]

	for i, v in enumerate(me.vertices):
		for g in v.groups:
			index = g.group
			if index < len_groupNames:
				vWeightList[i][index] = g.weight

	return groupNames, vWeightList


def meshNormalizedWeights(ob, me):
	groupNames, vWeightList = BPyMesh_meshWeight2List(ob, me)

	if not groupNames:
		return [], []

	for i, vWeights in enumerate(vWeightList):
		tot = 0.0
		for w in vWeights:
			tot += w

		if tot:
			for j, w in enumerate(vWeights):
				vWeights[j] = w / tot

	return groupNames, vWeightList

def getBoneWeights(boneName, weights):
	if boneName in weights[0]:
		group_index = weights[0].index(boneName)
		vgroup_data = [(j, weight[group_index]) for j, weight in enumerate(weights[1]) if weight[group_index]]
	else:
		vgroup_data = []

	return vgroup_data

def csc_armature_items(self, context):
	items = []
	for armature in sorted((o for o in bpy.data.objects if o.type == 'ARMATURE'), key=lambda o: o.name.casefold()):
		scenes = sorted(scene.name for scene in bpy.data.scenes if armature.name in scene.objects)
		description = "Scenes: %s" % (", ".join(scenes) if scenes else "unlinked")
		items.append((armature.name, armature.name, description))
	return items

def csc_find_export_armature(armature_name="", context=None):
	if armature_name:
		armature = bpy.data.objects.get(armature_name)
		if armature is None or armature.type != 'ARMATURE':
			raise RuntimeError("Selected export armature no longer exists: %s" % armature_name)
		return armature

	context = context or bpy.context
	active = context.view_layer.objects.active if context and context.view_layer else None
	if active is not None and active.type == 'ARMATURE':
		return active

	selected = [o for o in context.selected_objects if o.type == 'ARMATURE'] if context else []
	if len(selected) == 1:
		return selected[0]

	scene_armatures = [o for o in context.scene.objects if o.type == 'ARMATURE' and not o.hide_get()] if context else []
	if len(scene_armatures) == 1:
		return scene_armatures[0]

	export_scene = bpy.data.scenes.get('Export')
	export_armatures = [o for o in export_scene.objects if o.type == 'ARMATURE' and not o.hide_render] if export_scene else []
	if len(export_armatures) == 1:
		return export_armatures[0]

	armatures = [o for o in bpy.data.objects if o.type == 'ARMATURE']
	if not armatures:
		raise RuntimeError("No armature object found.")
	raise RuntimeError("Choose an Armature in the export dialog (found %d)." % len(armatures))

def csc_preferred_export_armature(context):
	try:
		return csc_find_export_armature(context=context)
	except RuntimeError:
		return None

def csc_export_meshes(armature_object):
	meshes = []
	for object in bpy.data.objects:
		if object.type != 'MESH' or object.hide_render or object.hide_viewport:
			continue
		parent = object.parent
		is_descendant = False
		while parent is not None:
			if parent == armature_object:
				is_descendant = True
				break
			parent = parent.parent
		is_bound = False
		for modifier in object.modifiers:
			if modifier.type == 'ARMATURE' and modifier.object == armature_object:
				is_bound = True
				break
		if is_descendant or is_bound:
			meshes.append(object)
	if not meshes:
		raise RuntimeError("No exportable mesh children or armature-bound meshes found for %s." % armature_object.name)
	return meshes

def csc_clean_bone_name(name):
	cleaned = name
	for char in CSC_BAD_BONE_CHARS:
		cleaned = cleaned.replace(char, "_")
	return cleaned

def csc_clean_object_name(name):
	cleaned = name
	for char in CSC_BAD_OBJECT_CHARS:
		cleaned = cleaned.replace(char, "_")
	if cleaned.endswith("_M"):
		cleaned = cleaned[:-2]
	return cleaned

def csc_validate_scene_for_export(uv_count, armature_object):
	if bpy.context.mode != 'OBJECT' and bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode='OBJECT')

	mesh_objects = csc_export_meshes(armature_object)
	fixes = []

	for mesh_object in mesh_objects:
		mesh = mesh_object.data
		while len(mesh.uv_layers) < uv_count:
			mesh.uv_layers.new(name="UV%d" % (len(mesh.uv_layers) + 1))
		fixes.append("%s UV layers ready (%d)" % (mesh_object.name, len(mesh.uv_layers)))

	for bone in armature_object.data.bones:
		cleaned = csc_clean_bone_name(bone.name)
		if cleaned != bone.name:
			old_name = bone.name
			bone.name = cleaned
			for object in bpy.data.objects:
				if object.type == 'MESH':
					for vertex_group in object.vertex_groups:
						if vertex_group.name == old_name:
							vertex_group.name = cleaned
			fixes.append("Renamed bone %s -> %s" % (old_name, cleaned))

	for mesh_object in mesh_objects:
		cleaned = csc_clean_object_name(mesh_object.name)
		if cleaned != mesh_object.name:
			old_name = mesh_object.name
			mesh_object.name = cleaned
			mesh_object.data.name = cleaned
			fixes.append("Renamed mesh %s -> %s" % (old_name, cleaned))

		mesh = mesh_object.data
		unweighted_vertices = [v.index for v in mesh.vertices if len(v.groups) == 0]
		if unweighted_vertices:
			vertex_group = mesh_object.vertex_groups.get("Bone")
			if vertex_group is None and armature_object.data.bones:
				root_bone = next((b for b in armature_object.data.bones if b.parent is None), armature_object.data.bones[0])
				vertex_group = mesh_object.vertex_groups.get(root_bone.name)
			if vertex_group is None:
				vertex_group = mesh_object.vertex_groups.new(name="Bone")
			vertex_group.add(unweighted_vertices, 1.0, 'ADD')
			fixes.append("%s weighted %d unweighted vertices" % (mesh_object.name, len(unweighted_vertices)))
		else:
			fixes.append("%s weights OK" % mesh_object.name)

	return fixes, armature_object, mesh_objects

def csc_parse_cn6_metadata(cn6_path):
	skeleton = []
	meshes = []
	current_mesh = None
	in_materials = False
	in_vertices = False
	in_triangles = False

	with open(cn6_path, "r", encoding="utf-8") as cn6_file:
		for raw_line in cn6_file:
			line = raw_line.strip()
			if line.startswith("//") or not line:
				continue
			if line.startswith("mesh:"):
				current_mesh = {
					"name": line.split('"', 2)[1],
					"vertex_count": 0,
					"triangle_count": 0,
					"bound_bone_ids": set(),
					"materials": [],
					"material_triangle_counts": {},
				}
				meshes.append(current_mesh)
				in_materials = False
				in_vertices = False
				in_triangles = False
			elif line == "materials":
				in_materials = True
				in_vertices = False
				in_triangles = False
				continue
			elif line == "vertices":
				in_materials = False
				in_vertices = True
				in_triangles = False
				continue
			elif line == "triangles":
				in_materials = False
				in_vertices = False
				in_triangles = True
				continue
			elif line == "end":
				in_materials = False
				in_vertices = False
				in_triangles = False
			elif in_materials and current_mesh is not None:
				if line.startswith('"') and line.endswith('"'):
					current_mesh["materials"].append(line[1:-1])
			elif in_vertices:
				if current_mesh is not None:
					current_mesh["vertex_count"] += 1
					parts = line.split()
					if len(parts) >= 34:
						try:
							bone_ids = [int(value) for value in parts[18:26]]
							bone_weights = [int(value) for value in parts[26:34]]
						except ValueError:
							bone_ids = []
							bone_weights = []
						for bone_id, bone_weight in zip(bone_ids, bone_weights):
							if bone_id >= 0 and bone_weight > 0:
								current_mesh["bound_bone_ids"].add(bone_id)
			elif in_triangles:
				if current_mesh is not None:
					current_mesh["triangle_count"] += 1
					parts = line.split()
					if len(parts) >= 4:
						material_index = int(parts[3])
						current_mesh["material_triangle_counts"][material_index] = current_mesh["material_triangle_counts"].get(material_index, 0) + 1
			elif line[0].isdigit() and '"' in line:
				try:
					skeleton.append(line.split('"', 2)[1])
				except IndexError:
					pass

	if not skeleton:
		raise RuntimeError("Could not read skeleton from CN6.")
	if not meshes:
		raise RuntimeError("Could not read meshes from CN6.")

	return skeleton, meshes

def csc_geo_groups_xml(mesh):
	materials = mesh["materials"] or [mesh["name"]]
	material_triangle_counts = mesh["material_triangle_counts"]
	groups = []
	first_prim = 0
	for material_index, material_name in enumerate(materials):
		triangle_count = material_triangle_counts.get(material_index, 0)
		if triangle_count == 0 and len(materials) == 1:
			triangle_count = mesh["triangle_count"]
		if triangle_count == 0:
			continue
		groups.append("""<Element>
<m_Name text="{material_name}"/>
<m_nFirstPrim>{first_prim}</m_nFirstPrim>
<m_nPrims>{triangle_count}</m_nPrims>
</Element>""".format(
			material_name=material_name,
			first_prim=first_prim,
			triangle_count=triangle_count,
		))
		first_prim += triangle_count
	return "\n".join(groups)

def csc_write_geo(geo_path, base_name, cn6_path, geo_class):
	skeleton, meshes = csc_parse_cn6_metadata(cn6_path)
	bones_xml = "\n".join('<Element text="%s"/>' % bone for bone in skeleton)
	meshes_xml = []
	total_vertex_count = 0
	total_triangle_count = 0
	for mesh in meshes:
		mesh_name = mesh["name"]
		vertex_count = mesh["vertex_count"]
		triangle_count = mesh["triangle_count"]
		bound_bone_count = max(1, len(mesh["bound_bone_ids"]))
		groups_xml = csc_geo_groups_xml(mesh)
		total_vertex_count += vertex_count
		total_triangle_count += triangle_count
		meshes_xml.append("""<Element>
<m_Name text="{mesh_name}"/>
<m_Groups>
{groups_xml}
</m_Groups>
<m_nBoundBoneCount>{bound_bone_count}</m_nBoundBoneCount>
<m_nPrimitiveCount>{triangle_count}</m_nPrimitiveCount>
<m_nVertexCount>{vertex_count}</m_nVertexCount>
</Element>""".format(
			mesh_name=mesh_name,
			groups_xml=groups_xml,
			bound_bone_count=bound_bone_count,
			triangle_count=triangle_count,
			vertex_count=vertex_count,
		))
	geo_xml = """<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects:GeometryInstance>
<m_CookParams>
<m_Values/>
</m_CookParams>
<m_Version>
<major>0</major>
<minor>0</minor>
<build>0</build>
<revision>0</revision>
</m_Version>
<m_Meshes>
{meshes_xml}
</m_Meshes>
<m_Bones>
{bones_xml}
</m_Bones>
<m_ModelName text="{model_name}"/>
<m_SourceFilePath text=""/>
<m_SourceObjectName text=""/>
<m_ImportedTime>0</m_ImportedTime>
<m_ExportedTime>0</m_ExportedTime>
<m_ClassName text="{geo_class}"/>
<m_DataFiles>
<Element>
<m_ID text="GR2"/>
<m_RelativePath text="{base_name}.fgx"/>
</Element>
</m_DataFiles>
<m_Name text="{base_name}"/>
<m_Description text="{base_name}"/>
<m_Tags>
<Element text="{geo_class}"/>
</m_Tags>
<m_Groups/>
</AssetObjects:GeometryInstance>
""".format(
		meshes_xml="\n".join(meshes_xml),
		bones_xml=bones_xml,
		model_name=skeleton[0],
		geo_class=geo_class,
		base_name=base_name,
	)
	with open(geo_path, "w", encoding="utf-8") as geo_file:
		geo_file.write(geo_xml)
	return meshes, total_vertex_count, total_triangle_count

def csc_convert_cn6_to_fgx(cn6_path, fgx_path, vertex_format):
	if not os.path.exists(CSC_CN6_TO_FGX):
		raise RuntimeError("CN6ToFGX.exe not found: %s" % CSC_CN6_TO_FGX)

	result = subprocess.run(
		[CSC_CN6_TO_FGX, cn6_path, fgx_path, str(vertex_format)],
		cwd=CSC_CN6_LIBS_DIR,
		capture_output=True,
		text=True,
		creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
	)
	if result.returncode != 0 or not os.path.exists(fgx_path) or os.path.getsize(fgx_path) == 0:
		output = (result.stdout or "") + (result.stderr or "")
		raise RuntimeError("CN6ToFGX failed: %s" % (output.strip() or "no output"))

def csc_do_export_selected(cn6_path, export_objects):
	previous_selection = list(bpy.context.selected_objects)
	previous_active = bpy.context.view_layer.objects.active

	try:
		for object in bpy.context.selected_objects:
			object.select_set(False)
		for object in export_objects:
			object.select_set(True)
		bpy.context.view_layer.objects.active = export_objects[0]
		do_export(cn6_path, triangulate=True, use_selection=True)
	finally:
		for object in bpy.context.selected_objects:
			object.select_set(False)
		for object in previous_selection:
			if object.name in bpy.data.objects:
				object.select_set(True)
		if previous_active and previous_active.name in bpy.data.objects:
			bpy.context.view_layer.objects.active = previous_active

def csc_export_fgx_geo(base_name, output_dir, geo_class, uv_count, keep_cn6, armature_object):
	os.makedirs(output_dir, exist_ok=True)
	previous_scene = bpy.context.window.scene if bpy.context.window else None
	armature_scenes = [scene for scene in bpy.data.scenes if armature_object.name in scene.objects]
	export_scene = next((scene for scene in armature_scenes if scene.name == 'Export'), None)
	target_scene = export_scene or (bpy.context.scene if bpy.context.scene in armature_scenes else None)
	if target_scene is None and armature_scenes:
		target_scene = armature_scenes[0]
	if target_scene is None:
		raise RuntimeError("Selected armature is not linked to a Blender scene: %s" % armature_object.name)
	try:
		if target_scene is not None and bpy.context.window:
			bpy.context.window.scene = target_scene
		target_scene.view_layers[0].update()
		fixes, armature_object, mesh_objects = csc_validate_scene_for_export(uv_count, armature_object)
		export_objects = [armature_object] + mesh_objects

		with tempfile.TemporaryDirectory(prefix="csc_cn6_export_") as temp_dir:
			cn6_path = os.path.join(temp_dir, base_name + ".cn6")
			fgx_path = os.path.join(temp_dir, base_name + ".fgx")
			geo_path = os.path.join(temp_dir, base_name + ".geo")

			csc_do_export_selected(cn6_path, export_objects)
			csc_convert_cn6_to_fgx(cn6_path, fgx_path, uv_count - 1)
			mesh_summaries, vertex_count, triangle_count = csc_write_geo(geo_path, base_name, cn6_path, geo_class)

			shutil.copy2(fgx_path, os.path.join(output_dir, base_name + ".fgx"))
			shutil.copy2(geo_path, os.path.join(output_dir, base_name + ".geo"))
			if keep_cn6:
				shutil.copy2(cn6_path, os.path.join(output_dir, base_name + ".cn6"))
	finally:
		if previous_scene is not None and bpy.context.window:
			bpy.context.window.scene = previous_scene

	return fixes, mesh_summaries, vertex_count, triangle_count

def do_export(filename, triangulate, use_selection):
	print ("Start CN6 Export...")

	file = open( filename, 'w')
	filedata = "// CivNexus6 CN6 - Exported from Blender for import to CivNexus6\n"

	try:
		modelObs = {}
		modelMeshes = {}

		objectSet = bpy.data.objects
		if use_selection:
			objectSet = bpy.context.selected_objects

		for object in objectSet:

			if object.type == 'ARMATURE':
				modelObs[object.name] = object

			if object.type == 'MESH':
				print ("Getting parent for mesh: %s" % object.name)
				for modifier in object.modifiers:
					if modifier.type == 'ARMATURE' and modifier.object is not None:
						parentArmOb = modifier.object
						if not parentArmOb.name in modelMeshes:
							modelMeshes[parentArmOb.name] = []
						modelMeshes[parentArmOb.name].append(object)
						break  # Only need the first armature modifier

		for modelObName in modelObs.keys():
			boneIds = {}

			# Write Skeleton
			filedata += "skeleton\n"

			armOb = modelObs[modelObName]
			armature = armOb.data

			# Calc bone depths and sort
			boneDepths = []
			for bone in armature.bones.values():
				boneDepth = getBoneTreeDepth(bone, 0)
				boneDepths.append((bone, boneDepth))

			boneDepths = sorted(boneDepths, key=lambda k: k[0].name)
			boneDepths = sorted(boneDepths, key=lambda k: k[1])
			sortedBones = boneDepths

			for boneid, boneTuple in enumerate(sortedBones):
				boneIds[boneTuple[0].name] = boneid

			boneIds[armOb.name] = -1 # Add entry for World Bone

			# Write World Bone
			filedata += '%d "%s" %d ' % (0, armOb.name, -1)
			filedata += '%.8f %.8f %.8f ' % (0.0, 0.0, 0.0)
			filedata += '%.8f %.8f %.8f %.8f ' % (0.0, 0.0, 0.0, 1.0)
			filedata += '%.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f\n' % (1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0)

			if (len(boneIds) > 1 or armOb.name != armature.bones[0].name):
				for boneid, boneTuple in enumerate(sortedBones):
					bone = boneTuple[0]

					position, orientationQuat = getTranslationOrientation(bone)

					# Get Inverse World Matrix for bone
					x = bone.matrix_local.copy()
					x.transpose()
					t = Matrix([[-x[2][0], -x[2][1], -x[2][2], -x[2][3]],
								[x[1][0], x[1][1], x[1][2], x[1][3]],
								[x[0][0], x[0][1], x[0][2], x[0][3]],
								[x[3][0], x[3][1], x[3][2], x[3][3]]])
					t.invert()
					invWorldMatrix = Matrix([[t[0][1], -t[0][0], t[0][2], t[0][3]],
										[t[1][1], -t[1][0], t[1][2], t[1][3]],
										[t[2][1], -t[2][0], t[2][2], t[2][3]],
										[t[3][1], -t[3][0], t[3][2], t[3][3]]])

					outputBoneName = bone.name

					filedata += '%d "%s" ' % (boneid + 1, outputBoneName)

					parentBoneId = 0
					if bone.parent:
						parentBoneId = boneIds[bone.parent.name] + 1

					filedata += '%d ' % parentBoneId
					filedata +='%.8f %.8f %.8f ' % (position[0], position[1], position[2])
					filedata +='%.8f %.8f %.8f %.8f ' % (orientationQuat[1], orientationQuat[2], orientationQuat[3], orientationQuat[0])
					filedata += '%.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f %.8f' % (invWorldMatrix[0][0], invWorldMatrix[0][1], invWorldMatrix[0][2], invWorldMatrix[0][3],
																						invWorldMatrix[1][0], invWorldMatrix[1][1], invWorldMatrix[1][2], invWorldMatrix[1][3],
																						invWorldMatrix[2][0], invWorldMatrix[2][1], invWorldMatrix[2][2], invWorldMatrix[2][3],
																						invWorldMatrix[3][0], invWorldMatrix[3][1], invWorldMatrix[3][2], invWorldMatrix[3][3])
					filedata += "\n"

			if len(modelMeshes) == 0:
				filedata += 'meshes:%d\n' % 0
			else:
				filedata += 'meshes:%d\n' % len(modelMeshes[modelObName])

				for meshObject in modelMeshes[modelObName]:

					mesh = meshObject.data
					if triangulate:
						mesh = mesh.copy()
						bm = bmesh.new()
						bm.from_mesh(mesh)
						bmesh.ops.triangulate(bm, faces=bm.faces[:])
						bm.to_mesh(mesh)
						bm.free()

					meshName = meshObject.name

					filedata += 'mesh:"%s"\n' % meshName

					filedata += 'materials\n'
					for material in meshObject.data.materials:
						filedata += '\"%s\"\n' % material.name

					# Read in preserved Normals, Binormals and Tangents
					vertexBinormalsTangents = {}
					originalVertexNormals = {}

					useOriginalNormals = meshObject.vertex_groups.get("VERTEX_KEYS") is not None and mesh.get('originalTangentsBinormals') is not None

					if useOriginalNormals:
						for index, vertex in enumerate(mesh.vertices):
								keyVertexGroup = meshObject.vertex_groups.get("VERTEX_KEYS")
								if keyVertexGroup is not None:
									weight = vertex.groups[keyVertexGroup.index].weight * 2000000
									decodedVertexIndex = str(int(round(weight)))
									if mesh['originalTangentsBinormals'].get(decodedVertexIndex) is not None:
										tangentsBinormals = mesh['originalTangentsBinormals'][decodedVertexIndex]
										originalVertexNormals[str(index)] = tangentsBinormals

					# calc_tangents still works in Blender 4.x/5.x
					mesh.calc_tangents(uvmap = mesh.uv_layers[0].name)

					for poly in mesh.polygons:
						for loop_index in poly.loop_indices:
							currentVertexIndex = mesh.loops[loop_index].vertex_index
							loop = mesh.loops[loop_index]
							currentVertBinormTang = (loop.normal[0], loop.normal[1], loop.normal[2], loop.tangent[0],loop.tangent[1],loop.tangent[2], loop.bitangent[0], loop.bitangent[1], loop.bitangent[2])
							if not currentVertexIndex in vertexBinormalsTangents:
								vertexBinormalsTangents[currentVertexIndex] = []
							vertexBinormalsTangents[currentVertexIndex].append(currentVertBinormTang)

					if useOriginalNormals:
						# Blender 4.1+ : use normals_split_custom_set without create_normals_split
						# (custom normals are implicit, no need for use_auto_smooth)
						clnors_list = [None] * len(mesh.loops)
						for loopIndex, loop in enumerate(mesh.loops):
							if originalVertexNormals.get(str(loop.vertex_index)) is not None:
								normalsEtc = originalVertexNormals[str(loop.vertex_index)]
								clnors_list[loopIndex] = (normalsEtc[0], normalsEtc[1], normalsEtc[2])
							else:
								clnors_list[loopIndex] = tuple(loop.normal)

						mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

						try:
							# Blender 4.1+ path
							mesh.normals_split_custom_set(clnors_list)
						except Exception:
							# Fallback for older 4.0
							mesh.create_normals_split()
							mesh.normals_split_custom_set(clnors_list)
							mesh.use_auto_smooth = True

					# Average out Normals, Tangents and Bitangents for each Vertex
					vertexNormsBinormsTangsSelected = {}

					for vertId in vertexBinormalsTangents.keys():
						sum0, sum1, sum2, sum3, sum4, sum5, sum6, sum7, sum8 = 0,0,0,0,0,0,0,0,0
						for currentrow in vertexBinormalsTangents[vertId]:
							sum0 += currentrow[0]; sum1 += currentrow[1]; sum2 += currentrow[2]
							sum3 += currentrow[3]; sum4 += currentrow[4]; sum5 += currentrow[5]
							sum6 += currentrow[6]; sum7 += currentrow[7]; sum8 += currentrow[8]

						numRows = len(vertexBinormalsTangents[vertId])
						vertexNormsBinormsTangsSelected[vertId] = (sum0/numRows, sum1/numRows, sum2/numRows,
																	sum3/numRows, sum4/numRows, sum5/numRows,
																	sum6/numRows, sum7/numRows, sum8/numRows)

					# Get Bone Weights
					weights = meshNormalizedWeights(meshObject, mesh)
					vertexBoneWeights = {}

					for boneName in boneIds.keys():
						vgroupDataForBone = getBoneWeights(boneName, weights)
						for vgData in vgroupDataForBone:
							vertexId = vgData[0]
							weight = vgData[1]
							if not vertexId in vertexBoneWeights:
								vertexBoneWeights[vertexId] = []
							vertexBoneWeights[vertexId].append((boneName, weight))

					grannyVertexBoneWeights = {}
					for vertId in vertexBoneWeights.keys():
						rawBoneIdWeightTuples = []
						firstBoneId = 0
						for i in range(max(8,len(vertexBoneWeights[vertId]))):
							if i < len(vertexBoneWeights[vertId]):
								vertexBoneWeightTuple = vertexBoneWeights[vertId][i]
								boneName = vertexBoneWeightTuple[0]
								rawBoneIdWeightTuples.append((boneIds[boneName] + 1, vertexBoneWeightTuple[1]))
								if i == 0:
									firstBoneId = boneIds[boneName] + 1
							else:
								rawBoneIdWeightTuples.append((firstBoneId, 0))

						sortedBoneIdWeightTuples = sorted(rawBoneIdWeightTuples, key=lambda x: x[1], reverse=True)

						boneIdsList = []
						rawBoneWeightsList = []
						for i in range(8):
							boneIdsList.append(sortedBoneIdWeightTuples[i][0])
							rawBoneWeightsList.append(sortedBoneIdWeightTuples[i][1])

						rawWeightTotal = sum(rawBoneWeightsList)

						boneWeightsList = []
						for weight in rawBoneWeightsList:
							calcWeight = round(255 * weight / rawWeightTotal) if rawWeightTotal else 0
							boneWeightsList.append(calcWeight)

						runningTotal = sum(boneWeightsList)
						if runningTotal != 255:
							boneWeightsList[0] = boneWeightsList[0] + (255 - runningTotal)

						grannyVertexBoneWeights[vertId] = (boneIdsList, boneWeightsList)

					position, orientationQuat = getTranslationOrientation(meshObject)

					filedata += "vertices\n"

					# Get unique vertex/uv coordinate combinations
					uniqueVertSet = set()
					uniqueVertUVIndexes = {}
					uniqueVertUVs = []
					currentVertUVIndex = 0

					currentTriangleId = 0
					triangleVertUVIndexes = []
					triangleMaterialIndexes = []

					for poly in mesh.polygons:
						triangleVertUVIndexes.append([])

						for loop_index in poly.loop_indices:
							vertexId = mesh.loops[loop_index].vertex_index

							uv = tuple(mesh.uv_layers[0].data[loop_index].uv) if mesh.uv_layers[0] else (0.0, 1.0)
							uv2 = tuple(mesh.uv_layers[1].data[loop_index].uv) if len(mesh.uv_layers) > 1 else (0.0, 1.0)
							uv3 = tuple(mesh.uv_layers[2].data[loop_index].uv) if len(mesh.uv_layers) > 2 else (0.0, 1.0)

							vertSig = '%i|%.8f|%.8f|%.8f|%.8f|%.8f|%.8f' % (vertexId, uv[0], uv[1], uv2[0], uv2[1], uv3[0], uv3[1])

							if vertSig in uniqueVertSet:
								triangleVertUVIndex = uniqueVertUVIndexes[vertSig]
							else:
								uniqueVertSet.add(vertSig)
								uniqueVertUVIndexes[vertSig] = currentVertUVIndex
								uniqueVertUVs.append((vertexId, uv[0], uv[1], uv2[0], uv2[1], uv3[0], uv3[1]))
								triangleVertUVIndex = currentVertUVIndex
								currentVertUVIndex += 1

							triangleVertUVIndexes[currentTriangleId].append(triangleVertUVIndex)

						triangleMaterialIndexes.append(poly.material_index)
						currentTriangleId += 1

					# Write Vertices
					for uniqueVertUV in uniqueVertUVs:
						vertexIndex = uniqueVertUV[0]
						vertex = mesh.vertices[vertexIndex]
						vertCoord = tuple(vertex.co)

						uv = (uniqueVertUV[1], uniqueVertUV[2])
						uv2 = (uniqueVertUV[3], uniqueVertUV[4])
						uv3 = (uniqueVertUV[5], uniqueVertUV[6])

						if originalVertexNormals.get(str(vertexIndex)) is not None:
							tangentsBinormals = originalVertexNormals[str(vertexIndex)]
							vertNormal = (tangentsBinormals[0],tangentsBinormals[1],tangentsBinormals[2])
							vertTangent = (tangentsBinormals[3],tangentsBinormals[4],tangentsBinormals[5])
							vertBinormal = (tangentsBinormals[6],tangentsBinormals[7],tangentsBinormals[8])
						else:
							vertNBT = vertexNormsBinormsTangsSelected[vertexIndex]
							vertNormal = (vertNBT[0], vertNBT[1], vertNBT[2])
							vertTangent = (vertNBT[3], vertNBT[4], vertNBT[5])
							vertBinormal = (vertNBT[6], vertNBT[7], vertNBT[8])

						filedata +='%.8f %.8f %.8f ' % (vertCoord[0] + position[0],  vertCoord[1] + position[1], vertCoord[2] + position[2])
						filedata +='%.8f %.8f %.8f ' % (vertNormal[0], vertNormal[1], vertNormal[2])
						filedata +='%.8f %.8f %.8f ' % (vertTangent[0], vertTangent[1], vertTangent[2])
						filedata +='%.8f %.8f %.8f ' % (vertBinormal[0], vertBinormal[1], vertBinormal[2])
						filedata +='%.8f %.8f ' % (uv[0], 1 - uv[1])
						filedata +='%.8f %.8f ' % (uv2[0], 1 - uv2[1])
						filedata +='%.8f %.8f ' % (uv3[0], 1 - uv3[1])

						if vertexIndex in grannyVertexBoneWeights:
							vBoneWeightTuple = grannyVertexBoneWeights[vertexIndex]
						else:
							vBoneWeightTuple = ([-1,-1,-1,-1,-1,-1,-1,-1],[-1,-1,-1,-1,-1,-1,-1,-1])

						filedata +='%d %d %d %d %d %d %d %d ' % tuple(vBoneWeightTuple[0])
						filedata +='%d %d %d %d %d %d %d %d\n' % tuple(vBoneWeightTuple[1])

					# Write Triangles
					filedata += "triangles\n"

					outputTriangles = []
					for triangle_id, triangle in enumerate(triangleVertUVIndexes):
						materialIndex = triangleMaterialIndexes[triangle_id]
						outputTriangles.append((triangle[0],triangle[1],triangle[2], materialIndex))

					sortedOutputTriangles = sorted(outputTriangles, key=lambda t: t[3])

					for triangle in sortedOutputTriangles:
						filedata += '%i %i %i %i\n' % (triangle[0],triangle[1],triangle[2], triangle[3])

		filedata += "end"
		file.write(filedata)
		file.flush()
		file.close()
	except:
		filedata += "aborted!"
		file.write(filedata)
		file.flush()
		file.close()
		raise

	print ("End CN6 Export.")
	return ""

class export_cn6(bpy.types.Operator, ExportHelper):

	bl_idname = "export_shape.cn6"
	bl_label = "Export CN6 (.cn6)"
	bl_description= "Export a CivNexus6 .cn6 file"
	bl_options = {'PRESET'}

	filename_ext = ".cn6"
	filter_glob: StringProperty(default="*.cn6", options={'HIDDEN'})
	check_extension = True

	triangulate: BoolProperty(
			name="Triangulate",
			description="Triangulate meshes before exporting",
			default=True,
			)
	use_selection: BoolProperty(
			name="Selected Objects",
			description="Export only selected and visible objects",
			default=False,
			)

	def execute(self, context):
		print ("Export Filename: {}".format(self.filepath))
		do_export(self.filepath,
			self.triangulate,
			self.use_selection,
			)
		return {'FINISHED'}

class export_csc_fgx_geo(bpy.types.Operator):

	bl_idname = "export_shape.csc_fgx_geo"
	bl_label = "CSC FGX/GEO via CN6"
	bl_description = "Export current Blender scene to Civ VI .fgx + .geo and copy them to CSC Geometries"
	bl_options = {'PRESET'}

	armature_name: EnumProperty(
			name="Armature",
			description="Armature whose mesh children/bindings will be exported",
			items=csc_armature_items,
			)

	output_dir: StringProperty(
			name="Output Directory",
			description="Folder where .fgx and .geo files will be copied",
			default=CSC_GEOMETRIES_DIR,
			subtype='DIR_PATH',
			)
	geo_class: EnumProperty(
			name="Geometry Class",
			description="Civ VI geometry class for the .geo file",
			items=(
				("LandmarkModel", "LandmarkModel", "Buildings, districts, city blocks, and clutter"),
				("DecalGeometry", "DecalGeometry", "Terrain decals"),
				("LandmarkObstructionProfile", "LandmarkObstructionProfile", "2D obstruction profiles"),
				("Unit", "Unit", "Unit models"),
				("VFXModel", "VFXModel", "VFX geometry"),
				),
			default="LandmarkModel",
			)
	uv_count: EnumProperty(
			name="UV Maps",
			description="Number of UV maps written to the FGX",
			items=(
				("1", "1 UV", "Position, normal, tangent, binormal, and UV0"),
				("2", "2 UVs", "Position, normal, tangent, binormal, UV0, and UV1"),
				("3", "3 UVs", "Position, normal, tangent, binormal, UV0, UV1, and UV2"),
				),
			default="3",
			)
	keep_cn6: BoolProperty(
			name="Also copy CN6",
			description="Copy the intermediate .cn6 into Geometries for inspection/debugging",
			default=False,
			)

	def execute(self, context):
		try:
			armature_object = csc_find_export_armature(self.armature_name, context)
			base_name = armature_object.name
			fixes, mesh_summaries, vertex_count, triangle_count = csc_export_fgx_geo(
				base_name,
				bpy.path.abspath(self.output_dir),
				self.geo_class,
				int(self.uv_count),
				self.keep_cn6,
				armature_object,
			)
		except Exception as exc:
			self.report({'ERROR'}, str(exc))
			print("CSC FGX/GEO export failed: %s" % exc)
			return {'CANCELLED'}

		print("CSC FGX/GEO export OK: %s" % base_name)
		print("  Meshes: %s | %d verts, %d tris" % (", ".join(mesh["name"] for mesh in mesh_summaries), vertex_count, triangle_count))
		for fix in fixes:
			print("  %s" % fix)

		self.report(
			{'INFO'},
			"Exported %s.fgx/.geo to Geometries (%d verts, %d tris)" % (base_name, vertex_count, triangle_count),
		)
		return {'FINISHED'}

	def invoke(self, context, event):
		preferred = csc_preferred_export_armature(context)
		if preferred is not None:
			self.armature_name = preferred.name
		return context.window_manager.invoke_props_dialog(self, width=520)

def menu_func(self, context):
	self.layout.operator(export_cn6.bl_idname, text="CivNexus6 (.cn6)")
	self.layout.operator(export_csc_fgx_geo.bl_idname, text="CSC FGX/GEO via CN6 (.fgx/.geo)")

def register():
	from bpy.utils import register_class
	register_class(export_cn6)
	register_class(export_csc_fgx_geo)
	bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
	from bpy.utils import unregister_class
	bpy.types.TOPBAR_MT_file_export.remove(menu_func)
	unregister_class(export_csc_fgx_geo)
	unregister_class(export_cn6)

if __name__ == "__main__":
	register()
