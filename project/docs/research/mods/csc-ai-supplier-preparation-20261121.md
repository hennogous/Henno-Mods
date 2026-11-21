# Preparing adjacent suppliers before the buyer opens

Problem 3 targets a working adjacent supplier by ten Online turns after
the mapped buyer opens. In the previous Continents run, six of thirteen
eligible buyers had working supply at opening. Two of the seven that
needed work met the ten-turn target. The [case timelines](csc-ai-axum-builder-availability-20261120.md#how-the-prompt-cases-got-supplied)
show the separate job-opening and Builder waits.

## Candidate

The established plot purchase preference can secure the first mapped
deposit in each class. A built Quarter can now also price the first
legal improvement while its exact buyer is queue-eligible or within
five turns of finishing its current research. The latter requires the
buyer's local building gates to be met. The uncommitted quote counts
half the expected ordinary transaction after research, an allowance
for the queue, and construction. One job receives at most 13 native
utility points (3,328 Q8) for preparation, even if several uncommitted
buyers share the plot. Queue commitment restores the existing ordinary
forecast and near-completion floor. The candidate uses the same native
improvement, acquisition and Builder channels as the control.

The working-buyer repair preference follows loaded Service requirements.
An audit of the loaded gameplay database and the same Lua catalogue used
by the publisher found these material gates for both Quarters.

| Stage | Bakers and Tailors material requirements |
| --- | --- |
| 2 | One improved Base |
| 3 | One improved Base |
| 4 | One improved Base and one improved Specialty |

The policy can prioritize Base for a working Stage 3 source even while
the Stage 2 buyer is out. In a recoverable Stage 4 outage it can give the
best legal repair in each missing class the existing 56-point upper band.
It adds the repair priority without claiming the full Service cash flow
for each repair. The existing economic value still determines whether
there is a reason to pay for another Builder. The policy tests exercise
research, queue priority, Stage 2 and 3 Base-only recovery, and Stage 4
repair with both classes damaged.

## Matched observation

The shared controller records the first queue-eligible buyer separately
from a published early bid. The common passive clock requires a legal
adjacent improvement and an unlocked, queue-legal, committed, or working
buyer. It records the exact legal and working plots for each material
class. An already-improved plot is scored in its own cohort. Read the
ordinary improvement tree logs for reservation and Builder assignment,
then verify the actual improvement at buyer opening and at turn +10.
Supply gained before +10 and lost later remains distinct from working
supply at the +10 census. The census also distinguishes late eligibility,
late openings and interrupted chains.

For treatment, also report first eligibility witnessed by an accepted
early offer. This captures jobs that were still missing during the
final research and finished before the common queue-eligible survey.
Keep the common survey clock for the direct comparison because the
control has no early-offer receipt.

The two SDK-generated packages use the same CE and CSC gameplay files.
Compare `257dfdc9` with `c6412e9e` for fresh games. The first turn-150
checkpoint pair used `cd541ad1` for preparation before the separate
Stage 3 repair correction. Both pairs are under
`Desktop/Codex/csc-ai-problem3-preparation-20261121`. Run
`supplier_deadline_results.py` against each completed ordinary run.

### Continents checkpoint, turns 150–175

Both runs matched all 122 structural opening rows and closed normally.
The treatment published fourteen early offers for three exact jobs.
Antium's Base Flax received a 13-point offer on turns 150–156 for its
future Wind Mill. Both runs reserved a different plot first,
then reserved Flax on 166, recruited on 167 and completed it on 169.
The working-supply survey reached it on 170 with the buyer online on 161.

Susa compared the Plantation on Tailors Base Cotton plot 1102 at 320
utility in control and 333 under treatment on turn 173. Both selected
that plot and recruited a Builder. This confirms the uncommitted bid
reached native job pricing. The published Specialty Plantation offer
for the Café concerned a different plot, 1103. The replay ended before
its buyer opened or the proposed site received a reservation.

The two arms had identical city production, purchase and unit operation
logs. The only tree log differences were the two Susa utility readouts.
Both arms trained 19 and purchased 11 ordinary Builders in the five AI
empires during the replay. Publisher mean and maximum were 1.820 and
2.542 seconds in control, and 1.905 and 2.924 in treatment over 26
publications each. Use the fresh games to assess scheduling benefit and
performance across the first unlocks and both buyer stages.

### First ordinary Fractal control, Online turns 1–250

The control reached turn 250 on map seed `28061117` and game seed
`38061117`. Its preparation clock and outcome windows were observed on
every turn. Of 11 Base buyers that needed work when eligible, six had a
reservation, five an assignment, and five working supply by opening.
By opening plus ten, ten had a reservation and assignment but still
only five had working supply. Eight further Base buyers were already
supplied at preparation. One Base case was interrupted before the deadline.

Six missed Base buyers included four close outcomes. Kingston, Mecca and
Cairo started to work on turn +12, and Kish on +13. The city tree at
Kingston, Mecca and Ur logged a failed protection check after a Builder
had already been assigned. Kish and Cairo completed after movement.
One Tailors buyer took 35 turns, and Ur remained unsupplied. The sample
therefore gives separate tests of earlier admission, route time, and
whether a Builder stays with a job after assignment.

The one fully observed eligible Specialty buyer was already supplied
when preparation became possible. Seven other Stage 4 buyers opened
without an eligible Specialty deposit. Six had none adjacent, and the
seventh's adjacent Tea was foreign-owned. The treatment on this seed
can qualify earlier Base work. A second map with eligible missing
Specialty cases is necessary for the full goal.

### First ordinary Fractal treatment, earliest changed decision

The ordinary treatment matched the control's opening map, AI seats,
starting plots, starting units, and native inputs. The first different
native tree or city production record was Knossos on turn 57. Both arms
had tried the Farm at (36, 29) on 55 and had to reopen the job. Control
then selected the Mine at (33, 29) at 81 utility. Treatment selected the
mapped supplier Farm again at 93. The two arms' native Builder contract
730 carried those exact values. The first different unit operation was
on turn 62.

The Farm finished on turn 65 in treatment and 69 in control, four
Online turns earlier. The physical working-supply surveys first saw it
on 66 and 70. Both were within their own buyer deadlines. Control had
completed the competing Mine at (33, 29) on 64. Through turn 140 the
treatment had not logged that Mine completion in Knossos. It opened
the separate Mine site at (36, 28) one turn later. Both arms had 3 of
5 eligible Base buyers working by opening plus ten among buyers with
a completed deadline window at turn 140.

### First ordinary Fractal pair, final turn 250

Both arms reached the deadline and closed cleanly. The table counts
buyers that lacked working supply at preparation and had a full window.
Reservation and assignment columns are the observed stock improvement
tree actions on legal supplier plots, including assignments that carry
an older reservation. Working columns use the physical survey.

| Material and arm | Needed work | Already supplied at preparation | Reserved / assigned / working by opening | Reserved / assigned / working by +10 |
| --- | ---: | ---: | ---: | ---: |
| Base, control | 11 | 8 | 6 / 5 / 5 | 10 / 10 / 5 |
| Base, treatment | 11 | 9 | 7 / 6 / 5 | 11 / 10 / 8 |
| Specialty, control | 0 | 1 | 0 / 0 / 0 | 0 / 0 / 0 |
| Specialty, treatment | 1 | 1 | 0 / 0 / 0 | 1 / 1 / 1 |

Treatment reached 7/9 Bakers and 1/2 Tailors Base cases. Control reached
5/10 and 0/1. Counting accepted pre-unlock offers as proof of earlier
eligibility gives the same aggregate treatment counts. Seven Specialty
openings in each arm lacked legal supply. Control also had one late
Specialty opening and an interrupted Base window. Treatment had two late
Specialty openings, one late Base opening and one Base opening without
legal supply. Buyer dates and cohorts can change after the games diverge.

Québec's Bakers Quarter at 696 provides the first Specialty follow-through
case. The treatment offered its Berries Plantation at 622 from turn 123,
published a higher quote once the Café entered production on 134, and
had the working Café on 139. Québec reserved and staffed the site on 142,
and built the Plantation on 145. The working supply was observed on 146,
seven turns after opening. The control had no open Café at that Quarter
by 250, so it gives no same-buyer timing comparison.

The matched Knossos decision was the first directly observed trade-off.
Its competing Mine at (33, 29) completed in control on 64 and had no
completion in treatment through 250. Across the original AI players,
control trained 98 Builders and bought 129. Treatment trained 111 and
bought 110, six fewer acquisitions in total. All other recorded queue
completions were 1,390 vs 1,327. The empire-wide counts include later
divergence after the early local choices.

Control resolved five of six Base supply outages in 3, 8, 8, 23 and 34
turns. Its sixth chain became unavailable. Treatment resolved all six
in 8, 8, 12, 12, 13 and 29 turns. These are buyer episodes, so a shared
plot can interrupt two buyers. The whole publisher averaged 1.377 s in
control and 1.569 s in treatment, with maxima of 3.064 and 3.468 s over
250 turns. The 0.192 s increase in mean includes the changed world state.
