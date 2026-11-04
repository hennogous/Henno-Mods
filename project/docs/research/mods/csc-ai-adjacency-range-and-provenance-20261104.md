# Why the adjacency engine has a 1023 range, and what CSC needs

4 November 2026. Source/rules audit following the Bakers building-forecast
investigation. No game was started, loaded or controlled for this audit; no
installation, gameplay, tuning, compiler or property writer was changed.

**The 1023 range comes from MAB's general binary encoding architecture. Current
CSC adjacency rules require much smaller per-rule amounts: 0–1, 0–3 or 0–6.**
We can specialize that encoding without discarding the shared rule matcher,
ownership logic, compatible-resource support or placement UI. Smaller encoding
alone does not make a native forecast faithfully evaluate its conditions.

## Provenance: adapted architecture, independently implemented CSC code

The [CSC integration record](../../integrations/csc-adjacencies.md) identifies
Ruivo's declarative rules, plot counting, ring traversal and property-backed
modifiers as architectural precedents. CSC independently implements its own
schema, compiler, evaluator and UI. It does not ship Ruivo's source or require
the MAB mod. Zegangani is credited for the historical specific-Wonder approach.

Read-only local MAB reference `NEW_ADJACENCY_BONUS_BY_RUIVO` is clean at
`d852b8466cf7152f4fd76cacec5fa8c2084d7c0a` (`test/all-features`). This is Henno's
integration branch, not pristine upstream. The 10-bit ladder is also present in
its upstream base `e978e6cdd7974f9db7e4ce3ef16e8a7e732e7d8b`, independently read
with `git show`; it is not a CSC-only invention.

- MAB `MAB_CORE_TABLE_INFO.sql:423–428` defines `Ruivo_BinaryList` as
  1,2,4,8,16,32,64,128,256,512, with a documented maximum of 1023.
- MAB `NEW_ADJACENCY_BONUS_BY_RUIVO_CORE_INSERT.sql:83–105` generates per-bit
  modifier amounts and property conditions for multiple provider types.
- MAB `NEW_ADJACENCY_BONUS_BY_RUIVO_GP.lua:16–59` multiplies count by the authored
  yield, truncates toward zero, caps the magnitude, and writes the binary bits.
- CSC `CSC_AdjacencySchema.sql:69–70`, `CSC_AdjacencyModifiers.sql:91–119` and
  `CSC_AdjacencyCore.lua:366–388` retain that numerical pattern in new code.

This establishes technical lineage. It does not establish the author's reason
for choosing exactly ten bits or any prior awareness of the native AI issue.

## MAB supports quantities far broader than adjacent resources

The inspected MAB source exposes and dispatches 141 named `FROM_*` functions.
That is a source inventory, not 141 verified runtime behaviors. Examples:

| Family | Actual source examples | Why six adjacent plots is not its general limit |
|---|---|---|
| Arbitrary properties | plot/city/player/game property, hashed and ring variants | A property can contain a caller-supplied magnitude. |
| Game statistics | storm count, standardized turns, highest human yield | Turn or yield totals can grow far beyond a local neighbor count. |
| City statistics | population, housing, surplus housing/food/amenities, district count, yield | These are city-level quantities, sometimes fractional or negative. |
| Player statistics | tech/civic totals, unit totals, resource types, yield, policy-slot totals | These aggregate an empire. |
| Ring statistics | hit points, damage, defense strength, workers, units, yields | A plot may contribute a quantity, not just a Boolean match. Wider bands add more plots. |
| UI statistics | unit levels, appeal, aircraft slots/units, plot yields | These use additional contexts and can aggregate several entities per plot. |
| Conditional owners/providers | buildings, policies, traits, technologies, civics, governments, promotions, beliefs; yields and other effects | The system is a general authoring interface rather than a fixed Quarter adjacency formula. |

Function anchors in MAB `RUIVO_STAT_MODULE_GP.lua`: property functions `:828–1035`,
game statistics `:1047–1080`, ring/UI functions including `:2196–2246,2660–3045`,
city statistics `:3078–3244`, player statistics `:3338–3510`; actual dispatch starts
at `:4340`. Owner gates are implemented separately at `:352–444`. The reference
also has arbitrary inclusive min/max ring traversal at `:15–58`.

CSC currently declares 55 supported source names, but only **five exact source
IDs** occur in the loaded rules. Retaining a tested helper is different from
needing all of MAB's general numerical capacity for every loaded rule.

## Complete current rules inventory and bounds

The inspected cached rules DB contains **46** `CSC_AdjacencyRules` rows. They are
all positive `SelfBonus`, and all non-Mill spatial rules use ring one. These are
loaded declarations, not 46 simultaneously active effects for every city:
policies, civilization-specific districts and Mill ownership gate activation.

