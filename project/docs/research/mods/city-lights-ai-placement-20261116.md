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
