# REA offline tooling trial — 30 October 2026

## Decision

REA is a useful supplementary value-tracing and evidence-export tool. This trial
does not justify replacing the prepared GhidraMCP/headless workbench, shared game
controller or Frida observations. It reproduced a known calculation and helped
inspect a concrete, previously unreviewed scripted-target setter. There is no
measured token saving, controlled throughput comparison or new live AI result.

No game was launched. No mod, RH file, original DLL, canonical Ghidra project,
global MCP registration or gameplay setting was edited. No follow-on game,
automation or campaign is dispatched by this result.

## Reproducible setup

All generated material is in
`H/rea-trial-20261030`, where H is this thread's visualization workspace
`C:/Users/Shadow/.codex/visualizations/2026/10/11/01a12a24-6714-7540-8d23-154b092106fe`.
The adjacent `rea_trial_*.py` files are this bounded trial's local drivers, not
a new game controller or a required shipping dependency.

- REA **6.8.0**, official npm archive verified against registry SHA512 integrity.
- Portable Node **24.22.1**, official archive verified against published SHA256.
  The installed system Node24.14.0 did not meet REA's current requirement.
- A readiness check rejected our existing Ghidra12.2: this published REA build
  accepts12.1.x, despite broader current upstream documentation. An isolated
  official **Ghidra12.1.4** copy passed, using existing JDK25.0.5+8. The old
  installation was not downgraded or changed.
- The npm archive had no lockfile. After the initial clean-install refusal,
  runtime dependencies were resolved into the trial directory and the resulting
  package-lock retained. Install scripts, dev dependencies and optional Frida
  were omitted. No global install or agent setup command was run.
- An ad hoc stdio MCP client used REA's actual tool schemas. The default output
  schemas made the229-tool catalog about3.5MB on the wire; output schemas were
  disabled for the actual analysis session. This is configuration overhead,
  not evidence of lower token use than our existing28-tool GhidraMCP.
- Default analysis,4GB JVM heap,900-second startup budget and60-second
  per-function decompile limit. Two caller-supplied labels only; no prototypes,
  old bodies or original symbols imported. Labels are assertions, not discoveries.

