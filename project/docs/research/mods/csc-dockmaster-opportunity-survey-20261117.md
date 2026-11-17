# Dockmaster opportunities across three maps

**Useful coastal layouts exist, but they are sparse and often acquired late.**
The older Fractal has two clear good local opportunities. The current Continents
has a useful follow-through case at Perth and a late prospective pair at Dallas.
None of the three surveyed worlds built an adjacent Tailors–Harbor pair.
Geography helps explain the scarcity; it does not explain all the missing chains.

17 November2026, Problems1.1–1.4/1.6 and2.1, finding **AI-C210**.
[Compact survey, cases and capture hashes](csc-dockmaster-opportunity-survey-20261117.json).
No resource generation, gameplay rule or AI coefficient changed for this survey.

## Map inventory

| World and sample | Tailors Base deposits | Coastal material clusters with room for both districts | Quarter footprints / Quarter–Harbor combinations | Owned pairs passing both current native admission checks |
|---|---:|---:|---:|---:|
| Current Continents,50 |40|15|31 /50|0|
| Current Continents,250 |35|8|12 /18|1|
| Earlier Continents,250 |21|6|10 /17|1|
| Earlier Fractal,250 |14|5|9 /13|3|

A layout puts a land Tailors footprint next to its Base resource and a non-lake
water Harbor footprint. Quarter/Harbor footprints must be resource-free and
unoccupied by another district; existing matching districts are allowed.
Overlapping layouts sharing a material cluster are grouped instead of counting
every hex combination as a separate chain. The first columns describe physical
room across the map; the last adds ownership and actual current native checks.
Native pairs use owned, revealed, improvement-compatible Base material.

The current Continents had no usable owned pair at50, although15 coastal
material clusters existed globally. Expansion later reached some of them.
The reduction to eight open clusters by250 reflects development, including
resource removals and occupation of potential footprints.

## Good opportunities and concrete constraints

| World / city | Layout and ordinary Harbor quality | What is present / missing |
|---|---|---|
| Current / **Perth** |Base1239 → Tailors1313 → Harbor1387; Quarter+3, Harbor+2|Improved Base, completed Harbor and working Lighthouse. Quarter/Workshop absent. Strongest current follow-through case.|
| Current / **Dallas** |Base2683 → Tailors2756 → Harbor2755; Quarter+2, Harbor+4, matching the city's best Harbor|Improved Base and owned footprints; both districts absent. Positive Quarter offers first appear249.|
| Earlier Fractal / **Opis** |Base479 → Tailors478 → Harbor551; Quarter+2, Harbor+3, matching its best alternative|Improved Base; both footprints owned and currently admitted. Quarter, Harbor and buildings remain to build.|
| Earlier Fractal / **Karkar** |Base473 → Tailors546 → Harbor620; Quarter+2, existing Harbor+3|Improved Base, Harbor/Lighthouse and Naval Tradition present. Quarter/Workshop missing; Quarter placement currently admitted.|
| Current / Adrianople |Base392 → Tailors391 → Harbor317; Quarter+2, Harbor+0|Owned and currently admitted, but a weak Harbor. Both districts missing.|
| Earlier Continents / Dumbarton |Base360 → Tailors434 → Harbor433; Quarter+1, Harbor+0 versus best+3|Owned/currently admitted, but sacrifices a much better Harbor. Should not be promoted heavily.|

Thus Fractal has **two good owned local layouts**, one already furnished with
Harbor/Lighthouse. Its third currently admitted owned pair, Kinchassa, offers
Harbor0 versus best4 and lacks an improved Base. On the earlier Continents the
only fully owned/currently admitted pair is similarly poor; Selkirk's alternative
needs unowned water and has a full district budget.

Perth and Dallas are useful potential layouts even though their Quarter plots
fail the saved-world native admission query at250. Both contain existing
improvements, and the original live cache recorded eligible Quarter cells.
The save reload does not reconstruct the earlier comparison; retain both facts.
Quarter ratings above include eligible local Mill effects and existing customers.

### Perth's offer history

The Harbor was founded142 at+2. Main CSC first logs the adjacent Tailors offer143
at+2; later its local rating reaches+3. Native readbacks record **42 score writes**
for this Quarter candidate. Its last published offer at250 is615,380Q8, about
2,404 native utility. No Quarter foundation follows by250. This is a supplied
offer with an unfinished investment path.

Dallas differs: the planner first logs its Quarter/Harbor layout at249 and250,
with latest Quarter bid139,045Q8, about543 utility. The receipt shows staging and
a cache read but no fresh score write in that short window. It is a late planning
opportunity rather than a long-standing ignored offer.

Surveyed players with candidate pairs have Naval Tradition at the endpoint.
Dockmaster's sail-driven ship benefits make early completion preferable; existing
promotion stops after the Renaissance. This inventory counts chain layouts;
ordinary transaction income continues to matter later.

## Implication for our next change

First trace **Perth's remaining reservation/production path** and preserve the
strong nearby Quarter/Harbor plan through execution. Karkar is a useful saved
case for a future controlled test of current policy. These are more targeted
than increasing Harbor bonuses everywhere.

All five surviving Tailors in the current run are inland. Its576 passive
Harbor-neighbour records contain no water tile. A stronger adjacency SQL signal
cannot produce a Harbor beside them; coastal planning must connect before the
Quarter is founded.

If material assistance later gains a coastal objective, initially redirect part
of its existing budget toward a few worthwhile Base–Quarter–Harbor layouts.
Require ordinary Harbor quality, rather than merely water within two tiles.
Current material correction version4 emphasizes Tailors2× Base-only and4×
both-material sites but has no coastal objective. No such change is in this run.

## Evidence and repeatability

Current seeds18461107/29461107; earlier Continents22051116/32251116;
Fractal19672039/29812257. All are Small maps with five original AI seats,
City Lights, Resourceful2 and Sukritact's Resources. They used their original
frozen policy versions; the older maps inventory opportunities rather than test
today's tuning.

The shared controller loaded current50/current250/Fractal250 once each, checked
exact checkpoint/package/module identities and unchanged structural census,
ran the read-only query and verified zero elapsed turns. Every session closed
exit0 and restored mod preferences. Earlier Continents reuses its complete
previous map survey and native Harbor comparison. No competing tuner or desktop
automation was used. Civ is closed after the inspections.

Tools: `tailors_coast_survey.lua/.py` and `dockmaster_opportunity_results.py`.
The parser excludes lake Harbors and water/impassable Quarter footprints,
retains unknown values in older captures and deduplicates overlapping layouts.
The updated query adds ordinary Harbor Gold, best current alternative, working
Base, local Workshop, Lighthouse and civic state. Large captures and cloned
packages remain outside the repository.
