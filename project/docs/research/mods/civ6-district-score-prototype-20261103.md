# District score bridge: prototype and bounded trial

3 November 2026. Follow-up to the
[static extension study](civ6-district-score-extension-20261103.md).

The native bridge is now implemented as an experimental Frida/CModule host.
Its isolated Win64 test passed167 checks. Game results are recorded below;
synthetic success alone establishes neither game integration nor AI efficacy.

## What was built

Maintained source: `project/tools/native_ai/district_score_extension/`.
The C callbacks filter candidates before any JavaScript callback and preserve
the ordinary function call, seven arguments and returned output pointer. The
only gameplay write available is a bounded signed32 addition to the pointed
NetValue result, before its ordinary canonical cache store. It never substitutes
an integer for the pointer in RAX.

The first profile is deliberately small: original AI player4, Avignon city655369,
Bakers' Quarter, owned plot3076 at42,41, one+256 Q8 addition maximum. Zero,
invalid sentinel, overflow and sentinel collision remain unchanged. Successful
negative scores are not generically discarded. The target is checked against
the caller, city/plot identities, R12 plot row and native district-admission flags.

Three additional native callbacks observe the city's completed district cache,
GetBestDistrict result and district present value. PresentValueOf's fourth
argument is a nullable **Plot pointer**, not a plot index. GetBestDistrict returns
the district index and writes two int32 coordinates; its -1 return must not cause
a read of an unwritten coordinate result.

The daemon declares an explicitly mutating profile even for its baseline arm.
It installs disabled, starts once after the source gate, freezes before Menu and
retains Frida and CModule references until the exact held native process exits.
Partial installation preserves the freeze interface. No live detach/unload path
is exposed. The active counter drains admitted frames; native exit remains the
final barrier for other intercepted entries.

## Offline verification

`independent-synthetic-01/result.json` records167/167 passing assertions,
normal exit0, no deadline expiry, no Frida error messages and unchanged source
pins. This was actual Win64 native execution in an owned disposable Python host,
using installed Python Frida17.24.3 and TinyCC CModule, without a Civ operation.
The broader91-case independent contract pack was **not** all executed.

| Evidence | What it establishes | Limit |
|---|---|---|
| Seven-argument native caller, pointer identity and score guard bytes | Original called once; output-only modification; argument preservation | The caller is an owned stand-in with the reviewed layout |
|27 independent decision-core cases | Signed arithmetic, zero/sentinel policy and supplied generation/role predicates | Metadata is supplied; this does not prove its native derivation |
|19 invalid native configurations, with prior-policy preservation | Refusal without partial policy publication | One immutable host window, not a native epoch API |
|10 malformed RPC packets | Exact14-int32 packet enforcement | Host interface only |
| Seven R12 admission combinations | Native row flags affect actual callback admission | Synthetic objects |
| Six memory-span checks | Null/unmapped/read-only write rejection and readable/writable acceptance | VirtualQuery does not pin object lifetime |
| Recursion and four joined native workers | Invocation gates remain separate; worker calls complete | No generic live-game unload proof |
| Five cache/best/PV monitor calls | Actual native callback signatures, null plot and no-choice handling | Original numerical functions are stand-ins |

One million out-of-scope native calls completed in274ms; four native workers
completed100,000 calls in15ms. These are synthetic timings, not Civ overhead
measurements. A deliberate output-pointer mismatch latched a fatal flag,
disabled further mutation and refused rearming; the final injected error count1
is expected evidence, not an unexplained passing-run error.

The unmodified source reader also ran in real Lua5.1 with mocked bindings:
six checks passed, covering Gameplay-compatible indexed district enumeration,
hidden sites, human targets, pending assistance, occupancy and wrong ownership.
Daemon lifecycle checks used mocks and do not establish real Frida failure recovery.

REA's Node Frida provider could not start because its package was unavailable.
No target was spawned by that attempt. The existing pinned Python Frida package
provided the native fallback; no dependency installation or configuration change
was made.

## Game protocol

The shared controller owns each session. Each arm permits one exact existing
save load and one250→251 interval, followed by freeze, normal Menu return,
exact settings restoration, supported native exit and unchanged package/save
verification. No new world, forced construction, research grant, queue clearing,
free plot acquisition or assistance-callback removal is part of the protocol.
Current CSC is a declared rebase; it is not a recreation of the October package.

