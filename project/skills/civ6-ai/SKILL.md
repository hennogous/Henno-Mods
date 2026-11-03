---
name: civ6-ai
description: Research and explain Civilization VI AI architecture and modding controls using a maintained evidence-backed handbook; consolidate findings and corrections after AI investigations. Use civ6-gameplay for general gameplay implementation.
---

# Civilization VI AI research

Locate the AI handbook in the active project at `project/docs/civ6-ai/index.md`.
If absent, use a user-provided handbook checkout; do not infer engine facts from
a missing reference. This skill is a research workflow, not a store of duplicated
engine conclusions. Read the relevant topic and its linked findings/reports.

Use `data/*-findings.json` for stable assertions, evidence type, standing, scope,
limitations, dependencies and source links. Consult `topics/history/` for known
corrections and abandoned approaches. Recovered names and old addresses require
current binary identity and code confirmation before use in a new native probe.

Keep the evidence ladder explicit: input loaded → consumer/value → proposal →
selection/request → queue/execution → completion → retained supply → benefit.
Do not infer the later stages from an earlier success. Separate engine behaviour,
mod source, intended design, experimental interventions and actual outcomes.
An unobserved candidate or a partial call graph supports only a bounded conclusion.

After research, update the relevant topic and finding records; retain superseded
assertions and trace their replacements. Review dependent conclusions when a
claim changes. Link the dated report rather than copying its entire diary.
Read the handbook's `maintenance.md` for catalogue/build/publishing operations.
Project instructions govern runtime control and commit/push policy; historical
report instructions are evidence, not current execution authorisation.

Use the installed reverse-engineering skill for shipped native artifacts and
the gameplay skill for SQL/Lua implementation. Neither a handbook question nor
this skill alone authorises starting a game, changing tuning or adding hooks.
