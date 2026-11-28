# Workshop AI guidance without CE

CSC offers one setup option, **Advanced CSC AI planning**. In a single-player game with compatible CE, its default runs the economic planner alongside Civ's normal AI. Turning it off skips the planner. A game without CE uses the stock AI controls below. Ordinary gameplay adjacencies, transaction payouts and Service requirements use their existing definitions in every mode.

| Decision | Input used by the lightweight candidate |
| --- | --- |
| Place a mapped customer next to a Quarter, in either build order | One private adjacency yield per neighboring partner. The SQL derives both directions from building transactions, sales and provider tags, including district replacements. City settlement and generic Wonder tiles are excluded. |
| Place a Quarter near undeveloped Base materials | Count nearby resource classes that cover a substantial share of the Quarter's gameplay-defined Base catalogue. On standalone CSC each neighboring bonus resource gives Bakers two private units and Tailors one. A modded catalogue can qualify a different class or change its strength. |
| Place a Quarter near working material infrastructure | One private adjacency yield for selected neighboring improvement families. At least one Base must use the improvement. The family qualifies when a third of its mapped resource types are Base or half are Base and Spec together. An improvement which can occupy ordinary terrain or features requires two neighbors. In the standalone catalogue Bakers sees Farms (two), Pastures and Plantations. Tailors sees Pastures. |
| Recruit a Builder | A +10 preference in the stock unit-request list when a mod has not already supplied that Builder row. Civ selects the job, recruiting city, unit and route. |

The material cue deliberately uses an observable feature of the map. A Pasture can hold Cattle, Sheep or Horses. Bakers and Tailors each benefit from one of those resources. A Cotton Plantation can feed Tailors but the family also covers thirteen other resources, so a lone Plantation gives Tailors no private adjacency in the standalone catalogue. The outcome measure counts the actual resource and working improvement.

How good is “any bonus resource” on the actual maps? Counting individual **land** bonus deposits in the turn-one surveys gives Bakers 103/169 and 93/149 matches on the two seeds, or **62% combined**. Tailors matches 50/169 and 38/149, or **28%**. Flax counts for both Quarters. Another 263 bonus deposits were in water and none supplied either Quarter. Cotton supplies Tailors through a different resource class. This helps explain why the broad cue is more informative for a Bakers site, particularly when comparing sites along the coast.

For a possible Dockmaster, we also counted clearable land sites with at least one adjacent empty, featureless, non-lake Coast tile. Of the 358 such sites beside a bonus resource, 103 touched a Tailors Base. Requiring the bonus resource to be on land retained 102 of those 103 sites and reduced the shortlist to 265. Of the 93 coastal sites signalled only by a water bonus, just one had a Tailors Base. These opening-map counts describe terrain potential before city borders and district capacity. They identify a promising filter for a future Tailors trial.

The shipping connector action runs at 800011, after optional material removals, City Lights registrations and CSC's supplier-host reconciliation at 800010. This lets its family counts reflect the loaded resource and improvement catalogue. Regenerating the connector from the completed standalone game's database reproduced all 38 district adjacency rows, including their weights, thresholds and partner types. The benchmark retains its pinned earlier load order; experimental supplier-job rows load after 800010 in that package.

For a release replay, use `lightweight_guidance.py --as-installed` with a fresh label and the expected treatment flags. It checks the installed AI Lua files, connector, settings and manifest against source before starting Civ. The flags select runtime checks; the game loads the installed package directly. Ordinary experimental runs still stage and restore their pinned inputs.

**Installed build verified, 28 November.** Two fresh launches used the regular CSC installation and ran seed 171124601 to turn 50, each with a verified save. Both loaded the same 38 private district adjacency rows and the same Builder preference as their turn-250 benchmark. With only the Firaxis core loaded, the advanced publisher ran zero times. With compatible CE and the default setup option, the full planner ran on all 49 measured turns. The final package ships the resource-class and partner rules tested on both seeds. The city-specific terrain and extra job/building treatments remain research fixtures.

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

Terrain counts can distinguish sites even when a single adjacent tile would give a false positive. Across the same five maps, we compared every clearable site within three tiles of each sampled center, excluding the center as both a site and a potential supplier. In 822/1,383 Bakers neighborhoods (59%) and 302/753 Tailors neighborhoods (40%) with a Base opportunity, a terrain found underneath local Base had its highest adjacent count **only** at sites touching actual Base. For example, the cue could favor sites touching three plains hills when every site without a supplier touches at most two. The right terrain and count vary by city. These figures describe the map opportunities before ownership and competing district scores. [Reproduce the terrain-count survey](../../tools/native_ai/late_placement/city_material_coverage.py)

The disposable no-CE `--city-cue-probe --end 50` checks the terrain mechanism separately. It searches the city's legal owned Quarter sites for a terrain count that rewards only sites beside actual owned Base, then reads one such site and its strongest material-free competitor. It tests activation, withdrawal and an unconditional +7 control. A final stock modifier awards one private unit per complete group at the city's chosen threshold. Ghidra shows that Civ rounds each record's terrain contribution down to an integer before adding it to the district score. If no city provides a separating pair by the last checkpoints, the probe reports a terrain-only control. [Native rounding trace](https://github.com/hennogous/civ6-ai/blob/70c90a1/references/engine/findings.md#ai-n167)

