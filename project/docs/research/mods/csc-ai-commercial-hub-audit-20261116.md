# Commercial Hub co-location audit — recorded latest250

16 November2026, **Problem2.1**, completed customer-first Continents250,
map22051116/game32251116, stock AI1–5, CL/R2/Suk. Policy19e29a42; CE2d200ef,
XP2 SHA092abfbb. This audit uses saved records only, as Henno requested while
using Civ VI/FireTuner. The current session was neither queried nor altered.
No replay, new game or tuning change. [Original results](csc-ai-customer-first-continents-20261116.md).
[Machine-readable footprint audit](csc-ai-commercial-hub-audit-20261116.json).

## Result

There are **two credible additional co-location opportunities**, at Aberdeen
and Napata. Each has a recorded owned, unprotected, resource-free footprint beside
a completed Bakers, with reconstructed ordinary base Gold matching the chosen
Hub's observed+2. That suggests at least some additional Hubs could have served
Quarters without a simple adjacency sacrifice. Aberdeen also presents a real
planning trade-off: that same footprint later becomes a good Tailors.

Among19 Hubs: three already touch completed Quarters, six have none within reach
at their native-choice turn, and ten are nonadjacent despite a Quarter near their
city. In that latter group, same-turn ownership/opportunity records identify
three resource-free footprints in two cities:788 at Aberdeen,1751/1825 at Napata.
The remaining geometric options include materials/luxuries, other cities' land,
and unknown historical ownership. This is a lower-bound opportunity audit, not
a count of every counterfactual legal Hub target.

## Two cases

|City|Completed supplier|Chosen Hub: foundation Gold|Alternative|Reconstructed base Gold|Later use|
|---|---|---:|---|---:|---|
|Aberdeen, player5|Bakers789, completed109|936:+2; native choice110|788, adjacent to Bakers|+2|Tailors187, complete188|
|Napata, player3|Bakers1826, completed45|2121:+2; native choice122|1751, adjacent to Bakers|+2|Spaceport168, complete190|

**Aberdeen788:** live opportunity record110 says owner5, same city262147,
frontier=false, protected=false; the map records no resource/feature. At that
point its neighboring districts are City Center862, Bakers789 and CL rural
713/714. The rural districts complete100/104 and Bakers109. The tile is river
adjacent (recorded when Tailors is built there). Base Hub arithmetic is River2,
minor adjacency2 from four districts, minus two CL rural Gold penalties: **2**.
There is no extra Lua Hub offer in109–111. The chosen site's native total at110
is **1607.188 utility**. Placing a Hub on788 would consume the later Tailors
footprint, so this is not an automatic improvement to the final city plan.

**Napata1751:** opportunity122 says owner3, same city131073, frontier=false,
protected=false. It is flat grassland floodplain, with no resource, beside
Bakers1826. CL rural1750 exists from69, completes78, and belongs to player12
until211. The ordinary rule reconstruction is River2 plus minor adjacency1
from Bakers/rural, minus the rural penalty1: **2**. No extra Lua Hub offer exists
in121–123. The chosen site's native total at122 is **1817.723 utility**.
Napata's other owned resource-free neighbor1825 has no river contribution in
the contemporaneous Tailors geometry and is less attractive on ordinary Gold;
it later becomes a Theater Square.1751 is the cleaner no-adjacency-sacrifice
candidate. Its later Spaceport use does not establish that native AI reserved
it for that purpose at122.

These are **base adjacency reconstructions**, using fixed geography, dated
neighboring district events and the rules used in this run. They are not recorded
counterfactual UI quotes or native legality results. The selected Hub's Gold is
sampled at foundation (113/123), while comparison turns are110/122. The losing
Hub cells and their component breakdown were not captured in the original run;
exact native eligibility, policy/city modifiers and winning margins need a
historical replay when Henno makes the machine available. The current records
still establish the concrete footprints, ownership, completed supplier and lack
of an extra Lua offer.

## Why the current guidance did not tip them

