# Ghidra session storage cleanup — 31 October 2026

Human authorized deletion of abandoned copies, preserving active sessions/master,
and requested preventing further archive growth. Read-only inventory had grown
from the earlier 176 estimate to 190 directories: 181 eligible, four live, five
recent. Deleted exactly the 181 reviewed candidates (94.05 GiB), then the installed
automatic startup sweep collected the five now-aged legacy copies (2.39 GiB).
Final total: 186 copies / 96.44 GiB.

Both master/template trees byte-identical; original four worker-backed sessions
preserved and still referenced. A further recent unmanaged copy remains protected
by the grace rule. Normal cleanup receipts were missing for the abandoned copies;
the old launcher only removed them in `finally`, so abrupt termination could bypass
cleanup. No assertion about the external termination cause.

Installed new launcher/session_gc helper with per-process creation-time leases,
startup/shutdown orphan sweeps, Windows mutex and strict resolved-root/reparse
guards. Ten safety tests passed. Both real MCP sessions exited0 and removed their
own clone; second smoke passed exact program SHA and 28-tool enumeration. First
additional SHA assertion failed without raw response retention, so no cause claimed.
Small old-launcher backup only; no duplicated database archive or new service/task.

Durable rules: project/docs/research/mods/csc-ai-ghidra-mcp-20261029.md.
Exact evidence H/ghidra-session-cleanup/final-verification.json plus linked receipts.
No Civ/game/settings or AI policy touched. No new game/automation/goal/commit/push;
unrelated art/source work preserved. Future starts use new cleanup; existing four
clients retain their original in-memory launcher until they exit naturally.
