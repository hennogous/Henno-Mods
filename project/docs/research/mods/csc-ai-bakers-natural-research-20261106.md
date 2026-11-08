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

### CE score producer and execution limits

The city row evaluator at RVA `3e2aa0` calls the improvement overload of
`ValueManager::NetValue` at `52a8c0` from `3e3423`. On return, it reads the
integer pointed to by RAX and copies it unchanged into the improvement's
slot in the row array at offset `0x30`. The Win64 entry takes output,
improvement ID, discount pointer and delay in registers, then horizon,
plot and city on the stack. The row writer supplies these identities
directly. The district hook's assembly boundary is unnecessary here.
The installed GameCore and Ghidra reference match at the function entry,
the caller's store, and the native floor. The three REA byte reads are
retained in `Desktop/Codex/csc-gamecore-hotfix-20261106/builder-net-value-rea.json`
with SHA-256 `2f9b4655c074e853d55b48f230cc9a9dede18317b111e5a3882e25d53525e615`.

The CE review build calls the original and uses the native score floor
at `b66cb0` for an otherwise admissible incompatible improvement on a
published supplier site. That value feeds all readers of the improvement
cache. CE checks the GameCore identity, entry prefix, caller and numeric
keys before changing the output. CSC publishes the compatible improvements
from the current material rules and narrows the allowance to the existing
improvement while it is working. A fresh calculation is required for a
new policy or its removal to change an existing cached value.

An assigned job has another route to the map. `ClearPlotNode::Execute`
at `55d970` can request RemoveImprovement and then HarvestResource before
`BuildImprovementNode::Execute` at `551360` requests construction or
repair. These execution paths do not consult the improvement forecast.
Existing reservations need a separate execution and recovery test.

### Automatic Builder protection in the matched CE replay

`ce-builder-policy-01` ran both arms from the exact turn-45 save with the
same CE build and CSC district policy. Only the treatment published the
Builder allowance. The fixture supplied original seat roles because the
save predates the publisher. The controller issued no work orders.

The control removed the Pasture on turn 52 and attempted a Cattle harvest
on turn 57. The end sample had no Cattle and no active Storekeeper. The
treatment published one site allowance and kept the same Cattle Pasture
throughout the sampled turns. CE recorded 23 writes with zero Builder
faults. One native receipt changed Farm on player 3, city 131073, plot 796
from 27,094 Q8 to the native ineligible value of −2,559,744 Q8. The treatment
verified the exchange and Storekeeper at turns 63 and 66.

Boston's treatment tree selected a different Farm site on turn 61.
The sample does not prove that the Builder completed that alternate Farm.
This demonstrates automatic score-stage protection in the saved fixture.
Normal starts, already assigned jobs, direct harvest routes and Workshop
delivery remain open. The supported MSVC build is CE review commit
`1b63d6a`, proxy SHA-256
`8da947135a71f53928a7cb0eb0c1d92a8b7eaaa86087f0d2844e7aff07e01945`.
Both arms closed normally and restored preferences and the fixture package.
The matched result SHA-256 is
`399cb76fb260c2b179f71cd088dd625f88cd50d54be33c3d05314f9d9c3df624`.

## Natural recovery after the Boston blizzard

The stock recovery replay starts from the exact turn-210 interruption save
`retention-02/stage2.Civ6Save`, SHA-256
`5b9b0e69608a27c7e2c535d4f879a3d25bc9574cd999ffcc58d15a9f6bcc15ae`.
The reload matches the gameplay and UI observation. Cattle remains at
plot 796 with no Pasture. The Water Mill at 721 is pillaged, and the
Granary at 795 is intact. The controller only advances turns and observes.

There are two separate native paths. `BuildImprovementNode::Update` at
`551a80` can identify a matching pillaged improvement for a reachable
Builder, and its Execute route issues Repair or BuildImprovement.
`CityBuild::BuildBuilding` at `3df040` admits an absent or pillaged
building, checks `CanConstruct` at `f7100` and constructs a native build
request for that building type at `6834a0`. A damaged Mill competes for
city production. Its repair does not use a Builder.

An active job can constrain recovery before any repair bid is compared.
Boston's production log shows a Spaceport occupying the queue. A separate
Wonder tree submits a St. Basil's Cathedral contract on turn 211 and
successfully reserves coordinates (56, 10), the Cattle tile. The
improvement selector at `3e5750` and terrain analysis at `3dec40` both
skip rows with a resolvable live reservation. This identifies a competing
claim to trace in a matched protection test. The reservation alone does
not prove that the Cattle was removed or that the Wonder was constructed.

At the turn-234 endpoint the Cattle remained physically developable. The
Pasture had not been rebuilt, the Water Mill was still pillaged, and
Storekeeper had not operated at any of the sampled boundaries. There were
no policy writes or Farm rejections. The preserved endpoint SHA-256 is
`5bc4c32495659e2670d76779cca25c0ec024fdda3f7aca98c65d06d4ed4d3e40`.
The next comparison should observe the Wonder reservation ID and its
release, then measure whether an unreserved site produces a legal Pasture
job. For the Mill, observe the first actual production choice with the
repair available and record its cached value, legality, competing choice,
queue entry and realized payout. The earlier district-repair payout
failure involved a damaged Quarter, whereas Boston's Quarter remained
complete in this replay.

### A repair score and a Wonder score have different callers

Both callers reach building NetValue at RVA `52a050`. At `3e3edd` the
caller passes two `-9999` coordinate sentinels for ordinary city building
scores. In that branch, an existing pillaged building sets a repair flag
that doubles the computed score before the result is written to the city
building array. At `3e419a` the caller passes the tile's X and Y after
the native Wonder eligibility checks and copies the result into the tile's
building score array. The compiled Wonder protection intercepts only the
second caller.

`GetBestBuilding` at `3e4710` reads the city-center row's building values,
checks the candidate's queue count and applies native preferences and
requirements. A repair can win this comparison before the city is ready to
act. The ordinary `QueueNextBuild` path at `3e8190` and the threat path
at `3ea150` are separate. The latter has threat and attack gates in
addition to a score comparison. A higher repair score does not establish
that an economic build will be preempted.

### Matched Wonder protection changed the reservation

`ce-wonder-recovery-01` used the exact turn-210 damaged save in both arms.
Both loaded the same CE build and CSC district and Builder policies. Only
the treatment enabled the tile-specific Wonder protection on the protected
supplier sites. The live score sample for Boston and Cattle plot 796 moved
building index 67 from 4,638 Q8 to the native ineligible value of
−2,559,744 Q8.

On turn 211 the control selected St. Basil's Cathedral and successfully
reserved coordinates (56, 10). The treatment instead selected Országház
and successfully reserved (53, 9). The repeated success lines in each
tree describe its reservation steps. They do not establish two distinct
claims. The controller issued neither order.

At turn 222 the treatment retained the developable Cattle, with no
working Pasture and with the Water Mill still pillaged. The control also
had neither link repaired. The matched outcome proves that the policy
can change the Wonder plan and reserve a different site. It leaves
material job choice, repair scheduling and the existing-reservation case
open. The supported CE source is review commit `60a5a68` with proxy
SHA-256 `598d39b07f49c3e6646bb8c1c3b05cdb9dc32c2b069246ea61fab116c15088f6`.
Both arms closed normally and saved their endpoint. The matched result
SHA-256 is `b6b633c48c043315d1ce7c06b564810d6c71cbe2e71fa1c5561ee1b5aebdd0d9`.
Each arm reported 44,700 district-hook calls and zero district faults,
with 62 district entries at the endpoint. The Lua timer resolved no
nonzero durations in this window. These counts check activity and
capacity for the fixture. Native overhead still needs measurement.

### The Mill won the building comparison and missed the queue

`mill-repair-choice-01` resumed the exact stock turn-234 endpoint with a
read-only observer on the patched XP2 binary. The run reached turn 252
with zero native writes, no observer fault, and verified controller
restoration. Boston's Granary still worked, the Water Mill was pillaged,
and the developable Cattle had no improvement. Storekeeper growth was zero.

| Turn | Building comparison and actual production |
| --- | --- |
| 242 | The Spaceport completed. The eligible Water Mill repair scored 564,093 Q8 in the building comparison. Research Lab won with 1,325,518 Q8 and its build request succeeded. |
| 245 | The Research Lab completed. Water Mill won the building comparison at 645,296 Q8. Boston instead queued Theater Square contract 5774, submitted on turn 243. |
| 249 | Boston submitted Water Mill contract 5997 with a logged value of 1,511.0. |
| 250 | Boston queued Encampment contract 5954 after the Art Museum completed. No Mill build request appeared in the probe through turn 252. |

On this XP2 image, `QueueNextBuild` at RVA `3e8190` calls the building
selector with return address `3e849c`. Its ordinary contract branch
checks the city-build field at `0x150`, resolves the object through
`06bcd0`, then reads that object's signed value at `0x158`. It compares
the value against the unit value minus `0x100` and the project value.
A successful call to the contract's Execute slot at
`0x38` returns before fallback production selection. The building score
does not enter those contract checks. `LogContract` at `3f97e0` prints
the contract's `0x158` Q8 field divided by 256 and rounded to one decimal.
The submitted value is therefore a snapshot at a different stage from
the building selector or the later queue gate. A trace must capture the
values and eligibility of the contracts that actually reach admission.

The next recovery probe should trace how the stock proposal from
`CheckForUnitOrBuilding` at `3e1580` becomes a contender for admission.
Boston's turn-249 submission gives an existing legal repair request to
follow. Pasture job assignment needs its own test.

The trace is under `mill-repair-choice-01`. Its frozen SHA-256 is
`e2a71ed73410f6cf47dba075892880348337ff6c9be5af7ec8a2080f3151a8ea`.
The result SHA-256 is
`98a4f5d918a1be81712488a417930515ebbbfaaafb424f8b4e8a014ab753f081`.
The archived `AI_CityBuild.csv` identifies submissions and queue starts.
`City_BuildQueue.csv` records production progress. The probe's boundary
field identifies the beginning of a sampling segment.

### Native contract admission and value refresh

`ReceiveContract` at `3e9500` checks the offer's city-validation slot
`0x98` before adding its handle to the offered vector at city-build
`0x160`. Later `QueueNextBuild` scans that vector. It considers status 3
offers, validates them again, invokes the update slot `0x68`, then keeps
the largest signed value at contract offset `0x158`. The comparison is
strict, so equal later offers leave the earlier one in place. The winner
then faces the unit/project checks and Execute described above.

The assembly and exact hotfix bytes distinguish the item types in
`UnitRequestContract::Update` at `3fa5e0`. A building index at `0x190`
reaches building PresentValueOf `3e7e50` via `3fa630`. A unit index at
`0x178` reaches `3e8150` via `3fa69f`. A district index at `0x1a8`
reaches `3e7f40` via `3fa725`. Each path keeps the greater of the
retained contract value and the value returned by the corresponding
lookup. A targeted repair preference at the building lookup could pass
through the game's archived value setter and native competition. It
requires a legal offer to reach the update in the first place.

`mill-repair-contract-01` replayed the same turn-234 stock save with
additional read-only hooks on queue entry and the contract virtual methods.
All sampled Boston states matched the first replay through turn 252.

| Offer | At receipt | Before queue refresh | After queue refresh | Queue execution |
| --- | --- | --- | --- | --- |
| Water Mill 5997 | Accepted, 386,816 Q8 | Valid, 386,816 Q8 | 639,408 Q8 | No request |
| Encampment 5954 | Accepted, 3,439,104 Q8 | Valid, 3,439,104 Q8 | 3,694,136 Q8 | Succeeded |

Boston submitted the repair on turn 249 and compared both contracts on
turn 250 in the same queue pass. The earlier Research Lab provides a
positive control. Its value refreshed from 735,488 to 1,325,518 Q8 and
its contract executed when the Spaceport completed. At the turn-252
endpoint Boston still had an intact Granary, a pillaged Mill and no
working Pasture or Storekeeper.

The frozen trace SHA-256 is
`7dee26d09ac03362c1b504615548bbfcd3faa4649cb41a58027de9064f3c3bda`.
The original trace transposes the two labels `building` and `unit`.
Raw index 140 for contract 5997 is the Water Mill. The field offsets
above, the earlier building-selection trace and the closed production log
establish the identities. The preserved trace is unmodified. The REA
static trace of the exact patched image is
`ev_8569426d193a3db90ee899c49146e1a34a3b819392faeed02078ed1fd7657623`.

### The stock Mill repair completed after Encampment

`mill-repair-bid-control-01` cold-loaded the archived turn-249 autosave
SHA-256 `6d417eeea816a973ca4b4bd6eb62b692aca35e395218cf9cc71a48f2e492aaa3`.
The starting census matched. The turn-250 scores and Encampment execution
reproduced exactly. At the next vacancy, on turn 252, the same Water Mill
contract 5997 executed at 639,408 Q8. Its `BuildBuilding` request returned
true, and the native production log shows completion on turn 253 against
a repair cost of 40 Production.

The turn-255 gameplay census showed the existing Mill healthy at plot 721
and the Granary healthy at 795. The UI's post-repair sample carried turn
254. It showed 1 Production and 1 Gold on the Mill and 2 Food against
the Granary's base 1. The stricter same-turn exchange boolean stayed false
because the UI clock was one turn behind. Both clocks place the yield
read after the repair. The Cattle remained developable without a Pasture
and Storekeeper Growth remained zero.

The autosave control froze the read-only trace and restored the game and
temporary package. Its extra turn-255 save did not settle, so it has no
new checkpoint or final `result.json`. The endpoint census, archived
queue and restoration records remain available. Frozen trace SHA-256
`635704811d3912dab7d27954804bbef3a726bd99cab310f47583d08cd7a21634`.
Endpoint states SHA-256
`6d1905a2482c9b534a70030b11f9740fe1b999fd6e5768a6161c4e246c51f9f4`.
The proposed high diagnostic bid was withdrawn when this control
demonstrated stock repair and payout.

### Mill-only damage restored the full Service

`mill-only-recovery-01` loaded the verified healthy turn-66 Boston save
SHA-256 `56afbac023e9029f4d6fcaa5f270da07bc163bd724c6b511954de173b6630932`.
The shared controller issued one controlled setup operation to pillage
the existing Water Mill. The before/after city census differed only in
that building's pillage flag, and all six neighboring plot records were
identical. The Pasture and Granary were already working. No build order
or score change was made.

Boston finished University on turn 69 and selected Water Mill repair
through ordinary fallback production. The native `BuildBuilding` call
from `QueueNextBuild` returned true. The queue log shows repair completion
on turn 70 at a cost of 40 Production.

| Inactive turn | Mill | Granary Food | Mill Production / Gold | Storekeeper Growth |
| --- | --- | --- | --- | --- |
| 66 after damage | Pillaged | 1 | 0 / 0 | 0 |
| 69 | Pillaged | 1 | 0 / 0 | 0 |
| 72 | Repaired | 2 | 1 / 1 | 1 |
| 75 | Repaired | 2 | 1 / 1 | 1 |

The UI and gameplay clocks matched at each sample. The original Cattle
Pasture remained working, and the operation audit passed at 72 and 75.
The two Boston states verify stock building recovery with a competing
district contract or an existing University in production. The known
pillaged-Quarter payout issue is a different case. No building repair
priority was added. The missing Pasture in the late chain is the next
recovery dependency.

The result SHA-256 is
`4c08a91838ed60610643eee2baa9fbafb4b7485327b792c9f7efce97ffcf41bf`.
The frozen trace SHA-256 is
`ea11ddd2dd44343a2ace0134ad74df8d972eddbd04f054d2ee7a53813b1dd30d`.
The controller stopped at 75 after the repeat payout sample.

### Isolating the missing Pasture

The late stock chain still lacked its Pasture after Mill repair. On turn
253, a new Wonder planning tree successfully reserved the Cattle at
(56, 10). The contemporary ordinary improvement tree was pursuing a Mine
elsewhere. The reservation shows that stock late play had another
competing use for the supplier tile.

The earlier turn-66 checkpoint provides a separate test. The controller
removed only the Pasture, and the Cattle, Mill and Granary remained in
place. The first replay stopped before autoplay when its setup assertion
treated the now-buildable Cattle as an unexpected change. The next replay
accepted that transition and advanced through turn 75. It captured an
occupied improvement tree slot and positive Pasture scores before a
coordinate decoder fault stopped the trace. Both attempts closed and
restored the isolated package. The partial trace does not establish a
Pasture assignment or a recovery outcome.

The exact hotfix code shows two separate steps. `AnalyzeTerrain` at
`3dec40` writes a preferred improvement type after scoring rows and
resolving reservations. `CheckForImprovement` at `3e1150` requires a
free improvement tree slot, then calls `GetBestLocationFor` at `3e5750`
for that type. A nonempty reservation ID excludes a row only when the
manager lookup at `4019f0` returns a live object. The installed-image
REA row-evaluator trace is
`ev_d15420221964cf2ea5ea9c0c91658a8ca6ecebef53e1902cd6c6eb783594f88b`.

