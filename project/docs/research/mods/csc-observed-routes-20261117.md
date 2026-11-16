# Shared ordinary trade-route economy

17 November2026. G3, roadmap1.4/2.1/2.2. Services remain deferred.

The existing gameplay route payouts now have one shared read-model and pure
eligibility/arithmetic kernel. The live property scanner, BTS preview, UnitPanel
preview and SUIA use the same native definitions. AI counterfactual integration
is the next dependency; this slice publishes no new AI bids.

## Definition authority and preserved gameplay

Quarter transaction sidecars declare four channels and their existing native
modifier bindings. The late SQL processor reads the actual supplied-property
requirements and each payout's five native bits. It produces80 payout rows with
transaction Gold enabled,60 without. It changes no native effect, amount,
requirement or attachment. Unsupported gate, lifecycle or collection changes
fail qualification instead of being approximated by copied constants.

Preserved rules:

- Both domestic and international routes qualify. Owner-qualified city IDs
  distinguish equal city IDs belonging to different players.
- Bakers eligibility reads the destination's supplied property. Tailors also
  requires the relevant intact producer. These existing rules remain distinct.
- An unpillaged origin Quarter blocks its family's imports from foundation,
  before construction completes. This follows native HasDistrict defaults.
- Destination building-yield receipts require an intact receiving building.
- Counts remain complete, but payouts follow the native five bits:32 wraps to0.
- The existing host-authorized Version2 network operation remains the sole
  property writer. Read-only AI observations submit no operations.

Two preview corrections are intentional: Tailors now checks its intact producer
consistently, and disabled transaction Gold no longer appears in previews.
Export previews also omit amounts when the receiving producer is absent or
pillaged. These change presentation, not gameplay payouts.

## Observations and duration

The scanner exposes a cached plain-record snapshot of actual cities/routes,
invalidated by route/building/property events and turn changes. A bounded reader
qualifies durations in Gameplay using the trader's active MAKE_TRADE_ROUTE
operation and PARAM_TURN. The native outgoing UI record contains identities and
yields, but no duration or progress field.

Native minimum-end calculation, relative to operation start S:

`S + max(1, floor(base * speed / 100) + floor(globalEraChange * speed / 100))`.

Speed is GameSpeeds.CostMultiplier. The era is the current global era; join
Eras_XP2 by EraType. Native completion additionally waits for return to origin.
Forecast only through current-policy earliest end eligibility; after that, or
when duration is unknown, retain one observed turn and assume no renewal.
UI packets older than the one-turn phase allowance, future packets, or operations
started after the packet cannot establish a duration. The AI integration must
reject stale observations as whole facts, rather than use their fallback window
as evidence that an old route still exists.

## Native evidence

Reference XP2 SHA256
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`;
runtime `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
Identical full .text SHA
`d5bc8feddb8c030dbf2afc3fa9d9110eadbdb349cdb8aa56d5928625290c3d79`.

Relevant RVAs: outgoing692f30/cache7a9f0/helper693440; unit operation6feb30,
parameter6fe940, initialization40b80; minimum end38f720 and completion66bf70;
speed adjustment36f620/36f6f0. HasDistrict UI68e680→715b0 defaults
onlyComplete=false. Private traces stay outside the repository.

`C:/Users/Shadow/Desktop/Codex/csc-ai-ordinary-economy-20261116/routes250-01`
contains the bounded zero-turn replay. It matches the legacy scanner's complete
packets for67 cities and qualifies43/43 actual trader start times;20 are already
eligible to finish and therefore get one observed turn. Current policy is
Online50%, Future-era change30, base20. All10,954 CSC native effect rows,
137 fixed rows and the67-city population refresh match. No operations were
submitted or AI turns advanced. Native exit0, preferences and package restored.
The subsequent stale-packet guard is covered offline; replay packets are same-turn
and unaffected by that guard.

## AI integration and next checks

The pure route kernel accepts explicit future Quarter/producer/supply events
from the central plan, recomputes all counters together, and merges equal
continuous segments. Route count is bounded4096, event boundaries128. It invents
neither workers nor routes, and callers cannot claim a complete forecast after
exceeding either budget.

Native AmenityValue5272a0 compares the city's current happiness state with the
state after an amenity change. Price all concurrent route amenities together
per receiving city and interval. Current city amenities already include actual
CSC imports; hypothetical quotes must use offsets relative to those actual
amenities. Summing separate channel quotes can count the same happiness threshold
twice. The present CE pricing API's±8 bound needs consideration before larger
totals can be priced; splitting a nonlinear quote into chunks is incorrect.

Complete G3 by connecting route events to shared investment readiness, building
the live affected-customer world and accounting for adjacency/material changes.
Then qualify existing native overlap and residual delivery (G4), and measure the
complete priced path (G5). Keep native SQL placement preference1 during calibration.

## Human review after the complete implementation

Check a normal domestic and international import preview against its working
counterpart, both producer stages, a pillaged Tailor producer, and transaction
Gold disabled. Confirm that founding an origin Quarter stops imports and that
producer/supplier recovery resumes the appropriate route effects. The final
goal handoff will combine these with the other economy migration QA cases.
