# Shared Stage 2 AI policy on Fractal

This normal-start development run tests common Bakers and Tailors guidance
and a finite early-score penalty for weak Quarter sites. It compares one
Fractal map with its earlier stock-AI CSC baseline and v2 treatment.

## Policy under test

The loaded Quarter, producer, customer and replacement registries supply
the common policy. Bakers needs an adjacent owned City Center. Tailors can
plan around an existing Harbor or a plausible owned Harbor footprint.
Only an immediately legal Harbor site can receive a native customer bid.
A Harbor site covering a protected supplier or resource is omitted.

The previous 24- and 48-point positive Quarter bids are preserved. A legal
site with no viable adjacent Base deposit, or that would cover a mapped
material, receives a 256-point deduction. A site with viable Base and
no plausible customer footprint receives a 128-point deduction. Eligible
customer plots beside an existing credible Quarter receive 40 points.
These adjustments use Q8 at the native early-score boundary. The game
still compares and executes placements. Weak-site entries are dropped
first if the policy packet fills.

Both industries use the same initial nomination bands for a missing
producer or customer building. Those bands come from Bakers calibration
and need separate Tailors validation. The UI's native production check
screens building offers. The shared supplier policy chooses one actionable
Base job per chain, including chains with several deposits. It prefers
repairing a compatible pillaged improvement and applies a lower bid when
other links are outstanding. It preserves scarce Base and Specialty
suppliers using the existing district, Builder and harvest protection.
Quarter repair can use the same native admission when its remaining
Stage 2 links are ready. Trade route scoring is outside this trial.

## Reproduction and evidence

The game used the same Small Ancient Prince Online Fractal settings and
seeds as the earlier pair, map 18461109 and game 29461109. The initial map
signature, leaders, starting plots and starting units all matched. CSC map
assistance logged the same 30 Tailors resource additions on the same
plots. The shared controller ran the normal start to turn 200 with the
three modified CSC Lua files at commit `ca5ba9a` over the previous frozen
gameplay package and the same local CE binary at review commit `c10a076`.
No external policy or AI test mode was active.

The local evidence root is `Desktop/Codex/csc-ai-stage2-parity-20261108`.
The `run-v3-fractal` archive preserves the live Lua log, native logs, package
hashes, live Baker census and verified normal closure. The exact named
endpoint save timed out after play reached turn 200. The native Storekeeper
result comes from the original live log, independent of the save.

The scanner fixture and all ten CE Lua frontend tests passed. They cover
missing Base and missing customer penalties, legal and future Harbor
geometry, protected host plots, repeated customer entries, unique host
and building replacements, multiple Tailors Base deposits, and the shared
producer, customer, Builder and repair policy. The live results cover a
single world and cannot isolate one connector's effect.

## Live results

| Metric | Untuned | V2 | Shared Stage 2 |
| --- | ---: | ---: | ---: |
| Completed Bakers Quarters | 19 | 20 | 13 |
| Bakers with working Base at turn 200 | 4 | 5 | 5 |
| Bakers chains ever active | 1 | 4 | 4 |
| First confirmed Storekeeper | 145 | 143 | 98 |
| Confirmed Storekeeper chain-turns | 55 | 132 | 201 |
| Completed Tailors Quarters | 22 | 19 | 15 |
| Tailors with working Base at turn 200 | 4 | 3 | 3 |
| Active Tailors Stage 2 source property at turn 200 | 0 | 0 | 0 |

All three native Storekeeper audits cover turns 2–199. The four new
chain windows were 98–121 and 129–156, 161 and 172–199, 178–199,
and 102–199. The Tailors source property was inactive at every reported
publication. It has no independent payout audit in this trial.

The policy published on all 200 turns with zero omitted district packet
entries. The largest batch included 394 weak-site deductions. The sampled
native writes include both weak-site deduction bands for both industries.
The Harbor connector offered candidates in 25 turns, first at 141. The
capped score samples do not show a Harbor adjustment, so publication
alone establishes no actual Harbor score change. The Builder status
reported 163 positive score writes, versus 63 in v2, with zero faults.
These can repeat an evaluation of the same job and do not count Builder
assignments or completed improvements.