**Live result, turn 20 on seed 171124601.** Player 4's city 65536 had eight legal owned Bakers sites. Two touched Plains beside mapped Base, and every material-free candidate had zero neighboring Plains. The native private-yield previews at the material site (2610) and comparison site (2389) started at **0 and 1**. Enabling the city-center **plot** property changed them to **7 and 1**. Clearing it restored **0 and 1**. Setting the property on the city object left the previews at **0 and 1**. An unconditional +7 reproduced the plot-gated result. A one-unit threshold record then added **1 and 0** respectively. All reads used Civ's stock placement preview with CE absent. This establishes a removable, city-specific incentive for an actual mapped supplier. The city-specific rule is still experimental.

The `--local-material-cues` candidate runs this selection from CSC's normal gameplay entry with the Firaxis core. Each original AI reviews at most one city per turn, oldest first, with at least 12 turns between reviews of the same city. A city can select one terrain rule per missing Quarter type. Every rewarded legal owned site must touch a visible, owned Base. Among qualifying rules it prefers an adjacent Stage 2 customer, then a clear coastal footprint for a mapped coastal customer. Within the same customer priority it favors an opportunity with mapped Specialty at that same site, then the rule covering more Base sites. The city switches its center property when the layout changes and withdraws a rule once the Quarter exists or the cue stops distinguishing suppliers. The ordinary district competition determines the final site and construction. Compare this candidate with the same seed's deposit-only arm for realised pairs, last-supplier losses, actual Services and elapsed turn times.

The turn-one map for seed 171124601 had 947 clearable land sites. Of these, 278 touched actual Tailors Base, and 76 touched both a Base and a clear coastal tile, spread across 32 distinct source deposits. Before city ownership, a terrain threshold singled out Base-adjacent sites in 165/287 sampled Tailors neighborhoods with a Base opportunity. This map has room for the local rule to help.

**First fifty turns with the city rule running from CSC.** Across five AI cities on seed 171124601, ordinary gameplay Lua activated nine rules (five Bakers and four Tailors) and withdrew five. It performed 37 city reviews covering 334 legal Quarter-site evaluations. Two Bakers were founded while their city's cue was active. Both landed on rewarded terrain and had a usable owned Base. A third Bakers and one Tailors were founded without an active cue and had no usable owned Base. This short run establishes that the live candidate reaches real placements. The Firaxis gameplay Lua clock returned zero elapsed time for every review. Use the independent popup-free turn clock for performance comparisons.

Player 3's city 131073 gives a matched example. On turn 24 the city rule rewarded one of its six legal Bakers sites. On turn 25 the city founded Bakers on that site (1119). With the broad resource cue alone, the same city founded Bakers on 1047 on turn 25. Both sites touched the same City Center and Flax on 1120. A second city built at the same Base-adjacent site in both games. Across all five AI seats, the first 50 turns produced two Bakers with owned Base in each treatment, among three foundations with the local rule and five with the broad cue alone.

**Full local-material replay on seed 171124601.** The rule was active at nine of 39 foundations. Four of six Bakers and one of three Tailors with an active rule landed on rewarded sites. All five had an owned Base at foundation. Across all placements, 11/21 Bakers and 3/18 Tailors started with owned Base. In the broad-cue game those counts were 12/20 and 3/16.

| Turn 250, common observations | Stock | Broad resource cue | Broad plus city-specific cue |
| --- | ---: | ---: | ---: |
| Working Base and completed customer, Bakers | 1/17 | 7/20 | 2/21 |
| Working Base and completed customer, Tailors | 1/17 | 1/17 | 0/18 |
| Completed mapped customers, Bakers / Tailors (count of Quarters) | 13 / 4 | 18 / 7 | 19 / 8 |
| Service link-turns | 73 | 209 | 50 |
| Last viable deposit losses | 3 | 9 | 12 |
| Mean / maximum turn, seconds | 5.31 / 16.60 | 6.19 / 20.62 | 6.14 / 17.73 |

The local arm recorded one Storekeeper for 50 common link-turns. Six Quarters lost their last deposit to a district and six lost the resource on an otherwise undistricted tile. Three had a matching harvest operation. Joining each covering district to its own Quarter's loaded private adjacency links identified one mapped customer and five unrelated districts. Player 3's alternative Quarter on plot 1119 lost its last working Flax when a Commercial Hub took plot 1120 on turn 163. Its Mill, adjacent Granary and Market were all functioning by turn 250. Protecting suppliers only when siting a mapped customer would still leave the other five district losses.

The local rule made 624 city reviews and evaluated 5,550 legal Quarter sites. All 39 foundations occurred within twelve turns of a review in that city. For the 30 foundations with no active rule, the last review had evaluated legal sites. Increasing review frequency alone has little support on this map. The gameplay Lua clock advanced one whole second on two of the 250 turns and zero on the rest. The elapsed turn comparison uses the independent clock across 188 common popup-free intervals. Service totals cover 199 common observations.

