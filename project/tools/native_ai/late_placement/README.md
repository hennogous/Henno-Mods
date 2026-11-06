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
the archived turn on patched stock GameCore. This mode uses its own control
and records zero writes. The historical treatment runner and CE replay retain
their original build qualification.