### Publication and native consumption

The publisher refreshes once per game turn for the original AI majors in
single-player. It commits one packet and keeps it available for the native
decisions that run during that window. The next publication normally logs
the previous window's results. Fractal committed 200 packets and had no
reported district-score faults or omitted district entries.

The samples confirm positive and negative Quarter score edits for both
industries. The Stage 2 building hook changed 32 scores. Its retained first
write per window identifies native writes for Granary, Wind Mill and
Textile Workshop. In the window before the final publication, the Workshop
bid for player 4, city 589832 raised its nomination score from 147803 to
262491 Q8. That city owned the Cotton and Lighthouse chain at plot 2457
and still lacked a Workshop at the endpoint. Lighthouse bids were
published on turns 196–200. The four windows with subsequent native
readbacks had zero Lighthouse writes, and turn 200 was the endpoint.

Native protection also applied district selector masks, Wonder score
changes and Builder improvement score changes. The last selector
readback recorded 132 masked rows across the session. This can include
repeated comparisons. The harvest guard was active and logged zero
rejections. There were no eligible Quarter repair offers or admissions
in this game. The static customer adjacency and Builder recruitment
rules load into the gameplay database and have no individual acceptance
receipt. The capped samples cannot settle whether the separate published
Harbor site offers reached an actual native score write.

### Exact receipts in the matched follow-up

The CE follow-up fixed a supplier-exclusion wiring gap. The existing joint
selector admitted its observation from a district score entry, so a city
with a supplier exclusion and no score edits could miss protection. The
selector now admits either kind of entry and restores the same native row
byte when it returns. The native fixture verified masking and restoration
with an exclusion-only publication.

The CSC publisher reads targeted native receipts before replacing each
packet. The Harbor receipt queries the existing journal for an exact
version, player, city, district and plot. It can see writes beyond the
64-record status sample. The building receipt identifies the ordinary
forecast, effective comparison and write separately. Its forecast observer
uses the existing building NetValue detour. The ordinary forecast caller
and comparison bytes were verified against stock XP2 hotfix hash
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
Quarter repair status now also counts native consideration when a
candidate's city reaches the stock district decision.

The matched Fractal replay used CSC commit `ddda28e` and CE review commit
`d8df47d`, with CE DLL SHA-256
`f8121151c787e4dcd4fea876eaaef5d6d1bb2b54561bc94d9d7da6385f21aa07`.
The shared controller ran ordinary play to turn 200 and closed cleanly.
The map and starting roster, plots and units matched. The native city
build, production queue, research and unit operation logs were byte-for-byte
identical to the earlier v2.1 run. Both audits found 201 Storekeeper
chain-turns. No native score or receipt faults or omitted receipts were
reported in the matched follow-up.

| Exact offers with a subsequent receipt | Published windows | Native forecasts or score attempts | Comparison writes |
| --- | ---: | ---: | ---: |
| Harbor site | 28 | 28 | 28 |
| Granary | 147 | 146 | 24 |
| Wind Mill | 38 | 37 | 4 |
| Textile Workshop | 32 | 32 | 4 |
| Lighthouse | 4 | 4 | 0 |

All 28 Harbor offers had an actual native write and a cache observation
for the same site. Five city selector calls were observed across those
offer windows. Three exact wins covered two distinct Harbor sites, plots
2383 and 1437. The selector return does not establish construction or
whether the bid changed the winner.

The Lighthouse was forecast in every observed offer window. None reached
the ordinary building comparison for that exact candidate. Its turn-200
offer had no following window. The result shows native forecast exposure
and no score edit. It does not establish why the ordinary comparison
did not run. The Workshop for city 589832 again reached the comparison
and was written in the turn-199 window. There were zero Quarter repair
offers and no harvest rejections during the follow-up, so those paths
were not exercised by this map.

