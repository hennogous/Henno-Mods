# Packaged CE policy parity

This developer package moves the current `csc-adjacency-policy-v2` decisions
from Python into gameplay Lua. It contains no native binary, Python worker or
Frida dependency. Its manifest depends on the isolated CE fork test package,
CSC and Gathering Storm. It is not installed or enabled by building it.

`policy.lua` ports the current Python shortlist without changing its policy:
one highest-total Bakers/Tailors pair per city at Production+Gold >=4 receives
+1048576 Q8; every observed legal pair below4 receives the graded capped
negative priority. Supply resources prevent promotion. These are research
priorities, not monetary valuations. Other sites remain selectable.

`build.py --output <fresh output directory>` copies the maintained shared
scanner byte-for-byte and records its hash. The only shared scanner change is
a backward-compatible return of its existing observation table. The script
includes CSC's imported `CSC_AdjacencyCore` in its own context and calls its
read-only rule initialization. It never includes the gameplay property writer.
The scanner retains cached radius3 geometry, per-turn live adjacency evaluation,
the selected planned first Mill, river rules, founded-type exclusion and current
legal owned-site scope. Future/unowned sites remain outside this policy.

The native capability and trace paging must be present in the CE fork. Ordinary
CE1.3 is insufficient and fails closed. Its isolated test dependency GUID is
`d0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a06`; the policy package GUID ends `2a07`.

## Runtime and audit surface

Gameplay context: `CSC_CE_Policy`.

- `CSC_CE_PolicyStatus()` returns turn/version, original AI identities,
  disabled/failed/reason, latest full scanner snapshot and plan, and native status
  as a JSON string.
- `CSC_CE_PolicyReport()` prints that same table as `CSC_CE_POLICY_STATE=<JSON>`.
- `CSC_CE_PolicyDisable()` returns native disable success and permanently suspends
  automatic publication until the next game context is loaded.
- `GameConfiguration.GetValue('CSC_CE_POLICY_MODE')`: nil or `v2` enables the
  unchanged policy. `off` initializes identities and records native reset state
  but publishes no policy. Other values fail closed.

Original-human flags are captured before autoplay and saved as Game properties.
An unmarked loaded game after turn1 is rejected rather than inferring the old
human from changed autoplay roles. New and loaded contexts record native status
before the first publication. Their policy versions restart from native status.

Startup and `OnGameTurnStarted`/`LoadScreenClose` refresh once per new turn.
This event-driven timing differs from the Python controller's inactive-boundary
publication. Native changes must be measured; matching decision arithmetic does
not establish identical intervention timing or whole-analysis-pass atomicity.
At turn100 the script records the final scan/plan and disables without publishing
it, matching the old test endpoint. Every later event leaves it disabled.

Before replacing a policy, the script disables the old generation, then dumps
the now-stable native trace in pages. Suppressed in-flight invocations may still
finish native work; they cannot later write or append records for the old policy.
Trace records retain their original generation, while the page envelope names
the frozen journal's current generation. A publication clears the previous trace.
The Lua log therefore preserves it before replacement. Activation receipts keep
cheap native counters rather than duplicating the full trace each time.

Log markers: `CSC_AI_ADJACENCY_SCAN` (historical scanner print),
`CSC_CE_POLICY_IDENTITIES`, `CSC_CE_POLICY_PLAN`, `CSC_CE_POLICY_NATIVE`,
`CSC_CE_POLICY_TRACE`, `CSC_CE_POLICY_STOP`, `CSC_CE_POLICY_TRACE_FAILURE`, and
explicit `CSC_CE_POLICY_STATE` reports. The controller archives logs, clocks,
source pins and cleanup independently. No package function launches or controls
autoplay or issues build orders.

### Disk log framing

The first live CE run exposed two independent transport limits. Civ's Lua.log
caps each printed line at2047 bytes, while the native HKS `pushfstring` formatter
truncated a long JSON status at511 bytes. The CE module must use a length-aware
string push; Lua framing alone cannot reconstruct already-truncated native data.

Every autonomous receipt now uses a shared emitter. Short JSON payloads retain
their normal marker. Larger payloads use `CSC_CE_POLICY_CHUNK` frames containing
`schema=1`, `epoch`, `seq`, `kind`, `part`, `parts`, `bytes`, `sum32`,
`encoding="hex"`, and `data`. Each frame carries at most512 original bytes as
1024 hex characters, with the complete printed frame bounded to1600 bytes.
`part` is one-based. `epoch` records the native generation and game turn seen at
this context's first status query; `seq` increases per logical receipt. `sum32`
is the sum of original bytes modulo2^32, an integrity check rather than a hash.
Reassembly must require consistent framing, ordered complete parts, exact byte
length/checksum, valid UTF-8 and valid JSON. Do not silently skip damaged frames.

`SCAN` is an additional complete snapshot receipt emitted by the orchestrator;
the shared scanner's old direct print remains byte-identical and can truncate.
Explicit `STATE` queries retain their full direct Tuner reply, which is not
subject to the disk-line limit. Analyze autonomous receipts from chunked
SCAN/PLAN/NATIVE/TRACE rather than relying on the truncated disk STATE copy.

## Offline checks

Set `PYTHONPATH` to the existing Lupa directory, then run:

```text
python -B -m unittest discover -s project/tools/ai_workshop_bridge/ce_policy -p test_policy.py -v
```

The actual Lua is compared with the actual current Python shortlist on
source-hashed captured subsets, threshold/fractional/tie cases, randomized
multi-city pairs and the4096-entry boundary. Lifecycle fixtures exercise original
identity capture, saved-identity reconstruction, reset/off/disable, failure,
trace pagination and endpoint behavior. Fixtures establish those contracts, not
live CE behavior or AI quality. Shared scanner tests remain maintained alongside
the scanner.
