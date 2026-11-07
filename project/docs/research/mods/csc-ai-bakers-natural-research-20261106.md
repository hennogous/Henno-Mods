# Timing a Bakers bid against natural civic research

Problem **1.6** tests whether a later district bid can survive native
preparation and reach construction. In the earlier isolated Delhi replay, the
AI reserved the intended tile, but its Craftsmanship request reached eight of
eight waiting turns and the district plan failed. The new world starts in the
Ancient Era with Craftsmanship locked. No civic, research boost, district or
building is granted. [Earlier bid and expiry](csc-ai-hotfix-live-bid-20261106.md).

## Read-only Online pilot

The shared controller hosted Small Continents at Prince and Online speed,
with the isolated CSC rules package and patched stock Gathering Storm. It used
the fixed Mill study leaders and seeds, with no diagnostic world setup or
instrumented writes. It recorded the original major AIs at turn 1 and each turn
from 5 through 25. Craftsmanship was locked for all five at turn 1.

| Original AI player | First observed researching Craftsmanship | First observed unlocked |
| --- | ---: | ---: |
| 1 | 8 | 14 |
| 2 | 8 | 12 |
| 3 | 9 | 15 |
| 4 | 7 | 11 |
| 5 | 9 | 19 |

The gameplay console exposed civic selection and unlock state. The initial
probe got no usable values there from the UI methods `GetCulturalProgress`
and `GetTurnsToProgressCivic`. The pilot stopped at turn 25 with zero writes,
no saved candidate, and verified restoration. These turn numbers describe the
natural world created for this pilot.

## What the game measures

On the fingerprinted Gathering Storm binary, `GetTurnsToProgressCivic` in
the UI cache binding at RVA `6ad720` forwards to the cached culture object's
indexed `GetTurnsLeft` at `0b3410`. The gameplay binding
`GetTurnsLeftOnCurrentCivic` at `6f0f40` forwards to the live player culture
method at `280770`. That method reads the active civic, calculates the current
culture yield, then passes both to `GetTurnsLeft` at `2806c0`. The latter uses
the civic cost and accumulated progress with the player's carried culture.
This result estimates turns at the current yield. Actual completion can
change with yield, boosts, or a different research selection.

`CultureAi::EstimatedTimeToResearch` at `414b20` reads a separate AI planning
row for the requested civic. It may add time remaining on the active civic
when the active civic matches neither of the planning row's two civic fields.
This is a distinct decision input. A short current-civic ETA establishes a
timing opportunity while the district tree's acceptance and persistence still
need their own runtime evidence.

