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
