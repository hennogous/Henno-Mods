# Tracing the four +2 winners and giving +2 a useful preference

All four winners can be followed in the archived250 game without another game
or native probe. They represent **three cities**, with two failed nominations
in Alexandria Troas. Each comparison value reached the native selector; the
remaining obstacles occur later.

| City / observed winner | Quarter and site | What happened |
|---|---|---|
| Aachen,108 | Tailors2238,119.79 utility | Request1886 is submitted107 and the tree reports acceptance at119 from108–118. A Builder occupies production throughout that window. At119 the city appears under player62 instead of5; it later returns to player3. No Quarter foundation appears. |
| Alexandria Troas,140 | Bakers1342,1,338.87 | Population8, three population districts used and three allowed. The tree reports `Build Unit: Not Building`; no Quarter request is submitted. |
| Alexandria Troas,142 | Bakers1267,1,227.23 | A second site wins, with the same population/slot constraint and the same failed admission. Population9 at144 still allows only three. |
| Adrianople,197 | Tailors1574,2,537.87 | Request4547 is submitted196 and accepted. Its retained value refreshes to about1,376.6, later1,393.9. Artillery takes production198, a Market207, then Artillery208. Waiting reaches15 of15 at211; the request expires212. A Hippodrome is nominated213. |

The logs' cached `eligible=1` is not a population-slot permit. Alexandria's two
comparisons do not reach production competition. Keep future bids visible:
the earlier timing experiment established that growth can occur after global
publication. Native admission remains the construction gate.

Adrianople's first Artillery request is recorded around8,628 utility; the later
Artillery around7,233 and Market around1,955. Even assigning another64 to the
retained Quarter value would leave those recorded alternatives ahead. Aachen
has no idle queue before the control change. These four cases therefore do not
justify forcing a request, extending its wait or overriding district capacity.

## New calibration in main CSC

Henno requests meaningful support for otherwise worthwhile +2 sites. Start at
**48 native utility**, half the existing +3 preference. The normal model first
requires owned Base and positive economics after protection deductions.

| Adjacency | Siting preference | With Base and Spec |
|---|---:|---:|
| +2 | +48 | +64 |
| +3 | +96 | +112 |
| +4 | +192 | +208 |
| +5 | +288 | +304 |
| +6 or more | +384 | +400 |

Fractional adjacency interpolates48→96 between +2 and +3. Higher bands keep
their existing slope and cap. This changes the complete Quarter bid in
`CSC_AI_EconomyAdapters.lua`; positive legacy fallback adjustments are replaced,
not stacked. One utility point is256 Q8, so the +2 floor adds12,288 Q8.
Economic losses, no-Base deferral, material protection, normal slots and other
production choices retain their existing gates.

The37 economic/SQL tests and six publisher fixtures pass. The real owned/frontier
bid-path fixture verifies the extra12,288 Q8 reaches outgoing entries. Tests
also cover fractional72 at+2.5, Base+Spec64 at+2, unchanged higher bands, and
unprofitable and no-Base sites remaining deferred. This is a unit-qualified
new calibration; the preceding250 game used zero preference at+2.

## Evidence

[Compact trace summary](csc-ai-adjacency-two-followthrough-20261115.json) records
the four native winners, proposed48/64 arithmetic and source-file hashes.
Detailed city build, behavior and queue slices are under
`C:/Users/Shadow/Desktop/Codex/csc-ai-adjacency-two-20261115/`.
The original records remain in
`csc-ai-astra-gaps-20261114/fresh250-02/`.

Native request/cadence interpretation uses AI-N127/131. Current population
diagnostics and observed request failure identify Alexandria's admission gap;
no new native rejection-reason enum is inferred from `Not Building`.