The corrected `pasture-only-recovery-03` trace reached turn 75 with zero
score writes. Boston had positive Pasture values of 28,194–38,463 Q8
through the first six checks. The stored Cattle reservation 4521998
resolved false, while the ordinary improvement slot 10027025 stayed
occupied. Once the slot opened, the Irrigation boost had a live Cattle
claim. Ordinary planning picked a Camp on (54, 8), scored at 35,432 Q8,
and started a different improvement tree.

The boost tree reserved (56, 10) on turn 72 and found a Builder on turn
73. On that turn its move and clearance records linked unit 2228225 to
the Cattle. The unit log recorded the same Builder's resource harvest.
The turn-75 census confirmed the Cattle was gone. Boston's Mill and
Granary still exchanged yields, and Storekeeper Growth remained zero.
The controller closed normally and restored the package and preferences.

The archive contains all nine fresh autosaves from turns 67–75. The
turn-72 decision save SHA-256 is
`59d39aa77fbf9ecabc7a6694f778d659e95813e55446c1ba62fe46b29d97a285`.
Result SHA-256 is
`6e39eaa70f96adf1b3dd3d310cf9bbf702e71cbbfb893e155777b2f7f2d49cc7`.
Frozen trace SHA-256 is
`ae3ad99f87ece3ca828bbd9d2318f4aa25e41252e5f267ef725ec998930b6533`.
The joined `supplier-timeline-linked.json` retains the raw sources and
clocks, with the map width supplied by the archived gameplay readback.
Its SHA-256 is
`8ed0b46555abd85f162f84605d008954b4d80eed7e62d91d44dd5e54d053243f`.
The next comparison uses that decision save in both arms and changes
only the Builder protection capability. Retaining the Cattle and
assigning a Pasture are separate outcomes.

Two starts of the matched CE comparison ended before autoplay. The
first could not move its prepared package into the Windows Mods
directory. The second used a hash-verified copy, loaded the exact
scenario and restored cleanly. Its fixture script ran before the
autosave clock reached turn 72, so the policy stayed disabled. The
shared controller now activates that fixture script once after verifying
the loaded turn and census.

### The turn-72 protection arms both lost the Cattle

The corrected `ce-pasture-recovery-03` pair cold-loaded the same
turn-72 decision save, used the same qualified CE binary and validated
the original census in both arms. District protection was active in
both. Only the treatment staged Builder protection. It published one
allowance for the Cattle supplier before autoplay and reported no
native faults.

The turn-73 and turn-74 publication receipts each reported two changes
from their preceding intervals. In both, the first changed key was
player 3, Boston 131073, plot 796, Farm index 1. Its previous scores
were 41,309 and 42,128 Q8. CE replaced each with the native
ineligible value of −2,559,744 Q8.

The control and treatment still produced the same target job and
outcome. Their joined timelines link the turn-72 Irrigation reservation,
turn-73 clearance and harvest by Builder 2228225, and the missing Cattle
at turn 75. Both reached turn 84 with an intact Mill and Granary
exchange, no Pasture and no Storekeeper. Both closed and restored the
package and preferences. The native receipts establish writes to the
forecast. They do not order those writes against the actual selector
read or prove that the job read that score.

Control timeline SHA-256 is
`5cc2b3e02606ad23567db36b703a537f5db0adf2ff3596a36034f0fc036e3adc`.
Treatment timeline SHA-256 is
`dabd56e5077223b131e96d3fe094294c131da3160ccdf5c3c2f623f7bffcdac4`.
The earlier turn-69 replay adds read-only traces at all eight exact
location-selector callers, including boost checks and ordinary
proposals. This keeps cached selection, retained jobs and later
execution distinguishable.

### Earlier protection redirected the boost and preserved the deposit

Both `ce-pasture-early-01` arms cold-loaded turn 69 from SHA-256
`3869816217cf2e5bb428fec2632f08fdb39539138855a3ff6d9dcde3a0af1f16`.
The starting census, CE binary and district policy matched. Only the
treatment enabled Builder protection. The earlier stock turn-72 save
had been captured before the reservation first appeared in that run's
log. The turn-69 cold replay logged its control reservation on turn 71.
Use the checkpoint and the replay's own events to order the decision.

In the first traced interval, Boston's empire-trigger Farm location
returned Cattle plot (56,10) at 38,655 Q8 in control. The treatment
read −2,559,744 on that row and returned (54,10) for Boston. The
empire's Irrigation tree actually reserved (63,11) in treatment. The
control tree reserved (56,10) and Builder 2228225 harvested it on turn
73. At turn 81 the treatment still had the developable Cattle and the
control did not. Neither arm had a working Pasture or Storekeeper.
Both closed with preferences and packages verified and no trace faults.

The first empty ordinary slot gave the same Camp proposal in both arms.
During the turn-72 interval the treatment admitted tree 11337745.
Camp at (54,8) scored 35,432 Q8 and the Cattle Pasture scored 29,056.
The old Cattle reservation did not resolve. At the next empty slot
Camp again won at 39,518 against the Pasture's 32,096 Q8. This isolates
ordinary job competition after material protection. A diagnostic
8,192 Q8 Pasture bid is sized just above both observed gaps. The test
must verify which job the AI admits, assigns and finishes, then check
Storekeeper's actual payout. Already committed harvests remain a
separate boundary.

Control and treatment joined timeline SHA-256 values are
`63137657fb7f8a2c7817a89c9f24451c99b6ec7ea2341d05f0f700e0b6ff207c`
and `3965701a71bb263efa69b06caa2dfd6de2883c1eee36410c03ef8e3d9e1abba0`.

### A bounded Pasture bid restored Storekeeper in the matched replay

The `ce-pasture-bid-01` arms reused the turn-69 checkpoint and matched
its starting census. Both had the same CE binary and active district
and Builder protection. The only changed policy was a fixture-only
8,192 Q8 addition on the positive native Boston Cattle Pasture score
as it entered the improvement row at `3e3436`. The bid left other
players, sites, improvement types and ineligible results untouched.

At the first free ordinary slot, control admitted the Camp at (54,8)
with 35,432 Q8. The treatment read the stock Pasture at 29,056 Q8,
stored 37,248, and admitted its ordinary job for (56,10). Tree
11337745 reserved the Pasture on turn 72. Boston found a Builder on
turn 74, moved it to (56,10), and logged successful Pasture work.
The same turn's player-3 operation log has one Build Improvement
request, from Builder 2228225. The turn-75 census independently
verified the original Cattle and unpillaged Pasture.

On turns 75 and 78 the Water Mill paid Food, Production and Gold of
1 each, the Granary paid Food 2 against a base of 1, and the native
Storekeeper growth property was 1. Control still had the Cattle
with no improvement at turn 87. Its Granary and Mill retained the
existing exchange, with Mill Food and the Storekeeper property at
zero. Both arms closed and restored successfully. Direct growth
modifier recipient tracking is a separate qualification check.

Both first jobs used Builder request 914. Control's St. Louis began
training a Builder, but Boston found one before that production
finished and cancelled the request. The logs do not assign that
Builder to a particular training city. The subsequent control Camp
request 1015 timed out after eight turns without an available worker.
Changing the site bid recovered the chain in this case without a
new worker-supply rule. Other worker-starved states still need
separate tests.

Control and treatment joined timeline SHA-256 values are
`7d4215b76ad5a3ca907dc1e8ba3636b8e0a06091e6c8b5c34a26ece430cff4eb`
and `03900978ab45fa24a1be33f75d4afd90b208384a28b8d5769e6a448860b84214`.
The test applies to one controlled interruption in one world.
The next implementation should publish a reusable, bounded bid for
eligible suppliers through CE and verify it with the main CSC policy.

### Clear Plot validates its selected worker before submitting the operation

Ghidra on the matching Windows XP2 reference traces
`ClearPlotNode::Update` at RVA `55eaf0`. It resolves the bound target
coordinates and checks available workers for charges and reachability.
It starts with the selected unit field at `node+0x40` set to −1. The
ready path at `55ed62` stores the worker ID there and returns 1. Other
paths return 2 for a reachable worker or 3 for failure. All paths free
the temporary worker list before returning.

The later `ClearPlotNode::Execute` at `55d970` uses that worker ID.
If the worker's current plot has an improvement, it submits removal.
With an empty improvement slot and a true harvest binding, it
constructs a Harvest Resource request at `55da66` and submits it
through the unit-operation dispatcher. This is downstream of the
improvement score and already-bound job location.

The installed hotfix image SHA-256 `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`
matched the readiness, selected-worker write and harvest request
fingerprints. An offline check of a diagnostic guard kept native
cleanup and changed only an exact ready harvest to the existing
failure state with no selected worker. The live test must verify
whether the tree releases its job and the protected tile stays intact.

### A committed harvest failed safely and Boston used the plot again

Both `ce-committed-harvest-01` arms cold-loaded the same archived
turn-72 save at SHA-256
`59d39aa77fbf9ecabc7a6694f778d659e95813e55446c1ba62fe46b29d97a285`.
Both enabled the existing CE Builder protection and used the same
patched XP2 and CE binary. Treatment alone rejected the first ready
Clear Plot call for the exact protected plot, player and known
Builder 2228225. The guard reset the selected worker and returned
the native failure value. It observed later attempts without
changing them.

Both Irrigation boost trees reserved (56,10). On turn 73 the control
logged successful clearance by Builder 2228225 and submitted
Harvest Resource. Treatment logged `FAILURE, Clear Plot, Clearing
with -1`, with no corresponding harvest and no repeated ready call.
At turn 78 the ordinary Boston improvement tree successfully
reserved (56,10). On turn 79 it reached that plot and logged
successful Pasture work. Builder 2228225 issued the only matching
player-3 build-improvement request that turn. The turn-81 read
verified a working Pasture, Granary Food 2, Mill Food/Production/Gold
1 each, and the Storekeeper growth property at 1. Control had no
Cattle at its turn-81 endpoint. Both arms closed with no trace
faults and verified restoration.

The new reservation and finished work establish that another job
could use the site. The replay does not inspect the discarded
tree's internal object lifetime. This one-shot intervention
only covers the observed Clear Plot harvest route. Working
improvements, other removal routes and the reusable CE gate
need separate coverage.

The joined control and treatment timeline SHA-256 values are
`6016aea946f426c1f144905a1840686ffed71ef6c9fa135d5a3d955105cfecf6`
and `05d78d07ef59ffa008a3b6bae735f5d9c739fcb807a51101cabb8cd14e1443c3`.

The `ce-harvest-publisher-01` match repeated that comparison without
Frida. Both arms used CE review commit `4f6f235`, the same source
save and ordinary Builder protection. The treatment alone staged
Clear Plot protection through the main CSC publisher. The supported
Release x64 DLL SHA-256 was
`74fe01492a456c2d13e5095cc2c640254a2279d894f8647afc73525a799bde8d`.
The isolated build passed 70 score and policy checks and four
hook-group checks.

The native publication on turn 74 reported one rejection in the
preceding epoch for player 3, plot 796 and Builder 2228225. The
behavior tree logged the turn-73 failure. Control logged the
successful clearance and harvested. Treatment reserved the
same Cattle tile for Pasture at 78, built it on 79 and had
active native Storekeeper on its City Center at 81 and 84.
Control had no Cattle or Boston Storekeeper at 84. Both sessions
closed and restored successfully. This qualifies the reusable
guard for the matched route. Other destructive routes and
long-term effects in fresh games still need checking.

The integrated guard's control and treatment timeline SHA-256 values
are `4222d1146b3b1d8d819452947ff0b4d41fd869280b0a68cd8d9d7db7f1a37355`
and `9b6629c0b384bc7b843703ea0f84e3bb2c73c7d55049d332eb8572717f479f98`.

### The main CSC supplier publisher uses the existing CE score hook

Review branch `codex/ce-builder-supplier-bids` at `32e6edb` extends
the ordinary improvement NetValue hook from the earlier CE candidate.
The optional `CE_AIBuilderProtectionBid` entry carries one positive
bounded Q8 preference on a compatible improvement. The hook
checks the exact key and publication generation, preserves
the ineligible sentinel, and records positive and protection
writes separately. There is no new native hook for the preference.
The supported Release x64 build produced SHA-256
`b769ff9a6f03fdfcc32be33c2a2ddbd5c7f41fc6254170a147ef6e60096b941a`.
The isolated native run passed 58 score and four hook-group checks.

The initial CSC recovery policy applies to a completed Bakers
Quarter with Feudalism, its functioning Mill, a functioning
adjacent Granary or City Center replacement, and one viable
Base source whose improvement is missing or pillaged. CSC
publishes the bid alongside its existing allowance for that
protected source. The policy leaves alternative legal improvements
for the native scorer and retains protection when the optional
bid capability is absent. Offline Lua checks cover those gates
and the old interface.

The closed `ce-pasture-publisher-01` match used the main CSC
gameplay scripts and that CE build in both arms without Frida.
Control hid only the optional preference API. Both loaded the
turn-69 census, enabled protection and kept the Cattle. CE
reported the same 29,056 to 37,248 Pasture adjustment during
the turn-72 decision in treatment. The AI reserved (56,10)
on turn 72 and logged successful Pasture work on turn 74.
The protection-only control still had no Pasture and no
Boston Storekeeper at turn 81.

The synchronized treatment censuses at 75 and 78 verified
the Pasture, the Mill's supplier output and the actual native
growth modifier. Attachment instance 10788 had producer
district object 1239 (Boston Quarter 262147) and City Center
subject 782 (district 196610, player 3, city 131073). Growth
instance 16874 was active on that same recipient object.
Both arm endpoints and restorations were verified. This
validates the reusable publisher for the controlled recovery
case. The modifier sample provides exact identities for a
future per-turn collector. It does not establish duration,
fresh-game qualification or general unique replacement behavior.

Control and treatment joined timeline SHA-256 values are
`47f9af7a949b34798efa62ad147f90bc3e280f7a955f63461bf0653d3c8fc3c8`
and `b2acec07a823c7e480c1e08fccf0cf4966622063e7b57558301eb94f62c33df9`.

### Preserving the natural supplier did not resolve simultaneous damage

The `ce-natural-supplier-followthrough-01` continuation cold-loaded the
verified turn-222 Wonder-protected checkpoint with the main CSC publisher
and the CE supplier-bid build. It made no fixture edits after loading.
Boston's Cattle remained on plot 796 without a district or improvement
through turn 264. At all fourteen samples, the Water Mill was down and
the Granary was functioning. Storekeeper never operated in that window.
The existing recovery preference requires a functioning Mill and did
not provide a Boston Pasture preference for this simultaneous damage.

Boston finished Spaceport on turn 239, Research Lab on 242 and
Encampment on 249, with culture and military buildings between
production commitments. It then ran Orbital Laser projects through
turn 262 and switched to Modern Armor. The city log contains no Water
Mill submission or completion. The earlier stock branch that repaired
the Mill at 253 was a different trajectory. This run does not isolate
which competing native value kept the Mill out of the candidate list.
There was no fault in the CE Builder or Wonder policy. The game closed
and restored its package and preferences.

The 42 retained Lua publication receipts covered five original AI
players and 62–116 district entries per turn, with zero omitted.
Every reported Lua timing was 0.0000 seconds. This clock readout
does not establish runtime cost. A qualified timer and a matched
mature measurement are still needed.

The ten fresh autosaves for 255–264 were preserved from the closed
process with SHA-256 receipts in `treatment/decision-saves/archive.json`.
The turn-257 checkpoint is
`db8169ec7ed052a2e1da5ac65cf86b43eace359573c8894bd6b0e22aa74fcda3`.
Inspect an exact pre-selection save to distinguish a missing repair
proposal from an eligible proposal losing to other production.
Preserve strategic project competition when calibrating any repair bid.

### Military Academy beat the eligible Mill in building selection

`ce-late-mill-choice-01` cold-loaded the exact turn-258 autosave,
SHA-256 `6b80f5133634089fe37e98fbd59b14ba31149df09c059caa6285bb0154f5534e`,
with the same verified starting census and CE build. The read-only
trace sampled the ordinary building caller after the CE hook
returned. Boston's Mill passed the native requirements check in
all six observed building selections. Military Academy won each.
Its identity comes from contract 6344, whose native building index
27 matches the submitted Academy row in the city log.

At the fallback comparison in the turn-261 interval, the Mill's
cached row was 685,413 Q8. The Academy won the building selection
at 746,032 Q8. The city validated its earlier Academy contract and
refreshed its value from 547,584 to 746,032. No Academy contract
execution or ordinary building request followed in that queue
pass. Boston queued Modern Armor under Generic Offense at the
turn-262 decision. The AI kept Cattle and finished the replay at
264 with the Mill, Pasture and Storekeeper still down.

The cached Mill row and effective Academy winner are different
comparison stages. The trace does not establish a 60,619 Q8 bid
margin. Native `GetBestBuilding` at `3e4710` can transform the cached
value before ranking. `QueueNextBuild` at `3e8190` then compares its
building, unit and project alternatives after trying an offered
contract. The next trace records the Mill's actual comparison
operand and the queue's three category values before the generic
fallback. A legal building bid can matter only if it survives
these separate choices.

