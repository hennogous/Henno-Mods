# CSC Memory Index

`memory/` is agent-facing scratch/reference, not the durable home for collaborator-facing project truth. Durable notes should live in `project/docs/` or public `docs/`.

This folder was cleaned in June 2026: stale session notes were removed, and reusable implementation notes were promoted into durable docs.

## Active notes

- [Cafe prop scene](session_cafe_prop_scene_redo.md) — revision09 fits limestone paving to saved wall assembly and road05; B/H updated, AE prop edits preserved. Active decal master and PNGs now in `3D Art/Decals`; moved-image links repaired, validator passed. Atlas r035 unchanged. Handoff: `project/docs/art/cafe-regular-prop-delivery.md`.

- [Bakery prop-scene redo](session_bakery_prop_scene_redo.md) — revision08: oven UV3 uses original CSC_Atlas_E coals, shared material switched;49 emission flags disabled across20 affected ASTs to prevent stray glow. Geometry/othertextures/placements preserved; Currentr034 unchanged. Sources08 and evidence in bakery-props.md; cook/game pending.

- [Bakers completed Quarter bases](session_bakers_completed_quarter_bases.md) â€” Wind/Water bases 10/11 require all three service flags, reusing the shared art bridge and Tailors pattern; source checks pass, build/game review pending.

- [CSC map lab and native luxury study](session_csc_map_lab.md) — v4 Tailor2x Base-only/4x both+scaledfloor DEPLOYED and native-tested: six fresh paired Standard/Abundant maps, all targets/quantity/replay/pins pass. Tsites Std200/12,208/28,198/12; Abund199/24,232/24,172/44. Added73/94copies(total167). Original141flags/autostartfalse/diagnosticsfalse restored. No activecontroller. Report csc-tailor-density-native-20261017.md, fullresource inventories. Historical140-entryviewer unchanged.

- [CSC AI baseline](session_csc_ai_baseline.md) â€” COMPLETE: ten Online/Prince games to250, five vanilla Standard and five TAR-enabled Standard;110snapshots/20saves/115installedfiles verified,141originalmodflags/autostartfalse restoredfresh. B/Tcomplete259/132vanilla,252/133TAR;Basechosen153/287B,24/62Twhereavailable;Baseimproved32/115B,4/19T. Current report csc-ai-paired-standard-20261016.md; noAIchanges,noactivecontroller. Excludedtrial and game6same-turnweather/save recovery documented.

- Material returns: Henno confirmed during AI baseline work on 15 October that the prior material-return bug report was false; the mechanic works. Historical QA uncertainty is superseded.

- [Relationship icons and service labels](feedback_localization_relationship_icons_and_service_names.md) â€” category icons required across visible text, except plain Civilopedia chapter headings; MCUIS names omit venue suffixes. Shared contracts and generator checks enforce both.

- [Terrain-aware QA / manual handover](feedback_csc_terrain_aware_qa.md) â€” Henno is testing manually; automated game runs deferred. Terrain-aware planner draft is untested; qualify old ocean/forced-terrain evidence.

- [Scope and reuse](feedback_csc_scope_and_reuse.md) â€” audit across Quarters; prefer proven patterns and stronger contracts/validators over unnecessary new gameplay systems.

- [Gameplay QA trial](session_gameplay_qa_20261015.md) â€” expanded Tailors report: five confirmed defects; native auto-start works; five fixes now authorized. Follow the linked fix report for current verification and preference-restoration status.

- [Tailors completed Quarter base](session_tailors_completed_quarter_base.md) â€” all-three-flags base and Stage4 Fashion House alternate wired; source/logic checks pass, rebuild/game review pending.

- [SV interior outlines](feedback_sv_interior_outlines.md) â€” 14 October: thicker black contours around whole props and major building parts; keep small surface detail quiet.

- [Tailors storage direct-wall trial](session_tailors_storage_direct_wall.md) â€” Astra rebuild selected; new storage family now published with a shared 512Â² quadrant, canonical atlases and archive-bound backups; state UV/runtime integration pending.

- [Fashion House mustard dress](session_fashion_dress_mustard.md) â€” gown/sleeves recoloured; atlas r024 and native UV-only update installed, AE placements preserved.

- [Fashion House coach](session_fashion_coach.md) â€” revision 02, 937 exported vertices, standalone AE asset and shared atlas r023; fine trim removed per Henno's feedback.

- [Prop detail in paint](feedback_prop_geometry_detail.md) â€” Henno's coach feedback: omit small trim geometry, including seat rails; spend geometry on the main shapes, openings and support.