The loaded native SQL graph contains the **+1 private AI-yield link from Bakers
to Commercial Hub**, and both Bakers are completed before selection. This route
is active. The [earlier matched native test](csc-ai-native-customer-signal-20261116.md#controlled-native-replay)
shows that this input can change the selected Hub site; its measured utility
contribution there is35–48, not a universal value for every player/turn.

The newer Lua customer-first adapter handles **empty future Quarter footprints**.
It deliberately suppresses speculative credit for an already existing supplier
city/Quarter type, leaving those links to native SQL. Thus these two adjacent
sites receive **no additional Lua preference for serving the actual Bakers**.
The central Quarter ledger does not override the Commercial Hub's whole native
bid. Its native site costs and forecasts can still favor another location.
The winners' totals are recorded; the absent losing cells prevent assigning the
loss specifically to a Farm, worker yield, reservation or another native term.

This identifies a concrete coverage gap in2.1: after Quarter foundation, a
bounded customer preference/valuation for its real economy is missing. A focused
next check would compare the actual Hub cells at110/122 and test that preference,
retaining ordinary adjacency, material protection and valuable future Quarter
footprints. Increasing all customer bonuses blindly is not required by this audit.
Full prospective Service valuation remains separately queued under14.3.

## City Lights matters to the comparison

`Gameplay/COREX_Core.sql` attaches `RurComA/B/C_negGold_1` to Commercial Hub
(and Harbor): **−1 Gold per adjacent rural district**. Boroughs separately add
positive Hub Gold. Therefore a river tile beside a Quarter does not automatically
retain all its apparent Hub advantage. In Aberdeen, the two rural penalties
consume the ordinary minor-district gains; co-location would tie+2 rather than
produce a simple+4. This complements AI-C195: those penalties do not target CSC
Quarters themselves, but they do affect their customer districts.
The local CL source SHA13b976b1808d183a17971d3c246112f6ed7c2e99104845d1f6c3d1cc0dab6525
matches the original run's pinned manifest.

## All19 decisions

Gold is the selected district's placement-event Gold. The scope column uses
completed owned Quarters at the recorded native-choice turn, within a possible
city radius3 plus one neighboring hex.

|City|Choice turn|Hub plot|Gold|Recorded opportunity context|
|---|---:|---:|---:|---|
|Yangsan|70|2030|3|No nearby completed Quarter|
|Ray|72|2612|0|Resource, occupied or city-control constraints|
|Seoul|73|2105|2|No nearby completed Quarter|
|Aberdeen|110|936|2|Open owned footprints 788|
|Haddington|118|1528|3|Already adjacent|
|Napata|122|2121|2|Open owned footprints 1751,1825|
|Amsterdam|130|2970|2|No nearby completed Quarter|
|Gyeongju|135|1440|0|No nearby completed Quarter|
|Sedeinga|137|1759|2|Resource, occupied or city-control constraints|
|Roxburgh|140|871|0|Resource, occupied or city-control constraints|
|El-Kurru|147|1830|4|Already adjacent|
|Sparda|153|1651|3|Already adjacent|
|Ayr|157|1078|5|No nearby completed Quarter|
|Bakhtri|159|2611|0|Resource, occupied or city-control constraints|
|Newcastle|189|1864|1|Resource, occupied or city-control constraints|
|Gordian|216|2165|3|Resource, occupied or city-control constraints|
|Eindhoven|216|2307|4|Resource, occupied or city-control constraints|
|Iken|228|2195|2|No nearby completed Quarter|
|Johannesburg|240|1897|3|Resource, occupied or city-control constraints|

## Reproduction

`project/tools/ai_economy/audit_commercial_hub_placements.py` joins original
`planning-results.json`, raw `CSC_PLANNING_*` district history/opportunities and
`coast250-02/tailors-coast-survey.txt`. It includes minor/foreign district history,
which the original-AI construction summary filters out. Dates and ownership are
joined at each native decision, rather than taken from the endpoint map. The
endpoint map supplies geometry and explicitly labelled endpoint resources;
unknown historical legality/adjacency/native cells remain unknown.

Civ's odd-row/east-west-wrapped geometry is checked against **52 native adjacent-
plot paths** in the archived survey. Audit output contains19 Hub records, their
candidate footprints, same-turn city scopes and proposal windows. No connection
to Civ VI/FireTuner is made. No new reusable engine mechanism is asserted here;
these are CSC coverage and City Lights application findings.
