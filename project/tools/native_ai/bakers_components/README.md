# Bakers forecast component observer

Read-only, finite diagnostic for the original weak-site world's Delhi and
Majapahit. Root controls all native execution through the shared controller.
The observer starts no process, issues no order and installs no scoring policy.

Completed result: [weak Bakers forecast attribution](../../../docs/research/mods/csc-ai-bakers-forecast-components-20261104.md).
The one-load80→81 observation closed normally, with504 complete pairs and exact
building-sum arithmetic. No further runtime work follows automatically.

`observer.js` runs directly in Frida; it is also a CommonJS module for isolated
Node fixtures. It does not contain template placeholders. Retain the Frida
script and session until the exact native process exits normally; do not unload
the script or detach while patched code can still run.

## Host contract

1. Hash the exact loaded original XP2 DLL on disk, prove its module path and
   preserve the loaded-definition snapshot. The script additionally verifies
   PE32+, timestamp1719431003, image size12976128 and four32-byte fingerprints.
2. `script.exports_sync.init(spec, config)` installs disabled callbacks once.
3. `status()` confirms `installed`, four hooks, no `initError` and no faults.
4. `start()` opens one immutable collection window. Advance only the declared
   original80 save through81. The implemented driver permits no additional
   interval, second load or new world for this observer.
5. At an inactive boundary, `freeze()` refuses new root calls and drains accepted
   callbacks for up to five seconds. It returns the full snapshot. A drain
   failure is a retained-owner condition; it is not permission to detach.
6. Preserve snapshots/world facts, normal-exit/restoration receipts and logs.

`spec` has `path`, `sha256`, `image_size`, `timestamp` and `functions`, exactly
the four `{name,rva,bytes}` records exported as `BAKERS_POINTS` in Node. Required
SHA256 is `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
No CE or independent CSC proxy may be loaded in this diagnostic.

The world reader supplies `observerConfig`:

```json
{
  "profile": "bakers-components-v1",
  "mappingVerified": true,
  "targets": [{"player":5,"city":65536},{"player":3,"city":65536}],
  "buildings": [{"type":"BUILDING_CSC_BAKERS_RIVER_ACCESS","index":0}],
  "buildingCount": 1,
  "districtCount": 1,
  "districtIndex": 0,
  "mapWidth": 74,
  "mapHeight": 46,
  "maxPairs": 4096,
  "maxCallbacks": 200000,
  "maxThreads": 8,
  "maxDepth": 16,
  "maxRows": 37
}
```

The illustrated building array is abbreviated: actual config must contain all
six loaded Bakers definition types, with distinct indices in the verified
building collection. Counts and indices above are placeholders; never use this
example as a live mapping.

## What is measured

- `BuildingValue`: exact native output and readiness/horizon/discount input for
  the six actual Bakers building definitions in the two declared cities.
- `ModifierValue`: its nested total for the same building/city/native thread.
- `BaseYield`: each nested Amount/YieldType, district/plot context and signed
  accumulator difference. A change is a hypothetical-forecast observation,
  not a realised yield.
- `CalculateDistrictValues`: six values from the center-row raw building
  vector and mutable building vector, plus all bounded Bakers district rows
  before and after aggregation. Distinct pointer identities remain explicit.

Each accepted record has `id`, `thread`, `entrySequence`, `parentId`, `entry` and
`leave`. Component records correlate to their parent building through
`entry.buildingCallId`. Zero and invalid native sentinel values are preserved.
Unrelated nested buildings create a scope barrier to prevent false attribution.

Snapshots expose `pendingPairs`, `pendingFrames`, `stats.errors`, accepted and
completed pair counts, per-boundary counts, bounded faults and `stopReason`.
Budget saturation or an incomplete record invalidates a claim of complete
component accounting. No source claim requires complete capture of all cities.

## Offline verification

```text
node project/tools/native_ai/bakers_components/test_observer.js
```

`driver.py --help` lists the explicit native, save, installed-package, dependency,
specification and fresh-output inputs. `analyze.py --trace <trace-frozen.json>
--world <source-world.json> --output <new-directory>` performs the offline audit.
Run `python -B -m unittest discover -s project/tools/native_ai/bakers_components
-p 'test_*.py'` for15 source/world/analyzer checks; actual-Lua fixtures need Lupa.

The mock-memory checks exercise identity, nested attribution, unrelated-thread
and recursive-building isolation, exact signed/sentinel values, output pointer
identity, two distinct building vectors, row/vector/coordinate bounds, thread,
depth, pair/callback budgets, read-only memory-range checks and callback drain.
They do not load game code or establish live ABI correctness by themselves.

The [native review](../../../docs/research/mods/csc-ai-bakers-native-component-review-20261104.md)
records the static ABI and omitted-owner-gate path. A recalculated80→81 case
does not reconstruct the unrecorded historical per-building totals at86/89.
