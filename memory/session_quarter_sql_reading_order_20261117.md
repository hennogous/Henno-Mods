# Quarter SQL reading order — 17 November 2026

Henno wants the main Quarter files to read as an intentional implementation story:
types, resources, Stage 1 material improvements, Quarter, Stage 2–4 buildings and
Services/economic terms, plumbing, UI/art. This supersedes the old nine-section
template and the temporary end-of-file transaction catalogue layout.

Bakers/Tailors reorganized accordingly. Authored material/building/route terms
are in section 5; stable native bindings, property consumers and requirement
details are in section 6. Each core file has one building-transaction INSERT and
one yield-leg INSERT. Batch only identical conflict policies and column lists;
keep dependent temporary generators together. UI descriptions, notifications,
previews and art properties are in section 7. Drifting comments/empty migration
headings removed and replaced with explanations of the current ownership.

Henno reaffirmed CSC skill formatting: 1–6 columns horizontal/aligned, 7+ vertical,
Districts/Buildings field labels retained. Every Districts/Buildings row now has
those labels. The style-policy YAML and AGENTS describe the same outline.

All original literal row writes and other SQL expressions conserved. Disposable
copies of the existing game cache execute both versions identically: 466 tables,
64,196 rows. Existing 83 transaction tests (including 16 option combinations),
123 AI economy tests and both core style profiles pass. Offline fixture loaders
now select tables/bounded generators instead of relying on a bottom-of-file
declaration marker. No game/controller/Tuner launch.

Preserve separate work in progress, especially Tailors PLUNDER_GOLD and unrelated
AGENTS/localization locks. Shared SQL structure reference:
project/docs/integrations/csc-shared-sql.md.
