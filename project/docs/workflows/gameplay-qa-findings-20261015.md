# CSC gameplay QA findings — 15 October 2026

The subsequent [expanded Tailors QA report](tailors-qa-report-20261015.md) includes
this ownership bug, four additional confirmed defects and the broader coverage.
The first-slice coverage limits below describe this earlier run only.

Scope: first native FireTuner regression slice, Gathering Storm with CSC alone.
**No gameplay fix is retained.** Henno requested reporting only. The one edited
event registration line was restored; its file has no Git diff. Tests and QA
tooling remain separate from gameplay sources. Quarter gates are unchanged.

## CSC-QA-001 — purchased material does not update Quarter adjacency immediately

**Confirmed gameplay bug; medium priority.**

With two owned material tiles adjacent to a Tailors' Quarter, buying a third
adjacent material tile through `CityManager.RequestCommand(...,
CityCommandTypes.PURCHASE, ...)` should increase native district Production by
one. It remained at **+2 instead of +3** after the purchase, despite the tile
being owned and the resource being present. An explicit adjacency refresh fixes
the value. The defect therefore concerns event-driven invalidation, rather than
the resource counting or native yield-delivery calculation.

Reproduction:

1. Create an otherwise controlled Tailors' Quarter, with three adjacent Base or
   Specialty resource sites. Establish the no-material Production baseline.
2. Make two resource tiles owned and one unowned; explicitly refresh as fixture
   preparation. Confirm native district Production is baseline +2.
3. Buy the unowned resource tile using the normal native city purchase command.
   Confirm purchase eligibility and actual owner after the command.
4. Read `District:GetYield(YIELD_PRODUCTION)` in a subsequent tuner command.
   Expected baseline +3; observed baseline +2.
5. Explicitly refreshing adjacencies yields baseline +3.

Cause evidence: `CSC_AdjacencyGameplay.lua` subscribes to
`Events.PlotOwnershipChanged`, which is **nil** in the tested game. Native
purchase emitted `CityTileOwnershipChanged` in both gameplay and UI contexts.
A temporary in-memory subscription to that real event made the native purchase
update correctly. Removing that subscription reproduced the stale result. No
such temporary refresh subscription remains, and no source fix is retained.

Confirmed coverage is Tailors material ownership acquisition. Other
ownership-sensitive adjacency rules may be affected; they have not been tested.
Another subscribed refresh event, such as the next player turn, is expected to
correct stale values, but that recovery timing has not been measured here.

Evidence root:
`C:\Users\Shadow\Desktop\Codex\csc-gameplay-qa-20261015\`.

- `diagnostics/012-native-purchase-with-old-subscription.txt`: real purchase and
  emitted ownership event.
- `diagnostics/013-old-subscription-reproduces-stale-purchased-resource.txt`:
  ownership confirmed, native bonus still +2.
- `diagnostics/009-native-plot-purchase.txt` and `010-purchased-tile-yield.txt`:
  native purchase succeeds with the temporary correct subscription.
- `run/ownership-forced-refresh-diagnostic.txt`: recount corrects stale output.
- `run/CSC QA ownership stale regression 20261015.Civ6Save`: completed saved
  fixture; original path/hash in `run/save.json`. A reload can itself refresh
  adjacencies, so repeat the purchase steps to reproduce rather than assuming
  the saved stale amount will survive initialization.

## Automation findings

- **Historical launcher bug:** hard-coded `Network.HostGame(-1)` attempts an
  incompatible network transport in this installation. The game logged a
  transport/lobby mismatch. `ServerType.SERVER_TYPE_NONE` resolves to 0; using
  that enum and the frontend setup sequence successfully launched a test game.
  The new QA tooling uses the enum; gameplay code is unaffected.
- **Computer Use limitation:** capture worked, but both window activation and
  the attempted Begin Game click failed with `failed to activate captured
  window`. No successful automated mouse click was established.
- **Native startup passed:** enabling `Automation.SetAutoStartEnabled(true)`
  before hosting successfully dismissed the normal load-complete barrier and
  reached gameplay without Computer Use. This follows Firaxis's existing path,
  without relying on the historical environment-gated LoadScreen timer patch.
- **Test API distinction:** `WorldBuilder.CityManager():SetPlotOwner(...)` changes
  ownership without emitting the normal city ownership event. The initial
  forced-ownership failure alone was insufficient to establish a gameplay bug.
  The real purchase reproduced CSC-QA-001 independently.

## Passed and untested

Native Tailors material Production deltas passed for 0, 1, 2 and 3 adjacent owned
materials, including two Base resources and Base + Specialty stacking.

The first pipeline stopped on ownership testing. Resource removal/restoration,
full save/reload assertions, population scaling, Services, trade, compatibility
and other Quarter behaviours are **not established by this run**. A successful
fixture save was confirmed separately. Diagnostic assertions that deliberately
expect the old broken output are reproduction evidence, not regression passes.
