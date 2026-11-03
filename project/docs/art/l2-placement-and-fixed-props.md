# L2 placement, fitted paving and fixed props

25 October 2026. Installed in the editable source folders and CSC's AE assets.
Blender, native export, saved-assembly and camera checks pass. Henno confirmed
the facade-aligned paving matches in AE after fully restarting the editor; the previous
session retained an older preview. The subsequent extra front course is checked
in exported data and context renders, awaiting AE review. Cooking and native river appearance remain
untested; the context previews use flat ground projection.

## Shared L2 standard

Henno's in-game-tested `CSC_TEST_Tailor_Wrapper.ast` supplies the transform.
In AE attachment units it is position `(-0.101781, 4.960902, 0)`, Z orientation
`-0.203275` radians and unit scale. In Blender/source units, apply:

```text
p_new = Rz(+11.6467995805 degrees) * p_old + (-1.01781, 49.60902, 0)
```

The current shared L2 source and saved Tailor already coincided before this
change. The older generic runtime mesh and Bakery intact mesh were displaced by
`(-6.402237, -12.217735, 0)` relative to them. The Bakery now first corrects that
offset, then receives the wrapper transform. Its retained attachments, including
empty FX anchors, receive the same combined transform. Tailor attachments receive
the wrapper directly. Scale, culling, terrain-follow settings, materials and
variant-specific placement differences are retained.

The three explicitly named shared sources are updated in place:

- `Working Files/3D Art/Level 2/CSC_Level_2.blend`
- `Working Files/3D Art/Level 2/CSC_Level_2_CON+PIL.blend`
- `Working Files/3D Art/Level 2/CSC_Level_2_PIL_Decals.blend`

Matching FGX/GEO files, Tailor-specific state geometry and existing Bakery
pillage geometry have been updated. The shared starter retains its Bakers
preview palette. The refreshed masters preserve native geometry, UVs and shading
frames, with portable textures, Export/Review scenes and usable static weights.
Original authoring files are recoverable from the installation backup.

The live `CSC_Landmarks.artdef` entry now references `CSC_TAILORS_Tailor` directly.
The test wrapper file and XLP entry remain as historical evidence. **Do not apply
that wrapper to the relocated Tailor: it would apply the move a second time.**

## Tight shared cobble mesh

Both variants in `Working Files/3D Art/Decals/CSC_Stage_3_Cobbles_Two_Variants/`
now use the same fitted, subdivided mesh: **178 vertices / 320 triangles**.
Its support area is 14,193 square source units, down from 22,080 (about 36% less).
Henno rejected the preceding revision's overlap onto the road and requested
smaller stones in both variants, then rejected the baked slant/trapezoid shapes.
The current pass uses true orthogonal squares (4.492 x 4.492 world units) and
rectangles (7.906 x 3.953), with alternate rows offset by half a course.
Rows run parallel to the front facade, using a rigid UV rotation of 42.369667
degrees in the original kit frame, followed by the shared relocation transform.
That direction is measured from area-weighted vertical building faces. There is
no shear or baked perspective; both UV axes have equal texel density.

Each complete boundary stone must clear road03's actual painted footprint:
the 35% road-opacity contour plus 0.75 source units of clearance. This matches
the visible dirt edge; the much fainter texture halo extends well into grass
and is not treated as the road surface. Selection tests
the whole stone, not just its centre. The visible contour follows intact stones;
only a three-pixel transition in the grout supplies antialiasing. The shared
support mesh encloses both patterns without the original rectangular overhang.

The final front-curve follow-up adds one neighbouring course where complete
stones fit: eight square stones and seven rectangles. Existing stones, sizes,
stagger and UV alignment are unchanged. The same road-clearance rule excludes
cells that would encroach. This required geometry as well as texture changes:
the added visible alpha extends outside the previous support mesh. The shared
mesh grew from 172/311 to 178/320 vertices/triangles (about 2% more area), and
both Blender masters, CN6/FGX/GEO exports and matched colour/height maps follow it.
The dated tool is `project/tools/art/l2_front_course.py`; reports and backups
are under `Desktop/Codex/L2-placement-20261025/front-road-extra-course/`.

The rectangular and square maps reuse rectified interior paint from the existing
stone faces, placed into straight rectangular masks. Bevel height and normals
are regenerated from those masks. Their B/H alpha channels share exactly the
same stone-shaped outline. Projection height remains unchanged. Both atlases
are now 2048x2048 mapped to 184x184 world units; TEX width/height metadata matches
the DDS. This prevents the previous non-square texture/world ratio from stretching
the stones. The camera supplies the apparent slant in the rendered result.
The installed geometry
identity and group names remain `CSC_ALL_Stage_3_Cobble_Decals` and
`CSC_ALL_Stage_3_Cobbles_02_Decal`; material selection still chooses the variant.
Both variant `exports/` directories contain the updated CN6/FGX/GEO.

All four runtime B/H TEX source links now point to the corresponding PNGs in
these two variant folders. In particular, the rectangular B no longer watches
the older `CSC_ALL_Stage_3_Cobbles_Single_Decal` folder. Native DDS top-level
RGBA matches the staged PNGs exactly, including after AE's watcher re-encodes
the textures. This is a controlled river-footprint improvement, not a verified
claim about the engine's terrain-projection response.

## Building masters and bundled props

Paths below are relative to `C:/Users/Shadow/Desktop/Working Files/3D Art/`.
Each contains regular and `_2` Blender masters. Their main geometry is shared
between runtime variants; activated additions remain in the corresponding AE
assembly. The files contain independently exportable main geometry, not copied
pantry props or an obsolete whole-scene export arrangement.

