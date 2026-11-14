# Three-map CSC planning campaign —250 turns

All three preselected Small/Prince/Online games reached250 and closed with
exit0, restored preferences and complete selected censuses. Main CSC tuning
was the only treatment; City Lights, Resourceful2 and Sukritact's Resources
were enabled. No new upstream PR. The earlier automatic goal remains paused.

**Placement quality is good where construction happens; reliable follow-through
is not established.** The five original AI seats found eight Quarters in total,
seven Bakers and one Tailors. All eight have owned Base and at least+3 at
foundation; only three reach+4 and two have Spec. Each built site ties the best
positive offered geometry in its current city/type packet. This is not proof
that a specific late packet caused the earlier native choice, or that every
good alternative should become a Quarter.

Quarter quality uses the loaded rules with prospective local Mill bonuses where
applicable. It excludes future customers and is not active gameplay yield.
Native totals are choice-time utility; adjacency is a separate UI-event yield
vector. Pangaea includes a verified turn200 reload with an explicit native
capture gap. [Protocol, hashes, interruptions and corrections](csc-ai-planning-campaign-20261114.md).

| Map | Bakers | Tailors | +3+ | +4+ | Base | Spec / both | Vanilla footprints | Native totals joined |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Continents | 5 | 1 | 6 | 3 | 6 | 2 / 2 | 308 | 201/206 |
| Pangaea | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 253 | 142/151 |
| Fractal | 2 | 0 | 2 | 0 | 2 | 0 / 0 | 303 | 196/200 |

City Centers and Wonder footprints are included in footprint counts but excluded from the forecast-join denominator. A Wonder district completion flag does not establish completion of its building.

| Map | Exact new-site bids consumed | Reconsiderations / scopes | Physical neighbour order | Mapped losses | Paid tiles / Gold | Quarter-site payments |
|---|---:|---:|---|---:|---:|---:|
| Continents | 40/40 | 42/21 | neighbourFirst:7, quarterFirst:3 | 6 | 115 / 11189 | 0 |
| Pangaea | 4/4 | 31/20 | none | 0 | 71 / 5300 | 0 |
| Fractal | 7/7 | 35/16 | neighbourFirst:2, quarterFirst:1 | 0 | 89 / 9107 | 0 |

## Results against the requested problems

| Problem | Verified result | What this does not establish |
|---|---|---|
| 2.1 Order of placement |13 physical mapped neighbour pairs:9 neighbour-first,4 Quarter-first. Seven neighbour-first pairs are Bakers' City Centers; the other two are the Tailors' Commercial Hub/Theater. Later pairs are three sales hosts and Broadway. | No deliberate customer-following causality; no adjacent Stage2 Harbor for Tailors. Mapped building variants are not extra physical districts. |
| 2.2 Material retention | No last physical Base/Spec deposit destroyed. Six mapped incidents, all Continents Bakers: one nonlast Wheat/Wonder overwrite, Farm removal, ownership loss and three pillages. Five working-supplier disruptions include four observed restorations. Fractal's two Bakers have no mapped loss; Pangaea has no Quarters to expose. | No proof of universal protection or that tuning caused each repair. Continents' Banana Plantation remains pillaged at250. |
| 1.5 Funding and purchases |275 measured payments,25,596 Gold, every requested debit matched.15 distinct unowned Quarter offers across the games; zero frontier Quarter choices, zero Quarter-site payments and zero supplier-acquisition offers. | Generic purchasing is working; natural saving/buying for our Quarter and supplier targets is unshown. |
| 1.7 Defer/reconsider |108 deferred→offered packet transitions across57 city/type scopes;151,892 managed mask operations. Each arm has exercised masks and reconsideration. | These are repeated operations/state changes, not108 successful placements or151,892 separate decisions. Typed declines remain zero on the routine managed-column path. |
| 1.1–1.2 Resource parity | Source and fixtures treat Base/Spec independently using loaded resource tags and valid improvements; three maps contain Resourceful resources, and Pangaea contains11 Suk Gold. Mapped-neighbour observations cover five modded Base pairs, five vanilla Base pairs and two vanilla Spec pairs. | No naturally placed modded-Spec neighbour and no Stage4-gated Spec job/acquisition were exercised. Loaded compatibility is not complete economic payout equivalence. |
| City Lights providers | Loaded provider mappings validated; original AI built45/63/59 mapped provider districts. No provider was adjacent to one of their Quarters. | This is coverage and a negative outcome, not demonstrated provider-placement guidance. An observer0 provider pair on Continents is outside the treatment cohort. |
| 1.4 Opportunity vs construction | Distinct positive site identities: Bakers54/36/37; Tailors23/6/4. All8 built sites are positively offered and tie their packet's best geometry.51/51 new-site native BEST receipts consume the exact bid/write/version/preceding ordinal. | Alternative sites overlap across cities/turns, and can later disappear or become poor. Consumption does not prove admission, a live build contract, production, completion or realised Services. |

