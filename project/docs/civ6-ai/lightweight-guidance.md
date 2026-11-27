# Workshop AI guidance without CE

CSC offers one setup option, **Advanced CSC AI planning**. In a single-player game with compatible CE, its default runs the economic planner alongside Civ's normal AI. Turning it off skips the planner. A game without CE uses the stock AI controls below. Ordinary gameplay adjacencies, transaction payouts and Service requirements use their existing definitions in every mode.

| Decision | Input used by the lightweight candidate |
| --- | --- |
| Place a mapped customer next to a Quarter, in either build order | One private adjacency yield per neighboring partner. The SQL derives both directions from building transactions, sales and provider tags, including district replacements. City settlement and generic Wonder tiles are excluded. |
| Place a Quarter near working material infrastructure | One private adjacency yield for selected neighboring improvement families. At least one Base must use the improvement. The family qualifies when a third of its mapped resource types are Base or half are Base and Spec together. An improvement which can occupy ordinary terrain or features requires two neighbors. In the standalone catalogue Bakers sees Farms (two), Pastures and Plantations. Tailors sees Pastures. |
| Recruit a Builder | A +10 preference in the stock unit-request list when a mod has not already supplied that Builder row. Civ selects the job, recruiting city, unit and route. |

The material cue deliberately uses an observable feature of the map. A Pasture can hold Cattle, Sheep or Horses. Bakers and Tailors each benefit from one of those resources. A Cotton Plantation can feed Tailors but the family also covers thirteen other resources, so a lone Plantation gives Tailors no private adjacency in the standalone catalogue. The outcome measure counts the actual resource and working improvement.

## Research behind the choices

City Lights supplies a local example of stock improvement adjacency. RHAI5 uses the stock unit-request list in `core/Ops/RH_Ops.sql`. AI+ uses the Required City parameter on the Build Unit node of the Build City Improvement tree in `behaviortrees.xml`. Real Strategy's `base/RealStrategy_Anti.sql` illustrates gating a player's preference lists through a Lua strategy condition. That is a candidate for changing broad investment priorities when a shortage is observed.

The Ghidra trace shows that the stock district valuator reads each registered yield, applies the city's weight and also considers eligible competing districts on the same plot. A +1 private adjacency can swing a close location decision. Its final utility depends on both the city and the alternative uses of the land. [Reusable engine trace](https://github.com/hennogous/civ6-ai/blob/8e69bb6/references/engine/modding-controls.md#where-a-registered-adjacency-enters-district-valuation)

## Matched game comparison

The two preselected Continents map seeds are 171124601 and 171124605 on Small/Online. Compare stock CSC, the lightweight guidance and the full planner, always with ordinary AI leaders. The primary outcome is completed Quarters with a working adjacent Base and a completed mapped customer, counted once per Quarter. Track active Service links, Quarter foundations without usable owned Base, loss of the last supplier and popup-free turn times from the same stock automation clock. Retain the final saves for map inspection.

The first no-CE smoke test reached turn 25 and saved successfully. Only the pinned Firaxis XP2 core loaded. Sixteen Quarter-to-customer adjacency links were present while the full planner was absent, and the observer recognized 33 Service attachments. This test preceded the material-family cue. The five AI empires had completed no Quarters by that turn. The full games measure placement quality and Service operation.

In the first stock game the exported database contains the vanilla `UnitPriorityBoosts` list with no Builder entry. Both Build Unit nodes in the Build City Improvement tree (13 and 23) leave Required City unbound. Ghidra shows that XP2 initializes that input to −1 and uses the binding, when available, on the branch with no controlled cities. Writing an explicit −1 there repeats stock behavior. The candidate therefore leaves the tree alone, including any recruitment constraint that another mod has supplied.

### Seed 171124601 at turn 250