The original archived live log and replay package manifest are in
`Desktop/Codex/csc-ai-native-receipts-20261108/fractal`. The CE build
passed 101 native checks, four hook-group checks and instruction-call
delivery and restoration. Eleven CSC Lua frontend checks passed.

## Recovered endpoint census

The shared controller loaded the fresh native turn-200 autosave read-only.
It confirmed turn 200 with autoplay inactive and advanced zero turns.
The recovered save hash is
`a5462edb6e0bf3dd8ae3c3b235b7b1c282671a71bd59e46fc065226d6764ecc1`.
All 13 Bakers Quarter identities, tiles, completion and damage states
match the original live census. The recovered autosave is archived as
`run-v3-fractal/endpoint-recovered.Civ6Save`. The detailed readback and
clean recovery closure are in `endpoint-detail-run-v3`.

| Completed Quarter outcome at turn 200 | Bakers v2 | Bakers shared | Tailors v2 | Tailors shared |
| --- | ---: | ---: | ---: | ---: |
| Adjacent owned Base deposit | 10 | 9 | 8 | 7 |
| No adjacent owned Base deposit | 10 | 4 | 11 | 8 |
| Adjacent owned Base and Stage 2 host | 8 | 7 | 0 | 2 |
| Adjacent mapped Stage 2 host | 12 | 7 | 0 | 3 |
| Adjacent working Stage 2 customer building | 6 | 4 | 0 | 2 |
| Unpillaged Stage 2 producer building | 16 | 8 | 17 | 10 |
| Working Base improvement | 5 | 5 | 3 | 3 |
| Active Stage 2 source Service property | 3 | 3 | 0 | 0 |

The three Tailors Quarters beside a Harbor had distinct missing links.
Plot 2457 had a working Cotton Plantation and Lighthouse and lacked a
Textile Workshop. Plot 1436 had a working Workshop but still needed its
Sheep improved and a Lighthouse. Plot 2502 had a Workshop and Lighthouse
and lacked an adjacent owned Base deposit. The endpoint cannot tell
whether a missing deposit was absent at placement or lost later.

Five completed Bakers and six completed Tailors sites match a sampled
weak-site deduction by exact player, city, district type and tile. This
shows that the finite deductions still allowed some penalized sites to
win. The samples alone cannot establish which alternative would win
without tuning, or why a site later lost a qualifying link.

## Lighthouse follow-through

The archived receipt run's turn-200 autosave was replayed through turn
224 with the same CSC and CE packages. The save SHA-256 begins
`803ffeadfefb091b`. In Kőszeg (player 2, city 524295), the Lighthouse
was legal and absent at load, with its Harbor at plot 1437. The first
attempt stalled on the stock Wonder playback popup at turn 200. The
shared controller's Wonder guard applies within five turns of its
target. On retry the controller ran a four-turn opening segment, closed
the popup itself, then continued to turn 224.

The ordinary CityBuild nomination pass at XP2 RVA `3e1580` returns early
when the unit-or-building plan slot is occupied. It reads that slot at
offset `0x4` in the plan object pointed to by `CityBuild + 0x430`.
The ordinary selector call at `3e1605` supplies flags `0,0`. Its return
address `3e160a` is the CE hook's caller check. These code ranges match
the Ghidra reference `324c51e9` and Steam hotfix image `092abfbb`.

In the instrumented replay, the slot was free on turns 200, 207, 214 and
217. The ordinary building selector compared an eligible Lighthouse on
the first three turns. It still ran its building loop on turn 217, but
the Lighthouse was already built by then. Forecasts continued while
the plan slot was occupied. The native plan slot and the production
queue are separate. The game bought the Lighthouse on turn 216 while
a Nuclear Submarine was still in production. The Frida selector exit
hook rewrote the caller return address that CE checks. That run
establishes the slot and selector timing. Its zero-write receipts are
invalid as a test of CE bid delivery.

The clean replay used the same packages and CE's own receipts, with no
Frida attachment. CSC published a new eligible offer each turn. CE
recorded one actual comparison and one write for the exact Lighthouse
at each opening below. The receipts appear on the following turn.

