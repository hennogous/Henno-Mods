# Record Quarter quality when the AI commits

Active problems: **1.6 construction follow-through, 1.8 poor-site suppression**;
later supplier losses also concern **2.2 material retention**.

The [completed central-economy game](csc-ai-economy-250-20261113.md) measures
adjacency at the endpoint. That cannot establish whether a Quarter was poorly
placed initially or lost useful neighbors later. A new passive observer records
the missing lifecycle evidence before we adjust policy bands.

## Measurement contract

`project/tools/native_ai/late_placement/quarter_placement_watch.lua` is a
diagnostic reader, installed by the shared controller into the main publisher's
context. It is not another AI policy or a shipped gameplay component. It sends
no bid or order and changes no game properties, score bytes, unlocks or RNG.
The main CSC and CE packages stay byte-identical to the experiment's inputs.

The observer transparently forwards `DistrictBridge.Publish` and remembers only
accepted Quarter entries. Immediately before the next publication resets CE's
journal, it reads the existing bounded journal, preserving:

- The actual Quarter score read back at the native `GetBestDistrict` return.
- The latest preceding complete-score write for that same identity, if seen.
- The current accepted bid and its adjacency estimate, if observed since load.
- Generation, packet version and observation turn. These are different clocks.

A native winner may have a retained plan or an earlier score. A last-write
record is not causal proof that our intervention made it win. Journal ordering
is preserved: a later write in the window is never attributed to an earlier
selection. Existing observations before installation remain unknown.

District events record **foundation** and **completion** separately. Each records
Base/Spec counts, working compatible improvements, six neighbor facts and
nonzero adjacency rule contributions. Production and Gold are yields per turn;
native bids/operands are Q8 utility (256 per utility point), not yield amounts.

`eligibleProduction/Gold` use current rule eligibility and completed customer
districts. They describe geometry, not realised output from a foundation or a
pillaged district. `millForecast*` separately includes one prospective local
Mill, using the same choice as the live planner. Future customer footprints
receive no yield. This distinction prevents an unbuilt Mill from being presented
as current adjacency or a functioning exchange.

Loaded Quarters are labelled `loaded`; ownership changes are separate. A bounded
once-per-turn scan of existing Quarters catches missed events, explicitly
labelled `first-observed`. Neither enters foundation statistics. Event duplicates
are suppressed. Polling never scans new site candidates. A foundation callback
can follow footprint clearing; its accepted bid is the earlier planner estimate,
not a full pre-clear world snapshot.

The journal has CE's existing 16,384-record limit. Reads use pages of64 and do not
increase that capacity. Every diagnostic fault is logged and invalidates the
measurement, while the main policy still publishes normally. This is additional
test overhead, not a production performance measurement.

## First acceptance replay

The shared controller reloads the exact turn150 checkpoint from the completed
250 run and advances to175 with unchanged policy. The intended case is Sinope's
Tailors Quarter, player1/city327684/plot1062: originally requested166/completed171.
Save SHA256:
`e951c015f0d551946fb2a9ea8275db8d202aa7b9ec1129f61221340b753d48a3`.

Artifacts:
`C:/Users/Shadow/Desktop/Codex/csc-ai-placement-time-20261113/replay150-175-01`.
Driver: `quarter_placement_replay.py`; result reader: `placement_watch_results.py`.
The worker owns the console and restores preferences and temporary packages.
This is a saved-game diagnostic, not an additional fresh qualification game.

Sixteen observer/integration checks pass, including duplicate lifecycle events,
transparent publication forwarding, failed observations leaving policy intact,
and preventing a future write from being assigned to a past selection. Initial
live records demonstrate foundation/completion events and actual native operands.

### Completed replay: useful individual records, failed global completeness

The replay reached175, saved and closed with exit0; owners are absent and exact
mod preferences restored. The terminal observer assertion fails because two
turn163 callbacks refer to a district object unavailable to Gameplay. This is
preserved as a failed observation attempt, not silently accepted as complete.
The result reader requires explicit `--partial` and sets
`measurementComplete=false` when extracting its readable records.

The individual, fully emitted records include:

| Identity | Native selection | Published bid | Foundation | Completion |
|---|---:|---:|---|---|
|Sinope Tailors, player1/c327684/plot1062 |444,512 Q8 |−15,437 Q8 |169, +1 |172, +1 |
|Player2/c458757 Tailors/plot2021 |471,871 Q8 |20,909 Q8 |158, +2 |not captured by175 |
|Player3/c524295 Bakers/plot1012 |17,765 Q8 |17,765 Q8 |not captured by175 |not captured by175 |

The Sinope choice occurs in packet17; the journal is drained at167. Foundation
uses a later packet20 whose bid is26,378 Q8, so that foundation's bid must not be
substituted for the earlier decision's bid. The +3 Bakers choice has an exact
preceding complete write in packet22. Both poorer choices have no preceding
complete write observed since load. This demonstrates a concrete discrepancy
at the native reader and a separate case where the reader consumes our exact
value. It does not identify why the poorer row escaped replacement, nor prove
there was no write before150. The replay differs in subsequent timing from the
original game; it is not a deterministic request/completion-time reproduction.

The same packet contains **10 complete writes in Sinope's city** and **20 in
the other Tailors city**, affecting other cells. This narrows the failure:
the capability and city-wide path were active, but these particular winning
cells did not receive their complete value. It does not identify the rejecting
guard. The current native adapter checks row ownership/city, score-pointer
aliasing, valid scores before/after aggregation and an empty reservation ID.
Its reservation guard is stricter than the inspected native selector, which
also admits a row whose old request no longer exists and can compare against a
live reservation's threshold. Reservation and row state at the write boundary
must be measured before relaxing any guard. These are hypotheses, not fixes.

All four captured new foundations are below+3 (two+2, two+1), across original
major AI owners. Therefore at least some low endpoint values reflect initially
weak placement rather than only later supplier destruction. The incomplete
observer prevents treating this as an exhaustive placement census.

The revised reader records unavailable event identities as `DEFERRED` with raw
identity and clock, then lets the next live census identify the surviving
object. It does not fabricate foundation quality. It now seeds city-state
holdings too, distinguishes ownership changes even when native IDs change,
and handles instant completion and rebuilding. Diagnostics still cannot alter
the policy; deferred/first-observed rows remain a reported coverage limit.

### Fresh250 with lifecycle observations

The next normal Small Continents Online game uses the **same frozen639+6 CSC/CE
files**, seeds18461107/29461107 and original AI1–5. Only the read-only observation
code changes. No policy/native binary change is bundled into this measurement.
Shared-controller worker99392; artifacts `.../csc-ai-placement-time-20261113/fresh250`.
Henno subsequently stopped the run at160 and requested REA. It exited0 through
the owning controller, restored preferences/packages and retains a verified150
save. This is an incomplete observation, not a250-turn result. The final native
journal was not drained. The parser now distinguishes fault-free readers from
a completed/drained measurement. [Native reservation mismatch, exact behavior
and stopped-prefix scope](csc-ai-reservation-write-gap-20261113.md).

WildW `develop` was checked again during this investigation and remains
`2986a746b396eb93aad14f9afffb043a09c2c489`. No upstream PR is involved.
