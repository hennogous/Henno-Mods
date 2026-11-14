# CSC versus no-CSC district controls

Three preselected maps, five original AI players per map, through turn 250 on Online speed. Compare newly founded ordinary districts and Quarters, their placement adjacency, and the native values attached to those sites.

The CSC runs built 441 ordinary districts that consume population slots, plus 8
Quarters; the controls built 465 ordinary slot-consuming districts. That is 24
fewer ordinary districts (5.2%) and 16 fewer after including the Quarters.
21 of the net 24 difference occur on Fractal, where the CSC group also has one
fewer surviving AI and 8 fewer cities. Continents is almost level. Expansion,
survival and city growth are therefore central to reading the capacity results.

The new controls provide a usable calibration set: **1,124 foundations with
placement-event adjacency**, 586/597 preceding choice quotes for ordinary
investment districts, and 595/597 before-placement cached quotes. The native
entry reader succeeds on all 1,058 sampled calls. Coverage details follow below.

| Map | Native-type foundations CSC / control | Slot-consuming native CSC / control | CSC slot foundations | Cities at 250 CSC / control | Population at 250 CSC / control | Alive AI CSC / control |
|---|---:|---:|---:|---:|---:|---:|
| Continents | 308 / 307 | 158 / 156 | 6 | 48 / 49 | 602 / 572 | 5 / 5 |
| Pangaea | 253 / 248 | 124 / 129 | 0 | 40 / 51 | 435 / 477 | 5 / 5 |
| Fractal | 303 / 352 | 159 / 180 | 2 | 50 / 58 | 560 / 665 | 4 / 5 |
| Total | 864 / 907 | 441 / 465 | 8 | 138 / 158 | 1597 / 1714 | — |

Slot totals use the loaded RequiresPopulation rule. City Centers and Wonder footprints are included in the broader native-type count; City Lights districts are recorded separately in JSON. Cities and population describe the turn 250 empire, providing context for how much district capacity it developed.

## Common district types across all three maps

Exact district types, with unique replacements retained separately in the
per-map tables below. Counts are newly founded districts. Adjacency columns
show the indicated real yield; utility columns are native Q8 divided by 256.

| District | Count CSC / control | Mean adjacency CSC / control | Median native choice utility CSC / control |
|---|---:|---:|---:|
| Campus | 79 / 95 | Science 1.91 / 1.95 | 1268.7 / 1403.6 |
| Commercial Hub | 44 / 46 | Gold 2.36 / 2.61 | 1996.4 / 2099.8 |
| Harbor | 32 / 34 | Gold 1.78 / 2.88 | 2137.5 / 1764.3 |
| Industrial Zone | 26 / 27 | Production 2.23 / 1.74 | 1469.3 / 1466.1 |
| Theater Square | 83 / 81 | Culture 1.78 / 1.80 | 1662.2 / 1866.1 |
| Holy Site | 22 / 22 | Faith 1.23 / 2.05 | 579.4 / 841.5 |

Campus and Theater adjacency are close across groups. Industrial Zones have
higher production adjacency with CSC, while Harbors and Holy Sites have lower
adjacency. Total native utility adds other forecast and strategic contributions:
the Harbor figures illustrate why adjacency and total utility need separate
columns. Use these samples to calibrate locally competing bids, with their
city, turn and score age available in the JSON.

## Adjacency and native utility by type

Adjacency is sampled at the placement event and contains real yields. Native choice utility is the common score measurement in both groups; the controls also record the cached total just before placement. Parentheses show matched samples. A dash means the measurement is unavailable or the district uses another investment path, such as a Wonder. Detailed timestamps and coverage remain in JSON.

