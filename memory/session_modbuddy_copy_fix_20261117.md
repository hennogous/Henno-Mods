# ModBuddy duplicate Content copy fix — 17 November 2026

Henno reported Civ6.targets line154: DestinationFiles 1 vs SourceFiles 2. The SQL
consolidation had mapped two former schema Content entries to the same shared
Data/CSC_Q_ALL_Schema.sql path. Removed the repeated entry, keeping Schema/Common
together. No action JSON, shared SQL, SDK targets or gameplay changes needed.

Native MSBuild 12 reproduction uses the SDK Copy task's exact attributes. Two
Schema sources reproduce the error. Fixed copy passes all 287 current Content
files and byte-for-byte source/output comparisons. Temporary 125MiB copied assets
removed; small projects/logs are in Desktop/Codex/csc-modbuddy-copy-fix-20261117.
This qualified copying; art cooking was not run.

civ6proj_actions.py now checks duplicate Content destinations using Windows path
normalization. Action check, shipping tests and Quarter content-wiring validation
share that helper, avoiding the set conversion that previously hid duplicates.
Regression covers the actual project and case/slash/dot aliases.

Preserve unrelated art/Pedia/lens/project work. Stage only the duplicate-entry
removal from the project, along with validator/tests/docs. Reload CSC in ModBuddy
if its in-memory project has not picked up the external file edit before rebuilding.

Validation: all 201 Quarter tests and 11 ModBuddy action/packaging tests pass.
