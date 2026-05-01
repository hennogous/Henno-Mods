"""
CN6 Import for Blender 4.x/5.x — ported from Deliverator/Sukritact's io_import_cn6.py
Changes from 3.x version:
  - mesh.use_auto_smooth removed (custom normals implicit in 4.1+)
  - mesh.create_normals_split() removed — normals_split_custom_set() works directly
  - bpy.types.EditBone custom property via bpy.props removed — use dict storage instead
  - StringProperty annotation style updated
  - bl_info blender version bumped
  - unpack_list/unpack_face_list imports removed (not used in import)
"""

bl_info = {
	"name": "Import CivNexus6 (.cn6)",
	"author": "Deliverator, Sukritact (Blender 4+ port: Bill/CSC)",
	"version": (2, 0),
	"blender": (4, 0, 0),
	"location": "File > Import > CivNexus6 (.cn6)",
	"description": "Import CivNexus6 (.cn6)",
	"warning": "",
	"wiki_url": "",
	"category": "Import-Export"}

import bpy
import array
import shlex
from bpy.props import BoolProperty, IntProperty, EnumProperty, StringProperty
from mathutils import Vector, Quaternion, Matrix
from bpy_extras.io_utils import ImportHelper
from math import radians

def getRotationMatrix(matrix_4x4):
	return Matrix([[matrix_4x4[0][0],matrix_4x4[0][1],matrix_4x4[0][2]],
				[matrix_4x4[1][0],matrix_4x4[1][1],matrix_4x4[1][2]],
				[matrix_4x4[2][0],matrix_4x4[2][1],matrix_4x4[2][2]]])

def writeRotationMatrix(matrix_4x4, matrix_3x3):
	for x in range(0, 3):
		for y in range(0, 3):
			matrix_4x4[x][y] = matrix_3x3[x][y]

# returns the next non-empty, non-comment line from the file
def getNextLine(file):
	ready = False
	while ready==False:
		line = file.readline()
		if len(line)==0:
			print ("Warning: End of file reached.")
			return line
		ready = True
		line = line.strip()
		if len(line)==0 or line.isspace():
			ready = False
		if len(line)>=2 and line[0]=='/' and line[1]=='/':
			ready = False
	return line

