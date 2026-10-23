# Lua readability pass — 21 October 2026

Henno requested a commenting pass after the SQL readability work. Reviewed all
35 active CSC Lua files and added focused comments in 31. Four small include/read
wrappers already explained their purpose. Archives and the retired Ruivo source
were outside scope; original credits and imported UI implementations were retained.

Comments explain data flow, units and invariants: gameplay/UI authority, SQL
property and bit contracts, per-customer rounding, deterministic mutation order,
route snapshot validation/revisions, persistent Wonder Services versus current
benefits, material planner safety/RNG, lens classification/masking, notification
stack/cache behavior and compatibility hook/cache/pooling details. Corrected an
obsolete loading-event comment and clarified diagnostic snapshot serialization.
The CSC skill now carries a short Lua-readability directive near its SQL section.

Evidence lives under `Desktop/Codex/csc-lua-comments-20261021/`: exact pre-edit
Lua snapshots, comment-only patch, executable-token and syntax audit, validator
logs and adjacency parity output. The token scanner handles escaped quoted text,
long-bracket strings and both Lua comment forms. Lua compiler syntax checks adapt
Civ VI type annotations and the inherited UnitPanel's Havok tutorial structure;
they are offline checks, not a claim of native runtime acceptance.

All 35 files preserve executable tokens and BOM/line-ending style. Full Quarter
suite remains 165 pass / 2 pre-existing failures; Stage 4 handoff retains the same
localization-lock/material-contract errors. Policy returns pass 220 cases;
historical adjacency parity passes 1,465 comparisons, 61 rules and 610 modifiers.
Lens/placement and AI UI filtering/report suites pass. Material-map Lua tests
pass five captured maps, ten abundance profiles, initialization guards,
repeatability, coverage/census matching, zero shared RNG draws, rollback and
two-resource/optional-mapping paths. No game/build/install.