| Stock AI across five original AI seats | Bakers | Tailors |
| --- | ---: | ---: |
| Completed Quarters | 17 | 17 |
| With an adjacent working Base | 1 | 2 |
| With a completed mapped customer | 13 | 4 |
| With both working Base and completed customer | 1 (5.9%) | 1 (5.9%) |
| Without an owned Base deposit at the endpoint | 14 | 12 |

Of the 37 observed AI foundations, 26 lacked usable owned Base. Reading all six neighbors showed that 8/18 Bakers and 6/19 Tailors had *any* mapped Base adjacent. Three foundations had Base only outside the owner's borders. The other 23 had none on any neighboring tile. None of the 37 started beside a working Base supplier. That makes undeveloped land an important test for the lightweight guidance.

Six last-working-supplier losses were observed (three per Quarter type), with three losses of the last viable deposit. None of the six working-supplier losses showed a district occupying that supplier at the next turn boundary. The Service observer recorded two Storekeeper links for 50 active chain-turns and one Sacristan link for 23. The 199 observations exclude the five-turn controller handoffs. The stock game averaged 5.43 seconds per popup-free turn and peaked at 16.60 seconds (196 intervals).

### First lightweight treatment on the same opening

Both arms loaded the Firaxis XP2 core and completed 34 Quarters by turn 250. The private adjacency and Builder preference produced more customer neighbors on this seed. The scarce link was an operating material supplier.

| Turn 250 | Stock Bakers | Lightweight Bakers | Stock Tailors | Lightweight Tailors |
| --- | ---: | ---: | ---: | ---: |
| Completed Quarters | 17 | 18 | 17 | 16 |
| With a completed mapped customer | 13 | 17 | 4 | 7 |
| With a working Base | 1 | 2 | 2 | 1 |
| With both | 1 (6%) | 2 (11%) | 1 (6%) | 0 (0%) |

In the lightweight arm both supplied Bakers touched a City Center without a Granary. One had a Wind Mill. The supplied Tailors had its producers but lacked a Harbor. Across the 199 common Service observations, stock recorded 73 active chain-turns and lightweight recorded zero. Foundations without an owned viable Base went from 26/37 to 29/38. Losses of the last working supplier went from six to five, including zero losses in either arm where a district occupied the supplier at the next observation.

Across 194 common popup-free turns, stock averaged 5.42 seconds (maximum 16.60) and lightweight averaged 5.82 seconds (maximum 18.00). These are elapsed turn times for two diverging games. Both recorded zero advanced planner passes.

### Follow-up candidate for undeveloped land

All eleven foundation sites with viable owned Base had at least one neighboring bonus-class resource. The same signal also covered **12 of the 26** sites without viable owned Base. Waiting for adjacent improvements misses many early opportunities, while a bonus-resource cue by itself can attract a Quarter to unrelated resources.

The replay can test an extra stock adjacency rule against the same start (`--deposit-cues`). For each Quarter, a class must include at least two Base types, cover at least half its Base catalogue, and have at least one Base for every six resources in that class. On the standalone catalogue this gives Bakers +2 private yield for a neighboring bonus resource (six of twelve types match) and Tailors +1 (two of twelve). The registered yield has no conversion into Production or Gold. Compare the realized supplies and customers before choosing a shipping default.

**How much does a bonus deposit tell us?** The five independent vanilla-Abundant Continents maps in the map lab contain 4,489 ordinary clearable land sites. This count excludes occupied sites, impassable land, unremovable features other than floodplains, and strategic/luxury footprints. It uses each map's actual Quarter tags and native neighbors. It describes map geometry before city ownership, production or Builder decisions.

| Map condition | Sites | Adjacent Bakers Base | Adjacent Tailors Base |
| --- | ---: | ---: | ---: |
| All clearable sites | 4,489 | 1,693 (38%) | 503 (11%) |
| At least one adjacent bonus resource | 2,571 | 1,693 (66%) | 468 (18%) |
| At least two adjacent bonus resources | 796 | 632 (79%) | 182 (23%) |
| At least one adjacent land bonus resource | 2,375 | 1,693 (71%) | 468 (20%) |

