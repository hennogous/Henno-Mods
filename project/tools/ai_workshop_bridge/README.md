# Workshop delivery prototypes

**Preferred release:** CSC Lua/SQL with a Community Extension dependency. The
preserved tested carrier is the
[earlier CE fork](https://github.com/hennogous/CivilizationVI_CommunityExtension/tree/feature/ai-district-scores),
with `ce_policy/` and `ce_parity/`. Its unchanged v2 policy completed a bounded
Online100 test, including same-process context reset and save/load checks.
Stock CE1.3 lacks the API; upstream adoption and release qualification remain
separate. No installed CSC content is changed by these tools on import or build.

The master-based draft PR is closed. The API-only
[develop port](https://github.com/hennogous/CivilizationVI_CommunityExtension/tree/feature/ai-district-scores-develop)
has source review and offline checks; supported MSVC and native qualification
remain pending. It uses the existing CE project without the alternate whole-CE
builder. See `project/docs/research/mods/csc-ce-develop-port-20261105.md`.

See `project/docs/research/mods/csc-native-workshop-delivery-20261104.md` and the
maintained `project/docs/civ6-ai/topics/native/workshop-delivery.md` for results.
The current port and its exact evidence are in
`project/docs/research/mods/csc-ce-policy-parity-20261104.md`.

## Components

- `ce_policy/`: current Lua-only shortlist, shared scanner, lifecycle and durable
  framed receipts. No DLL/Python/Frida runtime is carried by this package.
- `ce_parity/`: isolated CE test packaging, shared-controller game driver and
  strict policy/native-trace auditor. Python audits/controls the test only.
- The fork's `native/AIDistrictScores.c` is the current native implementation;
  its `native/README.md` and `tools/README.md` describe the API and full build.
- `ce_probe/`: a Lua-only, read-only package using installed CE memory APIs and
  ordinary gameplay events. No hooks or memory writes. Its controller selects
  the exact Workshop CE subscription and restores preferences on normal exit.
- `ce_frontend/CSC_AI_DistrictBridge.lua`: the proposed CSC-side consumer of a
  CE-owned numeric batch API. It disables/rejects partial packets and reports
  unavailable on stock CE1.3. It installs no tuning policy automatically.
- `prepare_ce_contribution.py`: historical candidate preparation. It reproduces
  an earlier object-only proposal, not the subsequently qualified fork module.
  Do not overwrite the fork's current source with this older candidate.
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

The CE API is not in released1.3. The historical compiled objects and unapplied
patch alone did not establish a combined CE build; the later complete fork
and bounded parity test provide that development evidence. Do not ship
the CSC frontend as working tuning against an unmodified CE dependency. Native
callbacks remain numeric-only; do not replace them with CE's unfinished general
Lua callback. Save/load, timing, supported versions and mod compatibility remain
release gates beyond the bounded checks in the parity report, as does an actual
Workshop upload/subscription roundtrip. Existing CE functionality outside the
exercised path, MSVC, RomanHoliday and multiplayer have not been qualified here.

Run `test_gameplay.py --dependencies <lupa-dir>` for the actual diagnostic Lua,
`PYTHONPATH=<lupa-dir> python ce_probe/test_probe.py` for CE read fixtures, and
`python -m unittest discover -s project/tools/ai_workshop_bridge -p test_smoke_log.py`
for counter-reset reconciliation. Python temporary directories must be writable.
`CSCBridgeSelfTest` provides seven arithmetic checks in the independent DLL,
without loading game code. No test file launches Civ on import.
