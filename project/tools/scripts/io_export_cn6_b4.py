"""
CN6 Export for Blender 4.x/5.x — ported from Deliverator/Sukritact's io_export_cn6.py
Changes from 3.x version:
  - mesh.use_auto_smooth removed (custom normals are implicit in 4.1+)
  - mesh.calc_tangents() still works in 4.x
  - StringProperty annotation style updated
  - bl_info blender version bumped
  - unpack_list/unpack_face_list still exist in 4.x bpy_extras but may deprecate — kept for now
"""

bl_info = {
	"name": "Export CivNexus6 (.cn6)",
	"author": "Deliverator, Sukritact (Blender 4+ port: Bill/CSC)",
	"version": (2, 0),
	"blender": (4, 0, 0),
	"location": "File > Export > CivNexus6 (.cn6)",
	"description": "Export CivNexus6 (.cn6)",
	"warning": "",
	"wiki_url": "",
	"category": "Import-Export"}

import bpy
import bmesh
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

def menu_func(self, context):
	self.layout.operator(export_cn6.bl_idname, text="CivNexus6 (.cn6)")

def register():
	from bpy.utils import register_class
	register_class(export_cn6)
	bpy.types.TOPBAR_MT_file_export.append(menu_func)

def unregister():
	from bpy.utils import unregister_class
	unregister_class(export_cn6)
	bpy.types.TOPBAR_MT_file_export.remove(menu_func)

if __name__ == "__main__":
	register()