The frozen trace had no fault or active callback at shutdown.
Its SHA-256 is
`50e5a2f2d089187785e96cb4cb781dd93e3cb18c7db04e8fbe63266e30f01422`.
The native session and temporary package both closed and restored.

### The rejected project sent the queue straight to generic offense

`ce-late-mill-queue-01` cold-loaded the exact turn-261 autosave
`e393c2047e28ec9c167934799f9f1d55cef564d5e45e0d4f2cc062c84d9580b8`.
The read-only observer now sampled the effective candidate at
`GetBestBuilding` comparison `3e49da`. The earlier nomination used
407,461 Q8 for the Mill and 504,788 for Academy. At the ordinary
queue's building comparison, the Mill had 685,413 Q8 and Academy
746,032. The second trace independently measured the effective
60,619 Q8 gap at that comparison. The earlier gap was 97,327 Q8.

At the category comparison `3e8741`, Academy at 746,032 Q8 beat
ordinary unit index 2 at 77,654 and lost to project index 25 at
1,428,800. `BuildProject` returned false at `3e88e5`. The queue
called `GetBestUnitToBuild`, returned unit index 92 at `3e899f`,
and the city log recorded Modern Armor under Generic Offense on
turn 262. No building retry followed. The native `BuildProject`
routine at `3df4b0` can reject at `BuildQueue::CanAdvance` or at
operation-manager validation. This trace did not distinguish them.
`GetBestProject` at `3e5960` compares cached project values and skips
the current project. The inspected selector does not call either
of those validation gates before ranking the remaining projects.

The failed project outranked the Mill by 743,387 Q8 in this pass.
That difference describes the old comparison, including the
unexecutable winner. It does not price the economic benefit of
repair. Check whether native project eligibility can be established
before category ranking or whether a rejected operation can fall
through to the best remaining legal action. Measure a bounded Mill
bid separately at building ranking and keep valid strategic projects
in competition.

The frozen trace SHA-256 is
`ac90a198d36881fdc9c1e7a9588a55824e4b0b9a8ab8aa7e27a9c21290e4c122`.
It had no fault and no active observer at shutdown. The controller
closed the game and restored the temporary package and preferences.

The control arm of `ce-late-mill-bid-02` reproduced the same operands
and the rejected project. It sampled both validation returns inside
`BuildProject`. Project 25 returned false from `BuildQueue::CanAdvance`
at `3df4e5` and did not reach operation-manager validation at `3df568`.
The exact condition inside `CanAdvance` remains unresolved. The
control closed normally. Its frozen trace SHA-256 is
`15c883358019052b2463f6d365eab433f0e69e10069e682221735a3fa02fbcee`.
The first launch, `ce-late-mill-bid-01`, stopped before autoplay
because its control assertion expected Wonder protection disabled.
The corrected pair keeps that protection enabled in both arms.

The treatment's interval through turn 264 confirms that the +98,304 Q8
diagnostic preference changed both effective building winners to the
Water Mill, index 140. The earlier caller at `3ea73b` is in
`UpdateBuildQueueForThreat` at `3ea150`. It is a threat review rather
than `CheckForUnitOrBuilding` at `3e1580`, which calls the selector with
flags 0/0 and may create a new request tree. The pulse changed the
threat comparison from 407,461 to 505,765 Q8 and the actual queue
building comparison from 685,413 to 783,717 Q8. No Mill offer or
building submission appeared in the observed turn-261 queue pass.

Project 25 remained the higher category choice and returned false
from `CanAdvance` again. The generic unit return was unchanged.
Both arms still lacked a working Mill, Pasture and Storekeeper at
turns 264 and 267. The treatment trace had zero faults and zero
active callbacks at freeze. Its SHA-256 is
`22e2f971244da8df6f46e4e1a61b5ee1bb2d9f4a50c509ff7b0fd41dc583025f`.
Use the ordinary queue caller alone for any next repair comparison.
Check whether omitting only an unadvanceable project from ranking
exposes the next legal native choice. Keep all advanceable projects
and the engine's execution checks in place.
`QueueNextBuild` calls `GetBestProject` before it arbitrates offered
contracts and reuses that project value in default category ranking.
Filtering a project there can therefore admit an existing contract
before default building choice. Observe both stages in the next test.

## Project eligibility preserved a valid Terrestrial Laser

The matched `ce-late-project-eligibility-01` replay loaded the same
turn-261 save in both arms and ran through turn 264. The treatment
used the original `CanAdvance` for projects that could take the lead
in Boston's ranking. It made no Mill score change. The control's
project 25 won at 1,428,800 Q8, failed `CanAdvance` and never reached
operation validation. Boston queued Modern Armor through generic
offense on turn 262.

The treatment excluded projects 0, 5, 6 and 25 after failed checks.
Projects 8 and 26 passed. Project 26 won at 1,428,800 Q8 and passed
both `CanAdvance` and operation validation. Boston's build log
identified Terrestrial Laser on turn 262 and its queue recorded
44.3 of 300 production on turn 263. The trace does not identify
project 25 by name. Both arms ended with the Mill and Pasture still
down and no Storekeeper. This was a scoped diagnostic. It demonstrates
that pre-ranking eligibility can retain a valid project while fixing
this particular fallback. It does not establish a reusable repair bid.

## Boston repaired the Mill after Theater Square

The stock replay `mill-only-recovery-114-01` used the healthy turn-114
retention checkpoint. The setup pillaged only Boston's Water Mill.
The Cattle Pasture and Granary stayed working, and the exchange and
Storekeeper stopped. The new damaged source was saved and verified
as `mill-only-start.Civ6Save`, SHA-256
`23bcd375c079cb66ef099755adb6bd9b26963bbe72be89cde472dec47831c0f8`.
There was no native score or queue write.

Boston finished Military Academy and accepted an existing Theater
Square contract at 428,005 Q8. The city log names it on turn 118.
It submitted Water Mill repair contract 2028 on turn 119. On turn
124, Theater Square completed and the Mill contract executed at
544,874 Q8. On turn 125 the build queue recorded 76.3 production
against the 40-production repair cost. The turn-126 census found
the Water Mill, original Pasture, exchange and Storekeeper working.
The Granary yielded 2 Food against its base 1, the Mill yielded
1 Food and the Service Growth property was 1.

The replay shows stock AI restoring a ready chain after finishing a
competing district. The earlier opening used the existing district
contract, before fallback building selection. Raising that fallback
score alone would not move the repair ahead of this commitment.
The run ended at 126, so it verifies recovery at that endpoint.
The observer froze with no faults and no active callbacks. Its
SHA-256 is
`4c6218e876ea4cdda3bed8edc521a8fb9026e1eb38334be2f1bb66c4b61c7e79`.
Controller restoration passed.

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

## Native civic decision boundary

`CultureAi::DoTurnActivate` calls `QueueNextCivic` at `418860` when
`GetProgressingCivic` reports no active civic. The queue passes the
`CivicAnalysis` range and the excluded next-step index to the comparator
at `40de20`. `CivicAnalysis::toString` at `41e8a0` labels the row's goal,
owned flag, estimated turns, solo value and full value. Both values are
logged as Q8. The comparator first prefers unowned rows and avoids the
excluded next-step index. It compares full value at `+0x14` when the
signed product of the two turn estimates is positive. Otherwise it
compares the turn-estimate fields. The winner supplies its separate
next step at `+0x1c` to `Culture::CanProgress`. A failed winner takes
the random fallback among eligible unowned civics.

`CivicResearchContract::Execute` at `3f8250` calls `IncreasePriority`
at `416630`. It adds the contract value to the addressed row's full
score when that score is nonnegative. It does not change the actual
research queue. `CalculateFullValue` at `412c00` also resets and rebuilds
the score from the goal and up to two prerequisite levels. A stock-AI
Feudalism test should capture the effective goal operands near actual
queue selection, the queued legal prerequisite if any, Feudalism's
completion, and Storekeeper separately. These findings are static.

## Native Storekeeper turn sampling

`ce-storekeeper-watch-01` repeated the turn-69 Pasture publisher pair
through turn 78 with the optional PlotInfo watcher and no Frida. The
watcher sampled turns 70, 71, 73, 74, 76 and 77 in both arms. In treatment,
Boston's City Center received the active native Storekeeper growth effect
on turns 76 and 77. Control recorded zero active turns for Boston. Neither
arm recorded a watcher fault. The controller paused on turns 72 and 75,
and the watcher did not sample those boundaries or the initial and final
turns. Use a continuous autoplay interval to verify full interior coverage
before using this method to qualify a 100-turn count. The parser excludes
unsampled turns.

The saved control and treatment `Lua.log` SHA-256 values are
`415f71be98fdfaa6154f5e358f1e7618bfd7f8a10eee0f5098e1c75d2e21f385` and
`08c43c1a241d0d9263567e5ca7b9ecd73f372ea157247f95595d720a1775981d`.

## Separate local CSC and CE packages

`Desktop/Codex/csc-bakers-qualification-20261107/staged-01` contains
separate development packages. CSC uses the installed package's registered
assets, the AI and adjacency files from commit `3d180d6`, and the main mod's
canonical action declarations. Its manifest declares the local CE package
as a dependency. CE contains the reviewed harvest-gate build with DLL
SHA-256 `74fe01492a456c2d13e5095cc2c640254a2279d894f8647afc73525a799bde8d`.
Both received distinct local IDs. Packaging verified the CSC reference
was unchanged and all 18 parity-tool tests passed.

`Desktop/Codex/csc-bakers-qualification-20261107/development-smoke-01`
loaded that pair from ordinary Ancient start on a separate Continents
development seed, map 18461107 and game 29461107, on Online speed.
At turn 1 it verified the exact separate CE DLL and the unmodified
DX11 XP2 DLL. Main CSC recorded its five original AIs and published
on each of turns 1–8. CE reported 22,084 scoring calls and zero faults
at turn 8. The early policy had no qualifying protection entries.
One uninterrupted autoplay interval from turn 1 to 8 produced exactly
the six expected interior Storekeeper samples, turns 2–7, and zero
active chains. This verifies early clock coverage and package loading.
It leaves mature measurement, effect uptime and fresh-seed outcomes
open. The controller closed and verified preference restoration.

The Service audit now reports active and observed inactive ranges per
Quarter, with missing samples and ambiguous recipient attribution listed
separately. The native payout log and gap fixtures verified the distinction.
The runner can use a longer
bounded continuous window for mature games, preserving the shared
controller's ten-minute per-turn stall guard and the default 30-minute
interval for other callers. The offline controller suite passed.

The development smoke's `result.json` and `Lua.log` SHA-256 values are
`4ea0c76235f64d358bb0702be8b3eacc6dee314e963824b60f40e4ddc6f84427` and
`18f25f6876812488221f4f05bfc14a84606bfd45f06f0ab2424aaa965454ecae`.

The next development runner supports all three Standard-size map
scripts from the stock-AI roadmap. Its untuned arm removes only the
main AI gameplay action from an isolated copy of CSC's manifest.
The control keeps the same CSC and CE IDs and input content. For a
paired run the runner checks the input digests, seeds and settings,
then compares the turn-one map signature, leader roster and starting
units. The manifest transformation and census code passed offline
checks. The fresh control and live start comparison remain to verify.

### Owned-site placement publishing

The main CSC publisher now combines protection deductions with one
positive Bakers bid per eligible city. `CSC_AI_BakersSiteForecasts`
uses `CanProduce`, the native BUILD target list, and the specific plot's
`CanStartOperation` result. It scopes the scan to revealed, assigned,
owned plots within three hexes. It excludes visible mapped materials
under the footprint and plots the protection policy has priced.
A candidate needs viable Base supply and a friendly City Center for the
Granary. Loaded CSC production and gold adjacency rules forecast the
site and choose its correct future Mill branch. Specialty breaks ties.

The initial early-score bands are 12,288 Q8 for at least +4 combined
adjacency and 6,144 for a weaker viable site. These are calibration
choices. The previous one-off Boston success used a late adjustment,
so it does not establish an equivalent early amount. Native AI still
owns production selection and legal execution. The scanner and the
publisher packet passed offline fixtures, including preservation of
the supplier deductions on a placement-read failure. The fresh
development run `development-placement-01` used `staged-02` and
reached turn 45. It logged 219 `Unknown production type` errors from
Gameplay `lHasBeenPlaced` and published zero site bids. Supplier
protection remained enabled and the controller restored preferences.
The `Lua.log` SHA-256 is
`05df59f15f2fbb0f670fd27132a66ed6fcdab8290483e9bccc517ce841eeae4b`.

Gameplay's `ICityBuildQueue::PushMethods` at `6c9860` registers a
different implementation from the UI cache. `HasBeenPlaced` at
`6ca220` dispatches on a production discriminator, then reads a second
value. `DISTRICT` hashes to `0x080d3734` and selects the native
district-index overload. The Gameplay `CanProduce` registration points
to the `Not Implemented` stub at `6ca200`. The stock ProductionPanel
uses the UI-cache hash-only placement method and its separate readiness
method. CSC now calls those read-only methods through its UI bridge,
then checks the returned plots again in Gameplay before publishing.
The offline fixtures passed and `development-placement-02` uses the
corrected `staged-03` build. It reached turn 45 with zero placement
errors, positive bids on turns 14–45, and up to four bids per turn.
The CE status at turns 15–45 records 99 changed native score calls
across the 31 preceding publications, each containing only positive
placement entries. No entry was omitted. All 43 expected interior
Storekeeper samples were captured. None was active. The game closed
normally and restored preferences.

`development-placement-control-01` used the same package digests,
seeds, map signature, leaders and starting units, with only the CSC
publisher action removed. CE remained loaded with zero active entries
and zero changed scores. Ancyra submitted Bakers contract 422 at
`(24, 19)` on turn 39 and put it in production on turn 44 in both
arms. The proposal value was 349 with tuning and 325 in the untuned
arm. The 24-unit difference matches the 6,144 Q8 band. This verifies
score delivery through a native proposal on that site. The observed
major-AI Bakers queue outcome was the same in both arms. Neither arm
recorded a completion by 45 or an active Storekeeper sample.
The next publisher version records a bounded set of native score
samples by city and plot before each batch resets them.

The tuned and untuned `Lua.log` SHA-256 values are
`a4132057d3f4ae78ce8e795fdbebc1d1b351cf2b21280552053cc58de4fdb762` and
`ce0ddcf6a4853cba6c337d232e395098a10b3918398c89f547c70d11950be4cd`.

## Normal-start follow-through to turn 100

`development-chain-100-01` repeated the Small Continents development
start with the same map and game seeds. The tuned package added the
committed score samples to the previous tested package. Stock AI ran
from turn 1 to 100 with both local packages and no gameplay
interventions. The session closed and restored preferences. The 98
required interior Storekeeper samples recorded no active or
ambiguously attributed effect for the original major AIs.

| City | Quarter at 100 | Stage 2 state |
| --- | --- | --- |
| Ancyra | Complete at 48 | Working Rice Farm. Both Mill and Granary absent. |
| Alexandria Troas | Complete at 71 | Water Mill and Granary working. Unimproved Cattle 2312 is the sole mapped Base. |
| Melbourne | Complete at 82 | Working Rice Farm and Granary. Mill absent. |
| Amphipolis | Complete at 89 | Working Wind Mill. No adjacent City Center or mapped Base. |
| Mainz | Incomplete | Adjacent working Granary. No adjacent Base. |
| Boston | Incomplete | Adjacent City Center and two unimproved Base deposits. Granary absent. |

All five original major AIs had Feudalism by 100. Native score
samples positively identify the eventual site in Ancyra, Alexandria
Troas, Melbourne and Boston. These are delivered adjustments, not
proof that the city changed its choice. The run has no matched
untuned arm through 100. The first 99 published turns report 1,759
changed score calls in aggregate, including material protection.
The publisher logged zero elapsed CPU time at its recorded precision,
which does not bound cost in a mature empire.

Alexandria Troas had access to Pasture. The CE telemetry at turns
81–86 and 90–100 reports the +8,192 Q8 adjustment on the exact
city, tile and improvement, including 33,226 to 41,418 Q8 late in
the run. The city repeatedly reserved forest plot (20,30) for other
work while Cattle (18,31) stayed unimproved. Score delivery did not
establish proposal, job assignment or execution for the Pasture.
Replay the exact source and inspect the ordinary improvement type
and location selectors, the existing job slot, and available workers
before changing the bid.

The endpoint save SHA-256 is
`e47f3982a1cf4b9e69ec3950e86d009fd08f9fdd07a4ab7cc4e3ff0995f7d769`.
The turn-100 census and result SHA-256 are
`1bca1b1a0336efd6bf8a11561bbe9d7227ff35ca583ff625ba4ab0d4ef9903cc` and
`71a2e138df19d538a09a05da8df864fee01559fb3d27abb1e3e409118944b21e`.

### Alexandria selected a different Pasture

`development-alexandria-pasture-01` reloaded the exact turn-100
save with the same staged packages and an identical Stage 2 census.
The observer was read-only. Macedonia had three Builders with
four charges in total at load. Nine of the twelve observed
ordinary proposal calls found an existing improvement tree.
On each of the three open slots the native best improvement type
was Pasture, and the ordinary selector picked (18,29), not the
chain's Cattle at (18,31).

