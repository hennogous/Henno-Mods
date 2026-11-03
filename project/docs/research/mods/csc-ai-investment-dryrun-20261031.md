# Investment review and guarded-host dry run — 31 October 2026

After the [native admission trace](csc-ai-work-admission-20261031.md), Astra
recommended stopping selector tracing and making one planner investment decision.
The thin offline bridge is implemented and tested. **No complete real investment
case is established yet:** the bounded archives support deferral and a historical
Both-geometry control, not permission to place another Quarter.

## Implemented boundary

`project/tools/ai_tuning/investment_review.py` composes the existing strict
Both-or-real-+4 shortlist and chain coordinator; it does not create another
weighted utility model. Unknown costs, conflicts and capacity remain unknown.
Accepted/selected unfinished native commitments produce an observation/reconciliation
decision, not a duplicate request. A single fully evidenced Both-material option
can produce the host's player/city/quarter/source/materials shape for review.
Credible material development remains conditional; it does not add already-counted
resource adjacency again. Every result has `action_authorization=false`.

There is an explicit implementation gap: the installed assistance host currently
requires Both materials. A +4-only option without Specialty is deferred as an
unsupported host route, rather than silently passed through that backend. This
first bridge neither generalizes its foundation guard nor enables new placements.
Original-human/settings, current Quarter bindings, ownership, fresh native quotes,
caps/cooldowns, pending receipts and native/UI zero-progress checks remain the
installed host's responsibility. It remains the sole economic mutator.

`preview_host` executes the actual `CSC_AI_OpportunityPolicy.lua` Route/Funding
functions in an isolated Lua51 VM. It makes no Civ connection and duplicates no
funding formula in Python. The project and installed policy hashes both equal
`31fff6f5a40908dbbdd1a4507bf739b41fa465d68d87bacda69ff32a22731233`.
The preview covers an explicitly sourced subgraph and next tile, not globally
optimal routing, future quote freshness, full investment value or execution.

## Bounded real cases

| Case | What the archive proves | Decision supported |
|---|---|---|
| Source110 AI3/city131073 Bakers2338 | Native-legal opportunity, adjacent Specialty Honey, no mapped Base | Defer the start; neither a failed zero Plot preview nor CSC-only1P projection is a validated candidate total |
| Historical candidate517 AI2/city65536 Bakers1278 | Both geometry, actual quoted paid assignments and native0% foundation; Rice becomes working29 after foundation16; completion first observed71 | Geometry passes; do not backdate later material work into a credible plan at16 |
| Existing Bakers2419/Honey2344 | Legal/unlocked Camp work; recommended, but no Honey job captured in the bounded tests | A work-review option, not a proven assignment or demonstrated better investment |

These are separate historical/player/clock contexts, not three alternatives
simultaneously available to one empire. The older case does not establish current
legality, working Base at placement, uninterrupted retention, whole-chain costs,
stable original-human proof or net benefit. No +4 total is invented.

For the archived Sugar1204 step at16, the actual current host-policy preview
returns route[1204], price40, AI funds37, fallback3, reserve25 from treasury
72.39453125. This exactly reproduces the preserved receipt. Gross income is
explicitly derived from observed net income plus maintenance; site spend is
derived from the recorded remaining300 cap. The observed required subgraph is
not presented as a complete map. Reproducing finance does not authorize the
foundation or prove the old early placement was good or bad.

The bounded search inspected two assisted-site records in the candidate517
archive and a second study's report, plus the current source110 captures. It did
not establish a fully ready working-Base start. The extraction records exact
inputs and missing fields instead of launching a fresh campaign to fill them.

## Usage and verification

Run with an explicit output outside the source tree; existing outputs are refused:

```text
python -B -X utf8 project/tools/ai_tuning/investment_review.py --snapshot STRICT_SNAPSHOT.json --output NEW_REVIEW.json
python -B -X utf8 project/tools/ai_tuning/investment_review.py --host-input SOURCED_ROUTE_AND_FINANCE.json --policy "Civ Supply Chains/Lua_UI/AI/CSC_AI_OpportunityPolicy.lua" --output NEW_PREVIEW.json
```

The second command requires Lupa's Lua51 runtime. The input snapshot follows the
existing evaluator/coordinator contract; incomplete archive packets are not
silently padded into that schema with zero costs or fabricated supply eligibility.
Nine new tests and49 combined evaluator/coordinator/shortlist/review checks pass.
They cover existing commitments/footprints, missing costs, original humans,
credible future materials, the +4 host gap, actual Lua funding/subsidy opt-out,
caps, unknown treasury and foreign ownership. A real historical CLI replay also
matches the archived own/subsidy receipt. Synthetic positive cases validate code,
not actual AI improvement or a full real investment decision.

Evidence: `H/planner-decision-20261031/archive-case.json`, `evidence.md`,
`historical-preview-sources.json`, `historical-host-input.json`, `host-preview.json`
and `implementation-receipt.json`. H is this thread's visualization workspace.
No game, turn, installed file, actor, research or tuning weight changed during
this offline step. No live planner/backend hookup, new schedule or commit/push.

The next gate is one complete, fresh-enough investment case with real candidate
yield components, usable Base or credible development, costs and competing work,
then a guarded reviewed proposal. Do not resume a selector hook hunt or treat a
finance preview as measured policy benefit. The dry-run seam is now available
for that case and for subsequent Basic/RH screening.