| Map | District | Foundations CSC / control | Mean adjacency CSC | Mean adjacency control | Median choice utility CSC (n) | Median choice utility control (n) | Control pre-placement cache (n) |
|---|---|---:|---|---|---:|---:|---:|
| Continents | AERODROME | 8 / 6 | 0 | 0 | 2216.8 (7) | 2859.4 (6) | 3240.0 (6) |
| Continents | AQUEDUCT | 5 / 6 | food 1.20 | food 0.33 | 1529.1 (5) | 1950.3 (6) | 2077.5 (6) |
| Continents | CAMPUS | 27 / 34 | science 2.04 | science 1.97 | 1096.6 (27) | 1452.6 (34) | 1571.5 (34) |
| Continents | CANAL | 3 / 7 | 0 | 0 | 2086.0 (1) | 2551.2 (5) | 2792.2 (6) |
| Continents | CITY_CENTER | 49 / 48 | 0 | 0 | — | — | — |
| Continents | COMMERCIAL_HUB | 16 / 18 | gold 2.69 | gold 2.83 | 2033.9 (16) | 1924.2 (18) | 2228.3 (18) |
| Continents | DAM | 10 / 8 | 0 | 0 | 1248.1 (10) | 1075.5 (8) | 1243.1 (8) |
| Continents | DIPLOMATIC_QUARTER | 3 / 0 | 0 | — | 773.9 (3) | — | — |
| Continents | ENCAMPMENT | 17 / 17 | 0 | 0 | 2019.5 (17) | 2110.9 (17) | 1918.1 (17) |
| Continents | ENTERTAINMENT_COMPLEX | 6 / 9 | 0 | 0 | 1406.8 (6) | 1466.6 (9) | 1460.3 (9) |
| Continents | GOVERNMENT | 1 / 2 | 0 | 0 | 1061.8 (1) | 1006.6 (2) | 1041.0 (2) |
| Continents | HANSA | 6 / 3 | production 3.33 | production 3.00 | 2041.9 (6) | 363.9 (3) | 408.8 (3) |
| Continents | HARBOR | 12 / 10 | gold 1.83 | gold 2.90 | 2154.0 (12) | 2138.8 (10) | 2265.5 (10) |
| Continents | HIPPODROME | 4 / 2 | 0 | 0 | 295.1 (4) | 212.2 (2) | 250.5 (2) |
| Continents | HOLY_SITE | 7 / 7 | faith 1.14 | faith 0.57 | 760.4 (7) | 256.1 (7) | 513.7 (7) |
| Continents | INDUSTRIAL_ZONE | 8 / 8 | production 2.38 | production 2.00 | 1444.0 (8) | 1304.1 (8) | 1357.7 (8) |
| Continents | NEIGHBORHOOD | 14 / 13 | 0 | 0 | 1387.7 (14) | 1314.1 (13) | 1337.0 (13) |
| Continents | PRESERVE | 1 / 1 | 0 | 0 | 1420.4 (1) | 966.7 (1) | 967.1 (1) |
| Continents | SPACEPORT | 16 / 16 | 0 | 0 | 6865.3 (15) | 5332.9 (16) | 6026.8 (16) |
| Continents | THEATER | 33 / 30 | culture 2.00 | culture 2.37 | 1346.4 (32) | 1485.2 (30) | 1812.2 (30) |
| Continents | WATER_ENTERTAINMENT_COMPLEX | 9 / 9 | 0 | 0 | 3001.1 (9) | 2030.8 (9) | 3084.6 (9) |
| Continents | WONDER | 53 / 53 | 0 | 0 | — | — | — |
| Pangaea | AERODROME | 4 / 5 | 0 | 0 | 1929.8 (4) | 1855.9 (5) | 1476.9 (5) |
| Pangaea | AQUEDUCT | 4 / 1 | 0 | 0 | 781.8 (4) | 1136.1 (1) | 1138.4 (1) |
| Pangaea | CAMPUS | 24 / 29 | science 1.83 | science 1.97 | 1301.2 (23) | 942.8 (29) | 1368.4 (29) |
| Pangaea | CANAL | 2 / 2 | 0 | 0 | 1716.5 (1) | 1904.6 (1) | -3994.1 (2) |
| Pangaea | CITY_CENTER | 43 / 51 | 0 | 0 | — | — | — |
| Pangaea | COMMERCIAL_HUB | 10 / 13 | gold 2.50 | gold 2.62 | 1779.0 (10) | 2452.6 (13) | 2174.0 (13) |
| Pangaea | DAM | 5 / 4 | 0 | 0 | 1771.0 (5) | 1130.8 (4) | 1065.7 (4) |
| Pangaea | DIPLOMATIC_QUARTER | 1 / 0 | 0 | — | 1201.6 (1) | — | — |
| Pangaea | ENCAMPMENT | 18 / 22 | 0 | 0 | 1483.3 (18) | 2240.6 (22) | 2577.6 (22) |
| Pangaea | ENTERTAINMENT_COMPLEX | 7 / 6 | 0 | 0 | 1321.8 (6) | 1997.2 (6) | 2203.9 (6) |
| Pangaea | GOVERNMENT | 2 / 2 | 0 | 0 | 837.4 (2) | 448.9 (2) | 494.0 (2) |
| Pangaea | HARBOR | 5 / 5 | gold 1.00 | gold 3.60 | 2776.5 (4) | 1308.6 (5) | 1442.8 (5) |
| Pangaea | HOLY_SITE | 9 / 8 | faith 1.44 | faith 2.75 | 359.4 (7) | 365.0 (5) | 570.2 (8) |
| Pangaea | INDUSTRIAL_ZONE | 8 / 8 | production 2.12 | production 1.38 | 1541.7 (8) | 1416.4 (8) | 1733.1 (8) |
| Pangaea | NEIGHBORHOOD | 3 / 1 | 0 | 0 | 1494.4 (3) | 657.9 (1) | 794.7 (1) |
| Pangaea | PRESERVE | 0 / 1 | — | 0 | — | 1330.5 (1) | 1384.5 (1) |
| Pangaea | ROYAL_NAVY_DOCKYARD | 4 / 2 | gold 1.50 | gold 1.50 | 1063.3 (4) | 801.6 (2) | 958.8 (2) |
| Pangaea | SPACEPORT | 13 / 15 | 0 | 0 | 6281.4 (11) | 3818.0 (15) | 4481.0 (15) |
| Pangaea | THEATER | 25 / 24 | culture 1.88 | culture 1.46 | 1763.8 (24) | 2017.9 (24) | 2319.4 (24) |
| Pangaea | WATER_ENTERTAINMENT_COMPLEX | 7 / 4 | 0 | 0 | 2711.8 (7) | 1905.6 (4) | 3089.2 (4) |
| Pangaea | WONDER | 59 / 45 | 0 | 0 | — | — | — |
| Fractal | ACROPOLIS | 1 / 5 | culture 2.00 | culture 2.40 | 389.3 (1) | 431.4 (5) | 622.3 (5) |
| Fractal | AERODROME | 8 / 10 | 0 | 0 | 2144.4 (8) | 1856.4 (10) | 2017.9 (10) |
| Fractal | AQUEDUCT | 7 / 5 | 0 | food 0.40 | 408.2 (7) | 984.3 (5) | 989.1 (5) |
| Fractal | CAMPUS | 28 / 32 | science 1.86 | science 1.91 | 1428.0 (28) | 1564.1 (32) | 1768.9 (32) |
| Fractal | CANAL | 7 / 7 | 0 | 0 | 2351.1 (5) | 1962.9 (5) | 2253.4 (6) |
| Fractal | CITY_CENTER | 50 / 55 | 0 | 0 | — | — | — |
| Fractal | COMMERCIAL_HUB | 18 / 15 | gold 2.00 | gold 2.33 | 1988.6 (18) | 1974.1 (15) | 2233.2 (15) |
| Fractal | DAM | 4 / 6 | 0 | 0 | 836.6 (4) | 1752.6 (6) | 2002.7 (6) |
| Fractal | DIPLOMATIC_QUARTER | 2 / 4 | 0 | 0 | 248.3 (2) | 791.8 (4) | 887.7 (4) |
| Fractal | ENCAMPMENT | 18 / 22 | 0 | 0 | 2764.3 (18) | 2091.1 (22) | 2392.1 (22) |
| Fractal | ENTERTAINMENT_COMPLEX | 9 / 11 | 0 | 0 | 2337.8 (9) | 1912.7 (11) | 2071.0 (11) |
| Fractal | GOVERNMENT | 1 / 2 | 0 | 0 | 427.3 (1) | 1016.0 (2) | 1352.3 (2) |
| Fractal | HARBOR | 15 / 19 | gold 2.00 | gold 2.68 | 1944.9 (15) | 1760.0 (19) | 1584.1 (19) |
| Fractal | HOLY_SITE | 6 / 7 | faith 1.00 | faith 2.71 | 573.0 (4) | 1117.4 (7) | 1095.0 (7) |
| Fractal | INDUSTRIAL_ZONE | 10 / 11 | production 2.20 | production 1.82 | 1531.7 (10) | 1599.0 (11) | 1815.4 (11) |
| Fractal | LAVRA | 6 / 4 | faith 3.00 | faith 2.75 | 866.4 (6) | 394.3 (4) | 415.0 (4) |
| Fractal | MBANZA | 3 / 7 | 0 | 0 | 906.8 (3) | 1171.8 (7) | 1512.1 (7) |
| Fractal | NEIGHBORHOOD | 9 / 15 | 0 | 0 | 1315.8 (9) | 1104.3 (15) | 1179.6 (15) |
| Fractal | PRESERVE | 3 / 1 | 0 | 0 | 239.8 (3) | 1559.8 (1) | 1742.5 (1) |
| Fractal | SPACEPORT | 11 / 19 | 0 | 0 | 3793.3 (11) | 5397.8 (19) | 6583.5 (19) |
| Fractal | THEATER | 25 / 27 | culture 1.40 | culture 1.48 | 1662.2 (25) | 1901.7 (24) | 2363.0 (27) |
| Fractal | WATER_ENTERTAINMENT_COMPLEX | 9 / 10 | 0 | 0 | 2268.6 (9) | 2095.9 (10) | 2387.8 (10) |
| Fractal | WONDER | 53 / 58 | 0 | 0 | — | — | — |

