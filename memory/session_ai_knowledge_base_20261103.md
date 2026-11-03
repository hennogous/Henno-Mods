# AI knowledge base — 3 November 2026

User authorised consolidation of all AI research, including AI optimisation
chat01a12a24-6714-7540-8d23-154b092106fe, into a readable local website. Follow-up
authorised regular verified commits/pushes so it is phone-readable; final response
must provide both AI handbook and CSC public-docs links.

Canonical handbook: `project/docs/civ6-ai/index.md`. Current explanations are
organised by engine/native systems, CSC mechanisms and history/corrections/open
questions. Stable finding records: `data/*-findings.json`; original source
catalogue records normalised-text SHA256 (UTF8/noBOM/LF) for Windows/Linux parity.
Exact native evidence package hashes remain in the original reports.

Consolidation: seven native topics/52findings, eight CSC topics/47findings plus
navigation/source map, three history topics/12findings. AI optimisation paginated
to its beginning:50pages/492distinct visible turns,11Oct–1Nov. Tool outputs omitted;
chat is design/decision provenance and report discovery, not fresh raw-artifact
verification. Selected provenance and review limits in `data/thread-review.json`.

Important reconciliations: private ordinary yields not automatically inert/AI-only;
correct once-only supplied PLAYER_PLOT handler; Aqueduct0x04; fixedsign multiplier
and percent units; ordinary customer building gate distinct from prerequisites;
later strategy re-adoption; later UI coldstarts close old pending status only;
selection!=queue!=completion!=workingchain!=benefit; failed placement captures
establish observer-cost limitation, not non-response. Broad campaign remains paused.

Website uses existing Quartz4.5.2 installation/lockfile in `docs/`, separate AI
profile `docs/quartz.ai.config.ts`. Tool `project/tools/ai_knowledge/build.mjs`
stages ignored `docs/.ai-handbook/content`, builds ignored `.ai-handbook/site`.
Local Mermaid11.4.0 pinned to existing Quartz renderer, licence retained. Metadata
limits source search ordering to handbook, preserving normal CSC search. Phone
viewport scrollbar-width fix is AI-only. TypeScript, source/hash/finding/link
checks and actual browser checks are required before publishing.

Existing public Pages URL verified200: https://hennogous.github.io/Henno-Mods/ .
Old /CivSupplyChains/ returns404; config/rootAGENTS corrected. AI hosted path is
https://hennogous.github.io/Henno-Mods/ai/ . Existing deploy.yml extended to build
both content trees and place AI output in public/ai. No second Quartz installation
and no hosted Sites registration. User requested hosted phone reading after the
initial local-only brief.

`project/skills/civ6-ai/SKILL.md` is versioned; validated and installed to
`C:/Users/Shadow/.codex/skills/civ6-ai/SKILL.md`. Compact workflow routes to handbook
instead of duplicating conclusions. Independent realistic retrieval review passed.

No game, native instrumentation, AI tuning, mod deployment or paused-campaign work
was run for this consolidation. Existing unrelated dirty source/art/tool changes
must stay outside the documentation commits. Publishing/closure receipts follow
in the handbook maintenance record and Git history.
