# AE owns building assembly and placement

Agreed with Henno on 12–13 October 2026. This overrides older Blender-master
composition, replacement-prop alternates and layout-wide prop-pillage guidance.

- **AE owns final assembly and placement**, including attachment copies,
  rotations and scales. Blender review compositions are optional proposals.
  Geometry/UV/material updates must preserve the saved AE assembly and settings.
- **Per-prop Blender delivery (Henno, 17 October 2026):** deliver one editable
  `.blend` per independently exported prop/model identity, including reusable
  wall assets; each file contains only that model's exportable geometry and rig,
  with its own identity, useful support pivot and material bindings. The current
  FGX exporter works best with one model per file. Multiple editable mesh parts
  belonging to that model are fine; repeated placements reuse the same master.
  A combined scene may be supplied for review, but is optional and never replaces
  the individual export masters. This supersedes the combined prop-kit blend
  requirement. Preserve the separate custom-decal masters below.
  Continue using/extending the canonical shared prop material/atlas; native
  pantry props retain their identities, source geometry and materials.
- **New texture artwork (17 October 2026):** use ImageGen for new custom prop
  texture artwork, then pack the approved patches into verified empty slots of
  the canonical shared prop atlas. Reuse existing textures when suitable; the
  new shared cobbles decal reuses the existing cobble texture/material. Preserve
  occupied atlas regions and existing UVs. Companion-map derivation, geometric
  AO baking, packing and validation remain deterministic technical operations.
  Publish accepted patches, maps and allocation/hash manifests together through
  the existing shared-atlas release workflow.
- **Bundled one-off props remain an option (13 October clarification).** A
  CSC-authored prop very close to/integrated with the building and not reused
  elsewhere may be part of its main geometry. In that case the AST references
  bespoke building GEO/FGX containing the starter building plus those props,
  rather than the generic starter geometry alone. Keep the props editable in
  Blender and retain shared prop material bindings in identifiable mesh/groups.
  Their internal positions belong to the geometry master; AE still owns the
  assembly and placement of that geometry and separate attachments. Reusable
  props and props needing independent terrain/placement remain attachments;
  pantry props always remain native attachments. Bundled bespoke props count
  toward the building's existing advisory geometry budget.
- Each standalone custom prop exports independently as an AE asset/XLP entry. Custom props
  are hidden in Construction and Pillaged; attachment Cull Mode is PERMANENT.
  Visibility and culling are separate controls. Bundled props also disappear in
  Construction/Pillaged through the intact main geometry/group state rules.
- Each new custom decal has its own editable blend and AE export.
- **Initial AE setup** supplies generic or bespoke main building geometry, its CON+PIL geometry,
  shared base-building PIL decal, custom decals, and one copy of each required
  standalone prop for Henno to place/duplicate. Do not also attach copies of
  bundled props. Later geometry updates do not recreate the assembly. Reuse the
  shared CON+PIL/PIL assets where they still match the building; reassess those
  sources if actual architecture changes, rather than duplicating them merely
  because intact props were bundled.
- **Alternates retain the standard building and props and add service props.**
  Henno places additions against the surrounding district base, roads and
  occupied space in AE. Existing Service activation rules remain applicable.
- Create the **base-building pillage decal once**, matching the shared building's
  pillaged geometry. Henno has a reusable single-debris-decal asset and manually
  attaches it to props that warrant debris. Do not generate layout-wide prop
  debris sheets or decide those attachments for him.
- Reconstruct the **saved AE AST** in Blender for finalized icon/SV inputs, with
  actual materials and attachment transforms. The blend is a disposable render
  snapshot, never a new placement master. Icon rendering uses the Quarter's
  light-roof `_2` image texture independently of the selected runtime assembly;
  SV retains runtime textures by default.
- Icon/SV render materials omit emissive image textures and use zero emission
  for buildings and props (Henno, 13 October 2026). Runtime AE materials retain
  their authored emission.
- For reusable XCF main-building paths, select fixed `--L1`, `--L2` or `--L3`
  camera registration (14 October 2026). Camera position/rotation, target,
  perspective lens and orthographic scale are independent of prop layout.
  Keep the same level/mode/resolution; assemblies outside the frame are reported
  instead of automatically reframed. `--auto-frame` is an explicit legacy option.

Use [the standardized render runner](2d/ae-asset-renderer.md). The existing
`export_assets.py` still implements legacy whole-scene export: do not use it to
overwrite a Henno-edited AE assembly until selective update behavior is added.
The new rendering tool does not change that exporter.
