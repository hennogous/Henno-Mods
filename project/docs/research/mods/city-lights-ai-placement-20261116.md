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
