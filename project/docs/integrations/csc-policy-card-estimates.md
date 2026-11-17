# Policy-card estimates: CSC, BRS and EPC

Updated 17 November 2026.

Extended Policy Cards (EPC) uses Better Report Screen (BRS)'s public
`ExposedMembers.RMA.CalculateModifierEffect` function while constructing cards.
CSC adds the hypothetical extra Quarter yields from district-adjacency policies.
These are display forecasts, with no gameplay or AI-policy changes.

## Loading

BRS retains its original `RealModifierAnalysis` context and initialization.
CSC loads its own paired XML/Lua context, `CSC_PolicyCardEstimates`, conditional
on BRS. It attaches through the existing exposed RMA table after BRS publishes
its decoder, calculator and formatter. If BRS initializes later, the
`LoadGameViewStateDone` event retries once. There is no per-turn polling.

Do not replace BRS's context and then `include('RealModifierAnalysis')`. The
installed BRS 7.0 manifest pairs that script with its XML but does not import it
as a support library. An applied replacement action alone does not establish
that the original script initialized. The previous adapter relied on that
loading assumption and returned silently if its expected functions were absent.

The adapter preserves the RMA table identity, original refresh listeners and
unrelated calculations. Its log identifies either a successful attachment or a
missing original API. A forecast error logs once per affected policy and falls
back to the original estimate; if that fails too, just the estimate is blank.
An optional Quarter estimate must not prevent opening the Government screen.

## Calculation boundary

CSC matches exact registered policy-return attachments from the shared adjacency
rules. These wrappers encode one return in ten property bits: forecast the whole
amount on the first wrapper and zero on its siblings, instead of adding their
literal bit weights. Only the active-policy gate is bypassed. Ownership, rings,
rounding, caps, unique districts, construction and pillage retain shared rules.

For policies with CSC attachments, the adapter folds public decoder results
using BRS 7.0's attachment, subject and influence-filter rules. Ordinary modifiers
still use BRS's original decoder. Other policies/objects use the original
calculator directly. This small fold is necessary because BRS's own aggregator
calls its context's decoder rather than the exposed decoder. It preserves the
four-result calculator and seven-result decoder contracts, numeric yields,
summary and detailed tooltip. Per-rule forecast caches last one request.

The installed BRS formatter skips Food at yield ID zero. A numeric probe detects
that case and restores Food in CSC policy summaries without duplicating it if
a later BRS version corrects the formatter.

## Regression and current status

Henno reports the Government screen stopped opening after the SQL/action
restructuring. Lua.log records three failures in EPC's animated row layout,
`GovernmentScreen.lua:1493`, looking up a card instance/control. CSC's optional
analysis adapter is in that card-creation path, so the stack's EPC filename does
not establish fault ownership. The saved pre-restructure action JSON has the
same RMA replacement action/properties as the failing build; the exact trigger
within the restructuring has not been reproduced.

The revised adapter removes that initialization dependency. Offline validation
executes all 80 policy/unique/count fixtures with installed BRS aggregation and
formatting. Separate Lua contexts verify immediate/delayed/missing API behavior,
original table/functions, unrelated passthrough and duplicate-event handling.
An injected forecast failure verifies recovery. EPC's actual card renderer also
returns successfully for normal and failing forecasts with stand-in controls.
Native Government-screen opening/animation is the remaining in-game check.

Run `project/tools/adjacencies/test_policy_card_estimates.py` with `--database`,
`--dependencies`, `--analyser` and optional `--epc` paths. These read installed
mods and the database; they do not edit Workshop files or touch a live session.
