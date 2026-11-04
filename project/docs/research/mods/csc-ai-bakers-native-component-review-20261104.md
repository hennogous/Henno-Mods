# Bakers building forecasts: native component review

4 November 2026. Offline follow-up to the weak-site penalty cases. This record
separates a newly traced candidate source of inflated value from the exact
historical component totals, which were not captured.

## Main result

The generated Mill adjacency wrappers have a reachable hypothetical-valuation
path that can credit every binary magnitude instead of the actual geographic
bonus. The native forecast compiler does not compile their owner property gate;
the outer wrapper supplies the actual district context needed by the supported
base-yield effect. This is a stronger and more specific finding than the earlier
general warning about unsupported requirements.

The ten magnitudes are 1, 2, 4, 8, 16, 32, 64, 128, 256 and 512. Their sum is
1023, whereas a real Mill's property writer enables only the bits encoding its
matched bonus. The static path therefore supports a concrete phantom-income
hypothesis. It does **not** by itself establish the numerical contribution in
Delhi or Majapahit, or prove that the entire later uplift is erroneous.

This review did not launch Civ, load a save, attach Frida, change scores, modify
the CE fork, or edit the Ghidra analysis database.

## Target and evidence

Existing Ghidra program independently rechecked with `get_program_info`:
Windows XP2 `GameCore_XP2_FinalRelease.dll`, image base `0x180000000`, SHA-256
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
Recovered names below are analyst mappings, not imported signatures.

Fresh raw Ghidra receipts are retained at
`Desktop/Codex/csc-bakers-component-review-20261104/native-static-receipts.json`.
They preserve program identity, the base-yield registry/vtable chain, full
initializer/analyzer decompilation, player-district bytes and AttachModifier
disassembly. They are raw Ghidra receipts, not REA Evidence IDs.

Reused exports and their existing evidence are under
`Desktop/Codex/csc-future-economy-forecast-20261103/native/` and
`Desktop/Codex/csc-district-decisions-20261104/native/`.
The earlier [modifier forecast investigation](csc-future-economy-forecast-20261103.md)
retains REA dossier IDs for compiler `48eb10`, analyzer `48e9e0` and sum
`529ed0`. The [timing report](civ6-district-cache-timing-and-purchases-20261104.md)
preserves the original score differences.

## Traced path from Mill to hypothetical Production

1. `CSC_AdjacencyModifiers.sql` creates each Mill's building-owned wrapper as
   `COLLECTION_PLAYER_DISTRICTS / EFFECT_ATTACH_MODIFIER`. The generated wrapper
   has neither an owner nor a subject requirement. The nested SelfBonus uses
   `COLLECTION_OWNER / EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE`; its plot-property
   requirement is on **OwnerRequirementSetId**, with no subject requirement.
2. The native compiler at RVA `48eb10` compiles the subject requirement via
   definition virtual `+0x60`. It does not compile owner virtual `+0x58` in this
   body. The prior independent interface audit proves those field identities.
3. The player-district iterator is registered through
   `b65bc0 -> 9fee70 -> {4635c0,4635f0,4634c0}`. It clears context `+0x78`, then
   yields actual player districts into that field. It is not restricted to the
   candidate Bakers site by these generated wrappers.
4. AttachModifier Analyze at `481bd0` copies the incoming analysis with
   constructor `0d8170`. Fresh instructions at `481bf4..481bf9` leave the incoming
   context in RDX while passing the local destination in RCX. This resolves the
   decompiler's misleading apparent one-argument call. The copy constructor
   explicitly copies the district pointer at `+0x78`.
5. The nested OWNER iterator does not erase that district pointer. Its known
   body only supplies a once-only iteration flag. The child therefore reaches
   the district branch of the base-yield analyzer.
6. Constructor `4891b0` maps `EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE` through
   `b65e10 -> a00010 -> {481730,4818c0,9b1040}`. Initializer `481730` reads
   Amount and YieldType into data `+8/+0xc`. Analyze `4818c0` normalizes the
   amount using the yield's default value and calls discounted timed income with
   the existing analysis readiness/horizon when `analysis+0x78` is non-null.
   It does not test the property's bit or actual river/hill adjacency itself.
7. ModifierValue `529ed0` evaluates the compiled wrappers separately and sums
   their results. With a district context, each bit's timed result is rounded
   to whole utility by `>>8` in the effect before being restored to Q8 in the
   outer sum. Do not substitute one exact `1023 * discount` formula for the
   actual per-bit rounding.

