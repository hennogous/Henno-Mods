# Art workspace relocation — 2026-09-10

Henno moved the working art/output folders to:
`/Users/henno.gous/Library/CloudStorage/GoogleDrive-henno.gous@gmail.com/Other computers/My PC/Working Files/Dropzone/Codex`

This is the current destination for art/research artifacts. It contains blacksmith
v1–v5, imagegen, texture-reference-review, art-guidance-review and research. The
Henno-Mods repository and versioned skill files remain in the Play checkout unless
subsequently moved. Do not recreate art outputs at the old output path by habit.
Inspect hardcoded paths in the earlier build scripts before rerunning them.

Research intake: four supplied JSON catalogs; review saved in the new root at
`research/catalog-intake-review.md`. 10,019 geometry records include 3,708 DIS_ entries;
seven selected building vertex/triangle counts agree with the earlier catalog. Unit
formation arithmetic is consistent, but variant averaging/material field semantics
need generator inspection. 514 records have errors and 54 exceed one million vertices.
No engine bottleneck or asset ceiling follows from these metadata records.

Market intake completed: `research/market-study/README.md` has source hashes, map/UV
sheets, material ablations, normal-Y alternatives, raw JSON, scripts and a packed
`Market-material-study.blend` preview. Repo summary: `project/docs/firaxis-market-study.md`.
Completed mesh 480v/294t/1mat; UV1 union 10.05%, UV2 1.41%, custom normals. Source blend
untouched. Base-only rendering already carries substantial local depth; normals
reinforce it. Preview shader/tangent convention is not validated against the game.

Library intake: `research/library-study/README.md`, with a packed
`Library-material-study.blend`, CN6-derived raw mesh JSON, coverage and material/mip
comparisons. CN6 supplied after initial FGX intake: 999v/537t in ONE mesh but TWO groups
(campus843v/445t, foundation156v/92t). Campus-only UV1 17.059%, UV2 2.077%. Foundation
material missing, shown gray. Construction counts from GEO only, no CON CN6 yet.
Mip variants have explicit MANUAL_MIPS and equal top levels but different lower levels;
ordinary B artwork differs and variant state usage is unverified. Repo summary:
`project/docs/firaxis-library-study.md`. Originals untouched; no Asset Editor validation.

Henno's correction: explicitly named MIP files are very rare in the Pantry; the campus
variants may be among the only examples. Do not treat these as a standard Firaxis
practice or a skill-development priority. Removed their rationale from the art skill;
default to ordinary automatic mips and investigate filtering only when useful.

Campus family follow-up: `research/campus-family-study/README.md`; repo summary
`project/docs/firaxis-campus-family-study.md`. Direct Library CON/PIL and University
CN6 analysis. Campus AO regions for intact/CON/PIL/University are mutually disjoint
and internally nonoverlapping, confirmed by polygon clipping (1e-12 area tolerance).
Analytical AO areas 2.079/2.135/2.135/10.014%, total16.364%; raster estimates differ
slightly. CON/PIL have identical indices, UV1 and N/T/B arrays; positions within .0001,
but different UV2. Skeletons/UV3 differ, so do not call them identical game states.
Each CON/PIL file1567v/833t; University2742v/1478t. Foundation MTL now supplied: B/N/G
only, no AO; its actual named DDS maps still missing. Skill now conditions AO validation
on bound maps and favors independently allocated state AO in a shared map. Parent-bake
reuse remains an explicit compromise. No AST/runtime visibility or bottleneck proof.
