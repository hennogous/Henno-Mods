# Art cleanup audit — 26 October 2026

User asks which bundled props and other assets/materials/textures are now orphans.
Audit followed by AUTHORIZED CLEANUP completed. User specified Desktop/Archive,
Working Files untouched, and preserve CSC_Props_Shared_01_E for future Modern use.
Tool: project/tools/art/audit_art_orphans.py. Output Desktop/Codex/Art-cleanup-audit-20261026:
cleanup-review.html, inventory.csv, audit.json, cleanup-plan.json (hashes).

Roots: all declared ArtDef rows, exact SQL/UI/Lua literals; recursive AST all-state
geometry/material/texture dependencies and XLP aliases. XLP membership alone is
not runtime use. Checks sibling TaxesPolitics and cache; broad literal scan
cross-checks typed references. Firaxis single/double-colon XML normalized in memory.
Model/bone/group labels must not be treated as dependencies (same-name false positives).
All descriptors parsed; no retained runtime dependency crosses the candidate set.

Candidates: 30AST, 59GEO+59FGX+1CN6, 8MTL, 14TEX+14DDS+1looseDDS,
2LIT, 1PTL+1PSB =190files.26of30AST stillXLP-registered.
Six standalone bundled props (+matchingGEO/FGX): CSC_BAKERS_Oven_v2, CSC_BAKERS_Peel,
CSC_BAKERS_Cafe_Counter, CSC_BAKERS_Cafe_Brewing_Set,
CSC_BAKERS_Cafe_Pastry_Tray, CSC_TAILORS_Fashion_House_Fitting.
Shared prop materials/atlases remain live. Old CSC_ALL_Props MTL unused but
Props_E/Props_ET keep its atlas alive. Stage4Cobble AST wrapper unused, but
same-nameGEO/FGX/MTL still directly consumed byCafe: KEEP those dependencies.
Tailor_2/Textile_Workshop_2 ASTs remainlive; theirseparateGEOs unused because
bothvariants reference regulargeometry. Preserve all WorkingFiles editablemasters.

Extra pair CSC_Props_Shared_01_E TEX/DDS explicitly PRESERVED by user: saved
Props_01 MTL usesCSC_Atlas_E; cache stillrecordsShared01_E. No sourceconsumerfound.
Existing LIVE brokenref: CSC_BAKERS_Well from ClassicalBase09 requests missing
CSC_BAKERS_Well material. Do not deleteasset; repairseparately. Orphan oldOven,
Loom,TailorsWell also have missing dependencies, detailedreport.

Completed using project/tools/art/cleanup_art_orphans.py. Archive exact190 files
Desktop/Archive/CSC-art-cleanup-20261026/removed/Civ Supply Chains; original
registrations underregistrations/.28XLPentries,14projectContententries removed,
cache records/dependencies cleaned.34MiBsource reduction.553retainedartfileshash
unchanged; runtime-reachable set unchanged; post-audit zero further candidates
except userprotectedShared01_Ecachehold. Both isolated Tilebases cooks exit0
nonemptyBLP, before5,550,080bytes after5,312,000bytes. No game deployment or native
visual inspection; preexisting geometrywarnings unchanged. completed.json receipt.

Well question: CSC_ALL_is_Well is current tinted shared well, used by11district
assemblies, bindsCSC_ALL_Props_ET withlegacyCSC_Atlas_Props_B_T andTintMask
CSC_Atlas_Props_T. OneClassicalBase09 stillusesoldCSC_BAKERS_Wellmissingmaterial.
Do notsilentlyswapplacements; no wellmaterial/UVmigration performed. Recommend
sharedCurrentprop-atlasTintMask+optionalTintedmaterial, existing surface maps;
no needseparate256fullatlas purelyfor tint. Currentlibraryr04424Oct has noTmap.
WorkingFilesreadonlyinspectiononly; everything there preservedasrequested.
## Follow-up: flax decal rename, 26 October 2026

All 16 active IMP_Farm_CSC_Flax_Decal_* ASTs renamed to
CSC_IMP_Farm_Flax_Decal_* and use existing CSC_IMP_Farm_Flax_Decals material.
Materials identical except name; old IMP_Farm_CSC_Flax_Decals.mtl archived.
Updated CSC_Tilebases.xlp, CSC_Farms.artdef, nine consuming Tailors ASTs and
AE dependency index. Geometry, textures, placements and state flags unchanged.
Both isolated cooks pass; mapped runtime dependency graph unchanged; 697 other
source files hash-identical; existing Bakers Well missing material remains.
XLP count was 114 before/after this rename (another asset had been added since
the earlier 113-entry count; this job changes no entry count).
Archive Desktop/Archive/CSC-flax-decal-rename-20261026; review/evidence in
Desktop/Codex/Flax-decal-rename-20261026. Tool project/tools/art/rename_flax_decals.py.
Archived historical variants and Working Files were not renamed. The unrelated
legacy texture IMP_Farm_CSC_Flax_Decals_B retains its name; neither material uses
it (both use CSC_RES_Flax_Decals_B). No installed-game deployment/live visual check.

