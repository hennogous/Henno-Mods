# GameCore linker-map resource

Added 29 October 2026 from `gamecore_xp2.zip`, supplied by Henno from another
modder. Use this resource when a native function, overload, class, virtual table
or source-object boundary would help answer a concrete CSC AI question. It is a
research aid, not a new runtime dependency or a requirement to catalogue the
entire engine before improving CSC.

## What it adds

The supplied Microsoft linker map records decorated C++ symbols, addresses and
object-file names. Demangling makes class ownership and overload signatures
readable. With the historical DLL, Ghidra can show named callers/callees and
reconstructed implementation together. Object names such as `CityBuild.obj`
provide an additional way to find related code; vtable symbols help locate
virtual interfaces and follow their slots.

Our earlier current-build Ghidra project already used community-transferred
function names. This resource adds the original decorated names, richer aliases,
data/vtable names and the historical binary for checking that transfer. It does
not magically reveal source files, comments, local variable names, complete
class layouts or a complete public API. Map-derived names and signature text
are distinguished from decompiler-estimated types and current-build behavior.

## Local resource and provenance

Resource root:
`C:/Users/Shadow/Desktop/Codex/csc-gamecore-symbol-resource-20261029`

| Item | SHA-256 |
|---|---|
| Supplied historical DLL, `input/GameCore_XP2_FinalRelease.dll` | `138b6477735af27f7bf779013176932f05270a8fd91287baa267f39ea8556a82` |
| Supplied map, `input/GameCore_XP2_FinalRelease.map` | `60d0e5a585ccf57e382e08e5bf9f1caa0d6648ae56700a3c53d91ac1fe77b9ba` |
| Supplied `most_recent_releas` DLL, identical to our current analysis/probe DLL | `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c` |

The historical DLL's PE timestamp is `6446ecb5` (24 April 2023); the map says
`6446be15` on the same date. These are **not equal**, and the reason is unknown.
The newer DLL's timestamp is `667c6f5b` (26 June 2024). Build timestamps do not
identify when a user installed a game or prove Steam package equivalence; use
file hashes to identify the actual engine.

`index/map-validation.json` records matching preferred image base, section bases
and entry point for the historical DLL. Three wrapped `.idata$6` linker sentinels
and 367 absolute entries are excluded from the address index. The remaining
**295,934 symbol rows** include **85,652 function rows at 43,806 distinct
addresses**. Aliases are not separate implementations. 32,077 of those addresses
also occur as PE exception-table function starts; leaf functions need not have
such entries. This is strong layout evidence, not a claim of exact map/binary
build identity despite the timestamp discrepancy.

The existing community mapping has 43,803 old-RVA rows; **all 43,803 occur in the
supplied map's function addresses**. `index/reference-bridge.json` records this
join and the original mapping categories. A matching address is not independent
validation of every current-build counterpart.

| Function | Historical RVA | Current pinned DLL RVA |
|---|---|---|
| `CityBuild::GetBestBuilding` | `3e1fd0` | `3e4710` |
| `CityBuild::QueueNextBuild` | `3e5a50` | `3e8190` |
| `CityBuild::CalculateDistrictValues` | `3dd7a0` | `3dfee0` |

These are existing community `unique` mappings, also used in our earlier targeted
analysis/probes. Do not apply one global address delta: the shifts differ.

## Reusable workflow

1. Search `index/symbols.tsv` for a function, class, object filename or decorated
   name. It includes public/static, function/data and PE-start evidence. Search
   the demangled `import/imported-symbols.tsv` when the Ghidra import is complete.
2. Open the isolated historical Ghidra project
   `ghidra-project/CSC_GameCore_SymbolReference_2023.gpr`. The current-build
   project remains `csc-native-ai-analysis-20261028/ghidra-project/CSC_Native_AI.gpr`.
3. Inspect the historical implementation and references with the supplied names.
   The maintained importer adds `MAP23_` labels and demangled signature text to
   its report. It does **not** import prototypes, create function boundaries or
   collapse folded aliases into a single authoritative signature. Unique existing
   function starts may receive readable names; aliases remain separate labels.
4. Locate the current counterpart using the pinned community mapping, Ghidra
   Version Tracking, or focused assembly/caller/vtable comparison. Review ambiguous
   matches, changed implementations and inferred matches individually. Validate
   current bytes and the intended call context before using an RVA for a probe.
5. Record the hash, RVA, evidence and scope in the relevant research note. Native
   value application, actual AI selection and improved supply-chain outcomes remain
   separate claims. Neither a symbol name nor reconstructed code proves efficacy.

The upstream mapping labels its target Steam build15038592; our earlier installed
package was15296837. Preserve that provenance distinction. The current DLL hash
and our checked targets are authoritative; do not assume every upstream entry is
independently verified for every installed package.

Useful first lookups: building/district evaluation and contracts, yield forecasts,
improvement/harvest valuation, Builder recruitment and job selection. Use a bounded
question; return to implementation/testing when the relevant mechanism is clear.

## Tools and reproduction

Maintained tools are in `project/tools/native_ai/`:

- `prepare_linker_map.py --map MAP --binary OLD_DLL --output INDEX_DIRECTORY`
  builds the raw searchable index and PE/layout receipt without executing a DLL.
- `ImportLinkerMap.java` is a Ghidra post-script taking `symbols.tsv`, expected
  program SHA-256, expected TSV SHA-256, and an output directory. Both hashes are
  checked before modifying the Ghidra database. It imports function and vtable
  labels; the full raw index retains the other data/compiler/unwind symbols.
- Existing `ExportAiTargets.java` and `run-headless.ps1` remain available for
  bounded reconstructed-C/assembly exports. Supply target RVAs and mappings for
  the **correct** program version; the existing current-build inputs are not
  historical-DLL inputs.

Ghidra12.2/Temurin25 are already installed below
`Desktop/Codex/csc-native-ai-analysis-20261028/tools`. See the resource's
`run-import.ps1`, `headless-console.log`, `import/import-summary.txt` and
`resource-receipt.json` for the actual command, status and verification. Absence
of a completed receipt means setup is pending, not proven successful.

No game launch, hooking, binary replacement, CSC/RH tuning or installed-asset
change is needed for this workflow. Keep supplied binaries, map, generated C and
Ghidra databases in the local research package, not in the mod or source-control
repository.

## Verified ready status

The isolated Ghidra project is saved and ready. The completed import contains
94,171 function/vtable labels, 94,080 demangled names and 31,872 renamed existing
functions, with zero out-of-memory-address entries or import errors. Three sample
functions (GetBestBuilding, QueueNextBuild, CalculateDistrictValues) all decompiled
successfully; reconstructed C, assembly and named references are in `review-exports/`.
The map explicitly names GetBestBuilding's argument as `FixedPointT<8>&`, consistent
with the Q8 representation observed in our current-build probe; this does not make
other inferred argument or class layouts authoritative.

The original ZIP is preserved as `input/original-attachment.zip`, including its
newer DLL. `resource-receipt.json` pins the local inputs, indexes and tool sources.
Initial Ghidra analysis reported missing PDB/DWARF, an automatic null-address
warning and some unprocessed RTTI descriptors. The first symbol import also hit
101 label/function rename collisions; `first-import/` preserves that report.
Distinct stable function names resolved all collisions on reimport. These were
research-tool issues, with no game execution or effects. Headless can return zero
when a script reports an error: check the receipt, import summary and target-status
files rather than process exit alone.