| Decision turn | Score before (Q8) | Score after (Q8) |
| ---: | ---: | ---: |
| 200 | 233441 | 246753 |
| 207 | 246778 | 260090 |
| 214 | 229661 | 242973 |

Each delta was 13312 Q8, or 52 native utility points. The turns between
those openings recorded forecasts with no ordinary comparison for that
candidate.

The clean run submitted Lighthouse contracts on turns 207 and 214
and bought the Lighthouse on turn 216 while the Nuclear Submarine was
still in production. CSC stopped publishing the offer on turn 217.
The instrumented run logged the same submissions and purchase, so this
replay demonstrates score delivery and physical follow-through without
establishing that the boost changed the choice. There was no observed
expiry gap. Keep the existing refresh rate for this path.

The trace and clean evidence are archived respectively in
`Desktop/Codex/csc-ai-lighthouse-followthrough-20261108-02` and
`Desktop/Codex/csc-ai-lighthouse-followthrough-20261108-03`. The clean
evidence pairs the scoped `Lua.log` receipts with the stock
`AI_CityBuild.csv` and `City_BuildQueue.csv` logs.

Both continuations reported one active Tailors source property on every
publication from turn 201 through 224. That property was already present
before Kőszeg's Lighthouse purchase on turn 216. The aggregate does not
identify the Quarter or audit the naval production bonus. The original
normal-start run still recorded zero active properties through turn 200.

## Long-term placement follow-up

The 10 November Fractal restart tested CSC revision `bc878976` from turn 1
through 200 on Online speed. It used the same two seeds, start signature,
AI leaders, initial plots and units as the archived receipt run. The CSC
package differed only in four placement Lua files. Both arms loaded CE
`f8121151c787e4dcd4fea876eaaef5d6d1bb2b54561bc94d9d7da6385f21aa07`.
CSC tuning was active in both arms, with stock AI and no probe policy.
The earlier readiness-first candidate was stopped at turn 152 and excluded.

The revised planner logged 57 Tailors site evaluations with both the
supplier improvement and Harbor pending. These are repeated evaluations,
not distinct plots. For example, on turn 29 player 4 had 11 legal Tailors
tiles, ten without a qualifying Base and one with both links pending.
The one viable site earned a placement offer. Across the whole map the
planner published 287 Tailors offers, none reaching its projected +4
adjacency band. Native samples included 22 Tailors writes of +24 utility
points and 49 Bakers writes of +48, the same sampled counts for those
bands as in the control. The samples alone cannot attribute a write to
the pending site in that example.

The two arms had byte-identical production queue, research and unit
operation logs. The city-build log differed in one building nomination
on turn 199, with a Seaport replacing a Textile Workshop candidate.
Confirmed Storekeeper operation matched across all 198 sampled turns
(2–199). The same four chains recorded 52, 29, 22 and 98 active turns,
for 201 chain-turns in each arm.

The native named checkpoint timed out after the live turn-200 census.
The shared controller verified a clean exit and restored preferences.
The turn-200 autosave was written during the run, immediately before the
endpoint readback. Its SHA-256 is
`7f456bf7ffac3d3ddae3c3fa2779d9ad85eaa064f17b75ff3b4db5d775a135a0`.
Loading it from the autosave folder returned to the menu. A byte-identical
copy in `Saves/Single` loaded at turn 200 with autoplay inactive. All 13
Bakers identities, plots and damage states matched the live census.
Both policies finished with the same 13 Bakers and 15 Tailors on the
same plots. The placement quality measures below also matched.

| Completed Quarters at turn 200, both arms | Bakers | Tailors |
| --- | ---: | ---: |
| Adjacent owned Base deposit | 9 | 7 |
| No adjacent owned Base deposit | 4 | 8 |
| Adjacent owned Base and Stage 2 host | 7 | 2 |
| Working Base improvement | 5 | 3 |
| Adjacent working Stage 2 customer | 4 | 2 |
| Active Stage 2 source Service property | 3 | 0 |