| Open comparison | Selected tile, Q8 | Supply tile, Q8 | Margin, Q8 |
| --- | ---: | ---: | ---: |
| First | 36,280 | 30,392 | 5,888 |
| Second | 34,739 | 28,851 | 5,888 |
| Third | 34,650 | 28,762 | 5,888 |

Each supplier value already includes the integrated +8,192 Q8.
Its row was owned and selectable with no reservation. Native logs
identify the first competing Pasture reservation on 102. The
competing tree found a Builder on 110. This shows that the Cattle
lost on the location comparison when the slot opened. It does
not show whether the AI would assign a Builder to that target.
The Cattle remained unimproved at 112. All eleven interior
Storekeeper samples were present with no original-major activation.

The controller closed and restored preferences. Civ truncated five
optional district telemetry batches on 107–111. The report parser
now records those omissions and still requires all Service samples.
The native trace froze without faults, SHA-256
`2ee267c238432d02c5dde88628b27335b4a5013baaf47ec83648d9d6ba10f083`.
The next matched diagnostic can use +6,144 Q8 on top of the current
bid for this one comparison, just above the measured gap, and
verify assignment, construction and Service. This is a test amount
for this save.

### The extra Pasture bid changed location and assignment

`development-alexandria-pasture-bid-01` used the same turn-100 save,
packages and turn-112 endpoint as the read-only comparison. The sole
intervention added 6,144 Q8 to the existing positive Pasture score on
Alexandria Troas's Cattle at (18,31), after the integrated CE adjustment.
The game selected that Cattle on all three open comparisons, at 36,536,
34,995 and 34,906 Q8. Each value was 256 Q8 above the corresponding
control winner on (18,29). The city reserved the Bakers tile on 102 and
found a Builder for it on 105, 107 and 110. The behavior tree reported the
move in progress through the last logged turn.

The endpoint still showed bare Cattle and no active Storekeeper in
the eleven interior samples. Macedonia's one remaining Builder had
three charges at (17,33). The generic unit log shows failed swap
attempts followed by move requests for that unit. That log does
not identify the route or establish why it had not reached the tile.
The scoped increase changed selection and assignment in this fixture.
Completion and payout remain separate evidence.

The run closed and restored preferences. Trace SHA-256 is
`8ff3c1ce12d32deb506df2be947afd46dc5f9c566e0c72baec4466a311143be9`.
Its turn-112 save SHA-256 is
`b3d6cc1aa78e8a156e60c4b110b229a3631ccaed57e24d7883aaca549fbc9545`.
### The follow-through control returned to the competing Pasture

`development-alexandria-movement-01` cold-loaded the treatment's
exact turn-112 save with the integrated bid and no extra preference.
The city retained its (18,31) reservation in the turn-112 behavior
log. At 113 a new ordinary job reserved the other Pasture at (18,29).
Builder 2359298 reached that tile at 117 with two charges. The tree
reported successful Pasture construction at 118, and the Builder had
one charge left. The AI later used its final charge on a Lumber Mill.
The Bakers supplier remained bare through 122. None of the nine
interior Storekeeper samples showed an original-major activation.

The movement watch sampled the owned Bakers tile at the end of
each Macedonian phase from 112 through 121. No unit was on the
target at those samples. This does not rule out transient occupancy
or contention on an approach tile. The Builder's movement and
construction on the competing site show it was capable of working.
This arm removed the extra bid at reload. A second continuation
from the same save retains it to test whether the Bakers tile
can remain competitive through allocation and construction.
The control `Lua.log` SHA-256 is
`4b2f4b9e7fdf9e4ad55550507b542f559bd78554b11c3ec6971058a18a692f34`.

### Keeping the bid active completed the Bakers Pasture and Storekeeper

`development-alexandria-movement-bid-01` used the same turn-112
checkpoint, packages and turn-122 endpoint as the movement control.
The treatment retained the extra 6,144 Q8 for the single Bakers
Pasture. The native job at 113 chose (18,31). Builder 2359298
reached that tile on 117 with two charges and spent one on the
Pasture at 118. The control built its Pasture on (18,29) at the
same time. The engine handled selection, movement and construction
in both arms.

The treatment's exact Cattle tile was owned and unpillaged with
a Pasture at 122. Native Storekeeper attached from Alexandria
Troas's Bakers district 524295 to City Center 458758 and applied
its Growth effect on all three interior turns 119–121 after the
Pasture was completed. The control had no such activation. The
integrated Builder bid stopped appearing in applied-score telemetry
after activation. Both sessions closed and restored preferences.

This proves that the finite supplier preference can carry a ready
chain through a native job reassignment and into actual Service.
It does not establish a globally optimal amount or retention across
ordinary starts. The existing CE build caps positive Builder bids
at 8,192 Q8, so the 14,336 Q8 total needs a wider bounded CE cap
and a separate test through the main publisher.

Treatment trace SHA-256 is
`50d934e6ae91c3208f10a56ba69f5559612c2e971b6c0b25f3905860bfe13c77`.
The outcome summary SHA-256 is
`498877b3dc5d0badc82296d096e95e0d1793b2f5cebc1b07b45436919fb8a9de`.

### The integrated supplier bid reproduced Storekeeper without a diagnostic hook

`development-alexandria-calibration-01` loaded the same verified
turn-112 save and compared its physical census before autoplay.
Only the CE DLL and three committed CSC AI Lua files differed
from the prior package. The CE review branch `11fc033` widens the
existing positive Builder cap from 32 to 64 utility units and
advertises it through the existing status call. CSC commit
`a9a6741` requests 56 for this ready-chain condition and clamps
it to the advertised cap. The original 32-unit CE still receives
32. The preference is absent when the supplier already works.

The calibrated CE DLL SHA-256 is
`7fbb24a1cbd6eccbe006840cb4dc1878def9fa6d928f2ecfa2be0b42588c750e`.
Its MSVC build and 70 district-score plus four hook-group checks
passed. The eight Lua frontend checks covered the original cap,
the widened cap and removal of the preference after improvement.

The run used stock AI and no external score writer. CE reported
20,480 to 34,816 Q8 for Alexandria's exact Pasture in the first
reported decision interval. The AI built the Bakers Pasture on
118. The same native Growth effect operated on all three interior
turns 119–121. The original integrated-cap control built the other
Pasture. All nine Storekeeper samples and the chunked district
telemetry passed the report audit. This qualifies the integrated
delivery of one calibrated bid on the replay. It still needs
normal-start, multi-chain and duration validation.

### The fresh calibrated game activated one Storekeeper

`development-chain-calibrated-125-01` started a normal Small
Continents game using the calibrated CSC and CE packages. The
terrain signature, leaders, original AI roster and starting units
matched the earlier turn-100 development game. Its earlier
production logs matched through their common window. The
controller issued only normal setup, autoplay and observation.

The main publisher applied 14,336 Q8 on Alexandria Troas's exact
Cattle Pasture in 36 logged reporting intervals, from 81 through
119 with gaps. The AI completed that Pasture on 118. The native
attachment and Growth recipient confirmed six active Storekeeper
turns, 119–124, all for the same Quarter. All 123 required interior
samples were present. No other original-major chain operated.
The turn-125 save shows the Quarter, Mill, Granary and unpillaged
Pasture in place. The controller restored preferences and retired
both temporary packages.

The census had nine completed Bakers Quarters and two unfinished.
Melbourne still lacked only a Wind Mill. Ancyra still lacked its
Mill and Granary despite working Rice. Some other sites lacked
mapped Base or an adjacent customer. The calibrated Builder
preference addresses Alexandria's missing link. The run still
has no matched lower-cap arm through 125, and its six active
turns do not establish long-run retention.

The 125 publications logged 3,442 changed district score calls,
including placement and protection, with up to 173 entries and
none omitted. No optional district sample batch was reported
truncated. The recorded Lua times were coarse, so this is work
volume evidence rather than a mature-empire overhead estimate.

Endpoint SHA-256 is
`bb5280928bc4c47b62f5aa58304bba873d08856aef692b548bbf1b83836d77de`.
Census and result SHA-256 are
`b09d7b77edd1861fce21fe18c7a9a0894f89b51f202add0a83521f1592e9e855` and
`a6722719b4571a5c820568a2603425b4e4881c782b9dbd99f3fcf6331acf7941`.

### Melbourne's available Wind Mill lost the ordinary building nomination

`development-melbourne-wind-mill-01` loaded the exact fresh
turn-125 save and observed it through 134 without score writes.
The UI queue reported the Wind Mill available at load. The
native building comparison called its requirements check and
passed it in all ten recorded choices, including the ordinary
0/0 caller at return RVA `3e160a`. In that ordinary comparison
the Mill had 93,359 Q8 and Amphitheater won with 205,591 Q8.
The native validation of Amphitheater contract 2391 linked
building index 13 to the city log on turn 132.

The other nine choices consisted of seven threat reviews and
two default queue building comparisons. The actual queue
passes accepted Star Fort contract 2119 at 289,297 Q8 on
127 and Commercial Hub contract 2312 at 281,757 Q8 on 131.
They did not reach the default category comparison. Neither
queue pass shows that the Mill could have beaten those offers.
Melbourne still had no Mill at 134. Alexandria independently
kept its Storekeeper active on all eight interior turns.

The follow-up applies 114,688 Q8 to the eligible Mill only at
the ordinary 0/0 comparison, just above the observed 112,232
Q8 gap. This tests nomination and any resulting native offer.
It leaves threat comparison, the later offer refresh and
production arbitration alone. The observer froze with no faults
and restoration passed. Trace SHA-256 is
`6d9c1c139e45a1df6884aa8901cf19837ff2af8fc0bfdcbe76c2a10f9d53e0e9`.

### The Wind Mill nomination changed without carrying its premium into the offer

`development-melbourne-wind-mill-bid-01` repeated the same save
and endpoint. Its only intervention was +114,688 Q8 at the legal
ordinary building comparison. The Mill won at 208,047 Q8. The
original Star Fort and Commercial Hub selections stayed in the
queue. On turn 132 Melbourne submitted the Wind Mill instead of
the Amphitheater, using contract ID 2391 in both arms. The Wind
Mill's native offer passed validation at 93,184 Q8, the whole-unit
value of its 93,359 Q8 cache. Neither arm built the Mill by 134.
Both closed and restored preferences.

The ordinary nomination result in `CheckForUnitOrBuilding`
at `3e1580` is compared with the unit candidate. It then supplies
the chosen item and its unlock facts to the one-use building tree.
The tree independently reads the city-center building cache
through `DecodeTriggerNode::Update` at `55a680` and
`BestExpectedYieldFor` at `3df010`. It shifts Q8 right by eight
for the whole-unit request value. On a later queue refresh,
`UnitRequestContract::Update` at `3fa5e0` calls building
`PresentValueOf` at `3e7e50` and keeps the higher of the stored
offer and current cached value. The non-Wonder city-center cache
is the same row and building index that the selector reads before
its local adjustments. A nomination-only increment therefore
changes which offer exists while leaving its initial and refreshed
valuations to their own native reads.

The matched treatment trace SHA-256 is
`a6eb8eab6a62f1d0e25d175709aab6e8ce4a9d956bb17edb899a5fde1d46510b`.
The turn-134 treatment save carries the Wind Mill offer. Continue
that save to observe its native validation, refresh, and actual
competition at the next queue opening before adding any premium.

### Melbourne executed the Wind Mill offer at its native refreshed value

`development-melbourne-wind-mill-queue-01` resumed the exact
turn-134 treatment save through turn 144, with the same two staged
packages and read-only observation. At the first observed queue
opening, the refresh raised contract 2391 from 93,184 to 141,617
Q8. The native queue accepted that same contract at 141,617 Q8.
The city log records Wind Mill production on turn 135 and
completion on 137. The endpoint census found the working Mill
on Bakers plot 1423 alongside its working Rice Farm and Granary.
Storekeeper was active on all six measured interior turns 138–143.
Alexandria also remained active on turns 135–143.

The matched `development-melbourne-wind-mill-queue-control-01`
continued the untreated turn-134 save through the same endpoint.
At the first queue opening the same contract ID carried Amphitheater
at 406,879 Q8, ahead of the unit and project operands at 79,938
and 73,546 Q8 respectively. Melbourne started Amphitheater on 135
and completed it on 139. Neither Mill nor Storekeeper was present
in Melbourne at 144. Alexandria operated on 135–143 in both arms.
The control's new observer anchor at `3e86d2` captured the
validated offer and its native unit and project competitors. It
was not loaded on the earlier treatment continuation, so its
gate operands cannot be attributed to the Mill choice.

This comparison supports targeting ordinary nomination first
for a city with a ready chain. It does not establish the
economic size of a reusable bid. The 448-unit intervention was
a diagnostic value sized to cross one observed gap.

The source save SHA-256 is
`f1e62184a1533dcf9d99a7e2e71a9ec724048035109cb4034971690e4b41f38c`.
The trace SHA-256 is
`86e23f4ea3ba8197fdcf79133e0ac729c014207ea63acc7ec44705abccc910cf`.
The turn-144 endpoint SHA-256 is
`3c08d207cf2f23f33f0de2626bbd9d1e0e7b98c633743edc793f8fe11829f01f`.
Native exit and controller restoration were verified.

The control source SHA-256 is
`e3b1eb0336089f093610f371bedba62ef8c60d95507916a1f2efba3e4e4552c8`.
Its trace SHA-256 is
`c83d9ac9912043c8ea9a040fa00e5b2e87169c7bb80007eb9ebc4036f8a503ed`.
The control exited normally and restored controller preferences
and package state.

#### Candidate CE nomination boundary

The existing function-entry Runtime hook cannot see individual
effective scores inside `GetBestBuilding` (`3e4710`). The
selector reads and transforms the cached score inline. On the
pinned XP2 reference, the prerequisite checks at `3e49c7` and
`3e49ce` precede the five-byte
`MOVZX R13D, byte ptr [RBP+0x48]` at `3e49d5`. A qualified
call-site adapter could replay that instruction and return to
the untouched signed comparison at `3e49da`. A normal CALL
through a near relay supplies a return address and allows a
Win64 unwind frame. R12D holds the building, R14D the effective
Q8 candidate score and R15 the CityBuild object. The native
frame retains the caller return at `[RBP+0x28]` and the two
flags at `[RBP+0x40]` and `[RBP+0x48]`. The intended scope
is return `3e160a` with flags 0/0.

The adapter places byte validation, relay ownership, instruction-cache
flushing and rollback in CE Runtime. The candidate lookup is generic
and CSC publishes its ready-chain criteria separately. The Windows XP2
reference SHA-256 is
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.

### Integrated CE nomination reproduced Melbourne’s Wind Mill and Service

`development-melbourne-ce-integrated-01` loaded the same turn-125
save and ran through 139 using the shared controller. CE review
commit `abf5d58` provided the native adapter. The main CSC
publisher staged one Mill preference on the ordinary boundary
because Melbourne had a complete Bakers Quarter, working Rice
Farm, an adjacent working Granary and Feudalism. Only the
unbuilt, unlocked Wind Mill qualified in Melbourne. No Frida
attachment or console score write was used.

The turn-133 publication recorded exactly one change in the
previous interval. Melbourne Wind Mill 139 rose from 93,359 to
208,047 Q8. The city submitted the native offer at 364 points
on turn 132, after the same Star Fort and Commercial Hub
commitments as the control. It chose the Mill on 135 and
completed it on 137 at its native refreshed value of 553.2
points in the city log. Melbourne recorded an active Storekeeper
turn on 138. The publisher stopped nominating the Mill once
complete. Alexandria operated on all 13 interior turns in both
arms. No native nomination faults were reported.

`development-melbourne-ce-parity-02` used the exact reviewed DLL
with the original CSC publisher and zero nomination entries.
Melbourne submitted and started Amphitheater under contract 2391,
matching the earlier stock nomination and queue choices. The
full city-build log was byte-identical to the first no-bid replay,
`development-melbourne-ce-parity-01`, on the earlier build of the
adapter. All three runs verified normal exit, controller preferences
and temporary package restoration.

The reviewed release DLL SHA-256 is
`995c93ce33f582638774547303899f35169f17da98a58795123f001ef1f45e7d`.
The integrated endpoint SHA-256 is
`3fde70ee828b6c4fb7d4630766bf4b31cd27744cdcd6553848ad5d7d8d47a613`.
The integrated Lua log SHA-256 is
`8667d3f91ad31e50daab2629724736f82dce5faf1223d195affda67ac91a60b2`.
The reviewed no-bid endpoint SHA-256 is
`feffebcf0c3b488f35add8faee213cc764089f76f912efe5250882530c20c185`.
Both release builds used the existing MSVC solution and pinned
dependencies. The reviewed source passed 74 native checks, four
hook-group checks and the synthetic executable relay test. Eight
Lua checks passed, including unlock, river, presence, material
and cap gates. The 448-unit bid is an initial calibration from
one gap. Fresh starts, other ready sites, Water Mill follow-through
and mature-game overhead remain to be measured.