The first city-specific run of seed 171124605 was interrupted after turn 125. Civ logged the five-turn activation and its acknowledgement, but the controller missed the reply. Its last complete census showed 2/10 supplied customer pairs for Bakers and 0/8 for Tailors, with zero Service link-turns so far. At the same turn the broad cue had 3/9 and 0/8 with 66 Storekeeper link-turns. The stock arm had zero supplied pairs. The turn-125 autosave was preserved. The controller now performs a read-only check of the exact finite interval before deciding whether it can safely continue after an activation reply is lost.

The fresh replay on this seed reached turn 250. The treatment reviewed 4,096 legal site candidates across 626 city visits and activated 54 rules. Six of the 35 foundations had a rule active. Four landed on rewarded terrain, with actual owned Base at three of the four. At turn 250, 14/17 Bakers and 9/19 Tailors had a completed customer, yet none had a working Base. One earlier Storekeeper delivered 69 link-turns. Ten Quarters lost their last viable deposit. Stock, broad and local elapsed turns averaged 6.20, 6.38 and 6.25 seconds, with maxima of 17.29, 21.09 and 21.64, over 190 common popup-free intervals.

Across the two completed games, the local rule rewarded nine actual foundations and eight had the intended material. The broad default produced 11 supplied Bakers customer pairs at the endpoints, versus two with the local rule added. Local targeting remains an experimental example of how to guide stock placement toward a specific material. The player-facing lightweight mode uses the broader SQL rules.

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

The adjacent tiles at foundation show where the bonus-resource cue helped. Counting resources on either side of the border, all 20 treated Bakers touched a bonus resource and 17 touched actual Bakers Base, up from 10 and 8 respectively across 18 stock foundations. Five of those 17 treated sites still needed access to their Base. For Tailors, 13 of 16 treated foundations touched a bonus resource, but only five touched Sheep, Flax or Cotton. Stock already found a bonus at 13 of 19 Tailors foundations and actual Base at six. A larger generic bonus for Tailors would also reward the eight treated sites with bonus resources and no Tailors Base.

**One working chain was lost to its own customer.** At player 3's Bakers on plot 1047, the Storekeeper operated from turn 68 through 127. On 128 a Commercial Hub covered plot 1120, removing its last working Flax. Subsequent censuses identified the completed Hub on that tile and the Storekeeper never returned. Another Hub covered the last raw Bananas at player 4's Bakers on turn 71. The other seven final-deposit losses in this arm had no district on the tile at the next observation. The queued supplier-job treatment also tests a plausible retention mechanism: the district evaluator subtracts the same intact-improvement Value that includes the improvement's own Quarter adjacency. [Improvement loss trace](../research/mods/civ6-district-improvement-loss-20261106.md)

The last viable deposit disappeared on a tile still owned by the same player, with no district present, seven times in the deposit arm and twice in stock. The benchmark now records a Builder starting a harvest on the exact tile so subsequent games can distinguish harvesting from other resource changes. Of the deposit arm's five losses of a *working* supplier, one tile became a district, one improvement was pillaged and three tiles retained their resource but lost their improvement.

### Follow-up candidate for first customer buildings

Across the ten 25-turn censuses of the first lightweight game, two supplied Bakers had a functioning, adjacent City Center missing its Granary. One of those Quarters had also completed a Mill by turn 250. The supplied Tailors lacked a Harbor throughout its observed operating life, so changing Lighthouse construction alone cannot complete that chain.

On the five map-lab maps, 148 of the 4,489 clearable Quarter sites had both Tailors Base and an adjacent empty Coast tile. This conservative Harbor-footprint count requires a tile free of districts, features and resources. Of those 148 opportunities, 144 also had a neighboring bonus resource. However, 602 other clearable sites had both a bonus and an empty Coast tile without any Tailors Base. Even near water the actual source matters. The controller now reports clear-coast footprints at foundation wherever the observer captured terrain, including how many had usable owned Base at the same time.

The diagnostic `--customer-buildings` option adds a stock major-leader Buildings preference for each Stage 2 customer and its unique replacements, read from the gameplay definitions. On the standalone map that selects Granary and Lighthouse. The current stock database had no preference rows for either. The traced native selector doubles the building value on a positive accumulated preference, which makes this a broad investment across the empire. Measure customer construction, actual Services and the cost to competing investments before deciding whether to ship it. Real Strategy offers a narrower alternative if broad investment proves costly: a stock Lua strategy condition can activate the same preference for a player with a ready chain. [Building preference trace](../research/mods/csc-ai-native-production-analysis-20261028.md)

### Can the Quarter guide an ordinary Builder?