This seed established that the policy can publish a pending-site offer.
It did not show that the revised ranking changes placement or deferral.
The endpoint also cannot establish when a Base deposit was lost.
Artifacts are in `Desktop/Codex/csc-ai-placement-potential-20261110`.
The zero-turn readback is `endpoint-detail-recovered/fractal.json`.

### Saved-world placement candidates

A separate zero-turn survey loaded three archived turn-200 positions using
the same planner and CE DLL as the Fractal restart. The shared controller
verified the saved boundaries and read the production planner without
publishing offers. The 283 Continents, 280 Pangaea and 276 Fractal rows are
owned legal Quarter-site pairs after the planner's ordinary exclusions.
The snapshots returned 11 +4-or-higher Bakers offers and no Tailors
offer in that band. They also contain 102 weak-only city/profile pairs.
These are screening counts for three saved worlds.

Mainz (player 3, city 327684, Continents) offers Bakers plot 1243 at +4
adjacency and +12,288 Q8. Plot 1167 received no CSC placement adjustment.
Three other sites received deductions. Geelong (player 4, city 327684)
has +5 at plot 1426, an unadjusted plot 1499 and three weak sites.
Both cases can separate the positive band from deductions if the
native planning slot opens. The census itself has no native comparison,
commitment or causal placement result.

Artifacts are under
`Desktop/Codex/csc-ai-problems-1-2-20261110/owned-site-survey-01`.

### All-stage neighbor forecast

The expanded scanner reads the loaded sales and goods-provider tags for
each Quarter. It combines the actual contribution of already placed
neighbors with one projected neighbor on an empty, owned, revealed
footprint. Stage 2 building and Service gates remain separate. The
offline fixture verified a future Commercial Hub and City Lights Rural
Community in a position with no feasible Harbor. It also verified the
separate provisional 16-point Harbor offer, native target requirement
and same-city population-slot guard.

The three matched turn-200 readbacks used the same 839 legal pairs.
Strong Bakers offers increased from 11 to 21. Strong Tailors offers
increased from zero to two, at Aachen and Mistahi Sîpihk. Missing-host
deductions fell from 147 to 23 across both Quarter types. Missing-Base
and covers-material deductions stayed at 652 across the same pairs.

Aachen's plot 1094, with a viable Base and four river edges,
moved from a missing-host deduction of 32,768 Q8 to an offer of
12,288 Q8. The observed change comes from the planner. A native score
write, winning comparison and construction need separate evidence.
The same empty footprint could also host a +5 Bakers site. The two
Quarter offers compete for it if both are still available at selection.

Astra's evidence review identified the remaining ordering limit. The
forecast uses current readiness when selecting one feasible future
neighbor and can keep the first candidate on equal readiness. An
unequal-value choice between future neighbors needs a separate test
before treating this as the maximum possible long-term adjacency.
Artifacts are under
`Desktop/Codex/csc-ai-problems-1-2-20261110/owned-site-survey-all-customers-01`.

### Aachen native comparison

Both arms cold-loaded the same turn-200 Continents checkpoint
(`e333251ec7318fb6b170678a956c28e02e2f9b01c4c4753c99e84b1a112fe19a`).
They used the same CE DLL and differed only in the scanner. The same
read-only observer recorded the returned winner and matrix values at
the native `CheckForDistrict` return site `3e0f3c`. It made no gameplay
writes. The first reference attempt exited during loading. The repeat
verified the exact staged packages and expected test configuration before
loading the same save. The controller restored the recorded original
preferences on exit.

| Turn | Earlier Tailors 1094 (Q8) | All-stage Tailors 1094 (Q8) | Encampment winner (Q8) |
| --- | ---: | ---: | ---: |
| 201 | 168,761 | 213,817 | 1,017,638 |
| 203 | 168,761 | 213,817 | 1,023,276 |
| 205 | 177,817 | 222,873 | 1,969,961 |
| 207 | 186,486 | 231,542 | 2,076,713 |

