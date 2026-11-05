# CSC gameplay-to-AI forecast coverage map

5 November2026. Offline reconciliation requested by Henno after the combined
Mill/building probe. **No game, native hook, score change, CE API change or further
repair investigation.** The human reading surface is the maintained
[effect coverage map](../../civ6-ai/topics/csc/forecast-coverage.md).

## Inputs and completeness

The unchanged source inventory has22 contribution groups and4 common native
components,19 loaded buildings and88 building-root attachments. All39 pinned
source files still match their exact-byte hashes. Only Bakers/Tailors are active.

The closed two-city analysis has361 complete pairs and complete modifier/district
accounting. Each source building/root tuple was matched to exactly one gameplay
group using its owning table and explicit root IDs/selector. Restricting ownership
matters: export supply-property names also match the trade prefix, but their
BuildingModifiers roots belong to the state group; actual trade consumers are
DistrictModifiers on City Center.

All88 source tuples have one observation in each city:176 root observations,
zero unmapped roots, zero duplicate classifications. These are attachment counts,
not a count of economic relationships or the percentage of value understood.
Improvement-, customer- and CityCenter-owned consumers remain separate scope.

The [portable JSON](../../../tools/native_ai/mill_building_study/ledger/forecast_coverage.json)
keeps all26 classifications, source channels, next questions, per-root accepted/
Q8 outcomes and child-call counts, plus input hashes. It supplements the original
source-only `contributions.json`; that historical inventory's unmeasured status
is not the current interpretation. Update the map and human topic together when
new evidence or source changes arrive.

## Refined interpretation

- Preserve roughly represented local exchanges and direct amenities.
- Correct demonstrated false eligibility: small Mill steps without geometry,
  both alternative Mill recipients, absent-Wonder Fashion House GPP.
- Producer-to-material wrappers have observed null collection iterators;
  reached Tourism and Café Service-grant children have absent effect analyzers.
- Do not generalise those missing consumers to all Services. Growth, Housing,
  Faith, Dockmaster and several GPP/grant roots return accepted zero with no
  child reached in these contexts. Their positive eligible cases are unmeasured.
- Improvement-to-producer income, ordinary population sales, routes, staffing
  and exact regional geography have no complete attribution here. In particular,
  a zero property-writer result is not a forecast of its later economic consumer.
- Raw district sums, mutable prerequisite construction values and hidden
  structural values are different. Do not add all of them to a new site bonus.

Native analysis input hashes retained in the JSON:
trace `026e421378a1dd9808e3ea923c2b13bc779fef5dda7ef77f2313653b999f2538`;
source world `49e31963f01f9e6220bee8c2bba0ab33f40adc3d874edb1ee593ea7b871b427e`.
Original artifacts remain under
`Desktop/Codex/csc-mill-building-study-20261105/run-03/independent-analysis/`.
Existing finding scope remains [AI-C059] and [AI-N074]; this is a crosswalk of
that evidence, not a new native experiment or universal missing-value claim.

## Deferred Mill issue

Henno explicitly chose to watch for the repair discrepancy in longer ordinary
test games rather than pursue dedicated reproduction now. Retain native payout,
Quarter/Mill health/location, property state and lifecycle history when such a
case appears. No fresh game is started by this map or its next-question list.
