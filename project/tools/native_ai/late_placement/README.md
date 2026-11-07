# Late district placement trial

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
closed reference named in `--recover-from`. The first cold load is the
control. A second load with `--repair-control <closed control>` derives
one diagnostic floor from the losing Mill offer and the contract that
actually executed. It permits a single forecast write only when the
repair reaches the same update boundary with the expected native value.
The test leaves validation, competition, production and completion to the
game. Its forced comparison is a mechanism test and provides no routine
CSC calibration.
