# Initial offline profile inventory — 28 October 2026

Follow-up completed: [full source/action audit](csc-ai-profile-source-audit-20261028.md), [Units/Builder native consumers](csc-ai-native-builder-consumers-20261028.md), and [archived decision cases](csc-ai-offline-chain-cases-20261028.md). Initial open questions below retain their original scope; follow-ups distinguish answered links from unresolved scoring.


Source inspection only, while Henno conducts manual QA. No live game access,
deployment, gameplay source edits or tests. This is a starting inventory, not
a complete current-runtime audit. Follow [the roadmap](../../integrations/csc-ai-roadmap.md).

| Source input | Where observed | Offline finding / next evidence |
|---|---|---|
| Improvement valuation | Data/CSC_AI_Basic.sql | Sets PSEUDOYIELD_IMPROVEMENT default30 and removes legacy CSC improvement list. Trace the effective native valuation; do not assume the number is minimal or optimal. |
| Builder production preference | Data/CSC_AI_Basic.sql | UnitPriorityBoosts entry Favored1/Value50 in the Units system. Buildings/Districts boolean findings cannot be transferred to Units without tracing its handler. |
| Builder movement | Data/CSC_AI_Basic.sql | Declares +1 with major-AI owner and Builder subject requirements. Inspect gates/overlap offline; actual application and useful travel/completion benefit remain separate tests. |
| Cross-city Builder contracts | Data/CSC_AI_Basic.sql | Sets Required City parameter2 to -1 for Build Unit nodes in Build City Improvement. This permits a contract scope; it does not prove reachable supply or successful recruitment. |
| RH separation | ModSupport/ModSupport_RH_AI.sql | Existing header deliberately leaves global pseudo-yields, UnitPriorityBoosts, movement and behavior trees to RH. New objective allows narrowly evidenced CSC gaps to be addressed, not blanket duplication. |
| RH CSC building guidance | ModSupport/ModSupport_RH_AI.sql | Contains historical Workshop forecastV6 and strategy coverageV7 sections. Source comments describing numerical rewards need review against the newly traced Buildings Favored semantics; no correction applied to gameplay source during QA. |
| RH foundation guidance | ModSupport/ModSupport_RH_AI.sql | Contains foundation-priorityV8 section. Audit effective preference sign, lifecycle and extra-placement effects rather than equating Value with priority strength. |
| Profile selection | Data/CSC_AI_Profile.sql; project/modbuddy/CivSupplyChains.actions.json; project/tools/ai_tuning/configure_profiles.py | Profile marker defaults OFF; generator declares separate Basic/RH actions. Full action-gate/load-order verification is pending; no current installed-profile claim. |

All mod source paths above are relative to `Civ Supply Chains/` unless prefixed
`project/`. Next offline work: finish source/action inventory; join inputs to
known native consumers; identify redundant/unsupported assumptions; inspect the
Units/Builder consumer independently; extract representative archived site and
queue cases for the planner. Live calibration waits until human QA is finished.