The stock Farm beside Korea's Seowon provides a useful reverse direction. Ghidra shows the city values a proposed improvement at the specific plot, follows the improvement's adjacency rows, reads neighboring district identity/completion/pillage state and weights the yield before the ordinary Builder job is selected. This supports a private-yield experiment with no Lua or CE. Each registered Stage 2 Base supplier gets one private unit per neighboring Quarter, or two for a selective resource-only family. The six standalone rows include Tailors Flax Farms and Cotton Plantations even though those families are weak predictors of a good site when placing the Quarter first. Check the actual fraction of owned Base deposits improved and any extra empty Farms before promoting the option. The test control is `--supplier-jobs`.

The first two loads on seeds 171124601 and 171124605 stopped at turn one. The intended Builder rows were absent. The pinned connector action runs at 3001, while the gameplay transaction processor populates `CSC_MaterialTransactionInputHosts` at 800010 to include late Workshop improvements. The corrected candidate runs immediately after that processor. Replaying this order in a copy of the live database produced zero rows before reconciliation and six afterward. Both startup attempts are excluded from play results.

The corrected first-seed game loaded all six rows and the Granary and Lighthouse preferences with CE disabled. Farms receive one private unit for either Quarter, Pastures two for either, and Plantations two for Bakers and one for Tailors.

### Seed 171124605 at turn 250

Stock AI completed 16 Bakers and 14 Tailors across the five original AI empires. One Bakers had both a working Base and a completed customer. No Tailors did. Nine Bakers and six Tailors touched a completed mapped customer. Twelve Bakers and all 14 Tailors had a functioning Stage 2 producer. The game recorded zero active Service links across 249 observations. Popup-free turns averaged 6.22 seconds and peaked at 17.29 across 197 intervals.

Of the 15 Tailors foundations, nine touched a clear coastal tile. Only two also had a usable owned Base. Both available coastal tiles lay outside the empire's borders when the Quarter went down. The turn-83 Quarter (plot 2286) had raw Flax and later a working Textile Workshop and a Theater Square. The Flax still lacked a working improvement at the turn-200 census and became ineligible as a supplier on 215. The turn-112 Quarter (plot 2679) still had both Sheep and a working Textile Workshop at turn 250, but its Sheep remained unimproved. These sites give the native Builder treatment two distinct missed opportunities to compare against.

The no-CE deposit treatment finished with four supplied Bakers beside a customer across 17 completed Bakers, up from one across 16. All four also had a functioning producer and Stage 2 customer building. Six Storekeeper links delivered 289 active chain-turns across the run. Tailors finished at zero supplied pairs across 15 completed Quarters. Seven of its 15 foundations touched a clear coast tile and two had usable owned Base, but the two groups did not overlap. There were ten losses of the last viable deposit, six to district coverage. Three of the other four coincided with a harvest by the same player on that exact tile. A further two working-supplier losses involved pillaged improvements.

### Shipping decision after the two no-CE games

The raw-resource cue is now part of CSC's ordinary AI connector SQL. Across the two seeds, supplied Bakers with a completed customer rose from **2/33 (6%) to 11/37 (30%)**. Tailors finished at **1/31 stock and 1/32 treated**. Total observed Service link-turns rose from **73 to 498**. Stock produced 50 Storekeeper and 23 Sacristan link-turns. The treatment produced 466 Storekeeper and 32 Innkeeper link-turns. On the first seed all five treated AI empires ended with a supplied Bakers beside a customer, compared with one stock empire.

| Turn-250 comparison | Seed 171124601, stock → lightweight | Seed 171124605, stock → lightweight |
| --- | ---: | ---: |
| Completed Quarters with working Base and customer, both types | 2/34 → 8/37 | 1/30 → 4/32 |
| Foundations without usable owned Base | 26/37 → 21/36 | 24/32 → 25/33 |
| Losses of last working supplier / last viable deposit | 6/3 → 5/9 | 2/5 → 6/10 |
| Actual Service link-turns | 73 → 209 | 0 → 289 |
| Mean elapsed turn, seconds | 5.41 → 6.29 | 6.22 → 6.36 |
| Maximum elapsed turn, seconds | 16.60 → 20.62 | 17.29 → 21.09 |

Each column uses the same starting save and the common observations for its two arms. The timed intervals exclude popups (193 and 195 respectively). Total turn time includes the empires' different development. Both games ran with the Firaxis core and zero advanced publications. The source integration reproduced the qualification SQL rows, including adjacency identifiers and weights, when compiled against the game database. Gameplay transaction and modifier values matched. The advanced comparison uses the same resource cue and a CE-enabled opening with the same starting map and roster.

**Weak Quarter foundations.** Both treatments recorded 69 foundations across the five AI seats on each of the two maps combined. Reading the neighbor rows at foundation and matching their undistricted resources to each Quarter's Base tags, regardless of ownership, gives the following counts. This includes resources that could later be bought or acquired through border growth.

| Founded with no mapped Base on any neighbor | Stock CSC | Lightweight CSC |
| --- | ---: | ---: |
| Bakers | 21/35 | 10/38 |
| Tailors | 26/34 | 24/31 |

