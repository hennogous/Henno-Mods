# Modern Bakery first proposal — 28 October 2026

## CURRENT: AE installed from final v3 save

28 Oct: user authorized install, paused to fix geometry, then resumed. Used v3
delivery review saved20:02; only two bargeboards changed. Original untouched.
New masters Bakery/modern/revision-04-ae, Level2/modern/revision-06-ae.
Rebaked Building AO with existing UV2; rigidly registered building/shelter and
AST placements to historical district frame (inverse fitted normalization).
DO NOT apply registration again. Props keep local pivots. Four zero-area gable
tessellation triangles omitted only in native output: main1090/588, shelter544/272.
Installed CSC_BAKERS_Bakery_Modern and _2 (standard plus truck),9 model/prop masters.
All preexisting ASTs exact. Initial one prop each; AE owns placement thereafter.
Modern era priorities2/3 preserve Service rule; no gameplay gate changes.

Atlas buildings r012 / propsr007. User edited Current B during publication and
explicitly said keep newer texture; exact PNG archived in r011. His export had
an empty grey Bakery quadrant. r012 restores ONLY that quadrant from r010;
every RGBA pixel outside it preserves his edits. DDS/new master snapshots use
merged r012; human-texture-merge.json verifies. AE auto-reimport race
checked/backed up, testedDDS restored. AssetCloud all new entries detected
automatically, no cache repair. Native9/saved-source/state/dependency/cook pass.
Fixed-L2 ASTrenders inspected. Historical L2CON+PIL reused temporarily; no modern
state kit authored. UI access denied by computer-use permissions; no native
viewport/glass/game/terrain claim or game deployment. Evidence Desktop/Codex/
modern-bakery-ae-20261028. Durable modern-bakery-first-version.md updated.
Propsr007 preserves later human mill colours in cells0/1/9 (Bakerycellsunchanged).
User also saved Wind_Mill_Modern_2.ast after installation; preserved as external
edit. final-verification.json passes and distinguishes this from publication.

## Previous: v3 from human-edited review, height/interior trial

Input is human-saved revision02 CSC_BAKERS_Bakery_Modern_2_Review.blend (19:29).
Preserve its dormer/chimney mesh edits/placements; don't rebuild from v2generator.
New Bakery folder revision-03-height-interiors; reusable L2 revision-05-height-interiors.
Ridge113->109.044 historicalmax; upperwallshortened, roof/dormers/chimneyrigidlylowered
3.956. Chimney darkmouth was orphaned atoldposition: reconnected toeditedcap.
Signbottom44->35.328 matchinghistorical. Fascia/soffitcloseeaves; gablecrossbeams-1
fix roofpenetration/AOdots. Oven/rack/trays/truck/workshop source geometry+placements
verifiedunchanged. Ground/foundation and shortreturn retained. All prior sources kept.

Nine shallow paintedbread trays replace identicalloaves: props36–38 round/long/mixed.
Aligned authoredheight+contactmicroAO; display612->432exportverts. Room-boxtrial in
groundwindow/door only: actualwallholes,1gap+6depth, paintedlargefaces incells11/12/15.
O lowglass/highG inexisting6/14, whiteOelsewhere; Eupperunchanged. Cyclesalpha is only
preview of documented nativeMSAAcoverage, no physicalrefraction or runtimeclaim.
Depth works but darker than flatwarmB atgamescale; showcomparison, don'tclaimbetter.

AO Building+Display freshlybaked B/Ndisconnected. Humanimportedhistoricalmesh was
viewporthidden butrenderenabled; exclude fromAO/renders, leave originalsourceintact.
Newreviewcopies stripped referenceonlymesh. Savedvalidators/native8assets pass.
Main1090/592, shelter544/272. Evidence Desktop/Codex/modern-bakery-v3-20261028.
No AE/runtime/atlasCurrentpublication. Durable report modern-bakery-first-version.md.

## Earlier: v2 built from selected C

User selected C and requested short shelter return, historical silhouette/footprint,
electric oven + stacked bread trolley under cover, delivery truck in `_2`.
Implemented prior notes: two missing left upper windows, compact dormers, warm
ground B and upper-only E. Main envelope unchanged. Shelter ends Y=-19, ten past
front Y=-29; no full side/back strip. Oven45deg at(-34,-46), rack(-43,-59).
Truck(-79,-64) only in `_2`, standardprops retained. Review proposal, no AE edits.