The Ghidra reference is XP2 SHA `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
The loaded stock hotfix is SHA `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`,
with the same code section. [Binary comparison](csc-ai-xp2-november-hotfix-20261106.md).

## Qualified turn-8 checkpoint

The second scout confirmed the UI cache returns numerical research data for
the original AI players. A Lua city iterator error stopped the run when the
first AI began Craftsmanship. The controller restored preferences and exited
normally. The corrected scout used the gameplay getter for turns remaining
and a same-turn UI query for accumulated progress.

On turn 8, player 4 had completed Code of Laws, was researching
Craftsmanship, and still had it locked. Both getters estimated four turns
remaining. The UI reported 7.6875 Culture accumulated toward that civic.
The two surveyed sites in city 65536 had spare district capacity. Both were
owned, revealed, legal by the plot query, adjacent to the City Center, and
adjacent to an owned mapped Bakers Base deposit. Plot 2420 had no feature
and Base plot 2421. Plot 2568 had a feature and Base plot 2642. This verifies
the scout geometry and timing. Native candidate scoring, the Granary's
presence, and material improvement readiness are separate checks.

The shared controller saved one exact inactive turn-8 boundary. The saved
world hash is `95a26a1976400ef0d8232fc3a0d2b857f0cbc277b6e07ff2f66195f7df1310bc`.
It is the single input for the control and diagnostic-bid arms.

## A fresh score while London's district plan was busy

The turn-8 control reloaded the exact save, matched the scout's source facts
and observed one turn. The Bakers cell at plot 2568 had a fresh score of
11,930 Q8 before and after aggregation. Plot 2420 was reserved. London made
no `GetBestDistrict` call in the observed window, so the run made zero writes
and did not open a treatment arm.

The native tree log separates the competing commitments. London's
improvement tree reserved plot 2420 at (52, 32). Its outstanding Holy Site
tree reserved plot 2421 at (53, 32), which was the mapped Base deposit next
to the first Bakers site. Holy Site preparation was still waiting on
Astrology under contract 34. Meanwhile the production log recorded Great
Bath at 11 of 90 Production. The Base reservation establishes a risk to the
proposed supply chain. This control did not observe the deposit being lost.

`CheckForDistrict` at RVA `3e0ee0` requires the city's outstanding district
tree ID to equal −1 before it calls `GetBestDistrict`. It also requires a
configured district tree. London's active Holy Site tree explains why the
fresh Bakers score had no selection opportunity. The queue's Great Bath is
a separate commitment. The next read-only pass searches for the first
qualified selection window in the same naturally advancing world. It can
admit a city whose Craftsmanship has unlocked through normal research.

## Boston's first observed selection window

The wider search resumed the untouched turn-8 save. It observed each
eligible decision window without writing and saved its input at the inactive
turn boundary. The first qualifying fresh choice was Boston, player 3 city
131073, on turn 22. Player 3 had unlocked Craftsmanship on turn 15 through
ordinary research. Boston had population 1, no district slot in use, and
an owned, empty site at plot 721 next to its City Center and Base plot 796.

The shared controller opened the turn-22 save as a fresh control. Boston's
district planning slot was free. Bakers at plot 721 scored 28,795 Q8 on
entry and after aggregation. Campus at plot 944 won at 39,269 Q8, matching
the discovery observation. This was a district selection. The city continued
producing other items.

By turn 37 the control had an unpillaged Granary at plot 795 and an
unpillaged improvement on Base plot 796. Boston had submitted a Bakers
construction contract on turn 34 and selected it for production on turn 36.
The first foundation observation on turn 37 was plot 648. Our candidate at
plot 721 remained empty. These are distinct sites and distinct moments in the
decision sequence.

## The one-time Boston bid reached construction

The treatment reopened the same verified turn-22 save. The original value
and city facts matched. A single write after native aggregation put Bakers
256 Q8 above the control's Campus score. The native selector returned
Bakers at the new value. The observer froze after that turn.

| Turn-22 district decision | Control | One bid |
| --- | ---: | ---: |
| Bakers plot 721, native aggregate | 28,795 Q8 | 28,795 Q8 |
| Diagnostic adjustment | 0 | +10,730 Q8 |
| Native selector | Campus at 944 | Bakers at 721 |
| Winning score | 39,269 Q8 | 39,525 Q8 |

Boston reserved (55, 9) and submitted Bakers construction contract 225
on turn 22. The city chose the contract for production on turn 26. The
first physical foundation observation was turn 27, at plot 721. The native
queue reached the production cost and marked contract 225 complete on turn
30. The exact district was complete at the next physical sample on turn 33.
Boston still owned Base plot 796, which retained the same unimproved deposit.
The Granary and Mills were absent at that boundary. The controller saved
this completed Quarter for the next decision.

The native production system handled each step after the single score change.
Craftsmanship was already available through normal research. This experiment
establishes follow-through in that ready state. The amount is a diagnostic
signal measured against the control winner.

## Boston lost the tracked Base before its Mill was available

The read-only continuation reopened the completed turn-33 Quarter. Boston
was on a hill with one river edge and the river-access flag. Water Mill
required Engineering and Wind Mill required Machinery. Both were locked.
Player 3 began Engineering naturally by turn 36.

The new Quarter remained complete, but at turn 36 plot 796 held a Campus
and its previously observed Base deposit was gone. The original treatment
log already records Boston choosing Campus, reserving (56, 10), and
submitting contract 318 on turn 31. The continuation selected that same
contract for production on turn 33. A new placement bid from the completed
turn-33 save would arrive after the site commitment. Boston's improvement
tree also had a reservation on the deposit. The Campus won despite that
reservation.

The observation follows the exact supplier nominated at turn 22. A fresh
census of all six neighboring plots is required to establish whether it
was still the Quarter's last viable Base at the destructive decision.
The next matched test repeats the accepted Bakers bid, saves before the
turn-31 district choice, and measures a new competing site before applying
any supplier-protection adjustment. Both arms will use that saved boundary.

`GetBestDistrict` at RVA `3e4a50` uses the native default −9,999 utility
as the initial minimum and as the reservation value when no live reserve
task resolves. A candidate score must exceed the reservation value and meet
or exceed the best value so far. This allows some negative scores to win.
The first protection test will use a finite deduction measured against a
viable alternative and verify the resulting decision and supplier separately.

## A matched deduction protected the only Base

The controller replayed the original one-write Bakers treatment and saved
the inactive turn-31 boundary. A fresh census of all six neighbors found
exactly one owned compatible Base deposit. It was Cattle on plot 796, with
Pasture legal under the player's existing technology. The other resource
observed was Sheep on plot 648, outside this Bakers Base mapping.

The two arms loaded the same turn-31 save. Campus at plot 796 entered
aggregation at 106,071 Q8 and finished at 108,726 Q8, with the same existing
plot-reservation ID in both arms. The control again chose that Campus and
covered the Cattle by turn 34. An eligible owned, unreserved alternative in
the native score table at decision time was Campus at plot 648, at 100,198 Q8.
The treatment deducted 8,784 Q8 from the destructive pair. Its score became
99,942 Q8. Native selection instead chose Campus at plot 720, at 107,337 Q8.
The selector could consider other rows beyond those used for calibration.

Boston selected the relocated Campus for production on turn 33 and completed
it on turn 37. The independent Pasture job moved a Builder to plot 796 and
applied the improvement on turn 33. The first physical sample with the working
Pasture was turn 34. That same Pasture and Cattle were intact at every later
sample through turn 45. The protected save retains the completed Quarter,
working Pasture, Granary and Water Mill.

Engineering was reported owned on turn 38. Boston submitted Granary contract
361 on turn 36, queued it on turn 37 and completed it on turn 39. It submitted
Water Mill contract 416 on turn 40 and chose it for production on turn 41.
The Water Mill was physically present at the correct Quarter on turn 44.
Research, Builder allocation and both buildings proceeded through native
decisions after the protection write. Feudalism and Storekeeper had yet to
activate at the turn-45 boundary.

The experiment establishes one successful finite deduction and observed
retention through turn 45. It does not qualify a general hard exclusion or
a permanent protection guarantee across future district choices.

## The ordinary exchange worked, then a Feudalism boost consumed the Base

The read-only continuation reopened the exact protected turn-45 save. The
Granary produced 2 Food against its loaded base of 1. The Water Mill on the
Quarter produced 1 Production and 1 Gold. The matching Cattle Pasture and
ordinary exchange were observed together at turns 45, 48 and 51. Feudalism
and the Storekeeper marker were absent. At turn 54 the ordinary building
yields remained, although the Cattle and Pasture were both gone. This
separates the ordinary exchange from the material gate for Storekeeper.

The cause was a Builder job, independent of the earlier district auction.
`Seek Civic Boost CIVIC_FEUDALISM` reserved (56, 10) for a Farm and sent
Builder 1376266 to the site. Its unit-operation log records
`REMOVE_IMPROVEMENT` on turn 52 and `HARVEST_RESOURCE` on turn 53. The tree
logs the same unit clearing the exact plot. The turn-54 census found no
resource, improvement or district on the tile. A Farm completion is not
established by these receipts.

`ClearPlotNode::Execute` at `55d970` first requests removal if an improvement
is present. On the later clear attempt its harvest branch requests the
resource removal. The earlier [player-wide harvest test](csc-ai-native-harvest-rule75-20261024.md)
showed why rejecting only the final operation can leave a reserved job
repeating. The next test targets admission of the destructive Farm candidate
before either operation can begin.

## Guarding the boost decision before reservation

The empire-wide improvement branch of `DecodeTriggerNode::Update` reads an
improvement value through `PresentValueOf` at `3e8000` and then calls
`GetBestLocationFor` at `3e5750` for each city. Both use the city's improvement
row scores at `+0x30`. The call at `55ae96` returns a plot pointer. The caller
skips a city when that result is null. Shipped `Build City Improvement`
executes Decode Trigger before Reserve Plot and Clear Plot.

The diagnostic guard watches only that call site for player 3's Farm. It
withholds a returned location only when it is plot 796. The original score,
other cities' candidates and later research stay in the engine's control.
This suppresses the city's unsafe top candidate at that call. It does not
calculate its second-best Farm site.

In the first guard attempt, Boston returned the Cattle at 27,094 Q8 while
Washington returned plot 1168 at 15,698 Q8. The guard withheld the Cattle.
The Feudalism tree reserved Washington's plot at (58, 15) on turn 46. A Python
variable naming error stopped the follow-through read at turn 48. The run
closed normally and the corrected attempt reopened the same turn-45 save.

The boost-only replay kept the Pasture through turn 54. A separate ordinary
Boston Farm job reserved the same plot on turn 53 and removed the Pasture on
turn 55. The Cattle remained. Feudalism was owned by turn 63, but the
improvement gap prevented Storekeeper. By turn 75 Boston had replaced the
Pasture and the Water Mill was pillaged, another distinct interruption.

`CheckForImprovement` at `3e1150` calls the same location selector at
`3e11a0` for the city's ordinary job. It requires a non-null location and
a positive plot-specific value before creating the improvement tree.
The next matched replay extends the exact plot guard to this second caller.

## Retained Stage 2 chain verified at turns 63 and 66

The final replay loaded the same protected turn-45 save and matched all
initial facts to the loss control. The guard covered both verified callers.
It withheld the unsafe Farm result once in boost planning and six times in
ordinary city planning. It changed no cached score or reservation. The same
Cattle Pasture worked at every sampled boundary from turn 45 through 66.

| Exact Boston readback | Turn 63 | Turn 66 |
| --- | ---: | ---: |
| Working Cattle Pasture on plot 796 | Yes | Yes |
| Functioning Water Mill in Bakers at 721 | Yes | Yes |
| Granary Food at 795, base 1 | 2 | 2 |
| Water Mill Production and Gold | 1 each | 1 each |
| Feudalism unlocked naturally | Yes | Yes |
| Storekeeper marker and Growth property | Present, 1 | Present, 1 |

Feudalism was still in progress at turn 60. By turn 63 the Storekeeper
marker and Growth property were active. This qualifies one retained chain
through two exact samples three turns apart. The Growth property is an
activation receipt. The actual percentage change in aggregate city growth
was outside this measurement.

The controller saved turn 66, froze the hook with no pending callbacks and
closed the game normally. This milestone uses three separately qualified,
scoped interventions on one world. It leaves generic material protection,
same-city Farm fallback, routine bid calibration and Workshop delivery open.

## The chain stayed active for 141 turns before damage

`retention-01` resumed the exact turn-66 save with the same scoped Farm guard.
The read-only observer checked the original Cattle Pasture, Bakers Quarter,
Water Mill, Granary and Storekeeper at every recorded player-turn end. The
controller also read building yields at inactive boundaries eight turns apart.
Boston's turn checks passed from turn 66 through 206. The first failed check
was the Pasture at the end of player 0's turn 207. The controller finished
that batch and saved turn 210. Cattle still occupied plot 796 with no
improvement, the Water Mill was pillaged, and Storekeeper's Growth property
was zero despite its marker still being present. The Granary was intact.

The captured weather log recorded a Crippling Blizzard centered at (55, 8)
on turn 207. The Quarter at (55, 9) and Pasture at (56, 10) were nearby.
`Expansion2_RandomEvents.xml` defines a 19-hex footprint and separate
improvement destruction and building pillage effects for this storm.
Ghidra on the `.text`-identical reference XP2 confirms that
`Climate::Manager::ApplyStormEffects` at RVA `1b9b10` evaluates the configured
damage on each plot returned by `GetStormPlots`. `RandomEvents::DealEventDamage`
at `23ce00` dispatches to the improvement and building handlers. The
destruction handler at `23d300` can clear an improvement without clearing its
resource. This makes the blizzard the leading explanation. The first run has
no per-plot damage attribution, and the later player-2 pillage request on
turn 207 follows the first observed Pasture failure.

The run checked 2,335 player-turn ends and recorded one Farm veto, applied in
the turn-66 batch. The final save and normal closure verified. The evidence
root is `retention-01`. SHA-256 for `retention/210.json` is
`f0504567ae6ff4623533420ec8305ce5fdc02df7d8b9001645f08bab5514ad19` and for
`Game_RandomEvents.csv` is
`994fdd7392b147d583abd215c0543a715df12e0b300c880e970fc09b18970c7f`.

`retention-02` reloaded the exact working turn-186 save and matched the prior
gameplay and UI readbacks. The same weather pattern and first failed Pasture
check recurred at turn 207. The exact-plot improvement removal event arrived
on turn 209, two turns after the first failure. The replay had no Farm vetoes
and no score writes. It ended at turn 210 with a verified save and restored
setup. The resumed run's `retention/210.json` SHA-256 is
`c19fd0f4e2b652cd8a1e749b1efee6cbe457f7a46816f8c12830df45c75a287d`.

## The same chain passed 152 turns in a separate continuation

`cohort-02` reloaded the exact healthy turn-90 save to look for other AI
Bakers chains. It independently qualified the same Boston chain for the
entire run from turn 90 through the turn-242 save. The chain kept its Bakers
Quarter and Water Mill on plot 721, Granary on plot 795, and working Cattle
Pasture on plot 796. Storekeeper remained active. All 2,388 recorded
player-turn ends agreed on the exact chain identity, and Boston's own turn
end was present once per elapsed turn. The independent UI readings at the
20 inactive boundaries showed 2 Granary Food against a database base of 1,
and 1 Water Mill Food. A gap, a changed physical participant or a failed
yield boundary would have restarted the streak.

The two continuations diverged. The turn-207 weather log for `cohort-02`
records a River Severn flood at (54, 27). The earlier Boston blizzard did
not recur. This run kept the same rules and had zero Farm vetoes. The cohort
observer only read state. The result establishes that the chain can last at
least 150 turns in normal play after establishment. The earlier replay
shows that damage can still break it. These runs leave post-disaster repair
and the reason for divergence between the two playbacks open.

The run closed normally and restored preferences and the temporary package.
The audit command is `python -B project/tools/native_ai/late_placement/survey_retention.py <closed-run>`.
The starting save SHA-256 is
`369f670a1ab0ad5a0ef004636f7feb7a6934b075242e12bb1caee4855f617728`.
The ending `cohort.Civ6Save` SHA-256 is
`17f4fa324387e99e4a662ba9d6a1f244916a5caf3700b1b6b7c530a3984c930f`.
SHA-256 values for `cohort-result.json` and `cohort/242.json` are
`28b0c04f65db1e45e3ca9cbcb7c459ed1f1bd7958cfb7641b69f361c2e36580b` and
`ab9db34b34d96f08293faef93374e6280d165c3cbcee3bd704bcb380334ba33a`.

## Automatic district protection replay

The matched CE replay uses the exact turn-31 Boston save and the same
hotfix-compatible DX11 CE score build in both arms. The treatment loads the
main CSC gameplay publisher. The replay supplies only original seat roles
because this save predates the publisher. Neither arm issues research,
production, placement or unit orders.

In `ce-supplier-policy-01`, Boston covered the Cattle with Campus by turn 37.
The harness captured its log baseline before Civ reset the logs during load
and stopped before running the treatment. In `ce-supplier-policy-02`, the
control repeated the loss and archived the logs. The treatment stopped during
startup because the gameplay context lacked a game-mode getter supplied by
the offline fixture. Both sessions exited normally and restored preferences
and the test package.

The publisher now reads the UI's single-player check through the existing
CSC read-only bridge. It waits for the UI to confirm the mode before it
captures roles or publishes any scores. The revised offline test covers
missing UI and hotseat as well as ordinary single-player publication.

In `ce-supplier-policy-03`, the revised publisher committed 20 district
penalties across five original AI players at turn 31. CE reported nine
applied changes before the turn-32 refresh and zero faults at turn 37. The
control built Campus on Cattle plot 796. In the treatment, Boston built
Campus on plot 720 and the Cattle on 796 had a working Pasture. CE reported
51 changes across the treatment's refreshes. Both arms closed and restored
the original preferences and verified temporary package manifests. The earlier
diagnostic applied one measured late write. This replay used the main mod's
automatic early publisher throughout the interval. The finite penalty
still needs calibration across more situations and normal starts.

The matched result is `ce-supplier-policy-03/result.json`, SHA-256
`307330e8b77590b5a89deac461922c14067010758fbf5d0a0d18ca12b2ceb407`.
The treatment Lua log SHA-256 is
`1a8576fc7cfac7287c5a098d0ad9c1d2fabaeff845f05392b11dd32a1dc7e547`.

The CE development build couples diagnostic and policy limits. Filling the
16,384-record journal or reaching 4,096 successful score writes faults the
policy. Multiple calls on one entry count as multiple writes. Committing a
new publication clears the journal and the CSC publisher currently logs
the preceding matched and changed counts. This is sufficient for a small
replay. For long runs, give diagnostic retention and policy application
independent limits, preserve useful evidence across generations, and replace
the frequent full-table scans with indexed lookups and city-local ranges.
Measure these paths in a mature empire before setting production budgets.

## Builder candidate filtering before native ranking

The previous Farm guard withheld the selector's final result. To keep any
eligible same-city alternative in contention, the next stock GameCore probe
filters the protected row inside `CityBuild::GetBestLocationFor` at RVA
`3e5750`. The selector reads the requested improvement's signed score into
ECX at RVA `3e5845` and compares it with the admission floor at `3e5848`.
The following `JLE` skips the row if the score does not clear that floor.
The selector's optional third argument filters by resource type, as shown
by its `NoSpecificResource` caller at RVA `3d7610` and the same row field
used to count unimproved resources. It cannot express a plot exclusion.

The probe checks the loaded instruction bytes, exact native caller and
player, Farm ID, coordinates and cached score. It gives the protected row's
comparison the signed minimum and leaves the cached score, other rows and
native selection logic intact. It records the location the original
selector returns, including an empty result when it defers.

`operation-candidate-filter-01` resumed the original turn-45 control save.
The first boost pass returned no Boston site after filtering the Farm on
Cattle 796 with score 27,094 Q8. Later ordinary calls returned Boston plot
794 with score zero after filtering the Cattle at 4,054 to 6,109 Q8. Those
returns establish that a lower-ranked row remained eligible. The native
logs separately show Boston reserving plot 719 and issuing a Builder
improvement operation on turn 58. Plot 719 already scored above the
filtered row in that pass, so the operation alone does not establish a
switch caused by the filter.

The probe filtered 11 candidate evaluations with no hook fault. The original
Cattle Pasture, Water Mill and Granary remained intact, and Storekeeper
operated at turns 63 and 66. The game closed normally and the setup was
restored. The trace SHA-256 is
`fc57bd019268394f4c050eb385da8e20656727617000a0b8d9c9984d466e4494`.
This is a scoped Frida diagnostic on stock GameCore. Generalizing the
admission policy, handling already reserved jobs and delivering it through
CE remain separate work.

## Native technology decision boundary

Engineering became active in the ordinary continuation. Ghidra identifies
`Research::QueueNextTech` at RVA `4fa9a0` as a route that selects the AI's
next actual technology. It compares `TechTreeAnalysis` rows and checks
`CanResearch` for the immediate step before calling `SetResearchingTech`.
The winning row keeps the research goal and the immediately researchable
step separately. A named Engineering goal can therefore yield a prerequisite
as the next researched technology.

`TechResearchContract::Execute` at `3f82e0` calls
`Research::IncreasePriority` at `4f9810`. That method adds to the selected
row's `+0x14` value when the existing value and row flag admit the change.
It has no immediate research setter call. `GetBestTechsToResearch` at
`4f95b0` has direct callers in the Grand Strategic cache's fill and update
paths. For a future research bid, trace the actual queue decision as well as
any score or contract result. This pass made no research changes.

## Evidence locator

The evidence root is `Desktop/Codex/csc-bakers-natural-20261106`. The first
pilot is `scout-01`. Its `scans/` contain the per-turn records, and
`source-version/` retains the exact executed Lua and Python. Pilot
`scout-result.json` SHA-256 is
`a4b8424ccc55c2478554bc32c5b4246d2c7a52eea9628461f2be39c5eaecdb27`.
The failed candidate scan is `scout-02`. The qualified source is `scout-03`,
whose `scans/08.json` SHA-256 is
`0089de5f3be73a5a530c69139e079265c21786395e854aa54feea781c5250049`.
The first control is `matched-01/control`. It closed normally and restored
preferences and the temporary package. The SHA-256 of `trace-frozen.json`
is `7db19defd41e4961ccaeb59d974e4e1e8321547b9432ddbfdfce997821a82375`.
The London tree records are `AI_Behavior_Trees.csv` lines 836–870 and
923–927. The Great Bath production row is `City_BuildQueue.csv` line 5.
The broader search and replay are under `matched-02`. The decision save is
`discovery/windows/22/source.Civ6Save` with SHA-256
`9675be27c614a2429a9cdca485a09a8d7421e627cc7833cb472bb9b1c390f55a`.
The control and treatment closed normally with verified preferences and
package restoration. The treatment's `trace-frozen.json` SHA-256 is
`1fac636f4e18ebaaefe51813488b1d44093bc14b4b2314cb13eeb562aed3200c`.
Its `completed.Civ6Save` SHA-256 is
`df1f756b027184d5deeb30040710f16985bac9547412300bc99a9529d21fdd79`.
The read-only supplier-loss observation is `stage2-01`. Its `result.json`
SHA-256 is `ea6e003b1589120e73f01873b7ee235c5ae23a4c5e99a401b373d9a707b448ec`.
The earlier Campus commitment appears in `matched-02/treatment/AI_Behavior_Trees.csv`
lines 20801–20826 and `AI_CityBuild.csv` line 142. The follow-on queue selection
appears in `stage2-01/AI_CityBuild.csv` line 4.
The pre-decision save is `pre-supplier-01/treatment/pre-supplier.Civ6Save`
with SHA-256 `e3d6cb7bbffab1285dcd5aebf17b23e028aeeb1d97de7116c7cbc655e43317b0`.
The two protection arms are under `supplier-01`. The treatment's frozen
trace SHA-256 is `af6ba6df721eb1ab5f5547e6538b059ef1ebc40ecf7a34fe6681aad773332945`.
The protected turn-45 save SHA-256 is
`8f745349d384f1c91069009c59efe898a9189c3fcab20eaaa0d4257e5c46f233`.
The exchange and Builder-loss continuation is `operation-01`. Its
`states.json` SHA-256 is `79ba98eb3d1e5289f0a52504c2a2d5fa522ff0512eb0696c3c932a39c5600ad9`.
Its preserved `UnitOperations.log` SHA-256 is
`e741fcb1b7cc8b8dbb5117cbbbf4f1be1a8ce3cc6ed6e37b2a89768c598d0389`.
The final accepted continuation is `operation-04`. Its checkpoint is
`stage2.Civ6Save` with SHA-256
`56afbac023e9029f4d6fcaa5f270da07bc163bd724c6b511954de173b6630932`.
Its `states.json` and `farm-trace-frozen.json` SHA-256 values are
`c0f55046bc894033ebe3575f8101eefdc6cbc40fc67262210bc8ffa6bd7c8550` and
`bc2526e4fd1e4e787a5e5d588c404c19563c5b21848cac1c90ef32ee5ed881e7`.