Source SHA256:
`ea818368130273e02e70e31449a6f24a54e34486b8bfa402dd34b62255443e48`.
Windows XP2 DLL SHA256:
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
The loaded PE path, size, timestamp and all four entry fingerprints are checked
before attachment; the current complete installed manifest and controller inputs
are pinned. The source gate verifies original AI identity, map/catalog mapping,
clear owned revealed site, assistance OFF and no pending work.

Baseline mode never writes. Treatment requires a closed baseline with an observed
qualifying nonzero/nonsentinel NetValue result and a fresh target cache record;
its loaded source facts and installed manifest must match. This fixture was
already a natural Bakers choice in the earlier trace, so even successful delivery
would not prove a caused winner switch.

## Game observations

The no-write baseline exposed exactly the intended ordinary candidate. The
treatment then changed that candidate's output once; its original score matched
the baseline. Each arm captured four records in order: NetValue, completed
district cache, best district/site, present value. Each intercepted3,086 calls,
admitted four, retained four and reported zero errors, suppression or unfinished
frames. Baseline wrote zero scores; treatment wrote exactly one and returned to
observation-only mode.

| Boundary | Baseline | Treatment | Difference |
|---|---:|---:|---:|
| Original NetValue, Q8 |119,170|119,170|0|
| Returned pointed score, Q8 |119,170|119,426|+256|
| Completed target cache, Q8 |339,677|339,933|+256|
| Native winner's cached score, Q8 |339,677|339,933|+256|
| Plot-specific present value, Q8 |339,677|339,933|+256|
| New request6478, logged integer value |1,326.0|1,327.0|+1.0|

Both winners were Bakers index36 at plot3076 (42,41). Baseline cache/PV was
1,326.86328125 utility; treatment was1,327.86328125. Both native behavior-tree
and CityBuild logs carried the corresponding truncated request value. The
observed downstream increment was+256, with no net amplification here; the
static possible1.5 preference branch is not a universal multiplier to assume.

Both arms closed normally, restored all145 mod-ID preferences/148 installed
entries and the saved autostart flag, retained the hook daemon until native exit,
and verified exit0, no remaining owner and unchanged632-file installed package
and original save. Their source facts, source pins, dependency pins and installed
manifests matched. Each daemon reported no diagnostic fault and remained until
native exit; final owner inventories were empty.

Independent log comparison found all142 CityBuild rows equal except request6478's
value at line121. All8,746 behavior-tree rows were equal except the matching
DecodeTrigger value (line6475) and accepted request value (line6498). All72
production-queue rows were identical. The before/after snapshot documents were
also equal across arms. This is a narrow one-turn contrast, not a general
instrumentation-neutrality or stability benchmark.

This demonstrates delivery through ordinary scoring into a new native request.
It does **not** demonstrate a changed winner: the target already won the
baseline. At boundary251 it was still an unbuilt Quarter and the city was
producing Send Aid. Construction, chain completion and empire benefit remain
unmeasured. Request value is not interchangeable with request priority.

## Interpretation and remaining work

The prototype implements a fixed single-entry numeric bridge. A useful authoring
layer could later prepare nonlinear material/customer/empire incentives from
copied state, but arbitrary policy authoring, Lua publication and economic
calibration are not implemented here.

Session/epoch/version are host labels for **one single-load window**. The C
callback does not independently observe native analysis generations. No
cross-load refresh, saved-policy lifecycle, multi-city policy replacement,
shipping loader, CE binary compatibility or general detour-unload mechanism is
established. Memory-region checks do not solve lifetime races.

Disabling the hook is not rollback: caches and requests can retain influence,
and treated autosaves must not become clean references. One allowed adjustment
can also be superseded by another fresh native evaluation. Interpret the actual
ordered trace rather than assuming a constant whole-pass treatment.

## Evidence package

Working evidence:
`C:/Users/Shadow/.codex/visualizations/2026/11/01/01a19677-29cc-7ba1-b183-955ff5f83acd/csc-district-extension-prototype-20261103/`.
The final reviewed package is copied to
`C:/Users/Shadow/Desktop/Codex/csc-district-extension-prototype-20261103/`.
Large native binaries, save files and dependency packages remain referenced by
identity rather than redistributed with the public handbook.