## Comparison setup

Small/Prince/Online250, matched selected seeds and leaders, with the same City Lights, Resourceful2 and Sukritact resource versions. Controls remove CSC entirely. Its resource and economic effects can change the generated world and later city growth, so read these results as the overall CSC comparison. Counts measure foundations; population measures surviving cities at 250. Pangaea with CSC includes the documented turn200-save continuation.


## Astra interpretation and tuning priorities

Requested by Henno after the completed comparison. This is a review and proposed
next work; it introduces no policy change or additional game run.

Keep the +3 Quarter quality floor, +4 preference and current placement-premium
bands. All eight founded Quarters have owned Base and meet the quality floor;
the still-open problem is conversion of worthwhile plans into construction.
Eight Quarters across fifteen original AI empires is sparse, especially zero
on Pangaea and only one Tailors. Start by explaining credible plans already
winning native comparisons, rather than lowering quality or multiplying bids.

Keep normal population-slot consumption and native admission. Continents builds
two more ordinary slot-consuming districts with CSC plus six Quarters. Across
Continents and Pangaea, including Quarters, the CSC group builds three more.
The aggregate shortfall is concentrated on Fractal alongside reduced survival
and expansion. This supports retaining the capacity approach. A later comparison
of CSC with tuning enabled/disabled answers the separate tuning-efficacy question.

