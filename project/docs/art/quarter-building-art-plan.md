# Quarter building art plan

> **Documentation audit — 2026-09-12: Current.** Records the user-agreed reusable kit, roof/beam differentiation, visible chunky occupational props, storage/crane, Industrial Era work and later cultural variants. Open choices are explicitly left open; existing concept studies do not authorize replacing the kit.
> Classification: Art planning. See the [full audit](../DOCUMENT-AUDIT.md).

**Agreed direction: 12 September 2026.** Henno's existing building kit is the foundation for CSC's Quarter buildings. Quarter-specific colour and substantial occupational props will give each building its identity. The base models are essentially finished; any architectural refinements should be minor and deliberate.

This document records the agreed production approach. Individual prop compositions, recolouring methods and later additions remain to be worked out. Earlier generated images are concept studies, not permission to replace the kit with redesigned buildings.

## Why a shared kit

The [Supply Chain Framework](../../../docs/content/design/supply-chain-framework.md) uses recurring mechanics across the eight [Quarter designs](../../../docs/content/quarters/index.md). Shared building families can make those roles recognisable without opening a tooltip:

| Kit family | Supply-chain role | What the scene should communicate |
|---|---|---|
| Level 1, including the smaller-shelter variant | Stage 2: intermediary goods | Base materials being processed into inputs for the later buildings |
| Level 2 | Stage 3: consumer goods | Everyday finished goods, their manufacture and supply to general customers |
| Level 3 | Stage 4: specialty goods | Specialist production using intermediary goods and specialty materials for selective customers |

These are mechanical roles, not three sequential upgrades to one building. Stages 3 and 4 both depend on Stage 2; Stage 4 does not require Stage 3. Preserve recognisable differences between the families across Quarters and eras. Existing function-specific buildings such as the mills can retain their distinct forms.

Architecture communicates the family, roof colour communicates the main yield, and props communicate the industry and the activity at that stage. Predictable placement on the Quarter base reinforces this. Modest rotations and storage extensions can vary the composition where they expose the work and fit the existing layout.

## Base models

Use the actual Blender sources as the basis for concepts and prop scenes:

| Source beneath `Working Files/3D Art/` | Role |
|---|---|
| `Level 1/CSC_Level_1.blend` | Level 1 with full side shelter |
| `Level 1/CSC_Level_1_S.blend` | Level 1 with smaller side shelter |
| `Level 2/CSC_Level_2.blend` | Level 2 building |
| `Level 3/CSC_Level_3.blend` | Level 3 building |

The supplied Mac source root is:

```text
/Users/henno.gous/Library/CloudStorage/GoogleDrive-henno.gous@gmail.com/Other computers/My PC/Working Files/3D Art/
```

