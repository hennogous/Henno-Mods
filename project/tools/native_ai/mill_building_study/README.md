# Mill and building forecast observer

Finite, read-only research observer derived from the tested
[`bakers_components` reader](../bakers_components/README.md). It starts no process,
calls no game or Lua function, publishes no policy, and never changes a native
value or return register. Root owns all game execution through the shared
controller. Installing Frida interceptors still patches executable entry points;
retain the script/session until the exact native process exits normally.

**CSC-only, no CE or other CSC native carrier.** The observer and CE both target
CalculateDistrictValues. Their hooks must not overlap. This research does not
alter the separately qualified CE API or its tuning policy.

## Target and configuration

Original Windows x64 XP2 SHA-256:
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
The host must prove the actual loaded path and on-disk hash. `init` additionally
checks PE32+, timestamp1719431003, image size12976128 and all six exact32-byte
entry prefixes. Other builds are rejected.

Exports for the host/spec builder: `STUDY_SHA`, `STUDY_POINTS`, `STUDY_TYPES` and
`STUDY_LIMITS`. The exact loaded world reader supplies this immutable config:

```text
profile: "mill-building-study-v1"
mappingVerified: true
targets: [{player:1, city:<loaded ID>}, {player:2, city:<loaded ID>}]
buildings: [{type:<exact CSC type>, index:<loaded native index>}, ...19]
buildingCount: <native building index limit>
districtCount: <native district index limit>
districtIndices: [<Bakers index>, <Tailors index>]
mapWidth, mapHeight: <actual loaded dimensions>
maxPairs: 16384
maxCallbacks: 300000
maxThreads: 8
maxDepth: 16
maxRows: 37
maxModifierName: 256
```

The19 types are the seven ordinary Bakers/Tailors buildings and twelve hidden
flags/Service buildings listed in `STUDY_TYPES`. Optional LGD's twentieth type is
outside this fixture contract. Counts must match native dense-vector index
limits, not merely the number of selected study definitions. A Boolean mapping
attestation does not replace the host's loaded-catalog/source validation.

RPCs: `init(spec, config)`, `start()`, `status()`, `snapshot()` and `freeze()`.
Initialize once with callbacks disabled, then start exactly one immutable
collection window. There is no restart, reconfiguration or detach RPC. For
controlled phases, the host preserves snapshots and external phase metadata with
record-ID boundaries. Freeze refuses new root calls and drains admitted frames
for up to5 seconds; failure requires retaining the attached owner. Budget/fault
or incomplete records preclude complete-accounting claims.

## Native boundaries

Recovered signatures are for this exact target, verified by current static
analysis. They are not general CE ABIs.

| Boundary | RVA | Win64 arguments / result |
| --- | --- | --- |
| BuildingValue | `52b900` | out, building, discount*, ready, horizon, player, city, coordinates*, changes; returns original out |
| ModifierValue | `529ed0` | out, analysis*, compiled-vector*, changes; returns original out |
| AnalyzeModifier | `48e9e0` | analysis*, compiled-descriptor*, changes; Boolean in AL |
| District base yield Analyze | `4818c0` | this, analysis*, effect-data*; accumulator observed |
| AmenityValue | `5272a0` | out, player, recipientCity, count, discount*, ready, horizon; returns original out |
| CalculateDistrictValues | `3dfee0` | CityBuild this; void |

Analysis fields retained: candidate building `+4`, city ID `+14`, yield index
`+64`, city/district/player/plot pointers `+70/+78/+80/+88`, ready/horizon/discount
`+b4/+b8/+bc`, signed accumulator `+c0`, native recursion depth `+c8` (hex offsets).
Collection iterators can change subject context. Such a change is recorded,
including its relationship to the root city/candidate, rather than mistaken for
an unrelated root forecast. Nested unrelated BuildingValue calls remain scope
barriers.

Compiler `48eb10` proves the64-byte compiled descriptor layout: effect object
`+0`, iterator object `+8`, subject-requirement hash `+10`, MSVC string `+18`,
effect data pointer `+38`. The string's size/capacity are `+28/+30`; capacity<16
selects inline storage. The reader admits at most256 printable ASCII bytes and
capacity4096, validates the complete span before reading it, and never scans for
a NUL terminator. Effect Analyze and iterator Next addresses come from their
vtable `+8`; addresses are observations, never invoked by the observer.

Every component retains its direct `parentId` and separate `buildingCallId`.
AnalyzeModifier's **after** accumulator is its result; its delta alone is not
the contribution, because the engine resets/assigns this field. AL0 and zero
results remain explicit. ModifierValue calls AnalyzeModifier once per64-byte
compiled entry; its count/base and direct children can reconcile the executed
inventory. Nested Attach callbacks must not all be added: a parent can overwrite
its accumulator with the last child result.

Both raw center-row and mutable building vectors remain separate. The actual
district matrix at CityBuild `+518` is also recorded separately from row `+20`
bindings, with capacity/length at `+520/+528`. CalculateDistrictValues calls the
FAutoVariable edit helper `72a920` on `+508`; that helper returns `+10`. It tracks
writes rather than copying the vector. Alias relationships remain explicit;
the observer never substitutes one pointer's values for another's.

## Coverage and interpretation

| Question | Current measurement | Limit |
| --- | --- | --- |
| Smaller/local Mill encoding | Full building, modifier-ID tree and base-yield Amount/context | Compare with actual loaded rules and gameplay properties; hypothetical income is not paid income |
| Ordinary transactions, material reciprocity, Services, exports and GPP | Each reached compiled modifier's name, handler/iterator, acceptance and accumulator | A source root absent from this building vector is unobserved here, not proved unsupported |
| Bakery/Café amenities | Separate discounted AmenityValue per actual recipient | Regional native BuildingValue sums then caps this subtotal at `0x3200` Q8; do not sum without the enclosing branch |
| Pop/export rules owned by City Center | May affect source facts or other forecasts | A CityCenter-owned consumer outside the scoped family BuildingValue is not captured |
| Specialists | Full building total and residual remain available | Building_CitizenYieldChanges is definition `+178`; the inspected BuildingValue/GetYieldChange bodies do not directly read it. No universal unsupported claim or separate specialist attribution follows |
| Prerequisite flags, depth, maintenance and delay | Entry timing/discount, raw flag forecasts and final totals | The first-prerequisite-depth heuristic affects an earlier subtotal; remaining non-modifier/non-amenity residual is unattributed |

Amenity recipients may differ from the root city. Their identity and whether
they share its owner remain explicit. This does not broaden root admission to
human0 or other buildings. Native regional coverage in BuildingValue uses city
centers; real CSC district/building geography must be compared separately.

The scalar effect normalization uses loaded yield defaults when an analyzer
leaves a yield index, and returns Q8 at ModifierValue. Keep the world reader's
complete yield-index/type/defaultValue catalogue for that offline conversion.
The point count of BuildingValue's unrelated `533190` call is a unit-forecast
route, not a specialist valuation.

No result proves a district winner, construction request, completion or economic
benefit without the corresponding later evidence. Fresh controlled fixtures
answer component questions; they are not historical game replays.

## Offline checks

```text
node project/tools/native_ai/mill_building_study/test_observer.js
```

The38 checks exercise six signatures, scope and barriers,19-family validation,
name/string and vector bounds, direct modifier ancestry, zero/invalid results,
regional recipients, raw/mutable separation, read-only adapters and finite drain.
They do not execute the new native hooks. The earlier four-hook runtime result
does not automatically qualify the two added boundaries.