The copied current GameCore DLL SHA256 was
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`;
image base `0x180000000`. These addresses apply only to that binary.

## Known control: GetBestBuilding

At RVA`3e4710`, REA recovered the same818-byte body as our existing export.
The negative preference branch uses0.5; the positive branch contains
`SHL R14,9` followed by `SAR R14,8`, reproducing the2x fixed-point multiplier.
The sign tests and cached-value selection agree with the manually reviewed
production analysis and the separately observed producer selection.

This does **not** re-test the upstream SQL parser or establish the private80
signal's marginal benefit. Those conclusions have their own earlier evidence.
Ghidra12.1.4 renders some constants/branches differently from12.2, so readability
differences cannot be attributed to REA alone.

## Unresolved route: scripted target and rally

One bounded value-trace request on Lua wrapper RVA`6c6220` automatically retained
the instance resolver, integer conversion and native setter RVA`4d10a0`, among
six function dossiers. We inspected those retained records after close without
reopening Ghidra. Existing pinned mappings supply the names; REA supplied the
current-build bodies, assembly and dependency records.

Static findings:

1. The wrapper resolves the `AiMilitary` instance from Lua argument1, reads
   operation/target/rally from arguments2/3/4, and forwards them to`4d10a0`.
   The resolver has explicit invalid-instance / dot-versus-colon error handling.
2. The setter uses an operation container on that supplied instance; after the
   `-1` check it checks an ID-derived index and a non-null operation pointer,
   then calls mapped `Operation::SetTargetAndRallyPoints` at`4e1850`.
   This supports the explicit-instance route. It does not validate ID generation,
   correct caller ownership in a running game, economic job support, cancellation
   or reservation release. Cross-AI controls remain necessary.
3. **The setter is not a pure lookup.** A conditional path reads mapped
   `Player::Instance::GetVisibility`(`2f81f0`), calls mapped
   `Visibility::Manager::ChangeVisibilityCount`(`35a7f0`) with+1 for the two
   plots, calls `AI::Targets::UpdateKnowledgeBase`(`515d70`), then changes the
   counts back by-1. This occurs **before** the operation-ID`-1` comparison at
   `4d1300`. The exact visibility-array meaning and any lasting knowledge change
   have not been observed live. Do not use invalid operation IDs as a claimed
   no-effect native probe.

The last finding was checked against assembly and independently decoded PE
relative-call bytes: calls at`4d11e3/4d1235/4d129c/4d12eb` resolve to`35a7f0`,
`4d124d` resolves to`515d70`, and the later compare bytes are`41 83 fd ff`.
This is build-specific static evidence, not a runtime mutation test.

## Utility, limits and cost

| Query | Observed seconds | Result |
|---|---:|---|
| First GetBestBuilding dossier, including cold import/default analysis |347.672| Known calculation reproduced |
| Building value trace |1.219|4 decompilations; partial graph |
| Scripted-target wrapper dossier |0.032|121-byte wrapper |
| Scripted-target value trace |0.593|6 decompilations; native setter included |
| Evidence export / close |0.094 /0.406|12 records, including10 complete function dossiers; cleanup verified |

These are individual local observations, not a benchmark against an equivalently
cold existing toolchain. The export was5,055,237 bytes. The graph queries returned
only the first100 nodes: the known trace reached its2500-node ceiling and reported
3344 total edges; the target trace reported675 nodes/789 edges. Both were explicitly
truncated and reported unresolved indirect calls and missing bindings. The returned
target page included18 derived argument bindings. Counts are graph observations,
not unique gameplay facts or proof of an end-to-end job.

The incremental value is automatic dependency graphs **plus retained callee
dossiers**, which reduced manual retrieval for the setter. The tool did not
automatically interpret visibility semantics, recover missing ownership context,
or prove a job would execute. We still used the existing maps and reviewed code.
Default fresh imports, ephemeral databases, version restrictions and graph noise
are reasons to retain our prepared workbench as the default. Use REA selectively
when cross-function dependency evidence answers a concrete question.

## Closure and evidence

`trial-audit.json` checks body sizes, the known multiplier, binary hashes and eight
PE-decoded direct-call targets. `independent-cleanup.json` verifies the original
Python10164, Node8780 and Java6248 identities absent and REA's private temporary
runtime removed. The copied and original DLL hashes remained equal; no Civ
process was present. Dependencies and portable analysis tools remain isolated for
possible future use, with no automatic registration.

Raw request/response/timing records, complete `evidence-bundle.json`, per-function
extractions, package/runtime download receipts, protocol, dependency lock and
cleanup receipt remain in R. The audit is an evidence consistency check, not
an independent runtime replication of reconstructed logic.

Related: [existing production analysis](csc-ai-native-production-analysis-20261028.md),
[native goal routes](csc-ai-community-native-job-routes-20261030.md),
[roadmap (historical)](https://github.com/hennogous/Henno-Mods/blob/819b67c/project/docs/integrations/csc-ai-roadmap.md).
Upstream: [REA](https://github.com/morluto/rea),
[value tracing](https://github.com/morluto/rea/blob/main/docs/native-investigation.md#bounded-static-traces),
[Windows provider](https://github.com/morluto/rea/blob/main/docs/windows-ghidra-p0.md).

## Installed skill and MCP integration — 1 November 2026

The user explicitly requested all REA skills and MCP registration. The tested
REA6.8.0 package ships one official skill, reverse-engineer-anything: all eight
files, including its supporting guides, are now installed under
`C:/Users/Shadow/.codex/skills/reverse-engineer-anything`.

Codex now has a user-level `[mcp_servers.rea]` entry pointing to the existing
portable Node24.22.1/package entrypoint, Ghidra12.1.4 and JDK25. No additional
runtime or analysis-database copy was created. All prior configuration was
preserved; this changes no game, mod, existing Ghidra MCP, permissions or goal.
Output schemas are disabled to avoid the unnecessary catalog expansion observed
in the trial; all229 tool definitions remain exposed. Ghidra heap4GiB,
provider-startup900s, host-tool1020s and host-startup120s are scoped to REA.

A real MCP initialize/tools-list and target-free binary_session call succeeded
in6.062s, reporting REA6.8.0/229 tools; verification Node exited0 after input
closed. No binary or live game was opened. Codex's own mcp-get also recognizes
the enabled stdio registration. Existing clients need a reconnect/restart to
load the new connection; registration is not proof of hot-loaded tools in a
chat already running. The installed skill is available on a subsequent turn.

Receipts and the private configuration backup are in
`H/rea-integration-20261101`. Do not publish that config backup. The server still
depends on `H/rea-trial-20261030`: retain that runtime folder while registered,
or update the registration before moving/removing it. The earlier trial's
no-global-registration statements remain historical facts for30 October.
