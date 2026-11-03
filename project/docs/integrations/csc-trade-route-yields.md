# CSC trade-route yields and SUIA display

## Bakers route contract

An eligible domestic or international route imports from a supplied Bakery and/or Cafe when the
origin lacks a functioning Bakers' Quarter. Bakery supply requires an adjacent
improved base material; Cafe supply requires adjacent improved base and specialty
materials. These are material-supply gates, not the complete Service civic gates.
The scanner reads the destination's SQL-owned `CSC_BAKERS_BAKERY_SUPPLIED` and
`CSC_BAKERS_CAFE_SUPPLIED` properties.

Each eligible route contributes +1 Food and +1 Amenity per supplied channel to
its origin, and +1 Production and +1 Gold per channel to its destination's
corresponding building. Routes to different supplied cities each contribute the
full amount. Two Bakery destinations therefore provide +2 Food and +2 Amenities;
a supplied Cafe at either destination adds its independent channel.

Origin and destination counts are represented by the existing 1/2/4/8/16 binary
modifier pattern (0–31 per channel). The base modifier handles bit 1, with generated
companions for 2/4/8/16. The receiver derives flags from counts and writes both city
and City Center plot properties. The UI compares import bits as well as counts
so saves with legacy positive counts acquire their missing import flags.

`ModSupport_SUIA.sql` explicitly registers each Bakers Food modifier bit with its
property and amount. `Suk_YieldTT.lua` sums active registered bits, subtracts the
already-paid Food from **Modifiers**, and adds it to **Outgoing Trade Routes**.
The total is unchanged. Destination Production/Gold remain building yields;
this override does not add an Incoming Trade Routes bucket. Amenities are not
normal yield tooltip entries.

## Tailors route contract

The same per-route pattern applies to Tailor and Fashion House imports. Each
eligible route pays +1 Culture and +1 Amenity per supplied building channel to its
origin. Two distinct destinations with both buildings supplied therefore pay
+4 Culture and +4 Amenities in total. Losing one channel reduces both by 1.
The existing destination-building/pillage, material-supply and
origin-without-functioning-Tailors-Quarter gates remain in the scanner.

Tailors' own SQL defines its import bit modifiers. The shared receiver derives
all four Bakers/Tailors import channels' flags, and the UI repairs missing legacy
bits for each. SUIA registers all Tailors Culture bits under Outgoing Trade Routes,
and the Tailors contract checks every companion's amount and exact property gate.
This extends the source stacking repair at Henno's explicit request on 24 October;
no files were installed into the open game and native stacking remains pending
rebuild/reload.

## Equal international exchanges — 24 October 2026

Henno explicitly requested equal international and domestic CSC exchanges,
including UI handling. The same source-building supply, origin-Quarter exclusion,
per-route amounts and channel stacking now apply regardless of city ownership.
The gameplay scanner counts every active route once at its origin and credits
the actual destination owner. The synchronized host operation already carries
the target city's owner separately from its sender, so no cross-owner mutation
shortcut is needed.

Better Trade Screen previews/overview yield arrays, their import/export tooltips
and Amenity display use the same eligibility for foreign routes. The selected
Trader panel includes the same Food, Culture and Amenities. SUIA reads the same
origin import bits for either nationality and moves their full Food/Culture
amounts into Outgoing Trade Routes without changing city totals. Destination
Production/Gold still belong to the supplied buildings and retain their normal
building-yield presentation.

CSC amounts are flat city/building modifier payouts. BTS adds them after native
international route multipliers, matching the real effects. This changes CSC's
additional exchange amounts; vanilla routes retain their normal native yields
and modifiers. The contract's route pattern is now `GP.TRADE.SUPPLIED_ROUTE`;
older `LP.TRADE.DOMESTIC_*` localization-pattern IDs describe the existing bullet
format and do not impose a route-nationality gate. Player-facing descriptions
already refer to Trade Routes generally and need no wording change.

## 24 October 2026 native diagnosis

At turn 8 in Henno's manual game, Alexandroupoli had an active domestic route to
Pella. Pella's Bakery supply property was 1, but both cities' route properties
and revisions were absent. Alexandroupoli's native Food tooltip contained only
5 Food from Worked Tiles, and its total Amenities were 0.

The empty `CSC_TradeRouteInteractions` UI context was hidden. Its events queued
refreshes, but the hidden context did not execute the deferred `SetUpdate`
callback. Setting that context visible allowed the existing synchronized
operation bridge to run without changing turns or creating routes. Independent
reads then showed origin import count 1, destination export count 1, revision 1
on each city, +1 Food from Modifiers in the native tooltip, and total Amenities 1.
Henno confirmed that SUIA displayed the Food in the correct category and that
the Amenity appeared.

The permanent source fix explicitly shows the empty context and queues a refresh
on `LoadScreenClose` as well as the existing events. The separate source stacking
fix changes Bakery/Cafe imports from positive-count activation to binary counts.
Neither source change was installed into the open game. The context wake was the
only live repair; rebuilding/reloading is required to exercise the new stacking
SQL. The existing user edit to Bakery CitizenSlots was preserved.

## Verification and remaining scope

- Six focused tests execute Bakers/Tailors distinct-destination stacking, supply loss, route
  removal, hidden-context updates, legacy-save reconciliation, and the production
  SQL/presentation amounts for every count 0–31 in all four import channels.
- Those six plus eleven multiplayer/lifecycle tests pass under Lua 5.1.
- Eighteen existing phase/manifest/presentation regression tests pass. Both edited
  SQL files pass the layout checker.
- Four additional international tests execute host-to-foreign-city updates,
  combined domestic/foreign counters, the actual BTS multiyield getters with
  international multipliers, Trader-panel eligibility and the production SUIA
  reclassification helper. Together with six route-contract validator regressions
  and the prior checks, 45 focused tests pass;
  the 21 gameplay/UI execution tests also pass under Lua 5.1.
- Native multi-route stacking after rebuild/reload remains unverified. The live
  success above verifies the existing single-route payout and SUIA classification.
- Tailors' implementation contract, resolved trade-stacking decision and SUIA
  assertions now track the matching per-route bit gates. Full contract validation
  reports current Bakers gameplay/localization reference-hash drift, the
  unreconciled Bakers material declaration, and an out-of-date generated Bakers
  text file. The localization drift appeared during concurrent source work;
  these unrelated inputs and locks were preserved. Focused stacking, lifecycle
  and presentation checks all pass.

Focused checks live in
`project/tools/quarter_contracts/tests/test_bakers_trade_routes.py` and
`test_multiplayer_hardening.py`. Use the documented isolated `lupa` dependency
from [multiplayer hardening](csc-multiplayer-hardening.md) for offline execution.
