# Offline chain decision cases — 28 October 2026

Built from CLOSED turn100..105 mechanism-study artifacts while Henno uses Civ
for manual QA. No live game/cache/client access, new decisions, game control,
deployment or gameplay changes. These cases support the
[roadmap (historical)](https://github.com/hennogous/Henno-Mods/blob/819b67c/project/docs/integrations/csc-ai-roadmap.md), not a new test result.

## Reusable extraction

`project/tools/ai_tuning/offline_cases.py ARCHIVE --output OUTPUT.json` reads
three explicit archived JSON files. The output records their SHA256, exact
source pointers, scope and missing information. It has no native dependencies.
Output for this study: `Desktop/Codex/csc-native-ai-analysis-20261028/offline-chain-cases.json`.

Five focused integrity tests pass: city IDs never join across players, different
district types never pair, missing yields remain unknown, private and real
values stay separate, and duplicate source options fail rather than inflate
counts. Archived-case assertions additionally verify Coimbra's four alternatives,
absence of Harbor rows and the Rice1087 repair record.

## Opportunity set, not decision count

The archive contains 888 customer-site records. Grouping by
`(player, city ID, district type)` produces 819 adjacent/nonadjacent option pairs.
Of these, 74 have higher captured real Gold on the nonadjacent alternative and
554 have equal captured Gold. These are overlapping option pairs, not 819 unique
jobs or 554 economically equivalent sites. Other yields, downstream benefits,
costs and actual decision exposure are not fully observed. Existing source
district-index mapping caveats remain in the output.

## Case A: customer opportunity without a customer decision

Coimbra, player4/city131073, has an archived Harbor option at1266 adjacent to
Quarter1341: real Gold0/private10. Same-city nonadjacent options are1194 Gold3,
1195 Gold2,1193 Gold1 and1196 Gold0, each private0. This is a genuine same-city
trade-off; it is **not** the desired +4 conflict case.

The baseline/customer0/customer30 review has no logged Coimbra Harbor-tree rows
in the studied interval. Baseline production instead records:

| Turn | Logged event |
|---|---|
|100|Workshop contract1871 selected; Builder contract1995 completed|
|101|Builder contracts2081 and2084 submitted|
|103|Workshop1871 completed; Builder2081 selected|
|104|Builder2081 cancelled; Builder2084 selected; Fashion House2181 submitted|

These are native log events, not independent physical completion checks in this
extractor. Original raw rows use player/city name; numeric city ID comes from the
site exposure and is recorded separately. Do not infer the cancellation reason,
Builder scarcity, or why no Harbor was requested from this sequence alone.

Planner/test implication: keep **eligible opportunity** separate from **actual
selection exposure**. A favorable site need not be the city's next investment.
Use this as a customer opportunity case and a production/Builder trace candidate,
not as proof that the customer incentive was ignored.

## Case B: repair need without proven access or assignment

Player5 Bakers1160 has Rice1087 recorded as last-Base supply in repair state at100.
This is the sole repair support link in this extracted snapshot (not a whole-map
claim). Prior outcome analysis found no repair benefit through105.
Reachable available charges, path safety, job legality and fresh assignment are
not established by these records. The evaluator should report repair need plus
unknown execution feasibility, not invent a Builder shortage or scorer failure.

## Case C: intervention after a competing commitment

The baseline outcome records player1 Tailors1863 first observed at101, replacing
Maize. The mechanism-results report traces accepted Tailors contract2012 to99,
before the100 treatment, next to assisted Bakers1862. The current extractor
preserves the recorded outcome and cites the earlier commitment evidence; it
does not pretend the original99 logs were re-audited here.

Planner/test implication: a planned future customer or new Quarter must carry
existing commitments and lost supply as costs/constraints. A post-commitment
preservation intervention is not a clean test of avoiding the original choice.
The prepared pre-commitment pair remains unobserved; no retry is started.

## First evaluator contract

The first planner artifact should be an explainable fact vector, before a single
weighted score. Required groups are:

- Identity/provenance: player, city, Quarter/type, plot, observation turn,
  package/mappings and source pointers.
- Present benefits: separately measured real Production/Gold and other relevant
  yields, mapped Base/Specialty, river, existing customers and built stages.
- Future plan: specific legal improvement/customer plots, unlocks, ownership,
  conflicting commitments, execution requirements and estimated delay. Unknown
  feasibility gets an explicit unknown state, not free development credit.
- Costs: fresh versus estimated acquisition costs, own/subsidy portions,
  production, Builder charges/travel, lost resource/tile benefits, district
  capacity and opportunity cost of competing locations.
- Chain state: incomplete/working/pillaged, missing next stages, available
  development capacity and observed risks. Missing supply and missing customer
  buildings are distinct bottlenecks.
- Alternatives: start this chain, develop/repair an existing one, or defer.
  Explain conflicting land claims and shared benefits without double-counting.

Current archive extraction provides useful opportunities and counterexamples,
but not all these fields. It cannot responsibly certify a +4 future site or
calculate net empire return. The next offline step is to add available archived
world facts and identify remaining capture needs before calibrating weights.
Do not force absent facts into zeros to make the proposed score computable.

Sources: [mechanism results](csc-ai-mechanism-tests-20261025-results.md), archived
natural-exposure100.json, coimbra-customer-decision-review.json and
quantified-outcomes.json; exact source hashes reside in the generated casepack.
