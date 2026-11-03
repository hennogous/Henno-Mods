> **Retired, 3 November 2026:** these Basic/RH assistance profiles are archived and no longer load. See [the fresh-start record](csc-ai-reset-20261103.md). This page retains the previous implementation for reference.

# CSC AI assistance: Basic and RH profiles

Status: 24 October 2026 — source candidate, offline checks passing. No deployment
or native qualification of the new ordinary-turn host/RH combination yet. The
human's turn-150 inspection game remains on its archived build and stays open.

## Player settings

| CSC AI assistance | Supported RH enabled | Effective tuning |
|---|---|---|
| Off | No | Underlying Civ AI; no CSC AI inputs or interventions |
| Off | Yes | RH alone; no CSC AI inputs or interventions |
| On (default) | No | Basic CSC tuning plus CSC supply-chain assistance |
| On (default) | Yes | RH baseline plus automatic CSC supply-chain extension |

**Subsidise AI tile purchases** defaults On and depends on CSC AI assistance.
It applies in either enabled profile. Off means the AI must fund the full next
tile from its safe budget; an unaffordable step waits. On donates only that step's
shortfall. There is no turn 100 cutoff. These are new-game settings, not live
mid-transaction controls. The resource-map assistance setting stays independent;
formal comparisons should share that resource pass and disable this master for
the baseline.

## Basic tuning

`Data/CSC_AI_Basic.sql` owns general improvement valuation of 30, Builder Units-list
preference of 50, +1 movement for major AI Builders, and the native documented
Required City=-1 production parameter. The owner/unit requirements exclude humans
and non-Builders from the movement modifier. Contract flexibility permits a
different city to meet demand; it does not reserve, move or create a Builder.

These are native configuration inputs. Prior pilots provide combined-treatment
evidence and useful native behavior traces, not an isolated causal estimate for
each number. The newly packaged movement/profile combination still needs native
testing. Do not describe native declaration or offline fixtures as AI-choice proof.

## Shared CSC extension

Both enabled profiles retain the existing directed Quarter/customer placement
signals, broad bonus-resource and river guidance, and AI-owned adjacent mapped
material/improvement modifiers from `CSC_AI.sql`. The mapped tags include enabled
compatibility resources. Existing conditional Service research preferences remain
preferences only; there is no forced research, strategy-to-Service matching,
production queue rewrite or unit/improvement/building grant.

Experimental early all-owner private resource/improvement forecasts are not
promoted. They showed citizen-allocation spillovers, and Mine positives remained
unobserved in the last pilot. Likewise, soft last-material preservation signals
and urgency callbacks did not establish reliable preservation. Their research
files remain available but the old material-care DB/script actions are removed
from these normal profiles. Global harvest bans are excluded.

The existing broad native district-adjacency private channel can also be valued
on human plots; no direct economic-yield conversion does not establish complete
citizen-allocation inertness. Record this existing limitation in future matched
comparisons. UI filtering is presentation, not an engine scoring boundary.

## Installed opportunity host

`CSC_AI_Assistance.lua` runs in Gameplay, using `CSC_AI_AssistanceUI.lua` only for
native target/price/production readbacks. It needs no FireTuner, external Python
controller or per-turn deep capture. It handles every eligible major AI ID and
also excludes configured humans during autoplay.

The first scope scan caches each city's geography once. It marks revealed Both
opportunities with the source within 3, material observation within 4, and unowned
acquisition tiles within 3. Owned material at4 can count. Owned, unowned and enemy
ownership remain distinct; foreign deposits are never bought. Changed scope
fingerprints/new cities rebuild plans, with a broad reconciliation every 25 turns. Each AI
turn rechecks the marked opportunity. Native target enumeration is reused only
within that synchronous callback; prices/wallets stay fresh and mutation invalidates
the cache. No Python transport delays or deep benchmark exports run on installs.

