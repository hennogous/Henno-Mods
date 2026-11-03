# Maintaining the AI knowledge base

The canonical content lives in `project/docs/civ6-ai/`. Dated investigation
reports remain under `project/docs/research/mods/` and implementation records
under `project/docs/integrations/`. The existing Quartz checkout in `docs/`
builds both the CSC player documentation and this separate handbook.

## Finish research by updating the model

For a new investigation, identify the affected topic and existing finding IDs
before adding new prose. Record the exact assertion, evidence type, scope,
limitations and source links in the relevant `data/*-findings.json` file.
Add a new finding ID for a distinct assertion; preserve existing IDs so links
remain useful across revisions. Topic pages provide the readable explanation.

The same mechanism can have a native finding and a CSC application finding.
Use cross-topic links and `related` finding IDs to connect these views; use
`depends_on` only for an actual evidential dependency. Do not infer causality
merely from related records.

When evidence challenges an existing finding, record the challenge and check
dependent findings. Retain superseded records and explain what replaced them.
Update the current topic, corrections page and relevant evidence-page notice.
Do not silently rewrite old observed results as though the new interpretation
had been known at the time. Scoped negative findings stay scoped.

Keep generic engine behaviour distinct from CSC application, intended design,
current implementation and historical experiments. An old chat instruction or
report's pending section never authorises a new game or restarts paused work.

## Evidence and portability

`data/source-catalog.json` records original paths, titles, document categories,
byte sizes and SHA-256 hashes. It is a catalogue of reviewed source documents,
not a claim that every sentence is current. The compact thread-review record
preserves AI optimisation coverage and selected decision provenance; the full
private chat is not exported into the website.

Catalogue document hashes use UTF-8 without BOM and LF newlines, so Windows and
Linux checkouts compare the same text. Exact-byte native artifact hashes remain
in the original reports. The source-map snapshot also preserves its review-time
file hashes; those may differ after Git changes line endings.

Large evidence stores remain external: native databases, exported dumps, save
files and game packages are identified by paths/hashes in their reports. A link
to a Desktop folder is a locator, not a portable backup. Preserve the named
evidence packages separately when moving hosts. Do not copy game binaries or
whole chat transcripts into the public handbook.

## Build and read locally

From the repository root:

```text
node project/tools/ai_knowledge/build.mjs --update-catalog
node project/tools/ai_knowledge/verify.mjs
node project/tools/ai_knowledge/serve.mjs
```

Open `http://localhost:8091/`. The build prepares an ignored content projection
at `docs/.ai-handbook/content/` and writes the generated website to
`docs/.ai-handbook/site/`. Those are generated copies; edit the canonical
Markdown and JSON, then rebuild. `--update-catalog` deliberately refreshes the
source hashes; use it after reviewing changed sources. Without that flag a stale
catalogue fails the build.

The handbook uses `CSC_AI_HANDBOOK=1` and a separate configuration derived from
the existing Quartz setup. Normal public CSC builds keep their normal content
and configuration. No second Quartz installation is required.

## Commit and publish

Henno requested regular commits and pushes of handbook work on 3 November 2026.
At useful verified checkpoints, commit the affected handbook, cited report and
publishing files, then push. Keep unrelated mod/art/tool changes out of those
commits. Henno subsequently clarified: commit and push findings without extra
website, link or deployment QA. Preserve checks needed for actual gameplay/native
changes; publishing is not another experiment gate. Refresh the source catalogue
when its inputs change so the normal build can consume the committed content.
This is an ongoing research-completion convention, not a scheduled background job.

The existing Pages workflow builds the CSC site and places this handbook under
`/ai/` in the same deployment. For its hosted links the AI build sets
`--base-url=hennogous.github.io/Henno-Mods/ai`. The source and local site remain
usable independently of publishing.

## Review checklist

- Assertions link to their reports and identify the evidence actually obtained.
- New findings have valid, unique IDs; dependencies and source paths resolve.
- Corrections reach the current explanation and affected historical reports.
- Static analysis, runtime observation and inference remain distinguishable.
- Outcome claims include costs, clocks, cohorts and comparison limitations.
- Build, maintained-page links, diagrams, search and phone layout are checked.
- Source catalogue and the chat-review coverage accurately describe their scope.
