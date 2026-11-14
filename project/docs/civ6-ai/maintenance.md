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

The installed skill is a separate Git repository. Its canonical files are
`SKILL.md`, focused engine references and `references/engine/findings.md`.
The old native topic paths in this repo are pointers, preserving existing links.

The JSON registers and source catalogue under `data/` are historical migration
snapshots, not another live publishing database. The former renderer remains
under `project/tools/ai_knowledge/` for historical reproducibility; it is not
part of routine research or deployment.

Large saves, native dumps and test packages remain in their evidence stores.
Record paths and hashes; a Desktop path is a locator, not a portable backup.
No game binaries or private transcripts belong in the public repositories.
