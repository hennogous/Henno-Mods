# CSC Memory Index

`memory/` is agent-facing scratch/reference, not the durable home for collaborator-facing project truth. Durable notes should live in `project/docs/` or public `docs/`.

This folder was cleaned in June 2026: stale session notes were removed, and reusable implementation notes were promoted into durable docs.

## Active notes

- [Fashion House mustard dress](session_fashion_dress_mustard.md) — gown/sleeves recoloured; atlas r024 and native UV-only update installed, AE placements preserved.

- [Fashion House coach](session_fashion_coach.md) — revision 02, 937 exported vertices, standalone AE asset and shared atlas r023; fine trim removed per Henno's feedback.

- [Prop detail in paint](feedback_prop_geometry_detail.md) — Henno's coach feedback: omit small trim geometry, including seat rails; spend geometry on the main shapes, openings and support.

- [No Civilopedia referrals](feedback_localization_no_civilopedia_referrals.md) — player-facing text states information directly; never tells players to consult another page for requirements/effects/details.

- [Tailors Stage 4 Tourism](session_tailors_stage4_tourism.md) — all four services changed to +2 Tourism per supplied Fashion House; text and automated checks updated, in-game review pending.

- [Tailor garment rack](session_tailor_garment_rack.md) — wall rack and three garments extracted as one installed asset; 312 vertices, native readback and saved-source checks pass.

- [AE-owned 3D assembly workflow](session_ae_owned_art_workflow.md) — 13 October: skill workflow overridden; saved-AST icon/SV renderer delivered and repeatable on Textile Workshop. AE owns placement; selective geometry export remains future work.

- [Level 1 open ground interior](session_level1_foundation.md) — requested intact and S CON+PIL kit thresholds/floors removed, inward foundations completed; both FGX/GEO pairs installed and native readback verified.

- [Storage AE crash investigation](session_storage_asset_crash.md) — AO2 DDS header fixed and user-confirmed; six extension attachments restored; automatic full-dump capture runs at sign-in and re-arms after AE sessions.

- [Storage S/M AO rebake](session_storage_sm_ao_rebake.md) — four sources + canonical AO2 PNG rebaked in existing regions; CON+PIL UV2 repaired; all four FGX/GEO pairs and AO DDS installed, native readback verified.

- [CSC AI feasibility](session_csc_ai_feasibility.md) — native virtual-yield placement precedent, custom preview/AI boundary, exact material and builder scoring experiments still needed; research only.

- [Quarter lenses and placement](session_quarter_lenses.md) — minimal shared material/sales palette and improved-resource outlines, icon-coloured Bakers/Tailors districts; placement sampler retired. Automated/native checks pass, revised visual review pending.

- [Storage animation research](session_storage_animation_research.md) — v12 deck aligned to sled runners and gait, geometry-only update; v11 clip retains Cargo_TipUpright 90-degree sack lift and concealed rightward reset. Native/clearance checks pass; AE/cook/game review open.
- [Storage L open interior](session_storage_interior.md) — open upper floor/inward walls, foundation entrance extensions and 0.9 resize exported; current AO2 DDS already refreshed. CON+PIL later.

- [Bakers flour replacements](session_bakers_flour_integration.md) — original names retained; 156 placements updated; vertex savings and cook evidence in the durable report.

- [Stage Manager service-icon studies](session_stage_manager_icons.md) — four venue variants; latest crossed ballet shoes and tilted microphone head, with 100%/80% layers and review paths.

- [Fashion House export](session_fashion_house_export.md) — revision 12 exported and installed; authored paving, native vegetation bindings and unused material-slot fixes.

- [CSC adjacency replacement](session_csc_adjacency_replacement.md) — bundled first implementation, parity/live yield evidence, clean reload check and test preference restoration.

- [Expanded art merged into CSC](session_art-pack-merge-20261007.md) — six variants, shared Service gates, current ModBuddy setup and export repairs. [Art Pack split trial](session_optional-art-pack-test.md) is historical; current ownership is in [expanded building art](../project/docs/art/expanded-building-art.md).

- [Bakers Storage_L rev 01](session_bakers-storage-l-rev01.md) — additions + 27 reused props built; crane (animated) next; PIL/CON+PIL/AO/flour cataloguing open.
- [Reusable prop library](project_reusable-prop-library.md) — initial 33-asset Blender library delivered; preserve source identities/transforms/materials; source Construction/Pillaged behavior catalogued.
- [Pantry plant intake](session_pantry-plant-review.md) — 47 approved vegetation assets added to the live library; selection, verification and review-package paths.

