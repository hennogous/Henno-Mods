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
planned Production+Gold is at least4, and applies the existing graded, capped
deduction to observed legal sub-4 pairs. It retains river and first-Mill rules,
material-resource preservation, founded-type exclusion and owned-city tile scope.
The port does not add frontier scanning, building incentives, subsidies, orders
or a final-aggregate penalty.

## Complete fork build

The fork builds existing CE functionality together with the new native module.
The checked-in upstream build omits dependency inputs. The reproducible portable
route stages the source and restores missing AsmJit files from a pinned matching
revision; existing vendored CE files retain precedence. It builds actual
Capstone5.0.3 and MinHook1.3.4, with portable Zig0.15.2. There is no global compiler
installation and no game DLL is copied into the package.

The output preserves157 original export names/ordinals,155 as forwarders, with
local create/destroy wrappers. Imports are Windows/UCRT only. MSVC project wiring
was added, but the MSVC route remains untested. Process-owned hooks initialize
once; policy and trace state reset at context creation and before destruction.

The development CE and Lua packages have separate temporary identities ending
`2a06` and `2a07`. This avoids the earlier local/Workshop CE duplicate-resolution
problem and leaves stock CE and CSC content untouched.

## First native attempt: a reporting failure, closed at3

`run-01` loaded the full CE fork and reached Online turn3. A native status string
was truncated to511 bytes by the public HKS `pushfstring` formatter, making its
JSON incomplete. The Lua log independently truncates individual lines at2047
bytes, while Tuner replies can retain longer output. Neither the source-only
fixtures nor a successful link had exposed these real transport limits.

The shared driver stopped and normally closed the game. All152 subscription-level
preferences/149 IDs and autostartfalse were restored; installed package manifests
matched; no native/Tuner owners remained. The raw failure is retained. This is a
partial debugging run, not completed parity or an efficacy result.

The shipped HKS exports no free `pushlstring` API. The correction uses short
native string fragments and the exact public HKS concatenation/stack-check APIs,
without assuming a LuaPlus C++ object layout. Long autonomous Lua receipts are hex-framed into bounded disk
lines with context epoch, sequence, ordered parts, byte count and checksum.
The reader rejects incomplete or conflicting receipts. Full scans, plans and
native traces must survive without a continuously connected Tuner client.

## Qualification protocol and current boundary

The next run uses the maintained shared controller, Online speed and endpoint100.
It first checks a fresh context through6, saves that boundary once, creates an
observation-only context through2 in the same process, then reloads the saved6
and checks captured scanner facts before continuing. Native module paths/hashes,
Lua/Python decisions on identical snapshots, signed score arithmetic, trace
coverage, original-human exclusions, retirement and exact restoration are gates.

Gameplay publication is event-driven rather than the old controller's inactive
boundary publication. Generation fences retire old callbacks; they do not promise
that a whole asynchronous analysis pass uses one policy. Disabling the hook does
not undo existing cached values or retained requests. Matching policy arithmetic
does not imply identical historical outcomes or economic benefit.

The corrected `run-02` has passed fresh1–6, exact SaveComplete/hash verification,
a same-process observation-only world1–2 with native version/entries/changed0,
and reload6 with no differences in captured scanner facts. Packaged Lua decisions
match the Python shortlist on every accepted snapshot so far. The frozen first
phase log reconstructs1050-byte native status messages and a57-record trace page,
exceeding both former transport limits without lost chunks. It contains net,
cache and best-winner records; PV coverage and both adjustment signs remain part
of the final assessment.

**The Online100 continuation and final parity assessment are pending.**

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
