# Community tooling cross-check —30October2026

Henno supplied another modder's setup notes: old Windows symbols, headless batch
exports, masked-byte/neighbor/callgraph mappings, Linux DWARF types, alias tables
and live verification. Their depot IDs, full corpus sizes, mapping percentages
and call-site agreement are reported external claims, not independently audited
results of this checkout. Their stated per-class Windows-minus8 observation is
not a universal ABI/layout transformation.

Our existing resources already include both maintained headless exports and
interactive MCP, separate hash-pinned historical/current DLL projects, linker-map
aliases and live Frida observations. MCP is an access interface; reproducible
batch exports remain useful. Current read operations should remain read-only;
annotations/renames must be explicit and useful outputs exported. The canonical
DLLs remain pristine, and decompiler types are hypotheses until validated.

Importantly, the pinned local civ6-gamecore-reference already contains published
Linux-derived class layouts and Lua binding data:1915 layout entries,1920 methods
on124 objects,2281 signature entries. This is a published selected reference, not
the full raw109k-function/140k-type corpus described by the other modder. A raw
DWARF import into our current Windows Ghidra database has not been established.
Reference location: Desktop/Codex/csc-native-ai-analysis-20261028/reference/
civ6-gamecore-reference/reference/data/{layouts,lua_methods,lua_signatures,
lua_objects}.json. These JSON files are minified; parse/select records instead
of printing whole matching lines.

## Immediate preflight lesson

The local lua_methods record lua:CityDistricts.GetDistrictByIndex is registered
on gameplay only (Lua::ICityDistricts). GetNumDistricts separately lists ui-cache
and gameplay. The failed shadow reader used both in PlotInfo. The composite
native error does not identify its exact nil callee, but the existing registry
already flags GetDistrictByIndex as an unsupported UI assumption. Consulting it
before launch would have caught that mismatch. Shipped CitySupport's UI Members
traversal is the separate source precedent used by the offline repair; its new
native validation remains pending.

For each future native reader/probe: check object, exact method, registered_on
context, interface, mapped build confidence, argument/return evidence and a
shipped same-context call site before loading. A native C++ method's existence
does not imply a Lua binding or UI availability. Keep missing/ambiguous records
explicit, and require a narrow positive native exposure check for claims of
availability. This is now documented workflow, not an implemented automatic
source linter or a retrospective successful native test.

Use evidence labels with explicit scope: reported, inferred, statically verified
for a named binary/platform, observed natively, and comparative benefit. Upstream
“verified” often means static registration/decompilation, not observed live. Keep
aliases and ICF ambiguity rather than promoting one name to an authoritative ABI.
Windows fields and calling conventions need current-build validation; Linux
layout/prototype information is a lead, not permission to copy offsets.

Practical next tooling increment: a small deterministic lookup/context preflight
over these existing JSON tables, tied to actual probe method inventories. If raw
types or mapping reconstruction are needed later, request the modder's extracted
tables, alias/confidence data and extraction scripts before duplicating them.
No game, download, binary edit, new framework or Ghidra mutation was performed
for this cross-check.