Current Bakery folder: BAKERS/Bakery/modern/revision-02-concept-c.
Current reusable: Level 2/modern/revision-04-bakery-corrections.
Both under Desktop/Working Files/3D Art. Saved masters authority after human edits.
Portable candidate textures: props32–35 truck; buildingStage3 cell14 warmwindow,
cell6 warmdoor. B/N registration, grain alignment, isolated AO bake corrected.
Published r009/r005 unchanged. Eight masters + assemblies validators pass;
all eight native geometry/UV/tangent/weight round trips pass, maxerror<4e-6.
Evidence Desktop/Codex/modern-bakery-v2-20261028. No game/AE/runtime install.
Historical fitted footprint is approximate reference; no exact native parity or
road-clearance claim. Durable report project/docs/art/modern-bakery-first-version.md.
Everything below is earlier history, including the concepts-first restrictions.

## Earlier: concepts first, first model not accepted

User corrected BOTH reusable L2 + Bakery: restore missing upper windows on left
long facade (supersedes prior blank-wall instruction), dormers closer to original
concept, warm ground-level glazing painted into B; E adds upper-level lighting.
Work-area layout open. Oven front should be45degrees to building OR same direction
as front door; extension may change to make that plausible. `_2` explicitly adds
small Bakery delivery truck loading for adjacent Market, retaining standardprops.
User wants several concept images FIRST. Record notes, do not change3D/atlases/AE.
Concept output: Desktop/Codex/modern-bakery-layout-concepts-20261028.

Delivered THREE ImageGen paired boards (standard left, Market-delivery `_2` right):
A compact chamfered45-degree corner bakehouse; B right-facing oven parallel to
entrance wall; C open loading porch with truck backed towards tray racks. Each
adds only one small cream/green Bakery delivery vehicle in `_2`. Current drawings
restore two long-wall upperwindows and warm groundglazing. User selection pending.
Full prompts/paths in concept-manifest.json. Image details remain illustrative:
A standard sign drifts from pointedhex (existing sign remains authority), C exact
oven yaw needs blockout confirmation, all roadclearance/paving unvalidated. No
mesh/atlas/AE edits were made. Do not treat any option as selected yet.

User asked for first modern Bakery using reusable L2 and approved concept.
Current authoring package: `3D Art/BAKERS/Bakery/modern/revision-01-sheltered-bakery`.
Review scene `CSC_BAKERS_Bakery_Modern_Review.blend`; separate oven, bread display,
bread rack, tray stack and Bakery sign masters. Existing flower boxes retained.
Actual saved L2 r03 main/workshop appended, source hashes and decoded geometry,
normals/UVs/topology checked identical. Do not redesign architecture to restore
superseded concept windows. Historical openings/forward lean-to are explicit.

No AE/current atlas/ArtDefs/game edits. Candidate merges building r009/props r005
with L2 TR + props24/25 candidates. New ImageGen surfaces26–31; independent AO
rectangles documented. Existing regions preserved. First version only; road
placement/state integration remains future work, not verified.

Oven inside bay at(-34,-63,0), display(10,-37,0), rack(-45,-75,0), trays(-20,-73,0).
Sign uses existing point-up/down hex geometry with new breadface. Props working
identities pending review before library publication. No sacks added in this draft.
No procedural B painting. Explicit measured relief, baked AO normals disconnected.
First visual checks fixed repeated bread-side scoring, exposed the oven, and removed
redundant nearly coincident oven/tray overlays. Actual angular shapes in the neutral
view are the rack's cast shadows; isolated oven distinguishes them from defects.
New normal derivatives corrected for actual128px input (older helper hardcodes512,
amplifying the requested relief4x). Full scene3776exportvertices, advisoryoverage;
allinstancescounted. Separateprops236/612/602/120/132vertices.
All images no emission; concept comparison attached on dark.

Evidence `Desktop/Codex/modern-bakery-v1-20261028`; source scripts
`project/tools/art/modern_bakery`; durable handoff
`project/docs/art/modern-bakery-first-version.md`. Use saved masters after user edits.

