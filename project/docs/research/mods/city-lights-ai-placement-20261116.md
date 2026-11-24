# City Lights AI tuning and district placement

**16 November2026, Problem2.1.** The installed City Lights includes substantial
native SQL AI guidance and economic assistance. Its AI rows are present in the
last closed CSC replay database. Our City Lights-enabled stock-AI comparisons
therefore include City Lights' own assistance as well as normal engine behaviour.
No game was launched and no gameplay/tuning file was changed for this inspection.

## Registered and loaded package

Workshop2190389813, mod ID95b955fc-2dd1-41c5-989e-0265d98a28bd, manifest version1.
`City Lights.modinfo:387` registers `Gameplay/COREX_Civ_Ai_Updates.sql` at load200
when the **City Lights setting** `CL_GAME_MODE=Singleplayer` is selected. That
setting defaults to Singleplayer (`Gameplay/00_COREX_GameData.xml:14`). It is a
mod configuration switch, not a test of whether the current application has a
multiplayer session. The source file contains27 AI modifiers and six preference
lists. The package contains no Lua or DLL files: these mechanisms use native
rules and modifiers. Unique-district preferences also occur in the civilization
integration SQL outside that singleplayer action.

Source AI SQL SHA256:
`7260b4fe113d0d204c41d0f684246851087a53642b3965d27064c7b513c718fa`.
[Read-only loaded definitions, exact queries and source hashes](city-lights-ai-placement-20261116.json).
The database snapshot is from the closed `all-partners1-survey150` replay; the
queries establish loaded definitions and attachments. Actual magnitudes in the
native selector would need a controlled trace, as in our customer-signal replay.

## Explicit AI guidance and assistance

| Mechanism | What the installed code does | Source |
| --- | --- | --- |
| District preferences | Assigns listed leaders urban, rural or hybrid traits. Urban favours the three Borough tiers and marks rural towns unfavoured; rural reverses that; hybrid favours Boroughs. These are boolean `Favored` entries with default Value0, not an authored final site score. | AI SQL231–305,413–454 |
| Urban AI adjacency | Urban-trait AI gets additional Food adjacency of1/2/3 for Borough tiersA/B/C through `EFFECT_DISTRICT_ADJACENCY`. The identifiers/descriptions say Production, but the actual YieldType is **Food**. | AI SQL57–59,93–104,386–388 |
| Rural AI adjacency | Rural and hybrid AI get +1 Gold per relevant adjacent improvement: Farms/Pastures/Plantations for Farming Towns; Mines/Lumber Mills/Quarries for Mining Towns; Fishing Boats/Fisheries/Camps for Fishing Towns. | AI SQL67–75,118–171,393–411 |
| Rural construction | Rural-trait AI gets +40% district Production for each of the three rural town types. | AI SQL64–66,112–117,390–392 |
| Urban maintenance relief | Base Borough tiers give AI cities +10/+15/+20 Gold, matching those tiers' maintenance. | AI SQL24–29,60–62,105–110; Core SQL157–159 |
| Urban amenity relief | TierA/B/C amenity penalties are changed to human-only. Their core amounts are−3/−5/−7. | AI SQL33–40; Core SQL1517–1519 |
| Free building progression | AI cities with the corresponding tier1 building are granted tier2 Culture/Gold/Science buildings after Guilds for BoroughA, Urbanization forB and Cold War forC. The subject gates require both the tier1 building and an AI player. | AI SQL9–22,45–55,81–91,173–208 |
| Building preferences | Separate leader traits favour Science, Gold or Culture branches and mark competing branches unfavoured. | AI SQL307–381,431–433,456–513 |
| Unique districts | Additional favoured-item entries cover Gyoson, Troyu, Frontier Town, Xian, Elysee, Fuerte, Tsikhe and Upapitha; Venice districts are favoured for minor civilizations. | Civs SQL162–175 and subsequent civilization blocks; Civ_NF_3 SQL167–171 |

These AI-only yield/production/building effects are real gameplay advantages,
whereas our private placement yield is a separate signal. Their gates and trait
assignments matter: the urban Food and rural Production bonuses do not apply to
every leader. Human/AI identity uses inverse/noninverse
`REQUIREMENT_PLAYER_IS_HUMAN`, confirmed in the loaded requirement definitions.

## Ordinary placement economics and constraints

Core SQL adds normal adjacency inputs for all players:

- Each of the three base Borough types has **+1 Production per adjacent district**.
  Typed neighbours add further yields; examples include Campus/Science, Holy
  Site/Faith, Hub or Harbor/Gold, Theater/Culture and Industrial Zone/Production.
  These typed bonuses scale with Borough tier. Loaded generic Production rows
  remain+1 for all three base types.
- Rural towns have their own typed positive adjacencies, including Holy Sites
  and Encampments. They also cause−1 adjacency on several nearby vanilla
  specialty districts. This is attached to the **receiving vanilla district**,
  rather than a negative native adjacency row on the rural town itself. The
  loaded32 negative links cover11 vanilla/unique recipient types; none targets
  a CSC Quarter.
- Urban and rural types are mutually exclusive within a city. All six base
  types have `RequiresPopulation=0`; rural types allow multiple copies and
  have `NoAdjacentCity=1`. Boroughs are one per type per city and have
  `Aqueduct=1`; Fishing Town additionally has Coast/AdjacentToLand flags.
  These flags and exclusion rows constrain eligibility before site preference.
- Boroughs also have Appeal-dependent Housing, providing another ordinary
  native valuation input. Buildings, policies, civilization integrations and
  other gameplay effects add further local benefits.

See Core SQL154–185,190–385,388 onward and715–737. The native engine consumes
these inputs through its ordinary eligibility and valuation paths; no separate
City Lights Lua placement planner is shipped in this installed package.

## Consequences for CSC

Our +1 private-yield partner adjacency complements existing native siting
incentives. A Borough beside a Quarter can already receive generic Production
adjacency, and urban-trait AI has an additional Food incentive to cluster.
Rural providers are encouraged toward their mapped improvements, which can also
make them natural neighbours for resource-dependent Quarters. The loaded City
Lights rural adjacency penalties do not directly cancel CSC Quarter adjacency.
Material protection remains necessary when districts compete for a footprint.

Keep City Lights configuration fixed in comparisons. Its free upgrades,
maintenance/amenity relief and other advantages affect construction patterns
and empire yields, so economic outcomes should be interpreted with that package
included. The recent zero/+1/+4/+8 customer-signal arms already held City Lights
constant, preserving their causal comparison. No increase to our placement bonus
or extra interaction definition is justified by this source inspection alone.


## Customer-placement follow-up

The [latest Hub audit](csc-ai-commercial-hub-audit-20261116.md) highlights another
part of the loaded CL rules: `COREX_Core.sql` attaches−1 Gold from each adjacent
rural district to Commercial Hub and Harbor. These penalties target customers,
while the preceding finding about no rural penalty on CSC Quarters remains true.
Include them when comparing a Quarter-adjacent customer site with an alternative;
a river and several districts need not produce the naive unmodified Gold total.

## Revised Continents comparison, 23 November 2026

