# Late district placement trial

For a normal-start development run, `ce_bakers_fresh.py` can
capture intermediate chain dependencies with `--census-turns`
followed by up to eight interior turns. The gameplay callback reads
each requested snapshot during autoplay. The endpoint remains
controlled separately. Completed samples are saved as
`chain-census-TURN.txt`. The result records complete, incomplete and
missing samples independently of the Storekeeper turn audit.

Use `--qualification` for the preselected Standard-size games listed in the
[roadmap](../../../docs/civ6-ai/roadmap.md#current-milestone-and-active-problem).
This requires a fresh Online start, `--through 249` and `--saves`. It records
all four intermediate censuses and audits the full interior Storekeeper clock.
The matched Continents control uses `--untuned --matched-source` with the
tuned run's archived `source.json`. The controller checks the initial map,
roster and units and requires matching staged packages before deriving the
control manifest. The per-game retention result counts Quarters with at least
100 confirmed active turns. Keep separate evidence for recovery and comparison
across runs.

For a fresh development diagnosis, `--observe-supplier-at` pauses at
a shared-controller boundary and verifies the scoped Cattle still
lacks its Pasture while the other Bakers links are ready. Supply
`--supplier PLAYER CITY QUARTER PLOT`, `--probe-dependencies` and
`--saves`, then allow 1–15 more turns for observation. The runner
archives the inactive source before attaching the read-only probe.
The report lists the boundary clock as unsampled if the pause
prevented its UI sample. Every other interior clock is required.
Qualification remains continuous.

The Wind Mill opening probe uses `--mill-opening-components` with
`--resume-from` pointing to the verified 105–120 supplier run,
`--wind-mill 4 131073 1423`, `--through 112`, `--saves` and
`--probe-dependencies`. It checks the inactive source and its
package hashes, then removes the exact Rice Farm in the replay
copy and confirms the Rice and Granary remain. The component
observer records the Mill forecast without adding a bid.

Add `--melbourne-builder-offers` and use `--through 116` to
record receipt validation and queue arbitration for the six Australian
cities. `opening-offer-cities.json` maps their IDs. Join the offer IDs in
`wind-mill-trace.json` to `AI_CityBuild.csv` and the job's tree log.
Add `--melbourne-builder-recruitment` to also capture the existing
Builders' controllers and evaluator pools for the exact Rice target.
That mode records other Australian recruitment calls only when they
change a Builder's controller. Both extensions leave native decisions
unchanged after the initial fixture setup.

This trial uses the archived Online turn-1 Mill study checkpoint and its exact
isolated CSC package. The shared controller owns each process and advances it to
turn 2. The experiment targets Delhi's flat inland Bakers site at plot 1210.

The observer records Civ's ordinary aggregation before the trial writer runs.
The writer checks the original caller, city, row, matrix alias, reservation,
eligibility, live score and matched baseline. The two downstream readers
record the winner and plot-specific present value. Native request logs provide
independent evidence of what the city proposed.

The driver runs three arms from the same checkpoint. The baseline establishes
the native values. The pulse lifts the Bakers pair one utility unit (256 Q8)
above the baseline winner. The correction arm uses the native credits
reconciled by `calibrate.py`. Each write arm is limited to one cell and one
calculation. `--reference` reuses a closed, verified baseline and pulse when
running only the correction arm.
The shared controller restores preferences before each normal exit and the
driver retires the temporary package by hash after the final process closes.

The correction preserves Civ's positive raw-building gate. On this plot the
Wind Mill hills benefit is unavailable, and the Water Mill cannot receive the
reciprocal Bakery and Café bonuses. `verify_csc_policy.py` checks the policy in
`Civ Supply Chains/Lua_UI/AI/CSC_AI_QuarterPlacement.lua` against the native ledger
under Lua 5.1. The main mod imports the policy as a library. The trial uses
Frida for native delivery and has an exact saved-world scope.

`ce_replay.py` replays the matched pulse using CE's Lua entries, without a
Frida attachment. Supply the completed correction run as `--proof`. The
`--fixture-carrier` option selects the test DLL through front-end SQL in the
isolated saved mod identity. The shared controller verifies the loaded module,
the starting world, both score paths, native preparation and restoration.

For the November Windows hotfix, run `audit_xp2_hotfix.py` with the earlier
reference DLL and the patched DLL. `driver.py --hotfix-baseline` then observes
the archived turn on patched stock GameCore with zero writes.
`--hotfix-pulse` runs a fresh turn-2 control and the matched one-cell pulse
with Frida. `--hotfix-control` can reuse a closed control whose stock DLL,
save, package, hook sources, trace and result are verified. The writer freezes
after turn 2. The controller then samples
Delhi's exact plot through turn 25, ending earlier if the Quarter completes
or the owner changes. The control comparison ends at turn 2. Later
observations describe what the treated AI did after the pulse. The
calibrated correction and CE replay retain their original build qualification.

## Natural Craftsmanship checkpoint

`scout.py` hosts the isolated Online game without granting unlocks or adding
world fixtures. It records the original AIs' civic selections, reads turns
remaining in gameplay and progress in the UI, and saves one inactive boundary
with a qualified Bakers site. Start checking on turn 5. Candidate timing
requires positive Craftsmanship progress, Code of Laws complete and one to
four turns estimated remaining. `--pilot` can supply archived natural unlock
timing when the native estimates are unavailable.

`natural_bid.py --scout <closed scout directory>` loads the exact save in
stock GameCore and observes one turn with zero writes. With `--search-through`,
it first searches later turns for a free district tree and a fresh selection,
then cold-loads that exact pre-decision save for the control. A distinct
competitor and a fresh score can qualify one diagnostic bid at 256 Q8 above
that winner. The treatment reopens the same save and changes one unreserved
owned cell after aggregation. It checks the original native scores and
observes the native winner before freezing. Both arms retain the native
contract and queue logs. Follow-through samples record the civic unlock,
foundation, district completion and exact supplier separately. All game
actions after the one score change are ordinary AI decisions.

`natural_chain.py --match <closed matched run> --through <turn>` reopens the
completed Quarter for a read-only Mill unlock observation. It records local
geometry, access flags, each Mill's technology, Granary state and the tracked
supplier. A missing gameplay legality getter is recorded as `null`. The run
stops if the tracked supplier is lost. The original Boston continuation found
the Campus on that supplier, which moved protection ahead of Mill delivery.

`natural_bid.py --replay <accepted match> --capture-at <turn>` repeats the
verified Bakers bid and captures an earlier inactive boundary. Use
`supplier_protection.py --replay <closed capture> --through <turn>` to census
all six neighbors and compare two cold loads of that boundary. The control
must reproduce the destructive pair and its loss. The treatment lowers that
one finished score below a safe, positive alternative. It preserves the
native reservation and records the actual choice, supplier and completed
buildings. Its retained checkpoint is available for the Service observation.

`natural_chain.py --continue-from <closed protection run>` follows that
checkpoint and reads actual building yields from the UI alongside gameplay
supplier and Service state. `--guard-farm <closed loss control>` with pinned
`--dependencies` adds the Boston-only diagnostic veto to the two verified
Farm location callers. It preserves the first confirmed Storekeeper chain
at a later independent sample. The final branch stops when that persistence
check succeeds, the tracked supplier is lost, or the supplied turn cap is
reached.

## Building repair contract test

`natural_chain.py --observe-mill-repair` traces one damaged Boston Water
Mill on the exact patched stock DLL. It records receipt and queue
validation, refreshed offer values, the chosen contract, the resulting
building request and actual building output. It uses the shared controller
with no score writes by default.

`--repair-autosave` accepts a preserved autosave listed in its adjacent
`archive.json`. The observed Boston state at that turn must match the
closed reference named in `--recover-from`. Use the late continuation to
see whether a retained Mill contract eventually executes.

`--pillage-mill-from` instead loads a closed operating chain, verifies the
exact healthy state and pillages only the Water Mill once. After that
setup, stock AI owns the queue and repair. The test reports the initial
damage, Mill completion, actual building output and whether Storekeeper
restarts while the original Pasture stays intact.

## Supplier job and recovery evidence

`natural_chain.py --remove-pasture-from <closed operating run>` verifies
the healthy checkpoint, removes the one mapped Pasture, and leaves
the Mill, Granary and Cattle in place. The AI controls all subsequent
production and Builder work. The read-only trace distinguishes the
terrain decision, the ordinary improvement tree slot, and site selection.

Each finite play window archives its fresh autosaves in `decision-saves/`.
The receipt records their checksums and marks missing or older files.
A reload still needs the expected scenario census before play.
`supplier-timeline.json` aligns the trace, tree log, Builder operation
log and inactive Service samples. Native trace records carry the start
of their interval. They have a different time resolution from the game's
turn logs. Player-only Builder log entries stay unattributed unless
other evidence links the unit and plot.

`ce_bakers_supplier.py --wonder --resume-wonder-treatment <closed match>
--through <turn>` can continue the protected turn-222 arm under the same
native capability and main CSC publisher. It verifies the starting census
and stops at a bounded endpoint or after two consecutive operating
samples. This is a continuation of the treatment.

`ce_bakers_supplier.py --builder --pasture-autosave <saved boundary>
--through <turn>` runs both CE arms from the archived decision file.
Supply the closed stock run with `--replay`. Both arms must match its
observed census before advancing. Builder protection is the one changed
capability. The result records the deposit, improvement and actual Service
separately so a successful protection result cannot pass as recovery.
It archives both arms' fresh decision saves and writes joined
`supplier-timeline.json` files after both arms close. Add
`--decision-observer-deps` with the pinned Frida directory to record
native location-selector callers and the exact cached score they see.

With `--pasture-bid`, both arms keep Builder protection and only
treatment adds 8,192 Q8 to Boston's eligible Cattle Pasture forecast.
With `--guard-committed-harvest`, both arms also keep Builder
protection. The exact turn-72 save enables only the Clear Plot
observer, which rejects the first qualifying ready call from the
known harvest Builder in treatment and records subsequent retries
without changing them. Compare the tree logs and final supplier state
to see whether the old job released. These modes are mutually exclusive.

`--publisher-pasture-bid` uses the built CE supplier bid API and the
main CSC publisher in treatment, with ordinary Builder protection
in both arms. The control hides only the optional bid API in this
fixture. This comparison does not attach Frida and also records the
raw native Storekeeper modifiers at each inactive boundary.

`--publisher-harvest` similarly holds score-stage Builder
protection constant and enables only the reusable CE Clear Plot
protection in treatment. It uses the exact turn-72 fixture and
captures the active growth recipients and harvest receipts.

The joined timeline also connects Boston's recorded Builder contract
IDs to their submission, city selection and cancellation logs. A
production request alone does not identify the Builder that did the work.

For a deeper Storekeeper audit, `storekeeper_runtime.lua` can be read
through the shared controller in the `PlotInfo` UI context at an
inactive boundary. It lists the native growth and attachment instances,
their activation, owners and subjects. The end record reports the
sampled turn and number of matching instances, including zero. This
is a diagnostic snapshot. Run `storekeeper_runtime.py <Lua.log>
--players <original AI IDs>` to count only sampled turns with matching
native attachments and active growth recipients. It reports gaps
and checks for missing or conflicting receipts. The paired publisher
replay validated the Boston source and recipient objects. Per-turn
qualification still needs a live-verified sampling clock.

`--wonder-autosave` continues a closed, protected recovery from a
later matching inactive census with the same CE binary. Supply the
original Wonder match and pinned observer dependencies. The Mill
observer reads the ordinary score after the CE call has returned.
