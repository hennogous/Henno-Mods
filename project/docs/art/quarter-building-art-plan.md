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

### Prop direction

- **Chunky, visible, activity-led props do the heavy lifting.** Exaggerate identifying shapes such as the loom, mortar, vat, furnace, workbench or stockpile so the profession is readable at game distance.
- Show what the building does at its particular stage. Raw fibre and broad cloth production belong to a different scene from tailoring everyday garments or making specialty clothing.
- **Standing rule:** place defining work equipment outside the side roof, visible from above, and use the sheltered area primarily for stored inputs, finished goods, crates or bales. Keep operator space and circulation clear. Apply a task-specific exception when the activity requires cover.
- Arrange props into meaningful groups for processing, inputs, finished goods, drying or loading, with gaps that keep their silhouettes readable. Do not fill every gap with small clutter.
- Keep entrances and working routes plausible. Large props should feel used and supported, not arranged as oversized ornaments outside an unrelated house.
- Give quieter sides and rear views considered storage or service details. Avoid adding exterior paving aprons or display plinths unless the particular scene calls for them.

Follow the current [Civ VI art skill](https://github.com/hennogous/civ6-art/blob/main/SKILL.md) and [art-direction synthesis](https://github.com/hennogous/civ6-art/blob/main/references/art-direction-synthesis.md). The [CSC production conventions](https://github.com/hennogous/civ-supply-chains/blob/main/references/art-production-conventions.md) set building budgets targeting 2,000 exported vertices ±10% (a planning range of 1,800–2,200, upper limit 2,200), including delivered props; count the actual export rather than assuming source counts equal runtime counts. Resolve an over-budget composition through simplification, or explicitly revise its budget with Henno. Animation requires its own checked implementation path.

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