- 28 October Bakery interior lighting installed: buildings r013 plus new
  CSC_Buildings_Emissive/r001. Brighter ImageGen B cells11/12/15 only; fixed Stage3
  room UV3 slots8/9/10, black sentinel12. Bakers historical E256 and modern E512
  now separate; historical DDS and modern upper-window pixels preserved.
  Existing masters stay revision06-ae/revision04-ae, already registered. Native
  UV3-only change60vertices; AO/shape/AST/ArtDefs/XLP unchanged. Cook/saved-file
  checks pass; AE closed so cache registered with backup. Night native intensity
  awaits human review. No Service variants or game deployment. Read
  project/docs/art/quarter-emissive-atlases.md and evidence Desktop/Codex/modern-interior-lighting-20261028.

- 28 October historical placement match: both modern Bakery AST displays uniformly
  scaled0.731258 and centred on historical stand/table; `_2` truck uses historical
  cart position/orientation, scale unchanged. Other props/geometry/textures untouched.
  Saved-AST day/night review in Desktop/Codex/modern-bakery-placement-20261028.
  AE assemblies own these changes; do not copy stale review-blend placements back.

- 28 October oven E installed: shared props r008 expands existing
  CSC_Props_Modern_01_E from black16 to256,8x8 grid, oven windows only in cell26.
  UV3 changes4 native oven-front vertices; 17 other consumers clear of cell26.
  Preserve black cell56/global(.02,.02), no B/N/AO/geometry/AST placement edits.
  Master and both review blends updated; saved/native/cook pass, native brightness
  still awaits review. Evidence Desktop/Codex/modern-oven-emissive-20261028.

- Oven-glass correction,28 October: props r009 supersedes r008. Henno wanted
  emission across the glass, not mainly the bread. Cell26 now has a warm linear
  radiance floor(.18,.075,.021) across both full pane masks, plus0.32 painted detail.
  Frames/handles remain black; all other atlas pixels preserved. Texture-only
  update, DDS validated and night preview inspected. No geometry/UV/AST edits.
  Evidence Desktop/Codex/modern-oven-glass-emissive-20261028.

- 28 October modern L2 active roof palette: buildingsr014, Stage3 B2/3/8 now
  historical active yellow-green roof/darker-green ridge andbarge trim. Preserve
  cream window frames; no geometry/normal/AO/AST changes. Retain atlas colour until
  human recolours. Daytime historicalcart/moderntruck comparison attached, wider
  matched L2 camera job only. Evidence Desktop/Codex/modern-bakery-active-roof-20261028.

- 29 October modern L2 CON+PIL installed in reusable L2 and both modern Bakery ASTs.
  Main only: no extension/shelter/props/interior/floor. Source Level 2/modern/CON+PIL/
  revision-01/CSC_Level_2_Modern_CON+PIL.blend, already district-registered.
  Open thick masonry, exposed grain-aligned timber, 30-unit foundations. Scaffold
  Construction only; shell CON+PIL, native burn binding. 1462+588=2050 vertices.
  Buildings r015: only AO [1024,512,1536,1024] changed; painted maps and existing
  AO untouched. State masonry sampling matched worked after initial review caught
  oversized brick. Saved/native/all-state/AO front-back/cook pass; AE cache updated.
  Preserve AE worked/prop/decal rows. No live viewport/game/deployment claim.
  See project/docs/art/modern-level2-con-pil.md; evidence modern-l2-states-20261029.

- 29 October bread display depth fixed and re-exported: width35.1004 and height25.594
  unchanged; totaldepth13.1626->31.0520, counter24.1767 matches historical table.
  Rear anchored; posts and painted loaves not stretched, two tray rows per shelf,
  648nativevertices. Master and two Review blends updated in revision04-ae.
  Propsr010 changes only own AOcell512,512..768,768; all B/N/G/M/E and other AO
  pixels preserved. Native/saved-file/cook checks pass; all ASTs byte untouched.
  Follow-up resolved: user explicitly approved moving the alternate trolley clear.
  Only _2 CSC_Attach_Rack X/Y changed to -17.310166/-7.137929, retaining rotation
  and scale and leaving a 1-unit gap. Standard trolley unchanged. Exact XML diff
  and pre-move backup are in the same output package.
  Evidence modern-bakery-display-depth-20261029; comparison image in that folder.
