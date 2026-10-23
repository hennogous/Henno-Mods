# CSC SQL readability

Henno requested on 21 October 2026 that the existing SQL formatting preference
be made prominent for agents and applied across active CSC SQL.

The maintained guidance is now near the top of the installed CSC `SKILL.md`,
with examples in `references/sql-formatting.md`. The historical MAB reference
links there rather than maintaining a separate copy. Short inserts (1–6 columns)
are horizontal and aligned; 7+ columns use vertical column/value/SELECT lists.
Keep labeled Districts/Buildings values aligned and meaningful grouping/comments.

`project/tools/quarter_contracts/format_sql_layout.py` implements the layout and
supports `--check`. It edits whitespace between tokens only; comments and quoted
text remain exact. The localization generator applies it before writing outputs.
The Bakers style catalog and Quarter tooling README reflect the same convention.

Formatting pass: 76 active CSC SQL files reviewed, 65 changed, plus one generated
localization example. Archives, retired Ruivo source and TaxesPolitics were outside
scope. Existing work was snapshotted first; locked Bakers SQL reference hashes
were refreshed only after exact token-preservation checks, with approvals intact.
Evidence: `Desktop/Codex/csc-sql-format-20261021/` (before snapshot, before/after
validator logs, SQLite replay, validation summary). No build, install or game run.

Pre-existing validation blockers were recorded before editing: stale Bakers
localization reference hash, missing `E.POLICY_RETURN_ADJACENCIES` expected build
coverage in a test, and Bakers material-contract reconciliation. Keep these
separate from formatting; do not silently refresh unrelated locks or approvals.

## Fuller SQL comments — 21 October 2026

Henno subsequently asked for plenty more comments in Bakers', Tailors' and AI
SQL. Added explanations throughout all nine core/Gold/M&C/AI files: file maps,
source/recipient direction, attachment-to-child tracing, eligibility gates,
population scaling versus integer stacks, additive M&C amounts, shared Lua
properties, Service persistence/venue handling, presentation anchors and the
separate AI placement/improvement/research inputs. Also corrected stale processor
names and population-path comments. The CSC skill records this fuller commenting
preference alongside its formatting rules.

Evidence is under `Desktop/Codex/csc-sql-comments-20261021/`: 395 comment lines
added, 14 old lines replaced; all nine files preserve executable tokens/literals,
formatting and BOM/line-ending style. Paired SQLite replay has identical schema
and table contents (415 successful statements, 55 identical populated-cache
duplicate-row collisions). Full suite retains 165 pass / 2 existing failures;
Stage 4 retains its exact prior localization/material errors. Four matching
Bakers SQL locks were refreshed for comments only; approvals were preserved.
