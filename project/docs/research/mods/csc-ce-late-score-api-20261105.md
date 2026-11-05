# CE C++ refactor and late district score API

Henno asked to refactor the tested `develop` port in line with WildW's review
feedback and add the late write. The feature branch still uses upstream
`develop` at `2986a746b396eb93aad14f9afffb043a09c2c489`, confirmed before editing.
The earlier C port remains the behavior reference and has its own qualification.
[Previous port and review requirements](csc-ce-develop-port-20261105.md)

## Integration review

| Concern | Change |
| --- | --- |
| Direct MinHook use | The feature uses typed hook descriptions and `Runtime::InstallHookGroup`. The shared helper creates every trampoline before enabling the group. It reports create, queue and apply errors, and rolls back only hooks created by that call. The existing single-hook helper keeps its behavior. |
| C code in a C++ project | `AI::DistrictScores` uses CE's C++20 build, `hks::lua_State`, `PushLuaMethod` and the existing create/register/reset lifecycle. The feature uses scoped ownership for file and hash handles and scoped locks for policy data. Lock guards leave scope before HKS calls that can exit via `longjmp`. Only the Win64 NetValue shim and its entry linkage are ABI-specific. |
| Unlabeled addresses | `native/target_identity.h` names the GameCore functions, caller return sites, CityBuild fields and row offsets. The code checks the original binary SHA, loaded prefixes, and the aggregation caller's relative `CALL`. |

## Gameplay Lua contract

`CE_AIDistrictScoresLateEntry(player, city, district, plot, expectedBeforeQ8,
expectedFinalQ8, deltaQ8)` adds a late entry to the existing Begin, Allow and
Commit transaction. Each pair can appear once across the early and late APIs.
The same generation fence, write budget and trace capacity apply to both.

At the qualified `DoTurnActivate` call to `CalculateDistrictValues`, the hook
captures a candidate only when it has the expected positive entry score. On
return, the row must still be a non-center, owned, eligible, unreserved row in
the same CityBuild district matrix. Its row score pointer must alias that matrix,
and its finished native score must match the expected value. The adjusted score
must remain positive and within the safe score range. `late` journal records
show the finished score and the result, with reason 5 or 6 for an entry or final
score mismatch. The ordinary cache, winner and plot present value can then show
what consumed the result. [Late native boundary](csc-ai-late-placement-20261105.md)

The caller still supplies the expected scores and the calibrated delta. The API
does not expose the consumed building roots needed to price new CSC corrections
on arbitrary sites. That measurement is separate from applying a known delta.

## Offline qualification

The existing Release x64 Visual Studio project builds with MSVC 14.44 and
Windows SDK 10.0.26100. The final DLL SHA-256 is
`fbf1df557e1168447a64e1b224dd399a9b9790caaf0f7d3f56683be7e30e2fc9`.
All 157 upstream PE export contracts match, the compiled shim retains its
88-byte Win64 stack allocation and unwind record, and the pinned original's
late call has bytes `e89fd5ffff` and targets `CalculateDistrictValues`.

The isolated C++20 host passes 50 scoring checks and four hook-group checks.
It covers the early score and diagnostic paths, a late adjustment, stale entry
and final values, reservation changes, matrix bounds, generation retirement,
and rollback when create, queue or apply fails. Synthetic tests use fake
MinHook and original game routines. The actual DLL build uses CE's existing
dependencies. [CE feature checkpoint `ba06976`](https://github.com/hennogous/CivilizationVI_CommunityExtension/commit/ba06976cc01ced0f2efe9c93878e94ff89e5410a)

## Matched native replay through CE

The shared controller reloaded the same Online turn-1 Delhi checkpoint used
for the Frida proof and advanced it to turn 2. The captured starting world
matched exactly. The process loaded the pinned original GameCore and the
refactored CE DLL. A single Lua transaction admitted two different pairs.

| Boundary | District and plot | Native Q8 | Result Q8 |
| --- | --- | ---: | ---: |
| Early NetValue | Tailors, 1210 | 77,534 | 77,535 |
| Late aggregation return | Bakers, 1210 | 104,621 | 248,479 |

The late entry required 77,534 Q8 at aggregation entry. The cache, native
winner and plot-specific present value all read the resulting 248,479 Q8.
Delhi's district tree decoded Bakers at 970 utility, reserved (26, 16), and
accepted the missing Craftsmanship goal. The CE journal contains six records,
two writes, and zero native API faults. The replay reached preparation. The
4,398 Q8 calibrated deduction has its own earlier Frida replay and a synthetic
CE check. This CE replay used the diagnostic pulse.

The save had been created with CSC alone. Enabling a separate CE mod in the
menu still loaded stock GameCore, so the first attempt stopped before
publication. The trial copy of CSC then selected the CE DLL through its existing
package ID using a front-end SQL action. This kept the gameplay payload and
saved world intact. The first attempt with that carrier matched the world and
stopped before publication because the harness pointed to a missing reference
path. The corrected attempt validates the reference before opening Civ.
This isolated packaging is a test fixture. Deployment still targets a CE
dependency, and the replay covers one matched calculation with this build.

The process closed normally with exit code 0. The shared controller verified
preference restoration, the trial package was retired by content hash, and the
working CSC and stock CE packages verified unchanged.

Evidence is under `Desktop/Codex/csc-ce-late-placement-20261105/run-03`.
`ce-journal.json` has SHA-256
`306c5486cbcd5caba4c326c1b21f6c707c4440f04ab68c13d77e9a9e5d9ea87a`.
The command receipts, native AI log slices and `result.json` retain the complete
decision evidence. [Early and late replay driver](https://github.com/hennogous/Henno-Mods/blob/main/project/tools/native_ai/late_placement/ce_replay.py)