- [No Civilopedia referrals](feedback_localization_no_civilopedia_referrals.md) â€” player-facing text states information directly; never tells players to consult another page for requirements/effects/details.

- [Tailors Stage 4 Tourism](session_tailors_stage4_tourism.md) â€” all four services changed to +2 Tourism per supplied Fashion House; text and automated checks updated, in-game review pending.

- [Tailor garment rack](session_tailor_garment_rack.md) â€” wall rack and three garments extracted as one installed asset; 312 vertices, native readback and saved-source checks pass.

- [AE-owned 3D assembly workflow](session_ae_owned_art_workflow.md) â€” 13 October: skill workflow overridden; saved-AST icon/SV renderer delivered and repeatable on Textile Workshop. AE owns placement; selective geometry export remains future work.

- [Level 1 open ground interior](session_level1_foundation.md) â€” requested intact and S CON+PIL kit thresholds/floors removed, inward foundations completed; both FGX/GEO pairs installed and native readback verified.

- [Storage AE crash investigation](session_storage_asset_crash.md) â€” AO2 DDS header fixed and user-confirmed; six extension attachments restored; automatic full-dump capture runs at sign-in and re-arms after AE sessions.

- [Storage S/M AO rebake](session_storage_sm_ao_rebake.md) â€” four sources + canonical AO2 PNG rebaked in existing regions; CON+PIL UV2 repaired; all four FGX/GEO pairs and AO DDS installed, native readback verified.

- [CSC AI feasibility](session_csc_ai_feasibility.md) â€” native virtual-yield placement precedent, custom preview/AI boundary, exact material and builder scoring experiments still needed; research only.

- [Quarter lenses and placement](session_quarter_lenses.md) â€” minimal shared material/sales palette and improved-resource outlines, icon-coloured Bakers/Tailors districts; placement sampler retired. Automated/native checks pass, revised visual review pending.

- [Storage animation research](session_storage_animation_research.md) â€” v12 deck aligned to sled runners and gait, geometry-only update; v11 clip retains Cargo_TipUpright 90-degree sack lift and concealed rightward reset. Native/clearance checks pass; AE/cook/game review open.
- [Storage L open interior](session_storage_interior.md) â€” open upper floor/inward walls, foundation entrance extensions and 0.9 resize exported; current AO2 DDS already refreshed. CON+PIL later.

- [Bakers flour replacements](session_bakers_flour_integration.md) â€” original names retained; 156 placements updated; vertex savings and cook evidence in the durable report.

- [Stage Manager service-icon studies](session_stage_manager_icons.md) â€” four venue variants; latest crossed ballet shoes and tilted microphone head, with 100%/80% layers and review paths.

- [Fashion House export](session_fashion_house_export.md) â€” revision 12 exported and installed; authored paving, native vegetation bindings and unused material-slot fixes.

- [CSC adjacency replacement](session_csc_adjacency_replacement.md) â€” bundled first implementation, parity/live yield evidence, clean reload check and test preference restoration.

- [Expanded art merged into CSC](session_art-pack-merge-20261007.md) â€” six variants, shared Service gates, current ModBuddy setup and export repairs. [Art Pack split trial](session_optional-art-pack-test.md) is historical; current ownership is in [expanded building art](../project/docs/art/expanded-building-art.md).

- [Bakers Storage_L rev 01](session_bakers-storage-l-rev01.md) â€” additions + 27 reused props built; crane (animated) next; PIL/CON+PIL/AO/flour cataloguing open.
- [Reusable prop library](project_reusable-prop-library.md) â€” initial 33-asset Blender library delivered; preserve source identities/transforms/materials; source Construction/Pillaged behavior catalogued.
- [Pantry plant intake](session_pantry-plant-review.md) â€” 47 approved vegetation assets added to the live library; selection, verification and review-package paths.

- [Quarter building art plan](../project/docs/art/quarter-building-art-plan.md) â€” agreed 12 September 2026: retain Hennoâ€™s kit, Quarter roof/beam colours, assistant-built chunky prop scenes, storage/crane animation, Industrial Era variants and later cultural additions. [Internal docs index](../project/docs/README.md); studies now live under `project/docs/research/`.

