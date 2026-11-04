# Mill forecast differences and simpler representation options

4 November 2026. Offline follow-up to the measured
[Bakers component observation](csc-ai-bakers-forecast-components-20261104.md).
No game, attachment, scoring change or installed-content change occurred.

## Both Mills are affected by the same encoding leak

Each Mill owns ten generated player-district attach wrappers, whose OWNER
children supply base Production amounts1,2,4,…,512. The hypothetical compiler
omits their owner property gates. The observed ordinary building forecast
therefore consumes all ten amounts for **both** Mills. The real hill/river
matching is not the reason one forecast differs from another.

| Forecast | Ready time | Horizon | Discount input | Phantom bit contribution, Q8 |
| --- | ---: | ---: | ---: | ---: |
| Majapahit Wind Mill |24|50|4.0|1,589,504 |
| Both Water Mills |25|50|4.0|1,408,256 |
| Delhi Wind Mill |26|50|4.0|1,356,544 |

These are observed readiness inputs, not independently itemised research,
district-construction and building-construction delays. Static evaluator code
shows those sources of delay, but the earlier probe did not hook every ETA.
The hidden River Access prerequisite can affect Water's readiness/early depth
heuristic; this observation does not assign its exact share of the25 turns.

The helper at RVA `528660` computes a timed stream as income-through-horizon
minus income-through-readiness. Its `528310` implementation uses fixed-point
arithmetic and a truncated polynomial approximation with several intermediate
integer divisions. Readiness is therefore not a perfectly smooth exponential
price. A bounded offline reproduction of the observed branch matches **all480
captured BaseYield calls**, including all40 unique amount/readiness cases.

For the512 child, the respective whole-utility outputs are3,109,2,755 and2,655.
The outer modifier sum restores Q8. Per-bit rounding explains why adding1023
first and discounting once is not an exact substitute.

The prerequisite-depth multiplier runs before the modifier sum. It does not
multiply these dominant bit contributions. Nor does the number of existing
districts multiply the result: the nested attach handler assigns the last
child result for each wrapper rather than summing all district callbacks.

## Water's forecast is calculated, but not admitted into these district sums

The district aggregation uses a mutually-exclusive canonicalisation gate:
an exclusion that is present **or has a lower definition index** skips the
current building's district contribution. In this loaded family, Wind139 is
lower than Water140. Water also excludes the lower No River Access138 flag.
Thus Water is skipped in this ordinary pass even if neither exclusion is
actually built. Wind is the admitted Mill in both measured cities.

This establishes the inspected code and these loaded definitions, not a universal
rule that the AI never builds Water. Building requests, actual legality and
district aggregation have separate consumers. Changing SQL insertion order
would change canonicalisation, not resolve the phantom forecast.

## The actual geometry is much smaller

Current generated rules specify:

- Wind:1 Production if the Quarter's **own tile is hills**. MinRings0/Rings0
  is not a count of adjacent hill tiles.
- Water: floor(0.5 × river-crossing-edge count), so the maximum is3 Production.

Ten generic bits are unnecessary for these two particular ranges. Reducing
Wind's owned encoding to bit1 and Water's to bits1/2 would reduce their phantom
capacity from1023 to1/3. It would not make the AI apply the gates it currently
omits. This is magnitude containment, not accurate foresight.

An alternative is one Boolean +1 flag for Wind and three Boolean +1 threshold
flags for Water. Lua would write `amount>=1`, `amount>=2`, `amount>=3` as0/1
properties, each using the already-established PropertyMinimum1 requirement.
That avoids assuming arbitrary numeric property thresholds work in gameplay.
The same omitted-gate AI still sees the full1/3 capacity. Unit flags are simpler
to explain, but do not solve the forecast contract by themselves.

The recorded bit components allow an exact limited arithmetic projection:
Wind bit1 is1,536 Q8 in Majapahit and1,280 in Delhi; Water bits1+2 total3,840
Q8 in both cities. Those numbers describe the retained **bit contribution**
under the same captured inputs. They are not a tested new building output,
district total, chosen site or gameplay outcome. Other terms and later gates
must be evaluated separately.

Moving the existing property requirement from OwnerRequirementSetId to
SubjectRequirementSetId does not repair this interpreter. The compiler would
then encounter `REQUIREMENT_PLOT_PROPERTY_MATCHES`, which the inspected AI
registry does not support; unrecognized requirement entries are omitted.
An empty ALL list succeeds. The distinction between gameplay activation and
hypothetical requirements remains essential.

