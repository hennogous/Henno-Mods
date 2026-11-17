# Customer district placement in the latest Continents run

**Connections outside Harbors are also modest.** Commercial Hubs have the best
vanilla customer connection rate; City Lights urban sales districts connect more
often. These whole-game counts include districts in cities without a Quarter.

17 November2026, Problem2.1, **AI-C212**.
[Physical counts and owner-specific evidence](csc-ai-customer-placement-breakdown-20261117.json).
Recorded-data analysis only; no game or tuning change.

| Customer district | Founded | Distinct sites ever adjacent to a mapped Quarter | Rate | Customer placed after an adjacent Quarter |
|---|---:|---:|---:|---:|
|Commercial Hub|16|3|19%|3|
|Entertainment Complex / Hippodrome|10|1|10%|1|
|Holy Site|7|1|14%|0|
|Theater Square|31|2|6%|1|
|Water Park|10|0|0%|0|
|Harbor|13|0|0%|0|
|CL urban sales districts, all three tiers|28|7|25%|5|

The3 Hubs have4 Quarter links: one Hub neighbours both Bakers and Tailors.
All3 are founded after an adjacent Bakers Quarter. One Theater follows its
Tailors; the other precedes it. The Holy Site precedes its Tailors. The connected
Entertainment Complex follows Bakers; all3 Hippodromes have no connection.
The loaded SQL connector definitions include Water Parks despite zero links.

CL goods providers are a separate direction:4 rural district sites connect out
of37 founded (three Rural Community A, one C). Two follow their Quarter and two
precede it.15 Bakers/City Center pairs also occur, all City-Center-first.

The construction denominator is the whole map, not the number with an equally
good adjacent alternative. Eventual adjacency includes Quarters placed after
customers. This measures connections rather than attributing all of them to
our guidance or classifying every unconnected district as a missed opportunity.

## Correction to earlier aggregate counts

The initial analyzer keyed relationships by player as well as plots. Capture
could count one physical pair again. Player identity remains useful for native
offer attribution; physical placement counts now deduplicate it.

| Measure | Earlier owner-scoped count | Physical count |
|---|---:|---:|
|All Quarter/neighbour pairs|42|35|
|Excluding City Centers|24|20|
|City Center pairs|18|15|
|Non-City-Center Quarter-first / customer-first|15 /9|12 /8|

Signal associations remain11 customer foundations with private yield, five
physical links with prior economic offers and two exact matches in each planning
direction. The prior ordinary-economy run corrects20→19 non-City-Center pairs;
the new run therefore moves19→20. Hubs remain three (previous3/15,current3/16).

Analyzer schema v2 keeps owner-specific evidence and counts physical sites once,
while preserving multiple Quarter links for a shared customer. Frozen loaded SQL
connectors supply zero-link types. Tests cover capture, shared customers and
zero-link Harbors. Archived v1 JSON remains the original owner-scoped output;
use this v2 report for physical counts.