| Exact AdjacencyType | Rows | Current meaning | Count / encoded amount bound per row |
|---|---:|---|---|
| `FROM_RINGS_CAO_DISTRICT` | 37 | 17 customer-return rows plus 20 policy-owned copies | 0–6 matched plots / 0–6 yield |
| `FROM_RINGS_TYPETAG_RESOURCE` | 4 | Bakers/Tailors Base and Specialty Production | 0–6 matched plots / 0–6 Production |
| `FROM_RINGS_TYPETAG_DISTRICT` | 2 | Bakers/Tailors sales Gold | 0–6 matched plots / 0–6 Gold |
| `FROM_RIVER_CROSSING` | 2 | Bakers Water Mill and Tailors river Production | 0–6 edges / `truncate(edges/2)`, hence 0–3 Production |
| `FROM_RINGS_CAO_TERRAIN_SETS` | 1 | Wind Mill, `IsHills`, ring zero | Boolean 0/1 / 0–1 Production |

The six-neighbor bound is per Boolean rule. Wrapped-map deduplication can reduce
the number of distinct plots; it cannot increase it. Multiple tags on one plot
do not multiply one typetag rule's count. Several independent rules can stack,
so **0–6 is not a bound on a Quarter's entire combined adjacency**.

The 26 non-policy IDs are:

```text
CSC_BAKERS_CITY_CENTER_FOOD_FROM_QUARTER
CSC_BAKERS_COMMERCIAL_HUB_FOOD_FROM_QUARTER
CSC_BAKERS_ENTERTAINMENT_COMPLEX_CULTURE_FROM_QUARTER
CSC_BAKERS_HIPPODROME_CULTURE_FROM_QUARTER
CSC_BAKERS_PRODUCTION_FROM_BASE
CSC_BAKERS_PRODUCTION_FROM_SPEC
CSC_BAKERS_STREET_CARNIVAL_CULTURE_FROM_QUARTER
CSC_BAKERS_SUGUBA_FOOD_FROM_QUARTER
CSC_BAKERS_WATER_ENTERTAINMENT_COMPLEX_CULTURE_FROM_QUARTER
CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER
CSC_BAKERS_WATER_STREET_CARNIVAL_CULTURE_FROM_QUARTER
CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS
CSC_CITY_ALL_SALES_GOLD_TO_BAKERS
CSC_CITY_ALL_SALES_GOLD_TO_TAILORS
CSC_TAILORS_ACROPOLIS_CULTURE_FROM_QUARTER
CSC_TAILORS_COMMERCIAL_HUB_CULTURE_FROM_QUARTER
CSC_TAILORS_COTHON_PRODUCTION_FROM_QUARTER
CSC_TAILORS_HARBOR_PRODUCTION_FROM_QUARTER
CSC_TAILORS_HOLY_SITE_CULTURE_FROM_QUARTER
CSC_TAILORS_LAVRA_CULTURE_FROM_QUARTER
CSC_TAILORS_PRODUCTION_FROM_BASE
CSC_TAILORS_PRODUCTION_FROM_RIVER_EDGES
CSC_TAILORS_PRODUCTION_FROM_SPEC
CSC_TAILORS_ROYAL_NAVY_DOCKYARD_PRODUCTION_FROM_QUARTER
CSC_TAILORS_SUGUBA_CULTURE_FROM_QUARTER
CSC_TAILORS_THEATER_CULTURE_FROM_QUARTER
```

The remaining 20 IDs are exactly the appropriate base return ID with
`_<PolicyType>` appended:

| Receiver family in this cache | Quarter return | Policies | Rows |
|---|---|---|---:|
| Commercial Hub, Suguba | Bakers Food | Town Charters, Economic Union | 4 |
| Commercial Hub, Suguba | Tailors Culture | Town Charters, Economic Union | 4 |
| Harbor, Cothon, Royal Navy Dockyard | Tailors Production | Naval Infrastructure, Economic Union | 6 |
| Holy Site, Lavra | Tailors Culture | Scripture | 2 |
| Theater Square, Acropolis | Tailors Culture | Aesthetics, Sports Media | 4 |

Optional resource tags do not raise a ring-one Boolean rule above six. Additional
customer/unique district types can create more rows, but do not raise each row's
bound. A new coefficient such as +2 per neighbor raises that rule's maximum to
12; a wider ring, quantity-valued source or new provider requires a fresh bound.
The old frozen optional-mod fixture has more rows than this cache; its 61-row
inventory must not be substituted for today's 46 loaded rows.

## Future Quarter designs need local predicates, not a universal 1023 promise

The canonical public Quarter pages currently describe adjacent materials and
customer districts throughout the eight designs. Additional site conditions
include Forest/Rainforest presence for Apothecaries; Hills for Stonemasons and
Blacksmiths; fresh water for Carpenters; river presence for Goldsmiths/Brewers;
and qualifying Wonder adjacency for Stonemasons. These are small local counts or
Boolean conditions. Blacksmiths and Brewers include +2 coefficients, so their
bounds cannot be copied blindly from the current +1 rows.

This is **design evidence**, not implementation or a complete future-engine
contract. Population-based sales, Services, trade routes and regional building
effects belong to their own systems, not automatically to `CSC_AdjacencyRules`.
As the [migration plan](../../integrations/mab-independence-plan.md) states,
future Quarters require review when implemented. It is reasonable to keep
specific-Wonder and other tested helpers without granting every rule 1023 yield.