Each final Tailors score rose by 45,056 Q8, exactly the difference
between the old `-32768` and new `+12288` Lua adjustments. The other
observed Tailors cells and the Encampment winners matched. The observer
recorded a populated reservation handle at 1094. It did not resolve the
effective threshold, so an eligible row flag does not establish whether
that pair could pass the reservation test. The Encampment led by at
least 803,821 Q8 even before considering that gate. Aachen submitted
no Tailors construction contract through turn 208 in either arm.

This verifies a native score effect for the wider neighbor forecast.
The next comparison needs a site and competing investment with a
smaller score gap, and an observed unreserved row or effective threshold.
Artifacts are `aachen-tailors-selector-01` and
`aachen-tailors-selector-reference-02` under the same Desktop folder.

### Nicopolis weak-site deduction

A read-only scout used the same Continents save and all-stage scanner to
watch the ordinary district selector. It screened 222 surveyed owned
Quarter pairs across 30 comparisons through turn 208. It shortlisted
unreserved weak sites whose final score gap was smaller than their
surveyed deduction. This screen suggests a replay case. It cannot
predict how the early adjustment affects all downstream components.

The matched ablation used the same turn-200 save and CE DLL. The only
package change omitted one weak site entry for Nicopolis (player 1, city
524295), Bakers district 36, plot 472. The scanner still read the same
site and the diagnostic changed no positive offers or other deductions.
The two native observers read the same stock selector return and wrote
no game data. The native comparison on turn 203 followed the earlier
Water Park plan recorded on turns 200–202.

| Turn 203 | Production policy | Plot 472 deduction omitted |
| --- | ---: | ---: |
| Bakers plot 472 (Q8) | 347,924 | 413,460 |
| Bakers plot 398 (Q8) | 396,462 | 396,462 |
| Returned and reserved plot | 398 | 472 |
| Request in the district tree | Purchase plot 398 | Construct Bakers on plot 472 |

Plot 472 was unreserved at comparison. Its finished score increased by
exactly 65,536 Q8. The other three near-margin cells in the scout also
matched their ablation scores. The treatment with the deduction selected
frontier plot 398. The stock district tree reported an accepted purchase
request for that plot through turn 207. The ablation submitted and
accepted a Bakers construction request for owned plot 472 on turn 203.
At the ablation endpoint both plots were empty and neither had a viable
owned adjacent Bakers Base. A later Hippodrome plan had reserved plot 472.

The deduction changed which tile Civ chose and which request it issued.
The frontier alternative fell outside the owned-site planner. This case
does not establish a stronger Quarter site, Gold spending, deferral of
the Quarter type or eventual construction. A frontier-aware test needs
both plot ownership and the proposing city, which are distinct in the
native plot-analysis row.

Artifacts are `weak-site-scout-continents-01` and
`nicopolis-weak-ablation-01` under the same Desktop folder.

The 11 November repeat in `nicopolis-original-durable-01` reproduced
the original turn-203 winner and both scores using the same scoped
observer as the ablation. Boundary snapshots show plot 398 unowned
through turn 203 and owned by Nicopolis at 208. It passed
`CanHaveDistrict` even while unowned. Neither plot had an owned viable
Base in those snapshots. The visible neighboring resources reported
beside 398 were Silver and Salt. Ownership alone does not identify
whether acquisition used Gold or culture.

The repeat restored the recorded preferences left by the interrupted
load and verified a clean exit. The durable fixture runner is
`project/tools/native_ai/late_placement/nicopolis_replay.py`.
Its separate frontier mode is a scoped diagnostic of CE admission,
rather than the production frontier policy.

### Frontier score admission

The `nicopolis-frontier-durable-01` diagnostic added one negative
entry for unowned Bakers plot 398 while retaining every existing
offer and deduction. On turn 203 its finished score fell from
396,462 to 330,926 Q8. Owned plot 472 stayed at 347,924 Q8.
The native selector chose another unowned frontier site, plot 401,
at 391,714 Q8. The CE DLL was unchanged.

This establishes that the existing CE score hook can consume an
entry for a proposing city before that city owns the plot. The
BUILD-operation target list used by the owned planner is therefore
too narrow for weak-site coverage. A second footprint can evade
a deduction applied only to the first recorded case.