- [Art Dropzone location and catalog intake](project_art-dropzone.md) â€” current Google Drive art/output root; research catalog scope and validation notes.
- [Civ VI 3D art skill development](../project/docs/research/art/civ6-3d-art-development.md) â€” first portable skill draft, texture-generation directives, trial plan and tool assessment; blacksmith 1,491-vertex Asset Editor parity confirmed by Henno.
- [Blacksmith v5 texture refinement](session_blacksmith_v5.md) â€” latest blend/package paths, authored relief, generator changes and validation.
- [Civ VI shape hierarchy feedback](feedback_csc_shape_hierarchy.md) â€” chunky structural forms must read in clay; bargeboard thickness must be measured across the slope.
- [Working Files reachable from Mac](project_working-files-mac-access.md) â€” Shadow's Working Files syncs via Google Drive `Other computers/My PC/`
- [Art performance & material architecture](project_art-performance-and-materials.md) â€” revised evidence boundary: resource discipline and geometry budgets; no measured universal Civ VI bottleneck ranking.

## Promoted docs

- Dynamic art properties â†’ `project/docs/art/dynamic-art-properties.md`
- Bakers service notification UI â†’ `project/docs/integrations/bakers-service-notification-ui.md`
- ComfyUI icon implementation notes â†’ `project/docs/art/2d/icon-pipeline-implementation-notes.md`

## Resolved feedback

- Decal geometry visibility feedback was applied to the generic `civ6-gameplay` skill: `DecalGeometry` supports normal `GroupStates`; the limitation is reveal-animation keying, not general visibility.

## Local tooling lessons

- Attachment orientation correction (14 September AE screenshots): AST `m_orientation` is radians; AE displays degrees. Serialize `radians(-Blender_Z_degrees)`, not negative degrees directly. Prior exporter tests repeated the wrong degree formula and missed visible rotation errors. Unit scales within 1e-6 of 1 may be serialized as exactly 1; keep intentional non-unit scales. Bench dark-wood/UV work was explicitly deferred and reverted; focus remains placement parity.

- Scene export owns its TileBase templates; no existing output Workshop AST is required. Revision-08 metadata maps to bundled `level1_small`. Henno clarified 14 September: normal runs must install FGX/GEO/AST and merge the XLP, reusing existing MTLs. The runner now installs by default; `--no-install` is the opt-out. CSC defaults use explicit existing-material bindings and reject unmapped materials. Earlier 13-DDS preview runs predate this preference. Details: [scene exporter](../project/docs/art/blender-scene-export.md). Use local `project/tools/directxtex/texconv.exe` when texture conversion is needed; the old CivNexus6 copy fails at startup. Provenance/checksum: [DirectXTex](../project/tools/directxtex/README.md).

- Shadow's normal Windows environment has Python installed at `C:\Users\Shadow\AppData\Local\Programs\Python\Python312\` with the launcher at `C:\Users\Shadow\AppData\Local\Programs\Python\Launcher\py.exe`. If Codex command execution cannot resolve or run `py`/`python`, describe it as a Codex sandbox/runtime limitation, not as "Python is not on PATH" for the user. For Codex-side tests, use the bundled runtime at `C:\Users\Shadow\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe` unless the user's local Python environment is specifically required.

## Active implementation reset

- Tailors contract-first restart â†’ `session_tailors_contract_restart.md`

## Removed stale notes

- old session startup order;
- obsolete project notes location pointer;
- Q2 2026 roadmap snapshot;
- old memory-discipline feedback now superseded by repo documentation boundaries;
- CivAssetForge viewer prototype notes, which belong with the separate CivAssetForge repo rather than CSC memory.

- [Tailor lean-to atlas propagation](session_tailor_leanto_atlas.md) â€” both variants/state previews remapped, CON+PIL normal shading fixed, square cobbles synced; complete 11-FGX re-export installed and verified.

- [CSC map setup preferences](feedback_csc_ai_map_setup.md) â€” future AI tests Online speed and Abundant; map surveys need counts rather than native saves. Fifteen-map [resource comparison](../project/docs/research/mods/csc-map-material-opportunities-20261016.md) complete for all eight Quarters.

- [CSC AI tuning](session_csc_ai_tuning.md) — ACTIVE SINGLE250 test same-save atomic-observer continuation supervisor4204, Desktop/Codex/csc-ai-quarter-resources-20261018/trial-v2e-resume; active-stage.json + job/live-status authoritative. Workshop extra80 + Quarter40 native fixture mechanism proved (UI120/far0); all native/pillage/pristine gates PASSED; game reached63, UI observer repaired and same autosave resumed; gap51..resume recorded. AI90/Builder50/native12/4/10, DX12 vs historicalDX11. Actual41source/121installed files archived. No competingTuner/source edits. Sparse15min heartbeat csc-quarter-resource-incentive-test; delete after this ONE run. T1-T5 deferred by user, do not launch automatically.