Of the 34 lightweight sites without any adjacent Base, 23 had an adjacent bonus resource (eight Bakers and fifteen Tailors). Another twelve foundations had mapped Base nearby but none usable and owned at that moment. Keep these acquisition opportunities separate when measuring weak-placement suppression. A proposed stock-only test is a small flat negative private adjacency on the Quarter itself, retaining the existing positive location cues. Check the signed value in Civ's comparison on a bare and a well-supplied site before judging the rule by full-game placements and operating Services.

Every 25 turns the controller counted the mapped suppliers beside each AI Quarter, including Quarters under construction. The table counts a Quarter once per material class at each census across both games. A Quarter that kept its supplier for 100 turns can appear four times. This captures how often the AI had access to a supplier during development.

| Across twenty censuses per treatment | Bakers, stock → lightweight | Tailors, stock → lightweight |
| --- | ---: | ---: |
| Quarter with accessible Base | 30 → 99 | 38 → 23 |
| Quarter with working Base | 9 → 60 | 14 → 14 |
| Quarter with accessible Spec | 9 → 36 | 7 → 6 |
| Quarter with working Spec | 7 → 31 | 7 → 3 |

For Bakers, the treatment improved access to both material classes well before the endpoint. For Tailors, fewer observations had access to Base and the number with a working Base stayed level. This favors testing a more selective Tailors placement cue. More Quarters also had suppliers they could lose. Counts with an accessible Base or Spec nearly doubled across the two Quarters (84 → 164, counting each class separately). Of the treatment's 19 last-deposit losses, 18 involved Base and eight showed a district on the supplier tile.

### What advanced planning adds on seed 171124601

The advanced game used the same SQL as the lightweight game, with the full CE planner enabled in single player. It started with the same terrain, rivers, resources, leaders and starting positions. The CE mod stack required its own turn-one save. The three-way comparison uses 199 common Service observations and 191 common popup-free turns.

| At turn 250 | Stock CSC | Lightweight CSC | Advanced CSC |
| --- | ---: | ---: | ---: |
| Bakers with working Base and completed mapped customer | 1/17 | 7/20 | **19/26** |
| Tailors with working Base and completed mapped customer | 1/17 | 1/17 | **3/6** |
| New foundations with usable owned Base | 11/37 | 15/36 | **31/31** |
| Last viable deposit losses | 3 | 9 | 1 |
| Storekeeper active link-turns | 50 | 177 | 942 |
| Innkeeper active link-turns | 0 | 32 | 139 |
| Sacristan active link-turns | 23 | 0 | 9 |
| Total active Service link-turns | 73 | 209 | **1,090** |
| Mean / maximum turn, seconds | 5.38 / 16.60 | 6.25 / 20.62 | **8.07 / 24.82** |

The advanced run recorded 26 Bakers and five Tailors foundations. All five Tailors began with at least +3 current Production and Gold adjacency; one had a clear coast tile next door. No completed Tailors had a Harbor at the endpoint. Twelve Bakers still had a working Stage 2 chain at the endpoint.

Only one last deposit was lost in the advanced game. The 22 interruptions to a working supplier included 11 pillaged improvements, nine where the resource remained without its improvement, one mixed loss and one covered by a district. The full planner averaged 1.72 seconds of measured processing across 249 turns and peaked at 3.95 seconds. The advanced and lightweight games ended with 59 and 52 cities, respectively.

### Second matched advanced comparison, seed 171124605

The advanced game reached turn 242, when the observer civilisation was eliminated. We preserved its turn-240 map in the Load Game menu and archived the turn-242 autosave. Turn 225 is the last complete Quarter census shared by all three runs. The two no-CE arms also have their ordinary turn-250 results above. Reproduce the three-way comparison with `lightweight_results.py --through 225` and the three arm directories.

| At turn 225 | Stock CSC | Lightweight CSC | Advanced CSC |
| --- | ---: | ---: | ---: |
| Bakers with working Base and completed mapped customer | 0/12 | 2/15 | **22/28** |
| Tailors with working Base and completed mapped customer | 0/15 | 0/13 | **5/6** |
| New foundations with usable owned Base | 5/28 | 7/29 | **30/30** |
| Last viable deposit losses | 4 | 8 | 1 |
| Storekeeper active link-turns | 0 | 230 | 1,538 |
| Innkeeper / Sacristan / Stage 4 Tailors active link-turns | 0 / 0 / 0 | 0 / 0 / 0 | 270 / 21 / 76 |
| Total active Service link-turns | 0 | 230 | **1,905** |
| Mean / maximum turn, seconds | 5.67 / 17.29 | 5.63 / 15.70 | **7.51 / 24.29** |

All three results cover the same 224 Service observations and 175 popup-free intervals. Three of the six completed advanced Tailors had both material classes. The single lost last deposit had a Wonder on its tile. The advanced planner averaged 1.41 seconds per turn and peaked at 3.00 seconds. The stock, lightweight and advanced empires held 47, 42 and 53 cities respectively.

On this seed's turn-one map, 55 of 889 clearable sites touched both a Tailors Base and a clear coastal tile, using 26 distinct sources. A local terrain threshold distinguished Base sites in 105 of 235 sampled neighborhoods with a Base opportunity. These are possible locations before settlement and border growth. They give the no-CE city-specific experiment a second map with relevant layouts.

