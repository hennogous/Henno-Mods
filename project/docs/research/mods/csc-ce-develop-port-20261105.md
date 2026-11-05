# CE API contribution reset: develop, scope and maintainability

5 November 2026. Henno approved closing the premature master-based draft,
preserving the tested fork, preparing an API-only feature branch from develop,
revalidating it and discussing the final scope before any new upstream PR.
This report preserves the initial offline handoff and the subsequent supported
build qualification. Henno returned to the keyboard: installation and both
MSVC builds now pass; the bounded native regression is in progress. No
replacement upstream PR has been opened.

## Upstream status and scope

[PR9](https://github.com/Wild-W/CivilizationVI_CommunityExtension/pull/9)
was closed at **2026-11-05 06:39:18 UTC**, with the approved explanation that a
focused develop-based API contribution will follow scope review/revalidation.
No replacement PR was opened and the old feature branch was not rewritten.

- Old tested fork remains clean at `a928eb8b4298ed24dc2d74be0123ca2da434ed63`.
- Its reference branch remains
  `hennogous/CivilizationVI_CommunityExtension:feature/ai-district-scores`.
- The isolated checkout also preserves
  `archive/ai-district-scores-master-20261105` at that same commit.
- New branch: `feature/ai-district-scores-develop`, based on upstream develop
  `2986a746b396eb93aad14f9afffb043a09c2c489`.
- Reviewed source checkpoint `f9eda1c9922c36717156f89e1eb72bf6045887d4`, pushed to
  [the new feature branch](https://github.com/hennogous/CivilizationVI_CommunityExtension/tree/feature/ai-district-scores-develop).
- Reproducible test-driver/documentation follow-up:
  `87f48fc7878d00851279bccbc9dd30cfe147470b`. The native C implementation is
  unchanged by that second commit. Both commits are pushed; the fork is clean.
- Checkout/evidence root: `Desktop/Codex/csc-ce-develop-port-20261105/`.

WildW's stated convention is feature branches into develop, with master reserved
for managed releases. The old PR had bundled an alternate Python/Zig build route
with the API. That was a development workaround, not an API requirement. The new
contribution uses the existing Visual Studio project and excludes that alternate
builder. CSC's placement policy remains in CSC; CE exposes generic native tools.
New API capabilities and future PR grouping still need review with Henno.

## What the source port contains

The new native module lives under
`CivilizationVI_CommunityExtension/native/` in develop's directory layout:
the C module/header, Win64 MASM entry shim, target-identity metadata and API notes.
The existing Main.cpp receives initialization, per-Lua-context registration and
create/destroy reset calls. Existing project/filter files gain per-file C11,
MASM and Bcrypt integration for both x64 configurations.

The port preserves develop's logger, process-owned `std::call_once`, export and
destroy implementation, and newer CE features. It does not replace Runtime,
HavokScript or Exports source. The unused independent-carrier branch and old
GNU shim/build tooling are absent. The earlier public API, numeric guards,
diagnostic families and HKS long-string transport remain the intended contract.

Independent source review checks the recovered Win64 input/output contracts,
stack arguments, output-pointer identity, qualification-before-hooking, worker
thread behavior, context reset, locks, failure handling and generation fencing.
Source parity is not proof of MSVC code generation or a working develop DLL.

The independent source/ABI review passes. Final C SHA-256 is
`7a6cdf2abe5770268af51d23b2d45e7db0edcd6ee5605bc557785e766a4a6343`.
The readability receipt verifies **7,774 C tokens, 53 header tokens and all
preprocessor directive lines unchanged**. Thirty inherited function bodies and
the CE integration initializer match their reviewed reference. Receipts are
`api-source-checks.json` and `readability-token-check.{py,json}` in the evidence root.

## Maintainability is a contribution requirement

Henno explicitly relayed WildW's concern about maintaining AI-written code.
The readability pass expands dense control flow and adds explanations beside:

- recovered native ABIs, row spans and evidence-backed target addresses;
- ownership, staging/publication locks and worker-only numeric lookups;
- context generations, in-flight callbacks, persistent caches and sticky faults;
- Q8 units, bounded tables/journals, protected scores and overflow handling;
- HKS argument-error exits and bounded JSON assembly;
- qualification failure and partial-hook cleanup.

Comments must explain reasons and limits rather than merely restate syntax.
The review preserves program tokens while changing comments/layout; a reviewer
walkthrough and explicit qualification limits accompany the code. Neither good
comments nor the historical Online100 result substitutes for fresh native tests.

## Initial offline handoff: build environment prepared

At the initial handoff, the host had the older ModBuddy VS2013 shell/MSBuild12 and SDK8.x, but lacked
MSVC v143, MSBuild17, a current Windows SDK and vcpkg. The approved minimal
Microsoft VS2022 Build Tools installer was downloaded, signature-verified and
hashed. Windows elevation waited; Henno then deferred installation until he is
at the keyboard. The launcher was cancelled; no toolchain installation occurred.
An elevated process inventory still lists the old Windows consent window
(PID11484) after launcher cancellation. Dismiss that existing prompt before
starting a fresh installation; do not assume the elevation request disappeared.

`environment/` contains a pinned vcpkg checkout, external manifest and ordinary
MSBuild imports, verified dependency archives, baseline source inventory and
PowerShell build recipes. These are local environment artifacts, not a new CE
build system. They avoid global vcpkg integration or changes to the CE project.

- vcpkg baseline: `5d68747adeb88f05aac8ca4d18d29e50296509b1`.
- MinHook1.3.4 and Capstone5.0.9 with x86 enabled, `x64-windows-static`.
- Develop has removed AsmJit; no backend restoration is needed.
- An output-directory-only library-name alias accommodates upstream's legacy
  `libMinHook.x64.lib` pragma versus the vcpkg library name.
- First build the immutable upstream baseline, then the API feature, through
  the same existing solution and environment to distinguish pre-existing errors.

The installer is Microsoft's VS17 release bootstrapper, SHA-256
`972d771c33c2887b13900c2052e5d2e88208531f6d5ee3c4405d7648e853009b`.
Intended installation path is `C:/BuildTools/CE-v143`; no files were installed
there during this work. Installer plan and environment provenance are retained
outside the source checkout. Do not restart elevation while Henno is away.

## Offline verification and test preparation

The actual Lua policy/lifecycle/transport suite passes **24 tests**. The harness,
record auditor and isolated-package suite pass **17 tests**. The shared game
controller passes **164 tests**, including content-ID selection and original
preference backup guards. An offline fixture now supplies its own user directory
instead of assuming the sandbox's redirected LOCALAPPDATA contains Civ logs.

All **36 isolated native C checks pass**, compiled with the already available
Zig0.15.2 compiler. They use synthetic buffers, stub originals and abort-if-called
MinHook/assembly-entry stubs; no CE DLL or game is loaded. This is a unit test,
not a replacement CE build route or proof of MSVC/MASM integration. The receipt
is `offline-selftest/result.json`, with exit0 and executable SHA-256
`35d0fe442453fcaf830896ce94ed98aac6253c18984ec32772a137c1a7c77d43`.
The exact isolated driver is included under `native/tests/selftest.c` for reviewer
reproduction. Its README gives an out-of-tree x64 MSVC recipe, explicitly pending
execution with the supported toolchain.

The installed CSC Core differs from the final reviewed source. Rather than
overwrite the human package or silently claim matching bytes, the regression
package builder creates a distinct test copy ending `2a08`, retaining installed
art and overlaying only the four reviewed adjacency files. The Lua test package
depends on that identity and records the Core actually provided by it. The
controller accepts the selected CSC identity and also verifies the unchanged
human reference package. Its default production IDs remain unchanged.

Prepared packages under `packages/` are **not installed**. The CSC snapshot has
618 files with reference and overlay hashes; the policy remains the existing v2
formula. The future run will be a carrier/lifecycle regression using the reviewed
adjacency fixes, not a matched economic experiment or an isolated Mill-fix arm.
Only the CSC and policy packages are prepared; there is no new complete CE DLL
or CE package until the supported build runs.

## Questions to settle before a replacement PR

The current contribution is the qualified-boundary score API and diagnostics,
not a commitment to every possible AI control. Review these separately:

| Question | Why it belongs in scope review |
| --- | --- |
| Publication ownership | There is one publisher per context; multiple consuming mods must coordinate. Per-mod ownership/composition is not implemented. |
| Correction boundary | The existing hook precedes future-building aggregation. A later forecast correction needs evidence and its own contract. |
| Read-only component diagnostics | Building/effect detail may distinguish benefits from approximations, but must be bounded and filter before expensive cross-language work. |
| District-local building eligibility | A native predicate could eventually replace hidden flags, but current flags work and no replacement API is implemented. |
| Lifetimes and versions | Exact-target guards, generation fences, unsupported live unload, save reconstruction and compatibility limits need maintainer review. |

Do not add speculative capabilities just to enlarge the proposal. Identify the
concrete CSC mismatch and whether a reusable CE control is necessary. Build
mechanics remain a separate discussion only if the supported build cannot meet
the feature's actual requirements.

## Qualification planned at the initial handoff

When Henno is at the keyboard, finish the approved toolchain installation, build
upstream baseline and the port, run native self-checks with that toolchain and
inspect DLL exports/imports and MASM unwind/code generation. Only then install
isolated test packages and use the maintained shared controller for a bounded
Online-speed regression, never beyond100. Preserve exact content/preferences,
native identities, source pins, policy and all four trace families, generation
retirement, HKS transport and context/save checks. Original CSC/CE stay untouched.

No game, FireTuner request, Frida attachment, installed package update, new live
score or native develop-DLL result is claimed by this offline handoff. Earlier
[master-based parity results](csc-ce-policy-parity-20261104.md) remain historical
qualification of that earlier artifact. They are not inherited by this branch.

## Supported-toolchain continuation

Henno returned and resumed installation. The first elevated attempt failed with
exit87 because `--lang` is not valid for this install operation; it installed
the Installer client, not the compiler. Later automation-launched consent
requests did not produce a usable prompt for him. A small, readable desktop
launcher ran the corrected command directly from his session. Installation
completed with exit0, and `vswhere` confirms a complete, launchable instance
without a reboot requirement:

| Tool | Installed version |
| --- | --- |
| Visual Studio Build Tools 2022 | 17.14.37827.9 |
| MSVC v143 | 14.44.35207 |
| Windows SDK | 10.0.26100.0 |
| Installation root | `C:/BuildTools/CE-v143` |

The pinned vcpkg dependencies compiled successfully. Unmodified upstream
develop and feature `87f48fc` then built through the same existing Release/x64
VCXPROJ and environment. Both report **144 warnings and zero errors**; the API
adds no compiler warnings. Neither build required a CE source fix. The baseline's
98 source-file hashes remain unchanged and the feature checkout remains clean.

| Complete DLL | Bytes | SHA-256 |
| --- | ---: | --- |
| Upstream baseline | 670,208 | `18af3c5a0e92d98756a0fdfcd28351bdcbaf1efdcd646ce6a27adfcb995991ad` |
| Develop API feature | 685,056 | `b1090682fc6c964d077c36efe4dcbac6693d6bf83f9da08b5ad4c0f6e77d139b` |

The exact tools, dependency libraries, source inventories, invocations, logs and
MSBuild binary logs are pinned in `supported-msvc-builds.json` under the evidence
root. The external environment uses static MSVC runtime/dependency libraries;
the resulting feature DLL imports only Windows KERNEL32, USER32 and BCrypt.
This is a supported-project build, not the earlier whole-CE Zig workaround.

The isolated test recipe also runs successfully with x64 MSVC C11: **36 checks,
exit0**, executable SHA-256
`dffa1f07ac473e7ecb3c1ad876f28281df9901dacf239862fdd37d06e348794c`.
Its receipt is `msvc-selftest/result.json`. These synthetic tests still use stubs
and do not execute the real assembly hook or load Civ.

An independent static audit of the complete DLL confirms all 157 export names,
ordinals and forwarding contracts match the baseline. The actual 68-byte MASM
shim preserves the recovered stack arguments, R12 context and return address;
its PE exception entry describes the 88-byte stack allocation correctly.
Bounded disassembly also corroborates the original-game hash, timestamp, image
size and instruction-prefix guards before hook installation, all eight Lua
bindings, initialization order and create/destroy resets. Reproducible scripts,
symbols, disassembly, import/export tables and receipts are under
`independent-artifact-audit/`. This is a static regression gate, not observed
exception unwinding or native lifecycle proof.

## Native regression in progress

The shared `ce_parity` driver has started an Online-speed test capped at100,
including the planned fresh-context and exact-save reload checks. The evidence
directory is `native-regression-msvc-01/`. The driver exclusively owns Tuner;
its executed Python/Lua sources and installed packages are frozen during the run.

The two old dedicated development packages were moved into `runtime-backup/`
before installing the new CE and policy copies. A separate CSC regression copy
contains the reviewed adjacency files. `runtime-staging.json` records all source,
backup and installed hashes. Human CSC and stock CE remain unchanged. After the
driver closes and restores preferences, restore the previous development copies
and move test copies out of Mods, checking their recorded inventories.

No native outcome is claimed yet. Completion requires the driver's lifecycle,
module, source, content and preference receipts plus the four-family trace audit;
the earlier prototype's results remain separate.