One bonus resource catches 93% of the genuine Tailors sites, but four in five sites it flags lack Sheep, Flax or Cotton. Two bonuses are a stronger Bakers cue. A blanket requirement for two would also discard 63% of the genuine Bakers sites. A prospective vote can scale with the cluster while keeping single-resource sites eligible. Avoid a general coast penalty for Tailors: the Harbor is its Stage 2 customer. [Map survey inputs and definitions](../../tools/map_survey/README.md)

An offline terrain tie-break gave a modest further gain. For each map we used the other four to choose a land terrain, then ranked sites on the held-out map by four points per adjacent bonus resource plus one per two adjacent tiles of that terrain. The target was the share with genuine Base among the top fifth of clearable sites, splitting cutoff ties evenly. For Tailors, all five training folds chose flat tundra. Held-out precision averaged 25.6%, versus 21.7% with bonus resources alone. Even the improved ranking was wrong about three times in four, and the survey assigns no cost to investing in a marginal tundra city. This result favors prioritizing proven improvements and customers before introducing standalone terrain incentives.

For exact raw resources, the stock adjacency row exposes a single resource class. Historical gameplay tests confirm that a combined class string cannot retain bonus membership and also act as a second classification. CSC's earlier exact-resource modifier did correctly highlight mapped plots next to *existing* Quarters. Its transfer to a prospective district score was unverified. The hypothetical requirement compiler also drops some gameplay gates, including the property requirement, and its ordinary PlotAdjacentToOwner handler does not measure the distance between two plots. Reusing that modifier as a site bid needs a candidate-stage readback. [Class test](../research/mods/native-resourceclass-multivalue-probe-20261028.md) · [Exact live-yield experiment](../research/mods/csc-ai-quarter-resource-incentives-20261019.md)

Two other stock controls help explain the boundary. Ghidra traced the `PlotEvaluations` item `Specific Resource` from its index initialization to its sole direct reader, `CitySiteEvaluation::AddSubValue` on the reference XP2 build. That preference informs where to settle a city. In the shipped Build City District tree, Decode Trigger supplies the location already chosen by the district evaluation. Purchase Plot, Reserve Plot and Build Production consume that location. The stock Lua Script Condition node declares a string input and no Map Point output. A separate Use Scripted Command node dispatches commands on units controlled by the tree. Neither supplies a documented site bid here. The current experiment therefore leaves settlement and those trees alone.

### A city-specific alternative

The district valuator has a second route on owned land. Before its competition adjustment it calls the stock adjacency calculator. That calculator also reads the owning city's active dynamic adjacency modifiers for the proposed district and yield. Thus a city could give Tailors an incentive for a particular terrain **only where that city's actual Flax, Cotton or Sheep makes the terrain informative**. This uses the same native effect as the terrain-adjacency pantheons. A change in the exact resource layout could switch off the incentive.

In a preliminary offline survey we sampled every third clearable plot by index as a hypothetical center, searched three tiles out, and required *every* site signaled by a single terrain or feature to touch an actual Base. The maps contained such a cue for 213/1,414 Bakers neighborhoods and 105/749 Tailors neighborhoods that had Base opportunities. These overlapping neighborhoods include land outside eventual borders. This is a selective supplement to the broad fallback.

The disposable no-CE `--city-cue-probe --end 50` checks the terrain mechanism separately. It selects two owned sites in one city with different counts of the same terrain, reads their stock Quarter adjacency, enables a private +7 test modifier, and checks withdrawal and an unconditional positive control. A production implementation would need to keep each rule aligned with the city's actual deposits and measure placement gains and turn cost.

### First full game with the undeveloped-deposit cue

All three games on seed 171124601 used the identical turn-one save. These figures use 199 common Service observations and 191 common popup-free intervals.

