# Why the +2 threshold produces few additional Quarters

The new Continents records show that the +2 policy is active. The larger filter
is the value comparison against other districts, followed by capacity/admission
and production follow-through. The earlier results report concentrated too much
on the latter two stages when explaining the total construction count.

Scope: unchanged main CSC `9f450233`, XP2 SHA092abfbb, CE400e6755; ordinary
Small/Prince/Online250, map20851115/game31051115, CL/R2/Suk, original AI1–5.
This analysis uses the closed records and starts no new game.

## The actual +2 policy

`EconomyAdapters.PlacementValue` requires both Base supply and minimum+2. It
then requires a positive economic forecast after protection costs. Only after
that gate does a+2 site receive its **48 native-utility siting preference**.
The preference is144 at+3 and288 at+4, with bounded material-clump and customer-
layout preferences separately. A+2 geometry alone is therefore insufficient.

The economic model uses current customer district footprints, building/unlock
timing, maintenance, supply and other costs. An unbuilt customer does not provide
transaction income. Completing a Quarter also consumes an ordinary district
slot. All of these continue to matter after lowering the adjacency minimum.

## Recorded opportunity and choice funnel

| Placement band | Distinct positively bid city/type/plot identities | Published observations | Median total bid | Native new-Quarter best comparisons | Foundations in this band |
|---|---:|---:|---:|---:|---:|
|+2 to below+3 |99 |4410 |253.4 |3 |0 |
|+3 or better |52 |3181 |466.5 |13 |5 |

The identities overlap across bands as adjacency changes: there are118 distinct
positively bid identities overall, across46 city/Quarter scopes. Of the99+2
identities,88 are observed positively bid while owned. This is a repeated set of
overlapping planning options over250 turns, rather than99 independent districts
that should all be constructed.

There are558 distinct city/type/plot geometries observed at+2. Many never receive
a positive bid: the complete-value path still checks Base supply, usable
forecasts, protection and profitability. The aggregate captures do not assign
every omitted geometry a complete per-site economic rejection ledger.

All three+2 native wins belong to the same early Bakers1130 opportunity in
Niani, packets152/154/157. Population-slot snapshots are full4/4 and the native
tree returns Not Building/No contract. The same footprint later belongs to
Nioro, where capacity is0/1 and its rating is+3; it is founded179.

## Same-city, same-round price comparison

Select observations with a published **owned+2 offer and ready/exempt Quarter
capacity**, then join the native district selection on Core turn/player/city.
Exclude completed native footprints, Quarters, City Centers, Wonders and
unread/invalid native totals. For each selected native result, compare the best
matching+2 Quarter bid in that publication.

This yields **918 city-round observations**. The chosen other district has a
higher value in all918. Median winning native value is**2539.1**, against
**396.7** for the best matching owned+2 Quarter. These are same-round prices;
we do not replay admission of every Quarter offer or assume that a free slot
establishes all native legality checks.

For a concrete early case, Meroë's+2 Tailors2376 is bid82.8 on14 while the
native Holy Site2377 is chosen at272.4. The Holy Site later supplies a real
customer neighbor; Tailors becomes+3 and is founded39. The later Sacristan is a
successful consequence of that spatial sequence, not evidence that the earlier
Holy Site choice was mistaken.

The4096 Quarter ceiling is reached by only three published observations across
both bands.24 of the918 native alternatives exceed it. The ceiling deserves
awareness but is not the broad explanation for these low bids.

## What this changes in our interpretation

The lower adjacency bar admits many more bids, but most+2 bids still lose the
district comparison. Capacity and15-turn request expiry explain important
selected cases; they cannot explain the bulk of+2 opportunities that never win.

**Whole-Quarter calibration needs explicit review.** Using native Q8 pricing for
individual yield streams gives consistent units, but does not establish that
our whole investment is weighted comparably to native district/building totals.
Our model uses a fixed50-turn window and serial building preparation with
transactions gated by existing customers; the engine adds qualifying future-
building forecasts and its own heuristics. The score gaps warrant comparing
those assumptions before increasing a flat siting bonus or multiplying all bids.

Next1.4/1.6: take a few materially good+2 and+3 owned sites with free capacity,
compare their complete ledgers to the actual competing district forecasts, and
calibrate their overall strength. Preserve normal district/unit/project
competition and the spatial quality distinction. No live policy value changes
are made by this investigation.

## Diagnostic correction

The passive observer still labelled geometry as `qualified` at the legacy+3
threshold. Actual policy and published+2 bids were unaffected. The table above
recomputes bands from raw `upper` values using the active minimum2; raw logs stay
unchanged. Older `distinct_geometry_qualified_candidates` summaries therefore
mean the observer's+3 label for this run, not the policy's eligibility floor.

The maintained observer now reads `EconomyAdapters.MinimumAdjacency`, records
`minimumAdjacency` and falls back to3 for legacy adapters without that field.
It still neither publishes its own bids nor repeats a forecast.24 observer/
analysis checks pass, including the live-minimum and legacy-label cases.

[Counts, match filters and examples](csc-ai-quarter-bid-funnel-20261115.json).
Source artifacts remain under
`C:/Users/Shadow/Desktop/Codex/csc-ai-new-continents-20261115/continents250-01/`.
