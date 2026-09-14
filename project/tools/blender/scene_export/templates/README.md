# Exporter-owned TileBase templates

These files are inputs shipped with the exporter, outside live mod content.
Generating a building never requires its output AST to exist.

- `tilebase.ast`: default TileBase shell, no attachment points or auxiliary
  geometry. Its one placeholder model supplies all five state rows and is replaced
  entirely by decoded building/fixed geometry and material bindings.
- `level1_small.ast`: the same shell with the shared `CSC_Level_1_S_CON+PIL` and
  `CSC_Level_1_Decals` model instances, preserving their state tables. This profile
  references those shared mod geometries; it does not duplicate/export them.

Select a profile through `csc_export.template_profile`. The default is `tilebase`.
Buildings needing shared construction/pillage geometry must select a suitable
profile; the bare default does not invent those models. Per-building pillage
decal geometry comes from the scene's `decals` list.

Provenance: extracted from CSC's previously authored Textile Workshop TileBase
schema on 14 September 2026. Removed all Workshop geometry, materials and
attachments. Kept TileBase cook settings and the main mesh's FOW/burn/snow/state
parameters; the small profile additionally retains the two shared model instances.
The `Building`, `BuildingMesh` and `BuildingMaterial` names are placeholders and
must never survive in generated output.

For existing revision-08 blends, discovery maps the old explicit
`Assets/CSC_TAILORS_Textile_Workshop.ast` reference to `level1_small`. This is an
exact compatibility alias, independent of whether that output exists. No source
blend edits or runtime Git reads are needed. Unknown custom template paths still
fail instead of silently losing their behavior.

The generated job and discovery report record the selected profile and actual
template path. Templates retain no animation/timeline bindings or FX; introduce
additional profiles explicitly when a building requires different behavior.
