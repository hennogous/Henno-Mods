# Material development matched campaign

Compare normal Small Fractal games through turn 250 on Online speed. Map seed
`28061117`, game seed `38061117`, with City Lights, Resourceful 2, Sukritact's
Resources, Latin American Resources and Extended Policy Cards. The shared
controller freezes the packages and verifies the starting map, leaders and
opening state. Stock AI is the opponent in both arms. The control freezes
main CSC as of the start of Problem 3, including transaction-priced exact jobs.
The evidence directory is `Desktop/Codex/csc-ai-problem3-20261118`.

## What the candidate changes

- **3.1** A working buyer can benefit from several suppliers in its material
  class. Each physical plot contributes its best positive build or repair
  option. The best job for a currently missing class keeps the earlier
  readiness floor. Additional jobs use the native price of their own
  transaction gains. Specialty work needs a working fourth-stage buyer.
- **3.2** Supply jobs share the charged Builder inventory across the player's
  cities. Near units reserve one charge per supported job. The loaded build
  permissions cover compatible units such as the City Lights Farmer for a
  Pasture. The R2 Sawmill still needs a Builder. A bounded native route query
  checks nearby candidates when available. Advance up to four
  uncovered jobs as potential capacity requests and let the game consume one
  per player/publication. Existing Builder production covers the first extra
  unit without another sponsor. The job's value is added at the exact native
  Builder contract initializer after the stock tree attempts recruitment.
- **3.3** Quote the actual improvement return beginning after its estimated
  prerequisite path and work delay. One missing dependency gets the offer.
  Subtract the gain of a ready alternative on the same plot. For the first
  missing material of a class, take an immediately legal job if there is
  one. Already progressing topics receive no offer. A completed Quarter with a
  working customer and a queue-legal Stage 2 producer can justify its first
  supplier unlock before the producer is built. Its return starts after both
  the work and producer are complete. The native queue compares temporary
  analysis rows and validates the winning step.