Plans prefer Base count, then Specialty count within the Both tier. A route may
secure the source and two selected resources with up to 2 connector tiles. It
does not demand all future prices upfront. One next step receives a fresh native
quote/reach/reveal/ownership/treasury check. Per-city cooldown is one turn;
per-player limit is 3 acquisitions per 5 turns; rolling and per-site spending caps
are 300. The reserve is the maximum of 25, two upkeep turns, and ten deficit turns.
At most 80% of surplus is the AI's safe own contribution. The remainder is donated
only when the dependent setting permits it. Donation is not a free land grant:
the full quoted cost is debited and ownership/city/treasury receipts are checked.

This backend is **assisted paid city assignment**, not proven native AI PURCHASE.
Pending grant/assignment/debit states are saved before effects. Ambiguous effects
are not resent. Same-turn owner readback may complete a pending debit once; a
later-turn changed wallet never triggers blind reconciliation. Compact receipt
indexes/totals survive saves; no deep data gathering is installed.

Once source and selected materials are owned, the host requires native/UI
legality, a Quarter unlock, positive cost and zero current progress. It creates
one 0% incomplete foundation, verifies unchanged cost/progress/queue, and leaves
construction to the AI. Only the same Quarter type excludes another placement;
an unfinished different Quarter is left to native legality. Requested foundation
records are retained even on postcondition failure, preventing reconstruction.

Paid acquisition/automatic foundations are inactive in multiplayer and hotseat in
this first candidate. Static tuning is unaffected. A tested synchronization path
is required before enabling those economic actions there.

## RH ownership and compatibility

Automatic detection uses the actual reviewed ModInUse ID, not a display name.
`project/config/csc-ai-profiles.json` is the alias/load-order registry. The current
beta is 5.097, ID 2501be3e-9780-4e9f-9506-4ff71cf076cb. Do not invent a public ID or
assume an unreviewed release keeps the same UI/schema. Adding a reviewed alias and
running `configure_profiles.py` regenerates the criteria/actions. Earlier alias
matches exclude later ones, so CSC scripts are installed once.

With RH enabled, CSC does not reset its global improvement value, unit priorities
or movement, and does not replace its trees. It only supplies an absent documented
Builder production parameter; an authored RH value remains authoritative. The CSC
extension loads after the reviewed beta's final DB override. RH's own `RHAITags`
registry receives the name of CSC's private yield so its tooltips/Pedia/report can
filter it. CSC does not copy RH code or replace its reports. Schema and native UI
behavior still need qualification together in the combined setup.

## Validation boundary and next native checks

The focused suite checks the settings/mode matrix, aliases and duplicate-handler
exclusion, native-schema SQL with sentinel RH values, movement scope, economic
faults, caches, normal-turn buy/place callbacks, and native-style UI signatures.
It does not prove the new installed host works in a stock ordinary-turn session,
that the actual combined RH game improves performance, or that preservation is
solved. Those require fresh authorized native tests after human inspection ends.

Use an observation-only controller for those tests. The experimental foundation
and funded-acquisition adapters now reject the installed host as a competing
mutation owner. Old experiments remain archived and must not be replayed under
the new source. Verify settings Off, subsidies Off, each active profile, normal
save/reload, native 0%/Gold receipts and RH UI before release deployment.

### Source verification, 24 October 2026

The 40 profile/native-schema/Lua51 checks, 12 legacy foundation-planner checks,
and 18 own-first funding regression checks pass. ModBuddy action JSON round-trips
through project CDATA. This is offline source verification, not native profile
or combined-RH qualification.

A final read-only installation comparison found 26 differences from the archived
517-file inspection package, including the new settings/profile metadata and
art files. The source task did not deploy or restore them. Current installation
must therefore not be described as the unchanged archived candidate or original
510. Reconcile its manifest after the human finishes inspection; do not overwrite
the open game's files. The scoped inspection automation was reported absent by
the app and was not recreated.

24 October native qualification update: RH5.097 + both expansions has reached turn50 in the scoped pilot. The new UI-readiness/stable-human host confirms7acquisitions295Gold(41own254subsidy) and3native/UI0%foundations with unchanged queue/cost. Native proof is independent-native-actions50-confirmation.json in the current child. First25 had no economic interventions due earlier integration bugs; coverage is mixed and full150 remains pending. No universal performance or preservation claim.