The corresponding shared Windows workspace is `C:\Users\Shadow\Desktop\Working Files\3D Art\`. Verify the active host's paths before working. Storage building sources will be identified when that work begins.

The initial inspection opened all four files successfully. They have UV1, UV2 and UV3, and 402–558 source vertices per building; these are not exported counts or a final prop budget. Level 3's saved Blender materials produced dark patches and strong window emission in the review renders, so check those bindings before judging or changing its surface finish. Those renders did not establish in-game appearance.

Use separate editable working scenes or versioned copies for variations. Preserve the original kit files as the reference. Possible small refinements include ridge treatment, framing and opening readability; this plan does not call for a wholesale remodel or universal changes to roof pitch and proportions.

The bases are intentionally **off origin**, already positioned for their district slots and road relationships. Preserve their authored placement and orientation when appending them into a prop scene; move review cameras to frame them. Temporarily append the matching road layout from `Working Files/3D Art/Quarters/` to check entrances, prop clearance and work/loading routes. `CSC_ALL_Classical_Base_05_Road_Decals.blend` is an identified reference. The layouts share the same network, differing in how much is paved versus dirt path; keep that distinction in context checks. Exclude the temporary road geometry from building-only renders and export.

### Level 2 placement standard — 18 September 2026

Henno approved the current Tailor Worked footprint as the reusable Stage 3 standard.
The shared sources `Level 2/CSC_Level_2.blend` and `Level 2/CSC_Level_2_CON+PIL.blend`
now use that placement. The Tailor-specific shared CON+PIL source also aligns its
building and lean-to with Worked; scaffolding and the fallen sign follow the
building. Reuse the updated authored placement directly, without reapplying the
older Tailor +6 Y setback. This changes the starting points for future work; it
does not migrate previously authored Quarter buildings automatically. Source mesh
data and UVs are preserved. Windows export and runtime checks remain separate.

## Colour system

Retain painted material detail, value variation and shading when recolouring. Roof surfaces and main roof beams need separately controllable masks or material regions.

| Quarter | Roof direction | Main roof beam direction |
|---|---|---|
| Bakers' | Established Food green | Retain established treatment unless a later concept calls for a change |
| Tailors' | Culture purple-pink | To settle with the concept |
| Apothecaries' | Science blue | To settle with the concept |
| Stonemasons' | Production burnt orange | Grey |
| Carpenters' | Production burnt orange | Brown |
| Blacksmiths' | Production burnt orange | Black |
| Goldsmiths' | Gold yellow | Distinct from Brewers'; exact colour undecided |
| Brewers' | Gold yellow | Coordinate with Goldsmiths'; exact colour undecided |

Grey, brown and black beam colours are the agreed way to differentiate the three Production Quarters. They refer to the main roof beams, not necessarily every timber or structural component. Keep sufficient tonal variation for dark beams to retain their shape.

Henno referred to the Jewelers' in this discussion; the Quarter's current canonical name is Goldsmiths', with the Jeweler as its Stage 4 building.

The recolouring workflow is still open: the assistant may generate the variants, or Henno may use the existing GIMP path templates. Compare a representative result and choose the reliable method before rolling it out. Do not replace the GIMP templates merely to automate the task. Exact colour values will come from the established textures/templates and reviewed concepts.

## From concept to Blender prop scene

1. **Read the building's Quarter design.** Identify its inputs, processing activity, output goods and supply-chain stage. Use the framework for the common pattern and the Quarter document for thematic differences.
2. **Frame the actual base model.** Choose Level 1 or Level 1 S where applicable, and retain the authored proportions, footprint and attachment conventions. Use a consistent view to compare variants.
3. **Create concept images for both versions of one strong composition.** Start from Henno's supplied building image or a render of the applicable base model, then dress it with its Quarter colours and occupational scene. Iterate that composition with Henno; develop alternatives only if requested or needed after review. Provide a concept image for the standard version and another for the expanded version, with matching camera/framing for comparison. Henno reviews both before detailed prop construction; an already accepted concept remains valid.
4. **Build and place the props in Blender.** Append/import the applicable base into the working blend and create editable, named prop meshes matching the accepted concept, first checking the large forms and composition, then developing materials and selected detail. Reusable equipment and storage props can be shared where appropriate.
5. **Review the complete scene.** Send renders with the base included, checking the intended elevated game view and useful rotations, including at normal play distance. Henno may reposition props in Blender; continue from his edited scene. Adjust props and placement before deciding that the base architecture needs alteration.
6. **Prepare the asset for the existing export workflow.** Deliver base and props together as a building asset while retaining separate named meshes/groups for material assignment and state visibility. Keep each significant prop as its own editable mesh, separate from the base, and preserve independently controlled groups through export. Smaller props may be grouped where their materials and visibility match. Include separate pillaged prop decal geometry. Deliver the editable scene, export-prepared version, external textures, state review images and geometry/material report; complete export and in-game checks through the established pipeline for the production asset.
7. **Render final icon and strategic-view inputs.** After placement review and Henno's edits, render the latest scene for the existing 2D pipelines. Use the separate Wind Mill icon and SV references under `Working Files/2D Art/Quarters/Bakers/` and its `StrategicView/` subfolder. For SV, match Henno's perspective correction that makes outside walls more vertical and less inward-convergent at the bottom. Preserve the manual directional-shadow handoff: blue-ish colourization at about 70% opacity with light from the top left. Full source filenames and current command sequence live in the CSC production conventions; consult [Henno's commands](../workflows/commands-cheatsheet.md) and the live scripts before execution.

### Shared prop materials

Create a **fresh shared prop atlas library**, aiming for **fewer than five shared prop atlas materials across CSC art collectively**. Reuse common wood, stone, textile, metal and other surfaces. The legacy `Working Files/3D Art/Textures/CSC_Atlas_Props_B.png` is a coverage/style reference; preserve it for existing assets, but give the new library its own layout and remap reused props accordingly. This target does not replace the building atlases and independent AO/emissive layouts.

Plan the fresh layout around the first normal/expanded scene and likely cross-Quarter reuse. Keep new regions stable once mapped, adding missing surfaces as actual scenes require them. Do not create all four sheets in advance or migrate unrelated existing assets during this first scene.

Ovens, furnaces and other emissive equipment need an `_E` map through UV3. Prefer one shared B/N/G/M set for these props and a shared emissive sheet with lit regions and padded black for unlit faces. Reuse compatible material instances; separate meshes do not require a unique material per prop. Avoid proliferating surface/emissive combinations. AO remains geometry-dependent through UV2, with asset overrides checked during integration. The existing `CSC_ALL_Props` and `CSC_ALL_Props_E` materials demonstrate shared surface bindings; the new library still uses fresh textures.

### Expanded art

Provide normal and expanded versions where the design calls for an adjacent-service story. Use extra and/or different props while retaining the base, placement and material library. Record the service, recipient, full activation conditions and visual prop changes for each building. Each complete variant remains subject to the existing geometry budget.

**Alternate selectivity under review — 19 September 2026:** Henno raised that small prop or costume swaps can disappear at game scale and tell too little story to justify another asset. Explore an alternate only when its service suggests a strong, legible change in silhouette or activity, such as the Joinery boat; do not treat a generated pair as approval to build both. The earlier expectation to provide an expanded version for every eligible service is being reconsidered. Confirm the production choice after reviewing each candidate at gameplay scale, including its extra geometry and asset cost. The Fashion House theatrical studies are exploratory candidates, not accepted alternates.

**Fashion House direction — 24 September 2026:** Henno chose to proceed without an alternate version for now. Continue the standard luxury-atelier concept and add cobbles in the forecourt between the building and the road. This is an explicit building-specific paving request, not a new default for other buildings. Ground-flush cobbles reach the inner road edge. Henno subsequently rejected the cutting-table setup as too similar to the Tailor. The current replacement proposal, requested for visual review, is a standing cheval mirror with a third dress form carrying a half-finished brocade gown, a low stool and an open trims case; preserve the finished garment displays and sheltered stock. The fitting-scene image remains a proposal, not an accepted modelling layout. The theatrical study is parked; do not build or wire an alternate unless requested later.

**Fashion House production requirements — 24 September 2026:** Henno tentatively supports the fitting-scene direction and particularly likes the garments displayed inside the building; preserve that feature in the model plan. Final clarification: the ivory gown and claret coat displays stay close to the building as fixed scene geometry sharing building height; interior display garments are also fixed and may be very low poly. Henno’s final clarification combines the mirror and unfinished fitting gown into one Fashion House-specific asset with one ground pivot, so their terrain-height adjustment cannot diverge. No shared-library reuse or CSC_ALL publication is implied. Proceed with this combined asset and the scene blockout. This supersedes the earlier proposal for three reusable dressed-form assets. Extend the existing shared prop atlas from canonical `CSC_Props/Current`, including a very glossy mirror-surface patch; do not create an independent Fashion House atlas. Reuse existing cloth/wood regions where suitable and preserve occupied rectangles and static runtime filenames. Create a new versioned atlas release as part of delivery, including authoring patches, companion maps, AO sources/allocations, manifests, hashes and updated `Current`/`CURRENT.json`. Live pointer checked on this date: `2026-09-18_Shared_01_r007`; the next release is expected to be r008, subject to rechecking Current before promotion. Review the mirror material in the destination renderer; the concept's garment reflection is illustrative, not an established runtime feature.

**Fashion House model review and atlas release — 24 September 2026:** The first editable model is in `codex-outputs/CSC_TAILORS_Fashion_House/revision-01`: fixed frontage and low-poly window garments, one combined `CSC_TAILORS_Fashion_House_Fitting` asset with a single ground pivot, and a fitted cobbled forecourt. Blender/CN6 decoding measures2144 vertices for building+props and56 for paving (2200 total). Published canonical `2026-09-24_Shared_01_r008` adds only polished mirror surface slot49; all existing surface regions, both AO pages and emissive were preserved and hashes verified. New layout-dependent Stage4 AO/PIL and destination/game checks remain pending model review. Henno is correcting the green Level3 roof portions in the Tailors building atlas.

**Fashion House user-layout refinement — 24 September 2026:** Henno moved the fitting assembly, seat and case in revision01; those placements are authoritative. He raised this building’s limit to2500 exported vertices, requested additional library stock and geometry AO, and asked for two new cloth colours with no teal (teal belongs to the Tailor). Revision02 preserves all prior vertex positions, object/parent transforms and pivots; it adds five library-stock instances, simple form necks/stems and coat lapels. Claret and sapphire occupy Shared01 slots25/26; new fixed-display and isolated fitting-assembly AO occupy Tailors Stage4. The complete scene including cobbles is2444 exported vertices. Inward polygon winding was corrected on six pre-existing parts and one new lapel without changing vertex positions or connectivity. Canonical r009 is the corresponding atlas release; old surface regions and unrelated AO are preserved. Blender/CN6 and mapped AO were checked; PIL and destination/game checks remain. This2500 cap is Fashion House-specific.

**Fashion House window and prop-density revision — 24 September 2026:** Henno rejected the timber window display cases and asked to use his existing building-atlas opacity map with the garment forms inside the building. Revision04 removes the three cases, restores the original window polygons/UVs and binds `CSC_Atlas_O` unchanged. It adds six library instances: two textile bales, a crate, two folded cloth pieces and a claret bolt. Existing surviving geometry and placements are preserved; total including cobbles is2480 exported vertices. The Blender cutout preview uses threshold0.8; destination coverage transparency remains to be checked. Props release r010 refreshes only fixed-display AO; all surface maps, the fitting cell and other AO stay unchanged. The Tailor world-light setup is retained in Review and Export.

**Fashion House luxury direction — 24 September 2026:** Henno judged the added stock clutter too low-budget and approved a more deliberate presentation: remove bales/crates/rolls, use a scaled wide library workbench as a low display plinth for the exterior gowns, add a claret runner with restrained gold border, and upholster the fitting seat. Revision05 retains the building, window opacity, mirror/gown and seat controller placements; only the exterior garments rise onto their platform. Ivory dominates, claret is the signature colour and sapphire is confined to the fitting gown. The runner is a ground-projected decal and the upgraded seat has its own ground-pivot master. Total including all props/paving is2434 exported vertices. Atlas r011 updates only Fashion House fixed/seat AO inside the prior fixed half-cell; surface maps and mirror/gown AO stay unchanged.

**Fashion House boutique composition — 24 September 2026:** Henno clarified that the shelter is storage; the exterior display should communicate the salon inside. He raised the complete-scene cap to3000 exported vertices for distinctive composition, not incidental detail, and requested better window garments. Revision06 starts from his latest saved revision05 placements and exact updated Tailors B texture. It uses fuller ivory/sapphire gown silhouettes, a narrow claret coat, a scissors sign and three dimensional window outfits (coat, full gown, belted dress). Two uniformly scaled library crates, two folded cloth pieces and one bolt occupy the shelter. The invalid nonuniformly scaled workbench from revision05 is removed; its replacement is separately authored fixed plinth geometry at unit scale. All surviving user object transforms and the original building/glazing geometry are verified unchanged. Counts: fixed building2269, combined fitting309, seat246, runner20, cobbles56; total2900. Canonical atlas release `2026-09-24_Shared_01_r012` rebakes the fixed-display and mirror/gown AO cells; seat AO, every unrelated AO region and all shared surface maps remain unchanged. Proper world lighting is retained. Blender/CN6 checks pass; PIL and destination/game appearance remain unverified.

**Fashion House court courtyard — 25 September 2026:** Henno approved modelling the court dressmaker concept (historical concept01). Revision07 removes the forecourt platform/runner and broad cobble apron. A shallow open ivory arbour, claret curtain, folded screen and broad court gown establish the fitting area; a narrow path leads to the door. The mirror now shares its ground pivot with the ivory gown; the blue gown joins the fixed frontage. Native garden props are one `Shrub_Long`, one `Tree_C_Sm` and three `Shrub_Round_Single_Flowered_White`, with source geometry, UVs and component transforms verified unchanged. All placement scales are uniform. Counts: fixed2151, fitting311, courtyard203, chair54, plants261, path16 = **2996** intact vertices. Separate combined base-plus-prop PIL decals have60 vertices and a full ruined-building preview. Canonical atlas release `2026-09-25_Shared_01_r013` updates only the Fashion House AO family cell; other pixels and all surface maps remain unchanged. Base building, glazing, roads, storage and current user roof texture are preserved. Blender/CN6 verification passes; FGX/Asset Editor, terrain and game appearance remain pending. Editable delivery: `codex-outputs/CSC_TAILORS_Fashion_House/revision-07-court-courtyard`.

**Fashion House garden revision — 25 September 2026:** Henno judged the initial garden too weak. Revision08 replaces the scattered shrub/specimen arrangement with a low curved clipped hedge, three smaller white-flowered bushes in a connected border, leafy planting at the arbour foot, and a shallow climbing canopy/vines integrated into the existing Courtyard master. The hedge is a new Fashion House-specific Garden_Border master using the native foliage material; the canopy is explicitly authored derivative geometry, not an edited native asset reference. Four ground plant placements remain exact native references. The full intact count is2997: fixed2151, fitting311, courtyard283, hedge35, chair54, native plants147 and path16. All placement scales are uniform. Non-garden geometry/UVs/placements and existing textures are preserved. The r013 atlas remains unchanged; garden surfaces reuse native foliage resources. Updated PIL layout and Blender/CN6 checks accompany `codex-outputs/CSC_TAILORS_Fashion_House/revision-08-garden`; destination review remains pending.




**Henno's latest direction (12 September 2026):** show expanded art when the requirements for establishing the adjacent service are satisfied, including its technology/civic unlock. His example is a boat frame at a Joinery next to a Lighthouse once Shipbuilding is researched. For the Textile Workshop, the current design specifies Naval Tradition, adjacency to an improved Base Material, and an adjacent Harbor containing a Lighthouse for the Dockmaster service. Sailmaking is the agreed visual story, consistent with the earlier textile study's natural-canvas variant.

The alternate-art fix was pulled at Henno-Mods `11595de` on 12 September 2026. Source inspection confirms that the Textile Workshop property is producer-owned and shares the full Dockmaster Service gate, including Naval Tradition, material supply and an eligible Lighthouse customer. No new gameplay implementation was needed; runtime behaviour was not retested in this session. See [dynamic art properties](dynamic-art-properties.md).

### Pillaged prop representation

Provide separate **pillaged decals geometry**: major intact props disappear during `Pillaged` and are represented by damaged/scorched prop decals at their locations. Keep intact props and replacement decals in independently controllable mesh groups. Preserve the base building's existing pillaged treatment. Include the matching existing base pillage decals with the new prop decals in the delivered decal geometry and review; retain their placement/UVs and keep base versus prop groups identifiable. Avoid duplicating the base decals during asset integration. These runtime decals are separate from SV sprites and temporary road-layout geometry.

Plan the decal representation for both normal and expanded scenes; share it only where the footprint and damaged-prop story fit. Review the full building in intact and pillaged states, checking visibility, emission, decal placement and z-fighting. Include decal/material counts, each state's visible geometry and complete delivered totals in the report; the existing budget remains unchanged. The CSC production conventions carry the export/group checks.

### First production scene

**Latest placement revision:** Move the normal Textile Workshop loom fully out from under the side roof and put stored crates/bales under that roof instead. Retain rear storage and include the existing Level 1 small-base pillage decals with the prop decals.

**Current concept revision:** Keep the road visible, dye vats, a modest group beside the door and one or two goods visibly inside, but reduce the crowded frontage from revision 02. Arrange distinct processing stations with operator space and clear walking routes from the road to the door, loom and other work areas. Empty working/circulation space is part of the composition. Move bulk storage to the rear: stacked crates and bundled goods against the back walls/corners, with those quieter views considered even where the front concept hides them. Avoid a continuous row of props between the building and road.

The expanded scene is now a **wholesale sailmaking transformation**, superseding the earlier retain-and-adapt composition. Canvas production should dominate the loom, worktable, drying/storage and goods, with conspicuous sailmaking cues. Produce revised standard and expanded concept images for review before building the scene; the generated revision is not accepted until Henno reviews it.

Henno selected the **Tailors' Textile Workshop**. Use `/Users/henno.gous/Play/codex-outputs/textile-texture-pass-02` as the earlier visual/prop reference, including its colourful standard cloth and natural-canvas sailmaking distinction. Its bespoke architecture and dedicated atlas do not replace the agreed Level 1 kit and fresh shared prop library. Inspect reusable props and adapt their placement to the actual kit and roads. The old complete export measured 1,895 vertices; that is historical evidence, not a budget measurement of the new assembly.

**Connected drying-frame concept — 30 September 2026:** An exploratory normal Textile Workshop image attaches the coloured cloth-drying rails to the shelter's outer post and beam while retaining the exposed loom, dye vats and sheltered stock. This is a concept for comparison with the current freestanding frame, not an approved Blender change.

### Prop direction

- **Chunky, visible, activity-led props do the heavy lifting.** Exaggerate identifying shapes such as the loom, mortar, vat, furnace, workbench or stockpile so the profession is readable at game distance.
- Show what the building does at its particular stage. Raw fibre and broad cloth production belong to a different scene from tailoring everyday garments or making specialty clothing.
- **Standing rule:** place defining work equipment outside the side roof, visible from above, and use the sheltered area primarily for stored inputs, finished goods, crates or bales. Keep operator space and circulation clear. Apply a task-specific exception when the activity requires cover.
- Arrange props into meaningful groups for processing, inputs, finished goods, drying or loading, with gaps that keep their silhouettes readable. Do not fill every gap with small clutter.
- Keep entrances and working routes plausible. Large props should feel used and supported, not arranged as oversized ornaments outside an unrelated house.
- Give quieter sides and rear views considered storage or service details. Avoid adding exterior paving aprons or display plinths unless the particular scene calls for them.

**Herbalist concept direction — 30 September 2026:** Keep shallow drying shelves and hanging herb bundles integrated into the main stone wall left of the small shelter, with its square wall window fully open and visible. The wide workbench with a large mortar and pestle is the primary station in the middle of the front yard, completely outside the side roof. Extend the shelter's outer right-hand timber structure into a secondary three-tier herb-drying rack, with its trays and hanging bundles visible beyond the roof edge; it should read as part of the shelter rather than a freestanding frame. Put one basket of fresh herbs just right of the bench. Leave clear routes to the door and into the shelter, with operator space around the bench; keep every prop off the roads. Sheltered baskets/jars and live plants are subordinate. The editable layout was first implemented in Blender revision 04 for review; atlas/AO, PIL and destination-game checks remain. Both integrated racks and the newly authored basket count toward the bespoke budget; an existing Tailors basket includes fibre and was unsuitable for herbs.

**Herbalist density pass — 30 September 2026:** Blender revision 05 enlarges and fills the wall trays below the open window, rotates and deepens the shelter-post trays toward the game camera, and adds five exact native tea/broadleaf plant placements. The counted export total is 2,359 vertices (159 above the advisory 2,200 ceiling); the whole visible scene is 5,057. Saved-file validation has zero errors and one budget warning; 19 attachment source checks pass. Final material/AO, PIL and game checks remain pending.

**Herbalist painted-herb revision — 30 September 2026:** Blender revision 06 replaces the separate herb meshes on all drying trays with scattered leaf artwork painted on the existing solid tray boards. A strong scene-local tangent-space normal map supplies leaf-edge, ridge and overlap relief; only the upside-down hanging sprigs retain simple leaf and stem geometry. Basket/bin herb contents are solid textured fill. Both roofs have lighter science-blue tiles and darker blue beams for contrast. The counted export total falls to 1,922 vertices (906 base + 697 integrated bespoke + 319 bespoke attachments); the whole visible scene is 4,620. Saved-file validation has zero errors and warnings, all 19 attachment source checks pass, and the original base geometry/UVs remain intact. These surface and roof colours are Blender previews, not a published shared atlas release. Bespoke prop AO is planned for unallocated cells within Apothecaries' Stage 2 region of `CSC_Props_Shared_01_AO`; no AO bake or atlas publication has yet been made. Final material/AO, PIL and destination-game checks remain pending. Delivery: `codex-outputs/CSC_APOTHECARIES_Herbalist/revision-06`.

**Herbalist prop refinement — 30 September 2026:** Blender revision 07 replaces the circular fill floating over the sheltered square bin with a fitted rectangular herb fill and swaps the naturally dark Zimbabwe pot for a compact patterned native pot. The hanging herb branches beside the wall window and right rack, plus the working sprig by the mortar, are enlarged; the right hanger extends beyond the trays and its ties meet the beam. The entrance crate moves closer to the wall and gains a second herb basket. The front basket now contains an intact native white-flowered shrub; its widened bespoke basket contains the shrub's lower volume without changing the shrub's geometry, UVs, material or ground pivot. Counted geometry is 2,092 vertices, with 4,839 visible including native/shared attachments. Saved-file validation reports zero errors or warnings, and all 21 attachment source checks pass. Road and window clearances remain. Atlas/AO, PIL and destination-game checks remain pending. Delivery: `codex-outputs/CSC_APOTHECARIES_Herbalist/revision-07`.

Follow the current [Civ VI art skill](https://github.com/hennogous/civ6-art/blob/main/SKILL.md) and [art-direction synthesis](https://github.com/hennogous/civ6-art/blob/main/references/art-direction-synthesis.md). The [CSC production conventions](https://github.com/hennogous/civ-supply-chains/blob/main/references/art-production-conventions.md) set an advisory target of 2,000 exported vertices ±10% (normally 1,800–2,200). Count building and bundled geometry, bespoke attachments and bespoke decals; exclude native pantry and agreed genuinely reusable CSC prop references from that target, while reporting every visible placement in the scene total. Measure split export vertices. Report overages as warnings rather than blocking export for the count alone. Animation requires its own checked implementation path.

Use [texture and UV guidance](textures-and-uvs.md), [shared-atlas AO guidance](shared-atlas-ao.md) and the [export pipeline](export-pipeline.md) for implementation details. Keep recolouring, new geometry and AO changes coordinated; the colour treatment alone should not erase authored construction detail.

## Storage buildings and loading crane

Create Quarter-specific prop scenes around the shared storage buildings. Stored materials, goods, containers and loading activity should identify the Quarter while preserving a recognisable storage family.

Assess the existing large storage building. A completely new large variant is an option, not yet a decision to replace it. Its design should support an upper-level loading bay and an **animated crane loading goods into that bay**.

The animated crane is part of the planned storage work. Start by identifying the source storage model and verifying a minimal crane animation through the Civ VI export/runtime path. Establish the crane's pivots or rig, hoist and load movement, loading-bay clearance and a repeatable loading cycle before polishing the full scene. The static-building workflow alone is not evidence that this animation will work.

Use a crane structure that can be shared, with Quarter-appropriate loads where practical. Keep its movement readable at game distance and within the usable scene envelope. Check the animation in game as well as in Blender. A temporary static pose may support blockout, but does not complete the animated-crane objective.

## Industrial Era variants

Create Industrial Era versions of all building families, including storage. The working expectation is that most changes will be textures/materials and selected props; confirm this against each model and trade.

Preserve the footprint, stage identity and recognisable massing. Update construction and equipment coherently: manufactured roofing, masonry, finished joinery or metalwork where appropriate, along with period-suitable production, storage and handling props. Small geometry changes may be necessary where the new construction or equipment affects the silhouette or openings.

Retain the Quarter roof and beam colour system. An Industrial Era appearance does not change the building's supply-chain stage. Identify whether the storage crane needs an era-specific treatment when planning those variants.

## Later cultural variants

Culturally unique versions can be added over time without delaying the shared-kit rollout. They may earn bespoke architecture where a documented craft tradition changes the equipment, working arrangement or silhouette. Retain the Quarter colour family, mechanical role and compatible placement.

The earlier shortlist is a research backlog, not a commitment to build every entry:

| Existing CSC building | Candidate tradition | Reason to explore |
|---|---|---|
| Wind Mill | Persian asbad | Vertical-axis milling produces a distinct structure |
| Smelter | Japanese tatara ironworks | Furnace, bellows and shelter form a specific working building |
| Café | Ottoman coffeehouse | Gathering and coffee preparation shape the frontage and interior |
| Winery | Georgian marani | Buried qvevri and grape processing shape the cellar arrangement |
| Textile Workshop | Indian cotton weaving | Strong textile-industry identity expressed through equipment and cloth |
| Fashion House | Inca fine textiles; Chinese silk/brocade; later Parisian couture | Different traditions of specialty garment production |
| Apothecary | Chinese medicine hall | Dispensing and preparation spaces, especially for a later-era reference |
| Distillery | Scottish whisky production | Distinctive stills and storage, especially in the Industrial Era |
| Luthier | Cremonese instrument making | Particularly close match to the building's specialty role |
| Sculptor's Studio | Greco-Roman marble workshops | Open carving activity and unfinished sculpture |
| Jeweler | Asante royal goldsmithing | Courtly specialty demand; would require a suitable cultural/civilisation scope |

Research anchors: [asbads](https://whc.unesco.org/en/tentativelists/6192/), [tatara](https://www.mlit.go.jp/tagengo-db/en/R5-00278.html), [coffeehouse culture](https://www.unesco.org/en/articles/cafes-rich-blend-cultures?hub=67076), [qvevri](https://ich.unesco.org/en/RL/ancient-georgian-traditional-%20qvevri-wine-making-method-00870), [Indian textiles](https://www.metmuseum.org/fr/essays/indian-textiles-trade-and-production), [Inca textiles](https://www.metmuseum.org/art/collection/search/751901), [Chinese silk](https://ich.unesco.org/en/RL/sericulture-and-silk-craftsmanship-of-china-00197), [Paris couture](https://www.palaisgalliera.paris.fr/en/exhibitions/worth-inventing-haute-couture), [Chinese pharmacy](https://www.ehangzhou.gov.cn/2023-04/03/c_284220.htm), [Scottish whisky](https://www.nms.ac.uk/discover-catalogue/collecting-contemporary-scottish-whisky), [Cremonese luthiery](https://ich.unesco.org/en/RL/traditional-violin-craftsmanship-in-cremona-00719), [Aphrodisias](https://aphrodisias.classics.ox.ac.uk/), and [Asante goldsmithing](https://www.metmuseum.org/art/collection/search/312427).

Select the particular region and historical period before designing a cultural asset. These references span several eras; do not treat them all as Classical Era architecture or use a cultural appearance to imply unplanned mechanical bonuses.

## Work sequence and open decisions

| Work package | Intended result | Still to decide or verify |
|---|---|---|
| Kit and colour preparation | Existing sources ready for Quarter variants | Any minor refinements; exact beam colours for Goldsmiths/Brewers; assistant recolouring versus GIMP templates |
| First production prop scene | Textile Workshop: one reviewed composition with normal/expanded art, Level 1 kit and a fresh shared prop atlas | Final equipment composition, full/small shelter selection and texture allocation |
| Quarter rollout | Concepts and finished prop scenes for the remaining building variants | Prioritisation and reusable prop sets |
| Storage scenes and crane | Quarter goods around storage plus a working upper-bay loading animation | Storage source files; large-model reuse/replacement decision; animation pipeline proof |
| Industrial variants | Coherent era update across the building families | Texture-only cases versus cases needing new geometry or equipment |
| Cultural additions | Selective historically grounded unique models or kit adaptations | Which traditions and civilisations to prioritise |

Judge success by a complete Quarter scene at the game camera: the player should recognise the building family, distinguish the industry through its activity and colours, and see the defining equipment without searching beneath the roofs.

**Vertex-budget scope — corrected by Henno, 26 September 2026:** the normal 2,000 ±10% target covers direct building geometry, bundled props and bespoke one-off attachments. Native pantry and genuinely reusable approved CSC props are excluded; potential library candidates are not automatically exempt. Attachment hierarchy serves terrain behavior, not budget avoidance. The Fashion House Courtyard therefore counts even with its separate pivot. Report this bespoke total alongside reusable placements and whole-scene totals. Historical direct-only counts below describe the previous interpretation and do not establish compliance with this corrected scope.

**Fashion House garden revision09 — 25 September 2026:** follows Henno’s supplied court-garden target, with connected planting on both sides of the entrance, native hedges/evergreens/flower beds, a shallow authored climbing canopy and cream rose geometry. Budget scope is direct geometry only: main2151, attachments6832, entrance decal16; visible intact total8999. All placements are uniform. Native ground plant meshes/UVs remain original; the courtyard canopy is declared authored derivative geometry. The ivory skirt is 20% narrower and 55% deeper, retaining original height/bodice and its mirror-shared pivot, with the gold stripe centred on the front. Privacy-screen panels and edging have explicit reverse-wound back faces with separate vertices and opposite normals. Shared atlas r014 adds rose self-AO in unused Stage4 space and rebakes fitting AO, preserving all other AO and every surface map. Delivery: `codex-outputs/CSC_TAILORS_Fashion_House/revision-09-court-garden`; Blender/CN6 and PIL verification accompany it, destination review remains pending.

**Fashion House cap refinement — 25 September 2026:** Henno restored the normal 2,000 ±10% main/direct geometry budget (2,200 ceiling) now that separate attachments are excluded. Current direct geometry 2,151 leaves49 vertices headroom; do not add geometry merely to fill it.


**Fashion House user-layout repair — 26 September 2026:** revision10 preserves every mesh, UV and visible placement in Henno's saved revision09 edit. It aligns a dedicated Fashion House CON+PIL master (ruin and scaffolding) to the moved/rotated main building; includes Review-only duplicate roses in Export; reconciles copied native/custom attachment instances and transforms; gives the garden crate/folds one ground-supported Garden_Stock controller; and refreshes custom masters and aligned combined PIL decals. All39 attachment placements validate against their sources. Main/direct geometry is2089, attachments6726, path16, total8831; the2200 direct-geometry ceiling remains. Atlas r014/AO is unchanged. A native validation correction selects the catalogue's default-visible components, matching library import rather than requiring hidden pillaged meshes. CSC skill now explicitly excludes all reused attachments from building targets and forbids prop encroachment onto roads unless Henno explicitly requests it. Delivery: `codex-outputs/CSC_TAILORS_Fashion_House/revision-10-layout-repair`; FGX/game integration and destination paving selection remain unverified.


**Fashion House pillage scope — 26 September 2026:** Henno requested no PIL decals for plants. Revision10's combined PIL asset now contains four original building cards plus seven solid-prop cards (44 exported vertices); native plants, rose sprays and climbing foliage generate no debris cards. The arbour card is bounded by its solid structure, screen and curtain. Intact geometry and attachment placements are unchanged.


**Pantry attachment correction — 26 September 2026:** pantry assets already exist in the game's asset inventory; using them adds placements, not new CSC definitions. Henno clarified that all pantry props remain native attachments. Only CSC props may optionally be bundled into building geometry when nearby and not expected to need significantly different terrain height. Fashion House revision10 converts both shelter crates and the garden crate to exact native DIS_COM_Crate attachments; Garden_Stock now contains only CSC cloth sharing the garden crate pivot. Latest user placements are preserved exactly, and existing add-on controller selection/duplication are tested. No new CSC definitions are added. Main2041, attachments6774, path16, total8831;42 attachment placements. Solid-only PIL remains44 vertices.


**Scene validator findings — 26 September 2026:** the shared authoring validator is now available in CSC Scene Tools1.3.0 and enforced by the export decoder. The current Fashion House passes the corrected native-crate split but fails on21 pantry-derived foliage components retained within the CSC Courtyard assembly. Mechanical source/export checks previously passed because they did not enforce this provenance boundary. Those components need correction; the validator does not alter them. Read-only report: `codex-outputs/CSC-scene-validator/fashion-house.md`. Road/AO/composition/thin-surface/state reviews remain explicit requirements, not automatic passes.


**Fashion House foliage violations corrected — 26 September 2026:** all21 pantry-derived Courtyard components now reference original native assets through separate uniformly scaled attachments. Fourteen preserve old shape to floating-point precision; seven compressed leaf clumps regain native depth using fitted placements. Other geometry, UVs and positions are unchanged. The custom Courtyard master drops to1062 vertices; main2041, attachments6774, path16 and total8831 remain unchanged. There are63 placements, with no new CSC asset definitions. Final authoring validation has zero errors; all nine masters decode and63 source/support/transform checks pass. Updated intact/top/pillaged renders were reviewed, screen reverse faces and CON+PIL alignment verified. Solid-only PIL remains44 vertices. Blender/CN6 handoff complete; destination/game checks remain separate. Current files are in revision-10-layout-repair.


**Fashion House lean pass — 26 September 2026:** Henno corrected the budget scope: bespoke one-off assemblies count even as terrain-following attachments; potential library candidates are not automatic exemptions. Revision11 removes29 custom rose meshes (seven sprays plus eight arbour clusters), saving2813 vertices (31.9%) and one custom prop definition. Surviving geometry, UVs and placements are unchanged. Direct2041 + Courtyard286 + Fitting311 + chair54 + garden cloth40 =2732 budgeted solid vertices; native3270 + entrance decal16 gives6018 visible total. Conservatively all remaining custom attachments count. The original2200 limit is retained: the validator correctly reports one budget error (532 over), with an optional scope clarification pending. This is a light-cleanup review, not a zero-error final handoff. All56 source-parity checks pass; screen/CON+PIL/solid-onlyPIL and render reviews pass;74 automated tests run (67 pass,7 skip). Native/library sources and atlasr014 are unchanged. CSC Scene Tools1.3.1 now displays the corrected budget. Files: `codex-outputs/CSC_TAILORS_Fashion_House/revision-11-lean-garden`.


**Fashion House counting agreement — 26 September 2026:** Henno approved the budget definition, including bespoke entrance-decal geometry, and confirmed the chair and cloth as reusable (cloth can serve the storage building). Current revision11 budget is2041 direct +286 Courtyard +311 Fitting +16 entrance decal =2654. The separate chair54 and Garden_Stock cloth40 are exempt approved reusable references, alongside3270 native vertices. Bundled shelter cloth remains in the direct count. Whole scene stays6018; no geometry or placements changed. Metadata records the approval without renaming/publishing shared-library assets. The skill now carries the agreed rule and CSC Scene Tools1.3.2/validator includes bespoke decal geometry. One numerical budget violation remains:454 above2200; no exception has been granted.76 tests run (69 pass,7 skip). This supersedes the prior pending-classification note, not the remaining numerical overage.


**Fashion House shared library intake — 26 September 2026:** published `CSC_ALL_Chair_Upholstered_Claret` (54 vertices) and `CSC_ALL_Folded_Cloth_Claret_Ivory` (40 vertices). Henno chose to keep the folded claret/ivory pair together as one reusable asset, and explicitly kept the upright claret bolt bundled. Revision11 uses the new shared identities and archives superseded local masters. Geometry/UVs/placements and pivots are unchanged; all56 source checks pass. Library now199 records, with197 prior blends and catalogue entries preserved; compatible r014 AO update leaves every existing used allocation unchanged. Add-on1.3.3 preserves declared multi-component frames when importing. Contact sheets and shared HTML gallery refreshed. Runtime registration remains pending; the separate building budget overage remains2654/2200.

**Budget enforcement clarification — 28 September 2026:** Henno clarified that the 2,000 ±10% vertex budget is a design goal, not an export gate. Continue counting direct geometry, bespoke attachments and bespoke decals with the agreed reuse exclusions; report overages as warnings and allow export. No exception or approval is required merely to exceed the target. This supersedes earlier hard-cap/budget-error language in the dated Fashion House notes. Mechanical validity and source-parity errors remain blocking.

**Tailor vertex revision — 2 October 2026:** The verified `codex-outputs/CSC_TAILORS_Tailor/revision-10-vertex-budget` scenes count 2,156 vertices (normal) and 2,197 (alternate), including final UV2 seams and bespoke attachments. Three existing approved shared Workbenches per scene now carry complete catalogue reuse metadata. A joint UV2 pack saves 225/234 actual exported vertices; the alternate also loses four shallow cloth-roll cores and two tiny trim strips, while both variants and their lean-to master lose two zero-area faces. Their two Stage 3 AO cells have been rebaked and published as canonical Shared01 r019 with all other atlas pixels unchanged, following Henno's explicit authorization. Matching revised Tailor scene sources are published as `TAILORS/Tailor/revision-10-vertex-budget` in Working Files.

**Standing art-publication approval — 2 October 2026:** In response to the request to publish the completed Tailor scene package and shared AO release to their established Google Drive backed Working Files locations, Henno said “yes! always.” Treat this as standing authorization to publish similarly completed and verified CSC art revisions to their established Working Files scene folders and versioned shared atlas library without asking him again for the same transfer. Continue using the execution environment's filesystem approval mechanism where required; do not extend this approval to unrelated destinations or public release.

**UV2-inclusive planning — 2 October 2026:** Henno clarified that the 2,000 ±10% design goal includes vertices split by the final AO UV2 layout, as well as UV1 and UV3 splits. Plan headroom before AO allocation; report the exporter-equivalent count after final UV2 unwrap and bake, not a pre-AO mesh count as the budget result. Diagnose seam growth per object and optimize UV layouts or unreadable geometry without sacrificing the approved silhouette and mapped AO. The budget remains advisory, with overages reported as warnings rather than export blocks.