There is an important boundary: the direct ordinary BuildingValue context has
city `+0x70` and player `+0x80`, but initially no actual district `+0x78` or plot
`+0x88`. A direct OWNER/base-yield child without the outer player-district
wrapper would contribute zero through this handler in that context. Ignored
owner gates alone were insufficient to prove this path; the outer traversal
and context copy are the missing links.

Do not multiply the hypothesized 1023 by the number of player districts.
AnalyzeModifier resets its local result, and AttachModifier copies the child
result back by assignment. The inspected outer traversal can overwrite that
result on successive districts rather than add an independent 1023 for each.
A runtime record is needed for an exact total and iteration behavior.

## How buildings reach the district score

`CalculateDistrictValues`, RVA `3dfee0`, obtains the center-row analysis object
from `*(CityBuild+0x4c8)` and reads its raw building vector at `row+0x28`.
For each definition in order, its ordinary district contribution requires:

- passage through the mutually-exclusive definition checks;
- positive raw building value;
- a prerequisite district and `MustPurchase` clear;
- an available player district mapping; and
- absence of that district in the city, or all of it pillaged.

The pass sums those admitted raw values into one city/type contribution, then
adds that contribution to positive district/site entries. The ordinary row-zero
special case first zeros a positive center entry. The same routine separately
propagates positive dependent-building values into its mutable building vector;
that is not the same source as the raw vector used for the district sum.

The flag identity is directly grounded in the retained current loader
`7b5eb0`: query column `0x1d` is shifted into definition `+0x159` bit `0x04`.
The current query at `a49920` names zero-based column29 **MustPurchase**.
Thus the hidden River Access/No River Access buildings are excluded from this
district sum directly. Their role in a prerequisite-depth chain is separate.
The independent dependent-propagation guard at bit `0x10` corresponds to query
column42 **RequiresPlacement**, rather than MustPurchase.

These boundaries make the first measurement cheap: capture the six Bakers
definition entries in the raw vector immediately before this routine and
the affected district entries before/after it. Preserve mutually-exclusive
ordering, definition flags and actual presence/pillage facts. Do not assume
both Mills count just because both have a positive forecast.

## Original weak-site measurements remain incomplete

| Case | After early penalty | Final cache | Later net difference |
| --- | ---: | ---: | ---: |
| Delhi Bakers plot1429 | 1,207 | 1,358,358 | 1,357,151 |
| Majapahit Bakers plot1829 | 32,200 | 1,623,830 | 1,591,630 |

The old traces retain NetValue, cache, best-site and present-value boundaries,
not the per-building vector or nested modifier deltas. The difference cannot
be retrospectively divided among Mill, Bakery, Café, preference and other
processing from those records. Existing AI_CityBuild.csv selected requests
are also not the missing complete hypothetical building vector.

The normal Bakery/Café amenities, appropriate material/customer transactions,
maintenance and construction/research delay remain real possible components.
The prerequisite-depth multiplier acts on an earlier subtotal, before the
later modifier sum. It must not be claimed to multiply these adjacency-bit
wrappers or every later amenity/modifier contribution.

## Small decisive observation

Root owns any runtime test and its shared controller. No new scoring policy is
required to measure the following observer-only chain:

- At `52b900`, bound building IDs to the actual loaded Bakers family and record
  out-pointer return, discount input, readiness/horizon, city/player and input
  coordinates. This is nine ordinary Win64 arguments: out, building, discount,
  ready, horizon, player, city, coordinates, map changes.
- Within the same native thread's scoped building call, record `529ed0` sum
  and `4818c0` effects. For each child, retain Amount/YieldType, candidate
  building, city, district-context identity, timing and accumulator before/after.
- At `3dfee0`, retain the admitted raw building inputs and district cache
  differences. Compare the arithmetic exactly, not just directionally.
- Obtain the actual CSC adjacency/property bits for the relevant world/site
  separately. A phantom 512 contribution while that property is zero would be
  stronger evidence than an unexpectedly large total alone.

Finite call/record budgets, exact binary and loaded-definition identity,
thread-scoped nesting and explicit incomplete-capture flags are necessary.
No engine API or Lua call belongs in an off-turn worker callback.

The result should distinguish: real native benefits to retain, approximate
benefits requiring correction, implementation-artifact forecasts to remove,
and still-unmeasured terms. A separate controlled contrast can then determine
whether a correction changes the chosen site; this offline path trace does
not establish that choice or an improvement in empire outcomes.