| Building | Current source folder | Change | Direct native vertices |
|---|---|---|---:|
| Tailor | `TAILORS/Tailor/revision-11-l2-placement/` | Existing building/fixed geometry moved; lean-to and other attachments retained | 1,590 |
| Bakery | `BAKERS/Bakery/revision-09-l2-placement/` | Current Oven_v2 and both placed peels bundled | 2,018 |
| Fashion House | `TAILORS/Fashion House/revision-13-fixed-fitting/` | Fitting assembly bundled | 2,626 |
| Cafe | `BAKERS/Cafe/revision-01-fixed-counters/` | Both counters, brewing set and pastry tray bundled | 2,993 |

The Fashion House fitting placements differed by less than 0.001 source units
between the saved variants; the shared geometry uses the regular placement.
All other requested bundled placements match exactly apart from float precision.
The Bakery's always-hidden obsolete oven mesh is removed; the visible current
oven is preserved. The alternate Bakery's missing CON+PIL and PIL model references
are restored from the regular asset. Bundled prop group states retain their
original visibility and emission settings, so props do not appear in construction
or pillage. No duplicate attachments remain for the newly bundled props.

Fashion House and Cafe exceed the advisory 2,200 direct-vertex target. These
counts exclude their remaining attachments and the shared cobble mesh; they are
not whole-scene budget claims. Bundling reuses the existing geometry rather than
adding new visible props. Source and rendered normal/activated pairs were checked.

Cafe now references bespoke `CSC_BAKERS_Cafe.geo/.fgx`, with a matching
`CSC_BAKERS_Cafe` armature, model/root and migrated attachment ownership.
The Bakery pillage master likewise has its own export identity. This prevents
the installed Blender export button, which names files after the armature,
from overwriting a shared kit model. The generic L3 kit is unchanged.
The new geometry is registered in ModBuddy and
AE's dependency cache. Pantry and reusable CSC attachments retain their identities.

## Preserved 2D view

`render_ae_asset.py` reads the class presets from
`project/tools/blender/ae_render_camera_presets.json`. Both L2 camera matrices and
their target receive the same rigid transform as the building. Lens, film shifts,
orthographic scale and resolution rules remain unchanged. L2 Sun directions also
rotate with the building; the worker accepts an optional class-specific
`sun_direction`. L1 and L3 retain their existing cameras and lighting.

All 1,590 Tailor main/fixed vertices retain their projected positions to within
0.000412 pixel for icon and 0.000367 pixel for SV at 1024px. Before/after renders
were visually compared. The Bakery now aligns to this common L2 standard; its
previous offset from the kit is intentionally corrected.

## Verification and recovery

Evidence and backups: `C:/Users/Shadow/Desktop/Codex/L2-placement-20261025/`.

- 16 final installed Blender masters reopened and passed the scene validator.
- All 16 export through the installed CN6 add-on; positions, normals, tangents,
  binormals and UV1/2/3 match the intended data within 0.000009 source units.
- 55 meshes across 11 native geometry files passed CN6-to-FGX readback checks.
  GEO bone counts are derived from actual FGX bindings; inactive phantom bindings
  in inherited decal data are removed.
- All eight Worked assemblies retain expected world-space geometry, effective
  texture/material bindings and emission flags. Maximum difference is 0.000557
  source units, from the Fashion House's pre-existing rounding difference.
- All 80 before/after combinations of eight assets and five visibility states
  resolve successfully. The regular and activated previews were inspected.
- The renderer's 12 unit tests pass; all fixed-class camera and calibration checks
  pass. The standard installed-asset renderer resolves the new Cafe dependency.
- AE watcher changes were audited: texture pixels remain exact, TEX changes are
  expected source links/timestamps, and required cache dependencies remain present.

Main review files: `Updated_Assemblies.png`, `Tailor_Camera_Comparison.png`,
`Cobble_Before_Top.png`, `Cobble_After_Top.png`, and the two textured
`context/<asset>/sv/<asset>_Input.png` previews. The reconstructed `.blend` files
under `reviews/` and `context/` are disposable previews, not export masters.

`install-report.json` records individual destinations, hashes and original-file
backups under `install-backup/`. `source-links-backup/` and
`export-identity-backup/` preserve subsequent link/identity corrections.
`stone-edge-revision/before/` and `stone-edge-revision/install-backup/` preserve
the first curved/feathered paving and its later complete-stone revision.
`smaller-stones-road-clearance/` records the subsequent smaller-stone pass,
road-clearance checks, previews and installation backups. Earlier previews are
historical where their paving differs; current road-context previews are in
`context/CSC_TAILORS_Tailor/` and `context/CSC_BAKERS_Bakery/`.
`orthographic-running-bond/` contains the latest straight-stone, half-offset,
facade-aligned revision, with its own backups and shape/alignment checks.
Source tools are `l2_placement_migration.py`,
`l2_placement_blender.py`, `l2_cobbles.py`, `l2_stone_edges.py`,
`l2_smaller_cobbles.py`, `l2_orthographic_cobbles.py` and `l2_context_render.py` in
`project/tools/art/`. They are a dated migration using its immutable baseline;
do not rerun historical installation steps over later AE edits.

Build normally in ModBuddy when ready for the next game review. Check river
variants, the lean-to's full ground support, paving projection and state transitions
in game. Henno has confirmed the final AE appearance; cooking and native in-game
appearance remain untested.