The control and treatment both ran main CSC guidance, Dev CE `6244570`,
the native private yield and the same City Lights stack. The only differing
CSC file was `CSC_AI_EconomyAdapters.lua`, where the switch enabled the
bidirectional partner planner and stronger supply-backed layout bids in
the treatment. Both `Modding.log` files record loading `COREX_Civ_Ai_Updates.sql`.

Among the five AI players, City Lights assigns Pachacuti, Lautaro and Tamar
the rural trait and assigns Bolívar and Gilgamesh the hybrid trait. Rural
leaders favour the town types and receive +40% Production toward ordinary
rural districts. Both groups receive the improvement-based Gold adjacency
for those types. Farming Towns open at Irrigation and use no population
district slot. Their ordinary economy includes a Farmer on completion and
Food for incoming domestic routes. The Feudalism building can add a route
slot in a city without a Market or Lighthouse. Tamar's separate favoured
district row is for Tsikhe. The Georgia variant replaces the Mining Colony,
uses no population slot, grants a Miner, and adds mountain Production
adjacency and conditional Faith and Tourism. The ordinary rural AI modifier
rows name the base district types. The contribution of individual modifiers
to the observed native score gaps remains unmeasured.

Rural Communities A/B/C and Tsikhe were the returned winner in 570 of 762
recorded outscored Quarter comparisons in control and 742 of 975 in the
treatment. The treatment had 172 same-tile losses in that group. Among
the 36 losses to Rural Communities for the stronger early layout bids,
13 used the same tile. Counts are native comparisons and can repeat across
turns for one city. The remaining differences show city-wide investment
competition between distinct footprints.

