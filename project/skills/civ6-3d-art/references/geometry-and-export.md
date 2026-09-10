# Geometry and export: count what the renderer receives

## Surface patches and shared vertices

Use economical faces for walls and broad roof surfaces; give silhouette edges,
openings, structural members and visible thickness enough geometry to read. Open
meshes and intersecting pieces can be appropriate. Remove enclosed or buried faces
only after checking camera rotation, shadows and state changes. Smooth connected
patches remain useful for curved roofs, vessels, arches and domes.

“Floating quads” is a useful construction strategy, not a mandatory topology type.
An imported game mesh with many disconnected patches may have been split during
export at UV/normal seams. It does not establish exactly how the original artist
modeled it. Do not split every triangle merely because imported geometry is split.

The supplied native Market import measures 480 vertices, 294 triangles and 94 indexed
components, but only 17 components after grouping coincident positions at 0.001 source
units. It has custom corner normals; about 37% differ from geometric face normals by
more than one degree. This supports deliberate patch boundaries with mixed shading,
not mandatory flat shading or indiscriminate welding. Positional coincidence alone
does not mean attributes can be shared, or prove the original authoring topology.

For scale: a box may contain 8 shared positions in an editable mesh, while six hard
faces with independent face attributes need 24 vertices. Two triangles on a planar
quad can still share four vertices. Splitting each triangle would use six. A box
without its bottom has five independent quads: 20 vertices, not 10.

Budget silhouette, material groups/draw calls, texture allocation and many placed
instances together. Do not compromise the defining roofline to reach an arbitrary
vertex number when the actual project budget permits it.

## Why counts expand

A Blender position can have several face-corner attributes. UV seams in any exported
channel, discontinuous normals or tangents, mirrored UV orientation and some material
partitioning/export policies can require duplicated runtime vertices. UV1 sharing
does not remove UV2 seams. Triangulation normally adds triangles rather than positions,
but evaluation, modifiers and exporter rules can change the result.

Maintain three different quantities:

1. Editable source positions: useful for authoring, not the final budget.
2. Export-prepared/evaluated mesh vertices: should expose planned splits in Blender.
3. Actual exported vertices per mesh/LOD: authoritative for that export stage.

Measure FGX/Asset Editor counts for the same mesh/LOD and build. Multiple material
groups, attachments, LODs or states may make an aggregate UI count incomparable.
The aim is no unexplained expansion; literal equality with the editable source is
neither necessary nor guaranteed. Equality with the export-prepared Blender mesh is
a useful target once validated through the actual converter.

## Observed CSC exporter behavior (inspect current code before applying)

At the 2026-09-10 blacksmith baseline, `project/tools/scripts/io_export_cn6_b4.py`:

- Triangulates before writing.
- Keys output vertices by source vertex ID plus UV1, UV2 and UV3, formatted to eight
  decimal places. Distinct source IDs remain distinct even at identical positions.
- Collects loop normal/tangent/bitangent values and averages them per source vertex
  on the ordinary authored-mesh path. The deduplication key does not independently
  preserve conflicting loop normals or tangents.
- Has an alternate path for preserved imported normal/tangent data.

Consequences: don't assume the generic ideal of a full attribute-tuple exporter.
For this version, prepare separate source vertices where corner normal/tangent data
must differ, or deliberately improve and regression-test the exporter. Do this on
an export copy and retain the editable source. Blanket splitting was a conservative
workaround for the blacksmith, not an optimized rule to enforce on every asset.

When the exporter changes, update its adapter/measurement procedure rather than
blindly reusing a guessed count formula. Prefer real temporary exports for budget
validation. Exporter changes need known-good imported and newly authored fixtures.

## Export-preparation and verification

Establish final scale in mesh data and apply transforms according to the destination
pipeline. Preserve intended hard/smooth shading. Finalize triangulation consistently
between normal baking and export; evaluate modifiers and inspect the resulting mesh.
Resolve discontinuities in all three UV channels and tangent space before counting.

Check degenerates, missing faces, flipped winding, unexpected material slots, names,
bone bindings, unique AO coverage and texture paths. Do not enforce manifoldness for
static surface architecture. Do not auto-repair intentional openings into solid boxes.

An acceptance report should contain:

- Source and export-prepared counts, actual CN6 counts, triangles and materials.
- Exporter/converter versions or hashes, asset ID and exact input files.
- UV channel order and AO overlap/bounds result; texture dimensions and color spaces.
- Mesh dimensions/transforms and armature/binding checks.
- Converted mesh counts and destination inspection when available.
- Gray and textured renders, then a same-scale in-game view when available.

The blacksmith measured 1,491 CN6 vertices and 781 triangles with one material. Its
v4/v5 CN6 vertex and triangle sections matched exactly, including UVs. Henno then
confirmed that the 1,491 Blender vertices also appeared as 1,491 in Asset Editor.
Blender → CN6 → Asset Editor parity is confirmed for this blacksmith (destination
count user-reported). The in-game screenshot also shows visual placement. Do not
generalize this to all topology or claim a separately measured destination triangle
count, converter version or tangent validation that was not supplied.

## First calibration fixtures

To extend the blacksmith's confirmed parity into predictable automated export,
test a hard cube, smooth cylinder,
mirrored UV patch, two coplanar triangles, and an independent UV2 seam. Compare the
export-prepared Blender counts with CN6 and converted FGX, and inspect shading under
a moving light. Keep the same fixtures as regression tests for exporter changes.

Blender's [mesh structure documentation](https://developer.blender.org/docs/features/objects/mesh/mesh/)
explains the distinction between positions and face-corner data. The local exporter
source, not that generic model, determines this pipeline's actual serialization.
