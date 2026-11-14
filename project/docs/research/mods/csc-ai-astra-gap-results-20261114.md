# Astra investigations: fixes and completed Online250 result

The integrated changes improve chain operation while preserving observed
placement quality. On the same Continents starting world, the AI builds seven
Quarters instead of six and delivers **582 Storekeeper active chain-turns,
up from 437**. All seven foundations have owned Base and at least +3 site
quality. Both ordinary play and the separate payout diagnostic are saved or
closed as appropriate, with verified restoration and no remaining test owner.

## Comparison

Small/Prince/Online, map seed18461107, game seed29461107, City Lights,
Resourceful2 and Sukritact's Resources. Initial map signature, starting positions
and units match the earlier CSC Continents run. Only main CSC tuning operates
in the ordinary game. This is one matched-start integration comparison.

| Measure | Previous | Current |
|---|---:|---:|
| Bakers / Tailors foundations | 5 / 1 | 5 / 2 |
| Foundations with owned Base and +3 or better | 6 / 6 | 7 / 7 |
| +4 or better foundations | 3 | 3 |
| Foundations with both Base and Spec | 2 | 3 |
| Built sites tying the best geometry in their positive-offer packet | 6 / 6 | 7 / 7 |
| Exact new-site bids consumed by native district winners | 40 / 40 | 51 / 51 |
| Mapped Quarter/neighbor pairs established, all stages | 10 | 16 |
| Adjacent City Lights goods providers | 0 | 1 |
| Storekeeper active chain-turns | 437 | 582 |
| Storekeeper chains with at least100 active turns | 2 | 4 |
| Ordinary slot-consuming district foundations | 158 | 170 |
| Paid tiles / Gold spent | 115 / 11,189 | 99 / 8,949 |
| Quarter-footprint / supplier purchases | 0 / 0 | 0 / 0 |

Site quality includes the possible local Mill and existing customers, with no
future-customer adjacency. The +2 floor is live; all actual new foundations in
this run exceed it. The four current Storekeeper chains contribute176,153,146
and107 active turns, measured on the same turn2–249 window as the earlier437.
Astra independently recomputed those totals from both raw Lua logs.

At250, all five Bakers have healthy Mills; four have an improved Base and a
healthy adjacent Granary. Both Tailors have healthy Workshops and improved Base,
but neither has a healthy adjacent Stage2 customer. Their Stage2 Service
properties are zero at250. Customer/service follow-through for Tailors is the
clearest next operational target.

The five AIs end with50 cities/605 population, versus48/602 previously.
Summed city Production at250 is2,698.04 versus2,035.65; reported Treasury
`GetGoldYield` totals4,734.18 versus4,507.95; city Food surplus totals236.93
versus260. These are terminal observations of the diverged game paths.

## Numbered investigation outcomes

| Problem | Closed work and evidence |
|---|---|
| **1.6 Follow-through** | Ghidra/body parity and the150–200 replay trace Lingapura's nomination, accepted request, fixed footprint,15-turn wait, Builder120 versus Quarter112.62 and subsequent stronger native investments. Its later +4 site gains adjacent owned Base; both footprints are unworked. Retained requests update their existing site rather than retarget. Keep native competition and the current economic formula. The fresh package delivers51/51 new-site values and constructs seven Quarters. |
| **1.1/1.2 Material coverage and quality floor** | The geometry pre-screen and complete-value gate now share minimum2. Unconditional gameplay reconciliation attaches the five ordinary incoming roots to loaded valid improvements, including R2/CL cases. The actual loader verifies25 expected hosts exactly once. The separate native payout experiment verifies real Food/Culture increments below. |
| **1.2/2.1 Relationships** | Same-city future-customer preparation uses two known free population slots for its extra preference; Quarter bids remain available with one/unknown slot. All14 CL provider reverse edges load exactly once. Player2's Bakers1049 precedes Rural Community1048: founded107, complete108, private placement yield1 at foundation. Its native choice and pre-placement cache are recorded. |
| **1.5 Acquisition** | AI-C162/163 retain their paid-footprint→ownership→construction and paid-supplier→Farm qualification. Six current supplier and six publisher fixtures plus243 rebuilt CE native checks cover relevant drift. The examined Fractal frontier bid loses before the purchase stage. This run generates no Quarter-frontier winner or supplier-acquisition offer, so it supplies no new funding defect to fix. |

