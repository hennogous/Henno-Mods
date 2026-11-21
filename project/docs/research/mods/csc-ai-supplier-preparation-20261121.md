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