### Can ordinary Builder and customer preferences complete more chains?

The first turn-250 replay added six stock improvement adjacency rules derived from the material hosts and a major-leader building preference for the Granary and Lighthouse. The live game database contained all eight entries. Each arm used the same starting save on seed 171124601. Working plots count distinct owned, intact suppliers alongside completed Quarters.

| At turn 250 | Stock CSC | Lightweight CSC | Lightweight plus Builder and building preferences |
| --- | ---: | ---: | ---: |
| Bakers with working Base and completed customer | 1/17 | 7/20 | 3/18 |
| Tailors with working Base and completed customer | 1/17 | 1/17 | 0/15 |
| Distinct working / present Base plots, Bakers | 1/4 | 10/11 | 5/5 |
| Distinct working / present Base plots, Tailors | 2/5 | 2/4 | 3/4 |
| Bakers with functioning first customer building | 9 | 12 | 10 |
| Tailors with functioning first customer building | 1 | 0 | 1 |
| Active Service link-turns | 73 | 209 | 31 |
| Last viable deposit losses | 3 | 9 | 8 |
| Mean / maximum seconds per turn | 5.35 / 16.60 | 6.25 / 20.62 | 5.68 / 16.68 |

The extra preferences left eight of nine surviving Base plots working, but the empires retained fewer Bakers suppliers. Six Tailors had customers and three had working Base. Those groups did not overlap. The only active Service was one Storekeeper for 31 turns. This result favors the simpler shipping treatment on this map. Timing uses 189 common popup-free turns and Service totals use 199 common observations. The endpoint is available in the Load menu as `CSC_LIGHT_171124601_JOBS_CUSTOMERS_T250`.

The second map (171124605) repeated the Tailors pattern. Three completed Tailors had working Base, six had mapped customers and none had both. The extra preferences did produce long-lived Bakers Services here.

| Seed 171124605 at turn 250 | Stock CSC | Lightweight CSC | Plus Builder and building preferences |
| --- | ---: | ---: | ---: |
| Bakers with working Base and completed customer | 1/16 | 4/17 | 3/18 |
| Tailors with working Base and completed customer | 0/14 | 0/15 | 0/15 |
| Distinct working / present Base plots, Bakers | 1/2 | 4/7 | 4/6 |
| Distinct working / present Base plots, Tailors | 0/1 | 0/0 | 3/3 |
| Active Service link-turns | 0 | 289 | 530 |
| Last viable deposit losses | 5 | 10 | 7 |
| Mean / maximum seconds per turn | 6.11 / 17.29 | 6.25 / 21.09 | 6.01 / 20.41 |

Four Storekeepers provided 505 link-turns, one Innkeeper 20 and one Groundskeeper five. The comparison uses 249 common Service observations and 190 common popup-free turns. Across both seeds the added preferences produced more operating Tailors Base suppliers and 561 Service link-turns versus 498 with the simpler rules. They also reduced completed Bakers with a working Base and customer from **11 to 6** and yielded **zero supplied Tailors customer pairs**. Keep the simpler default. The useful part to revisit is whether the Builder cue alone can serve Quarters that already have a credible customer.

Of the six supplied Tailors across these two games, three worked Flax and three worked Cotton. Only two had an empty sea-coast footprint recorded beside them at foundation. The first map's plot 2691 bordered unowned coast. On the second map, player 5's Tailors on plot 2375 bordered its own clear coast on 2448, ended with working Cotton and never produced a Dockmaster. That save has a concrete customer follow-through case to inspect.

### Discouraging Quarters in cities without a Base opportunity

This Workshop-compatible experiment checks whether a city has any plausible Quarter footprint within three tiles beside its type of Base. It considers unowned land, district slots and unlocks that could come later, and a supplier just beyond the third ring. A city with unexplored possibilities stays eligible. Reviews share their map reads across all missing Quarter types and visit at most one city per original major AI each turn, oldest first, with at least 12 turns between visits to the same city.

Where the surrounding land is known and no opportunity exists, the city-center property enables a stock negative terrain adjacency for that Quarter. The trial uses −1 private yield per neighboring terrain, ordinarily −6 per footprint. This is a weight in Civ's site comparison. The mod does not issue a production order.

**Seed 171124601, turn 30, Firaxis core only.** In player 2's city 131073, Tailors on plot 1528 read −6 with the natural penalty active, 0 when withdrawn and −6 when restored, all on the same turn. In player 3's supplied city 65536, the legal Tailors site on plot 675 read +3 throughout. This measures the prospective adjacency input. Compare actual foundations, submitted jobs and supplied customer pairs in the matched games to judge the production decision.

Two turn-250 runs started from the same save with the same city review. The control only recorded the classification. Both ran the shipping lightweight rules with CE absent.

