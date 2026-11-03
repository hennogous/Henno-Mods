# Native AI static extraction

Ghidra headless exporter, validated with Ghidra 12.2 and Temurin JDK 25.0.5+8 on the pinned Windows XP2 GameCore DLL.

Run `run-headless.ps1` with explicit `AnalysisRoot`, `GhidraHome`, `JavaHome`, `Targets`, and `Mapping`. An initial `ImportBinary` imports a local pinned DLL copy; later runs reopen the saved program with analysis disabled. Generated projects, C/disassembly, logs, manifests, caches and binaries belong beneath the Desktop Codex output directory, not this source directory. Use paths without spaces for the analysis/tool locations because Ghidra's Windows batch wrapper can mishandle them.

Targets file: one `hex_rva short_name` per line. Mapping file: tab-separated columns `old_rva,new_rva,category,size,name`, with optional # comments and a header. Only unique/unique-reordered/resolved names are applied. Old sizes and signatures are never imported. Multiple names at the same RVA become separate labels, not merged signatures. Function boundaries come from the PE importer and native Ghidra analysis.

Output: per-target estimated C, assembly, entry references/callers, direct called functions; target-status.tsv records recovered body ranges, mapping category, completion and decompiler error; ai-parameter-string-xrefs.txt locates two AI parameter strings and their containing reference functions. The decompiled types and arguments remain estimates requiring assembly verification.

Validated 2026-10-28: initial 13 requested functions and all 67 trustworthy direct CityBuild methods exported successfully. The current local package and pinned hashes are under Desktop/Codex/csc-native-ai-analysis-20261028. No game launch, hook, or installed game modification is performed.


The 2026-10-28 setup and analysis completed without fatal import/analysis/decompiler errors for recovered functions. Portable tool archive hashes were verified against official release metadata. Two callback addresses (RVA4a2850 and4a2550) had no native analyzed function start and were deliberately skipped; manifests record this rather than inventing boundaries. The full per-run receipt is `tooling-analysis-status.json` in the local analysis package. Initial warnings concerned absent PDB/DWARF and one null-address callback during automatic analysis; they did not prevent successful target exports.

## Supplied linker-map resource

The 29 October attachment is now an isolated, searchable historical GameCore reference. See [resource guide](../../docs/research/mods/csc-ai-gamecore-symbol-resource-20261029.md) for hashes, Ghidra project paths, current-build transfer rules and the disclosed map/DLL timestamp mismatch. `prepare_linker_map.py` creates a PE-checked symbol index; `ImportLinkerMap.java` imports hash-gated names into the historical project without applying prototypes or changing function bodies. Use this for a concrete native question; no game is required.

## Interactive GhidraMCP access

The installed local `ghidra` MCP exposes the analyzed current GameCore through
decompilation, xrefs/callers and bounded data inspection. See the
[setup and operating guide](../../docs/research/mods/csc-ai-ghidra-mcp-20261029.md)
for pinned versions, snapshot ownership, exact binary checks and actual smoke
evidence. It complements these reproducible headless exports and live probes;
it does not establish AI behavior from decompiled code alone.


## Lua context preflight and Linux-derived reference data

The pinned local community reference already includes `reference/data/
lua_methods.json`, `lua_signatures.json`, `lua_objects.json` and `layouts.json`.
Before a native reader, inspect exact `registered_on`/interface and same-context
shipped usage; C++ availability does not establish a Lua UI binding. In particular,
CityDistricts.GetDistrictByIndex is Gameplay-only in that registry. Parse these
minified files with JSON tools, not unrestricted line search. Full raw DWARF
import and automated context checking are not implemented. See
[cross-check and evidence scope](../../docs/research/mods/csc-native-tooling-community-crosscheck-20261030.md).


Community behavior-tree/operation activation reports: see
[native job route review](../../docs/research/mods/csc-ai-community-native-job-routes-20261030.md).
These add externally reported live activation evidence; callback identity and
economic-job execution remain unvalidated here. Do not install the demonstration
mods or use their historical RVAs without a separate protocol.


## Optional REA value tracing — locally tested

