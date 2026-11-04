# Workshop delivery and a Community Extension release path

4 November2026. **Delivery research; further AI tuning is held.** Henno prefers
CSC to ship Lua/SQL with a dependency on Community Extension, rather than maintain
its own native DLL. The independent carrier below is an experiment, not the
selected CSC release architecture.

> Same-day follow-up: the [CE fork parity port](csc-ce-policy-parity-20261104.md)
> subsequently built and exercised the complete CE-native consumer and packaged
> Lua policy. The object-only candidate below remains the original investigation
> record. The new API is still absent from released CE1.3.

## Correction: a native component can live inside a Workshop package

An earlier conversation implied that native district hooks necessarily require a
separate launcher or manual DLL installation. That was too restrictive. Civ VI's
frontend `GameCores` table has `PackageId` and `DllPrefix`; a mod can select a
GameCore DLL from its own `Binaries/Win64` folder. Installed Workshop CE1.3 does
exactly that. Its optional console INI in the executable folder is not a required
DLL installation step.

Primary package: Workshop3277976174, GUID
`3351473b-0746-417a-a618-2b66a04d8f3d`.
`CommunityExtension.modinfo:15–23` registers frontend `Data/Config.sql`, whose
six lines select package GUID and prefix `GameCore_XP2_CE` for Expansion2.
The manifest includes `Binaries/Win64/GameCore_XP2_CE_FinalRelease.dll`.
The [author's repository](https://github.com/Wild-W/CivilizationVI_CommunityExtension)
and [Workshop description](https://steamcommunity.com/sharedfiles/filedetails/?id=3277976174)
describe the proxy mechanism. The fetched Workshop page contains inconsistent
removed/incompatible and subscription UI; that scrape alone cannot establish
current new-subscriber availability or moderation acceptance of a new item.

## Independent delivery experiment — completed

Source: `project/tools/ai_workshop_bridge/`. Own prototype GUID ends `a04`,
prefix `GameCore_XP2_CSC_Bridge`. It loads the installed pristine GS GameCore by
absolute executable-derived path and checks its entire-file SHA-256 before
installing hooks. No game DLL or executable is redistributed or replaced.

The proxy preserves157 original export names/ordinals, including explicit
create/destroy wrappers;155 others forward to the original. A separate assembler
shim preserves the ordinary caller's R12 row and seven-argument Win64 ABI.
The hot hook uses a native immutable policy snapshot, never Lua or game APIs.
Gameplay Lua owns begin/allow/entry/commit/disable/status calls. The diagnostic
is observation or a tiny+256Q8/+1utility input, not our adjacency+4 policy.

Build: portable Zig0.15.2, MinHook1.3.4; generated output stays outside the repo.
The DLL has only Windows/runtime imports, with no Python/Frida dependency.
Twelve actual Lua5.1 fixture checks and seven isolated native arithmetic checks
passed. Four log-reconciliation regressions were added after the live test.

| Live check | Result |
|---|---|
| Observation, fresh Online1→2 | Own package DLL and installed original independently present in module list; native API ready,2383 recorded NetValue calls at2,0 writes/0 faults. |
| Packaged+256 diagnostic, fresh Online1→6 | Package-owned Lua published new windows; preserved Lua.log establishes42 adjustments across four captured generations, every sample exactly+256 and excluding original human0. |
| Same-process context destruction/recreation, observation1→2 | Generation advanced to20; version/entries/changed reset to0 and disabled. No old policy crossed into the new world. |
| Closure | Both processes normally exited0;149 subscription-level preference entries/146 IDs and autostartfalse restored; CSC/prototype files unchanged; no owners remained. |

The second driver's final postassert returned1 because its end-of-turn snapshots
missed counters reset by the next publication. The game itself had already
closed normally. Its original result and exit are preserved. Offline reconciliation
of the already archived package log found42 writes and exact+256 samples; no
game was replayed to fix the report. The maintained analyzer now deduplicates
cumulative receipts by generation. This proves delivery, not a changed choice,
Quarter completion, economic benefit or full release lifecycle.

## Preferred release: CSC Lua plus a CE-owned native capability

CE's existing `Mem`/`ObjMem` primitives can access writable data, including
potentially the completed shared district-score matrix. That alone does not
establish a synchronized edit window between worker refresh, future-building
aggregation and selection. Editing the final matrix would also differ from our
earlier pre-store intervention and needs fresh-analysis/idempotence handling.

`RegisterCallEvent` is not a qualified shortcut. The
[author's current wiki](https://github.com/Wild-W/CivilizationVI_CommunityExtension/wiki/Memory-Manipulation#registercallevent)
marks it unfinished. Pinned/current public source exposes callback ABI and
lifetime concerns: stack/shadow-space handling, volatile argument preservation,
raw pointer bits passed through a double, no found state serialization/teardown,
and trampoline/jump-range assumptions. This is source analysis, not an observed
CE crash. GetBestDistrict is an activation/proposal path; its Lua thread safety
must not be inferred simply from the separate off-turn scoring jobs.

The proposed robust interface puts the hook and synchronization in CE and leaves
CSC's economic policy in ordinary Lua. A numeric batch carries exact
player/city/district/plot adjustments. CE performs scope/version checks, protects
invalid results, owns generations and disables on context retirement.

`prepare_ce_contribution.py` produces a contribution candidate from the same
native module with `CSC_CE_INTEGRATION`: **no separate CSC DLL is linked**.
It registers proposed `CE_AIDistrictScoresBegin/Allow/Entry/Commit/Disable/Status`
globals through CE's existing Lua registration and resets at create/destroy.
Two AMD64 COFF objects compile; the focused unapplied Main.cpp patch passes
`git apply --check` against CE commit
`e59b5aa910c8a0fcab9b31973ffa477443de0e09`.

This API is a **proposal, absent from released CE1.3**. Compilation of its objects
is not a full CE/MSVC build, compatibility test or maintainer acceptance. No
maintainer was contacted and no patch, DLL or Workshop item was published.
An independently maintained CE fork would still mean maintaining a native
distribution; it must not be presented as a dependency on stock CE.

## CE-only capability probe

`ce_probe/` packages only Lua and a manifest depending on the existing Workshop
CE. It uses ordinary gameplay events, registers no native callback and performs
no memory writes. Ten Lua5.1 fixtures passed. It fingerprints current GameCore
headers/functions, then follows statically verified Game/PlayerManager/CityManager
pointers, checking city identity against normal Lua APIs before bounded cache
reads. `Players[id].__instance` is a Lua reference wrapper and must not be treated
as a native Player::Instance. Reference Linux layout offsets also differ.

Job-complete flags are observations, not locks. CE does not expose pointer-span
validation; bounded reads and exact build checks do not make arbitrary pointers
safe.

The final CE-only Online1→3 probe passed: **307 bounded log receipts,55 city
observations and174 district-site score reads**, with no disabled-probe receipt
or memory writes. Module inspection verified CE1.3 and the installed original,
with no CSC proxy or Frida. The local CE copy selected by Civ's dependency
resolver was byte-identical to Workshop CE. Native exit0, exact150 preference
entries/147 IDs/autostartfalse restored, and CE/CSC/probe files unchanged.

The observed ordering explains why data access alone is insufficient: player1
at OnGameTurnStarted and PlayerTurnStarted on2 had job/offturn flags0; its later
PlayerTurnActivated snapshot had both1 and readable scores. This is not proof
that the latter precedes GetBestDistrict or provides an exclusive write window.
The proposed new CE score API was absent in the actual queried Lua context.

Four preceding attempts stopped in the menu without creating worlds. A disabled
local CE copy plus enabled Workshop copy caused native `ContainsDuplicates`
under recursive dependency activation and `MissingDependencies` under
nonrecursive activation. Selecting the dependency-resolved local copy avoided
moving/editing either installation. Three earlier read-probe worlds reached3
but disabled their diagnostic before cache access due to script assumptions:
Civ lacks `_G` here, and CE's FIELD_* constants were numeric **strings**, not
missing numeric APIs. Scalar normalization and regression fixtures resolved
these issues. All those processes also closed normally with preferences restored.
These failed branches are retained; they are not successful cache-read trials.

The proposed CSC-side adapter in `ce_frontend/` contains no DLL or native
addresses. Seven fixtures cover unavailable stock CE, numeric publication,
rejected/partial packets, human exclusion inputs and HavokScript environments.
It must remain disabled until a CE version provides the new consumer.

## Evidence and remaining release gates

Evidence root:
`C:/Users/Shadow/Desktop/Codex/csc-workshop-native-delivery-20261104/`.
Build identities and package hashes: `prototype-v1/build-manifest.json`.
Original native DLL SHA:
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
Installed CE DLL SHA:
`36ba871516326878984dac0d1903a08a48490ad386516cca4910c83f846f662f`.
CE export inspection: REA
`ev_63590d14493f79049cd42ef9d83cfcca4f713fd51ecb40b8af4bcb9297a3b579`.

Retained runs: `smoke-observe-01/`, `smoke-write-and-recreate-01/` and its
`reconciled-delivery.json`. CE-only results are `CE-read-probe-08/`; earlier
`CE-read-probe-01` through07 preserve the bounded failed branches.
The CE candidate is in `ce-contribution-v1/`, with
unapplied patch, source pins, compiler logs and contribution manifest.

Before further tuning, resolve the CE-owned consumer and validate the actual
combined CE build. Then qualify save/reload, wrong-version behavior, publication
timing, extended runs and intended mod combinations. CE is Windows/GS-specific
and shares the single GameCore selection with other native replacements. Actual
Workshop upload/subscription roundtrip is not tested by local package loading.
Keep those gates distinct from the now-demonstrated absence of an external
launcher requirement.
