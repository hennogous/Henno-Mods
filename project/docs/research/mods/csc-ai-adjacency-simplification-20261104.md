# Both Mills inflate: MAB lineage and a smaller CSC representation

4 November 2026. Follow-up to the measured
[Bakers forecast breakdown](csc-ai-bakers-forecast-components-20261104.md).
This investigation was offline: source, loaded rules, existing native captures,
fresh read-only native analysis and executed Lua fixtures. No game, installation,
production compiler, tuning or CE API was changed.

## The user's explanation is substantially correct

The ten-bit adjacency architecture is inherited from MAB's approach. CSC now
independently implements that architecture in its own bundled code; it does not
depend on the external MAB mod. The local read-only reference and its original
upstream base both contain the1,2,4,…,512 ladder and1023 limit. This was not a
new requirement introduced by CSC's Wind Mill. [AI-C054]

Binary encoding itself is not inherently wrong. It represents any integer0–1023
with ten conditional amounts rather than1023 separate unit modifiers. The
problem is the combination of **unneeded large amounts** and the hypothetical
AI evaluator **omitting their gameplay property gates**. A correctly gated
forecast would not credit every amount. Gameplay still pays only active bits;
the million-scale native utility is discounted income in fixed point, not a
million actual Production or evidence of a gameplay yield exploit by itself.

For example, a real +1 Wind bonus enables the1 bit and disables2..512. The AI
forecast nevertheless values1+2+4+…+512. This is a false forecast of the encoding
capacity. Removing those unreachable amounts directly addresses its magnitude.

## Water is affected too; two different mechanisms explain the apparent difference

Both Mills own the same ten weighted adjacency children. Wind uses its own hill
tile; Water counts river edges. Neither geometry check is what produced the
different large native forecasts. [AI-C055]

| Captured forecast | Ready input | Horizon | Discount input | Encoded-bit forecast, Q8 |
| --- | ---: | ---: | ---: | ---: |
| Majapahit Wind |24|50|4.0|1,589,504|
| Water, both cities |25|50|4.0|1,408,256|
| Delhi Wind |26|50|4.0|1,356,544|

The native timed-income helper discounts the same erroneous stream using the
different readiness inputs and fixed-point rounding. An offline reconstruction
matches all480 captured base-yield callbacks and40 unique amount/time cases.
Readiness combines native delays; individual research/building ETA shares were
not separately observed. The prerequisite-depth heuristic acts earlier and does
not multiply this later bit contribution.

Separately, the district aggregation skips an excluded building if its exclusion
is present **or merely has a lower definition index**. Wind139 precedes Water140;
Water also excludes No River Access138. Thus **the Wind forecast, not the Water
forecast, entered both measured district sums**. That does not mean Water is
safe, or that the AI can never build it. Changing insertion order would change
the canonical representative without repairing either forecast.

## CSC's real requirements are small

The complete currently loaded bundled-adjacency table has46 rules, using only
five of the55 source types declared by CSC. All currently use SelfBonus.

| Rules | Rows | Maximum actual encoded yield per rule |
| --- | ---: | ---: |
| Neighboring resource/district matches, including policy copies |43|6|
| Water Mill and Tailors river edges |2|3|
| Wind Mill's own hills tile |1|1|

Water uses `floor(edge count/2)`, so six edges give3. Wind is one Boolean own-tile
condition, not a count of adjacent hills. Multiple independent rules can stack;
six is not the limit for an entire Quarter's combined adjacency. Nor does this
inventory bound population-based sales, Services or exports in other CSC systems.

The MAB reference supports141 dispatched source functions, including population,
housing, yields, turns, property values, units, damage and wider rings. Those can
produce quantities much larger than a local neighbor count. That establishes a
broader source capability, not the author's particular reason for choosing ten
bits or a measured AI failure for every MAB feature. The
[range/provenance audit](csc-ai-adjacency-range-and-provenance-20261104.md) retains
the original source identities and complete current rule inventory.

## Simpler representations

| Representation | Wind | Water | All46 current rules, child modifiers | Forecast if all conditions are omitted |
| --- | --- | --- | ---: | --- |
| Current ten weighted bits |1..512|1..512|460|Capacity1023 per rule |
| Bounded binary |One amount1|Amounts1 and2|134|Maximum1/3 for Mills; ring capacity7 for a real maximum6 |
| Unit steps |One +1 switch|Three +1 switches|265|At most the actual rule maximum, but possibly credited at the wrong site |

