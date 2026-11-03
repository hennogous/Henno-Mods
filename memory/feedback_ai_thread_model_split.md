# Model allocation for the CSC AI research thread

User decision: 29 October 2026. Scope: thread
`01a12a24-6714-7540-8d23-154b092106fe` and work explicitly delegated from it.
This supersedes this thread's earlier preference for Astra as the main model.
It is not a global model preference for unrelated threads or projects.

Henno will select **GPT-6.1 Sol as the main model from the next turn**. Do not
claim to change the main model yourself. This policy does not require changing
Codex global configuration or restarting an already running agent/game.

## Allocation

| Model | Default responsibility | Escalate when |
|---|---|---|
| **GPT-6.1 Sol (`gpt-6.1-sol`) — lead** | Main conversation, roadmap execution, routine GhidraMCP/source inspection, implementation, bounded native experiments, interpreting ordinary results and maintaining durable evidence. Own tasks end to end rather than merely relaying worker messages. | The experiment cannot distinguish competing explanations, native ABI/pointer assumptions remain risky, evidence contradicts the working model, or an architectural/gameplay tradeoff needs deeper judgment. |
| **GPT-6.1 Terra (`gpt-6.1-terra`) — optional bounded worker** | Structured log extraction, tables, report/document drafting, visual evidence review, and straightforward parsers/fixtures/refactors with clear contracts and checks. | Scope is ambiguous, native memory/observer correctness is involved, or repeated rework makes delegation uneconomical. Return uncertainty instead of inventing mappings. |
| **GPT-6 Astra (`gpt-6-astra`) — consultant** | Experiment design, difficult reverse-engineering/ABI reasoning, competing causal explanations, major planner/architecture decisions, and milestone critique of whether findings support a gameplay change. | Use a focused consultation at a real decision point. Astra should not stay active to poll a healthy game, relay status, or duplicate routine artifact review. |

Terra's suitability for particular code tasks is a hypothesis to evaluate by
correctness, rework and total cost, not a claim that it has already been tested
on these native tools. Sol remains the default for complex implementation and
live-game ownership. All models have the same evidence and safety obligations.

## Delegation and usage discipline

- Do small/sequential work in the lead. A task does not automatically need all
  three models. Add a worker only for a concrete independent deliverable or when
  it saves meaningful lead work. Add a reviewer at a useful gate, not on each poll.
- User authorizes the above model-specific delegation in this thread. Use exact
  model IDs when spawning the intended specialist. Prefer a fresh, focused
  context (`fork_turns="none"` when selecting a different model) with objective,
  relevant files/evidence, constraints, output contract and stop condition.
- Give Astra a compact evidence packet and a concrete question: what is known,
  what is uncertain, alternatives, proposed change and the decision needed.
  Ask around experiment design, conflicting findings or final interpretation;
  do not schedule consultations merely because time has passed.
- One native owner only. Reuse maintained controllers and scripts for waiting,
  phase checks, bounded capture and cleanup. Other agents read closed artifacts.
  Do not have lead, worker and reviewer repeat the same polling and analysis.
- Preserve independent review for native hooks/ABI assumptions and materially
  consequential conclusions. Independence means checking raw evidence, not
  adding multiple summaries of the same worker claim.
- Keep tool output narrow and aggregate logs with code. Avoid repeated full
  history/file dumps. Review only the source/evidence needed for the decision.
- Measure completed-task usage and rework, not just model token price. Cached
  input still counts. Separate uncached input, cached input, output (including
  reasoning), task scope, speed assumptions and actual billing uncertainty.
- Prefer useful coverage of the major CSC mechanisms over exhaustive engine
  catalogues. Stop at a useful decision boundary or declared limitation. Future
  probe executors should support graceful stop at an inactive boundary when the
  question is answered; never retrofit such control into frozen live sources.

## Why this changed

The local snapshot for the current foundation probe,20:25:04–21:14:58 UTC on
29 October, counted root and the two explicitly spawned Sol workers; automated
approval review was excluded. Cumulative counter deltas matched last-request
usage exactly, with no resets or duplicate-snapshot counting.

| Model | Uncached input | Cached input | Output, including reasoning |
|---|---:|---:|---:|
| Astra |242,620|26,785,792|44,061|
| Sol workers |389,604|52,069,760|105,074|

Raw total-token split was34% Astra/66% Sol. At published Standard credit rates,
the illustrative cost split was about82% Astra/18% Sol. This is **not a bill or
an exact subscription-allowance calculation**;99.2% of input was cached. It
shows why delegating execution while keeping Astra active as a polling and
duplicate-analysis supervisor was not an efficient arrangement.

On that date Terra's published Standard credit token rates were half Sol's.
Rates and included-plan accounting can change; verify before future estimates.
Sources: https://learn.chatgpt.com/docs/pricing and
https://learn.chatgpt.com/docs/models . Local measurement receipt and script:
`H/model-usage-foundation-current.json`, `H/summarize-model-usage.py`, where H is
this thread's visualization workspace.

## Continuing work

The model switch does not cancel or restart the foundation observation. Read
`session_ai_foundation_observation_20261029.md` and actual run artifacts first.
Do not rehost a game, duplicate a native client, revive old goals/automations,
or edit frozen sources because the main model changed.


## Completion delivery limit observed30October

The prior Sol worker finished and wrote its independent audit while the parent
had ended its turn, but no new parent response ran. Henno's next message resumed
the lead. Do not promise automatic idle-thread wake-up merely because subagent
completion is delivered. Keep an authorized orchestration turn active through
collection, or use a real explicitly authorized follow-up mechanism. No periodic
automation was created for this producer probe; do not resurrect old monitors.