The supplier fixtures include modded Spec and shared Base/Spec deposits. Full
play includes modded Base adjacency; the explicit Maple test supplies physical
modded Specialty coverage. Native eligibility, normal district slots and
competition with units/projects remain in place. No general bid increase,
subsidy, forced retarget or timeout extension was added.

## The loader correction and actual payouts

The first startup failed the new row audit at turn1, before autoplay. Our earlier
assessment that479 was late enough was wrong: R2 creates Sawmill at799990 and
optionally edits it at800000; CL adds resource-validity links at9999. Eight
attachments were absent even though the resource tags already existed.
Reconciliation now loads at **800010** in main ModBuddy and the runtime package.
The failed startup is preserved; the same selected seed succeeds on replacement.

After the ordinary game is sealed, the separate shared-controller diagnostic
reloads its exact250 save and grants declared human fixtures. Actual UI building
yields show these increments against a stable baseline:

| Functioning supplier | Wind-Mill Food | Café Food | Workshop Culture |
|---|---:|---:|---:|
| Wheat / Farm control | +1 | 0 | 0 |
| Maple / R2 Sawmill | 0 | +1 | 0 |
| Bamboo / R2 Sawmill | 0 | 0 | +1 |
| Unmapped Stone / diagnostic Sawmill | 0 | 0 | 0 |
| Final improvement removal | 0 | 0 | 0 |

The diagnostic advances zero AI turns and leaves the source save unchanged.
Queue item, population and Treasury remain unchanged around grants and samples.
Its unsaved fixture world is then closed and preferences/packages restored.
The ordinary250 results exclude these grants.

## Material retention and next work

No last physical Base or Spec deposit is destroyed by placement. Wheat1308 is
covered at40 with another Base remaining. The Specialty-access exhaustion at54
is Honey2606 changing from player3 to player5; Honey and Camp remain present.
Five working-supplier interruptions include Farm removal, ownership change and
pillage. The Flax1060 pillage at243 remains unrepaired at250, interrupting the
last six sampled turns of that chain. Recovery latency is still useful work.

Astra supports closing this investigation-and-validation goal. Subsequent
improvements are Tailors' operational customer links, broader natural acquisition
opportunities, a bounded test of own-Production feedback in forecasts, and faster
recovery. The current results support the integrated package as a whole.

## Evidence and reproduction

The [compact scorecard](csc-ai-astra-gap-results-20261114.json) preserves counts,
terminal census summaries, native observer counters, exact save identity and
physical payout receipts. [Investigation details](csc-ai-astra-gap-investigation-20261114.md)
retain code/body hashes and corrections. Reusable engine cadence is AI-N131 in
the `civ6-ai` skill. No upstream PR was submitted.

Artifact root: `C:/Users/Shadow/Desktop/Codex/csc-ai-astra-gaps-20261114/`:

- `lingapura-components150-200-01`: completed diagnostic replay.
- `fresh250-01`: preserved turn1 loader-audit failure and normal cleanup.
- `fresh250-02`: completed ordinary game, ten censuses and all five checkpoints.
- `comparison`: raw-record comparison with the earlier Continents run.
- `payout-qualification-01`: successful physical payouts and cleanup.

Both completed sessions verify native exit0, owners absent and exact preference/
package restoration. Full play drains23,745 native records with zero faults,
zero active callbacks and no buffered records. Its250 save SHA256 is
`3db454db0e3d5f1ffb11dffe593ffe98f5a160f911530097e8e1a0c43e2a6f8f`.

Recompute the comparison using
`planning_campaign_results.py --run Previous=<old-continents250-01> --run Current=<fresh250-02> --output <new-output>`.
The three physical-payout validator tests, Lua5.1 parsing and current SQL/
deployment regressions pass; actual receipt tables above close the live check.