Calibrate Quarter values against the alternatives competing in the same city
and decision. The type medians give scale and context, rather than a target bid.
Harbors illustrate the separation: lower mean Gold adjacency with CSC, higher
median native utility. The current +96–384 utility placement premiums should be
reviewed against an actual losing margin and a checked economic ledger.

Recommended sequence:

1. **1.6, with 1.4/1.7:** trace a still-credible Pangaea nomination such as
   Lingapura alongside a successful Continents investment. Identify its
   admission, retained request value, production comparison and eventual action.
   Use the shortest preserved replay window if the archives miss a necessary
   boundary. Keep London's expired +3→+2 withdrawal as a regression case.
2. **1.1/1.2/2.1:** correct the known AI-C182 incoming exchange attachments,
   then close relationship-guidance gaps. Current `CSC_AI_AdjacencyScan.lua`
   suppresses future-customer nomination whenever host and Quarter share a
   city and both require population; it never checks whether two slots exist.
   Review this blanket condition with fresh capacity/native admission, testing
   one free slot, two free slots, cross-city hosts and unavailable capacity.
   The customer connector SQL derives edges from the customer-building registry.
   Compare loaded provider tags with actual edges before adding any missing
   City Lights provider relationships. Keep future-customer yield excluded from
   the Quarter ledger until the customer exists.
