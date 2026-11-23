# Problem 3 material job follow-through

## Exact job pricing in CSC

The first implementation uses the loaded material transaction definitions and
the native yield price to compare legal build or repair options. It counts what
the job adds to an operating buyer and an observed worked tile. Deposit
adjacency is already present. A worked-tile return loses its bid contribution
when staffing is unknown. Replacing an existing improvement subtracts its
already-active transaction legs. The native quote starts at the five-turn
work allowance used by the economic model. The existing +26 and +56 fallback
bands remain available when live pricing is unavailable or below the band.

Each Quarter proposes one exact job for its missing material class. Separate
Quarter buyers can add genuine benefits to the same improvement. The fallback
band is shared, and the combined bid stays within the CE packet's advertised
limit. Other compatible improvements remain legal as supplier protection
entries. Their native valuations stay intact. The only change to shipping
policy is in main CSC's Lua. The 159 economy and 19 CE front-end tests pass.

## Fractal repair replay

Both arms replay the original Online Fractal turn-150 checkpoint through
turn 183. The candidate package changes only the three CSC Lua files for
material work. The stock AI, options, CE, other mods and save match. Wheat 925
at (37, 12) serves Bakers Quarters 926 and 924.
Tenochtitlan owns the Wheat and its Storekeeper works at turn 150. The Farm is
pillaged at 156 and the Service turns off. The other Quarter shares the
deposit; only working buyers contribute to each native quote.

The candidate's first live direct quote is 16,796 Q8 (65.61 utility) for
Tenochtitlan's Bakers, capped to the current CE maximum of 16,384 Q8 (+64).
On observed turns when the plot is unworked, only the producer input is valued
at 6,544 Q8 and the ordinary +56 floor applies. The candidate raises the native
repair request from 147 to 155. Both arms record a completed Builder request
on turn 174. Angkor Thom's earlier Sheep case lost job admission, while this
case reaches a Farm reservation and still fails to put a Builder on it. Both
arms end at turn 183 with the Farm pillaged and Storekeeper inactive.

Mycenae provides a positive supplier case in the same replay. The candidate
opens the Pasture at Sheep 2546 (30, 34) on turn 161 with native value 155
and finds a Builder. The control first reserves that plot on turn 163.
Both arms build the Pasture on 169. The candidate's exact unit-operation
log records Builder 6225939 submitting Build Improvement on that turn.
The replay shows earlier selection and a completed job in the candidate.
Both arms take until the same turn to finish.
The controller reloaded the retained candidate turn-183 autosave and advanced
zero turns. It read an unpillaged Pasture on owned Sheep 2546, the exact
completed Textile Workshop in Quarter 2620, and a working Base entry on that
plot from the shipping supplier reader. This verifies physical follow-through
for the candidate in a case with a usable Builder.

The CSC publisher reports 32 samples on turns 151–182. Its average/maximum
time is 3.219/5.000 seconds in the control and 3.469/4.000 seconds in the
candidate. This coarse-timed replay includes diagnostics and scheduling
variation. Use a same-state timing test to isolate the pricing cost.

## Builder request handoff

The shipped improvement tree tries Find Available Unit before it checks a
pending native Builder request. A completed request can return success and
advance the tree to Protect Unit without recruiting one. The tree can fail
and drop the repair reservation in that update. The stock replay switches to a
Ski Resort on turn 175. A new native job can therefore win after a valuable
repair loses its reservation.

In the matching Windows XP2 binary, `UnitRequestContract::UnitCreated` checks
unit type, the required city (or -1), and contract state. It can mark several
matching requests complete for one new Builder. Where the contract requests
control, it assigns one controller to the unit. Completion receipts therefore
need a separate unit-assignment check.

The Ghidra reference SHA starts with `324c51e9`. The relevant spans of the
contract decorator (RVA `559670`), its per-contract check (`55a030`), the
completion notification (`3f9fa0`) and worker search (`554b10`) match the
installed `092abfbb` binary byte for byte. Native receipts and paired endpoint
state qualify any later handoff result separately.

Both initial handoff preflights closed without advancing. Runtime inspection
found an existing detour at the per-contract helper in the installed setup.
The revised diagnostic observes the verified direct call at `5598d1` and
leaves the callee's existing hook in place. The intervention is scoped to
the exact Fractal Farm request and permits a single additional worker search
after a completed contract. It adds no production bid or unit operation.

The two arms ran from the same verified turn-169 save through turn 185.
Contract 3389 returned success on turn 174 in the control. The treatment
changed that return to Running exactly once, then the same contract returned
success on 175 after another native worker search. The next job, a Ski Resort,
moved from 175 to 176. Both arms reached 185 with the Wheat still pillaged and
Storekeeper inactive. Keeping a completed request's job open one more turn
is therefore insufficient for this observed shortage. The handoff adjustment
remains diagnostic. Problem 3.2 needs an available, reachable worker or an
earlier competing production request.

Artifacts are under `Desktop/Codex/csc-ai-material-development-20261118`.