At the integrated endpoint, Ancyra still needed both a Mill and
the Granary despite its working Rice Farm. Charleston had built
the Water Mill and Granary and had Feudalism. Its adjacent Maize
still had no Farm. These are separate next checks for customer
nomination and supplier follow-through.

### Granary exchange resolves the receiving player's building replacement

CSC attaches the Granary-to-Mill exchange modifiers to the Granary and
explicitly copies those source attachments to registered Granary replacements.
The Mill-to-Granary Food modifier and the functioning-Granary requirement
both name the base Granary in SQL. In patched Windows XP2, the native
`CityHasBuilding::Test` at `832c30` takes the subject city's owner and
resolves the configured index through its player-city replacement table
before testing presence and pillage. `AdjustBuildingYieldChange::Apply`
at `871f30` resolves the configured recipient index through the same
table before calling the building yield-change function. The
replacement override writer at `264110` confirms the table at
offset `0x150` in the player-city object. This is static evidence
for the requirement and recipient directions. A live replacement
case is still needed to verify the exchange and Service together.
The standalone replay's gameplay database has no Granary replacements.
The addresses are RVAs in the Windows XP2 reference with SHA-256
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.

### Ancyra's legal Granary lost nomination and a military contract took production

`development-ancyra-granary-01` continued the exact integrated
Melbourne endpoint from 139 through 150. Ancyra (player 1,
city 131073) had a completed Quarter at 1430, the adjacent
working Rice Farm, Feudalism and no Mill or Granary. The UI
reported the ordinary Granary legal. The read-only observer
recorded both ordinary `3e160a` comparisons reaching the Granary
with requirements satisfied.

| Ordinary comparison | Granary Q8 | Castle Q8 | Gap Q8 | Native offer |
| --- | ---: | ---: | ---: | --- |
| First | 21,982 | 170,016 | 148,034 | Castle 2638 on turn 142 |
| Second | 35,144 | 155,988 | 120,844 | Castle 2840 on turn 149 |

The only observed production opening had Cuirassier contract
2783 at 266,496 Q8. It passed the native unit and project
comparison at 72,258 and 74,045 Q8 respectively, then executed.
The best-building fallback evaluation in that pass gave Granary
71,623 Q8 and Castle 260,128 Q8. No Granary offer competed at
the contract gate. Ancyra still lacked both buildings at 150.
Alexandria and Melbourne each kept Storekeeper active throughout
all ten measured interior turns 140–149.

The two nomination margins describe competition with Castle in
this city. They do not price the marginal CSC value of a Granary
when the Mill is also missing. The endpoint contains a separate
Trebizond case where the Water Mill completed on 148 and the
adjacent Granary is still missing. The Maize supplier in Charleston
and the Wheat supplier in Trebizond remain unimproved.

The Ancyra trace SHA-256 is
`a2b708b78f08826a051ed180299ebbf45356634a32a1b8204ba91038e4f59a16`.
The turn-150 endpoint SHA-256 is
`1c6a36651a77d2361d06d651856eac8c57d6de921e2aede0fa4fca2d146f8843`.
The observer froze without a fault and the shared controller
verified native exit and restoration.

### Trebizond's working Mill gave a closer Granary comparison

`development-trebizond-granary-01` resumed the turn-150 Ancyra
endpoint through 164. Trebizond (player 1, city 327684) already
had the Water Mill at Bakers plot 914, Feudalism and a legal
Granary at its adjacent City Center. Wheat 913 was still
unimproved, so the Granary could start the ordinary exchange
before the Storekeeper conditions were complete.

The only observed ordinary Granary nomination reached
the native comparison at 46,458 Q8. Library won at 119,277
Q8 and became offer 3238 on turn 163. The earlier production
openings accepted Star Fort 2837 and Theater Square 3015,
with Theater Square still occupying production at the endpoint.
There was no Granary offer or building in this arm. Alexandria
and Melbourne each recorded all 13 measured interior Service
turns, 151–163.

The trace SHA-256 is
`b3ee8ef811ad754b997d489aa2d8e441601ea403c1a7bb04a1d5d1be5bc3c9a0`.
The control's endpoint SHA-256 is
`8b72d11fdf220b059504c61c7dba82dc7a9f118a8a73ef77f92edf6f3f2293eb`.
The trace froze without a fault and the shared controller
verified native exit and restoration. A one-shot diagnostic
adds 73,728 Q8 to the same legal ordinary comparison, just
above the observed gap of 72,819 Q8. This tests nomination
before considering the economic size of a general policy.

For the first reusable preference, isolate the ordinary
exchange with a working Mill. The real Granary gains one Food,
and the Mill gains one Production and one Gold. Storekeeper
growth and Engineer points depend on the separate working
material and civic conditions. With no Mill, as in Ancyra,
value depends on when and whether the complementary
investment can complete.

The native `BuildingValue` routine at `52b900` reads live
yield changes for the candidate's index and separately evaluates
the modifier vector indexed by that same building. The incoming
Food modifier belongs to the Mill and requires an existing
functioning Granary. Those two inputs do not by themselves
forecast that incoming Food when the Granary is absent. The
Granary-owned Production and Gold roots can enter the second
input. Their delivered native credit at this site remains to be
measured before adding a preference for any of those yields.

### A matched Trebizond nomination produced a valid Granary offer

`development-trebizond-granary-bid-01` loaded the same turn-150
checkpoint, packages and endpoint. The one-shot diagnostic
matched the ordinary caller, a legal Granary and the observed
46,458 Q8 candidate. Its 73,728 Q8 addition gave 120,186 Q8
at nomination. The city submitted Granary under the control's
contract ID 3238 on turn 163. That offer validated at 46,336
Q8, or 181 whole score units, from the unchanged native
building cache. Star Fort and Theater Square had already
taken the same slots as in the control.

At 164 the UI still reported Granary available and absent, and
the Water Mill still read zero Food, Production and Gold.
The Theater Square was in progress. The replay establishes
nomination and offer admission. It does not yet establish
production, exchange or Service in Trebizond. Alexandria and
Melbourne kept their Storekeeper effects throughout the same
13 interior turns as in the control. Controller restoration
and native exit were verified.

The treatment trace SHA-256 is
`ec19582e00f5606771d3e9c2f10e0fbb50c721cfdea57bf537782757480c787e`.
The treatment endpoint SHA-256 is
`2ae1ca1bb49d4814acddd1c98d200a87baaddbf40d5b32ee55d63ad42a3b7a43`.
The continuation of that endpoint uses read-only observation
to check refresh, native production competition and actual yields.

### Trebizond bought the Granary through the admitted contract

`development-trebizond-granary-queue-01` ran the treatment endpoint
from 164 through 178 with no further adjustment. The city log reports
`PURCHASE` for Granary contract 3238 on turn 164. The two observed
production openings instead took Library 3299 on turn 170 and
Encampment 3484 on 173. At 178 the Granary was working at plot 988,
but the Water Mill was pillaged. The UI showed the Granary's base
one Food and no Mill exchange yields. That late snapshot cannot
establish whether the exchange operated before the damage.

The patched XP2 `UnitRequestContract::Execute` at `3f8850` has
a separate purchase path. Its building branch calls
`Economic::TryPurchaseBuilding` at `458d00`. That function
checks construction eligibility, compares the city's current
building present value with a normalized Gold cost threshold,
then checks spending limits and runs the ordinary purchase
command. The successful branch marks the contract and logs the
purchase. The static path explains why a nominal building
contract can complete without a production-queue selection.
The actual Gold cost and threshold operands were not captured.

The continuation trace SHA-256 is
`586a4c80adf35901fe6017dff282017be8c74123ce53e02eb92652000e393c7b`.
The endpoint SHA-256 is
`59bdb4ff4cea1d24994fee2f2bb7e84368b05cbbe55e89a7a05d5af1cca61041`.
The controller verified normal exit and restoration.

### The purchased Granary delivered the ordinary exchange before the Mill was damaged

`development-trebizond-granary-exchange-01` repeated the same
turn-164 save with no adjustment and stopped on 167. The UI
reported two Food at the Granary against its database base of one.
The Water Mill delivered one Production and one Gold, both up from
zero at the source. This confirms the reciprocal exchange after
the native Granary purchase. No Storekeeper effect was measured
in Trebizond. The ordinary exchange and the material-gated Service
are separate outcomes.

The endpoint yield receipt SHA-256 is
`94e1bf0bd7c3f210ed137d17da83c38585ec799c82a9a7fc437ecdccaa203d73a`.
The later checkpoint file timed out. The yield receipt and native
purchase log were already captured, and the controller verified
normal exit and restoration. This arm supplies no reusable
turn-167 save or full endpoint census.

### Charleston activated a third Storekeeper after a farm bid

In the same 164–178 continuation, Charleston already had
Feudalism, a working Water Mill on Bakers plot 2025 and the
adjacent Granary. Its Maize at 2100 was unimproved at the
start. The turn-176 publication reported the preceding CE
Farm bid on 2100, priced from 58,005 to 72,341 Q8. The
endpoint census showed the working Maize Farm, and the
Storekeeper watcher verified operation on 176–177.
Alexandria and Melbourne each operated on every measured
turn 165–177. The new chain is evidence of follow-through
from the existing supplier policy on another resource and
city. There is no matched no-bid arm for Charleston, so the
bid's causal effect is still unmeasured in this case.

### Native Granary valuation priced Food and returned zero for the exchange roots

`development-trebizond-granary-components-01` observed the
turn-150 source through 154 with no score adjustment. It captured
four native `BuildingValue` calls for Granary 3. The working
Water Mill and available, unbuilt Granary were verified in the
source. All four Granary-owned Mill Production and Gold roots
were accepted in all four calls. Their accumulators returned
zero and the modifier subtotal was zero. No child was observed
under these roots. This is a missing forecast contribution in
the sampled context.

The existing one Food passed the intrinsic yield normalizer at
`52b110` from caller return `52bb71`, yielding 383–395 Q8
per turn. The income calls at `528310`, with caller returns
`52c3ad` and `52c3cd`, priced the start at 12 turns and horizon
at 50. The ratio of the horizon-minus-start result to the same
income input was about 12.06. Multiplying that factor by the
normalized Food gives 4,618–4,762 Q8, about 18–19 nomination
score units as a first approximation. This extrapolates from
the actual native stream and allows for rounding. It does not
value Production, Gold or future Storekeeper.

The initial CSC preference is 4,608 Q8 for a legal, missing
Granary beside a working Mill. It prices the incoming Food only,
and the existing CE nomination channel applies it after native
eligibility. CSC asks the UI queue which ordinary or unique
Granary variant is legal. It leaves the actual purchase and
production comparisons to their native valuations. Mill repair,
missing producers and future Storekeeper require separate
valuations. The 18-unit calibration is from one city.

The native trace SHA-256 is
`54c09a4b9e96ee23e2fbf07dcbeb6efa979f26607fa3b09cbd0010a63389fd8d`.
The short replay verified normal exit and restoration.

### The first integrated Granary replay did not reach the native comparison

`development-trebizond-granary-food-ce-01` published the 18-unit
policy while the Frida selector observer was attached. CSC reported
one nomination entry at 150 and two from 151. CE recorded zero
changes and zero faults. The captured selector trace is
byte-identical to the original control, and Trebizond again
submitted Library 3238. This provides no evidence of the 18-point
bid's effect on the competition.

CE's adapter uses the native frame's return address to identify
the ordinary caller. The observer installs an exit callback on
that same function. A clean replay using CE's own telemetry and
bounded packet-key logging will distinguish an observer
interaction from a publication or eligibility failure.
The replay verified normal exit and restoration.

### The clean replay applied the calibrated Granary Food bid

`development-trebizond-granary-food-ce-02` used the same
turn-150 source, reviewed CE binary and 18-point policy
through 164. It added a bounded log of packet keys and used
CE's own telemetry with no Frida attachment. The packet
contained player 1, city 327684, building 3, delta 4,608 Q8.
At turn 164 CE reported one change in the preceding interval,
from 46,458 to 51,066 Q8 for that exact key. The same Library
offer 3238 was submitted on turn 163. The matched selector
control had Library at 119,277 Q8. No Granary or exchange
was present at the endpoint.