The integrated correction enumerates radius-three map geometry,
requiring an unowned, revealed, district-free site adjacent to
the player's land and passing `CanHaveDistrict`. It prices
covering a visible mapped material with the existing deduction.
It also prices an absent Base only when all neighboring plots
are revealed, all mapped Base resource types are visible, and
there is no visible own or unowned mapped Base nearby. Fog,
hidden Base types and potential supplier acquisitions keep
this frontier deduction neutral. CE still validates the native
row's city and eligibility before applying an entry.

These extra uncertainty guards apply to the new frontier scan.
The existing owned-site scan still uses owned viable suppliers
and needs separate purchase-path qualification. The correction
does not yet price a missing frontier customer footprint.

The `nicopolis-integrated-frontier-01` replay staged the two
production files, the scanner and its publisher, from the main
CSC source. It contained no fixed-plot score injection. On turn
203 it reproduced the diagnostic's 330,926 Q8 at plot 398,
347,924 at owned plot 472, and selected frontier plot 401 at
391,714 Q8. The district tree reserved plot 401 and issued
an accepted purchase request. The packet contained at most
520 entries through turn 208 and reported no omitted entries.
No planner failure was recorded. The independent Astra review
found no correctness blocker in the new frontier path.

All six neighbors of plot 398 were revealed at the source
snapshot. Its visible neighboring resources were Silver and
Salt, neither a Bakers Base. The current readbacks did not
classify plot 401's full chain prospects. A changed native
winner therefore establishes delivery and coverage without
proving an improved site or a completed Quarter. Its actual
purchase, supplier and customer path are the next follow-up.

### Following the frontier request through turn 216

The `nicopolis-purchase-401-01` continuation used the same turn-200
save, CE DLL and integrated production scanner. A separate read-only
observer watched the plot branch of `Purchase::Start`: its recomputed
quote, the negative Q8 argument at the Gold debit call, that call's return,
and the annex call's return. Native identities and instruction fingerprints
were checked before attaching. Boundary snapshots covered plots 398,
401 and 472 and the revealed facts around them.

The turn-203 winner again was Bakers at plot 401, 391,714 Q8.
The district tree reported the same accepted plot-purchase request
**4333** on turns 203–213. On 214 it said `Not Buying anything`.
The next observed joint comparison, on 215, chose Harbor at plot
327, 362,786 Q8. At the turn-216 endpoint plot 401 was still unowned
and empty. It had no known adjacent Bakers Base. Neighbor 402
remained unrevealed; 328, unrevealed at source, was now revealed
without a resource. This is an uncertain site under the frontier
policy, rather than a demonstrated good supply-chain site.

The scoped purchase trace contained **zero events and no observer
fault**. Plot 398 had become Nicopolis-owned and remained empty,
with zero viable owned Base and one Specialty supplier. Without a
positive purchase event validating these callbacks in this interval,
the empty trace does not establish its acquisition mechanism. It also
does not identify which quote, budget, command or contract gate kept
plot 401 unbought. A debit-return record would repeat the preserved
Q8 argument; it would not independently measure a treasury change.

The shared controller closed with native exit code zero, no remaining
owned process, verified preference restoration and verified package
retirement. Independent Astra review agreed that the evidence proves
neither paid acquisition nor an improved Quarter foundation. Problems
1.5 and 1.6 remain open here. The next diagnostic follows the request
upstream through the city quotes and earmarked plot/slush savings.

Evidence hashes:

| Artifact | SHA-256 |
| --- | --- |
| `purchase-trace.json` | `5b89c221819eab292290ef7ffe8ca3eaabfd6c6e869069bf08c684869391c853` |
| `AI_Behavior_Trees.csv` | `86462c9806211e7bf5dd53e752a0439751f16bdbe8327275223dd5f5f898503e` |
| `selector-trace.json` | `159874048c7b59271742006d6b5805c66484754058e26cbd1b73856f4ca67469` |