- [Quarter building art plan](../project/docs/art/quarter-building-art-plan.md) — agreed 12 September 2026: retain Henno’s kit, Quarter roof/beam colours, assistant-built chunky prop scenes, storage/crane animation, Industrial Era variants and later cultural additions. [Internal docs index](../project/docs/README.md); studies now live under `project/docs/research/`.

- [Art Dropzone location and catalog intake](project_art-dropzone.md) — current Google Drive art/output root; research catalog scope and validation notes.
- [Civ VI 3D art skill development](../project/docs/research/art/civ6-3d-art-development.md) — first portable skill draft, texture-generation directives, trial plan and tool assessment; blacksmith 1,491-vertex Asset Editor parity confirmed by Henno.
- [Blacksmith v5 texture refinement](session_blacksmith_v5.md) — latest blend/package paths, authored relief, generator changes and validation.
- [Civ VI shape hierarchy feedback](feedback_csc_shape_hierarchy.md) — chunky structural forms must read in clay; bargeboard thickness must be measured across the slope.
- [Working Files reachable from Mac](project_working-files-mac-access.md) — Shadow's Working Files syncs via Google Drive `Other computers/My PC/`
- [Art performance & material architecture](project_art-performance-and-materials.md) — revised evidence boundary: resource discipline and geometry budgets; no measured universal Civ VI bottleneck ranking.

## Promoted docs

- Dynamic art properties → `project/docs/art/dynamic-art-properties.md`
- Bakers service notification UI → `project/docs/integrations/bakers-service-notification-ui.md`
- ComfyUI icon implementation notes → `project/docs/art/2d/icon-pipeline-implementation-notes.md`

## Resolved feedback

- Decal geometry visibility feedback was applied to the generic `civ6-gameplay` skill: `DecalGeometry` supports normal `GroupStates`; the limitation is reveal-animation keying, not general visibility.

## Local tooling lessons

- Attachment orientation correction (14 September AE screenshots): AST `m_orientation` is radians; AE displays degrees. Serialize `radians(-Blender_Z_degrees)`, not negative degrees directly. Prior exporter tests repeated the wrong degree formula and missed visible rotation errors. Unit scales within 1e-6 of 1 may be serialized as exactly 1; keep intentional non-unit scales. Bench dark-wood/UV work was explicitly deferred and reverted; focus remains placement parity.

- Scene export owns its TileBase templates; no existing output Workshop AST is required. Revision-08 metadata maps to bundled `level1_small`. Henno clarified 14 September: normal runs must install FGX/GEO/AST and merge the XLP, reusing existing MTLs. The runner now installs by default; `--no-install` is the opt-out. CSC defaults use explicit existing-material bindings and reject unmapped materials. Earlier 13-DDS preview runs predate this preference. Details: [scene exporter](../project/docs/art/blender-scene-export.md). Use local `project/tools/directxtex/texconv.exe` when texture conversion is needed; the old CivNexus6 copy fails at startup. Provenance/checksum: [DirectXTex](../project/tools/directxtex/README.md).

- Shadow's normal Windows environment has Python installed at `C:\Users\Shadow\AppData\Local\Programs\Python\Python312\` with the launcher at `C:\Users\Shadow\AppData\Local\Programs\Python\Launcher\py.exe`. If Codex command execution cannot resolve or run `py`/`python`, describe it as a Codex sandbox/runtime limitation, not as "Python is not on PATH" for the user. For Codex-side tests, use the bundled runtime at `C:\Users\Shadow\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` unless the user's local Python environment is specifically required.

## Active implementation reset

- Tailors contract-first restart → `session_tailors_contract_restart.md`

## Removed stale notes

- old session startup order;
- obsolete project notes location pointer;
- Q2 2026 roadmap snapshot;
- old memory-discipline feedback now superseded by repo documentation boundaries;
- CivAssetForge viewer prototype notes, which belong with the separate CivAssetForge repo rather than CSC memory.

- [Tailor lean-to atlas propagation](session_tailor_leanto_atlas.md) — both variants/state previews remapped, CON+PIL normal shading fixed, square cobbles synced; complete 11-FGX re-export installed and verified.
