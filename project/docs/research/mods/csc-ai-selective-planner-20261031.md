# Attachment-aware site projection and selective start policy

31 October 2026. Offline analysis and implementation only; no native launch,
settings change, installed-file change, AI turn, purchase or placement.

## Result

The two source110 projection discrepancies are accounted for by source-building
attachment multiplicity and pillage state. An attachment-aware reconstruction
matches **11/11 captured existing Quarter controls**, compared with 9/11 for the
shared preview's boolean source-presence calculation. This is a reproduction of
observed adjacency under the captured SQL, not a new dynamic intervention or a
validated native candidate-preview API.

The declared one-city capture contains 12 native-legal alternatives across six
plots. **None has an adjacent mapped Base resource.** The new selective screen
therefore recommends no new start among these alternatives. This is a bounded
city/turn conclusion, not evidence that the empire has no good Quarter sites.

Two existing material-development opportunities are more concrete: owned Flax
2489 lacks a valid improvement beside Bakers2488 and Tailors2564; owned Honey2344
lacks an improvement beside Bakers2419. Their improvement legality, Builder
assignment, travel, charges and competing work still need assessment. They are
development candidates, not submitted or completed jobs.

## Reproducible evidence

Closed input:
`C:/Users/Shadow/Desktop/Codex/csc-native-shadow-planner-20261030/run-02`.
`shadow-initial.json` equals `shadow-final.json`; `initial-census.json` equals
`final-census.json`. The report records each exact SHA256 and JSON source path.

Output:
`H/offline-site-planner-20261031/offline-review.json`, where H is this thread's
visualization workspace. The original capture and its failed projection gate are
preserved. Full cleanup remains verified in the original closure receipts.

The capture's installed manifest agrees exactly with the inspected current source:

| File | SHA256 |
|---|---|
| `CSC_AdjacencyCore.lua` | `813acb3de6750922ada38f1baa898833f2ca5e04d34014c62e6926c5b93e9f2b` |
| `CSC_AdjacencyModifiers.sql` | `2fe744ca28d6525910e1a4fb2b0f06a5c9d961c721cdca9735eb69a0996fb084` |

## Why the numbers differ

`A.Eligible` asks whether a source building is present anywhere in the authored
collection. `cityHasBuilding` uses HasBuilding, including a pillaged building,
and returns a boolean. The preview then adds one encoded amount per eligible
rule. The SQL compiler instead attaches the modifier through **each** source
building. Current mill rules use `COLLECTION_PLAYER_DISTRICTS`; they are not
limited to the Mill's own city.

The captured player has three unpillaged Wind Mills, in cities196610,262147 and
655369, and one pillaged Water Mill in city65536. Named UI building inventories
cover ten cities; the complete Core city census establishes that the eleventh
city720906 has no buildings. Repeated inventories on different district tiles
are deduplicated by `(player,city)`.

| Existing Quarter | Shared computed P/G | Attachment model P/G | Observed district adjacency P/G |
|---|---:|---:|---:|
| Bakers2488 | 3 / 1 | 2 / 1 | 2 / 1 |
| Bakers2419 | 3 / 1 | 5 / 1 | 5 / 1 |

At2488 the preview credits one river Production despite the only Water Mill being
pillaged. At2419 it credits one hill Production; the native observed result is
consistent with all three working Wind Mill attachments. The other nine controls
already match. Per-source fractional amounts are truncated/encoded **before**
multiplying by source instances; doubling a count before truncation is different.

This explains both residuals without changing policy weights or treating zero
Plot previews as authoritative. It also exposes an important design distinction:
empire-wide mill stacking is the current SQL behavior, not merely a local river/
hill benefit. Whether to retain that design is a separate decision. This work
does not silently narrow the collection, remove stacking, or patch the shared UI.
If its preview is repaired later, change source multiplicity in preview totals;
do not multiply gameplay property counts too, which would double-count SQL's
already repeated attachments.

## Resource geometry is not working supply

Current material adjacency rules count owned, visible mapped resource plots;
the Base/Specialty resource adjacency itself does not require a working improvement.
Producer supply and Services have additional improvement/ownership/other gates.
Thus an unimproved Honey can contribute to adjacency while providing no working
supply. The model and planner must not add its adjacency again when proposing
an improvement; improvement benefit belongs to the chain's operating outcome.

The existing-chain inventory contains twelve distinct adjacent mapped material
plots: nine with functioning improvement geometry, two needing valid improvements,
and one unusable/not owned. These are geometry states, not twelve proven working
Services or economic transactions. The capture has no repair case in that mapped
set. No inference about all empire Builder work follows.

## Implemented reusable tools

Under `project/tools/ai_tuning/`:

- `shadow_projection.py`: pure attachment-aware reconstruction using captured
  rules, source building inventories and full Core city coverage. Missing pillage
  or city inventories remain unknown. Real P/G and private units stay separate.
- `review_shadow_capture.py`: offline CLI validating endpoint equality and the
  captured legal opportunity set, emitting controls, structural start screening,
  and deduplicated existing material work. It does not overwrite original files.
- `selective_planner.py`: a small shortlist policy over the existing strict
  evaluator, with sourced stable original-human exclusion. It requires credible
  Base supply/development and either Both potential or combined real P+G >=4.
  +3/+4/+5 are selectable trial thresholds; none is calibrated net benefit.

Future material/customer credit still requires the evaluator's concrete plot,
mapping, feasibility, capacity, affordability, positive delay and marginal real
yield evidence. Empty customer space or CanHaveDistrict is not that commitment.
Existing unfinished chains, accepted production, footprint loss and valued customer
alternatives require explicit comparison. Missing costs remain unknown. The
shortlist removes only conservative same-context dominated alternatives; it
does not invent an empire budget, weighted utility or global allocation.

The captured alternatives remain partial: the native Plot preview failed known
positive controls, and future execution/costs are unknown. None is promoted to a
complete +4 investment case. The strict shortlist is tested on synthetic complete
inputs; the real capture supports the earlier structural no-Base exclusion only.
All outputs retain `action_authorization=false`. No live host/backend is wired
to this new policy yet, and no improvement in AI outcomes is claimed.

Run from the repository root:

```text
python -B -X utf8 project/tools/ai_tuning/review_shadow_capture.py CAPTURE --output NEW_OUTPUT.json
```

## Validation and next useful decision

66 focused tests pass across attachment/pillage handling, selective starts,
existing evaluator/coordinator, archived cases, geometry and the executed-Lua
reader fixtures. Seventeen tests are new. The actual closed capture independently
produces 11/11 matching existing controls and 12/12 no-Base structural deferrals.
Synthetic tests establish implementation behavior, not native benefit.

Use the captured Flax/Honey work and richer existing archived site inventories
to choose the first useful follow-through comparison, rather than forcing a new
Quarter into this city. Before connecting a new-start shortlist to live spending,
provide a complete actionable site/cost/competition example and freshness guards.
No repeat source110 load is needed to fix a reporter. The unknown arbitrary
native Builder-job payload interface remains parked; use working guidance and
the existing guarded backend when its own gates are met.