def do_import(path, DELETE_TOP_BONE=True):

	scn = bpy.context.scene
	if scn==None:
		return "No scene to import to!"

	try:
		file = open(path, 'r')
	except IOError:
		return "Failed to open the file!"

	try:
		if not path.endswith(".cn6"):
			raise IOError
	except IOError:
		return "Must be a cn6 file!"

	# Load Armature
	try:
		lines = getNextLine(file).split()
		if len(lines) != 1 or lines[0] != "skeleton":
			raise ValueError
	except ValueError:
		return "File invalid!"

	if bpy.ops.object.mode_set.poll():
		bpy.ops.object.mode_set(mode='OBJECT')

	armature = bpy.data.armatures.new("Armature")
	armOb = bpy.data.objects.new("ArmatureObject", armature)
	armature.display_type = 'STICK'
	scn.collection.objects.link(armOb)
	bpy.context.view_layer.objects.active = armOb

	# read bones
	boneNames = []
	bpy.ops.object.editmode_toggle()

	# Store rotation matrices in a dict instead of custom bone property
	# (bpy.types.EditBone custom props via bpy.props no longer works in Blender 4+)
	bone_rot_matrices = {}

	currentLine = ""

	boneCount = 0
	boneNameDict = []
	parentBoneIds = []
	positions = []
	quaternions = []

	while(not currentLine.startswith('meshes')):
		currentLine = getNextLine(file)

		if (not currentLine.startswith('meshes')):
			lines = shlex.split(currentLine)
			boneNameDict.append(lines[1])
			parentBoneIds.append(int(lines[2]))
			positions.append([float(lines[3]), float(lines[4]), float(lines[5])])
			quaternions.append([float(lines[6]), float(lines[7]), float(lines[8]), float(lines[9])])
			boneCount = boneCount + 1

	for i in range(boneCount):
		fullName = boneNameDict[i]
		boneNames.append(fullName)
		bone = armature.edit_bones.new(fullName)

		if parentBoneIds[i] >= 0:
			parentBoneName = boneNameDict[parentBoneIds[i]]
			bone.parent = armature.bones.data.edit_bones[parentBoneName]

		pos = positions[i]
		quat = quaternions[i]

		# Granny Rotation Quaternions are stored X,Y,Z,W but Blender uses W,X,Y,Z
		quaternion = Quaternion((quat[3], quat[0], quat[1], quat[2]))
		rotMatrix = quaternion.to_matrix()
		rotMatrix.transpose()

		boneLength = 3
		if bone.parent:
			parent_rm = bone_rot_matrices[bone.parent.name]
			bone_parent_matrix = Matrix([[parent_rm[0], parent_rm[1], parent_rm[2]],
										[parent_rm[3], parent_rm[4], parent_rm[5]],
										[parent_rm[6], parent_rm[7], parent_rm[8]]])
			bone.head = Vector(pos) @ bone_parent_matrix + bone.parent.head
			bone.tail = bone.head + Vector([boneLength,0,0])
			tempM = rotMatrix @ bone_parent_matrix
			rm = [tempM[0][0], tempM[0][1], tempM[0][2],
				  tempM[1][0], tempM[1][1], tempM[1][2],
				  tempM[2][0], tempM[2][1], tempM[2][2]]
			bone_rot_matrices[fullName] = rm
			bone.matrix = Matrix([[-rm[3], rm[0], rm[6], bone.head[0]],
								 [-rm[4], rm[1], rm[7], bone.head[1]],
								 [-rm[5], rm[2], rm[8], bone.head[2]],
								 [0, 0, 0, 1]])
		else:
			bone.head = Vector(pos)
			bone.tail = bone.head + Vector([boneLength,0,0])
			rm = [rotMatrix[0][0], rotMatrix[0][1], rotMatrix[0][2],
				  rotMatrix[1][0], rotMatrix[1][1], rotMatrix[1][2],
				  rotMatrix[2][0], rotMatrix[2][1], rotMatrix[2][2]]
			bone_rot_matrices[fullName] = rm
			bone.matrix = Matrix([[-rm[3], rm[0], rm[6], bone.head[0]],
								 [-rm[4], rm[1], rm[7], bone.head[1]],
								 [-rm[5], rm[2], rm[8], bone.head[2]],
								 [0, 0, 0, 1]])

	# Roll fix for all bones
	for bone in armature.bones.data.edit_bones:
		roll = bone.roll
		bone.roll = roll - radians(90.0)

	# read the number of meshes
	try:
		lines = currentLine
		if not lines.startswith('meshes:'):
			raise ValueError
		numMeshes = int(lines.replace('meshes:',''))
		if numMeshes < 0:
			raise ValueError
	except ValueError:
		return "Number of meshes is invalid!"

	# read meshes
	boneIds = [[],[],[],[],[],[],[],[]]
	boneWeights = [[],[],[],[],[],[],[],[]]
	meshVertexGroups = {}
	vCount = 0

	meshes = []
	meshObjects = []

	for i in range(numMeshes):

		while(not currentLine.startswith('mesh:')):
			currentLine = getNextLine(file)

		lines = currentLine.split(':')
		meshName = lines[1][1:-1] + '#M'
		meshes.append(bpy.data.meshes.new(meshName))

		# read materials
		materialNames = []
		while(not currentLine.startswith('vertices')):
			currentLine = getNextLine(file)
			if (not currentLine.startswith('materials') and not currentLine.startswith('vertices')):
				materialNames.append(currentLine[1:-1])

		# read vertices
		coords = []
		normals = []
		tangents = []
		binormals = []
		uvs = []
		uvs2 = []
		uvs3 = []
		numVerts = 0
		normalsTangentsBinormals = []
		originalTangentsBinormals = {}

		nonMatchingNormalTangentBinormal = True

		while(not currentLine.startswith('triangles')):
			currentLine = getNextLine(file)
			if (not currentLine.startswith('vertices') and not currentLine.startswith('triangles')):
				lines = currentLine.split()
				if len(lines) != 34:
					raise ValueError
				coords.append([float(lines[0]), float(lines[1]), float(lines[2])])
				normals.append([float(lines[3]), float(lines[4]), float(lines[5])])
				tangents.append([float(lines[6]), float(lines[7]), float(lines[8])])
				binormals.append([float(lines[9]), float(lines[10]), float(lines[11])])

				if (numVerts < 10):
					if (abs(float(lines[3]) - float(lines[6])) < 0.000001 and abs(float(lines[4]) - float(lines[7])) < 0.000001 and abs(float(lines[5]) - float(lines[8])) < 0.000001 and
						abs(float(lines[3]) - float(lines[9])) < 0.000001 and abs(float(lines[4]) - float(lines[10])) < 0.000001 and abs(float(lines[5]) - float(lines[11])) < 0.000001):
						nonMatchingNormalTangentBinormal = False
					else:
						nonMatchingNormalTangentBinormal = True

				uvs.append([float(lines[12]), 1-float(lines[13])])
				uvs2.append([float(lines[14]), 1-float(lines[15])])
				uvs3.append([float(lines[16]), 1-float(lines[17])])

				normalsTangentsBinormals.append([float(lines[3]), float(lines[4]), float(lines[5]), float(lines[6]), float(lines[7]), float(lines[8]), float(lines[9]), float(lines[10]), float(lines[11])])

				boneIds[0].append(int(lines[18]))
				boneIds[1].append(int(lines[19]))
				boneIds[2].append(int(lines[20]))
				boneIds[3].append(int(lines[21]))
				boneIds[4].append(int(lines[22]))
				boneIds[5].append(int(lines[23]))
				boneIds[6].append(int(lines[24]))
				boneIds[7].append(int(lines[25]))

				boneWeights[0].append(float(lines[26]))
				boneWeights[1].append(float(lines[27]))
				boneWeights[2].append(float(lines[28]))
				boneWeights[3].append(float(lines[29]))
				boneWeights[4].append(float(lines[30]))
				boneWeights[5].append(float(lines[31]))
				boneWeights[6].append(float(lines[32]))
				boneWeights[7].append(float(lines[33]))

				meshVertexGroups[vCount] = meshName
				numVerts += 1

		# read triangles BEFORE building mesh (Blender 5.x needs from_pydata for reliable mesh construction)
		faces = []
		while (not currentLine.startswith('mesh:') and not currentLine.startswith('end')):
			currentLine = getNextLine(file)
			if (not currentLine.startswith('mesh:') and not currentLine.startswith('end')):
				lines = currentLine.split()
				if len(lines) != 4:
					raise ValueError
				v1 = int(lines[0])
				v2 = int(lines[1])
				v3 = int(lines[2])
				mi = int(lines[3])

			if v1 < numVerts and v2 < numVerts and v3 < numVerts and (mi < len(materialNames) or len(materialNames) == 0):
				faces.append([v1,v2,v3,mi])

		# Build mesh with from_pydata (works reliably in Blender 4.x/5.x)
		mesh = meshes[i]
		face_verts = [(f[0], f[1], f[2]) for f in faces]
		mesh.from_pydata([tuple(c) for c in coords], [], face_verts)
		mesh.update()

		# Set material indices per polygon
		for fi, f in enumerate(faces):
			if fi < len(mesh.polygons):
				mesh.polygons[fi].material_index = f[3]

		meshOb = bpy.data.objects.new(meshName, mesh)

		for materialName in materialNames:
			if materialName in bpy.data.materials:
				meshOb.data.materials.append(bpy.data.materials[materialName])
			else:
				material = bpy.data.materials.new(materialName)
				meshOb.data.materials.append(material)

		if (nonMatchingNormalTangentBinormal):
			meshOb.vertex_groups.new(name="VERTEX_KEYS")
			keyVertexGroup = meshOb.vertex_groups.get("VERTEX_KEYS")

			for v in range(len(mesh.vertices)):
				encoded_weight = (v / 2000000)
				keyVertexGroup.add([v], encoded_weight, 'ADD')
				originalTangentsBinormals[str(v)] = normalsTangentsBinormals[v]

		mesh['originalTangentsBinormals'] = originalTangentsBinormals

		# Add UV layers and set per-loop UVs + custom normals
		mesh.uv_layers.new(name='UV1')
		mesh.uv_layers.new(name='UV2')
		mesh.uv_layers.new(name='UV3')

		custom_normals = []
		for l in mesh.loops:
			custom_normals.append(tuple(normals[l.vertex_index]))
			mesh.uv_layers[0].data[l.index].uv = uvs[l.vertex_index]
			mesh.uv_layers[1].data[l.index].uv = uvs2[l.vertex_index]
			mesh.uv_layers[2].data[l.index].uv = uvs3[l.vertex_index]

		mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

		# Blender 4.1+/5.x: normals_split_custom_set works directly
		try:
			mesh.normals_split_custom_set(custom_normals)
		except Exception:
			# Fallback for older Blender versions
			mesh.create_normals_split()
			clnors = array.array('f', [0.0] * (len(mesh.loops) * 3))
			mesh.loops.foreach_get("normal", clnors)
			mesh.normals_split_custom_set(tuple(zip(*(iter(clnors),) * 3)))
			mesh.use_auto_smooth = True

		meshObjects.append(meshOb)
		scn.collection.objects.link(meshObjects[i])

	for mesh in meshes:
		mesh.update()

	# Create Vertex Groups
	vi = 0
	for meshOb in meshObjects:
		mesh = meshOb.data
		for mvi, vertex in enumerate(mesh.vertices):
			for bi in range(boneCount):
				for j in range(8):
					if bi==boneIds[j][vi]:
						name = boneNames[bi]
						if not meshOb.vertex_groups.get(name):
							meshOb.vertex_groups.new(name=name)
						grp = meshOb.vertex_groups.get(name)
						normalizedWeight = boneWeights[j][vi] / 255
						grp.add([mvi], normalizedWeight, 'ADD')
			vi = vi + 1

		mod = meshOb.modifiers.new('mod_' + mesh.name, 'ARMATURE')
		mod.object = armOb
		mod.use_bone_envelopes = False
		mod.use_vertex_groups = True
		meshOb.parent = armOb

	if DELETE_TOP_BONE:
		bone = armature.bones.data.edit_bones[boneNames[0]]
		while not bone.parent is None:
			bone = bone.parent

		name = bone.name
		armOb.name = name

		if (len(armature.bones.data.edit_bones) > 1):
			bpy.ops.object.select_pattern(pattern=name)
			bpy.ops.armature.delete()

	bpy.ops.object.editmode_toggle()
	bpy.ops.object.editmode_toggle()
	bpy.ops.object.editmode_toggle()

	return ""

class Import_cn6(bpy.types.Operator, ImportHelper):

	bl_idname = "import_shape.cn6"
	bl_label = "Import CN6 (.cn6)"
	bl_description= "Import a CivNexus6 .cn6 file"

	filename_ext = ".cn6"
	filter_glob: StringProperty(default="*.cn6", options={'HIDDEN'})

	filepath: StringProperty(name="File Path", description="Filepath used for importing the file", maxlen=1024, subtype='FILE_PATH')
	DELETE_TOP_BONE: BoolProperty(name="Delete Top Bone", description="Delete Top Bone", default=True)

	def execute(self, context):
		do_import(self.filepath, self.DELETE_TOP_BONE)
		return {'FINISHED'}

def menu_func(self, context):
	self.layout.operator(Import_cn6.bl_idname, text="CivNexus6 (.cn6)")

def register():
	from bpy.utils import register_class
	register_class(Import_cn6)
	bpy.types.TOPBAR_MT_file_import.append(menu_func)

def unregister():
	from bpy.utils import unregister_class
	unregister_class(Import_cn6)
	bpy.types.TOPBAR_MT_file_import.remove(menu_func)

if __name__ == "__main__":
	register()