3. **1.5:** trace one credible unowned Quarter site from offer through frontier
   eligibility, selection, contract, category funds and payment. Use a separate
   existing-chain supplier case if offer generation is the missing step.
   Existing generic payments show the payment mechanism operates; the missing
   CSC-target transition may occur before funding. Review subsidies or fund
   changes only after the target actually reaches that boundary.

Astra inspected `CSC_AI_EconomyAdapters.lua`, `CSC_AI_AdjacencyScan.lua` and
`CSC_AI_Connectors.sql`. The lead independently checked the same-city guard and
customer-registry edge source. Actual missing provider edges still need a loaded
set comparison; absence of an explicit provider-tag expansion alone does not
identify every absent relationship. Material protection remains in place.

## Recording and recovery

| Control | All original-AI foundations / UI matches | Ordinary choice quotes | Ordinary pre-placement cache | Native entry reads |
|---|---:|---:|---:|---:|
| Continents | 377 / 377 | 204 / 206 | 205 / 206 | 357 / 357 |
| Pangaea | 323 / 323 | 148 / 152 | 152 / 152 | 296 / 296 |
| Fractal | 424 / 424 | 234 / 239 | 238 / 239 | 405 / 405 |
| Total | 1124 / 1124 | 586 / 597 | 595 / 597 | 1058 / 1058 |

Ordinary quote coverage excludes City Centers, Wonder footprints and City Lights
types. Broader foundation counts retain those categories separately. Missing
choice/entry joins remain explicit in the artifact JSON. Median utilities use
the matched samples; the table includes sample sizes. A before-placement value
is the cached cell at factory entry. Wonder generic cells can hold the -9999
sentinel and stay outside utility calibration.

Every game reaches250, archives all ten 25-turn censuses and closes with exit0
and restored preferences. Continents and Fractal have50/100/150/200/250 saves.
Pangaea has50/100/150/200 saves; its final save permission stayed unavailable
with no SaveGame request sent. Its complete250 observations are retained.

Two diagnostic stops were recovered offline without repeating their games:
Continents ended on the old pending-event assertion; Pangaea ended on its save
permission timeout. Their raw failures, closure records and offline audits are
preserved. The runner now journals pending events and handles unavailable
optional saves separately. Fractal completes normally with these improvements.
Its four pending events refer to existing district plots that are removed
immediately after capture events; they add no new construction. Across controls,
14 extra matching UI additions are existing City Centers changing owner.

All observers are read-only policy diagnostics. CSC is absent, native tuning
counters stay zero and the pinned CE/CL/R2/Suk stack is recorded. No RHAI5 or
external tuning runs. The live CSC policy in the earlier treated games remains
unchanged. The older automatic goal remains paused; no further games are queued.

The corrected factory-return field masks AL. All construction counting uses
physical events. The older no-CSC foundationTurn field copied an extra native
event argument; analysis uses the row's actual turn. The Fractal callback fixes
that boundary. Shipped Base/Assets/UI/GenVFX.lua names argument 7 iEra and puts
completion percentage at 9. Reusable guidance is corrected in the AI and gameplay
skills; native sampling is recorded as AI-N130.

## Reproduction and artifacts

- [Fixed protocol, seeds, interruptions and binary qualification](csc-no-csc-district-baseline-20261114.md).
- [Earlier CSC campaign results](csc-ai-planning-campaign-results-20261114.md).
- Maintained comparison: project/tools/native_ai/late_placement/vanilla_district_compare.py.
- Artifacts: C:/Users/Shadow/Desktop/Codex/csc-no-csc-district-baseline-20261114/.
- Comparison JSON/Markdown and coverage-audit.json: comparison/ under that root.
- Each arm retains source/package pins, loaded SQLite, native journals, raw Lua
  events, censuses, checkpoint receipts and session closure. Recovered arms also
  retain failure.json and offline-observation-audit.json. The campaign ledger
  preserves both stopped states before its completed state.

16 focused observer/database/native-VM and 6 checkpoint-phase tests pass; 9
planning/financial analysis regressions also pass. The full comparison rebuilds
from all six closed arm archives. Knowledge updates use Markdown; no Quartz build.