The first attempt at the upstream diagnostic, `nicopolis-purchase-budget-01`,
was interrupted before menu configuration. Its worker and native process
were absent on recovery. No preference snapshot or controller command
journal existed. Both temporary packages exactly matched the recorded
manifests and were retired. It produced no gameplay evidence and is not
counted as an engine failure.

The second attempt, `nicopolis-purchase-budget-02`, reached a turn-210
progress receipt but left neither a final native trace nor a closure
receipt. Its recorded worker and native process were absent on recovery.
Henno reported Shadow instability that morning. This attempt supplies
no conclusion about purchases or the game engine. The follow-up adds
immediately streamed, host-synced partial receipts so delivered native
observations can survive a worker or machine interruption. Asynchronous
trailing messages may still be lost. Exact integrated package recovery
retains the original preference snapshot for final restoration.

### Native quotes reached an insufficient earmarked plot fund

The `nicopolis-purchase-budget-03` replay retained the same integrated
policy and exact checkpoint. Its complete selector trace and behavior-tree
CSV were byte-identical to `nicopolis-purchase-401-01`. Adding the read-only
Economic observations did not change those recorded choices or requests.
The frozen purchase trace contains 110 per-city quotes and eleven
selected-city savings checks on turns 204–214, with no observer fault.
Both streamed journals match their final traces exactly in content and
order: 121 purchase observations and two district selections.

Only Nicopolis had a positive quote for plot 401 in each attempt; the
other nine player-1 cities returned `-1`. The native selected-city
savings check recorded the following values, converted from Q8 to Gold:

| Turn | Quote | Plot fund | Slush fund | Required plot fund | Combined funds |
| --- | ---: | ---: | ---: | ---: | ---: |
| 204–206 | 145 | 0 | 0 | 36.25 | 0 |
| 211 | 150 | 24.1484 | 75.0742 | 37.5 | 99.2227 |
| 213 | 120 | 29.0234 | 87.7070 | 30 | 116.7305 |
| 214 | 150 | 33.3398 | 101.1328 | 37.5 | 134.4727 |

The Q8 factor was 64, representing one quarter of the quoted cost.
In all eleven samples the earmarked plot fund was below that first
threshold. The combined funds were also below the quote, but this is
a reconstructed predicate: the native combined-funds branch follows
the first check and is skipped when the first fails. The Ghidra recheck
confirmed quote return `459169`, saved fund pointers at stack
`+0xd0/+0xd8`, the Q8 cost multiplication, first rejection at
`4591b0`, and the later combined-funds rejection at `4591c9`.

The funds were not permanently zero. The AI accumulated them naturally,
and on 213 it lacked only 250 Q8 in its plot fund and 837 Q8 in the
combined funds. The quote changed again before the next attempt. This
does not establish how much actual treasury Gold the player held: its
earmarked savings and displayed treasury are separate observations.
Increasing the Quarter's site value alone would not make the captured
fund balances meet this gate. A subsidy or own-funds allocation would
need separate delivery and accounting evidence.

There were no command-level quote, debit or annex receipts for any
player-1 plot in this interval. The paid-command callbacks still lack a
natural positive control. Economic attempted plot 401 on 214 even
though that turn's tree log said `Not Buying anything`; that text must
not be equated with contract cancellation. The endpoint still had
unowned, empty plot 401 and no known adjacent Base. The next acquisition
fixture should have credible known supply and customer geometry and
record actual treasury and income alongside quotes and earmarked funds.

`purchase-trace.json` SHA-256 is
`ed2e45457960f0ec740b9d19fd9b7f20822bc4bf9b075005c022bc6deff888eb`.
Selector and behavior-tree hashes match the preceding evidence table.
Independent Astra review confirmed the register/stack decoding, arithmetic,
stream equality and the distinction between the binding first check and
the unexecuted second predicate. This diagnoses the funding gate and
does not close the acquisition, foundation or profitable-chain tests.

The shared controller verified normal closure at 216: native exit zero,
no remaining owned process, original preferences restored and exact
temporary packages retired. All observers and recovery code remain
diagnostic tools outside the CSC mod. Production tuning was unchanged.
