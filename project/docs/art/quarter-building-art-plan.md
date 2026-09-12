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
3. **Create contextual concept images.** The assistant dresses the base model with its Quarter colours and occupational scene. The point is to choose equipment, scale and composition around the existing building. Henno selects or refines the concept before detailed prop construction; an already accepted concept remains valid.
4. **Build and place the props in Blender.** The assistant creates editable, named prop meshes around the base model, first checking the large forms and composition, then developing materials and selected detail. Reusable equipment and storage props can be shared where appropriate.
5. **Review the complete scene.** Check the intended elevated game view and useful rotations, including at normal play distance. Adjust props and placement before deciding that the base architecture needs alteration.
6. **Prepare the asset for the existing export workflow.** Deliver the editable scene, props, external textures, review images and geometry/material report; complete export and in-game checks through the established pipeline for the production asset.

### Prop direction

- **Chunky, visible, activity-led props do the heavy lifting.** Exaggerate identifying shapes such as the loom, mortar, vat, furnace, workbench or stockpile so the profession is readable at game distance.
- Show what the building does at its particular stage. Raw fibre and broad cloth production belong to a different scene from tailoring everyday garments or making specialty clothing.
- Keep defining equipment visible from above. Roof overhangs should conceal only as much as needed to anchor the activity convincingly in the building. Use the smaller shelter, orientation or placement when those solve the problem.
- Arrange props into meaningful groups for processing, inputs, finished goods, drying or loading, with gaps that keep their silhouettes readable. Do not fill every gap with small clutter.
- Keep entrances and working routes plausible. Large props should feel used and supported, not arranged as oversized ornaments outside an unrelated house.
- Give quieter sides and rear views considered storage or service details. Avoid adding exterior paving aprons or display plinths unless the particular scene calls for them.

Follow the current [Civ VI art skill](https://github.com/hennogous/civ6-art/blob/main/SKILL.md) and [art-direction synthesis](https://github.com/hennogous/civ6-art/blob/main/references/art-direction-synthesis.md). The [CSC production conventions](https://github.com/hennogous/civ-supply-chains/blob/main/references/art-production-conventions.md) set building budgets targeting 1,500 exported vertices with a hard cap of 2,000, including delivered props; count the actual export rather than assuming source counts equal runtime counts. Resolve an over-budget composition through simplification, or explicitly revise its budget with Henno. Animation requires its own checked implementation path.

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
| First production prop scene | One reviewed concept carried through Blender, export and game review | Which building goes first; final equipment composition and texture allocation |
| Quarter rollout | Concepts and finished prop scenes for the remaining building variants | Prioritisation and reusable prop sets |
| Storage scenes and crane | Quarter goods around storage plus a working upper-bay loading animation | Storage source files; large-model reuse/replacement decision; animation pipeline proof |
| Industrial variants | Coherent era update across the building families | Texture-only cases versus cases needing new geometry or equipment |
| Cultural additions | Selective historically grounded unique models or kit adaptations | Which traditions and civilisations to prioritise |

Judge success by a complete Quarter scene at the game camera: the player should recognise the building family, distinguish the industry through its activity and colours, and see the defining equipment without searching beneath the roofs.