CSC tagged those four types as goods providers for both Quarters. Both arms
loaded the +1 private placement yield for the City Lights district beside
either Quarter. The completed-district histories record 13 provider links
in control, all Bakers, and 11 in the treatment, including three Tailors
links. [Revised run and decision evidence](csc-ai-stage-investments-20261121.md#revised-continents-result).

### How the Gold and Production bonuses enter the game

City Lights attaches the Gold rule to rural and hybrid AI leaders through
`MODIFIER_PLAYER_CITIES_IMPROVEMENT_ADJACENCY`. Firaxis ships that modifier type
in Byzantium & Gaul, where Gaul's Commercial Hub gets minor Gold adjacency
from Mines. City Lights supplies its own improvement lists and sets
`Amount=1`, `TilesRequired=1`. For example, two Farms and one Pasture give a
completed Farming Town +3 ongoing Gold adjacency. The bonus belongs to the
district, requires no citizen working those tiles, and grows as matching
improvements are added. The normal Farming Town bonus to nearby improvement
tiles is a separate effect. See City Lights `COREX_Civ_Ai_Updates.sql` lines
67–75, 118–171 and 393–411, and Firaxis `Byzantium_Gaul_Modifiers.xml` lines
47–52 and `Byzantium_Gaul_Civilizations.xml` lines 516–544.

The rural-only +40% construction modifier enters the native district forecast
through build time. In the tested Windows XP2 build (SHA256
`4de40abf7c739f53c1f3f825863ace84dc220e5a42d87620e56fceaf3fbd4dc8`),
`AdjustDistrictProduction::Apply` resolves the player's buildable district and
stores the rate in the city build queue's per-district array at offset `0x2d8`
(write RVA `0x8c3aa6`). District `GetTurnsLeft` reads that array (RVA
`0x0fe6f0`). The ordinary AI district evaluator calls `GetTurnsLeft` at RVA
`0x3e2928` and passes the estimate plus unlock delay into `NetValue` at RVA
`0x3e2979`. Faster construction brings the benefits forward in the forecast.
The leader's explicit district preference is a separate input. This static
trace establishes the route into the estimate. The observed win margins above
still combine all inputs. See [district score anatomy](https://github.com/hennogous/civ6-ai/blob/main/references/engine/district-score-anatomy.md#how-do-construction-bonuses-affect-the-forecast).

### Would a higher bid save contested Tailors sites?

The revised Continents treatment recorded 13 same-tile losses to Rural
Communities for strengthened layouts whose Quarter and customer were both
prospective. They came from two distinct plots. Match each loss to an exact
positive Quarter write and the joint selector in the same native generation,
then join the offered cell to the same turn's `CSC_AI_STRONG_QUARTER_LAYOUT`
record. The table reports how many published scores would strictly overtake
the observed winner if that Quarter alone received the additional utility.

| Quarter | Comparisons | Distinct plots | Gap range, native utility | +64 | +128 | +160 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Bakers | 10 | 1 | 1,247.54–2,500.94 | 0 | 0 | 0 |
| Tailors | 3 | 1 | 123.11–135.94 | 0 | 1 | 3 |

All three Tailors comparisons were at Bolívar's owned +2 site on plot 1934
on turns 171–173. It had Base and Specialty supply and a prospective Theater
Square footprint on 1933. The city had no free population district slot. The
Farming Town ranked first at roughly 1,252 utility each time. The exact
observed Quarter writes show no other strengthened Tailors offer for that city
before those decisions. The targeted customer trace supplied no comparable
Farming Town score for an alternative tile at those decisions. A Spaceport
occupied 1934 on turn 194.

Across all positively adjusted Tailors offers, 107 same-tile losses to a
Rural Community came from five candidate plots. The only four comparisons
within 160 utility were on plot 1934, including one ordinary offer on turn
120 whose gap was 117.07. By turn 250 a Rural Community had occupied zero
of the five disputed tiles. A Spaceport and a Commercial Hub occupied two,
with the other three showing no subsequent foundation.
City Lights' native `NoAdjacentCity=1` rule removes these rural districts
from the direct competition at City Center-adjacent sites such as a Bakers
Storekeeper pairing with a Granary.

On these records a +64 same-tile boost never changes a Tailors result.
A +160 boost changes the score order for one distinct Tailors site, while
its strengthened layout is waiting for capacity and the land stays free
of City Lights construction. Keep current bid values until a replay case
has a strong, buildable Quarter and an actual close conflict for its
footprint. The broader comparison still includes competition for the city's
investment across different tiles.

Evidence is `audited-connection-result.json`, `Lua.log` and
`AI_CityBuild.csv` in the revised `continents-candidate` archive. Score
gaps are Q8 values divided by 256. The arithmetic holds the recorded scores
fixed. Reservation, production and construction use later decisions.

### Keep the spatial score for a qualified layout

The comparison at plot 1934 exposed where the score was lost. On turn 171
the ordinary economic quote with its building forecast was about 953
utility. Adjacency, materials and customer space contributed another 276.
The combined +2 cap reduced 1,229 to 900. The separate 216 utility for the
validated layout brought the final bid to 1,116, against the Farming Town's
1,252.

For a validated strong layout, cap the ordinary forecast before adding
adjacency, material and customer-spacing preferences. Reapply the signed
site subtotal and explicit protection penalty after the cap. The site
subtotal includes the native footprint adjustment or separately priced
purchase and displacement streams where applicable. The model keeps the
native invoice deduplication. The marginal Service and separate strong-layout
preference enter once. Ordinary layouts retain their combined cap for
forecast and siting. The recorded turn-171 inputs produce approximately
1,301 under the new ordering, including the same 216 for the layout and a
91-utility site cost. The fix uses the existing anchored qualification
and applies independently of the competing district family.

The scoring audit corrected four related boundaries. A ceiling-limited
Quarter carries its validated customer identity even when its separate
layout credit is zero. Continuity stores the ordinary bid for a one-round
missing-facts window, with no strong-layout or connection premium carried.
Customer-first backup value charges the connection difference once by
comparing the complete Quarter bids after removing the estimated contribution
of each already-priced link. The customer valuation caps the relative
forecast before applying the shared reference credit, preserving the intended
distance between the alternative and reference. The existing early-positive
guard and the final native score ceiling still apply.

### Turn-250 run with the installed CSC package

The controller verified the same Continents opening and used the same pinned
Dev CE DLL. It ran the installed CSC package with anchored connection guidance
and its diagnostics enabled. A later package diff found that the Bakers SQL
changed only in whitespace. The three AI Lua modules contained the substantive
gameplay-code changes, alongside a different mod identity, packaging and
presentation files. The comparison still covers all five AI corrections
together.

| AI outcome through turn 250 | Earlier run | Installed CSC |
|---|---:|---:|
| Bakers founded / completed | 18 / 17 | 15 / 14 |
| Tailors founded / completed | 2 / 2 | 1 / 1 |
| Prospective strong layouts with native score writes | 17 | 19 |
| Quarter sites built from those layouts | 0 | 3 |
| Exact planned customer pairs completed at those sites | 0 | 1 |
| Completed Quarter/customer opportunity pairs, all tracked layouts | 10 | 13 |
| Distinct realised Bakers Service chains, stages 2 / 3 / 4 | 12 / 4 / 0 | 10 / 6 / 2 |
| Distinct realised Tailors Service chains | 1 | 0 |
| Active Service link-turns across 200 common observed turns | 891 | 996 |
| Per-turn publisher wall time, average / maximum | 1.23 / 2.53 s | 1.14 / 2.29 s |

The two-Base Tailors layout on plot 2603 got a native best-site receipt and
was founded on turn 232. Its planned customer pair was still incomplete at
turn 250. At plot 1934, the Base-plus-Specialty Tailors layout also reached a
native best-site decision. A later same-tile comparison scored the Theater
Square at 1,778 against the Tailors at 1,035. The Theater Square was founded
on turn 142. The fixed-input comparison above measures the original score
clipping; the live run reached a different build decision on the same tile.

Evidence is in `Desktop/Codex/csc-ai-main-layout-scoring-20261123/continents`,
including the pinned inputs, endpoint save, `main-package-layout-comparison.json`
and `audited-connection-result.json`. Both runs recorded zero native faults.
The named turn-250 save also reloaded under the normal mod preferences. The
controller checked the pinned Dev CE provider, human control of the local seat
and parity across 222 structural census rows. See `reload-check/inspection-save.json`
beside the run directory.

At the endpoint, Score Victory was enabled with a 250-turn limit. The world
entered the Future Era on turn 241. Bolívar, Pachacuti and Tamar reached the
Future Era. Shaka, Gilgamesh and Lautaro reached the Information Era. See
`era-check-ui/era-and-victory.txt` for the saved game's own readings.

#### Why the run produced four fewer Quarters

| Original AI seats | Earlier run | Installed CSC |
|---|---:|---:|
| Distinct Quarter sites with a positive offer | 127 | 114 |
| Recorded comparisons of positive Quarter bids | 1,105 | 891 |
| Quarter bids outscored | 975 | 810 |
| Exact Quarter bid selected | 129 (11.7%) | 80 (9.0%) |
| Distinct Quarter sites with an exact bid selected | 27 | 20 |
| Quarter construction requests recorded | 23 | 19 |
| Requests completed / failed or cancelled / still submitted | 19 / 2 / 2 | 15 / 2 / 2 |

Comparison counts include repeats. Site counts use player, city, district and
plot. All 20 earlier foundations and all 16 new foundations joined to an
exact recorded bid selection at their site. The city production logs show an
unchanged count of failed, cancelled and outstanding construction requests.
The four fewer completed Quarters track four fewer requests.

Twelve foundations matched between the runs. Six earlier Bakers footprints
and two earlier Tailors footprints dropped out, while three Bakers and one
Tailors appeared elsewhere. Five of the six earlier Bakers tiles had no
recorded positive offer in the new run. The sixth, plot 2578, fell from +3 to
+2 direct adjacency in the last offers. The new city evaluating it founded a
Bakers at plot 2502. Both former Tailors tiles still received offers. Plot
3087 lost observed comparisons and remained unbuilt. Plot 3009 received a
wonder foundation on turn 209. These joins use the two runs' `Lua.log`,
`audited-connection-result.json` and `AI_CityBuild.csv`.

The first recorded change in the winning district and tile was Quito's
turn-100 packet. Its two-Base Bakers bid on plot 2528 rose from 680 to
783 utility with the same recorded economic quote, forecast adjustment,
site cost and linked customer. The earlier run selected a 728-utility
Mining Colony on plot 2232. The revised run selected the Bakers. It
still had to wait for city capacity and was founded on turn 124. The first
physical district divergence followed on turn 105.

#### Matched test with one pinned CSC build

The controller replayed Continents to turn 250 using the identical archived
CSC package, Dev CE and optional mod hashes. The control restored the former
combined cap arithmetic in memory after the empty turn-one packet. The
other four AI corrections remained active. An offline parity check returned
the original scorer's values and eligibility reasons on 2,500 generated
cases. The control reproduced every historical Quarter foundation identity
and turn, and its entire recorded Service history. The cap ordering alone
was sufficient to reproduce the observed count change on this seed.

| Result | Legacy cap | Revised cap |
|---|---:|---:|
| Distinct Quarter sites offered | 127 | 114 |
| Native Quarter bids selected | 129 | 80 |
| Completed Bakers / Tailors | 17 / 2 | 14 / 1 |
| Strong-layout sites with a Quarter foundation | 0 | 3 |
| Completed tracked Quarter/customer pairs | 10 | 13 |
| Realised Service link-turns across 200 common observed turns | 891 | 996 |

The control also scored the same live quotes with the revised order for
diagnosis. Among changed quotes, the revised cap raised all 81 strong-layout
quotes across six sites, by a median 168 utility. It lowered 807 ordinary
quotes across 29 sites by a median 122 utility, and raised another 224
ordinary quotes across eight sites by a median 10. Keeping the signed land
value outside the cap preserves costs or benefits the old total could clip.
The ordinary placements retain their spatial cap. Quito's strong case
changed from 680 to 783 with zero land cost and reproduced the first native
winner change described above.

The two arms shared 12 Quarter foundations. The revised arm added four
other sites and lost eight earlier ones. Six earlier Bakers no longer
received a positive offer for the same city and plot. Of those six tiles,
one received a lower offer for a different city. Both older Tailors sites
still received offers. A Wonder consumed one site and the other stayed
empty. The changed district choice altered the later city layouts and
opportunities alongside the direct effect on individual scores.

Both arms reference the same 391 MiB CSC snapshot. The legacy arm's save
contains its turn-250 map and reopens under the installed scoring policy.
An exact legacy replay uses the archived test switch through the controller.
Evidence is in `Desktop/Codex/csc-ai-main-layout-scoring-20261123/continents-legacy-cap-250`,
including `quarter-cap-comparison.json`, `quarter-cap-control.lua` and the
native receipts.

For the next comparison, follow both footprints in a strong layout through
their own district choices and construction. Increase the offer on a
contested side when it currently loses and its best viable alternative
would materially weaken or break the connection. Two contested sides can
both need support. If an equivalent footprint exists, use the smaller
value of preserving the edge and leave genuinely stronger district sites
competitive. Check for a single priced shared benefit before changing
either bid or charging a conflicting placement.

### Both footprints before either foundation

The revised-cap baseline contains 20 distinct modeled physical pairs after
deduplicating their stages and repeated turns. A two-footprint audit joins
same-tile native choices to accepted packet versions while each layout was
being modeled. It separately follows later occupation and only assigns a
score gap when the same native comparison supplies both values.
The revised-cap baseline offered 14 physical Bakers pairs and six physical
Tailors pairs. One strong pair completed both districts, a customer-first
Bakers layout. Two Tailors footprints had both a recorded same-tile loss
and subsequent occupation by a different district. Other footprints were
occupied without an exact scored loss in the available journal.

The updated audit keeps the strongest bid per district for the district-level
comparison and also reads the exact cell when a rival wins its plot. In the
revised-cap archive it finds 376 same-tile losses across scored cells, 108 of
which disappear when the report only keeps the best site for each type. One
Bakers footprint and two Tailors footprints in the modeled strong pairs both
lost a recorded comparison and were occupied by a different district. These
are observation counts across native comparisons and distinct physical
footprints respectively.
The baseline's customer observer mainly followed candidates around existing
Quarters. A planned customer on an empty pair could be missing from that scope
even when the engine compared its tile. The updated observer follows both exact
cells from the accepted packet and reuses the existing native journal. It
reports the ordinary cached comparison independently of any explicit CSC bid.

| Case | Quarter footprint | Customer footprint |
|---|---|---|
| Panama Tailors and Theater Square | 1934 later hosted a Theater Square. Its exact bid beat the Tailors by 743 utility in the turn-137 packet. | The first target at 1935 hosted a Campus on turn 57. The next target at 1933 later hosted a Spaceport. |
| Quito Tailors and Commercial Hub | 2603 lost one recorded same-tile comparison to a Farming Town by 38 utility in the turn-225 packet. The Tailors was founded on turn 232. | 2529 received a Commercial Hub choice during a modeled pair. It remained unbuilt at turn 250. |
| Tamar's Bakers and Entertainment Complex | 3011 hosted a Farming Town on turn 118. | 2936 hosted a Tsikhe on turn 111. |
| Ayacuchu Bakers and Commercial Hub | 1431 hosted the Bakers on turn 195. | The Commercial Hub was founded on 1357 on turn 187. |

A proposed future footprint currently earns a spatial preference. The exact
customer can receive an early prospective material offer. The separate
replacement-cost calculation begins with an existing Quarter or customer
foundation. A proposal on two empty sites therefore lacks that calculation
on both legs. Test a bounded shared loss estimate for the two empty sites
before increasing any general bid band. Founding either half must hand off to
the existing anchored path, and ownership or a new substitute must invalidate
stale plans.

A short scout replay reproduced the Panama Campus using the archived turn-50
save and the pinned revised-cap CSC package. At the comparison observed on
turn 57, the Campus on 1935 scored 634 utility and the reciprocal Tailors
candidate on 1935 scored 338. The Theater Square's observed candidate was
1934, at 436, so there was no observed direct Theater bid at 1935. This is a
stronger-native-placement control. Quito's 38-utility gap provides a separate
near tie against a Rural Community. The city was at its population district
limit during that decision. The native comparison can test the score effect,
and construction requires a separate capacity-ready comparison or follow-through.
The scout finished on turn 62 with zero
observer faults or dropped records. The run and its native journal are under
`Desktop/Codex/csc-ai-paired-footprints-20261124/panama-scout/control`.
The temporary native copy of the archived checkpoint was removed after close.

The first trial applies a shared footprint cost while both strong targets
are empty and owned. It prices the ordinary mapped transactions and the
Quarter's real additional adjacency through the existing economy model.
Construction and research timing enter that quote. If a similarly strong
replacement is visible, its leg receives no extra support. Otherwise the
planner allocates up to half the connection value across the scarce legs,
with at most 64 utility per leg and four priced pairs per player per turn.
The existing early-cost consumer charges competing uses of the same tile.
An established pair and a prospective pair can submit competing claims to
that consumer, which uses the largest applicable loss once. Short matched
replays use the same installed package and switch prospective placement on
at the matched boundary before the choice under study.

In the natural replay from turn 200, the control selected the Tailors at
2,653 utility in the comparison observed on 226. The Farming Town had 2,534
on the same plot. This differs from the earlier uninterrupted game. The
control first reserved plot 2603 on 215 and submitted its Tailors contract
on 229, then
founded the district on 237. The linked Hub on plot 2529 was still absent on
242. Each replay must establish its margin from its own native journal.

Both natural replay copies finished at 242 with the same 94 district
foundations. The treatment modeled the Quito pair on 21 turns. It assigned
3.4 to 18.7 utility per footprint, and the journal recorded a Farming Town
deduction on both plots. The same Tailors reservation and contract sequence
followed in both arms. Several Hub net quotes were already negative. The
pressure verified the two writes and left both native decisions unchanged.
The matched inputs, stock reservation/contract trace and exact score timeline
are in `Desktop/Codex/csc-ai-paired-footprints-20261124/quito-prospective-replay`.

The next prototype uses the same total allowance for each scarce leg. A
currently legal positive bid splits its allowance between a credit on the
planned district and a cost on rival uses of its tile. This permits a
limited change when the competing district is on another plot. A waiting
leg receives only the footprint cost. The native legal-target read and a
positive customer net quote guard the additional bid.

The turn-50 Panama replay used that revised policy and switched it on only
in the treatment after the matching turn-52 census. Both arms recorded the
same 634-utility Campus, 338-utility Tailors on plot 1935, and 436-utility
Theater Square on plot 1934. The Campus reserved its tile on 56 and was
founded on 57 in both arms. The prototype staged no local prospective offer.
This verifies that the trial leaves that stronger native case alone. The
both-footprint trace is under
`Desktop/Codex/csc-ai-paired-footprints-20261124/panama-prospective-v2-replay`.

The separate Quito capacity fixture opens one slot in both arms before
the compared choice. It verifies the Quarter, Hub and Farming Town through
the actual legal-target reader and measures the prepared control's score
again. Native selection, the successful Reserve Plot node, the city-type
contract and the physical foundation are tracked at their own clocks. A
second district in the same city still needs its own capacity and build
order. Stronger competition can be checked against the Panama Campus
and customer-first follow-through against the Ayacuchu pair.

The setup passed on the first capacity attempt. Quito grew from 15 to 16
population and the UI reported one free slot. The exact Tailors and Hub
plots, and the Farming Town on the Tailors plot, all passed the legal-target
check. The controller stopped before switching policy because its
post-growth census used the anchored switch argument. The corrected census
uses the matched switch turn shared by both experiment types. The aborted
run verified a clean exit and preference restoration. The retry uses the
same hashed archived save and installed CSC pin.

The corrected replay matched 202 prepared structural rows and both copies
finished at turn 242. The treatment quoted the Tailors–Hub layout on 18 turns
and sent positive bids for both legal targets. On the closest same-tile
Tailors comparison, the Farming Town's lead moved from 60.03 to 50.06
utility. On the Hub footprint the lead moved from 375.25 to 355.74. The
same reservations and Hub contract appeared in both arms. Neither district
was founded, and military units took 16 of the last 18 production turns in
the control. Both maps recorded the same foundations by district type from
the switch.

The exact packet revealed another budgeting error on Tailors 2603. The
turn-234 prospective offer assigned 2,552 Q8 to the Tailors and 2,552 to
charging rivals on that tile. The merged native entry charged the Farming
Town 1,252 Q8, the same amount as the control's existing customer plan.
The writer had subtracted existing-customer pressure again from the
prospective cost, even though the prospective quote prices the new Hub's
contribution after existing transactions and already deducts its own
credit. The corrected writer keeps the remaining prospective cost and
continues to use the largest loss across claims on a tile. Anchored costs
still share their own budget with their anchored credit.

For each completed 250-turn pair, run `anchored_connection_results.py --paired`
with the control and treatment archives. The report checks the opening policy
receipt, loaded binaries, ordinary map and roster, pinned content, and both
Load Game saves against their archives. It reports physical pairs separately
from realised Services, whose duration uses verified turns available in both
arms. Guidance timing covers the full observed turn window.
The treatment also records any comparable substitute that released a planned
footprint, with the exact alternate plot and publication turn. This lets the
report distinguish a contested tile that could be replaced from one that was
protected because the shared planner found no comparable substitute.

Panama showed why a substitute must avoid the lost tile in either district
role. On turn 56 of the original revised-cap run, the Tailors bids on 1935
and 1934 were 86,502 and 85,299 Q8. Each planned its Theater on the other
tile. Both bids fit the 10% replacement band, but both layouts require the
same two tiles. The planner now keeps the loss allowance on each tile until
it finds a complete layout that leaves that tile unused. Genuine
alternatives still release the tile and the price bands stay the same.
The regression also checks a substitute that rescues just one footprint.

The next scouting cases use the known Continents seed. Before turn 124,
Quito's Bakers on 2528 had two mapped Base deposits, Wheat 2454 and Flax
2602. It lost to a Farming Town on the same plot by 56.53 utility in
packet 106. The linked Hub on 2453 remained unbuilt. A scout from the
turn-50 archive can identify the first unreserved comparison. The separate
no-City-Lights source recorded promising Tailors and Theater layouts at
1934/1933 and 1935/1936 before turn 50, while the Quarter tiles were still
outside the city's ownership. Its scout follows practical owned layouts
and checks the exact archived four-mod stack. Scouting leaves the policy on
the revised baseline and reads the existing native journal.

The no-City-Lights scout completed turn 95 with the original four optional
mods. Player 5's city `196610` first offered an owned, capacity-ready
Bakers on 1610 with Entertainment Complex 1684 on turn 67. It founded
the Bakers on 1684 instead on turn 70. Its anchored plan later identified
1610 as a viable customer site, with the Hub admitted on turn 92. At
turn 94, player 4's city `458758` offered Bakers 2124 and Hub 2198 with
two Base deposits, and Bakers 2273 and Entertainment Complex 2198 with
Base and Specialty. The matched no-City-Lights replay scopes both cities
before the first strong offer and follows their alternate layouts too.

The same scout exposed a coverage gap on the stronger Bakers site at 1684.
Its turn-67 bid was 232,468 Q8 with an existing City Centre customer. The
planner also found a legal Entertainment Complex footprint at 1610 beside
that site, but the established customer occupied the single layout field and
left the future link unpriced. The planner now keeps the established customer
for the initial Quarter valuation and retains the strongest unbuilt customer
separately. Their shared forecast prices only what the new connection adds
over the existing one. The separate footprint can follow through to the
anchored planner if the Quarter is built first.

Both no-City-Lights replays matched at turn 65 and finished at turn 112.
Nippur reserved Bakers 1684 on turn 69 and completed it on turn 73 in
both. Its Hub 1610 got within 114.12 utility of Theater Square 1756 and
remained unbuilt. Rustavi reserved Bakers 2273 on turn 94, founded it on 97
and completed it on 100 in both. The treatment moved its native bid from
978.37 to 979.99 and released customer plot 2198 because Entertainment
Complex 2274 offered a substitute. A later proposal moved the scarcity
allowance to the customer side when Quarter 2273 was a viable alternate
for Quarter 2125. Rustavi reserved 2198 on 111 and had no foundation there
at the endpoint. Both arms modeled 11 exact pairs, matched all 120 observed
foundation sites and turns, and recorded 115 Bakers Stage 2 link-turns. The
comparison used the package before the additional unbuilt-customer coverage
in Nippur.

The calibration keeps half the net quote while either leg is waiting or
capacity is uncertain. An individual legal-target read can admit both
districts against the same last city slot. The prospective quote discounts
research and production but does not forecast the date of the second slot.
When both legs are admitted and their cities jointly have enough free slots,
the planner can allocate the full discounted quote once across the scarce
plots. Each leg still has the 64-utility ceiling and splits its allowance
between its own bid and the rival's same-tile cost. The native tests need a
loss within that realizable swing. For example, Quito's 79.76-utility quote
would move either of two equally scarce sites by at most 39.88 before the
existing anchored adjustment, short of the observed 60.03 lead.

When both footprints belong to one city, the prospective quote now checks
which district order can finish the pair sooner. For example, a Quarter
that takes six turns can be built while the city researches a customer
that unlocks in ten turns and takes four to build. The first order finishes
both districts in 14 turns. Building the customer first takes 20. Both
economic comparisons keep the same production schedule, so the result
isolates the new connection. The native engine still chooses the actual
order, and both sides of the quote still apply the customer's research and
the actual supplier and building prerequisites.

The earlier Quito replay matched at turn 95 and closed at turn 132. In
both arms, the alternative Bakers on plot 2603 led the proposed Bakers
on 2528 by 167.40 utility in the closest observed comparison. That
proposed Quarter–Hub pair received no extra support. The treatment did
price other links, including Bakers 2529 with Hub 2455 in the same city.
Both arms matched all 53 foundations after the switch, and logged 76
Bakers Stage 2 link-turns and 20 Bakers Stage 3 link-turns. Use this as
a stronger-choice comparison. Continue scouting for lower native margins
where the city can build both sides of the connection.

The preselected fresh Continents scout reached turn 100 and saved turn 50
for the matched replay. Delhi's owned Tailors 940 and Harbor 865 plan was
available in the turn-95 packet with one free district slot. Industrial
Zone 1011 led by 7.184 utility in the observation on turn 96. This is a
plausible close contest for the Quarter-first route, with normal production
and the Harbor's later slot still to be tested. Mbanza Kongo's Hub 1615 was
reserved on 91 and founded on 93, before the planned Bakers 1690. It gives
the same replay a customer-first case. The matched window loads turn 50,
switches the prospective policy on turn 90, and follows both through turn
125 on the same package and City Lights stack.

The control reached turn 125. In the treatment, Windows reported
`EXCEPTION_IN_PAGE_ERROR` in the controller-owned Civ process at turn 100.
The preserved log covers ten common post-switch turns, 91–100. The cause
of the native exception is undetermined.

| City | Both arms through turn 100 | What the candidate did |
| --- | --- | --- |
| Mbanza Kongo | Founded Commercial Hub 1615 on turn 93 and completed it on 96. | On turn 94 the saved plan identified the standing Hub and priced the missing Bakers on its original plot 1690 at 18,892 Q8 (73.8 native utility). |
| Delhi | Founded Tailors 940 on turn 96 and completed it on 97. | The planner named Harbor 865 on turns 91–96. Its construction required a later unlock. |

The candidate logged 80 prospective layout evaluations representing 14
distinct site pairs (four Bakers, ten Tailors). Only four appeared on the
older strong-site shortlist in that same window. The full-game report now
follows the ten additional priced layouts (three Bakers, seven Tailors)
as well. Four distinct prospective pairs qualified with a City Lights
goods provider. No exact proposed pair founded both districts
inside the common window. The interrupted treatment logs are in
`continents-layout-continuity-v8/treatment/exception-turn100` under the
24 November paired-footprints study. The customer-land replay starts from
the separate archived turn-100 source.

After one side was built, the candidate recorded eight opportunities for
a missing district across both Quarters involving a provider. These count
each eligible district type once per anchor and target city. For example,
two different Rural Community types were eligible on plot 1726 beside
Tailors 1725. No such eligible pair completed before turn 100. In the
control, an Upapitha took plot 1310 on turn 92 beside Bakers 1236, a
Wonder took 1235 on turn 119, and 1309 remained a possible alternative
at the earlier survey. Named substitutes that complete are now reported
by their actual plots and build dates.

Across those ten common turns, all five AI players' Lua guidance combined
averaged 2.014 seconds per turn in the control (maximum 2.526) and 2.429
in the candidate (maximum 3.043). The mean increase was 0.415 seconds.
Both short arms included the anchored planner and diagnostics. The full
games compare against the packaged default.

The earlier completed Continents run gives a concrete customer-land case.
In Gori, Bakers 2492 was founded on 83. The district tree reported an
accepted purchase request for 2419 as late as 101, and an Entertainment
Complex was founded there on 111. A Rural Community was founded on 3011
on 118, after a purchase request on that tile and adjacent to Bakers
3084 founded on 110. The newer observer records the plot purchase and
Gold change directly. Its report also counts purchases that become
completed partners under the default policy.

### Which purchased sites and completed pairs had a working supply?

On the separate turn-100–140 Continents replay control, the five AI players
bought 17 tiles. Seven had a district founded by the purchasing city before
the endpoint. Those were two Rural Communities, one Tailors, a Dam, a
Diplomatic Quarter, an Encampment and an Industrial Zone. Faras shows the
whole land sequence. Contract 1754 was accepted through turn 108 and marked
done on 109. Faras paid 65 Gold for plot 2794 that turn and founded a +3
Tailors on 114. On 115 the planner identified the owned neighbouring tile
2795 for a Holy Site or Theater Square. This case establishes the ordinary
Quarter purchase path. Customer land has its own offer and construction count.

For the completed earlier turn-250 Continents game in
`csc-ai-main-layout-scoring-20261123/continents`, the final map had 14 Bakers
pairs with a non-City-Center customer district. Thirteen had both districts
operational and a working adjacent Base supplier. All three customer-first
pairs and 10 of the 11 Quarter-first pairs qualified. Four also had working
Specialty. Tailors had one completed customer-first pair, with a working Base.
All seven Bakers–provider pairs had working Base, three also had Specialty.
The full-game comparison now makes this same join between each physical pair
and its own Quarter's supply. An individual Quarter can serve multiple partners.

In that historical game, 810 Quarter comparisons had a recorded higher
district score. Rural Community A won 477 and Rural Community B won 58.
For customer bids the count was 830, with 493 going to Rural Community A.
This includes completion credit on the reference site when a Quarter
already exists. The earlier count of 759 missed that publication path.
These counts include repeated decisions in the same city. The paired report
now gives the winning type, plots and score gap for comparisons across the
city, including when the two districts wanted different plots.

In the corrected turn-100 replay the candidate proposed Tailors 2458 and
Commercial Hub 2457 on turn 103. On 104 native readbacks for four rival
districts on supplier 2459 each recorded a score write and an eligible cache
read for its 16-utility deterrent. Tailors was founded on 105, and on 106 the
planner repriced the original Hub site at 20,014 Q8 (78.2 utility). Tile 2385
was an available substitute. The switch census matched across all 141 rows.

### Where did the second district go?

Both arms of the corrected customer-land replay reached turn 140. Over
turns 103–140, the control founded one Bakers and one Tailors. The candidate
founded two Bakers and four Tailors, each on a plot it had priced. It priced
17 distinct Bakers layouts and 24 Tailors layouts. Several shared a Quarter
site. None of the 41 completed its designated pair or a named substitute by
140. Both arms recorded 17 ordinary tile purchases and zero CSC customer-land
offers.

In Addis Ababa the new Tailors stood on 2458 from turn 105. The planned Hub
on 2457 received a relative bid on 106 and ten subsequent reference-site
completion credits. On turn 135 the city selected Ruhr Valley for that plot.
On 135 the planner had named 2532 as its backup. On 136 it made that backup
its first choice and named 2533 as the new backup. All five subsequent
packets through 140 were published with zero omitted entries, and the
occupied 2457 received no further Hub offer. This demonstrates release and
replanning. The queue put production into Ruhr Valley. There was no recorded
positive Hub bid on 2532 during those five turns.

The six new Quarters belonged to eight distinct proposed pairs. Seven of
those eight partner tiles had no subsequent district foundation by turn
140. Only Addis Ababa lost its partner tile to another build. Seven pairs
had at least one later plan marked ready. For example, the planner renewed
the Rural Community on 2611 beside Bakers 2685 on seven turns between 120
and 139. Faras's Theater Square plan was ready on four turns and later
waited on capacity. Delhi's Harbor was waiting on all three turns after
Tailors was founded. Across all 41 proposals, 25 saw neither tile taken.
These counts put the emphasis on getting a ready second district selected
in time. Increasing tile protection alone has limited reach here.

**Sodo chose the right provider type on a different tile.** The city founded
Bakers on 2685 on turn 117 and finished it on 127. Plot 2611, adjacent to
that Quarter, had been priced for Rural Community A through turn 114.
The planner offered it 6,602 Q8 in extra completion value on 127. In the
next packet it used 2611 as an economic reference and reduced another
site's score, but recorded no completion credit on 2611. The city's native
winner on 128 was Rural Community A on 2612 at 540,434 Q8 (2,111 utility).
The purchase node immediately accepted contract 2663 there and recorded
its tenth waiting turn on 138. Sodo put production into its Water Mill,
a Builder and a Cuirassier during that interval. No Rural Community
construction contract appeared before the endpoint.

The journal recorded 641,204 Q8 for 2611 in version 28 and the native
winner in version 29. There was no same-version read for 2611 at the
choice, so the margin is unknown. In the installed XP2 GameCore
(`4de40abf`) the joint selector at RVA `0x3e4310` checks the current
cached cell against its row threshold and running best. An earlier high
value is useful for locating the decision window but cannot price that
turn's losing bid.

The follow-up candidate addresses two gaps reproduced in the publisher.
A Quarter already selected by the engine now remembers its validated
customer while awaiting foundation, even on turns that skip the pair's
quote. Its original expiry still applies. After foundation, one of the
two existing visits per build order can reprice a ready saved partner
on subsequent turns. The other rotates across the ordinary candidates.
With six eligible groups, the regression repriced the lone ready saved
partner on every publication and reached all five alternatives. A separate
case confirms that a competing foundation releases the saved customer.
Live conversion of the Sodo pair remains an open test.

### Standalone turn-250 control, 24 November

The default planner's common survey identified 34 targets where at least
one proposed tile received its intended district. A target is one founded
district and one mapped partner type in a specific city. Several proposed
tiles for that partner count once. These targets cover the common survey
of owned sites. The endpoint census also includes links made elsewhere.

| Outcome of the 34 targets | Count |
| --- | ---: |
| Completed on the surveyed tiles | 4 |
| Completed with the intended partner on another adjacent tile | 5 |
| Partner type already built elsewhere when the first surveyed tile was founded, with no completed link | 2 |
| Partner type founded elsewhere afterward, with no completed link | 6 |
| Partner city never founded the requested district type | 17 |

The nine successful targets produced eight distinct adjacent pairs. One
Bakers–Entertainment Complex pair fulfilled two surveys. From actual
foundation dates, Bakers had three Quarter-first and three customer-first
pairs. Both Tailors pairs were Quarter-first. On the whole endpoint map,
including sites outside that survey and excluding City Centers, Bakers had
12 completed pairs and Tailors five. Nine Bakers and four Tailors pairs had
both a working Base supplier and a functioning mapped buying building.

The 17 unbuilt partners were eleven Commercial Hubs and six Entertainment
Complexes. The median time from Quarter foundation to the endpoint was 158
turns. All 17 had an observed free population slot at some point, and 16
saw their city found another district later. On eight of the 17, CE recorded
positive customer-site adjustments after Quarter foundation. None of those
exact proposed tiles subsequently appeared as the native district winner.
The matched candidate should show whether it gets more of these investments
into the queue or completes them on a suitable adjacent alternative.

Four of the eight targets yielded 15 comparisons with a final score for
both the proposed site and the winner in the same packet. The median gap
was 831 native utility. The closest was Meroë on turn 60. Bakers 2735 had
been founded at +4 on turn 57. Its proposed Entertainment Complex on 2660
received +34.5 early utility and finished at 690.2, against 759.3 for Harbor
2587. The Harbor received contract 793, entered the queue after the Temple
of Artemis on turn 63 and received 29.9 Production on 64. The turn-50 save preserves the lead-up for
a matched replay if customer competition remains weak on this seed.

Source on Shadow: `csc-ai-paired-footprints-20261124/full-v13-standalone-control`
under Desktop/Codex. The paired report's `anchored_target_followthrough`
field groups the targets and records the order of each distinct completed pair.

### Matched standalone result, 24 November

Small Continents, Online speed, map seed 171124601, game seed 171124602.
The two turn-250 arms used the same five AI players, opening map and v13
build. The control ran the current default CSC tuning. The candidate
enabled prospective and anchored pair guidance. Pairs in the table exclude
City Centers. One Quarter can support more than one adjacent customer.

| Measure | Current default | Candidate |
| --- | ---: | ---: |
| Completed Bakers / Tailors Quarters | 23 / 3 | 25 / 6 |
| Completed Bakers–customer pairs, Quarter-first / customer-first | 8 / 4 | 14 / 4 |
| Completed Tailors–customer pairs, Quarter-first / customer-first | 4 / 1 | 4 / 4 |
| Pairs with a working Base supplier, Bakers / Tailors | 11 / 4 | 16 / 7 |
| Pairs also having a functioning mapped buyer, Bakers / Tailors | 9 / 4 | 10 / 7 |
| Exact pairs completed / eligible owned layouts in the common survey | 4 / 238 | 12 / 232 |
| Exact pairs completed / layouts where a proposed tile got its district | 4 / 38 | 12 / 58 |
| Working adjacent Base deposits at 250, Bakers / Tailors | 27 / 2 | 29 / 6 |
| Working adjacent Specialty deposits at 250, Bakers / Tailors | 3 / 0 | 2 / 0 |
| Bakers Stage 2 active chains / chain-turns over 199 shared observations | 17 / 1,368 | 17 / 1,488 |
| Bakers Stage 3 active chains / chain-turns | 5 / 248 | 5 / 192 |
| Tailors Stage 3 active chains / chain-turns | 1 / 58 | 2 / 72 |
| Guidance seconds per turn, mean / maximum | 1.65 / 3.55 | 2.75 / 7.82 |

For the exact common-survey pairs, the mean interval between foundations
went from 12 to 93.5 turns for Quarter-first Bakers and from 28 to 53.3
for customer-first Bakers. Quarter-first Tailors went from 82 to 87.5.
One customer-first Tailors pair took nine turns in the candidate. The
larger sample includes some long waits. The candidate's additional
scarcity pricing covered 54 Bakers and 58 Tailors layouts, of which four
and one completed on the priced tiles. These tracked sets overlap.

Two customer sites on land acquired in ordinary play completed a pair in
each arm. There were zero explicit CSC offers to buy customer land. No
Tailors Stage 2 Service was observed. For customer bids with a matched
native score, exact wins increased from seven to 14. Campus beat a customer
31 times in each arm. In the candidate, Theater Square accounted for
another 23 losses and Bakers for 17. A district comparison can recur
before construction.

Barcelona's Holy Site demonstrates that a stronger rival can take a
protected tile. In packet 154, the planner used half its link allowance
to bid for a Bakers–Commercial Hub pair on 2457 and 2383. CE confirmed a
1,443 Q8 site cost on Holy Site 2383, then recorded it winning the city
comparison at 353,637 Q8 against the Hub's 299,765 on the same tile and
packet. Contract 3465 was submitted on 154. The Holy
Site took plot 2383 on 157 and completed on 160. In the candidate's
prospective-site readbacks, six wins on four distinct sites reported
both a cost write and a site win.

In the candidate, 55 of 272 newly logged Quarter-first opportunities
matched a customer plot recorded as unowned on the same turn. Fifty
were in cities with all slots used. Those records mark changes in
observed opportunities, so a site can stay eligible across other turns.
Of 1,720
Quarter-first plans, one matched an unowned best plot. It was the
Commercial Hub on 603 at turn 105. Its city had used all three slots.
The prospective planner also priced a Holy Site on unowned 2612 at turn
50 with both slots used. That narrows the investigation to what happens
between the unowned opportunity and the bid. The Gori replay can observe
the actual buyer and invoice before the native purchase decision. An
additional site that has yet to be priced can also prevent the planner
from establishing that land has a material advantage over its backups.
The strongest case to price directly is plot 1453 on turn 117, next to
Bakers 1454. The city had a slot, but its two quotes went to owned sites
1381 and 1529. At turn 189 a priced unowned site, 2947, finished below
zero while the owned 2875 was positive. Purchasing that plot would have
reduced the value of the connection.

The diagnostic overlay generator `customer_land_appraisal.py` prices one
named frontier option and the backups for the same Quarter and seller
stage, including sites outside the planner's two-quote shortlist. It
records the Gold quote, the link after that expense, the best equivalent
owned option, other paid alternatives, capacity, and the plan that
actually went forward. An offline three-site example chose the same owned
plot with and without the overlay. The diagnostic appraised the skipped
paid plot at 70 utility after a 20 Gold invoice, against 60 for the best
owned option. This establishes that the shortlist can miss an economic
advantage. Replaying 1453 will show whether it did so on Continents.

Quarter forecasts accounted for 408,958 of the 419,188 additional logical
model evaluations. All 18,585 candidate Quarter quotes were distinct by
turn, player, city, type and plot. The next performance check should count
actual ledger builds and the time spent pricing them. A logical evaluation
can reuse a result. The newer customer-ownership and saved-partner changes
were developed after this build was pinned.

Two short replays on the reviewed build will revisit actual completions
from this seed. The turn-150 save precedes the Commercial Hub foundation
on 603 (154) and Tailors on 602 (163). The native AI had already selected
the Quarter site before this save. Switch at 151 and follow both cities
through 168. The turn-200 save has Bakers on 1162. Switch at 211, before
the Hub selection recorded in packet 216, and follow 1163 through 235.
These same-state tests isolate follow-through in each build order.

#### Forecast performance follow-up

Quarter placement used to copy the streams belonging to the proposed
Quarter on every search trial. Its scoring function reads the totals.
The candidate now copies streams only for the winning forecast, keeping
the Q8 objective and final breakdown intact. On four offline worlds with
2–9 chains, it produced identical forecasts, scores and evaluation counts.
The full economy suite passed all 233 checks.

The existing 16-state cache already covered a small shared-customer world.
In larger offline worlds the first 32 slots eliminated 25 of 53 candidate
ledger builds with four chains and 28 of 102 with seven. These worlds had
several optional investments tied to a shared customer. To estimate the
effect on the live game, build the diagnostic-only model overlay using
`project/tools/native_ai/late_placement/joint_forecast_profile.py`. It
counts real ledger builds, pricing, 16-state hits and the additional hits
that a 32-state cache would give on the same winning search. The diagnostic
uses the existing 16-state results for every bid. Compare its counters from
the turn-200 standalone save with the ordinary turn-250 evidence. Use
measured turn times from an ordinary candidate for release qualification.

### City Lights turn-250 control, 24 November

Small Continents, Online speed, map seed 171124603, game seed 171124604.
The current-default control reached turn 250 and saved a named, verified
endpoint. It completed 25 Bakers and one Tailors. Its common survey
recorded 187 eligible Bakers layouts and 140 Tailors layouts. Five
Bakers layouts completed on both proposed tiles, with two Quarter-first
and three customer-first. Tailors completed none of its surveyed layouts.

At turn 250, excluding City Centers, Bakers had 17 completed adjacent
customer or sales pairs. Fourteen involved a mapped buying district,
and ten had both a working Base supplier and a functioning buyer
building. Bakers also completed 13 separate City Lights goods-provider
pairs, nine Quarter-first and four provider-first. Eleven had a working
Base supplier. The completed Tailors had no adjacent completed mapped
customer or provider.

The median interval from the first foundation to the second was 34
turns for Quarter-first provider pairs and 100.5 for provider-first.
Ålesund was the quickest Quarter-first case. Bakers took plot 1976 on
turn 135, then Rural Community A took adjacent 1902 on turn 139 with
+2 ordinary Gold adjacency. The pair completed on turn 141. Kaiapoi
demonstrated the reverse order. Rural Community A took 2679 on turn
131, then Bakers took 2753 on turn 148 and completed the pair on 152.
The archived turn-100 save precedes both cases.

Across 200 observed turns, 15 Bakers Stage 2 chains delivered 1,114
active chain-turns and seven Stage 3 chains delivered 411. CSC guidance
took 1.97 seconds per turn on average and 4.92 seconds at maximum.
The matched candidate uses the same pinned build, map and game seeds.

| Turn-140 outcome across five AI players | Control | Candidate |
| --- | ---: | ---: |
| Bakers with a non-City-Center customer, counted per pair | 15 | 13 |
| Of those pairs, both districts operational and working Base | 14 | 11 |
| Tailors customer pairs, all with working Base | 1 | 2 |
| Bakers pairs whose adjacent district can host a mapped buying building | 10 | 7 |
| Bakers pairs with a working Base and a working mapped customer building | 4 | 2 |
| Tailors pairs with a working Base and a working mapped customer building | 1 | 1 |
| Bakers–goods-provider pairs, all with working Base | 2 | 3 |
| Bakers Stage 2 active chain-turns on 31 common observations | 190 | 212 |
| Distinct active Bakers Stage 2 chains on those observations | 8 | 8 |
| All guidance per turn, five players combined, mean / max | 1.807 / 2.295 s | 2.714 / 3.712 s |

The timing uses all 38 common post-switch turns. The chain observations
also cover the shared lead-in. Neither arm recorded an active Tailors
Service on those observations. The immediate bottleneck is completing
the second district at an acceptable turn cost.

The additional Tailors partner in the treatment was a City Lights
Upapitha. Its sales tag grants an adjacency benefit. The other Tailors
pair in each arm had a mapped buying building and a functioning Base.
The distinction also matters for Bakers. Five control partners and six
treatment partners at turn 140 were sales-only districts. The comparison
now counts both kinds of customer in its total and reports how many had
a working mapped buyer. A district with both roles counts once per Quarter.
The earlier turn-250 map had 12 buyer-capable and two sales-only Bakers
pairs at the endpoint. Eight had both a working Base and customer building.

Across the 38 common turns, the planner examined 8,317 customer options
in the control and 21,048 in the candidate. The joint economic model ran
94,786 and 142,263 evaluations respectively. One avoidable cost was asking
the engine for a plot's assigned city again for each customer district.
The revised planner shares that read across both Quarters and their
customer types for one player's current snapshot. In a five-tile test
with two potential customer types, the same options, adjacency and
displacement now need five city lookups and one neighbour scan, down from
16 and two. The next snapshot reads the cities afresh. The timing figures
in the table above precede this change.

**Customer-land replay targets.** The archived turn-50 Continents save
(`737c6582fd7e`, map seed 1457395586) passed the controller's source and
package preflight. Three historical buying cities on this seed had a
district purchase request followed by an actual adjacent pair. Gori's
Entertainment Complex 2419 was founded on 111 beside Bakers 2492. Caracas
founded Rural Community 2826 on 117 beside Bakers 2751. Batumi founded
Rural Community 3011 on 118 beside Bakers 3084, and a second Bakers
Quarter on 3012 later linked back to it. Use those three sites in both
arms, switch on 87 and follow through 140. The short-replay land observer
can now record the raw price, whether that city is the unique buyer, its
treasury and the native terrain check on each chosen plot, starting before
CSC submits an offer. This diagnostic adds no work to ordinary games.