The [30 October offline trial](../../docs/research/mods/csc-ai-rea-trial-20261030.md)
reproduced the building preference multiplier and automatically exported the
scripted-target wrapper and native setter. REA6.8.0 required an isolated
Ghidra12.1.4; it rejected our12.2. Keep the existing prepared workbench as default,
using REA selectively for bounded dependency graphs/retained callees. Graphs were
partial; no token-saving or live AI benefit claim is established. The setter has
a conditional visibility/AI-knowledge update before its invalid-ID check, so an
invalid operation ID does not establish a no-effect probe. No agent registration
or game launch was performed.


## Bounded retained runtime observer

`observer_host.py` / `observer_daemon.py` compose the maintained NativeSession
callbacks; `work_admission_observer.js` is the current two-boundary adapter.
Explicit exact module/spec/config and dependency inputs are required. Attach
disabled, verify source facts, enable once, snapshot at inactive boundaries,
freeze before Menu and retain the Frida session until exact native exit. The
source110→113 case natively closed with five complete pairs and restored settings.
Other hooks still require their own ABI and scientific-coverage preflight.

See [the work-admission result](../../docs/research/mods/csc-ai-work-admission-20261031.md).
Important target-build findings: the ordinary city check gates on its stored
improvement-tree ID; cached Builder recommendations are grouped by a unit-definition
key rather than individual worker availability; the generic recommendation getter
returns an opaque receiver. Native behavior-log state can be printed without a
fresh decoded-trigger invocation. Preserve these distinctions when interpreting
recommendations, commitments and execution. These are observations for the pinned
current DLL, not a general Lua job-submission interface.


## Industrial Zone prerequisite observation

`industrial_zone_probe.py` composes the shared full-game controller and
`NativeSession`; it is a deliberately fixture-specific probe for the exact
archived turn-250 save, with Toulouse/4:262147 missing Workshop and
Nicomedia/2:589832 already constructing Factory. It requires explicit save,
native-directory, binary, DLL, user-root, installed-package, dependency, spec and
new-output paths. It refuses a wrong save, foreign native owner, changed inputs
or altered source premise. This is not a general campaign runner.

The `industrial-zone-decision-v1` observer profile uses
`industrial_zone_observer.js` to pair four city-scoped boundaries: dependency
aggregation, building selection, queue arbitration and building dispatch. Dynamic
loaded building indices and cache aliases are checked before observation.
`industrial_zone_snapshot.lua` reads physical facts in GameCore_Tuner; Gameplay
district enumeration uses `GetNumDistricts`/`GetDistrictByIndex`, not `Members()`.
Unavailable optional queue methods are preserved as unavailable.

Sources and dependencies remain frozen during the native session. The driver
advances at most five one-turn intervals, normally stopping after three with
calculation coverage, then uses the shared freeze/menu/restore/exit lifecycle.
An active named CSC assistance callback is suspended only in its owning context;
the actual 1 November fixture loaded profile OFF, so no suspension was needed.
Production, technologies and weights are not changed by the probe.

See [the actual result and evidence](../../docs/research/mods/civ6-industrial-zone-decision-boundary-20261101.md).
Source-gate tests: `test_industrial_zone_probe.py`; observer ABI/memory tests:
`test_industrial_zone_observer.js`; profile/lifecycle tests:
`test_industrial_observer_host.py`. Passing mocks does not substitute for native
API/source eligibility or adequate decision exposure.

## Disposable Ghidra session storage

`session_gc.py` is the Windows stdlib companion deployed beside the local MCP
launcher. The launcher leases each clone before copying, records exact owner/worker
creation identities, and collects abandoned copies on startup/shutdown. Only
reparse-free UUID direct children of the explicit session root qualify; masters
are never collection targets. Legacy unleased copies need ten quiet minutes and
no process references. Uncertain ownership/access/inventory preserves the copy.
Do not use age alone or delete the whole `sessions/` directory. Export durable
findings and retain small receipts rather than database archives.

Run focused safety checks with `python -B -m unittest discover -s
project/tools/native_ai -p test_session_gc.py`; Windows process discovery needs
normal host permissions. See the [MCP guide](../../docs/research/mods/csc-ai-ghidra-mcp-20261029.md)
for deployment, protection rules, receipts and verified cleanup totals.
