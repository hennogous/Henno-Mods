# CSC and City Lights economy benchmark

Small Continents, Online speed, Prince, Gathering Storm. Each seed fixes
the same six leaders and rules across Vanilla, CSC, City Lights, and the
combined stack. The five original AI seats supply the totals. CSC uses its
qualified default guidance and Dev CE. Vanilla and City Lights alone use
the original GameCore. CSC's material placement can change resources and
some starting plots even with the same seed and roster. The comparison
measures each installed stack's whole-game outcome.

## Verified Online endpoints

Sixteen turn-250 archive and Load Game copies match their save hashes.
The complete four-arm sets are 171124601, 171124611 and 171124613. One
601 arm reuses the earlier identical policy, content and opening receipt.
The first seed's City Lights-only run completed after the controller used
its supported five-turn popup-recovery windows.

| Seed | Verified arms | Interrupted arms |
| --- | --- | --- |
| 171124601 | All four | — |
| 171124605 | — | Vanilla lost the observer around turn 222 in both attempts |
| 171124611 | All four | — |
| 171124613 | All four | — |
| 171124615 | Vanilla, CSC, City Lights | Combined lost the observer |
| 171124617 | Vanilla | CSC lost the observer. The remaining arms did not start. |

The controller closes a game when the original observer is eliminated. It
cannot verify a bounded continuation on that seat. Keep partial seeds out
of the four-way mean and preserve their completed arms for the contrasts
they support.

## Mean of the three complete seed sets

All values are totals across the five AI seats, averaged over the three
seeds. Production, Food and Gold are per-turn rates. The sampled averages
use ten equally spaced snapshots from turn 25 to 250.

| Turn-250 metric | Vanilla | CSC | City Lights | Combined |
| --- | ---: | ---: | ---: | ---: |
| Production | 1,621 | 1,679 | 2,623 | 3,112 |
| Food surplus | 235 | 242 | 313 | 327 |
| Gross Gold | 2,096 | 2,084 | 5,768 | 6,994 |
| Maintenance | 1,180 | 1,421 | 3,309 | 3,628 |
| Net Gold | 915 | 663 | 2,459 | 3,366 |
| Treasury | 2,662 | 2,871 | 9,008 | 7,798 |
| Population | 539 | 570 | 633 | 659 |
| Cities | 51 | 43 | 53 | 51 |

| Sampled average | Vanilla | CSC | City Lights | Combined |
| --- | ---: | ---: | ---: | ---: |
| Production | 672 | 720 | 1,015 | 1,144 |
| Food surplus | 160 | 186 | 200 | 202 |
| Gross Gold | 726 | 786 | 1,915 | 2,135 |
| Maintenance | 386 | 462 | 1,049 | 1,143 |
| Net Gold | 340 | 324 | 866 | 992 |
| Treasury | 1,220 | 1,478 | 2,794 | 3,672 |
| Population | 266 | 287 | 303 | 308 |
| Cities | 30 | 28 | 31 | 30 |

## Variation and combined effects

Each entry is turn-250 Production / net Gold per turn. A blank has no
verified turn-250 value.

| Map seed | Vanilla | CSC | City Lights | Combined |
| --- | ---: | ---: | ---: | ---: |
| 171124601 | 1,629 / 1,227 | 2,136 / 864 | 2,746 / 2,865 | 3,031 / 3,438 |
| 171124611 | 1,397 / 445 | 1,292 / 215 | 2,763 / 663 | 3,155 / 2,238 |
| 171124613 | 1,838 / 1,074 | 1,609 / 910 | 2,360 / 3,848 | 3,149 / 4,423 |
| 171124615 | 1,920 / 449 | 1,599 / 385 | 3,611 / 3,492 | |
| 171124617 | 2,074 / 741 | | | |

City Lights alone increased endgame Production and net Gold on all four
seeds with both those arms. CSC alone increased Production on one of four
and ended with lower net Gold on all four. About 60% of the City Lights
net Gold gain over vanilla among the three complete sets came from 613.
On 601, Amanitore accounted for 55% of the sum of absolute seat-level net
Gold changes with City Lights alone, and Philip II accounted for 55% in
the combined comparison. On 613, no seat accounted for half of either
endgame result.

For a matched seed, the combined effect beyond the sum is `combined − CSC
− City Lights + vanilla`. The three endgame net Gold results were +936,
+1,804 and +740. Over the ten checkpoints, the results were −35, +309 and
+151. The same endgame statistic for Production was −222, +496 and
+1,017. Production gains exceeded the sum of the individual gains on
two maps. The Gold interaction was larger at turn 250 in all three.

Raw inputs, 25-turn snapshots and save names are in `Desktop/Codex/`
under `csc-cl-economy-factorial-20261125` and
`csc-cl-economy-four-added-seeds-20261126`. The replayable reader and batch
script are `project/tools/native_ai/late_placement/economy_factorial.py`.
