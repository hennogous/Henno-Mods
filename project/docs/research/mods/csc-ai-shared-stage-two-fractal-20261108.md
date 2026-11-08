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