The native fund journal records1582 targeted affordability checks.132 pass both
gates;787 fail category funds despite sufficient actual Treasury. Observed
weights are3/4/1/1 and the maximum plot account is150 Gold. These are generic
category accounts, not earmarked Quarter savings. Of275 payments,272 have the
buyer still owning the tile at the first strictly later map snapshot. The other
three Fractal payments have free-city62 ownership by the next snapshot: player4
plots1287/1583 paid on130/132, and player2 plot790 paid on170. Their debits still
match; this shows a later ownership/retention limit rather than proving a failed
payment. Same-turn map snapshots and the invalid native owner bytes are not
used as ownership confirmation.

Pangaea's zero is not simply a missing packet:4/4 exact native Quarter choices
land. London site783 falls from+3 to+2 on8; its old contract is submitted on16
at104 utility and accepted on25 at−1024, with no foundation. This is consistent
with withdrawing an expired opportunity. Lingapura's submitted contract and
the two later capacity-full comparisons still need follow-through diagnosis.
Do not raise every bid to force all old offers to construct.

Fractal's player3 is alive at150 and eliminated by175. All five original AIs
survive on the other two maps. No Quarter capture occurs in the cohort; held
Quarter counts at250 remain6/0/2. Comparisons are descriptive, with no new
matched untuned control using this City Lights/resource stack.

## Next work

1. **1.6 Follow-through:** inspect the still-credible nominations/production
   decisions that do not build, keeping London's justified withdrawal separate.
2. **1.5 Natural acquisition:** use a controlled, credible unowned footprint or
   adjacent supplier to close the gap between published offers, purchase
   contracts, category funding and actual payment. Broad games did not exercise it.
3. **1.1–1.2 Compatibility:** fix the separately documented missing incoming
   Food/Culture attachments for some CL/R2 improvements before claiming that
   modelled benefits equal realised benefits. Keep this separate from score tuning.
4. Exercise an actual modded-Spec neighbour and a CL-provider relationship;
   the broad campaign leaves both outcome paths unproven.

## Controller, diagnostics and reproducibility

The hidden spy warning has a dedicated, guarded, one-shot observer cancellation
path, pushed in `c63be794`. It checks finite Core autoplay/control, newest CSV
phase, loaded statement/choice shape and exact session participants. It uses
stock Escape-equivalent `CloseSession`, never an explicit response or promise;
possible implicit diplomatic effects are logged.106 controller regression tests
pass, including the captured205 CSV trace, stale UI-human flags and visible/hidden
view handling. **No live spy-cancellation receipt was produced by these games.**
Fractal naturally exercises the existing troop-warning handler at240 and proceeds.

After all games closed, removed the unqualified wrapper+0x1c native owner reads
(skill AI-N129), and role-gated the observer's working-supplier flag. Raw campaign
records remain unchanged and the analysis applies the corrections to every arm.
Fifty-three policy/observer/recovery/analysis tests pass, including the unrelated
Farm regression and a native-wrapper fixture with no readable owner byte.
These53 plus the106 controller tests are offline checks, not additional live games.

The original Pangaea205 branch is retained but excluded after its exact200 save
marker. Recovery01 stops before autoplay on the old turn1-only preflight;
recovery02 verifies44/44 structural rows, continues200→250 and closes cleanly.
The final outcome is one Pangaea seed, not extra games. The two repeated parent
entries in the runner's raw interruption array reflect recovery invocations,
not two separate205 failures. Short qualification attempts and their limitations
remain in the protocol report.