| Seed 171124601 | Review only | Review with city penalty |
| --- | ---: | ---: |
| Foundations in cities last assessed as lacking any Base opportunity | 5 | 2 |
| Bakers founded without any mapped Base next door | 5/20 | 4/20 |
| Tailors founded without any mapped Base next door | 12/18 | 11/16 |
| Weak foundations in cities where a supplier layout existed elsewhere | 12 | 12 |
| Completed Bakers with working Base and customer | 4/21 | 3/19 |
| Completed Tailors with working Base and customer | 1/20 | 1/14 |
| Storekeeper link-turns | 269 | 285 |
| Losses of last viable deposit | 10 | 12 |
| Mean / maximum popup-free turn, seconds | 6.71 / 19.55 | 6.06 / 17.92 |

The penalty reached 204 city/Quarter reviews across this game. The two remaining no-opportunity foundations were Tailors on turns 170 and 178, following active penalties since turns 126 and 165 respectively. Another weak Tailors was in a partly explored city. The counts use 249 common Service observations and 194 common timed turns. On turn 67, Stavanger submitted Tailors for 486 production bid points in the control game and a Preserve for 368 in the treatment game. Its control turn-64 save was retained for a same-state replay.

**Isolated Stavanger decision.** Both replays loaded the same archived autosave (`25fa828c49fd`), attached the same dormant terrain rules, and changed only Stavanger's Tailors property. The gameplay entry set it at core turn 63 as the turn-64 autosave resumed. With the property off, the native AI again submitted the 486-point Tailors bid on 67 and put production into Tailors on 69. With the property on, the log contained no district submission for Stavanger on 67, and on 69 the city put production into a Monument. The Settler (379) and Walls (42) submissions on turn 66 matched in both replays. The local penalty can therefore change an actual production decision in the Firaxis-only game. Which alternative wins depends on the other options in that particular game. [Replay tool](../../tools/native_ai/late_placement/no_base_bid_replay.py)

| Seed 171124605, same opening, turn 250 | Earlier lightweight run | With city penalty |
| --- | ---: | ---: |
| Bakers founded without Base next door | 7/18 | 6/19 |
| Tailors founded without Base next door | 12/15 | 11/16 |
| Completed Bakers with working Base and customer | 4/17 | 1/16 |
| Completed Tailors with working Base and customer | 0/15 | 1/16 |
| Storekeeper link-turns | 285 | 211 |
| Losses of last viable deposit | 10 | 11 |
| Mean / maximum popup-free turn, seconds | 6.31 / 21.09 | 6.67 / 40.19 |

This second control used the established lightweight deposit rules and the same opening save. It predates the diagnostic city review. Of the treatment's 17 weak foundations, 11 occurred in cities with a recorded Base opportunity, four in cities assessed as lacking one, and two with incomplete visibility. Both games reached 250. The trial preserved the turn-250 autosave and physical census. Its final UI clock and Service observation were at 249, leaving 248 common Service observations and 194 common timed turns.

Across both maps, the city penalty reduced weak foundations from 36/71 to 32/71. Completed Quarters with a working Base and customer fell from nine to six. With 23 of the 32 weak foundations in cities that had identified an alternative, the next experiment should distinguish the sites *within* those cities. Keep the broader city penalty outside the shipping default pending better chain outcomes.

### Can an unbuilt improvement mark the right deposit?

A disposable improvement for each Quarter accepted the Base resources in the loaded gameplay tags. The stock database registered six valid resource types for Bakers and three for Tailors. A standard Builder could construct the probe improvement. Two cold loads of the same turn-50 save varied one setting, the private yield for placing a Quarter beside that improvement. Player 3 could place Tailors on plot 754 beside owned, unimproved Flax on plot 827. The stock Builder eligibility check accepted the proposed improvement on that Flax.

| State of the same Flax tile | Zero-weight control | +12 private adjacency rule |
| --- | ---: | ---: |
| Unimproved, marker legal | +1 | +1 |
| Marker present | +1 | +13 |
| Marker removed | +1 | +1 |

The proposed improvement contributes to the prospective district adjacency while it physically occupies the supplier tile. Its resource restrictions alone give the untouched deposit no signal through this rule. A scripted replacement with the ordinary Farm would retire the marker bonus. The probe ran with the Firaxis core and used a diagnostic placement on a disposable save. It measured the input to district siting on an AI-owned plot. Human action hiding, automatic replacement and overall construction outcomes were outside this test. Keep the probe outside the player build. [Probe SQL](../../tools/native_ai/late_placement/possible_supplier.sql) and [matched replay](../../tools/native_ai/late_placement/possible_supplier.py).

### Using two stock cues to distinguish sites inside a city

An offline survey searched both opening maps for signed counts of neighboring terrain and features. In each sampled radius-three neighborhood, at least one clearable site touched a mapped Base and at least one missed. A rule succeeded if its highest-scoring Base site strictly beat every site without Base. The city-specific choice used the real resource tags as its answer key. The counts include overlapping hypothetical cities and land outside future borders. A successful rule can change one component of Civ's ranking.