The result confirms delivery and retention of the competing
choice in this fixture. It also explains the earlier observer
interaction. The pinned Frida implementation substitutes an
exit trampoline for the return address on the selector's stack.
CE's native caller guard reads that address to admit only the
ordinary nomination. Use CE telemetry alone when qualifying
this carrier. [Frida Gum 17.24.3 return-address replacement](https://github.com/frida/frida-gum/blob/17.24.3/gum/guminterceptor.c#L2111-L2114).

The clean Lua log SHA-256 is
`6241fbfca8ed3aea41bce132f07b5388ff4535ed9890302b617ad2342d4ddbbb`.
Its endpoint save SHA-256 is
`98e8b2de316db76208b4881d40934fa548628ddd74be0b737340e2436ab9e200`.
The controller verified normal exit and restoration.

### Native player weights calibrate the full ordinary Granary exchange

`development-trebizond-granary-components-02` repeated the
read-only turn-150 to 154 component window. The probe first
identified the player valuation object in Trebizond's Granary
`BuildingValue` call. It captured 16 positive Production inputs
and 16 Gold inputs from other ordinary building yield calls
through `52bb71` that used that same player object. These
calls establish each native normalization weight independently
of the reference buildings' own scores or build dates.

One Production normalized to 370.2–370.9 Q8 and one Gold to
370.7–371.0 Q8, using the observed output-to-input ratios.
Using the Granary's measured 12.06 stream factor gives about
17.5 score units each for Production and Gold. CSC rounds the
three exchange terms down to 18 + 17 + 17, or 13,312 Q8.
This first full exchange bid applies to a legal, missing
customer next to a working Mill. The Water Mill and Granary
exchange was observed directly. Future material, producer
and Service benefits require separate pricing.

The second component trace SHA-256 is
`a027ae84d49cd25db10835723befce194a00162ab92c8fe9d9face5c93231a3b`.
The controller verified normal exit and restoration.

### The full exchange bid reached Trebizond and preserved the Library choice

`development-trebizond-granary-exchange-ce-01` used the same
turn-150 checkpoint through 164 with the rounded 52-point CSC
policy. The reviewed CE package was unchanged. CE's own telemetry
reported player 1, city 327684, building 3 changing from 46,458
to 59,770 Q8 in the interval ending at 164. The city still
submitted Library contract 3238 on 163. The run verified the
larger bid's delivery with no external attachment. The choice
remained consistent with the control in this opening.

The passive gameplay milestone watcher emitted complete physical
dependency censuses at turns 153 and 160 during autoplay. Both
were archived separately from the continuous Storekeeper audit.
This verifies the observer path for longer runs without stopping
the game at each milestone.

The integrated Lua log SHA-256 is
`553e6dc4cbcc615231b9a6ac1b1ea1815b0b82535151c26ee87d30fd16b11998`.
The milestone receipts have SHA-256 values
`2fad43c04f664ffc8b8542a108deb9b6543dc59442e21558332f4bed5fe4a2d4`
and `8170a18ae2e541696d7fb7042504c87e530086b57d812cbe4575f2aad9f57a38`.
The controller verified normal exit and restoration.

### Melbourne bought its Mill in the ordinary-start development run

`development-ordinary-exchange-249-01` used the earlier Small Continents
development seeds and the integrated 52-point Granary exchange policy.
The separate CSC and CE packages loaded on turn one. The stock AI
researched and played under shared-controller autoplay. No qualification
seed or external score writer was used.

At turn 100, the census had eight Bakers Quarters, six complete, with
Feudalism unlocked by all five original AI majors. Melbourne's Rice Farm
and Granary worked, and only the Wind Mill was missing. The 448-point
Mill preference reached the nomination scorer in the interval reported
on 97 and the city had submitted Wind Mill offer 1521 on 96. Production
went to a Knight on 97 and an Industrial Zone on 102.

The next observed nomination receipts included a score change from
50,366 to 165,054 Q8 in the interval reported on 111. Melbourne
submitted Wind Mill offer 1907 on 110. The native city log records its
purchase on 113. From 114, the native Storekeeper observer confirmed
the active attachment and Growth recipient. The continuously sampled
clock had no gaps from 2 through 154. Melbourne operated on 114–154,
the only original-major Bakers chain confirmed in that window.

At 150, 14 of 15 Quarters were complete. Six of those 14 lacked
an adjacent mapped Base deposit, an adjacent City Center customer
footprint, or both. Six more had both types of neighbor and multiple
unfinished links. Aigai (player 2, city 196610, Quarter 2311)
had a working Water Mill and Granary, but its sole Cattle at
(18,31) still lacked a Pasture.
The same 14,336 Q8 supplier preference reached the scorer repeatedly,
including all reporting intervals 100–155. Aigai's ordinary
improvement trees logged five other reservation locations in 100–159.
These records establish scoring and competing reservations. They
leave the reason the Cattle missed admission unresolved.

Heidelberg opened a second chain. Its Quarter was still unfinished
at 150, with no Mill, Granary or improved Maize. The production
ledger shows Granary finishing on 158, Quarter on 163 and Water
Mill on 174. The improvement tree was already reserving the Maize
at (59,17) by 172, before the Mill finished and the final-link Farm
preference became applicable. The tree reached the tile on 177
and the native Water Mill attachment and Growth recipient first
operated on 178. This is an observed multi-link sequence. Its
activation was too late for 100 active turns within this window.
Storekeeper dropped out on 184–186. On 185, Heidelberg's ordinary
improvement tree reached the same Maize tile and logged a successful
Farm repair. The original Quarter and its City Center regained
the native Growth effect on 187. The logs do not identify the
source of the damage or isolate a contribution from the bid.

Launceston bought Water Mill offer 3781 on 181. In the next
nomination interval, the 52-point exchange bid changed the
Granary candidate for player 4, city 458758, from 78,805 to
92,117 Q8. The city submitted Granary offer 3903 on 182 and
bought it on 188. Its native Storekeeper attachment and Growth
recipient first operated on 189. This is the first ordinary-start
follow-through for the full exchange bid. The run has no matched
control for this city, so the sequence does not prove that its
nomination would have lost without the bid.

The earlier calibrated game built Alexandria's Pasture on 118. This
game used newer packages and reached a different live state. A replay
of the current decision window can separate ranking, reservation,
assignment and movement without changing the preference first.
The preserved `diagnostic-AutoSave_0154.Civ6Save` SHA-256 is
`8dff282a47f0137be39baa99c1c15f1e1897128c4d8f8badd2d4f981dd349b8d`.
The development evidence is under
`Desktop/Codex/csc-bakers-qualification-20261107`.

### One of four development chains reached 100 active turns

The normal-start game reached the inactive turn-249 boundary and
closed with verified preference and package restoration. All four
milestone censuses completed. The strict effect audit found every
interior sample from 2 to 248, with no ambiguous attribution.
The endpoint had 24 Bakers Quarters, 22 complete.

| Chain | First active | Active ranges | Cumulative turns |
| --- | ---: | --- | ---: |
| Melbourne | 114 | 114–238, 242–248 | 132 |
| Launceston | 189 | 189–248 | 60 |
| Magdeburg | 214 | 214–248 | 35 |
| Heidelberg | 178 | 178–183, 187–206 | 26 |

Melbourne had no Farm on its Rice at the turn-240 census. Its
Wind Mill and Granary were working. The CE receipt for the
interval reported on 240 raised the exact Farm from 18,012 to
32,348 Q8, and the improvement tree reserved that tile on 239.
The tree reached the Rice on (18,20) and built a Farm on 241.
The native attachment and Growth recipient resumed on 242, and
the endpoint census confirmed the working Rice Farm on the same tile.

Heidelberg lost its only adjacent Base deposit when Dam contract
4536 took (59,17). The census found a working Maize Farm there on
200 and a Dam with no resource there on 240 and 249. Contract 4536
was submitted on 202 and entered the city queue on 206. The native
Service stopped on 207. In the CE score batch for policy version
202, the Dam on that tile fell from 482,672 to 458,096 Q8.
The 24,576 Q8 deduction reached the exact pair and the district
still went forward. The evidence leaves the other Dam sites and
downstream arbitration unresolved. A permanent-loss guard needs to
account for alternate legal sites and any competing flood benefit.
The six-neighbor censuses at 200 and 249 show that Heidelberg owned
every adjacent plot and had no other mapped Base. Once the Dam removed
Maize, buying a tile or assigning another Builder could not restore
this Quarter's chain from those remaining neighbors.

In the Windows XP2 reference, `FloodRiver` at RVA `72d400` scans
the affected river's floodplain plots for the district marked as
preventing floods. It checks completion and pillage state before
suppressing damage. `GetFloodPreventionDistrict` at `72e130` reads
that flag from the district definition. The shipped Dam definition
has `PreventsFloods` and `OnePerRiver`. Compare same-river flood
coverage using the native lists from `GetRiverForFloodplain`
(`5bcd70` Lua binding) and `GetFloodplainPlots` (`5bc970` Lua binding).
Equal flood coverage leaves placement legality, Production, housing,
and any other location effects to check separately.

The follow-up observer reads the Dam's score on each currently
surveyed candidate after `GetBestDistrict` returns to `CheckForDistrict`
at `3e0f3c`. It reads the engine's selected district and coordinates
there. The survey separately calls the UI's native district build
operation for every candidate at the saved boundary. Offline fixtures
verified same-river and different-river coverage, occupied and rejected
sites, and decoding of the native score snapshot. These checks do not
establish whether Heidelberg has an alternative in a live game.

At 200, Aigai's Water Mill was pillaged and its Cattle was
still unimproved. Both were unchanged at 249. The preserved
turn-154 save samples the earlier decision window before that
second missing link.

The first read-only follow-up, `development-alexandria-autosave-154-observe-01`,
loaded the exact rotating autosave. The native return player was still
AI-controlled and the game advanced from 154 to 155 while the shared
controller checked readiness. The controller rejected the handoff before
installing the observer and then closed and restored the packages.
This yielded no ranking evidence. Use an inactive turn boundary in a
same-seed development start to obtain a verifiable observation source.

The endpoint save SHA-256 is
`4d38825b47b95567ffcd3e14a62b8842c4d6ea07af99849443bf5f749d6e21c4`.
The Lua and behaviour-tree logs are
`a9e19e99d49741815f3b804c30f60b42554f0f0314db1c0d84fd9e69d8cb3ba8`
and `449749615a77f50c84e210794968c0df8d94f65c3aec7c1d8bedbf4f581f7127`.
This was a development game with no matched control. The
preselected validation seeds remained unused.

### The same development setup produced different Pasture follow-through

`development-alexandria-fresh-154-observe-01` used the same
seed, packages, map fingerprint, original AI roster, leaders and
starting units. Native city production records diverged by turn 55.
The original long run's exact Quarter was in Aigai, as confirmed
by its placement tree at (17,31) and completed Bakers contract.
The new run called the matching player, city and Quarter site
Alexandria Troas. Use player and plot identifiers when comparing
the branches. The two branches are not a controlled bid comparison.

The new run applied the same 14,336 Q8 preference to the Cattle
Pasture. Its ordinary tree first reserved the exact tile on 82.
The tree submitted a Builder request after failing to find an
available unit on 109, when it admitted the Pasture again. A Builder
reached the plot and constructed the Pasture on 118. Native
Storekeeper operated on every interior sample from 119 to 153.
The turn-154 physical census confirmed all four links. The
diagnostic guard correctly skipped the native observer because the
expected missing Pasture was already working. The controller
closed and restored the session.

The archived Lua log SHA-256 is
`19273b1b996e35a28623612bd859145a716db27d9cd30153af8ae9a34a6f605e`.
The behaviour-tree log and boundary census are
`6d121b16452086b6d7374be678121b658a42bb508a9185aced43e286f1da2f30`
and `0f04b44e02e322137aad8bb1ef2ff47ad38c9ea79c4e7ccc4a5683afb04c5c77`.
A same-policy observation window starting on 105 can capture the
second admission and follow-through. Increasing the bid would
change the diagnostic before we know why the branches differed.

### Builder recruitment and movement are separate decisions

In the Windows XP2 reference, `FindAvailableUnitNode::Update` at
RVA `554b10` checks units already controlled by the behavior. It
can then call `Control::Manager::RecruitUnits` at `403190` with
the control identity, effective request priority and a selection
callback. The manager filters the empire's units before invoking
that callback. In the inspected typed-target branch,
`FindUnitsEvaluator::ChooseUnitsFrom` at `553570` selects by
requested type priority, then shortest plot distance at equal
priority. Plot distance is not a movement-path proof.

`RecruitUnits` builds its first candidate pool only from units with
`m_aiController == -1`, `m_bProcessedTurn == false` and
`m_bDelayedDeath == false`. Its second pool comes from a signal
request using the requested priority and control identity. That pool
still checks the two Boolean fields. The archived names and offsets
are explicit in the unit constructors at RVAs `39b140`, `66bf0`
and `66180`, respectively `0x300`, `0x258` and `0x2e8` in the
unit object. These are recruitment filters. They do not show which
one affected Melbourne's nearby Builder.

The Ghidra reference SHA-256 is
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
The loaded hotfix was
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
Their `.text` sections matched byte for byte and the callback table
entry at RVA `a0ce08` pointed to `180553570` in both files.
This separates existing-unit recruitment from city production and
later movement. It leaves the failed availability checks in a
particular job to be traced at runtime.

### The Pasture won open admissions and waited for a Builder

`development-alexandria-fresh-105-observe-01` used the same
integrated packages and the same 14,336 Q8 Pasture preference.
At the verified inactive turn-105 boundary, player 2 city 196610
had Feudalism, the working Water Mill and Granary, and the bare
Cattle at (18,31). The native observer watched 105–120 without
an external score write.

Of 15 ordinary proposal checks, 11 found an existing improvement
tree. In the first three open checks the selector chose the exact
Pasture at 34,995, 34,906 and 34,785 Q8. Each opened a new
ordinary job. At the fourth open check, after the supplier was
complete, the city chose a different improvement.

The city reserved the Cattle on 107, 109 and 113. On 109, the
native Find Available Unit node failed and the tree submitted
a Builder request at 136. Both of Macedonia's Builders still
had charges in that turn's independent census. The logs do not
identify the specific recruitment filter that rejected each unit.
Builder 2359298 reached the Cattle on 117 with two charges, used
one to build the Pasture on 118, and remained a live unit.
Native Storekeeper operated on 119.

The inactive source save SHA-256 is
`dfc29fce2c25bb717bc3a2374640a37accc4052d0fd7989b753479153f1f83cd`.
The frozen native trace had no faults or active frames, SHA-256
`5bbe47b3446a0c01bb8d1afc7c430c2770957e529631e158314f462fbd0c7440`.
The controller reached 120, saved and closed cleanly. The first
summary rejected the missing Storekeeper sample at the deliberate
105 pause. The recovered audit verified every other interior
clock and recorded 105 as unsampled. Qualification continues to
require an uninterrupted sample range.
This identifies the bottleneck in the successful branch after
admission. Aigai's divergent branch remains a separate ranking
and scheduling comparison.

The same 105 checkpoint holds Melbourne's completed inland
Quarter at 1423, working Granary and Rice Farm, and absent
Wind Mill with Machinery unlocked. For the opening-investment
test, remove the Farm in a shared diagnostic preparation and
verify the remaining world facts before comparing arms. Measure
whether the unbuilt Mill's forecast credits the immediate
Granary exchange before setting a bid. This isolates the case
where the supplier policy waits for the Mill while the Mill
policy waits for working supply.

### Native forecasts read existing yield changes for the candidate building

The Ghidra reference's `BuildingValue` at RVA `52b900` first
normalizes its definition's intrinsic yield rows. The return
address of that normalization is `52bb71`. A separate loop
then enumerates yield definitions and asks the city's building
collection for the exact candidate building's yield change.
It calls `CityBuildings::GetYieldChange` at `10c0e0`, with
return address `52bd7f`. Positive amounts are normalized via
the distinct return address `52bda1` and enter the income
subtotal before the discount stream. These call encodings were
confirmed on the loaded Steam hotfix, SHA-256
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.

An empty intrinsic row set therefore leaves the dynamic path
available. The separate prospective modifier analysis still
needs its own receipt. The opening probe measures both paths for
Melbourne's Wind Mill, keeping the working Granary and removing
only the Rice Farm from the replay copy.

### Melbourne's opening forecast already credits Production and Gold

The first opening replay verified the source census, removed only
the Rice Farm and confirmed that Melbourne could build the Wind
Mill. The new observer profile was missing from the shared
recorder's allowlist. The replay closed before collecting forecast
data. The corrected profile accepts only player 4, city 131073
and Wind Mill index 139, with the existing scoped bounds.

`development-melbourne-opening-components-02` reloaded the
same verified source, prepared the same change and saved the
inactive turn-105 state for a matched comparison. The surrounding
census was identical except for removal of the Farm on Rice
plot 1498. Melbourne retained its working Granary and complete
Quarter. The legal Wind Mill remained unbuilt.

All seven Wind Mill forecasts from 105–112 read +1 Production
and +1 Gold through the existing city building-yield path.
Those terms normalized to 371 and 217 Q8 respectively. The
dynamic Food entry was zero. The Mill's prospective Food-to-Granary
root, `MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER`, also
returned zero in every forecast. The distinct material and
Storekeeper roots returned zero in this missing-supplier state.

Same-player reference normalization gave 383 Q8 per Food. The
observed 12-to-50-turn stream changed from 8,352 to 19,464 Q8
for input 922 Q8. Applying its marginal factor of about 12.05
to one Food gives an approximate 18.0 utility points. It would
double-count benefits to add the full Granary-side 52-point
preference to this Mill forecast.

The first ordinary opening compared the legal Mill at 44,739 Q8
with Castle at 115,453. Across the captured comparisons, the
gap was 30,902–71,830 Q8. A Food-only correction of 4,608 Q8
would leave Castle ahead in each observed comparison. No bid
was applied. Value the credible chain completion and its costs
separately before deciding whether to favor this opening.

The prepared save SHA-256 is
`233f30e7130343771e59272b526ab8d43642104c2fd175ba7f6ed6f708184cae`.
The fault-free trace SHA-256 is
`78005bfa9f8bc2d179fccf558d9e044dc4bb75e71754d32e9c7c4ebcda766d32`.
Both replays closed and restored the original packages and preferences.

The native child analyzers offer a way to price Storekeeper if
the chain can credibly become ready. The city-growth analyzer
at RVA `46fac0` uses the recipient's Food surplus when city
context exists and normalizes the resulting Food with a null
player context before discounting the timed stream. Its missing
city branch uses a separate fallback. The district Great Person
analyzer at `47b3f0` normalizes the configured Great Person type
as a player-weighted pseudo-yield and then discounts it. Its
default routine at `47b4c0` applies a different amount scaling.
The inspected code belongs to the byte-matched XP2 Ghidra
reference. These are child capabilities. Melbourne's missing
supplier kept the prospective Storekeeper roots at zero, so
this capture did not price actual Storekeeper.

#### Pricing the opening with the missing Farm

`development-melbourne-opening-components-03` repeated the prepared
opening without a score write. At the inactive turn-105 boundary the
city reported a Food surplus of 9, 45 Production for a new Builder,
and 40 Production for the Mill. Australia's census found one Builder
with one charge, at `(17, 20)`, adjacent to the Rice. The census alone
cannot establish availability to Melbourne's improvement tree.

Sixteen positive reference calls used Australia's player context, the
verified Engineer pseudo-yield index 4 and diplomatic context `-1`.
Each gave 230 Q8 per Engineer point. Seven observed Mill forecasts
reproduced the income window and about 12.05 marginal discount factor.
Using the measured surplus and the native growth analyzer's 10% rate
gives about 10.6 utility points of Growth. One Engineer point adds
about 10.8 points under the same window. These are calibrated proxy
values. The blocked Storekeeper roots did not return those values.

Under an optimistic scenario where the Farm is ready and worked when
the Mill opens and Storekeeper starts at once, the missing effects
sum to about 85 utility points at the observed weights and Food surplus.
That includes the outgoing Granary Food, Farm-to-Mill Food, the Farm's
CSC Production and Gold, Growth and Engineer points. It excludes the
Granary-to-Mill Production and Gold that the forecast already credits,
and ordinary Farm output outside the CSC exchange. Castle led by about
121–281 points across the captured comparisons. At these weights the
measured gap does not justify raising the Mill above Castle. Delay and
scarce Builder time reduce the expected value further. A fresh Builder's
45 Production across three initial charges gives 15 Production per
charge as a replacement-cost yardstick, with travel and other work still
to consider. Those costs were not subtracted from the utility estimate.

The frozen trace has no fault and SHA-256
`bf14fc43cc373dc6a9025b519012fb4b5985200fa33b5377f4985af630dd2e6a`.
The controller closed at 112 and verified package and preference restoration.

### Melbourne reserved the Rice Farm and could not recruit a Builder

In the same `-02` diagnostic, Melbourne's ordinary improvement tree
selected a Farm at its displayed value of 300 on turn 106. It reserved
coordinates `(18, 20)`, the bare Rice at plot 1498. `Find Available Unit`
then failed on every logged turn from 106 through 111. The tree's Builder
contract 1731 was submitted to six Australian cities including Melbourne.
The city build log contains those submissions and no later event for that
contract in the captured interval. The Rice remained bare at 112. CSC's
ready-chain preference did not nominate Melbourne's job with its Mill
missing. No diagnostic bid was applied.

The `-03` repeat reserved the same tile on 106 and reproduced all six
failed recruitment checks. Its starting census places the charged
Builder next to the Rice. The native trace also shows Melbourne
accepted contract 1731 on receipt at 76,800 Q8 (300 points). Melbourne
stayed on Kōtoku-in from 105 through 111 and the trace saw no native
queue comparison there. Its improvement tree logged the eight-turn
contract wait from 107 through 111. Other cities that logged the submission started
Castle, an Encampment or a Dam after finishing their previous builds. The existing
trace was scoped to Melbourne. It cannot distinguish a later invalid
offer in those cities from an eligible offer that lost the comparison.

Trace recruitment eligibility for the nearby Builder and follow the
existing offer across candidate cities through their next production
openings. The existing unit request observer has verified native entry
points for initialization, city validation and execution. Join those
events to the city log by player and contract ID.
[Unit request observation](csc-ai-native-contract-observation-20261028.md).

The unavailable unit and later city queue competition remain separate
questions. The trace establishes initial city acceptance for Melbourne.

#### The Rice Builder offer lost across Australian cities

`development-melbourne-builder-offers-01` used the same prepared
turn-105 setup and observed all six Australian cities through turn 116.
All six passed receipt validation for the Rice Farm's Builder offer
1731 at 76,800 Q8 (300 points). It passed validation again in nine
queue openings. The refresh left it at 76,800 Q8 every time. Each
opening executed a higher-valued offer. Melbourne itself eventually
reopened its queue on 114 and executed a Campus offer at 387,898 Q8.
The Rice job logged the eighth turn of its wait on that same turn.

The closest comparison was Adelaide. Its next build accepted another
Builder offer, 1791, at 94,976 Q8 (371 points). Sydney's improvement
tree requested it for the Farm at `(18, 26)`. Adelaide queued the unit
on 112 and it was still in production on 115. Melbourne's Rice was
still bare at 116. The other winners led
1731 by about 394–1,893 points. These are refreshed city offer values.
They price separate requests and must be distinguished from recruitment
priority, the unit's Production cost and the earlier building ranking.
The measured route reached cross-city production competition while the
request was still valid. These results do not support a longer deadline
or a broad Builder preference as the first intervention in this case.

The read-only trace froze with zero active frames and no fault.
The controller verified normal exit and restored the original packages
and preferences. The trace SHA-256 is
`376a381e67be12d28bd3984440da73780f72054b8d4f2379416ccd07c342a4fa`.

#### The first Rice recruitment found the nearby Builder already busy

`development-melbourne-builder-recruitment-01` observed the exact
Rice target `(18, 20)`. On turn 106 the recruitment request used
priority 2 and controller 24707087. Australia's one Builder, 2752514,
was still at `(17, 20)` with controller 24772611 and the processed-turn
flag set. It was alive. The call did not offer the Builder to the
evaluator and left its controller unchanged. The opening census had
confirmed one charge. The live observation identifies the failed
eligibility checks for this call and leaves the existing controller's
job to be identified. The behavior log shows Sydney found a Builder
for a Farm at `(19, 22)` earlier that turn, but it does not print the
unit identity.

The probe stopped recording later in the replay when it attempted to
read a null unit slot after an unsuccessful evaluator call. The native
typed evaluator can leave one slot with a null pointer when no unit
matches. The corrected observer reads the result vector only after a
successful return. The game reached 116 and the controller verified
clean closure. The incomplete trace preserves the complete first
roster snapshot. It did not retain the evaluator call from that first
check. Its SHA-256 is
`699ce91f6ba5bfa8ca10fc3b438ed466d5b7b68d973d4603a60605f6f7899f3d`.

`development-melbourne-builder-recruitment-02` reproduced the queue
result and joined the nearby Builder to its actual jobs. On 106
Sydney recruited Builder 2752514 from Canberra's earlier controller
and moved it toward `(19, 22)`. By Melbourne's check it had already
processed the turn. It repaired Sydney's Farm on 108, then became
unassigned with the processed flag still set. On 109 Canberra took it
again, for the Outback Station at `(12, 13)`. The unit reached the tile
on 114, built the improvement on 115 and was marked for removal.
The turn-116 census found no Australian Builder and Melbourne's Rice
still bare. Adelaide's new Builder remained in production.

The corrected trace captured all ten Rice recruitment calls from
106 through 115. Each evaluator call saw other unit types but no
Builder. The unit was processed from 106 through 114 and marked
for removal on 115. Sydney, Canberra and Melbourne all requested
priority 2 when recruiting the same unit. These outcomes establish
scarce capacity and earlier assignment in this fixture. A larger Rice
job score would leave those eligibility checks in place. A higher
production offer would compete with the other recorded investments.

The corrected trace froze with no active frames and no fault. The
controller verified native exit and package and preference restoration.
The trace SHA-256 is
`a3990797c37e5359f50ea02734e3d384fe25b12f354fbd343596c3af9dd0d65e`.

### The turn-100 portfolio had only two one-link opportunities

The archived turn-100 census from `development-ordinary-exchange-249-01`
contains six Quarter footprints with both an adjacent friendly Granary
host and an owned, uncovered, mapped Base deposit with its improvement
technology unlocked. Four Quarters were complete and healthy. The list
below uses footprint and unlock information. Builder reach, current
building eligibility and actual competing bids still require live checks.

| Player and Quarter plot | Missing chain links on turn 100 |
| --- | --- |
| 1, Ancyra 1430 | Mill and Granary |
| 2, Aigai 2311 | Base improvement |
| 2, 1860 | Quarter completion, Base improvement, Mill and Granary |
| 4, Melbourne 1423 | Mill |
| 4, 1426 | Quarter completion, Base improvement, Mill and Granary |
| 5, 2761 | Base improvement, Mill and Granary |

The one-link opportunities fit the existing policies. The other four
need an earlier investment before any last-link policy can apply.
Ancyra had a working Rice Farm and two buildings missing on turn 100,
the shortest remaining sequence among these four. The later Ancyra
Granary trace shows that legal construction can still lose to Castle
and military production. Capture earlier choice and expected completion
cost before pricing that first investment. One earlier census cannot
establish which candidate will be ready soonest in another start.
The separate Alexandria diagnostic preserved an inactive turn-120 save
with this same Ancyra footprint, working Rice and both buildings missing.
Its SHA-256 is
`a74a60e6f07b5303d01e5c441dce5e96d71e2cf1eebaa30c0ed02d6e230c2a56`.
The archived turn-100 census SHA-256 is
`4a6747a13056a9035cb2735b56283e85463154dd60a7963e12fa6a6c386ac091`.

#### A normal-start repeat reached four chains by turn 200

`development-early-portfolio-200-01` used the same Small Continents
development seeds and integrated packages as the turn-249 run. It
started normally and closed cleanly at 200. All six milestone censuses
completed, and all interior turns 2–199 were sampled. Only Ancyra and
Alexandria had both an adjacent customer footprint and an owned mapped
Base with its improvement technology unlocked at 80. Ancyra already
had its Farm and still lacked both buildings on 190. Melbourne needed
only its Wind Mill at 100 and 120.

| Chain | Active turns | Verified range |
| --- | ---: | --- |
| Alexandria Troas, Quarter plot 2311 | 69 | 119–187 |
| Melbourne, Quarter plot 1423 | 50 | 150–199 |
| Charleston, Quarter plot 2025 | 38 | 162–199 |
| Townsville, Quarter plot 1869 | 19 | 181–199 |

Alexandria's Quarter and Water Mill were pillaged at 200. Its original
Cattle Pasture and Granary still worked. The Service remained inactive
from 188 through 199. The census and Service records establish a live
repair opportunity. Alexandria finished a Research Lab and chose Dam
contract 4029 on 198. Its Dam was near completion at the saved boundary.
The cause of the damage and the next repair decision still need evidence.
The original Heidelberg Quarter at 1244 was absent in
this repeat. The save preserves Charleston's completed chain and sole
working Maize, next to the Dam that it placed at `(28, 27)` earlier in
the game. That supplies a live geometry check for the new Dam survey.

The result SHA-256 is
`c5facd1bec281d3a2fb99beebfa34afaf9d49dbc0a28c424714aa835342924c7`.
The archived inactive turn-200 save SHA-256 is
`641421d09b33a8f467b5d8635a98af1731c236edfa14d0acdbf95695ad5820d6`.

#### Charleston verified the live Dam survey

`development-charleston-dam-sites-01` loaded that turn-200 save without
changing the policy. The native river binding put Maize plot 2100 and
the completed Dam at 2026 on river 273. Its floodplain contains 1878,
1952, 1953, 2025, 2026 and 2100. The city operation exposed no legal
new Dam footprints at that boundary. On turn 204 the native district
selector chose Spaceport at `(28, 25)` and the Dam entry for
2100 remained the invalid value, −2,559,744 Q8, with the row ineligible.
The Maize Farm still worked at 206. This verifies the survey and score
observer on the live build. A genuine alternate-site comparison still
requires a city with an eligible threatened plot and an alternate.

The controller verified normal exit and restored both packages and
preferences. In the same read-only continuation, Alexandria's Dam
finished and Broadcast Center entered production. The Bakers Quarter
and Water Mill were still pillaged at 206. Trace repair nomination and
the next open production comparison from the archived boundary.

The survey SHA-256 is
`3be54b79cdb5b5a105bd0a828ff89d397c8d63822ec713ebb22a7cce5f57d787`.
The fault-free selector trace SHA-256 is
`43e687291466cbc5e97ec8472324af7ec68eacc7c441822ba8c6199939f6f30f`.

#### The Quarter can gate its own Mill's repair

The native existing-building requirements at `0f61c0` resolve the
pillaged building's district, including a district replacement.
When that district is complete but pillaged, the evaluator sets its
blocked-district flag and clears eligibility. The code also checks
contamination and hostile occupation. Alexandria's turn-200 UI build
queue returned false for the Water Mill while its Quarter remained
pillaged. That UI result does not identify the failed predicate by
itself. The native rule gives an independent reason to evaluate Quarter
repair first.

For the district itself, `GetBestLocationFor` at `3e5550` can return
the existing plot when the specified district is pillaged, before its
new-site search. `CanZone` at `0f97b0` has an existing-complete-district
path which checks pillage, coastal flooding and hostile units. These
are paths for a specified district. They do not establish that city
planning nominates the repair against new districts and other work.

The normal-start run's unit log shows a Barbarian Line Infantry
requesting pillage on 187, the last active Storekeeper turn. That log
does not record its target coordinates. It is a possible cause of the
Alexandria damage and remains unconfirmed.

`development-alexandria-producer-repair-01` read the Water Mill and
queue choices from the exact turn-200 save through 214. The Mill had
positive values and failed the requirements check on all ten recorded
building comparisons. Two advisory calls from `3e160a` still named it
the winner at 263,688 Q8. Their alternatives stood at 90,811 and
94,907 Q8. The other eight comparisons selected an eligible building.
The trace observed no Mill offer validation or repair request. The
four production passes executed a Broadcast Center, a Builder, an
Aerodrome and a Settler offer, respectively. The physical Quarter and
Mill remained pillaged at 214 while the Pasture and Granary worked.
The actual Service stayed inactive in the measured interior turns.
All 13 interior turns were sampled. Melbourne, Charleston and Townsville
worked throughout the interval. A German Quarter at plot 1677 first
showed an active Service on 213. The controller verified a normal exit
and restoration.

The Water Mill already had a strong advisory score. The observed
eligibility failure comes before effective production competition.
The next replay checks the Quarter's own build-operation legality
and compares its existing footprint in the district selector. It
also records whether an occupied district planning slot prevents a
new comparison. The fault-free first trace SHA-256 is
`7d538c18085d7684069d619cbe832a3b5028629e2f251ab3141412efacfea10b`.

`development-alexandria-quarter-repair-selector-01` replayed the same
turn-200 save through 214. The native build operation accepted the
existing Quarter repair at plot 2311 on the inactive turn-200
boundary. Twelve of 14 district checks found an existing tree. The
two open checks produced these comparisons:

| Turn | Existing Quarter score, Q8 | Aerodrome winner, Q8 | Difference in utility points |
| --- | ---: | ---: | ---: |
| 201 | 1,445,266 | 1,847,362 | 1,570.69 |
| 209 | 1,528,530 | 2,830,878 | 5,087.30 |

The cached Quarter row was owned and flagged eligible. It carried
reservation 6881299 at both checks. The observer does not establish
whether that reservation still imposed a live threshold. The Quarter
was below the recorded winner even without that possible threshold.
Alexandria submitted Aerodrome contracts 4422 and 4704. Both repairs
were still outstanding at 214 and Storekeeper remained inactive in
the measured interior turns. The differences are in district value.
A calibrated preference would need to represent benefits the native
score actually misses.

The native district `NetValue` at `52a440` already doubles its
accumulated value when the candidate matches the existing pillaged
district on that plot. The City Center branch also adds 12,800,000
Q8 before that multiplication. This is an input to the cache. Later
forecast aggregation can add other terms, so the final repair score
does not have to be exactly twice a hypothetical new district score.

The controller verified normal exit and restoration. The fault-free
selector trace SHA-256 is
`79cdfd5d62d680cead436e0c622e91cc7078c33f1b5500758f099d3763a84140`.
The inactive turn-214 save SHA-256 is
`a978f782b451a3d037ca736ce6ba663002faa67f3a0797dc122e2d1ca0c36bcb`.

The follow-up `development-alexandria-quarter-repair-selector-02`
opened that boundary. The native build operation still accepted the
repair. The UI queue reported 22 of 30 Production invested in the
Quarter, leaving eight. This is the cost of the Quarter link at that
boundary. It excludes the subsequent Mill repair and any time spent
waiting for production.

All 15 district planning checks from 214 through 228 found the same
active tree ID, 67567670. None of these checks called the district
selector. Both repairs were still outstanding at 229. Every
interior turn (215–228) was sampled for Storekeeper. Four other
chains operated on all 14, while Alexandria operated on none. The
controller verified clean close and restoration. The fault-free
`quarter-repair-trace.json` SHA-256 is
`d7ca696bc4ffebefa30ca53429b4e48152cee44a5cb375d3130c201a5d13ee59`.
Both selector runs are under `Desktop/Codex/csc-bakers-qualification-20261107`.

The read-only `development-alexandria-quarter-repair-reservation-01`
replayed the turn-200 source through 203. At the open turn-201 check,
the same two scores and the cached reservation ID 6881299 reproduced.
The effective exclusive threshold on the Quarter row was the default
−2,559,744 Q8. The reservation ID had no live AI controller at this check.
The Quarter entered the comparison and lost on value. Turn 209 was
outside this diagnostic window. `GetBestDistrict` (`3e4a50`) uses the
stored plot threshold only if `Control::Manager::Find` (`4019f0`)
returns the owning controller. Contract IDs use the separate
`FindContract` (`401a40`). `ReservePlotNode::Update` (`55ef10`) supplies
the tree's controller ID to `TryReservePlot` (`3ea040`). That function
checks the current owner when a different controller tries to reserve
the same plot, so a live reservation can still matter later. The
effective threshold observer reads the pointer used at `3e4b19` after
the lookup, guarded by the loaded hotfix's instruction bytes. The
fault-free trace SHA-256 is
`b34fcddfc52e1b07d245d77b85bd110a61b49bb32f585621fabb0f693b580a6d`.

The scoped treatment to investigate is a separate, ordinarily valued
repair offer for the existing footprint, with the stock district plan
and production comparison intact. Stock `CheckForDistrict` (`3e0ee0`)
creates a one-use behavior tree (`563840`), registers it with AI control
(`53feb0`) and records its ID in the district planning slot. Its
`BuildFromCityNode::Execute` (`55ba40`) creates and initializes a district
request (`3fe9a0`, `3f9100`), submits it to the manager (`403c70`) and
uses `ManageContract` (`5431a0`) to track a request that remains in
state 3. `ManageContract` retains a copy of the native request handle.
The shipped `Build City District` tree decodes the city, district and
plot before it submits the district request. For a trigger with a city
and a plot, `DecodeTriggerNode::Update` (`55a680`) reads the native
plot-specific present value (`3e7f40`) for the tree's valuation.
The manager updates each registered tree and checks for destruction
in `DoTurn` (`5639b0`). `CheckForDestroy` (`53ff60`) evaluates the
tree's owning player and completion state, so a one-use tree can
remain live across turns. `UnitRequestContract::Update` (`3fa5e0`)
refreshes a district offer using the greater of retained value and
current plot value, and separately updates turns from the remaining
Production. Verify that a
separate offer uses a native owner, deduplicates and expires on its own,
and competes against ordinary requests before integrating the policy.

### An ordinarily valued Quarter repair offer beside the stock plan

The treatment runs on the exact inactive turn-200 save from
`development-early-portfolio-200-01`. The shared controller verifies
the same package and census, a legal Quarter repair, a working supplier
and Granary, and the pillaged Quarter and Water Mill. On the native AI
thread, the probe waits for the turn-201 Aerodrome winner and both
known Q8 scores, including the Quarter's default reservation threshold.
It runs after stock `CheckForDistrict` has registered Aerodrome.

The probe resolves the existing footprint through the city's own
`GetDistrictAt` (`11e520`), the same lookup used by `BuildDistrict`
(`3df220`). The extra stock `Build City District` tree receives a
normal city priority and trigger context for the existing district,
with no research prerequisites to acquire. It gets a distinct native
controller. The stock slot and district values are untouched. The
observer records the request under that controller and the native
execution and controller release if they occur. Storekeeper is
measured separately. This is a pinned GameCore diagnostic, separate
from the CE API and the qualification runs.

The first attempt, `development-alexandria-quarter-repair-offer-01`,
reproduced the stock comparison but failed the footprint guard before
tree creation. The direct lookup used the wrong player object field.
The guard prevented a write, and the controller closed and verified
restoration. The trace SHA-256 is
`e3fe91019e98cdcd7110b89458ee38fdb33565071efcb19850a9d74f735eeb29`.
The retry uses the city lookup above.

`development-alexandria-quarter-repair-offer-02` passed that guard.
On 201 its separately labelled tree decoded the Quarter, reserved
plot `(17, 31)`, and submitted Quarter request 4421. The same native
city log recorded Aerodrome request 4422 on that turn. The tree logged
a decoded value of 1,227,157,293. The native city log reported the
Quarter request at 2,420,525 whole value units, versus 7,216 for
Aerodrome. The Quarter's selector value of 1,445,266 Q8 corresponds
to 5,645 whole units. Shifting the inflated decoder total into its
32-bit Q8 field and reading it back as whole units yields 2,420,525.
This run demonstrates separate request
admission. The unexpectedly high value invalidates it as a test
of ordinarily valued repair. The controller subsequently lost its
responsive tuner context at turn 202. There is no verified queue
execution, repair or Storekeeper outcome from this arm.

`development-alexandria-quarter-repair-offer-03` added a guard at the
decoder's function return. The shared controller lost responsive tuner
contexts at 201, with no repair-tree, decoder or request receipt. There
is no evidence that this attempt reached the guard. The game exited on
a graceful window-close request. A separate main-menu session verified
the original preferences and archived the two temporary packages at
their original hashes. The original `failure.json` SHA-256 is
`0e70947b6a0f6db7efb4821de43890ac3432b751472a0fc6f7937ca6c3d1a486`.

Astra identified a lifetime hazard in the original probe. It passed a
fresh Frida allocation to the native constructor and retained only
the returned address. A disposable-process test on Frida 17.24.3 and
QuickJS registered a weak finalizer on the allocation wrapper. The
wrapper finalized while the pointer returned through the native call
was still held. This demonstrates that the returned pointer does not
keep its owning wrapper alive. The test does not identify the cause of
either Civ VI failure. The revised probe keeps the original allocation
wrapper through construction, copying and cleanup.
[Frida Memory.alloc lifetime](https://frida.re/docs/javascript-api/#memory).

In the archived control, Aerodrome decoded to 7,216 whole units on 201
and 11,058 on 209, consistent with each selector score shifted by eight
bits. The revised guard reads the plot value just after the native
`PresentValueOf` call in `DecodeTriggerNode::Update` at `55afcc`, along
with the sum before that input. At the success epilogue `55b72b` it
checks both trigger value inputs and the decoded Q8 total. It rejects
the exact diagnostic tree before reservation or bidding if any value
differs. These two instruction probes preserve the original return
addresses of stock node calls. Their receipts are journalled before
the endpoint is reached.

`development-alexandria-quarter-repair-offer-04` reached 203. Its native
tree decoded the repair to 5,645 whole units, which matches 1,445,266 Q8
shifted by eight bits. Both trigger fields read as zero at tree creation.
Aerodrome kept its 7,216-unit request. The repair tree returned failure
before submitting a request. The controller closed and restored both
preferences and packages. The diagnostic's scratch-buffer cleanup
had faulted after tree creation because the generic game-memory reader
did not find the Frida allocation in its mapped ranges. The decoder
guard then failed closed. The trace SHA-256 is
`c7e8a3387f2558cc487b39664ef6e628fcaad485c17d55e59a7a63067d07672a`.
The probe now reads the native vector pointer through its retained
Frida allocation handle and frees a buffer only when one exists.

`development-alexandria-quarter-repair-offer-05` repeated the exact
turn-201 comparison. The corrected probe recorded 1,445,266 Q8 from
the plot getter, zero in the accumulator before that input, and zero
base and bonus. The decoder and the submitted request both carried
1,445,120 Q8, or 5,645 whole units. Quarter request 4421 reached native
state 3. The stock Aerodrome remained a separate request, 4422 at
7,216 whole units. The repair tree and stock tree retained distinct
IDs, 64028688 and 63963173. The city was producing Broadcast Center
when the two requests were submitted. A request accepted by the
native manager is still an offer to production.

Broadcast Center finished on 209. The native queue accepted request
4421 on that turn with its refreshed value of 1,528,530 Q8, equal to
the control's recorded Quarter value on 209. The turn-210 production
row shows 22 existing Production plus 36 new Production against a
30-Production repair. The separate controller was released on 210.
The city logged cancellation of the associated request during cleanup.
The turn-214 census confirms a restored Quarter, alongside the still
pillaged Water Mill and the working Pasture and Granary. Aerodrome
request 4701 entered native `IN PROGRESS` on 210. The queue log then
records Production going to a Settler on 211–213. Storekeeper did not
operate in Alexandria on any of the 13 sampled interior turns. The
matched control's Quarter and Mill were both still pillaged at 214.
The controller closed and verified restoration. The fault-free treatment
trace SHA-256 is
`ed0c9800ff98541b5af52c31a55a3b6a3c27c275d7b06b1c8a686a22f568485c`.
The verified treatment save at 214 has SHA-256
`7c8c0086ed022982cb2b8fab84c3c8b71a5d5fb8b5500da6531a0773bb5fa55c`.
Use it to measure the remaining Mill's legality and competition.

### Stock AI repaired the Mill and restored Storekeeper

The read-only `development-alexandria-water-mill-after-quarter-01`
continued that exact save from 214. At the source the Water Mill
was still pillaged. The native production query now returned true.
The stock AI submitted Water Mill request 4993 on 217 at 1,331 whole
value units. Its ordinary `0/0` building comparison passed native
requirements and selected building 140 at 340,938 Q8. Alexandria used
production to finish a Builder on 219. The native queue validated and
refreshed the 340,736 Q8 Mill offer to 566,288 Q8, then accepted it.
On 220 it recorded
61 accumulated Production against the 40-Production repair, including
31 new Production. The native Storekeeper watcher first measured the
working effect again on 221. It tied Water attachment instance 93255
to Quarter district 524295, then to the active Water growth instance
93256 on Alexandria's City Center district 458758, all under player 2.
The only repair intervention was the earlier extra Quarter admission
at the stock plot value. The fault-free Mill trace SHA-256 is
`07d26d71534dfe692292962dd212b5795074d59f578c6e76c14a8e4436c54667`.
All 14 interior turns were sampled. Alexandria operated on every
turn from 221 through 228, giving eight verified active turns after
the interruption. The 229 census confirmed the repaired Quarter and
Mill and the original working Pasture and Granary. The shared controller
verified a clean close and restoration. The inactive endpoint save has
SHA-256 `31bb234008fa5ffcc65636153f9201601ed665758f771322b574e3e73c2e276e`.

#### Proposed reusable delivery boundary

Keep the choice of repair candidates in CSC. Its existing Bakers scan
already finds mapped suppliers and customer districts. Initially request
the repair of a complete, pillaged Quarter only when the working supplier
and customer remain and the existing producer needs the Quarter restored.
The repaired host lets the ordinary AI handle its producer. The proposed
CE input is a bounded, versioned set of player, city, district and exact
existing footprint identities. It has no score or priority input.

At the same native admission phase used in the diagnostic, CE should
recheck original AI identity, current ownership, damage, exact footprint
and repair legality. Preserve the ordinary district tree. Keep at most
one supplemental repair per city and reject duplicates of the ordinary
plan or an existing supplemental repair. Use the stock tree template,
decoder and production queue. Report admission, request and retirement
as separate events. Keep active work bounded by candidate lookup and the
native lifecycle, with reconciliation after load before a candidate can
submit again. The native manager has `FindById` (`564020`) for live tree
IDs. Its `Read` (`564b40`) reloads its tree store and rebuilds active
lists. These are paths to qualify for deduplication across reload, rather
than evidence that the diagnostic's in-process IDs already provide it.

Review the reusable CE implementation separately from the proof. Match
the exact save in packaged CE and CSC with an empty candidate control.
Check repeated publication, active-tree save/reload, repaired or
invalidated candidates, and clean retirement. Confirm a matched
normal-value repair and actual Service before including this capability
in a delivery review. An Astra review agreed that this feature belongs
ahead of further repair score tuning. The early investment and fresh
validation runs remain separate milestones.

The isolated CE review worktree is `ce-district-repair-admission-review`
under `Desktop/Codex/csc-gamecore-hotfix-20261106`, on local branch
`codex/ce-district-repair-admission` at the exact staged DLL source
`abf5d5842aceff98e50612055a15044ff3f288fa`. This records the review base.

#### Packaged CE and CSC reproduced the Quarter repair

The review branch now implements the optional repair stage and status
inside the existing district policy transaction. Its supported MSVC
Release x64 build SHA-256 is
`4cfe1ccb0a6369cd123f9d18f3efc3dd87dffbbe42a9c75a347c478f8050ae85`.
The DLL preserves all 157 PE export ordinals and names from the reviewed
nomination carrier. The isolated native suite passed 86 checks and the
existing hook group and instruction checks. A Lua 5.1 fixture verified
the working supplier and Granary, matching pillaged Mill, damage and
Feudalism gates, four-field staging, duplicate and original-player
checks, and the older CE fallback.
[CE review source](https://github.com/hennogous/CivilizationVI_CommunityExtension/tree/codex/ce-district-repair-admission).

`development-alexandria-quarter-repair-ce-01` reloaded the exact 200
checkpoint with the separate CE dependency and the three changed CSC
AI files. There was no Frida attachment, Lua score write or manual
production order. On 201 CE admitted one repair tree with controller
64159762 and native plot value 1,445,266 Q8. GameCore submitted Quarter
request 4421 at 5,645 whole units and stock Aerodrome request 4422 at
7,216. When a second stock district plan became available on 209, CE
recognized the active repair and reported one duplicate. The repair
used the native queue and restored the Quarter on 210. CSC's next
publication had zero candidates. The turn-214 census confirmed the
working Quarter and the still-pillaged Mill. The controller verified
normal close and restoration. The inactive save SHA-256 is
`1d78ac421eb66caab2bc6d5ef06784f38f31d1aadfa154210f8570a4c1a41ad8`.

`development-alexandria-mill-repair-ce-01` reloaded that archive with
the same packages and no additional repair policy. The Mill was eligible.
GameCore submitted and accepted the same stock Mill request on 217 and
219, and finished the 40-Production repair on 220. All 14 interior
turns were sampled. The actual Storekeeper growth effect was active
on each turn from 221 to 228. The controller verified normal close
and restoration at 229. The endpoint save SHA-256 is
`5156e5ee9e76b4759cfab2732915b0205113b252dcb3264fdeb499a4c1b09243`.

The existing Lua timing log did not resolve sub-second differences
on this late-game replay. Measure the native admission overhead and
publisher cost with a higher-resolution clock in the performance pass.

#### An active Quarter repair survived a save and reload

`development-alexandria-repair-ce-active-save-01` repeated the packaged
treatment from the exact turn-200 source. GameCore submitted Quarter
request 4421 on 201 at 5,645 whole units. The controller stopped at 206
with the request still outstanding and verified the inactive save and
clean close. The save SHA-256 is
`1078a8f042656c79afc8913a336890eb715e4068d075351d4027d1d8c2e4d083`.

`development-alexandria-repair-ce-active-reload-01` loaded that exact
save with the same packages. The native build query reported the
Quarter repair legal with 22 of 30 Production. CSC published one
candidate and CE initially reported zero admissions and faults. On 209
the native queue used the original request 4421 for the Quarter repair.
When the stock district planner reopened, CE recognized the existing
repair and counted one duplicate, published in the turn-210 Lua log.
Across the replay CE reported zero new admissions and faults. CSC
withdrew the candidate on 211. The turn-214 census verified the same
Quarter healthy with the Mill still pillaged, the original Cattle
Pasture and the adjacent Granary both working. The controller verified
the clean close and the endpoint SHA-256
`347c58c7158889d60df47d1d2f7111a808c301f6228fa011ad133f54c829d6e4`.

#### The matched control still needed both repairs

`development-alexandria-repair-ce-empty-01` used the original turn-200
source and ran through 214 with the same CE binary. Across the 641
package files, the only change from the straight-through treatment
was one Lua line that set the repair candidate limit to zero. CE
reported ready with an empty table and no admission or fault on every
publication. In the control, Broadcast Center also completed on 209.
The later Aerodrome request 4704 entered production on 210. The
endpoint census confirmed the Quarter and Water Mill were both still
pillaged, with the original supplier and customer working. The
controller verified the clean close and inactive turn-214 save SHA-256
`eba7caf1ab28938c5766a7428ad9758996e156ad4aeb79ffe37f27297be75ee8`.

### Ancyra's early Wind Mill lost to Walls

`development-ancyra-wind-opening-01` continued the verified
`development-alexandria-fresh-105-observe-01` turn-120 archive through
135 with the original packages. The source save SHA-256 is
`a74a60e6f07b5303d01e5c441dce5e96d71e2cf1eebaa30c0ed02d6e230c2a56`.
Ancyra had Feudalism, an inland Quarter on 1430 and a working Rice
Farm on 1429. Its adjacent City Center had no Granary and the
Quarter's Wind Mill was legal and unbuilt. The read-only probe
recorded zero score additions at every scoped comparison.

| Ordinary building comparison | Wind Mill Q8 | Walls Q8 | Gap Q8 |
| --- | ---: | ---: | ---: |
| First | 46,569 | 154,244 | 107,675 |
| Second | 89,260 | 326,002 | 236,742 |

The Mill passed its requirements at these two ordinary `3e160a`
comparisons and at all fifteen scoped comparisons in other callers.
The first production comparison rejected Builder offer 2187 at
52,736 Q8 against the unit and project alternatives at 87,717 and
63,630 Q8. A Walls request succeeded on the building fallback. The
queue recorded Art Museum completion on 131 and Walls on 132–133.
The next scoped queue pass accepted Line Infantry offer 2376 at
258,816 Q8, above its unit and project alternatives at 76,510 and
66,660 Q8. The production log confirmed Line Infantry on 134. Both
Bakers buildings were still absent at the turn-135 endpoint, with
the original Rice Farm working. The observed margins describe how
strong the alternatives were. Pricing the Mill's chain contribution
also requires the likely timing of the Granary and the local value
of the benefits during that window.

The observer froze without faults and the controller verified clean
exit and restoration. The observer SHA-256 is
`b0a27df698fa57071c2104b9e2fb239e38b68af2035c1b29e202e9ccc4a4b4b4`.
The verified turn-135 save SHA-256 is
`027cfe5df1b4b701b7db6e433747fe7737e5e0ed8b4658631ef6813062416f9a`.

#### The paired Granary replay lost to the same alternatives

`development-ancyra-granary-opening-01` replayed the same turn-120
source and packages through 135, observing the Granary instead. It
was legal at the source and passed its requirements at all 17 scoped
comparisons. At the two ordinary nominations Walls won by larger
margins than it did against the Wind Mill.

| Ordinary building comparison | Granary Q8 | Walls Q8 | Gap Q8 |
| --- | ---: | ---: | ---: |
| First | 15,112 | 154,244 | 139,132 |
| Second | 27,852 | 326,002 | 298,150 |

Both replays had identical candidate comparison winners and winner
values, scoped queue gates and requests, 34 Ancyra city-build log
rows and 15 production queue rows. The source and endpoint chain
censuses matched after removing transport metadata. At 135 the
original Rice Farm still worked and both buildings were absent.

The Granary has its own native value. Its CSC exchange still needed
the Mill. The Wind Mill was the closer of the two at both ordinary
comparisons, but its omitted standalone CSC value at this site was
unmeasured. The observed gaps describe the actual competition, with
no calibrated first-link amount inferred from them. A separate
earlier opportunity is a legal Mill beside a working supplier and
Granary before Feudalism. The current Mill preference waits for
Feudalism even though the ordinary exchange can operate sooner.
Look for these cases in a frozen normal-start development game
before changing the nomination policy.

The Granary observer froze without faults. Its SHA-256 is
`2e18df5706089265d43b5ad338c88ebd6ccff03960520b720802869c92594420`.
The controller verified clean exit and restoration and the turn-135
save SHA-256 is
`251722b6cc83f64a452e24ff4e81857a805247675c138689d6d5cb2f00f9a0ed`.

### Shared Granary hosts receive one nomination preference

The CSC publisher formerly visited a Granary host once from each
adjacent working Mill. A two-Mill Lua fixture reproduced two
identical packets for player 3, city 77 and its legal unique
Granary replacement. The publisher now visits each customer city
once per player and policy publication, retaining the existing
13,312 Q8 preference and native eligibility checks. The same
fixture now receives one packet. In the exact reviewed CE commit
`abf5d5842aceff98e50612055a15044ff3f288fa`, `finish_nominations`
already retains the largest preference per building, player and
city at commit. CSC's change removes redundant UI eligibility reads
and avoids consuming the packet's input budget twice. The native
score already used one preference. The fixture leaves the value
of the incremental exchange from a second Mill unmeasured.

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