Artifacts: `C:/Users/Shadow/Desktop/Codex/csc-ai-planning-campaign-20261114/`.
`comparison/planning-campaign-results.json` preserves row-level joins, financial
exceptions and packet comparisons. Reproduce using
`project/tools/native_ai/late_placement/planning_campaign_results.py` with the
closed `continents250-01`, normalized `pangaea250-combined` and `fractal250-01`
inputs. Pangaea's canonical derivative omits Service logs; read those from its
raw, cut-off-qualified segments. No game binary or save is committed to the repo.

## Vanilla district calibration

These districts competed in the **tuned CSC/City Lights games**. They are not an untuned control. Different cities, turns and costs make their medians descriptive rather than interchangeable bid targets.

| Map | District | Foundations | UI joins | Mean nonzero adjacency yields | Native quote joins | Median utility | Median quote age |
|---|---|---:|---:|---|---:|---:|---:|
| Continents | AERODROME | 8 | 8 | 0 | 7 | 2216.8 | 2 |
| Continents | AQUEDUCT | 5 | 5 | food 1.20 | 5 | 1529.1 | 5 |
| Continents | CAMPUS | 27 | 27 | science 2.04 | 27 | 1096.6 | 4 |
| Continents | CANAL | 3 | 3 | 0 | 1 | 2086.0 | 7 |
| Continents | CITY_CENTER | 49 | 49 | 0 | 0 | — | — |
| Continents | COMMERCIAL_HUB | 16 | 16 | gold 2.69 | 16 | 2033.9 | 3.0 |
| Continents | DAM | 10 | 10 | 0 | 10 | 1248.1 | 4.5 |
| Continents | DIPLOMATIC_QUARTER | 3 | 3 | 0 | 3 | 773.9 | 1 |
| Continents | ENCAMPMENT | 17 | 17 | 0 | 17 | 2019.5 | 3 |
| Continents | ENTERTAINMENT_COMPLEX | 6 | 6 | 0 | 6 | 1406.8 | 8.0 |
| Continents | GOVERNMENT | 1 | 1 | 0 | 1 | 1061.8 | 1 |
| Continents | HANSA | 6 | 6 | production 3.33 | 6 | 2041.9 | 6.0 |
| Continents | HARBOR | 12 | 12 | gold 1.83 | 12 | 2154.0 | 3.0 |
| Continents | HIPPODROME | 4 | 4 | 0 | 4 | 295.1 | 5.5 |
| Continents | HOLY_SITE | 7 | 7 | faith 1.14 | 7 | 760.4 | 2 |
| Continents | INDUSTRIAL_ZONE | 8 | 8 | production 2.38 | 8 | 1444.0 | 4.0 |
| Continents | NEIGHBORHOOD | 14 | 14 | 0 | 14 | 1387.7 | 1.5 |
| Continents | PRESERVE | 1 | 1 | 0 | 1 | 1420.4 | 3 |
| Continents | SPACEPORT | 16 | 16 | 0 | 15 | 6865.3 | 2 |
| Continents | THEATER | 33 | 33 | culture 2.00 | 32 | 1346.4 | 3.0 |
| Continents | WATER_ENTERTAINMENT_COMPLEX | 9 | 9 | 0 | 9 | 3001.1 | 2 |
| Continents | WONDER | 53 | 53 | 0 | 0 | — | — |
| Pangaea | AERODROME | 4 | 4 | 0 | 4 | 1929.8 | 4.0 |
| Pangaea | AQUEDUCT | 4 | 4 | 0 | 4 | 781.8 | 4.5 |
| Pangaea | CAMPUS | 24 | 24 | science 1.83 | 23 | 1301.2 | 4 |
| Pangaea | CANAL | 2 | 2 | 0 | 1 | 1716.5 | 6 |
| Pangaea | CITY_CENTER | 43 | 43 | 0 | 0 | — | — |
| Pangaea | COMMERCIAL_HUB | 10 | 10 | gold 2.50 | 10 | 1779.0 | 3.0 |
| Pangaea | DAM | 5 | 5 | 0 | 5 | 1771.0 | 3 |
| Pangaea | DIPLOMATIC_QUARTER | 1 | 1 | 0 | 1 | 1201.6 | 8 |
| Pangaea | ENCAMPMENT | 18 | 18 | 0 | 18 | 1483.3 | 2.0 |
| Pangaea | ENTERTAINMENT_COMPLEX | 7 | 7 | 0 | 6 | 1321.8 | 2.0 |
| Pangaea | GOVERNMENT | 2 | 2 | 0 | 2 | 837.4 | 3.5 |
| Pangaea | HARBOR | 5 | 5 | gold 1.00 | 4 | 2776.5 | 1.0 |
| Pangaea | HOLY_SITE | 9 | 9 | faith 1.44 | 7 | 359.4 | 3 |
| Pangaea | INDUSTRIAL_ZONE | 8 | 8 | production 2.12 | 8 | 1541.7 | 5.5 |
| Pangaea | NEIGHBORHOOD | 3 | 3 | 0 | 3 | 1494.4 | 4 |
| Pangaea | ROYAL_NAVY_DOCKYARD | 4 | 4 | gold 1.50 | 4 | 1063.3 | 2.0 |
| Pangaea | SPACEPORT | 13 | 13 | 0 | 11 | 6281.4 | 1 |
| Pangaea | THEATER | 25 | 25 | culture 1.88 | 24 | 1763.8 | 2.5 |
| Pangaea | WATER_ENTERTAINMENT_COMPLEX | 7 | 7 | 0 | 7 | 2711.8 | 4 |
| Pangaea | WONDER | 59 | 59 | 0 | 0 | — | — |
| Fractal | ACROPOLIS | 1 | 1 | culture 2.00 | 1 | 389.3 | 1 |
| Fractal | AERODROME | 8 | 8 | 0 | 8 | 2144.4 | 4.0 |
| Fractal | AQUEDUCT | 7 | 7 | 0 | 7 | 408.2 | 5 |
| Fractal | CAMPUS | 28 | 28 | science 1.86 | 28 | 1428.0 | 2.5 |
| Fractal | CANAL | 7 | 7 | 0 | 5 | 2351.1 | 2 |
| Fractal | CITY_CENTER | 50 | 50 | 0 | 0 | — | — |
| Fractal | COMMERCIAL_HUB | 18 | 18 | gold 2.00 | 18 | 1988.6 | 3.5 |
| Fractal | DAM | 4 | 4 | 0 | 4 | 836.6 | 8.5 |
| Fractal | DIPLOMATIC_QUARTER | 2 | 2 | 0 | 2 | 248.3 | 1.0 |
| Fractal | ENCAMPMENT | 18 | 18 | 0 | 18 | 2764.3 | 4.0 |
| Fractal | ENTERTAINMENT_COMPLEX | 9 | 9 | 0 | 9 | 2337.8 | 3 |
| Fractal | GOVERNMENT | 1 | 1 | 0 | 1 | 427.3 | 2 |
| Fractal | HARBOR | 15 | 15 | gold 2.00 | 15 | 1944.9 | 3 |
| Fractal | HOLY_SITE | 6 | 6 | faith 1.00 | 4 | 573.0 | 7.0 |
| Fractal | INDUSTRIAL_ZONE | 10 | 10 | production 2.20 | 10 | 1531.7 | 2.5 |
| Fractal | LAVRA | 6 | 6 | faith 3.00 | 6 | 866.4 | 1.5 |
| Fractal | MBANZA | 3 | 3 | 0 | 3 | 906.8 | 3 |
| Fractal | NEIGHBORHOOD | 9 | 9 | 0 | 9 | 1315.8 | 4 |
| Fractal | PRESERVE | 3 | 3 | 0 | 3 | 239.8 | 8 |
| Fractal | SPACEPORT | 11 | 11 | 0 | 11 | 3793.3 | 2 |
| Fractal | THEATER | 25 | 25 | culture 1.40 | 25 | 1662.2 | 3 |
| Fractal | WATER_ENTERTAINMENT_COMPLEX | 9 | 9 | 0 | 9 | 2268.6 | 4 |
| Fractal | WONDER | 53 | 53 | 0 | 0 | — | — |
