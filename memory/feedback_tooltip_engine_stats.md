# Production-building tooltip stats — 20 October 2026

Henno reported duplicated Café Citizen-slot/specialist text while playing M&C.
The combined Leugi's Garden + M&C full-text override at load 3001 still carried
the line after the ordinary variants had been cleaned. Removed that source line,
two non-loaded example lines, and regenerated their SQL.

All production-building variants must omit their own CitizenSlots,
Building_CitizenYieldChanges and intrinsic local/regional Amenities because the
engine lists them below the authored description. This supersedes old guidance
to include a citizen-processing bullet in building-description order. Keep
Service destination-slot disclosures, notification fragments, Civilopedia
explanations, population transactions and cross-city effects explicit.

Durable workflow and audit:
`project/docs/workflows/localization-markdown-workflow.md`.
Tailors implementation contract and shared localization patterns now specify
every conditional variant. Generator/check, catalog/render validation and the
recursive source audit share the omission check. Regression tests execute all
four M&C/Garden action combinations in manifest load order.

Validation: 78 focused localization/contract/phase tests pass; generator --check,
pattern/source validation and Tailors contract validation pass. Full Stage 4
handoff still reports the pre-existing Bakers materials.yaml canonical design
mismatch (the Bakers public design was already modified before this task).
No gameplay fields changed; ModBuddy rebuild/game reload and visual review remain.
