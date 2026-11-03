# L2 relocation and fixed props — 25 October 2026

Completed source/AE-file installation for Henno's eight-part request and follow-up
to shape the cobble mesh itself. Durable truth:
`project/docs/art/l2-placement-and-fixed-props.md`.

- Wrapper: AE (-.101781,4.960902,0), z=-.203275; source T=translation
  (-1.01781,49.60902,0) @ Rz(+.203275). Shared source/Tailor matched; old generic
  runtime/Bakery needed +6.402237,+12.217735 before T. Remaining L2 attachments
  including FX anchors transformed, variant differences preserved.
- Updated exact Level2 shared blends in place; new Tailor11, Bakery09,
  FashionHouse13, Cafe01 masters under requested BAKERS/TAILORS folders.
- Oven_v2+two peels, fitting, two counters+brewing+pastry now main geometry.
  Both AST variants updated; pantry/reusable props stay attachments. Hidden old
  Bakery oven removed; Bakery_2 missing state references restored. Cafe new
  bespoke GEO/root/armature and attachment owners use CSC_BAKERS_Cafe. Bakery
  PIL also gets its own export root. Avoid inherited shared-kit names because
  the installed export button writes files using the armature name.
- Cobble rectangle replaced with 178v/320t fitted subdivided support (~36% less
  area), reused painted stone surfaces, matched B/H alpha; square/rectangular
  sources+exports installed. All TEX now point to current variant PNGs; rectangle
  previously watched obsolete single-decal B. No arbitrary culling changes.
- Henno's follow-up rejects faded/cut half-stones and requests more stones near
  road03. Final alpha follows whole-stone cells inferred from existing height-map
  grout, with only3px grout AA. Front/right target comes from red annotated render.
  Shift UV origin(-.015,-.10), retaining density, to fit complete front courses
  previously beyondV=1. Height alpha identical. Backups stone-edge-revision/;
  l2_stone_edges.py prepares/publishes this dated revision. No generic rerun.
- Later correction: NO stones on road, smaller stones for BOTH variants.
  l2_smaller_cobbles.py lays intact source-painted donors at .75 median linear
  size, all maps share donor transforms. Reject whole cells touching actualroad03
  alpha>=.35 plus.75worldunit clearance; onlygroutAA. UVoriginunchanged fromprior.
  .05 threshold trial overtrimmed because road has a faint halo well into grass;
  .35 follows visible dirt edge, inspected in actual road03 context render.
  Current report/backups: smaller-stones-road-clearance/. Prior outward-expansion
  previews are superseded. Check every visible alpha pixel against roadmask.
- Latest: user rejects trapezoid/baked-perspective shapes; wants SQUARES and
  RECTANGLES, half-stone staggered rows, PARALLEL TO FRONT FACADE. Current tool
  l2_orthographic_cobbles.py rectifies existing interior stone paint into true
  orthogonal masks: square4.492^2, rect7.906x3.953world. 2048square atlases map
  to184squareworld with equal texel density and rigid42.369667deg source-frame
  UV rotation from measured facade direction. No shear/bakedperspective.
  B/Halpha matched, H/Nbevel regenerated. Current backups orthographic-running-bond/.
- Live ArtDef test-wrapper reference replaced by direct Tailor to avoid double
  movement. Wrapper file/XLP retained as historical test; don't reuse on moved art.
- L2 cameras/target/light directions transformed together. All1590 vertices
  registration error <.000412px@1024; original view visually preserved.
- 16 installed saved-source validators and actual CN6 source exports pass;
  all18 position/N/T/B/UV floats agree <.000009. Native55meshes/11geos pass,
  phantom unused decal bonebindings removed and GEO counts corrected. Eight
  whole Worked assemblies agree material/emission and geometry <.000557 (tiny
  preexisting FashionHouse2 fitting rounding).80 state resolutions pass.
- 12 renderer tests and fixedcamera regressions pass. Initial tests hit Windows
  temp-folder permissions; rerun with real temp access passed. No test failures remain.
- AE watcher regenerated SqB DDS/TEX/cache: exact RGBA/alpha verified; source
  links/timestamp metadata permitted, required dependencies preserved. Installed
  Cafe standard renderer prepare-only pass.16 installed sources reopened pass.
- Outputs/backups Desktop/Codex/L2-placement-20261025. Native build/cook/live AE
  viewport/game not tested. User owns in-game river check. Source tools dated;
  don't blindly replay installation over subsequent AE edits.

Exporter lesson: saved custom split normals alone are not preserved by the
installed CN6 exporter's triangulation. Its supported VERTEX_KEYS group and
originalTangentsBinormals mesh dictionary preserve the exact native shading frame.
Put VERTEX_KEYS first (all vertices assigned) because that exporter indexes the
vertex's weight list by group index. Static validator excludes this metadata group.

AE follow-up: Henno's screenshot still shows older dense/slanted paving with a
soft rounded outline. Saved Tailor AST points to current Sq material; canonical
FGX/GEO and B/H DDS/TEX still match the installed revision. Actual DDS is2048square
with12levels. AE PID1328 began14:16 Warsaw; final files were installed14:27.
Stale live-preview data is a hypothesis, not a confirmed diagnosis. Computer Use
denied app access ("not approved to use asseteditor"); no UI refresh was performed.
Henno fully exited/reopened AE and confirmed "It now matches". The stale live
preview caused this mismatch; the final facade-aligned paving is now visually
confirmed in AE by Henno. This does not constitute an in-game river test.

Subsequent front-road extra-course request: l2_front_course.py reuses the same
orthographic paint/UVs and adds exactly one shared-edge neighbour ring where
the existing .75-unit/.35-road-alpha constraint permits it, front y<-55 and
within10units of road. +8 square/+7 rectangular stones; no existing alpha removed.
Matched B/H silhouettes. Geometry WAS required: added pixels extend outside
the old support, up to4.024square/7.637rect world units. Current mesh178v/320t,
area14192.603 vs13911.410prior; support +2%. Backups/reports front-road-extra-course/.
This newest course has context/data validation; earlier AE confirmation applies
to the preceding facade-aligned pass, not yet this extension.
