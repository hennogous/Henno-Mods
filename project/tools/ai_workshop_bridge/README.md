# Workshop delivery prototypes

**Preferred release:** CSC Lua/SQL with a Community Extension dependency. Further
AI tuning is held until its native consumer is qualified. No installed CSC
content is changed by these tools on import or build.

See `project/docs/research/mods/csc-native-workshop-delivery-20261104.md` and the
maintained `project/docs/civ6-ai/topics/native/workshop-delivery.md` for results.

## Components

- `ce_probe/`: a Lua-only, read-only package using installed CE memory APIs and
  ordinary gameplay events. No hooks or memory writes. Its controller selects
  the exact Workshop CE subscription and restores preferences on normal exit.
- `ce_frontend/CSC_AI_DistrictBridge.lua`: the proposed CSC-side consumer of a
  CE-owned numeric batch API. It disables/rejects partial packets and reports
  unavailable on stock CE1.3. It installs no tuning policy automatically.
- `prepare_ce_contribution.py`: produces a proposed CE integration patch and
  compiles native COFF objects; does not link, install or publish a CE DLL.
- `bridge.c`/`hook_entry.S`: common experimental native code. With
  `CSC_CE_INTEGRATION`, CE owns registration and context lifecycle. The default
  branch is an independent proxy used only to establish native package loading.
- `build.py`: builds that independent delivery experiment, qualifying the
  installed GameCore and preserving its export contract. It redistributes no
  game binary. The own-DLL experiment is not the selected release architecture.
- `run_smoke.py`: bounded shared-controller observation/delivery/context checks,
  no Frida. The corrected log analyzer retains receipts before counter resets.

All builders require explicit output paths outside this source directory.
Use the task's Desktop output folder for generated packages, caches and logs.
Toolchains/MinHook are developer build inputs, not player dependencies.

## Validation and remaining gates

The independent carrier proved local mod-folder loading,42 captured+256Q8 score
adjustments and same-process context reset. Its second driver postassert failed
because boundary snapshots missed reset counters; raw exit1 is preserved and
the existing Lua log was reconciled offline without replay. Both native
processes closed normally, exact preferences were restored and content hashes
matched. These are delivery facts, not AI improvement or release qualification.

The proposed CE API is not in released1.3. Its compiled objects and unapplied
patch do not establish a combined CE build or maintainer adoption. Do not ship
the CSC frontend as working tuning against an unmodified CE dependency. Native
callbacks remain numeric-only; do not replace them with CE's unfinished general
Lua callback. Save/load, timing, supported versions and mod compatibility remain
release gates, as does an actual Workshop upload/subscription roundtrip.

Run `test_gameplay.py --dependencies <lupa-dir>` for the actual diagnostic Lua,
`PYTHONPATH=<lupa-dir> python ce_probe/test_probe.py` for CE read fixtures, and
`python -m unittest discover -s project/tools/ai_workshop_bridge -p test_smoke_log.py`
for counter-reset reconciliation. Python temporary directories must be writable.
`CSCBridgeSelfTest` provides seven arithmetic checks in the independent DLL,
without loading game code. No test file launches Civ on import.
