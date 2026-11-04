# Local Mill unit-step source repair —4 November2026

User confirmed: Mill bonus only after the Mill is built in that Quarter, and
only to that Quarter. Authorized implementation of local scope and simpler
adjacency representation. Later explicitly chose **keep FireTuner open; finish
offline checks only**. No launch/load, FireTuner interaction, Frida attachment,
installed deployment or native save verification for this task.

Source changes: the two Bakers Mill rows explicitly CITY; `CSC_AdjacencyUnitSteps`
Wind1/Water3; compile exact four active +1 roots; legacy numeric definitions kept
dormant, old twenty building attachments removed; actual core local functioning
building/Quarter checks and exact GP building location; UI manager lifecycle
fallback; normal reconciliation clears old bit flags and writes new steps.
Generic signed encoding and all placement-policy weights unchanged. Planned
first-Mill scoring remains distinct from current income.

MAB read-only provenance: generic scope defaults PLAYER even for a building.
MAB supports CITY and honors it; CSC omitted the override. Thus CSC integration
error, not evidence of a broken MAB city collection. Reference mod unmodified.

Durable source/status and test receipts:
[implementation report](../project/docs/research/mods/csc-ai-local-mill-unit-steps-20261104.md),
[scope review](../project/docs/research/mods/csc-ai-mab-building-owner-scope-20261104.md),
[current adjacency contract](../project/docs/integrations/csc-adjacencies.md),
AI-C056/COR-009. Desktop receipts `Codex/csc-local-mill-steps-20261104/`.
Do not treat offline graph parity as native yields, saved-game attachment
migration, actual forecast magnitude, improved choice or empire benefit.

Unrelated dirty Quarter lens files were present before this task and excluded
from its commits. CSC skill reference updated separately; commit30ee60f pushed.

Final source freeze independently reviewed: Core5f193144…7eed, testde4a81ce…3639.
Focused9, frozenparity61rules/1465cases/55sources, policy220, scanner9,
edge48+48+384, placement6, SQLlayout3 and handbookprepare2 allPASS. Graph has
610legacydefinitions,20disconnectedMilldefinitions,4newsteps,594activepayouts.
Offline receipt +eightfilesource-review bundle saved under the Desktop root.
Quartz handbook build/verify pass; repeat final build after evidence text update.