For unit steps, Lua writes Boolean flags such as “amount at least1”, “at least2”
and “at least3”. Each flag enables a +1 modifier. This uses the existing proven
0/1 property check; it does not require assuming that a new numeric-range
requirement works. There are no +128/+256/+512 amounts to leak into forecasting.
The two Mills need **four child modifiers instead of20**; bounded binary needs
three. These counts exclude attach wrappers and requirement rows.

A one-hot design with mutually exclusive payments1,2,3 is less attractive here:
if the AI ignores their gates it sums to6. Amounts1..6 sum to21. Unit steps keep
the unconditional ceiling at3 or6 respectively.

The actual Lua5.1 `CSC_Adjacency.Write` was exercised across all317 possible
source-count cases in these current rules. Bounded binary and unit-step
reconstructions exactly match today's numeric payouts. This is **numerical
representation equality**, not a tested compiler replacement or proof of live
activation, stacking, save migration or corrected AI choices. The explicit
audit tool is [review_bounded_encoding.py](../../../tools/adjacencies/review_bounded_encoding.py).

## Smaller is safer, but not automatically accurate

With omitted conditions, even one +1 Wind modifier can still be forecast on flat
land. Unit steps bound that error; they do not teach the native evaluator the
exact geometry. Moving the same unsupported property gate from Owner to Subject
does not repair it: unsupported requirements are omitted there too.

Vanilla adjacency is also not a direct replacement for these authored rules.
Read-only native analysis shows that `Self` adds a flat term rather than gating
on the own tile's terrain; AdjacentRiver adds once for river presence rather
than counting edges. Ordinary adjacency rows have no required-building column.
The native terrain-adjacency building effect has a supported but coarse forecast,
not an exact future-site simulation. The
[native options review](csc-ai-mill-adjacency-native-options-20261104.md) preserves
the exact inspected consumers and context limits.

A further option is to keep the exact Lua matcher but publish the guarded bonus
on the district, without a Mill-owned player-district attach wrapper. In the
inspected ordinary candidate path, that direct OWNER effect lacks actual
district/plot context and forecasts zero. It could avoid this phantom building
forecast without a new native API, leaving planned geometry to CSC's explicit
site policy. That is **deliberate forecast omission**, not automatic foresight;
it needs gameplay/stacking and other-context qualification before adoption.

## Recommendation

Start with a narrow Mill-specific representation: **one Wind +1 switch and three
Water +1 switches**, retaining the exact matcher and placement presentation.
Do not rewrite the whole adjacency subsystem or add a compensating million-scale
AI penalty as the first response. Qualify the reduced native forecast and the
real bonus first; expand bounded generation to other rules if useful afterward.

If small remaining geometry errors matter to choices, compare district-owned
publication plus explicit forecasting with a precisely scoped CE consumer.
The current CE batch API does not contain a building/modifier-filter hook, so
that native extension would be additional work rather than an existing fix.

Preserve material visibility/ownership, policy doubling, unique district support,
river truncation, save migration and existing lifecycle behavior. Unknown/new
rule bounds must be explicit or rejected for review, never silently clipped.
Future +2 coefficients or wider/quantity-valued sources need different bounds.

One scope detail needs resolution before any ownership rewrite: current Mill
eligibility can activate from a Mill elsewhere in the empire, while the public
design describes the Mill in the Quarter. This is a pre-existing implementation/
design discrepancy, separate from encoding. No local/global scope change was
made or silently included in the numerical comparison.

## Evidence

- `Desktop/Codex/csc-adjacency-simplification-20261104/bounded-review-01/review.json`:
  317 actual shared-Lua cases,46 rules and460/134/265 child counts.
- Rules DB SHA-256:
  `819d4288f3b6b7307ad58e6ec4ce213edad7fdd48b73e4be82828363ac432a3c`.
- Shared core SHA-256:
  `813acb3de6750922ada38f1baa898833f2ca5e04d34014c62e6926c5b93e9f2b`.
- Source/range receipt:
  `Desktop/Codex/csc-adjacency-range-audit-20261104/range-audit.json`,
  SHA-256`a7660e3432b44fd5f0329206f8882297bd37e6a4cfaa83835e464f487eb7832d`.
- `Desktop/Codex/csc-mill-native-options-20261104/`: fresh Ghidra receipts and
 480-callback exact timing reconstruction. Original XP2 identity matches the
 prior component report; no program annotations or runtime were changed.

The range audit also executed24 focused actual-Lua cases and the existing220-case
policy suite. These are offline checks. A smaller production compiler, changed
native decisions and in-game/save behavior after replacement remain untested.
