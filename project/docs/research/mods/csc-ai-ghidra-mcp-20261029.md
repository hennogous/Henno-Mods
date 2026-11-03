# GhidraMCP local integration — 29 October 2026

LaurieWired/GhidraMCP is installed and registered as the local Codex MCP server
`ghidra`. It is an interactive access layer over our existing Ghidra analysis,
not a replacement for live Frida observations or an additional game DLL.

## Verified installation

- Upstream: https://github.com/LaurieWired/GhidraMCP
- Pinned commit: `1e980252087b2479a21b9ca6d82d5829538651a7`, package2.0.0.
- Local package: `C:/Users/Shadow/Desktop/Codex/csc-ghidra-mcp-20261029`.
- Isolated Python3.13.13 environment, exact dependencies in `requirements.lock.txt`.
- Extension built against our Ghidra12.2/JDK25.0.5+8. Upstream's README targeted
  12.1.4, so compatibility is established by this local build and smoke test.
- Jar SHA256: `201d18ffde71a83a678eae607de265861f37e5a00b989d91958c1197664d2b43`.
- MCP initialization, enumeration of28 tools, exact program SHA and real
  decompilation at VA`0x1800f97b0` passed. That is the current CanZone target used
  in the foundation investigation. Package version and MCP SDK/server-reported
  version are distinct; retain the raw receipt rather than conflating them.

No Civilization launch or game/installed-mod modification was required. The
canonical Ghidra project was copied only after its headless owner released it.
The canonical project and installation remain separate from MCP operations.

## Use

Call `get_program_info` first and verify current GameCore SHA256
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
Addresses are image virtual addresses; do not pass an RVA as though it were a VA
or use historical linker-map addresses for the current binary. Current preferred
image base is `0x180000000`. Use `search_functions_by_name`, function calls/xrefs,
decompilation/disassembly and bounded memory reads to follow an actual decision.
List queries are paginated. Mapped names and inferred types are not recovered
source contracts, and a static branch does not prove runtime choice or benefit.

The launcher uses stdio, a loopback-only ephemeral backend, explicit local jar,
`--no-analyze` and `--discard`. The snapshot includes the existing analyzed
program; it does not automatically absorb future canonical-project changes.
Refresh only after all relevant project owners exit, preserving provenance.
Mutation tools affect the disposable research session; changes are discarded,
so export useful annotations/findings to durable docs before closing it.

Each MCP client uses a disposable copy of the frozen analysis snapshot and
its own settings/cache/temp directories. Two simultaneous client sessions were
verified. Allow roughly 500 MB temporary project storage per active client;
graceful exit removes the session copy. The 31 October ownership-aware
collector below also removes abandoned copies on subsequent launcher starts
and exits; uncertain ownership is preserved.

## Codex connection and evidence

`C:/Users/Shadow/.codex/config.toml` contains only the added `mcp_servers.ghidra`
table for this setup. Command is the isolated `venv/Scripts/python.exe`, argument
the absolute `launch_mcp.py` path; startup timeout180s, tool timeout120s. All prior
configuration parsed identically after removing this added table. A private
backup and `codex-registration-receipt.json` are retained in the install folder.
Do not copy the full user configuration into the repository.

`codex mcp get ghidra --json` verified enabled registration. Real MCP behavior was
tested using the protocol client. The already-running parent conversation did
not gain a `ghidra` tool in its dynamic inventory immediately after registration;
a fresh/reconnected Codex session may be needed to expose it there. Configuration
and protocol success must not be reported as a tool call from that old session.

Evidence: `install-receipt.json`, `smoke-result.json`, `smoke-stderr.log`,
`requirements.lock.txt`, `README.md` and the registration receipt in the install
folder. Initial PyGhidra startup failed during optional logging-module import;
installing/eager-loading `rich.console` and isolated Ghidra application paths
resolved it without patching upstream source or changing the canonical install.

Related: [symbol resource](csc-ai-gamecore-symbol-resource-20261029.md),
[foundation decision path](csc-ai-foundation-decision-path-20261029.md),
[roadmap](../../integrations/csc-ai-roadmap.md).

Official setup references: [GhidraMCP](https://github.com/LaurieWired/GhidraMCP),
[Codex MCP configuration](https://learn.chatgpt.com/docs/extend/mcp?surface=cli).


### Direct conversation tools verified later on 29 October

The parent conversation now exposes and has successfully called GhidraMCP
get_program_info, function search/list, decompilation, disassembly and call/xref
tools. The current DLL SHA matched the pinned target. The initial inventory
absence above is historical. The foundation follow-through used these tools
read-only; no native game or canonical Ghidra database mutation was needed.


## Disposable-session retention — 31 October 2026

The installed launcher now uses `project/tools/native_ai/session_gc.py` (installed
beside the launcher). Each new session carries a small `session-lease.json` with
the launcher and worker PID plus exact Windows process-creation FILETIME. A live
owner protects a project even before copying finishes; a surviving worker protects
it after its parent dies. PID reuse does not establish ownership.

Startup and shutdown sweep abandoned UUID children of this installation's
`sessions/` only. Managed copies require both exact owners to be absent; older
unmanaged copies require no process references and ten minutes since their latest
file/directory creation or modification. A per-root Windows mutex prevents competing
collectors and releases automatically if its owner dies. Failed process inventory,
uncertain access, malformed leases, an unscoped Ghidra GUI, reparse points or paths
outside that direct-child boundary prevent deletion. Neither `project/` nor the
canonical analysis database is in scope. No scheduled task or background service
was added. Existing clients were left running; the new launcher applies to future
connections.

Normal exit still removes its own copy after its worker exits. Abrupt termination
can leave a temporary copy until the next launcher startup/shutdown. Keep useful
findings in exported files/docs, not disposable `--discard` projects. Keep small
JSON receipts, not archives of abandoned databases. `cleanup-latest.json` is bounded
to the latest sweep; each normal session receipt records its own sweep summaries.

The 31 October cleanup removed 186 abandoned copies (96.44 GiB):
181 from the reviewed manifest, then five more aged legacy copies during the first
automatic sweep. All four original live sessions remained present and referenced;
both frozen template and canonical master project file hashes stayed identical.
One recently created unreferenced legacy copy was conservatively retained by the
grace rule at final verification; a later sweep can collect it when eligible.

Ten focused safety tests passed, including live/reused identities, copy-before-worker,
surviving worker, inventory/access failure and path/reparse guards. Two real MCP
connections both closed with exit0 and removed their session copies. The first
check failed an additional program-hash assertion before saving its raw response;
that missing response is not diagnosed retrospectively. The second independently
enumerated 28 tools and verified the exact current GameCore SHA256. No binary or
project was changed between attempts, and neither launched Civilization.

Evidence: `H/ghidra-session-cleanup/{review-manifest,before-delete,deletion-receipt,
installation-receipt,mcp-smoke-result,final-verification}.json`, first/second smoke
stderr logs and the installed `session-receipts/`. H is the thread output directory
defined in project operating context. Maintain the Python collector as the canonical
automatic implementation; do not run separate legacy cleanup scripts concurrently.
