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
