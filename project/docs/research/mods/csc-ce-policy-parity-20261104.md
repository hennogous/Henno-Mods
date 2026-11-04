# Restoring the Python placement test through Community Extension

4 November 2026. Henno authorized a CE development fork to regain the placement
test capabilities of the local Python/Frida setup. This is a carrier and test
port, not a new scoring policy. The intended release remains CSC Lua/SQL plus an
upstream CE dependency, without a separate CSC DLL.

Fork: [feature/ai-district-scores](https://github.com/hennogous/CivilizationVI_CommunityExtension/tree/feature/ai-district-scores),
checkpoint `17f7c75`.
Base: WildW's `e59b5aa910c8a0fcab9b31973ffa477443de0e09`.
The feature is absent from released CE 1.3. An upstream PR follows qualification;
creation of a fork does not establish maintainer acceptance.

## The capability being ported

| Earlier setup | CE/Lua counterpart |
|---|---|
| Controller installs the read-only scanner through Tuner | Packaged gameplay Lua includes the same maintained scanner and CSC adjacency core. |
| Python computes the v2 shortlist | Pure Lua computes identical entries from identical captured observations. |
| Frida publishes numeric entries | Lua calls CE's typed begin/allow/entry/commit API. |
| Frida native callbacks alter fresh NetValue output | CE owns the numeric-only hook at the same qualified ordinary cache boundary. |
| Native cache/winner/PV observers | Three typed, read-only CE observers plus paged native records. |
| Python controls finite test intervals | The shared controller still controls the test; it does not compute or publish the game's policy. |

The retained rule promotes one best legal Bakers/Tailors pair per city when
planned Production+Gold is at least +4, and applies the existing graded, capped
deduction to observed legal sub-4 pairs. It retains river and first-Mill rules,
material-resource preservation, founded-type exclusion and owned-city tile scope.
The port does not add frontier scanning, building incentives, subsidies, orders
or a final-aggregate penalty.

## Complete fork build

The fork builds existing CE functionality together with the new native module.
The checked-in upstream build omits dependency inputs. The reproducible portable
route stages the source and restores missing AsmJit files from a pinned matching
revision; existing vendored CE files retain precedence. It builds actual
Capstone 5.0.3 and MinHook 1.3.4, with portable Zig 0.15.2. There is no global compiler
installation and no original game DLL is copied into the package.

The output preserves 157 original export names/ordinals, 155 as forwarders, with
local create/destroy wrappers. Imports are Windows/UCRT only. MSVC project wiring
was added, but the MSVC route remains untested. Process-owned hooks initialize
once; policy and trace state reset at context creation and before destruction.

The development CE and Lua packages have separate temporary identities ending
`2a06` and `2a07`. This avoids the earlier local/Workshop CE duplicate-resolution
problem and leaves stock CE and CSC content untouched.

## First native attempt: a reporting failure, closed at turn 3

`run-01` loaded the full CE fork and reached Online turn 3. A native status string
was truncated to 511 bytes by the public HKS `pushfstring` formatter, making its
JSON incomplete. The Lua log independently truncates individual lines at 2,047
bytes, while Tuner replies can retain longer output. Neither the source-only
fixtures nor a successful link had exposed these real transport limits.

The shared driver stopped and normally closed the game. All 152 subscription-level
preferences/149 IDs and autostart=false were restored; installed package manifests
matched; no native/Tuner owners remained. The raw failure is retained. This is a
partial debugging run, not completed parity or an efficacy result.

The shipped HKS exports no free `pushlstring` API. The correction uses short
native string fragments and the exact public HKS concatenation/stack-check APIs,
without assuming a LuaPlus C++ object layout. Long autonomous Lua receipts are
hex-framed into bounded disk lines with context epoch, sequence, ordered parts, byte count and checksum.
The reader rejects incomplete or conflicting receipts. Full scans, plans and
native traces must survive without a continuously connected Tuner client.

## Qualification protocol and completed result

The corrected run used the maintained shared controller, Online speed and endpoint 100.
It first checked a fresh context through turn 6, saved that boundary once, created an
observation-only context through turn 2 in the same process, then reloaded the saved turn 6
and checked captured scanner facts before continuing. Native module paths/hashes,
Lua/Python decisions on identical snapshots, signed score arithmetic, trace
coverage, original-human exclusions, retirement and exact restoration are gates.

Gameplay publication is event-driven rather than the old controller's inactive
boundary publication. Generation fences retire old callbacks; they do not promise
that a whole asynchronous analysis pass uses one policy. Disabling the hook does
not undo existing cached values or retained requests. Matching policy arithmetic
does not imply identical historical outcomes or economic benefit.

The corrected `run-02` passed fresh1–6, exact SaveComplete/hash verification,
a same-process observation-only world1–2 with native version/entries/changed=0,
and reload of turn 6 with no differences in captured scanner facts. Packaged Lua decisions
matched the Python shortlist on every accepted snapshot. The frozen first
phase log reconstructs 1,050-byte native status messages and a 57-record trace page,
exceeding both former transport limits without lost chunks. It contains net,
cache and best-winner records; the completed run also supplied PV records and
both adjustment signs.

| Completed check | Result |
|---|---|
| Native process and carrier | Same held DX11 process for both worlds and reload; actual module path/hash matched the complete CE build and pristine XP2. No Frida attachment. |
| Python-to-Lua decisions | 101 accepted snapshots matched the original Python shortlist, including the reloaded turn 6 comparison and final turn 100 scan. Python supplied no incentives to the game. |
| Publication and tracing | 100 published windows; 98 contained records. All 29,479 journal records reconstructed, with no missing pages or conflicting duplicates. |
| Signed delivery | 14,584 negative and 73 positive NetValue changes; every change matched the published player/city/district/plot and signed arithmetic. |
| Read-only diagnostic coverage | 14,663 cache, 132 winner and 27 PV observations. The other 14,657 records were NetValue changes. Winner records can concern other districts in the scoped city. |
| Failure/budget state | Zero native faults; no matched script/database runtime-error signatures in the closed logs. Protected-value arithmetic was additionally exercised in 36 isolated native checks. |
| Context and save/load | Observation context retained version/entries/changed0; saved turn 6 reloaded with no differences in captured scanner facts and original-human exclusions retained. This is not full RNG/cache/world parity. |
| Native follow-through | At turn 100, the five studied AIs had 12 Quarter foundations, 11 complete: 10 Bakers and 2 Tailors. This is observed construction, not counterfactual attribution or benefit. |
| Endpoint and retirement | Exact turn 100 final scan, no publication beyond the authorized endpoint; normal native exit0. |
| Restoration | All 152 subscription-level mod entries / 149 IDs and autostart=false restored; CSC, stock CE and both test-package manifests unchanged; no native/Tuner owners remained. |

**Development parity is restored for this bounded CSC-only setup.** The same
policy and the four diagnostic families now run through packaged Lua and CE,
without an external policy worker. The event-driven publication timing differs
from the old inactive-boundary driver, so this is not a claim of identical
historical outcomes. Native AI still owns selection, requests and construction.

This does not establish economic improvement, RomanHoliday/multiplayer or
general CE feature compatibility, MSVC qualification, arbitrary save/unload
behavior, an actual Workshop subscription roundtrip, or upstream acceptance.
After qualification, the contribution was opened as
[draft PR9 to WildW](https://github.com/Wild-W/CivilizationVI_CommunityExtension/pull/9),
head `a928eb8` (documentation follow-up to the tested native source).
It is for API/implementation review, not a release-ready claim. No separate
maintainer message was sent. [AI-N072] [AI-C052]

## Versions, tests and retained proof

- CE source checkpoint: `17f7c75` on `feature/ai-district-scores`.
- Corrected complete DLL: SHA-256
  `d80817659cefbb84feb5c5f3ce67429293bd604c274109dbdb93767f791aac6d`.
- GameCore: SHA-256
  `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
- Tested Lua/driver checkpoint: CSC `600a71f`; exact executed text is archived
  in `run-02/source-version` and qualified by `pins.json`. A post-run metadata
  correction distinguishes requested from actually completed lifecycle checks;
  it changes no policy or native hook behavior.
- Offline checks: 36 native, 23 actual-Lua policy/lifecycle/transport, 9 shared
  scanner, 15 harness/auditor, and 2 documentation preparation regressions passed.
- `run-02/parity-audit.json`, `result.json`, `reload-scanner-parity.json`,
  `checkpoint.json`, `loaded-modules.json`, `preferences-restored.json`,
  `session-closed.json` and seven archived log phases retain the result.
- The game-generated `AutoSave_0100` was copied after closure to
  `checkpoints/AutoSave_0100-treated-unreloaded.Civ6Save`, SHA-256
  `a7e2b6e979d389d4438440c6825db6877130e6e6edab832bfbc31d10893800ae`.
  Its header/file identity is verified; its saved clock has not been reverified
  by loading. It retains treatment history and is not a clean baseline.
- `build-v2/build-receipt.json` and `native-selftest-v2-receipt.json` retain
  source/compiler/dependency identities and the complete native checks.
- Read-only REA export checks independently retained HKS parent
  `ev_d07d4a4f92be2b6810517a36354fdc761c8dd3bd67052bd2d182c10120006c7c`,
  selected exports `ev_6a08f992356c44f08ccd264ad1f211b8d988810c19b07fd7ec7e3e61218f0cb2`,
  and CE parent `ev_a3792f48980a063b43d629d946511ab31e0b39435a3e20f75a29b5c03e45d5b2`.
  `rea-export-evidence.json` preserves the selected/summary records. These static
  tables establish export declarations; the game run supplies runtime proof.

## Maintained sources and evidence

- CE fork: native module, lifecycle integration, build tooling and dependency pins.
- `project/tools/ai_workshop_bridge/ce_policy/`: Lua decisions, packaged lifecycle,
  receipt framing, builder and actual-Lua fixtures.
- `project/tools/ai_workshop_bridge/ce_parity/`: isolated CE package assembler,
  shared-controller driver and trace/policy auditor.
- `project/tools/ai_site_planner/adjacency_policy/scan.lua`: original scanner,
  with a backward-compatible return of its existing observation table.
- `C:/Users/Shadow/Desktop/Codex/csc-ce-parity-20261104/`: versioned packages,
  installation receipts and native runs.
- `C:/Users/Shadow/Desktop/Codex/ce-fork-parity-20261104/`: complete native build
  receipts, dependency identities, compiler commands and isolated native checks.