## Supported native requirements still need the right context

The native AI registry does support `REQUIREMENT_PLOT_IS_HILLS`. Its handler
is `b66508 -> a03c70 -> 492db0`. Exact leaf bytes show it only tests the supplied
analysis plot at `+0x88`; with a null plot it returns false. It does not obtain
the plot from an actual district or city as a fallback. The current Mill attach
path has an actual district at `+0x78` but no plot at `+0x88`.

The supported river-adjacent requirement at `490dc0` differs: it checks an
explicit plot, then falls back to an actual district's plot, then the city plot.
It is a Boolean river test, not a river-edge counter. Therefore neither merely
substituting a familiar vanilla requirement nor relocating a gate establishes
an exact future-site forecast. The supplied context is part of the contract.

## Vanilla adjacency is not a drop-in translation

The ordinary native DistrictValue consumer does read native district adjacency
rows, through `260510 -> 25f570 -> 25f890`. However:

- `Adjacency_YieldChanges.Self` is **not** an own-tile terrain filter. Loader
  `7b2700` maps SQL column18 Self to definition `+0xc0` bit0x40. Consumer25f890
  adds YieldChange unconditionally for that bit, then independently checks six
  neighbouring plots for AdjacentTerrain and other matches. Self plus a hill
  terrain row gives a flat addition plus ordinary neighbour matches.
- AdjacentRiver checks whether the plot's river field is positive and adds
  YieldChange once. It does not multiply by the number of crossing edges.
  TilesRequired divides the completed accumulated value; it cannot recover
  a count that the Boolean river branch never computed.
- The ordinary row has technology/civic gates, but no per-building prerequisite
  column that directly makes the rule conditional on the selected Mill.

Native dynamic `EFFECT_TERRAIN_ADJACENCY` is registered and used by shipped
content. Its AI initializer `468cc0` reads Amount, DistrictType, TerrainType
and YieldType; it does not read a Self argument. Its AI analyzer `469010`
counts matching terrain at an existing district's own tile plus its six
neighbours. When the target district is absent, it instead counts a radius-three
neighbourhood around the city center. That is an approximate city forecast,
not exact scoring of the proposed Quarter tile. A supported effect is not
automatically a faithful implementation of Wind's own-hill rule.

## A localized alternative worth qualifying

One promising design is to retain Lua's exact eligibility/geometry calculation
and attach the property-gated SelfBonus directly to the district, instead of
giving each Mill a player-wide attach wrapper. This would remove the ordinary
Mill building forecast's encoding roots without a new native callback.

The inspected ordinary DistrictValue path creates a fresh GameModifierAnalysis
with candidate district index, city, player and timing. Its constructor48c8c0
zeros actual district `+0x78` and plot `+0x88`, and that path does not fill them
before ModifierValue. OWNER does not fill them either. BaseYield4818c0 adds
nothing when both are null. Thus a direct district-owned OWNER SelfBonus has
zero contribution through this specific hypothetical path, even if its property
gate is omitted. This is a bounded static conclusion, not a new runtime trial.

That design intentionally leaves geometry foresight to the explicit CSC policy
(which already plans the appropriate Mill), rather than exposing encoding
capacity as native income. It is not automatic native understanding. Before
implementation, preserve the existing eligibility contract, actual ownership,
multiple-Mill stacking and other-city effects deliberately; changing from one
attachment per building instance to one per district can change gameplay.
The ordinary direct-path conclusion does not cover every placement-specific
or nested forecast context.

A precise CE forecast correction is another option: identify these encoding
contributions and replace them with a credible, timed CSC estimate. The current
CE score-batch API does not expose a building/modifier-filter contract. Such a
consumer would need its own typed scope, synchronization and lifecycle review.
It is a potential later integration, not a capability already shipped by CE.

## Evidence

Pinned original Windows XP2 SHA-256:
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
Existing Ghidra target identity was rechecked before the fresh read-only calls.
No analysis-program annotations or functions were changed and no REA binary
session was opened. Native receipts and the bounded timing reconstruction are
retained under `Desktop/Codex/csc-mill-native-options-20261104/`.

Runtime inputs are the closed run01 `trace-frozen.json` and `source-world.json`
under `Desktop/Codex/csc-bakers-components-20261104/`, with the maintained
`analysis-02/` ledger. The earlier compiler/requirement findings and exact
pointer-chain evidence remain in the
[future economy report](csc-future-economy-forecast-20261103.md) and
[native component review](csc-ai-bakers-native-component-review-20261104.md).