| At turn 250 | Stock CSC | Lightweight, improvements only | Lightweight, plus raw deposits |
| --- | ---: | ---: | ---: |
| Bakers with working Base and completed mapped customer | 1/17 (6%) | 2/18 (11%) | **7/20 (35%)** |
| Tailors with working Base and completed mapped customer | 1/17 (6%) | 0/16 | **1/17 (6%)** |
| Completed Quarters with any completed mapped customer | 17/34 | 24/34 | 25/37 |
| Foundations without usable owned Base | 26/37 | 29/38 | 21/36 |
| Storekeeper active chain-turns | 50 (2 chains) | 0 | **177 (4 chains)** |
| Other active Services | Sacristan 23 (1) | 0 | Innkeeper 32 (1) |
| Last working supplier losses / last viable deposit losses | 6 / 3 | 5 / 4 | 5 / 9 |
| Mean / maximum elapsed turn, seconds | 5.41 / 16.60 | 5.82 / 18.00 | 6.29 / 20.62 |

The deposit arm ended with eight working-Base Bakers and two working-Base Tailors. No completed Tailors touched a Harbor; seven touched another mapped customer. The 37 endpoint Quarters are current holdings, while the 36 foundations count this cohort's own observed construction. The stock empires held 47 cities and the deposit empires 52.

At the moment of foundation, the deposit rule's gain was concentrated in Bakers. Stock founded 6/18 beside usable owned Base and the deposit treatment founded 12/20. Seven treated Bakers had at least +3 current Production and Gold adjacency and two had both material classes; stock had zero of each. For Tailors, owned Base foundations went from 5/19 to 3/16. None of the treated Tailors started beside a working Base or both material classes. All eight completed, Base-accessible Bakers in the deposit arm ended with a working supplier. Two of the four Base-accessible Tailors did.

**One working chain was lost to its own customer.** At player 3's Bakers on plot 1047, the Storekeeper operated from turn 68 through 127. On 128 a Commercial Hub covered plot 1120, removing its last working Flax. Subsequent censuses identified the completed Hub on that tile and the Storekeeper never returned. Another Hub covered the last raw Bananas at player 4's Bakers on turn 71. The other seven final-deposit losses in this arm had no district on the tile at the next observation. The queued supplier-job treatment also tests a plausible retention mechanism: the district evaluator subtracts the same intact-improvement Value that includes the improvement's own Quarter adjacency. [Improvement loss trace](../research/mods/civ6-district-improvement-loss-20261106.md)

### Follow-up candidate for first customer buildings

Across the ten 25-turn censuses of the first lightweight game, two supplied Bakers had a functioning, adjacent City Center missing its Granary. One of those Quarters had also completed a Mill by turn 250. The supplied Tailors lacked a Harbor throughout its observed operating life, so changing Lighthouse construction alone cannot complete that chain.

The diagnostic `--customer-buildings` option adds a stock major-leader Buildings preference for each Stage 2 customer and its unique replacements, read from the gameplay definitions. On the standalone map that selects Granary and Lighthouse. The current stock database had no preference rows for either. The traced native selector doubles the building value on a positive accumulated preference, which makes this a broad investment across the empire. Measure customer construction, actual Services and the cost to competing investments before deciding whether to ship it. Real Strategy offers a narrower alternative if broad investment proves costly: a stock Lua strategy condition can activate the same preference for a player with a ready chain. [Building preference trace](../research/mods/csc-ai-native-production-analysis-20261028.md)

### Can the Quarter guide an ordinary Builder?

The stock Farm beside Korea's Seowon provides a useful reverse direction. Ghidra shows the city values a proposed improvement at the specific plot, follows the improvement's adjacency rows, reads neighboring district identity/completion/pillage state and weights the yield before the ordinary Builder job is selected. This supports a private-yield experiment with no Lua or CE. Each registered Stage 2 Base supplier gets one private unit per neighboring Quarter, or two for a selective resource-only family. The six standalone rows include Tailors Flax Farms and Cotton Plantations even though those families are weak predictors of a good site when placing the Quarter first. Check the actual fraction of owned Base deposits improved and any extra empty Farms before promoting the option. The test control is `--supplier-jobs`.
