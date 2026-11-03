# Loaded-save native observation control — 28 October 2026

## Result

The uninstrumented and count-only instrumented arms both loaded the same existing
turn-1 save in fresh processes and advanced once to turn 6. Their exported initial
and final gameplay/UI state matches exactly. All 17 closed AI CSV files are
byte-identical, including contract identifiers. This resolves the earlier
fresh-versus-loaded comparison confound for this particular short scenario;
it does not establish universal instrumentation neutrality.

The user handed the game back after manual QA. No new world, CSC/RH tuning,
production order, DLL replacement or mod deployment was used. The existing
vanilla Gathering Storm test save has original human player 0 and actual AI
player 1; autoplay observations retain that distinction.

## Protocol and provenance

Accepted output: `Desktop/Codex/csc-native-trace-control-20261028/run-02`.
The source save in Civ's `Saves/Single` folder has SHA256
`8366470bb4e150cdc58fa039744df62d7e4544967e8d3937031b2d4df75f66e4`.
Native DLL SHA256:
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
The first arm never attached Frida. The second used only the previously reviewed
three count hooks, with checked loaded-module identity and entry fingerprints.
Hooks were enabled after initial census and made inert before endpoint census.
The session remained attached until supported native exit; no detach/unload was
issued. Both arms used the maintained controller's finite 1→6 operation.

Run-01 is preserved separately: its Desktop-path load request was acknowledged,
but Core never became ready. It performed no autoplay, census or Frida attachment.
The load log ended almost immediately; the root cause remains unproven. That
process was reconciled in MainMenu, preferences restored and normally exited.
Run-02 changed to the byte-identical existing native save path, recorded the load
return diagnostically and used phase-aware cleanup. It did not replay prior AI
outcomes from run-01, because none had occurred.

## Independent checks

`independent-audit.json`, its Markdown companion and the process-check receipt
record independently recomputed results:

- Both initial Core/UI exports are equal; both final Core/UI exports are equal.
- Final exports contain 2 cities, 13 units and 1,144 plots. Both cities have a
  positive UI queue with a valid production identity and nonempty Core current
  production. Player/city joins use the pair, since both cities have ID 65536.
- 17 closed AI CSV files match byte-for-byte: 3,326 complete records at turns
  1–5, plus 119 separately reported turn-6 boundary records. No trailing partial
  record was silently accepted, and no contract IDs were normalized.
- CityBuild has 14 records: 8 for actual AI 1 and 6 for original human 0.
  Behavior trees have 1,336 records: 876 and 460 respectively.
- Only AI_UnitEfficiency existed in both loaded-initial1 prefix archives;
  its 138,906 bytes match and are a true prefix of the closed file. The other
  16 AI files were absent at that point. Their complete closed generations were
  compared without invented prefix subtraction.
- Hooks observed 7 CalculateDistrictValues calls, 5 QueueNextBuild calls and
  zero BuildDistrict calls. No saturation or caller/thread overflow occurred.
  The latter is an unexposed function in this window, not evidence it is unused.
- All 48 source pins, 12 dependency pins, 598 installed-package files and 418
  archived-log hashes match. Both native exits and the trace-daemon exit are zero;
  the sole worker exited zero. A subsequent read-only process check found no
  study owners remaining.
- Each native preferences readback restored exactly 145 mod IDs and 148
  subscription/file entries, with AutoStart false. No package overlay occurred.

## Coverage limits and next trace

Snapshots cover exported plots/resources/ownership/improvements, cities,
districts/buildings, unit identity/location/damage/moves, treasuries/research and
combined current-production/UI queues. They do not cover all hidden state,
Builder charges, promotions, pillage state or RNG. Optional unavailable/error
values are retained (122 initial and 840 final entries in the audit's accounting);
equal missing values do not prove production-progress or full-state parity.

The actual AI's ordinary logs offer useful future trace cases: Uruk submitted
Builder contracts 5 and 10 at turn 2 with logged values 74 and 13; contract 5 was
selected at turn 3, then War Cart contract 7 at turn 4. These identities must be
verified anew in any later arm. Original-human Rome's separate Builder contracts
13 and 18 must not be pooled into AI outcomes.

A separate bounded field-reading observer is being prepared for unit-request
initialization, city validation and execution. This control does not certify
that richer observer. Its own endpoints/logs must be compared, all fields require
verified Windows identities and read-error handling, and absent exposure remains
unobserved. No native field-reading result is claimed here.

Related: [first instrumentation probe](csc-ai-native-instrumentation-probe-20261028.md),
[Builder priority consumer](csc-ai-native-builder-priority-20261028.md),
[AI roadmap](../../integrations/csc-ai-roadmap.md).