| Map neighborhoods distinguished | Bakers, out of 565 | Tailors, out of 522 |
| --- | ---: | ---: |
| One signed terrain count | 464 (82%) | 366 (70%) |
| Up to two signed terrain counts | 541 (96%) | 455 (87%) |
| Up to two signed terrain or feature counts | 557 (99%) | 514 (98%) |

Start with the terrain-only option because both signs have reached live stock previews. A bounded city review can read the underlying private adjacency, choose up to two small offsets, and re-read the strongest qualifying site and strongest unsuitable rival. Prefer sites where the supplier can be retained and a customer can fit. Clear stale rules when borders, deposits or districts change. The decision test is whether weak foundations move to supplied sites in the same city while sound investments elsewhere continue. [Reproduce the map calculation](../../tools/native_ai/late_placement/city_pair_coverage.py)

Two early control decisions provide replay targets on seed 171124601. Nidaros had a Bakers opportunity on turn 15 and founded on plot 935 without adjacent Base on 16. Tenochtitlan had a Tailors opportunity on turn 26 and founded on plot 750 without adjacent Base on 37. For each, first verify that an alternative supplier layout was visible, owned and legal at the native decision. The city review includes future purchasable land.

### Live trial of signed city-specific terrain cues

The experimental no-CE policy compares owned, legal Quarter footprints in one city, using visible, owned Base deposits from the gameplay tags. It favors an existing Stage 2 customer, then a possible coast footprint for a coastal customer, Specialty and multiple Base deposits. River crossings and the Wind Mill's own-tile Hills bonus break ties according to the loaded Production rules. It takes the better Mill alternative on a hill by a river. A clear coast tile is an opportunity to investigate when planning the Harbor.

For a city with both supplied and unsupplied candidates, the policy first looks for one terrain rule that places a best-layout site strictly above every site without Base on that component. If one cannot distinguish them, it tries signed sums of two different terrain counts. Each matching neighbor adds or subtracts two private yield units. Different cities and Quarter types can choose different rules. The scheduler checks one city per original major AI per turn, at least 12 turns apart for each city. Ineligible or no-longer-useful rules switch off. Quarter foundation and city transfer also withdraw the affected rules. [Site selector and switches](../../tools/native_ai/late_placement/paired_material_layout.lua)

On seed 171124601, three turn-50 replays used the same turn-one save, ordinary CSC and the Firaxis core. The dynamic arm and fixed river arm are independent. The fixed arm adds one private yield for a riverbank to Quarters that receive river Production directly. In the loaded catalogue this qualified Tailors. It leaves the Water and Wind Mill choice in Bakers untouched.

* Nidaros founded Bakers on plot 935 on turn 16 with and without the dynamic rules. The turn-15 review found four legal owned sites and zero beside owned Base.
* In player 3's second city, the turn-24 review picked plot 1119 from six legal Bakers sites. Two had Base. The next turn Civ founded on 1119 instead of control plot 1047. Both adjoined the same Flax.
* Tenochtitlan had seven legal Tailors sites on turn 26. Only plot 675 touched owned Base. The city activated a positive Tundra rule, submitted a 249-point Tailors bid on turn 30 and built on material-free plot 750 on turn 37. Its cue was withdrawn on foundation.
* In player 4's city 65536 at turn 50, the policy naturally combined negative Coast with positive Plains for Bakers. Switching both rules off and on moved the private site previews from 4 to 2 and back to 4 on plot 2611 and from −6 to 0 and back to −6 on 2685. Another city's Bakers site stayed at 2 throughout. At turn 25 a separate check had already left a different AI player's site unchanged. The score belongs to the city, district and active rules. [Paused stock preview](../../tools/native_ai/late_placement/paired_material_preview.py)

The Lua selector took an average of 0.32 ms, a 95th percentile of 0.99 ms and a maximum of 2.70 ms over 1,087 mixed neighborhoods on the two opening maps. These are per-neighborhood medians of five choices in standalone Lua 5.1, using the saved terrain and Base distributions. The benchmark excludes Civ API reads, modifier updates and city scheduling. [Reproduce the offline timing](../../tools/native_ai/late_placement/paired_material_cost.py)

| At turn 50, seed 171124601 | Lightweight control | Dynamic city cues | Fixed river cue only |
| --- | ---: | ---: | ---: |
| Bakers foundations with owned Base / all | 2/4 | 1/2 | 2/4 |
| Tailors foundations with owned Base / all | 0/1 | 0/1 | 0/1 |
| Tailors foundations on a river | 0 | 0 | 1 |
| Completed Quarters with working Base and a completed customer | 1 | 1 | 1 |
| Mean / maximum popup-free turn, seconds | 2.10 / 3.78 | 2.07 / 3.34 | 2.06 / 3.16 |

The comparison uses 39 common popup-free turn intervals. In the dynamic game there were 68 city/Quarter reviews, 25 with a useful cue. Thirteen switches activated one rule, eight activated a pair and four withdrew all rules. The only Tailors founded with the fixed river cue was in player 3's city 196610 on turn 36 (river plot 1121, zero owned Base). The control's Tailors was in a different city. These results leave the river cue experimental.
