# Maintaining CSC AI knowledge

Henno chose repo Markdown plus the `civ6-ai` skill on 11 November 2026.
The AI handbook's Quartz build, publication checks and source-catalogue refresh
are retired. The public CSC player documentation site remains independent.

## One authoritative home for each kind of knowledge

| Knowledge | Maintained home |
| --- | --- |
| Reusable engine mechanisms and AI-N findings | `civ6-ai/references/engine/` in [the skill repo](https://github.com/hennogous/civ6-ai) |
| CSC rules, tuning and AI-C findings | This repo's Markdown, including [findings](findings.md) and focused CSC topics |
| Current scope and next dependency | [Status](STATUS.md) and [numbered roadmap](roadmap.md) |
| Detailed observations, failures and artifacts | Dated [evidence reports](evidence.md) |
| Session carryover | Repo `memory/`; promote durable truth to the homes above |

## After an investigation

Lead the report and progress updates with what we learned, its practical
implication and the next useful action. Explain uncertainty when it changes that
interpretation or action; keep detailed evidence qualifications with the evidence.
Assess observation gaps against the measurements they affect. Record partial
coverage explicitly and recover useful results from completed games before
considering a repeat. Diagnostic completeness and safe game/native operation
need separate checks.

1. Record the result in its dated evidence report: exact input identities, intervention, native consumer, observed outcome and limits.
2. Update the focused engine reference/AI-N entry if it teaches reusable engine behaviour. Update CSC Markdown/AI-C entries for the mod application. Link the evidence rather than copying a diary everywhere.
3. Preserve stable IDs and superseded assertions. Allocate the next unused ID from the maintained register; inspect it rather than inferring the next ID from an old report.
4. Update status and the affected numbered roadmap item. Distinguish input, proposal, native comparison, request, execution, completion and realised benefit.
5. Check changed links and evidence scope. Run meaningful code tests when implementation changes. Knowledge edits do not need Quartz, Mermaid rendering or a website deployment.
6. Make regular scoped commits and pushes in each affected repo. Keep unrelated workspace changes out. Review CE contributions with Henno before any upstream PR.

On Shadow, the canonical Git checkout is `C:\Users\Shadow\.agents\skills\civ6-ai`,
beside `civ6-gameplay` and `civ6-art`. Codex loads the same checkout through
`C:\Users\Shadow\.codex\skills\civ6-ai`. Its maintained files are `SKILL.md`,
focused engine references, and `references/engine/findings.md`.
The old native topic paths in this repo preserve links to the skill. The
original `project/skills/civ6-ai/SKILL.md` and the local `docs/.ai-handbook/`
render tree belong to the retired handbook workflow.

The JSON registers and source catalogue under `data/` are historical migration
snapshots, not another live publishing database. The former renderer remains
under `project/tools/ai_knowledge/` for historical reproducibility; it is not
part of routine research or deployment.

Large saves, native dumps and test packages remain in their evidence stores.
Record paths and hashes; a Desktop path is a locator, not a portable backup.
No game binaries or private transcripts belong in the public repositories.

## Keep evidence useful and bounded

Henno's15 November retention preference is to keep vanilla/untuned baselines,
tests relevant to the current push, reusable tooling and source repositories.
Write useful findings and compact results into the repo, then purge superseded
raw experiments instead of accumulating a comprehensive evidence archive.
Record which experiment folders were retired so historical artifact links are
understandable. Current packages, active runs and required replay inputs stay
protected. Some closed package assets share disk storage through hard links;
copy an archived package out before editing it.
[15 November retirement list and protected comparison sets](retired-artifacts-20261115.json).