CSC keeps the AI+ pattern that lets a native improvement request consider
other cities. The charge check applies the RHAI5 idea of comparing worker
supply with useful work, using CSC's exact jobs. As in Real Strategy's source,
the appetite for improvements and unit demand are separate inputs. [Source review](csc-ai-material-development-audit-20261118.md#what-the-other-ai-mods-contribute).

## Native boundaries

Ghidra inspected the Windows XP2 reference SHA `324c51e9` and REA verified the
installed November XP2 hotfix SHA `092abfbb`. The CE installer also checks
the function entries in the loaded module. The technology, civic and Builder
hooks install independently. REA byte evidence is
`ev_adeeb93d908e763511d404a8003b762da26451a46707d7a7d1d6b8d234dfba72`.

| Boundary | RVA | Input and outcome |
|---|---:|---|
| Research queue and comparison | `4fa9a0`, `4f60d0` | Goal `+0x00`, immediate step `+0x04`, full Q8 `+0x14`, owned `+0x18`, turns `+0x1c`. The comparator takes the excluded step by pointer. The winning original row still goes through `CanResearch`. |
| Culture queue and comparison | `418860`, `40de20` | Goal `+0x08`, owned `+0x0c`, full Q8 `+0x14`, turns `+0x18`, immediate step `+0x1c`. The comparator takes the excluded step by value. The queue checks `CanProgress` on the selected step. `CivicAnalysis::toString` at `41e8a0` corroborates the goal offset. |
| City-improvement recruitment and initializer | `55ba40`, `3f9300` | The direct unit initializer call at `55be97` receives extra present value as a whole utility argument. The initializer converts it to Q8 and writes contract `+0x158`. The separate unit request priority and required-city arguments are preserved. The subsequent `Update` at `3fa5e0` takes the maximum of this value and the city's ordinary quote. |
| Gameplay path read | `700ed0` | `UnitManager.GetMoveToPath(unit, plotIndex)` returns the array of numeric plot indices as its first result. Check the returned route includes the job before reserving that charge. |

## Score already carried into Builder production

The loaded `TreeData` gives the same **Present Value** tag to Decode
Trigger (node 1), Add Goal Tech (6) and both Build Unit nodes (13, 23) of
the ordinary Build City Improvement tree. DecodeTrigger (`55a680`) reads
the admitted improvement and plot through `PresentValueOf` (`3e8000`)
and adds its Q8 value shifted right eight bits to the tag. BuildFromCity
(`55ba40`) passes that whole-unit tag as argument seven of the unit
contract initializer. The 2,560- and 1,821-byte bodies match the
reference and installed XP2 forms. A guided per-plot score thus already
raises the Builder contract's initial present value.

The follow-up policy credits the triggering job once. Its separate
capacity offer includes any clipped positive transaction value. It can
also include half of the strongest other unstaffed job's marginal value
within three tiles and the same city's lands. This prices one potential
use of a second charge while allowing for native reassignment and travel.
At most four exact jobs compete to draw one sponsored request per player
and packet. If only one job is uncovered and its whole value reached the
improvement row, its native request already carries that contribution.
The next candidate freezes this Lua change with the verified 262-check CE
DLL `ca09d797`. The Flax replay retains the preceding diagnostic package
so it can measure the exact native handoff.

In the matched checkpoint replay, both arms reserve the Bakers Flax repair
on turn 108. Its Builder contract 1859 is submitted to the same five cities
at 154 utility with the 64-unit improvement ceiling and 166 with the
128-unit ceiling. No separate capacity offer was scoped to that repair at
turn 108. This demonstrates the existing improvement-value contribution at
the production boundary. A different ongoing Builder contract, 1756, can
finish locally before that request is selected.

Native comparison receipts report the values and goal changes. Ordinary
research and production logs establish what was queued. A work-history row
requires a physical map transition. Native readiness, proposal counts and
completed unit contracts have their own fields.

## Full-game measurements

`material_development_summary.py` reads the passive observer through its
verified turn-250 finish. New work requires a previously observed eligible
adjacent deposit and a change to a working compatible improvement. A repair
requires the same improvement to go from pillaged to working. Land ownership,
newly revealed deposits and first Quarter observations can affect endpoint
supply. Work is attributed only to observed state transitions on land held by
the original AI. Physical plots and events are deduplicated across overlapping
Quarter links, with a separate breakdown by family and material class.

Inspect the distinct number of worked plots and the T250 working/eligible
share together, because the games can place different numbers of Quarters.
Count improvements and repairs separately. Record mean and peak guidance time
from `ai-processing-time.json`. The CE receipt also times scored copies of
research comparisons separately.

## Frozen candidate

CE source preparation and test code are in
`project/tools/ai_workshop_bridge/ce_material_development`. The standalone
host verifies 261 score checks, four hook group checks and the instruction
call lifecycle. The candidate Release DLL SHA256 is
`24d1775438b6364821b71b0dde011f45366de29788f784c1609e031b8da2109f`.
The control used `9f774e61`; the local native build changes only the optional
material consumers and publication support. Both packages use the same mod
IDs. The treatment file manifest differs from the frozen control in exactly
five main CSC Lua files and the CE DLL. For a binary-identical follow-up,
the same candidate CE can be installed with the untouched control CSC files.

The loaded Fractal database maps Vanilla Cattle and Sheep to Animal Husbandry,
Bananas and Cotton to Irrigation, and Resourceful 2 Bamboo and Maple Sawmills
to Construction. The current stack has no corresponding civic-gated ordinary
material improvements. Construction itself implies Animal Husbandry and is
the Textile Workshop's unlock. Look for remaining natural research demand on
Irrigation and the Bakers' independent Engineering/Machinery paths before
planning a controlled research replay.

## Closed control

The shared controller reached and saved turn 250, verified preferences and
package cleanup, and recorded native exit 0. The five original AI opponents
produced the following physical results. Several plots had both new work and a
repair during the same game.

| Material class | New improvements | Repairs | Working / eligible at 250 |
|---|---:|---:|---:|
| Bakers Base | 10 | 2 | 11 / 15 |
| Bakers Specialty | 3 | 1 | 2 / 3 |
| Tailors Base | 2 | 0 | 4 / 5 |
| Tailors Specialty | 0 | 0 | 1 / 1 |
| All physical plots | 15 | 3 | 18 / 24 |

The 18 events cover 16 distinct plots. The publisher took 1.321 s average and
2.837 s peak across all 250 turns, with zero publication failures. The durable
control outputs are `control-material.json`, `control250/ai-processing-time.json`
and `control250/session-closed.json` under the evidence directory. The treatment
was launched after the control closed. Its map, AI roster, starting plots
and units match the control. The loaded GameCore and candidate CE hashes
match the package pins. Technology, civic and Builder-request capabilities
all report ready on turn 1.

## First matched treatment result

Both sustained runs completed through the verified Online turn-250
boundary, archived saves and restored the original preferences. The treatment
closed at 22:28 local with clean native exit. The matched analysis is
`comparison-03.json` in the evidence directory.

| Material class | New improvements, control → treatment | Distinct repaired plots | Distinct plots with either kind of work | Working / eligible at 250 |
|---|---:|---:|---:|---:|
| Bakers Base | 10 → 10 | 2 → 1 | 11 → 11 | 11/15 → 7/12 |
| Bakers Specialty | 3 → 3 | 1 → 1 | 3 → 3 | 2/3 → 3/3 |
| Tailors Base | 2 → 1 | 0 → 0 | 2 → 1 | 4/5 → 2/4 |
| Tailors Specialty | 0 → 0 | 0 → 0 | 0 → 0 | 1/1 → 0/1 |
| All physical plots | 15 → 14 | 3 → 2 | 16 → 15 | 18/24 → 12/20 |

The first treatment fell short of the required increase. Repair events
increased from three to five because Tenochtitlan's Wheat 925 was repaired
four times. The Farm was absent from turn 228 after another disruption.
Kish's Flax 2188 stayed pillaged from turn 91 through 250 in treatment.
Bakers gained and lost different links. For example, player 3 improved Flax
1502 by turn 151 in treatment and Bananas 1429 by turn 161 in control.
Player 4 built the same Pasture on Cattle 1320 at 207 in treatment and
233 in control. That accelerates an individual job without changing
the distinct plot total.
By the endpoint, four working control deposits in the common eligible
cohort had lost their improvements outright or were pillaged on turn 234
or later in treatment (Flax 544, Silver 620, Maize 860 and Rice 865).
Different Quarter foundations also changed the plot pool.

Among deposits next to a completed, intact Quarter with its relevant buyer
already working, the turn-250 census records 17/22 working in control and
10/16 in treatment. The buyer-ready treatment gaps are all Base. They are
Wheat 925, Cattle 1325, Bananas 1429 and Flax 544, 2112 and 2188. Wheat 925
serves two Bakers Quarters and counts as one plot. This cohort helps
prioritise follow-through cases while the all-deposit table remains the
full-game comparison.

Positive native improvement-score writes increased from 401 to 674, with
zero reported faults. The treatment logged 133 Builder offers, covering six
exact jobs, and zero matching initializer receipts. Kish's exact Flax 2112
received 38 of these offers. Its only observed reservation in treatment
came earlier from a turn-34 technology boost. The ordinary city job used
different plots during the CSC capacity offer window. No qualifying
improvement-research offers appeared in the normal treatment.

The whole CSC publisher averaged 1.321 s in control and 1.322 s in
treatment, with peaks of 2.837 s and 2.772 s. Both have 250 measured turns
and zero failed publications. Replay the particular stalled native choices
before using the corrected build for the next normal-start comparison.

## Improvement admission and the first capacity offer

The improvement forecast survives as a per-plot Q8 value. Ghidra shows that
`AnalyzeTerrain` (`3dec40`) scans the plot rows and caches one preferred
improvement type. `CheckForImprovement` (`3e1150`) opens an ordinary job only
when its work slot is free. It calls `GetBestLocationFor` (`3e5750`) for the
cached type. That scan skips active reservations. The plot overload of
`PresentValueOf` (`3e8000`) reads the chosen row's Q8 value directly and the
admission requires a positive result. A production offer at `BuildFromCity`
can help once this job exists and requests a worker.

REA verified these Windows XP2 code ranges byte for byte against the Ghidra
reference `324c51e9`. The installed `092abfbb` evidence is
`ev_1b7d49498585083339883d56b2ceb6b2d80b680b67e2db8dfe3227d1a1073a67`
for analysis, `ev_66bb5d7964660caa1bf752e23a07c186c26439095dd3d664cb372374136fc1ca`
for admission, `ev_ec0728c223807b2729d563b8d74779140cce30e492e6937b977ebfade9aef4c1`
for location, and `ev_19bf11996641b5a30d2508794f7ed8e58f45cdc30cb3f78eb94c2d90bc4ff029`
for the value read.

The first live Builder offer was on turn 104 for player 5, city 131073,
Flax 2112 beside Tailors Quarter 2038. Its working Farm disappeared on turn
87 in both arms. CSC valued the replacement at 16,775 Q8 (65.53 utility).
The native policy reported one staged offer and zero matching Builder
initializers on the next read. Kish's ordinary Farm job on 106 reserved
(42, 29), while the missing Tailors Farm is at (40, 28). The other plot is
Flax 2188 beside Bakers Quarter 2114. Its Farm was pillaged. Both jobs
have CSC value and share Kish's ordinary slot. In both arms the engine
repeatedly selected the Bakers repair, sought a Builder or started moving
one to the plot. The control eventually repaired it on turn 174. The
focused replay reads both suppliers to see which work moves forward.

The closed control's 25-turn censuses contain no owned and visible bare
supplier whose mapped improvements all have missing technologies and whose
Quarter has an operating buyer or working Stage 2 customer. This is a sample
of demand in that seed. A separate turn-100 replay can create a paired Bakers
case requiring Irrigation. The candidate packages and stock research queue
stay the same in both fixture arms. Only the exact research offer is omitted
from CE staging in the fixture control. The ordinary comparison excludes
all fixture grants and actions.

The research fixture tests location eligibility with a missing topic.
Ghidra shows that `ImprovementBuilder.CanHaveImprovement` (`1a2a0`) passes
the actual player to the map placement predicate (`25acf0`). An ordinary
registered resource can pass before the improvement definition's main
`PrereqTech`. Particular feature or terrain rows can have their own
researched prerequisites. The loaded Bananas/Plantation resource row has
no required feature and the Plantation definition names Irrigation.
The four inspected implementation spans at `1a2a0`, `25acf0`, `25a230`
and `25dc10` match byte for byte on the reference and installed binaries.

The Flax capacity value reached 24,314 Q8 on turn 110 and the request
transport ceiling of 32,768 Q8 on turn 122. The active treatment still has
a 16,384 Q8 ceiling in the preceding improvement-score transport. That can
discard economically justified value before a job is admitted. The staged
follow-up CE source advertises 32,768 Q8 for the exact improvement row.
The main publisher accepts the new range when advertised and keeps the
original floor bands. The running treatment retains its frozen 16,384 Q8
ceiling. Use the exact city and Flax case to see whether the added margin
can change an ordinary reservation and lead to work.

The capacity consumer also had an independent scope defect. The frozen
hook required the trigger marker at tree offset 0x330 to be one. The
archived Farm and Mine admissions both carry zero there with a valid explicit
improvement index and plot. Ghidra's DecodeTrigger (55a680) consumes the
explicit improvement before it ever reads that marker. The marker gates a
fallback that looks up a city improvement when the explicit index is absent.
The 2,560-byte DecodeTrigger span matches the installed hotfix and Ghidra
reference. The next candidate identifies the exact city, plot, and
improvement when an ordinary job asks for a Builder. It still validates the
initializer caller and requested unit. The native regression fixture holds
the ordinary marker at zero and verifies rejection of a different
improvement on the same plot.

In the closed control, Kish finally reserved the exact Flax on turns 208
and 210 at 146 utility. Both times the tree found a Builder and began a move
to the tile. The following turn shows the sequence failing, and the Farm did
not return by turn 250. The focused replay checks an earlier window in which
ordinary Farm slots repeatedly opened. A changed reservation, a Builder
request or recruitment, and the eventual Farm each have their own evidence.

## Paired Flax replay from turn 100

`flax-05/comparison.json` compares the 64- and 128-utility ceiling packages
from the same archived control checkpoint. Both use integrated CSC and
match the saved world's structure before playing. The read-only probe
observes both selected plots. Both closed cleanly on turn 135.

| Kish outcome | 64-unit ceiling | 128-unit ceiling |
|---|---:|---:|
| Builder request for Bakers Flax 2188, turn 108 | 154 utility | 166 utility |
| Bakers Flax Farm repaired | Turn 128 | Turn 128 |
| First Tailors Flax 2112 reservation | Turn 133 | Turn 129 |
| Tailors Flax Farm working at 135 | No | No |

On turn 129 the higher ceiling produces a 210-utility request for the
Tailors Farm. The tree finds a Builder on 131, and Protect Unit fails on
132 before another reservation on 133. Both arms publish the same seven
separate capacity offers in the measured window. At 129 there is no
separate exact offer. The baseline and candidate record zero matching
initializer receipts. Check whether the earlier Lua roster credits
charged Builders held by other AI controllers before tuning this consumer
further. Nearby path viability and native availability are separate facts.

Protect Unit reads the explicit worker list when present. Otherwise its
native call at `55897c` gets the units still assigned to the job's controller.
The lookup `401ba0` filters delayed death and requires a matching controller.
The Protect Unit update at `558870` returns raw state 3 for an empty list.
The separate witness replay will capture this list together with the exact
Find Available Unit pools, Builder IDs and charges, and the controller of
each Builder in the roster. The fixture advances the archived game through
the same decisions without adding work orders.

Both loaded Build Unit nodes in Build City Improvement allow any city and
leave Release Unit When Built disabled. The native wrapper already asks to
keep the Builder under the request's control. On XP2, UnitCreated
(`3f9fa0`) can complete a waiting request when the unit type and city
match. If it keeps control and the requested controller remains valid, it
copies that controller to the new unit. That branch does not compare an
existing controller or request value. The witness replay records consecutive
completions against the same Builder so a completion and the actual holder
can be tracked separately.

### Improvement value also reaches native worker recruitment

The behavior tree constructor at `53e4d0` names the request priority,
recruit priority and present value members. Decode Trigger copies the
improvement score into the tracked Present Value member, scalar
`+0x210`. Find Available Unit reads it at `554b10` and passes it
as whole utility units to RecruitUnits `403190`, separately from
request/recruit priority. The free unit pool uses the ordinary
worker evaluator. When it still needs units, RecruitUnits passes
both numeric fields and the requester controller into the managed
unit supply signal at `400930`. The worker witness records both
numbers and both pools to show whether the higher material job
value reaches the release decision for this exact job.

One receiver of that signal is `BehaviorTree::ReleaseUnits` at
`543830`. It can offer units it holds to a higher-priority
request, or to a higher-Present-Value request at equal priority
when the holder permits that competition. Other holder rules
still apply. The callback returns offered IDs, and the recruiting
tree must then select and take control of one. This is how a
material job's revised forecast can affect competition for existing
workers without changing the city production bid a second time.
The 593-byte release routine span matches reference `324c51e9`
and installed hotfix `092abfbb`, SHA256
`f53ff790855abc7b172d68de601e8dbe084d8466cf7e18f82c7a7693ff0a8fa8`.

### Kish's worker was reassigned to Umma

The independent replay `kish-worker-05-late` reopened the original
turn-100 save and reached 135 with normal closure. It used stock AI
and the earlier 128-unit policy. The passive worker trace was confined to
125–135 after the first diagnostic handed off cleanly at 108. It
recorded four recruitment attempts, eight protect decisions and 106
release checks with zero callback faults.

At 129 and 130, every Builder in the captured Babylonian roster
had already processed its turn. Builder 2293771, the worker that
repaired the Bakers Flax on 128, was close enough to appear in a
simple inventory estimate. Its current controller offered it during
Kish's recruitment but the native evaluator received no Builder in
either pool. The normal 210-utility Builder request was submitted
to six cities and stayed waiting.

On 131 the Tailors Farm job took controller 32899099 and recruited
Builder 2949125 at (49,32) with one charge. On 132 another priority-2
job offered 581 utility against the Farm's 210. The stock release
routine offered that same unit. The next Kish protection check saw
an empty list and recorded the Builder at (49,30) with the new
controller 34209813 and its charge intact. The native tree journal
identifies the successful 581-utility job as Umma's Mine at (51,28).
It completed on turn 134. The Tailors Farm remained bare at 135.

The next main-CSC candidate preserves the stronger native job and
retains a conditional Builder quote when its workforce estimate only
found a nearby charged unit. That quote pays the positive residual
above the already-carried job value. It excludes any premium for
additional jobs. CE consumes it only when the exact native job
actually takes the Build Unit fallback. True shortages retain the
original portfolio estimate and releases preserve native priority.
The staged packet labels the conditional offers so their native
receipts and realised work can be counted separately.

At the same-start candidate 08 turn-160 boundary, 38 of 92
published Builder offers were conditional. Two reached native
production for the Kish Bakers Flax repair. On 123 the quote
rose from 218 to 221 utility, and on 133 from 219 to 223. The
normal native request path submitted both. The actual Flax
was still pillaged. The candidate had worked 14 distinct plots,
level with candidate 06 at the same boundary and ahead of the
control's 13. The endpoint determines whether the altered timing
adds completed material work.

Shadow went down during candidate 08 after its verified turn-185
boundary. The source logs and normal turn-188 autosave are retained.
The shared controller restored the original preferences and reopened
the verified normal turn-150 save as `treatment08-recovery150`.
All 176 retained original structural rows matched. The comparison
uses the preserved history through 150 and the resumed history
after that checkpoint. The observed turn-185 branch remains separate.
At turn 185, both the interrupted candidate and control had
worked 14 distinct plots. Candidate 08 had made five repairs across
two plots, compared with two repairs on two plots in control. It had
seven native Builder receipts, four conditional, all at submission
or later cancellation in the retained segment.

### Candidate 08 recovered endpoint

The resumed branch reached 250 and closed with settings restored. Civ
declined the manual save before any request was sent. The controller
archived its exact turn-250 autosave and verified the final observation.
The comparison joins original turns 1–150 with the resumed branch.

| Material role | New plots, control → 08 | Repair events | Distinct repaired plots | Working at 250 |
| --- | ---: | ---: | ---: | ---: |
| Bakers Base | 10 → 15 | 2 → 4 | 2 → 2 | 11/15 → 11/16 |
| Bakers Specialty | 3 → 3 | 1 → 0 | 1 → 0 | 2/3 → 2/3 |
| Tailors Base | 2 → 2 | 0 → 1 | 0 → 1 | 4/5 → 4/6 |
| Tailors Specialty | 0 → 0 | 0 → 1 | 0 → 1 | 1/1 → 2/2 |
| All physical plots | 15 → 20 | 3 → 6 | 3 → 4 | 18/24 → 19/27 |

Distinct worked plots increased from 16 to 23. Every control plot
that received work also received work in the recovered trajectory.
The seven additional plots include five Bakers Base suppliers and
one in each Tailors class. Publisher timing is 1.321 seconds mean
and 2.837 peak for control, versus 1.242 and 2.559 for candidate 08.
Both had 250 measured turns.

On resumed turn 195, Umma recruited a Builder and repaired Wheat
1975 after earlier sponsored requests had reached its queue. On
216 its native job built the Farm on Wheat 2047 after an earlier
conditional quote for that plot. The receipt logs show submissions
and cancellations for those requests. This distinguishes the later
physical work from training on a specific bid. The improvement
timeline also diverged after the load. The fresh candidate 09
run provides a comparison from an uninterrupted start if it can
finish on the original session. Evidence is `comparison-08-recovered.json`.

On turn 243, both Farms disappeared from the same Bakers Quarter's
working supplier set. Wheat plots 1975 and 2047 retained their owner
and resource, with no district or pillaged improvement recorded. Both
were still bare at 250 despite new contingency offers. The retained
logs do not identify the cause. This is a supply recovery case distinct
from protecting the deposits themselves. A follow-up should measure
turns from losing the last working supplier to the first productive
replacement and distinguish that from a repair to a pillaged Farm.

### Value the Service that the job would restore

A further main-CSC change feeds the existing gameplay-derived Service
ledger into an exact material quote. The Quarter, producer, customer and
Service unlock must already qualify. One improved resource must close the
remaining material deficit on its own. Working supplies and any other
required material are read from the live snapshot. The effect starts
after the existing work allowance or the prerequisite delay.

The same native price paths handle growth, yields and pseudo-yields.
Housing uses the actual receiving city's headroom and current Food. Its
existing benefits stay in that baseline. The ordinary material quote
survives a missing optional Service price. The Lua adapter carries the
Service subtotal separately so a supplemental Builder charge for another
job adds only ordinary gains. This prevents counting the same restored
Service twice across competing jobs.

The 169 economy and 20 front-end checks pass. Candidate 09 freezes
this change with the same CE binary. Its fresh matched run is
queued after candidate 08 closes. Candidate 08 tests the earlier
worker, queue and prerequisite changes using ordinary material
transaction pricing.

Candidate 09 verified the original opening and completed its
turn-125 checkpoint with nine distinct worked plots, matching
control. Both had eight new improvements, one repair, and
12/20 working suppliers. It issued seven positive Service
quotes. The first, for Kish's Tailors Flax on turn 107, added
6,250 Q8 to the ordinary 17,954 Q8. The result was a 24,204 Q8
plot-score offer. The published quote and any subsequent native
decision are tracked separately.

#### A shared Wheat Farm restored two Storekeepers

On turn 193, Wheat 925 was pillaged and both adjacent Aztec Bakers
Quarters lost their last working Base supplier. Both Storekeeper
growth modifiers became inactive. On turn 195, the material quote
carried 13,088 Q8 in ordinary transactions and 35,864 Q8 in Service
value before the plot score cap. The native Builder request rose from
219 to 282 utility. Its contract 4061 was purchased and completed on
turn 203. The reopened job quoted 257 versus 219 utility on 204.
Its next contract, 4369, also completed via purchase on 207. The
Tenochtitlan job found a Builder on 207, failed Protect Unit on 208,
then succeeded on 209. The unit log records a repair operation by
Builder 12189724 and the material guard records the Farm working again
on 209. Both growth modifiers were active at the turn-210 check. The
purchase rows identify the two exact contracts and omit the unit IDs.

### Candidate 09 fresh endpoint

Candidate 09 and the tuned control both completed the same normal-start
Online 250 setup. Their endpoint saves, passive observations, and clean
closures are verified in `comparison-09.json`.

| Material role | Distinct worked | New | Repair events | Distinct repaired | Working at 250 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Bakers Base | 11 → 13 | 10 → 12 | 2 → 4 | 2 → 1 | 11/15 → 10/14 |
| Bakers Specialty | 3 → 3 | 3 → 3 | 1 → 0 | 1 → 0 | 2/3 → 3/3 |
| Tailors Base | 2 → 1 | 2 → 1 | 0 → 0 | 0 → 0 | 4/5 → 4/5 |
| Tailors Specialty | 0 → 0 | 0 → 0 | 0 → 0 | 0 → 0 | 1/1 → 1/1 |
| All physical plots | 16 → 17 | 15 → 16 | 3 → 4 | 3 → 1 | 18/24 → 18/23 |

Publisher mean/peak was 1.162/2.605 seconds versus 1.321/2.837 in
control, over 250 turns each with zero failed publications. Candidate 09
published 72 positive Service samples and 216 Builder offers. Seven
native Builder receipts included the two purchases for the Aztec Farm.
The normal game had no material prerequisite offers. The net gain was
one additional worked plot and zero additional working suppliers at 250.

Kish illustrates the delay even after a buyer is operating. Its Textile
Workshop completed on 103. The adjacent owned Flax 2112 offered a legal
job by 107 and remained bare at 250. At the endpoint, 6 of 21 eligible
Base supplier links attached to working buyers were idle in candidate 09,
versus 5 of 22 in control. The link count allows a shared physical plot
to appear under more than one Quarter. It is a snapshot of eligible
owned deposits, without claiming every plot has a legal job that turn.

The next policy reads the current production item and remaining turns
for the exact mapped buyer. It quotes Base work during Stage 2 construction
and Specialty work during Stage 4 construction. The material income starts
when both jobs are due. A committed buyer within five turns can qualify for
the existing first-supplier floor. The code declines a stale, missing, or
undated commitment and reads the queue again on the next publication.
Each player gets one sampled commitment offer per turn for follow-through
analysis. Game 09 used the preceding policy.

### Candidate 10 active buyer test

The same normal-start Fractal ran uninterrupted through Online turn 250
with four changed CSC Lua files and unchanged XP2 and CE binaries. The
controller closed and restored the game setup. The endpoint is the native
turn-250 autosave, preserved when the UI declined the manual save before
any save command. The passive census verified all ten milestones and no
observer faults or drops. See `comparison-10.json`.

| Material role | Distinct worked, control / 09 / 10 | New in 10 | Repairs in 10 | Working at 250, control / 09 / 10 |
| --- | ---: | ---: | ---: | ---: |
| Bakers Base | 11 / 13 / 14 | 13 | 5 | 11/15 / 10/14 / 8/15 |
| Bakers Specialty | 3 / 3 / 3 | 3 | 0 | 2/3 / 3/3 / 2/2 |
| Tailors Base | 2 / 1 / 4 | 2 | 2 | 4/5 / 4/5 / 4/4 |
| Tailors Specialty | 0 / 0 / 0 | 0 | 0 | 1/1 / 1/1 / 1/1 |
| Physical plots | 16 / 17 / 21 | 18 | 7 across five plots | 18/24 / 18/23 / 15/22 |

Candidate 10 published in 1.308 seconds mean and 3.514 seconds peak
over 250 turns, compared with 1.321 and 2.837 seconds in control. Both
had zero failed publications. At Umma both working Wheat Farms (1975 and
2047) disappeared on 236 while Wheat and ownership remained. Both were
still bare at 250. Several other Bakers suppliers were pillaged late.
This left fewer working suppliers even after more work across the game.

The active-buyer diagnostics contain 19 quotes for eight exact Base
jobs. Seven saw later physical work, 10–136 turns after the first sampled
quote (median 23). The sampled jobs did not deliver material before the
buyer finished; the candidate did not sample a Specialty commitment.

| Site | First active-buyer quote | Work in 10 | Work in 09 | Work in control |
| --- | ---: | ---: | ---: | ---: |
| Kish, Bakers Flax 2188 | 61 | 75 | 75 | 75 |
| Kish, Tailors Flax 2112 | 103 | 239 | Open at 250 | Open at 250 |
| Hamilton, Tailors Sheep 626 | 108 | 118 | 118 | 118 |
| Umma, Bakers Wheat 1975 | 112 | 125 | 125 | 125 |
| Montreal, Bakers Bananas 1429 | 133 | 227 | Open at 250 | 161 |
| Baghdad, Bakers Cattle 1320 | 168 | 191 | 182 | 233 |
| Olympia, Bakers Wheat 2037 | 189 | 222 | Open at 250 | Open at 250 |
| Cairo, Bakers Cattle 1325 | 209 | Open at 250 | 241 | Open at 250 |

The Kish Water Mill quote lifted the native Farm score from 20,596 to
35,960 Q8 while the Mill was still in production. Kish's ordinary tree
kept reserving its Ziggurat site, worked on that job through 70, reserved
the Farm on 71 and completed it on 75. These dates match both references.

The capacity adapter published 205 offers for nine exact jobs, including
135 conditional offers that required native recruitment to fail. Native
initialization used seven offers. The readbacks account for 196 offers
without initialization and two endpoint offers without another readback.
All seven native receipts were individually identified.

| Turn | Exact job | Contract | Native utility | Observed disposition |
| ---: | --- | ---: | ---: | --- |
| 123 | Kish Bakers Flax repair | 2249 | 218 → 221 | Submitted, cancellation recorded on 125 |
| 133 | Kish Bakers Flax repair | 2478 | 219 → 223 | Submitted |
| 143 | Kish Bakers Flax repair | 2720 | 219 → 291 | Submitted while Oxford occupied Kish's queue |
| 153 | Kish Bakers Flax repair | 2974 | 188 → 222 | Submitted |
| 163 | Kish Bakers Flax repair | 3239 | 250 → 325 | Submitted, recruitment failed through 172 |
| 165 | Umma Wheat Farm | 3274 | 258 → 262 | Submitted, fresh job recruited a worker and built on 211 |
| 227 | Kish Tailors Flax Farm | 5336 | 241 → 244 | Submitted, cancellation on 232, later recruitment and Farm on 239 |

None of the seven sponsored contracts recorded a purchase or production
selection. The remaining Kish Bakers Flax repair stayed undone. Kish
opened a separate City Lights Power Station job at 8,121 utility on 173.
Umma selected its Builder on 174 and completed its contract on 175. The
Power Station was finished on 179. This exposes the competing work rather
than inferring that every unselected sponsored contract had a head-to-head
comparison with it. Candidate 09's two exact gold purchases remain the
verified sponsored acquisitions. In 10 the two later-built sponsored plots
were observed under fresh native jobs, with no acquired unit attributed
to their earlier contracts.

### Kish's repeated offers were sequential

The same Flax repair waited on four successive Builder requests in Candidate
10. Each used its own waiting window before the behavior tree released the
job and opened another request. Submission rows list each participating city
under the same contract ID.

| Contract | Submitted | Eighth wait turn | First missing |
| --- | ---: | ---: | ---: |
| 2478 | 133 | 141 | 142 |
| 2720 | 143 | 151 | 152 |
| 2974 | 153 | 161 | 162 |
| 3239 | 163 | 171 | 172 |

The native `BuildFromCityNode::Execute` at `55ba40` reads its stored contract
ID and returns when `BehaviorTree::GetContract` at `5401d0` resolves it. A
newly accepted request goes through `ManageContract` at `5431a0`. The same
Build Unit node therefore already retains one live request across turns and
multiple eligible producing cities. Keep the native lifetime for sponsored
requests and test concurrent nodes separately when shared jobs are involved.
The verified PE comparison found identical `.text` and `.pdata` on the
Ghidra XP2 reference `324c51e9` and live Windows hotfix `092abfbb`.
Evidence is `treatment10-250/AI_Behavior_Trees.csv`, `AI_CityBuild.csv`, and
`csc-gamecore-hotfix-20261106/pe-audit.json` under `Desktop/Codex`.

### Kish dispatch and Umma recovery prerequisite

The turn-150 Kish replay uses the saved Candidate 10 world and both frozen
packages. It applies a diagnostic 72-utility margin at the ordinary
improvement admission boundary, and tests a 48-utility finishing preference
only for a charged worker already on the exact job tile. The latter leaves
native request priority, release overrides, and the worker selection intact.
Neither hook enters the shipped CSC policy. The comparison uses plot scores,
worker controller evidence, physical work and unchanged package hashes.

The first paired replay opened its city work slot on 153, 163 and 173.
Both arms' stock selector chose the Flax Farm on 153 and 163, at 48,129 and
64,101 Q8. On 173 it chose the City Lights Power Station at 2,536,828 Q8.
The Farm was still pillaged at 175. Both probes saw 25 admission checks and
no eligible on-site release comparison. The early admission probe had passed
the row's first field to `GetBestLocationFor` as if it selected a plot. The
boost caller confirms that argument filters a resource definition. The probe
now tests the adjusted exact row via the stock selector and checks the
returned coordinates. The initial control's unmodified stock results and
worker logs remain valid references for the corrected replay.

The corrected run matched the passive source and finished at 175. The
three vacancy decisions stayed the same. On 173, Flax had 60,423 Q8
against the Power Station's 2,536,828. In both arms the Flax tree made
20 unsuccessful worker searches across the two admissions. The Builder
requests reached submission at 222 and 254 utility in the replay. The
Farm remained pillaged. There was no on-site release candidate, and the
bounded preference made no edits to these comparisons.

Static comparison used Windows XP2 Ghidra reference `324c51e9` and hotfix
`092abfbb`. The corresponding byte spans matched across 384 bytes at
`3e1150`, 512 at `3e5750`, 593 at `543830`, and 864 at `3dec40`.
Offline admission and release checks verify restoration of temporary
fields, the exact selected coordinates and unmodified higher-priority or
override release requests.

At Umma, archived monitoring also shows district 1974 pillaged on the same
turn both Farms vanished. The Mill is pillaged at the endpoint. CSC had
waited for already-working Base material to support the Quarter repair, and
waited for a working Quarter before planning supplier jobs. The new policy
can offer the native prerequisite repair if the producer is already on the
Quarter, an adjacent customer operates, and at least one legally usable
Base deposit is available. It leaves the Farm work to ordinary decisions
after buyer recovery. Offline suites passed 170 economy and 20 front-end
checks. The preserved turn-241 autosave loaded with player 0 still AI,
so the shared controller declined to play it. The matched diagnostic uses
the verified manual turn-200 save with the same scoped Farm removal,
Quarter damage, and Mill damage applied once in each arm. One of the two
Wheat deposits was already bare at that checkpoint. No later decisions
are forced.

Both Umma arms matched the turn-200 source census, verified identical
starting damage, and ran to turn 215. The old rule published zero repair
candidates. The new rule published one exact candidate from 201. CE
considered it repeatedly and reported zero supplemental admissions. The
CE repair hook considers supplementation only after the stock district
slot opens and the same call creates a new stock district tree. Umma
worked on its existing City Lights district through 213. On 214 both
arms submitted the ordinary repair for Bakers plot 1974 as contract 4899
at 7,812 utility. CE counted one duplicate in the following readback.
At 215 both arms still had the damaged Quarter and Mill and two bare
Wheat deposits. The Lua change clears the circular eligibility rule.
The native admission schedule still governed when the repair entered
competition. There was no live worker-retention qualification in either
case. Artifacts are in `dispatch-kish150-corrected` and `dispatch-umma200`.

### Kish searched after its Builders had acted

The passive turn-150 to 175 replay retained both native recruitment pools
for the two Flax plots. The stock Builder filter observed 23 recruitment
calls, all for the pillaged Bakers Farm. Eleven calls on turns 150 through
160 had no stock Builder in the roster. For the 12 calls on 161 through 172,
every stock Builder had charges and had already processed its turn. Across
33 calls to the native selection evaluator, some vectors contained other
unit types and none contained a stock Builder. The Farm was still pillaged
at 175 and its Water Mill remained operational throughout the replay.

Nippur's contract 3102 completed on 161 and handed its new three-charge
Builder 4128777 to the 856-utility Environmentalism boost job. Kish's
188-utility repair waited. On 164, the native release handler offered the
nearby three-charge Builder 4390912. The release allowed the transfer and
the stock processed-unit
filter discarded it before selection. That Builder later performed a
repair elsewhere on 168. The two examples give distinct cases for capacity,
stronger competing work and a late recruitment search.

The paired follow-up changed update order for an already reserved repair
in the same native priority pass. It looks for a local, charged, unprocessed
stock Builder and a lower-valued, competing improvement update. Movement,
recruitment, unit release, protection, production and repair still use
their stock paths. It advanced Kish on 172 ahead of Nippur's 83-utility
ordinary improvement, with Builder 4390912 two hexes away, unprocessed
and holding two charges at the start of the priority pass. Isin's
183-utility Ziggurat at (46, 27) had already recruited and moved that
Builder by the time the advanced Kish update ran. Isin offered the Builder to Kish's
250-utility request, and the processed filter removed it again. Neither
arm repaired the Farm through 175. This shifts the next test to the start
of that priority pass, where the same lower-valued holder can release a
still-available worker. The instruments run only in matched replays.

The passive evidence is under `kish150-worker-pools` with the matched source
census, `worker-native-evidence.json`, queue, behavior and operation logs.
The controller lost the preference command's acknowledgment after 175.
Readback on the same held process confirmed the original settings had
already been restored. The controller then closed it normally, archived
the packages and verified the original checkpoint hash.
The first treatment matched the same opening census and closed normally.
Its native `early-dispatch` record and matched comparison are archived in
`kish150-early-recruitment`.

### Kish recruited at the start of the priority pass

The next same-start treatment put the reserved Flax repair at the start
of its ordinary priority-2 pass on turn 172. Nippur's 83-utility job
released Builder 4390912 with two charges. Native recruitment selected it
for Kish's 250-utility repair and transferred its controller. Native
protection succeeded and the tree ordered movement toward (42, 29).
Isin's 183-utility Ziggurat then made three unsuccessful searches on
172–174. In control it secured the same Builder on 172 and started moving
toward (46, 27).

On 173, Nippur's 3,452-utility Power Station acquired the Builder through
stock same-priority release. The subsequent Kish protection check read
zero units. The Farm stayed pillaged in both arms through 175. The native
sequence demonstrates earlier recruitment and a real trade-off between
jobs. The next arm tests a single finishing opportunity if the Builder is already
on the Farm with charges and can work through native protection. Preserve
ordinary competition if reaching the Farm would still take travel.
Source parity, comparison and closed-session proof are in
`kish150-first-recruitment`.

### Kish completed the repair before the next reassignment

The matched finishing arm retained the same save, packages and opening census.
On 172 Kish recruited Builder 4390912 as in the earlier recruitment arm.
At the start of the priority-2 pass on 173, the two-charge worker was still
assigned to the Flax job and was standing on plot 2188. The probe gave that
tree one earlier update. Native protection succeeded and the game ran
`UNITOPERATION_REPAIR` on the Farm at (42, 29). The Water Mill buyer kept
operating. At 175 the Farm was working in treatment and still pillaged in
the passive control.

Isin's Ziggurat recruited Builder 4390912 on 174, two turns after its
assignment in the passive control. Nippur's Power Station recruited that
Builder on 173 in the recruitment-only arm. Its searches failed on 173 and
174 in both the passive and finishing arms. This isolates the work that the
extra finishing opportunity displaced and the work delayed compared with
ordinary play. The matched evidence is in `kish150-finish-recruitment`,
including `comparison.json`, `AI_Behavior_Trees.csv`, `UnitOperations.log`
and the closed-session record. This is a diagnostic probe of a native tree
handoff. The packaged CSC and CE policy must reproduce it from live offers.

The manager at `5639b0` traverses the tree list at `+0x388`, combines
the Boolean results of `BehaviorTree::Update` at `544360`, then runs
the separate destroy pass until stable. The two entry ranges in the
Win64 exception table are byte-identical in the Ghidra reference
`324c51e9` and live hotfix `092abfbb`. The 154-byte manager range
has SHA256 `455a61fd42227ea501585271497e37eb09d06e60b65d8d8aaa70c633032d5016`.
The 106-byte tree-update entry range has
`da35d8298e2ef2c1082b8b5c244199ce7225d7a24fff27b7e5eaf77dc36a2441`.
The direct call returns to `5639ea`. CE uses that return address to
restrict the argument swap to the manager traversal.

### The integrated policy restored Kish's Flax

The controller replay `kish150-packaged-worker-r1` uses the same saved world
and current integrated CSC Lua in both arms. Treatment replaces only the
CE DLL, using the isolated Windows Release build with SHA256
`44f95f01a746ec76aae6eb6f42815653eba2804a774c2ca74aa7eeb8e780aed5`.
CSC published Builder 4390912 for Farm 2188 on turn 165 and again on 166.
The native receipts record an earlier recruitment update on 165 and an
earlier finishing update on 166 for the same live controller. The engine
recruited the Builder on 165 and issued its repair operation on 166.
The Water Mill stayed operational. The Farm was working at the 170 and
175 boundaries. The control still had pillaged Flax at 175.

The same Builder had moved to Umma's Farm at (51, 26) and repaired it on
168 in the control. In treatment the Umma job still recruited on 165 and
completed on 170. Its next Farm at (49, 27) was built on 171 instead of
169. These are the physical opportunity costs of making Kish's supplier
available sooner in this matched world.

### Finishing-only replay from the same Kish assignment

After the Fractal result, CSC disabled worker scheduling by default.
An explicit replay opt-in offers an exact repair when an operating Base
or Specialty buyer has a single known viable supplier, the improvement
is pillaged and a charged stock Builder is already on the tile. The
separate CE finishing offer verifies native custody, the site and the
ordinary improvement tree. It advances that assignment once in its own
priority pass. Regular bid pricing and extra-capacity requests continue
to use their existing paths.

The shared controller used the historical broad replay build to prepare
one verified manual save at the inactive turn-166 boundary. Starting
both arms from that same save held the prior recruitment and travel fixed.
The two replays matched 203 structural census rows. Both had Builder
4390912 on the pillaged Flax Farm beside an operating Water Mill. Both
loaded the same finishing-only CE binary
`040af7d83c11448ebd2061053b82878a14b208046546256d02701c6966c68720`.
The replay's opt-in assignment was the only CSC file difference.

The default replay published zero finishing offers and the Flax remained
pillaged at 170. The opt-in logged one native finishing receipt on turn
166. The same Builder issued `UNITOPERATION_REPAIR` that turn, and the
Farm was working at the next boundary through 170. Its next Farm at
Olympia (37, 25) completed on 169 instead of 168. These results isolate a
completion benefit and the competing work it delayed in this fixture.
Both sessions closed with verified settings restoration. See
`kish166-finish-preparation` and `kish166-finish-only-r1/comparison.json`.

### Fractal dispatch comparison at verified snapshots

The treatment reached Online turn 250 on Fractal map seed 28111119 and game
seed 38111119. The starting world, Firaxis GameCore, optional content and CSC
files matched the baseline. Only the CE runtime DLL differed. Both arms used
the existing CSC scoring and Builder-request guidance.

The control resumed from its verified turn-150 save and later stopped
after a display failure. Its turn-200 save and turn-240 inactive boundary
were both verified. Measurements use the turn-start supplier census in
each arm, with the control's original history joined to its resumed
observations at turn 150. The later, unfinished control turns are excluded.

| Metric | T200 baseline | T200 treatment | T240 baseline | T240 treatment |
| --- | ---: | ---: | ---: | ---: |
| All buyers supplied within 15 turns | 16/17 | 15/18 | 18/20 | 17/20 |
| Base buyers supplied within 15 turns | 14/15 | 13/15 | 14/15 | 14/16 |
| Specialty buyers supplied within 15 turns | 2/2 | 2/3 | 4/5 | 3/4 |
| Working supplier plots | 20 | 19 | 20 | 19 |
| New improvement events | 22 | 24 | 25 | 27 |
| Repair events | 7 | 8 | 8 | 10 |
| Supplier outages restored | 1/1 | 2/3 | 1/2 | 2/5 |

By 240 the treatment had published 117 worker offers. The native consumer
gave jobs 11 earlier recruitment opportunities and six earlier finishing
opportunities, with no worker faults reported. On turn 208, the scheduler
matched Builder 10354689 to plot 2116. The native operation log records that
Builder's repair that turn, and Qaraqorum's behavior tree reports a completed
Farm repair at (44, 28).

The control's one completed outage lasted 63 turns. The treatment's two
completed outages lasted seven and eleven turns on different Quarter sites.
The Bakers outage at plot 1728 began on turn 105 in both arms. It recovered on
168 in the control and the buyer became unavailable on 182 in treatment
with the outage still unresolved. Each run recorded the same verified Base
work during buyer construction and zero Specialty construction cases.

At turn 250, the treatment alone had supplied 19 of 22 eligible buyers
within 15 turns. It saved and exited cleanly. The first Fractal result
demonstrates ordinary dispatch activity and additional material work.
The common boundaries show a lower on-time supply rate and one fewer
working supplier plot. The cutoff turns, source log hashes and per-buyer
data are in `comparison-fractal-28111119-verified-snapshots.json` under
`csc-ai-problem3-20261118`.

### Quebec's Specialty bid before the Café opened

The shared controller loaded the same turn-150 save in both arms and
verified the same opening census. At 159, it confirmed the Café was in
active production and pillaged the existing Berries Plantation at 622.
This was the only fixture change. The control omitted the exact unfinished
Café quote on each publication through 162. Treatment published three
committed-buyer offers at 16,796 Q8 on 160–162 as the remaining estimated
construction fell from three turns to one. The Café was operating at 163.

Native Quebec improvement work in the treatment chose an Ice Hockey Rink
during that construction window. The decoded request values were 420 on
160 and 655 on 161–162. Both arms first reserved Berries on 164, submitted
the same 318-utility Builder request after a failed search, then recruited
a Builder and began moving it on 165. Both Plantations were still pillaged
at 166. This establishes the construction quote and the competition it
faced. Physical Specialty work during Stage 4 construction still needs a
successful case. See `quebec150-cafe-specialty-ui-r2` for the matched
comparison, native logs and clean exits.

### Aachen built a Specialty supplier before the Café opened

The earlier Continents treatment is a positive example of ordinary
follow-through during construction. Aachen (player 3, city 393220) owned
Bakers plot 2532 and adjacent Honey 2606. The city selected its Café on
192 and had invested 99.5 of 125 Production on 195. It reserved the
Honey tile at (16, 35) on 193. Its native improvement tree completed a
Camp there on 195, and the material observer recorded a new working
Bakers Specialty supplier that same turn. The Café's construction
contract completed on 196.

This archived case precedes the current Builder scheduler. It shows the
physical sequence is possible with stock AI and a live production queue.
The current fresh-game observer will date work against the exact buyer
queue in both arms. Source is
`csc-ai-customer-scheduling-20261117/final-comparisons/continents-treatment250`,
using `City_BuildQueue.csv`, `AI_CityBuild.csv`, `AI_Behavior_Trees.csv`
and the material state event in `Lua.log`.

### Builder purchase and production use different ranking inputs

`Economic::ReceiveContract` (`458ac0`) first validates the request for the
economic path. `Economic::DoTurnActivate` (`457120`) compacts the pending
handles, stably sorts them and calls the purchase executor for requests that
pass its readiness gate. The insertion-sort comparator at `454f10` compares
the contract priority at `+0xc8` in descending order. The unit initializer
at `3f9300` derives that field from the native request priority and the
player's priority for the unit type. The separately supplied whole-unit
offer is shifted to Q8 for the production value at `+0x158`. The existing
CSC Builder supplement changes this production input. It does not move
the request up the economic priority order. This also explains why an
exact production receipt and a later purchase are different evidence.

The purchase executor uses a required city if the native request names one.
Otherwise `TryPurchaseUnit` (`459320`) iterates the player's city list and
checks its budget, unit cost and purchase command. A successful purchase
advances the original shared contract. A targeted improvement can therefore
get a completed request without the purchased Builder starting close by.
This is static control-flow evidence for the matching Windows XP2 reference
`324c51e9` and installed hotfix `092abfbb`. The two earlier Aztec Farm
purchases give live evidence that the same native requests can reach that
path. A purchase-specific change should be measured on a retained valid
request and preserve the native budget and alternative purchases.

### Native job selection can ask for a specific compatible worker type

`CheckPlotNode::Update` (`55e160`) reads the improvement's allowed unit
definition list and chooses the lowest current unit cost among types that
pass `CanTrain` in at least one city. The stock Build City Improvement
tree carries that option as `Builder Type` to Find Available Unit and its
unit-request fallback. `FindUnitsEvaluator::ChooseUnitsFrom` (`553570`)
filters by exact selected type before ranking. A generally compatible
worker can therefore exist while a particular job is asking for another
type. The stock Builder appeared in every Kish search in this replay.
City Lights allows its Farmer to build Farms, Pastures and Plantations.
Treat this as a compatibility opportunity for the wider campaign and
capture actual eligible worker types separately before deciding where to
broaden the policy.

## Paired Irrigation replay from turn 100

The archived player 4 has a single city and its Bakers Quarter is already
under construction. Both verification arms add the same isolated fixture
city, Bakers Quarter 947, operating Wind Mill and adjacent bare Bananas 1020.
Irrigation remains missing. The loaded Plantation row is a registered input
for the Wind Mill and the plot passes the ordinary native location check.
In control only, the exact Irrigation offer is omitted from CE staging.

The Lua policy quotes the same four offers in both arms. The treatment's
turn-104 offer reaches one native technology row at the actual comparison.
It adds 5,994 Q8 (23.41 utility) to 565,571 Q8. Stock goal, adjusted goal
and immediate step are all Irrigation. Both arms start research on turn
104 and own the technology on turn 105. The plantation remains unbuilt at
turn 108. The native comparison is verified independently from a change in
research selection. Both sessions close cleanly, with a matching fixture
opening and the original save preserved. The evidence is
`research-06/comparison.json`; the fixture results are separate from the
ordinary game's material-work counts.

The loaded campaign database explains why the research branch was
rare. The read-only audit joined the declared producer/material
transactions, registered input hosts, valid resource improvements
and actual resource tags. The only ordinary improvement unlocks
in those rows are Animal Husbandry, Mining, Irrigation and
Construction. Every covered class also has compatible improvement
types without an unlock. All improvement prerequisites in this
mod stack are technologies. The Tailors Textile Workshop itself
requires Construction. The Mills require Engineering or Machinery,
and the two Specialty buyers require Humanism. In a normal game,
the material unlock is therefore often already owned by the time
there is a producer that can use it.

## Normal-start follow-up

The shared controller verified the original seed, roster, starting map,
opening units and unchanged GameCore on the fresh game. The package uses
the corrected CE hash `ca09d7972946a4dc5a04eba9fd1992118165f8ad864bf159e5ebb89a0b076ff1`
and the latest main-CSC capacity logic. The game started at approximately
23:05 Warsaw time on 18 November. It uses the same stock AI, normal
Online rules and optional mods through turn 250. `treatment06-250` holds
controller and native logs. After verified closure, the runner will
write `comparison-06.json`. The offline comparison also traces observed
ordinary work-tree steps on plots with capacity offers in either arm.
It reads the archived log and needs no added in-game probe.

At the verified turn-120 checkpoint, all three arms had seven new
improvements, one repair and 11 of 23 eligible plots working. The
revised candidate had one separate Builder offer through that point,
compared with seven in the first candidate. Neither recorded a matching
initializer by that boundary. The turn-250 measurements remain the
qualification result.

The revised normal game later recorded two native initializer matches
for Kish's Bakers Farm repair on Flax 2188. On turn 143 an exact offer
raised contract 2721 from 219 to 291 utility, and the game submitted that
value in six cities. On 153 the offer raised contract 2971 from 188 to
220 utility and reached seven cities. Both were checked through turn
160. The receipts establish ordinary cross-city production submission
for the correct job. The repair was still waiting for a worker.

The next main-CSC change treats an in-progress Builder as capacity for
one compatible job within six tiles on the same land area. A visible
queue due in more than five turns leaves the job's offer eligible. Without
a usable terrain-area read, queue credit stays in the training city. This
replaces blocking all capacity offers whenever any city is training a
Builder. The six-tile radius matches the active-worker shortlist and the
five-turn allowance matches the material return estimate. The running
turn-250 follow-up retains its frozen policy.

Through the verified turn-190 boundary, both treatments had 13 new
improvements, five repair events across two plots, 14 distinct worked
plots and 16/23 working. Control had 13 new improvements, two repair
events across two plots, 14 distinct worked plots and 18/24 working.
The revised treatment had four native production receipts. Two new
requests for Wheat 1975 on turns 175 and 185 both rose from 369 to
439 utility. All four records had native production submissions, with
no selection observed through the boundary. Both exact jobs still
needed repair.

The 439-utility Wheat repair request was still waiting when Adab
selected an ordinary Builder request at 15,412 on turn 187 for
Uruk's City Lights Power Station at (40,23). The Power Station
request completed on 194, and the assigned Builder constructed
it on 196. The Wheat request recorded seven of eight waiting
turns on 192. This gives one concrete competing use of Builder
production and a unit that became available after the repair's
request window. The normal material jobs should continue to bid
their own economic return.

The second normal-start treatment stopped advancing on turn
242, during the finite 240–245 autoplay operation. The last
verified inactive boundary was 240. Both treatments had worked
15 distinct material plots, as had the control. The control
had 14 new improvements and three repairs across three plots.
Each treatment had 14 new improvements and five repairs
across two plots. Working supply was 17/25 in control and 14/21
in both treatments. The four exact production offers had
submission receipts. The two targeted plots were still
unrepaired at the verified count.

The controller's existing progress discovery stopped finding a
responsive Tuner state. The identified game process was present
and its CPU use stayed flat in a two-second host sample. The
retained T242 autosave is separate from the qualification count.
The archive `stalled-242-evidence` contains hashes of the captured
logs and autosaves. The restart plan uses the hashed normal
turn-200 save and the 243-row structural census extracted from
the original log. If the recovery is required, report its
post-reload branch explicitly alongside the original T240 count.

The owned test process was stopped after the shared controller's
ten-minute discovery timeout. Its exact preferences and test
packages were restored through a clean menu-only session. The
continuation in `treatment06-recovery200` reopened the original
T200 archive with the same GameCore, CE, CSC, optional mods and
Online settings. The source comparison matched all 219 retained
structural rows. It uses the same passive material observations
without a treasury capture or worker probe inside the game.

The resumed branch reached verified turn 250 and closed normally.
The explicit endpoint save was unavailable before any save
request was sent. The native turn-250 autosave was preserved
and hashed. The final material observations, city census and
publisher timing passed the offline finish checks.

### Recovered turn-250 comparison

The comparison counts work through the original turn-200 save
and then through turn 250 in the resumed branch. The intermediate
branch through turn 242 remains separate. Endpoint supplier
counts come from the resumed observation. This preserves the
matched opening and accounts for the reload.

| Material role | New plots, control → treatment | Repair events | Distinct repaired plots | Working at 250 |
| --- | ---: | ---: | ---: | ---: |
| Bakers Base | 10 → 10 | 2 → 5 | 2 → 2 | 11/15 → 10/13 |
| Bakers Specialty | 3 → 3 | 1 → 1 | 1 → 1 | 2/3 → 3/3 |
| Tailors Base | 2 → 1 | 0 → 0 | 0 → 0 | 4/5 → 4/5 |
| Tailors Specialty | 0 → 0 | 0 → 0 | 0 → 0 | 1/1 → 1/1 |
| All physical plots | 15 → 14 | 3 → 6 | 3 → 3 | 18/24 → 18/22 |

Distinct worked plots total 16 in control and 15 in treatment.
Publisher time averaged 1.321 seconds in the control and
1.208 seconds in treatment, with maxima of 2.837 and 3.617 seconds,
respectively, across 250 sampled turns each. There were zero failed
publications in the completed treatment timeline.

The resumed Babylonian Kish job eventually recruited a Builder
and repaired Bakers Flax 2188 on turn 248, after a fresh reservation
at 188 utility. The two earlier sponsored requests for the same
plot were submitted on 143 and 153. Each disappeared before this
later job and the resumed segment recorded zero Builder sponsorship
receipts. The physical repair is a native follow-through case after
the reload. The campaign's distinct worked plot count remains
below control. Evidence is in `comparison-06-recovered.json`
and the original and continued native logs.

The completed normal timeline had no eligible material prerequisite
offer. The paired Irrigation fixture provides the research-consumer
evidence for this package. The next main-CSC candidate also prices a
positive locked improvement for an existing buyer when another deposit
already has a ready job. Independent suppliers can both pay. The quote
still deducts a viable same-plot alternative, and a pending producer
keeps the first-supplier rule. The economy suite verifies simultaneous
ready work and a discounted locked offer for separate plots.

### Native Builder purchases

The ordinary unit request also has an economic execution path. Its
economic executor at `3f8850` passes the requested unit and any required
city to `Economic::TryPurchaseUnit` at `459320`. The helper obtains native
purchase prices, applies its budget and legality checks, and can complete
the same unit request via a gold purchase. The purchase call carries no
production valuation argument. An increased production quote proves
that the production path saw a higher value. The choice of which
requests reach economic execution remains a separate trace.

The same purchase helper also has a distinct caller at `3e27e8`.
`CityBuild::DoTurn` tries the type returned by `GetBestUnitToBuild`
for that city, then recomputes after a purchase. This is a city
unit candidate rather than the exact material request itself.

Ghidra reference `324c51e9` and installed Windows Steam XP2
`092abfbb` match over 658 bytes of the executor and 873 bytes of the
purchase helper. The helper span SHA256 is
`a147729fb1f2caba09663cf96c25bad77894957ee4c1d7e5f55a079823982627`.

### A repair spends movement and preserves charges

`Unit::Operations::Repair::CanStart` at `671c40` requires charge
count at least one and movement. Its executor at `672030` clears
the pillaged bit and calls `FinishMoves`. By comparison,
`XP2::BuildImprovement::Start` at `7490c0` calls
`ChangeBuildCharges(-1)`. The next CSC capacity estimate gives a
charged worker credit for one repair without reserving away its
build charge. Extra repairs still use capacity within the planning
window. This is a planning allowance. The native worker maintains
its legal movement and action timing.

### Homeland opportunistic resource jobs

The distinct Homeland resource routine `4bd130` can give a
charged worker a move and build request for a bare luxury or
strategic resource. Its plot callback `4ba9e0` scans within ten
tiles and prefers the nearest eligible owned deposit beyond
three tiles from its city. The resource-class predicates are
`7d8690` and `7d8750`. At the site it uses
`GetBestValidImprovement` (`665950`), which first consults the
city's choice and can fall back to the first legal buildable
type. This provides another way a spare worker can build an
outlying deposit. The route's bare-plot and class checks make
the ordinary city job tree the relevant target for pillaged
resources and most Bakers or Tailors suppliers.
