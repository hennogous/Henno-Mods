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

Thirteen observer/integration checks pass, including duplicate lifecycle events,
transparent publication forwarding, failed observations leaving policy intact,
and preventing a future write from being assigned to a past selection. Initial
live records demonstrate foundation/completion events and actual native operands.
Full replay acceptance, cleanup and case conclusions are pending.

WildW `develop` was checked again during this investigation and remains
`2986a746b396eb93aad14f9afffb043a09c2c489`. No upstream PR is involved.