## Encoding options

| Encoding proposal | Wind max 1 | Water max 3 | Ring rule max 6 | Children for today's 46 rows |
|---|---:|---:|---:|---:|
| Current ten-bit binary | 10 | 10 | 10 | 460 |
| Per-rule bounded binary | 1, weight 1 | 2, weights 1/2 | 3, weights 1/2/4 | 134 |
| Unit thresholds | 1 × +1 | 3 × +1 | 6 × +1 | 265 |

For unit thresholds, publish encoded magnitude M and activate one +1 child for
each threshold `M >= 1`, `M >= 2`, ... through the proven maximum. Negative rules
would use -1 children and magnitude thresholds after truncation; current loaded
rows are positive. Water's thresholds 1/2/3 correspond to edge counts 2/4/6.

Unit thresholds have exactly the true maximum capacity. Bounded binary's ring
weights have capacity seven for a true maximum of six; they need a writer bound
and still overstate by one if all conditions disappear in the AI approximation.
**Do not confuse unit thresholds with one-hot amounts.** One-hot Water rows
paying 1,2,3 under mutually exclusive equality gates sum to six if the forecast
ignores those gates; ring one-hot amounts 1–6 sum to 21. This would reintroduce a
smaller version of the same overvaluation hazard.

The narrowest first change is a Mill-specific compiler specialization: Wind's
one +1 child and Water's three +1 threshold children replace 20 weighted children
with four unit children. A bounded-binary Mill specialization would use three.
Neither proposal has been implemented here. Reducing the whole compiler is
optional once an explicit bounded-rule contract exists.

Smaller capacity is damage containment, **not a complete AI fix**. An interpreter
that ignores the relevant property conditions can still count all thresholds
when the true value is zero, iterate inappropriate districts, or credit a benefit
already active elsewhere. Native component evidence is required to choose the
correction; do not claim meaningful economic foresight merely because phantom
amounts are smaller.

## Scope must be decided separately from encoding

Current `A.Eligible` explicitly checks building scope (`CSC_AdjacencyCore.lua:
113–141`). With `COLLECTION_PLAYER_DISTRICTS`, it scans every city belonging to
the player and returns true when any has the named Mill. The writer then evaluates
the corresponding rule on each relevant completed district. The generated SQL
parent also uses player districts (`CSC_AdjacencyModifiers.sql:133–152`). Thus a
remote Mill can activate the authored property bonus elsewhere in that empire.

This is the **current implementation contract**, with earlier regression/runtime
evidence. The public Bakers description says the Water/Wind bonus applies once
the Mill is built in the Quarter. Those descriptions do not establish that the
empire-wide effect is the desired long-term design. The discrepancy should be
clarified explicitly; an encoding change must not silently convert global scope
to local scope or describe the existing behavior as settled intended design.

The eligibility building check is HasBuilding, not an explicit IsPillaged check.
Native building-modifier activation supplies its own gameplay lifecycle. Keep
that distinction when reviewing remote, pillaged or removed Mills.

Resource visibility, same-owner neighbors, policy ownership and direct unique
replacements also need preservation. Converting all rows to native
`District_Adjacencies` is a separate compatibility exercise. The loaded native
adjacency schema has `AdjacentResource`, `AdjacentDistrict`, `AdjacentFeature`,
`AdjacentRiver`, `TilesRequired` and `Self`, but no direct custom TypeTag,
MustOwn, river-edge-count or required-Mill column. Expanding explicit resource
rows may cover some cases; exact ownership, conditional buildings, reciprocal
returns and fractional edge semantics need per-rule proof. A wholesale removal
of the shared evaluator is not justified by the numerical-range finding.

## Evidence and offline verification

Evidence receipt:
`Desktop/Codex/csc-adjacency-range-audit-20261104/range-audit.json`,
67,505 bytes; SHA-256
`a7660e3432b44fd5f0329206f8882297bd37e6a4cfaa83835e464f487eb7832d`.
It retains all 46 rule rows with individual bounds/encoding capacities, source
pins, reference/base commit identities, registered function inventory and the
actual Lua results. Cached rules DB SHA-256:
`819d4288f3b6b7307ad58e6ec4ce213edad7fdd48b73e4be82828363ac432a3c`.
This is a rules snapshot, not a world-state or native forecast observation.

Verification performed:

- All 46 rows match the five bounded current source shapes; no hidden wider-ring,
  negative, multiplier or statistical rule was found in this complete table.
- 24 isolated actual-Lua-5.1 checks cover Wind/river/ring amounts, negative
  fractional truncation and threshold reconstruction, plus remote-building
  player/city/removal scope. These run against the current shared core in a mock
  world and do not touch the game.
- The existing read-only policy suite passed against this cache: 9 mappings,
  20 base/unique policy rows, 200 current policy bit modifiers and 220 gameplay/UI
  cases, plus mixed returns, ownership, events, native totals and Housing.

The proposed smaller compiler, native forecast behavior after such a change,
existing-save property migration and optional-mod release behavior remain
untested. No maximum, encoding, collection scope or gameplay effect was changed.
