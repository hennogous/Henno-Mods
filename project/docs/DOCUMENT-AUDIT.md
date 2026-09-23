# Documentation audit — 12 September 2026

**6 superseded**, **16 needs refresh**, **15 current**, **11 historical**, **2 provisional**, **1 parked proposal**.

## Evidence and limits

This is a document-level currency audit with focused checks against local source, not a line-by-line certification of every historical API or measurement. Every one of the 51 Markdown files present at the start is classified below. No other substantive files were found; any Finder metadata is outside the documentation inventory. The audit and archive index added by this pass are navigation records.

Checked sources include the [current building plan](art/quarter-building-art-plan.md), [art skill](https://github.com/hennogous/civ6-art/blob/main/SKILL.md) and [art-direction synthesis](https://github.com/hennogous/civ6-art/blob/main/references/art-direction-synthesis.md); [Tailors control](../specs/tailors/control.yaml), [implementation contract](../specs/tailors/implementation.yaml), [Quarter validators](../tools/quarter_contracts/README.md), and [Bakers catalogs](../specs/reference/); [Tailors SQL](<../../Civ Supply Chains/Data/CSC_Q_TAILORS.sql>), [Art Pack property Lua](<../../CSC Art Pack/Lua_UI/ArtProperties/CSC_ArtProperties.lua>), [actions JSON](../modbuddy/CivSupplyChains.actions.json), [actions tool](../tools/modbuddy/civ6proj_actions.py), and the [TaxesPolitics files](../../TaxesPolitics/).

Tooling checks used the actual [export script](../tools/scripts/csc_export_pipeline.ps1), [AO baker](../tools/blender/csc_shared_atlas_ao_bake.py), [PBR helper](../tools/blender/csc_generate_pbr_maps.mjs), [icon pipeline](../tools/comfyui/icon_pipeline/), [SV pipeline](../tools/comfyui/sv_pipeline/), [training scripts](../tools/training/) and [localization generator](../tools/localization/loc_md_to_sql.py). Existing native-study corrections were compared with current guidance; raw source assets were not remeasured in this audit.

Windows installations, ComfyUI checkpoints, Asset Editor, cooking, Civ VI runtime behavior and remote MAB PR status were not checked live. Their historical claims are explicitly scoped below. No gameplay code, approval gates, source models or external installations were changed.

## Status meanings

- **Current:** suitable for its stated purpose against the sources checked; does not mean runtime-certified.
- **Needs refresh:** specific conflicts, obsolete commands or mixed current/historical guidance remain. Read its audit notice before following the procedure.
- **Historical:** useful evidence, transcript or snapshot; not current status or a production specification.
- **Superseded:** replaced or demonstrably unreliable for its original purpose; archived with a replacement route.
- **Provisional:** investigation or proposed interface without a verified working implementation.
- **Parked proposal:** future related-project design, outside active CSC implementation.

## Priority findings

1. **Export and SV procedures need the next maintenance pass.** Export has stale paths in the actual script, a two-UV default and older state-name handling. SV documentation describes scripts/defaults that have since changed. These are tool/document reconciliation tasks, not cosmetic edits.
2. **Art guidance has competing generations.** The new reusable-kit plan and current art skill take priority. Old compulsory roof shapes, invalid UV percentages and mandatory AO rebaking rules must not leak into new assets.
3. **Quarter workflow status lagged implementation.** Tailors Stage 3 and art integration have approved phase gates marked ready_for_review. This does not mean user acceptance. Avoid copying the old clean-baseline or all-art-deferred language.
4. **History and live state were mixed.** MAB PR heads, ComfyUI installations, training runs and CE memory offsets cannot be certified from a dated note. They remain useful as scoped history.
5. **Duplicate research is retained, with scope.** The two geometry catalogues and two pattern summaries overlap and share the same measurement caveats. They are not independent corroboration. The existing direct-study corrections are the better calibration source.

## Changes made in this pass

Added a purpose, status and concrete finding for every original document; placed the same notice in each substantive file; archived five superseded root documents; moved four investigations/related-project notes to their appropriate folders; rebuilt navigation and updated repository links. Corrected the two icon script paths in the implementation notes and recovered the geometry inspector links under project/tools/scripts. Historical bodies and unresolved procedures are preserved beneath their notices; this audit does not pretend they have all been rewritten or tested.

## Document register

Paths below are the resulting locations. For moved files, the earlier location is recorded separately at the end.

| Document | Purpose | Status | Finding / next action |
|---|---|---|---|
| [art/2d/COMFYUI-MANUAL.md](art/2d/COMFYUI-MANUAL.md) | 2D tooling | Needs refresh | Icon paths are mostly current, but stated generation settings differ from icon_img2img.py (denoise 0.4, CFG 9, 40 steps, ControlNet 0.95). SV commands point to removed Blender-folder scripts; use comfyui/sv_pipeline. Postprocessing descriptions need reconciliation. |
| [art/2d/icon-pipeline-implementation-notes.md](art/2d/icon-pipeline-implementation-notes.md) | 2D tooling | Needs refresh | Transparent-input preservation, CPU rembg and per-run output behavior agree with source. Paths omit icon_pipeline, SAM helper is icon_sam_outline.py, and missing/failed SAM prints a message in the actual code. Fix paths below; retain these remaining behavior differences as refresh work. |
| [art/2d/icons-pipeline.md](art/2d/icons-pipeline.md) | 2D tooling | Needs refresh | Historical tuning differs from current icon_img2img.py, which uses denoise 0.4, CFG 9, 40 steps and ControlNet 0.95. Background removal is rembg/retained input alpha; SAM adds outlines. Current outline default is 15px, not the stated 28px. Old csc paths are obsolete. |
| [art/2d/strategic-view-sprites.md](art/2d/strategic-view-sprites.md) | 2D tooling | Needs refresh | render_to_sv_img2img.py/add_sv_shadow.py no longer exist in project/tools/blender. Current sv_pipeline supports rembg/retained alpha, SAM outlines, shadow plates and revealed/state variants. Brightness defaults off; old threshold/brightness/default-size guidance is obsolete. |
| [art/export-pipeline.md](art/export-pipeline.md) | 3D export | Needs refresh | The actual PowerShell script still hard-codes .openclaw/workspace/csc paths, defaults UVCount to 2, and recognizes separate _CON/_PIL suffixes. Merely correcting document paths would not fix the tool. Preserve three UV channels for the current kit; reconcile script/state handling before production use. Static export examples do not validate crane animation. |
| [art/textures-and-uvs.md](art/textures-and-uvs.md) | 3D materials reference | Needs refresh | Opening UV percentages repeat analyzer values invalidated by direct studies; island equality and atlas-allocation generalizations are too strong. Recent height/region PBR section matches the current tool direction. Separate current kit convention from historical measurements and resolve effective asset/material bindings. |
| [art/ai-3d-model-generation.md](art/ai-3d-model-generation.md) | 3D production | Needs refresh | Continuous swatches/no painted shadows and UV2 rebuild-on-UV1-change instructions conflict with current art skill and shared AO reuse. Blanket welding/culling guidance needs scoping. Existing kit and whole-scene exported budgets in the new plan take priority. |
| [art/shared-atlas-ao.md](art/shared-atlas-ao.md) | 3D production | Current | Algorithm description matches the current bake helper: nearest-3D selection, UV2-connected pack islands and least-squares transforms. Family AO reuse is an intentional approximation to review per variant. July bake status is historical; no originals were rebaked. |
| [archive/art/baked-ao-for-shared-atlases.md](archive/art/baked-ao-for-shared-atlases.md) | AO history | Superseded | Earlier narrative describes UV1-connected matching/twin ambiguity. Current shared-atlas-ao.md and csc_shared_atlas_ao_bake.py use UV2 pack connectivity, nearest-3D matching and least-squares transforms. Preserve the narrative, use the newer procedure. |
| [archive/art/BUILDING-SHAPES.md](archive/art/BUILDING-SHAPES.md) | Art direction | Superseded | Mandatory asymmetry, flat-roof prohibition and numerical ratios conflict with the corrected Firaxis studies and current art-direction synthesis. Preserve as earlier heuristics, not production rules. |
| [art/districts_buildings_art_guide.md](art/districts_buildings_art_guide.md) | Art integration reference | Needs refresh | File-relationship overview is useful; modeling/material sections overlap older generation/export advice and should defer to the current art skill. Static single-bone examples do not cover the planned animated crane. No current AE/cook/runtime validation was performed. |
| [archive/art/ART-KIT-3D-PASS.md](archive/art/ART-KIT-3D-PASS.md) | Art planning | Superseded | Unchecked foundation tasks predate the inspected kit and completed shared AO work. They are not a reliable remaining-work list. Use quarter-building-art-plan.md and shared-atlas-ao.md. |
| [art/quarter-building-art-plan.md](art/quarter-building-art-plan.md) | Art planning | Current | Records the user-agreed reusable kit, roof/beam differentiation, visible chunky occupational props, storage/crane, Industrial Era work and later cultural variants. Open choices are explicitly left open; existing concept studies do not authorize replacing the kit. |
| [art/dynamic-art-properties.md](art/dynamic-art-properties.md) | Art/gameplay integration | Needs refresh | Stage 3 is no longer declaration-only: CSC_Q_TAILORS.sql contains Stage 3 art attachment/property rows. The blanket no-improved-material-gate timing rule also needs Bakers/Tailors scoping. Stage 4 remains gated in control.yaml. |
| [archive/art/all-buildings-list.md](archive/art/all-buildings-list.md) | Asset inventory | Superseded | Claims complete coverage without source provenance, mixes wonders into the list and labels University of Sankore a Mali unique building. Not a reliable inventory or universal era-variant map; consult source assets and scoped geometry studies. |
| [integrations/MAB_CHANGES.md](integrations/MAB_CHANGES.md) | Dependency history | Historical | June 23 branch/PR/commit record. Remote PR status and the currently installed Windows branch were not rechecked. The final local-only claim conflicts with its own table listing an integration PR; do not treat either as live status. |
| [integrations/MAB_MANUAL.md](integrations/MAB_MANUAL.md) | Dependency reference | Needs refresh | Useful reverse-engineered schema reference, but the main table omits CSC-used MinRings and MustOwn extensions. Version/current-build wording and upstream completeness are unverified. Read with MAB_CHANGES.md and the live CSC adjacency processor. |
| [research/art/art-architecture-thread.md](research/art/art-architecture-thread.md) | Discussion record | Historical | Raw conversation retains unverified Pile and performance claims. The later art-performance-evidence-review explicitly withdraws Pile-specific guidance. Keep as provenance, not operational instructions. |
| [archive/tooling/COMFYUI-SETUP.md](archive/tooling/COMFYUI-SETUP.md) | Environment snapshot | Superseded | Claims SV training is still pending; lora-training.md and checked-in training scripts describe completed/custom LoRA work. Installed models, GPU, packages and service state are an old Windows snapshot, not current inventory. |
| [research/art/art-performance-evidence-review.md](research/art/art-performance-evidence-review.md) | Evidence review | Current | Explicitly corrects analyzer metrics and rejects an unmeasured engine bottleneck hierarchy. Consistent with later scoped native studies and current skill; no new runtime performance measurements were made. |
| [research/art/firaxis-guidance-review.md](research/art/firaxis-guidance-review.md) | Evidence review | Current | Dated, pinned guidance review explicitly corrects earlier AO interpretations and informs the current art skill. New original-design advice must be scoped to original assets; existing kit variations follow the user plan. |
| [research/mods/community-extension-modding.md](research/mods/community-extension-modding.md) | External API research | Historical | Contains dated April FireTuner results and version-sensitive memory offsets. Installed CE/game binaries and the full external API were not revalidated. Neither the beta/version wording nor this document implies CSC currently requires CE. |
| [integrations/ruivo-adjacency-processor.md](integrations/ruivo-adjacency-processor.md) | Gameplay integration | Current | Central processor exists and its ModBuddy action still uses LoadOrder 3000. Declarative config/tag ownership matches current Quarter/reference guidance. External MAB build compatibility was not runtime tested. |
| [integrations/bakers-service-notification-ui.md](integrations/bakers-service-notification-ui.md) | Gameplay/UI reference | Needs refresh | Core Storekeeper/service UI rationale remains useful. The old Aristocrat restoration/debugging note must be read in the TaxesPolitics boundary, not as CSC work. Recheck notification branches against current Lua before re-enabling anything. |
| [research/art/building-geometry-patterns.md](research/art/building-geometry-patterns.md) | Native asset interpretation | Historical | Broad interpretation of the older census; UV coverage, island averages and authoring inferences were qualified by the evidence review. Overlaps geometry-patterns.md; neither is a universal production specification. Some backing artifacts are unavailable. |
| [research/art/geometry-patterns.md](research/art/geometry-patterns.md) | Native asset interpretation | Historical | Condensed overlapping pattern summary. Floating-island averages and universal authoring claims are not established by the audited analyzer. Keep as historical synthesis with current-skill priority. |
| [research/art/building-geometry-catalogue.md](research/art/building-geometry-catalogue.md) | Native asset inventory | Historical | Broader catalogue overlaps geometry-catalogue.md. Existing metric-defect warning is essential; raw counts are historical observations. Several analysis-data/script links are unavailable at their recorded paths. Use direct native studies for calibrated examples. |
| [research/art/geometry-catalogue.md](research/art/geometry-catalogue.md) | Native asset inventory | Historical | Condensed overlapping catalogue, not an independent second measurement. Keep its existing evidence warning and consult broader building-geometry-catalogue/direct studies; do not treat old coverage values as measured occupied atlas area. |
| [research/art/firaxis-campus-family-study.md](research/art/firaxis-campus-family-study.md) | Native asset study | Current | Retains corrected distinction between disjoint UV2 coordinates and unresolved effective AO bindings. Scoped source observations remain useful; no AST/runtime or filtering validation is claimed. |
| [research/art/firaxis-city-block-study.md](research/art/firaxis-city-block-study.md) | Native asset study | Current | Explicitly scopes block-scale counts, mixed texture dimensions and unresolved AO bindings. Supports flat terraces without imposing a universal roof rule; not a single-building budget or performance profile. |
| [research/art/firaxis-library-study.md](research/art/firaxis-library-study.md) | Native asset study | Current | Useful direct counts and material comparisons with caveats. Its remaining foundation/CON next-input list predates the linked campus follow-up; use that follow-up for resolved inputs. AST/runtime and mip usage remain unresolved. |
| [research/art/firaxis-market-study.md](research/art/firaxis-market-study.md) | Native asset study | Current | Direct imported-model observations correct old Market UV coverage and blanket shading claims. Limits distinguish Blender approximation from FGX/runtime proof; still suitable as scoped calibration. |
| [README.md](README.md) | Navigation | Current | Rebuilt as the purpose/status index for every document in this audit; does not confer current authority on research or legacy instructions. |
| [research/README.md](research/README.md) | Navigation | Current | Research index refreshed to include moved procedural/AE/CE investigations and distinguish source observations, unvalidated proposals and historical transcripts. |
| [research/art/building_schema.md](research/art/building_schema.md) | Procedural design sketch | Provisional | No matching ridge_offset_y/trim_band implementation was found in project/tools. Treat volumes/features/meta as a proposed schema, not a supported generator interface or a requirement to rebuild the approved kit. |
| [quarters/LOCALIZATION-PATTERNS.md](quarters/LOCALIZATION-PATTERNS.md) | Quarter workflow | Current | Markdown-source ownership and implementation-grounded text agree with project/localization, loc_md_to_sql.py and bakers-localization-patterns.yaml. No conflicting workflow found in the checked sources. |
| [quarters/QUARTER-CONTRACT-WORKFLOW.md](quarters/QUARTER-CONTRACT-WORKFLOW.md) | Quarter workflow | Needs refresh | The clean Tailors baseline and blanket deferral of art are obsolete. control.yaml records foundation, materials_and_stage2, stage3 and art_integration ready_for_review with user approvals; acceptance is separate. Its phase approval_rule supersedes the old whole-contract approval sequence. |
| [quarters/QUARTER-VALIDATION.md](quarters/QUARTER-VALIDATION.md) | Quarter workflow | Needs refresh | Validator sources remain present, but repeated SQL-layout bullets/paragraphs need deduplication. The closing art-after-gameplay rule is too broad for the approved art_integration phase; use current per-phase gates. |
| [quarters/REFERENCE-PATTERN-CATALOG.md](quarters/REFERENCE-PATTERN-CATALOG.md) | Quarter workflow | Current | All three Bakers pattern catalogs exist under project/specs/reference. The reusable/parameterized/optional/Bakers-only distinction remains applicable; current control.yaml owns phase approval state. |
| [archive/QUARTER-PLAYBOOK-2026-06-26-outdated.md](archive/QUARTER-PLAYBOOK-2026-06-26-outdated.md) | Quarter workflow | Superseded | Already archived. Direct text-SQL editing, manual project actions and template-copy workflow have been replaced by Markdown localization, actions JSON and per-phase contracts. |
| [research/mods/SKILL-REVIEW.md](research/mods/SKILL-REVIEW.md) | Reference-mod research | Historical | March review captures many useful leads, but Not in skill labels describe then-current coverage, not today. The project/docs/data link is unavailable. Individual APIs and workshop versions were not revalidated; verify original source before implementation. |
| [related-projects/SPECIALTY_PRODUCTS.md](related-projects/SPECIALTY_PRODUCTS.md) | Related project boundary | Current | The parked Product substrate, Aristocrat and GreatWorks files exist in TaxesPolitics. Correctly separates that prototype from active CSC M&C improvement support. June runtime results remain historical evidence. |
| [related-projects/taxes+politics.md](related-projects/taxes+politics.md) | Related project design | Parked proposal | Exploratory T&P conversation, not active CSC rules. Internal tensions remain (Governors liked by Guilds versus all-bloc penalty; differing Estate district exclusions). Preserve as input for future design reconciliation, not an accepted implementation contract. |
| [workflows/commands-cheatsheet.md](workflows/commands-cheatsheet.md) | Tool commands | Needs refresh | Mixes an obsolete Mac OneDrive checkout with Windows commands and has an unterminated final path quote. SV command locations are outdated. Examples need a platform-specific rewrite before copy/paste use. |
| [research/art/asset-editor-ironpython-automation.md](research/art/asset-editor-ironpython-automation.md) | Tool investigation | Provisional | Correctly distinguishes static discovery from a pending live Asset Editor test. CSC_DumpPreviewerKnobs.py exists. Keep as research; it does not establish a working automated AE workflow. |
| [workflows/localization-markdown-workflow.md](workflows/localization-markdown-workflow.md) | Tool workflow | Current | Source folder, loc_md_to_sql.py and Markdown-to-SQL ownership match the repository. This audit checked the local workflow, not a new localization build or in-game rendering. |
| [workflows/modbuddy-actions-json.md](workflows/modbuddy-actions-json.md) | Tool workflow | Needs refresh | JSON/check/patch tooling exists and remains the active workflow. The instruction to export before starting needs qualification: actions JSON is the editing source; reconcile differences before exporting from .civ6proj so JSON edits are not overwritten. |
| [art/2d/lora-training.md](art/2d/lora-training.md) | Training reference | Needs refresh | Historical run results are useful. SDXL scripts use sdxl_train_network.py, unlike the generic command template. train_sv_lora.ps1 requests fp16 while icon/unit scripts use no mixed precision; the universal Windows prohibition is not a verified general rule. Environment/model availability remains unchecked. |
| [research/art/blacksmith-skill-trial-01.md](research/art/blacksmith-skill-trial-01.md) | Trial brief | Historical | September 11 experiment with explicit scope and outputs. Preserved as trial provenance; not the default plan for every CSC building and not proof the trial delivered or passed runtime checks. |
| [research/art/blacksmith-skill-trial-01-prompt.md](research/art/blacksmith-skill-trial-01-prompt.md) | Trial handoff | Historical | Saved task prompt, not an instruction to start work during this audit. Linked brief and canonical skill exist. A unique blacksmith experiment does not supersede the reusable-kit production plan; completion is not inferred. |
| [research/art/civ6-3d-art-development.md](research/art/civ6-3d-art-development.md) | Workflow development record | Historical | Learning record includes unique-building direction predating the agreed reusable-kit plan. Technical experiments remain useful; production direction comes from the new plan. Linked output/blacksmith-v5/README.md is unavailable at its recorded location. |

## Moves in this audit

| Previous location within docs | New location |
|---|---|
| `ART-KIT-3D-PASS.md` | [archive/art/ART-KIT-3D-PASS.md](archive/art/ART-KIT-3D-PASS.md) |
| `BUILDING-SHAPES.md` | [archive/art/BUILDING-SHAPES.md](archive/art/BUILDING-SHAPES.md) |
| `all-buildings-list.md` | [archive/art/all-buildings-list.md](archive/art/all-buildings-list.md) |
| `baked-ao-for-shared-atlases.md` | [archive/art/baked-ao-for-shared-atlases.md](archive/art/baked-ao-for-shared-atlases.md) |
| `COMFYUI-SETUP.md` | [archive/tooling/COMFYUI-SETUP.md](archive/tooling/COMFYUI-SETUP.md) |
| `building_schema.md` | [research/art/building_schema.md](research/art/building_schema.md) |
| `asset-editor-ironpython-automation.md` | [research/art/asset-editor-ironpython-automation.md](research/art/asset-editor-ironpython-automation.md) |
| `community-extension-modding.md` | [research/mods/community-extension-modding.md](research/mods/community-extension-modding.md) |
| `taxes+politics.md` | [related-projects/taxes+politics.md](related-projects/taxes+politics.md) |

## Missing evidence artifacts

The link check records unavailable backing artifacts below. These are evidence gaps in the retained historical material, not newly deleted files. No replacement measurements or files have been invented.

| Document | Unavailable target (relative to that document) |
|---|---|
| [research/art/civ6-3d-art-development.md](research/art/civ6-3d-art-development.md) | `../../../../output/blacksmith-v5/README.md` |
| [research/art/building-geometry-catalogue.md](research/art/building-geometry-catalogue.md) | `../../building-mesh-analysis.json` |
| [research/art/building-geometry-catalogue.md](research/art/building-geometry-catalogue.md) | `../../geo-stats-all.tsv` |
| [research/art/art-performance-evidence-review.md](research/art/art-performance-evidence-review.md) | `../../../../output/art-guidance-review/inspector-diagnostics.json` |
| [research/art/building-geometry-patterns.md](research/art/building-geometry-patterns.md) | `../../building-mesh-analysis.json` |
| [research/art/building-geometry-patterns.md](research/art/building-geometry-patterns.md) | `../../sample-geometries` |
| [research/mods/SKILL-REVIEW.md](research/mods/SKILL-REVIEW.md) | `../../data` |

The geometry inspector was found at [project/tools/scripts/inspect_building_mesh.py](../tools/scripts/inspect_building_mesh.py), and both catalogue/pattern links were repaired. Missing raw datasets and output reports were not found by filename in the local Play workspace. Their absence limits reproducibility; it does not invalidate every observation in those reports.

## Folder organisation

After the audit, the remaining 24 topic documents were moved out of the docs root. Their statuses and substantive contents are unchanged. The [folder index](README.md) and topic indexes provide navigation; repository links and source-code documentation pointers were updated. The earlier move table above records the audit-stage moves.

| Previous location within docs | Current location |
|---|---|
| `quarter-building-art-plan.md` | [art/quarter-building-art-plan.md](art/quarter-building-art-plan.md) |
| `ai-3d-model-generation.md` | [art/ai-3d-model-generation.md](art/ai-3d-model-generation.md) |
| `districts_buildings_art_guide.md` | [art/districts_buildings_art_guide.md](art/districts_buildings_art_guide.md) |
| `dynamic-art-properties.md` | [art/dynamic-art-properties.md](art/dynamic-art-properties.md) |
| `export-pipeline.md` | [art/export-pipeline.md](art/export-pipeline.md) |
| `shared-atlas-ao.md` | [art/shared-atlas-ao.md](art/shared-atlas-ao.md) |
| `textures-and-uvs.md` | [art/textures-and-uvs.md](art/textures-and-uvs.md) |
| `COMFYUI-MANUAL.md` | [art/2d/COMFYUI-MANUAL.md](art/2d/COMFYUI-MANUAL.md) |
| `icon-pipeline-implementation-notes.md` | [art/2d/icon-pipeline-implementation-notes.md](art/2d/icon-pipeline-implementation-notes.md) |
| `icons-pipeline.md` | [art/2d/icons-pipeline.md](art/2d/icons-pipeline.md) |
| `lora-training.md` | [art/2d/lora-training.md](art/2d/lora-training.md) |
| `strategic-view-sprites.md` | [art/2d/strategic-view-sprites.md](art/2d/strategic-view-sprites.md) |
| `LOCALIZATION-PATTERNS.md` | [quarters/LOCALIZATION-PATTERNS.md](quarters/LOCALIZATION-PATTERNS.md) |
| `QUARTER-CONTRACT-WORKFLOW.md` | [quarters/QUARTER-CONTRACT-WORKFLOW.md](quarters/QUARTER-CONTRACT-WORKFLOW.md) |
| `QUARTER-VALIDATION.md` | [quarters/QUARTER-VALIDATION.md](quarters/QUARTER-VALIDATION.md) |
| `REFERENCE-PATTERN-CATALOG.md` | [quarters/REFERENCE-PATTERN-CATALOG.md](quarters/REFERENCE-PATTERN-CATALOG.md) |
| `commands-cheatsheet.md` | [workflows/commands-cheatsheet.md](workflows/commands-cheatsheet.md) |
| `localization-markdown-workflow.md` | [workflows/localization-markdown-workflow.md](workflows/localization-markdown-workflow.md) |
| `modbuddy-actions-json.md` | [workflows/modbuddy-actions-json.md](workflows/modbuddy-actions-json.md) |
| `MAB_CHANGES.md` | [integrations/MAB_CHANGES.md](integrations/MAB_CHANGES.md) |
| `MAB_MANUAL.md` | [integrations/MAB_MANUAL.md](integrations/MAB_MANUAL.md) |
| `bakers-service-notification-ui.md` | [integrations/bakers-service-notification-ui.md](integrations/bakers-service-notification-ui.md) |
| `ruivo-adjacency-processor.md` | [integrations/ruivo-adjacency-processor.md](integrations/ruivo-adjacency-processor.md) |
| `SPECIALTY_PRODUCTS.md` | [related-projects/SPECIALTY_PRODUCTS.md](related-projects/SPECIALTY_PRODUCTS.md) |
