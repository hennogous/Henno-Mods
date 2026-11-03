# First native AI instrumentation probe — 28 October 2026

## Decision

The companion GameCore/Frida tools can observe mapped native AI entrypoints on
Shadow's installed build. This is a successful **instrumentation feasibility**
probe, not a verified scoring explanation or an AI-tuning result. A production
decision trace is now a practical next research route.

Instrumentation neutrality is **not established**: the production-choice log
matches exactly, but other AI values differ between the fresh and reloaded
executions. A future comparison must use loaded-save versus loaded-save arms
and capture both endpoint censuses successfully. Do not explain away the
differences as caching, randomness or Frida effects without isolating the cause.

## Scope and provenance

- One fresh, disposable vanilla Gathering Storm world, with official expansion
  content and no unofficial mods enabled. Duel/Pangaea, Online/Prince, Trajan0
  and Gilgamesh1, no city states; game seed281028/map seed281029.
- Uninstrumented initial1→6, then **one** instrumented replay of the same exact
  initial1→6. No new host, replacement world or repeated baseline.
- Both finite advances used the maintained FullGameController; no computer use,
  forced city production, grants, actor takeover or SQL tuning changes.
- No replacement CE/DevCE GameCore was installed. This uses the associated
  reverse-engineering mapping and a minimal Frida observation script.
- Steam build15296837. Native DLL SHA256
  `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`,
  PE timestamp`0x667c6f5b`, image size`0xc60000`.
- Reference mapping commit`7ddecbafa37b8d4598831f61ebc73538fd9fd987`;
  DevCE fingerprint-reference commit`6eb7ef180b36c4517e96791279f9166ceb738c45`.
- Frida17.24.3 installed only in the probe's isolated dependency folder. The
  upstream tooling documents tests with17.19; that is not our runtime version.
- Exact initial save SHA256
  `8366470bb4e150cdc58fa039744df62d7e4544967e8d3937031b2d4df75f66e4`.
  All exported initial state matched after load:1,144 plots, units, treasuries,
  research and roles. Hidden simulation/RNG identity was not observed.

## What we observed

| Mapped native entrypoint | RVA | Observed calls |
|---|---|---:|
| `AI::CityBuild::CalculateDistrictValues` | `0x3dfee0` | 7 |
| `AI::CityBuild::QueueNextBuild` | `0x3e8190` | 5 |
| `AI::CityBuild::BuildDistrict` | `0x3df220` | 0 |

All12 calls were on thread9324 in this process. This thread ID is run-specific.
No count cap or caller/thread-map overflow occurred. The counting window was
approximately12.05seconds, enclosing the finite advance and boundary checks;
it is not a controlled timing benchmark.

Each hook validated the original32-byte target fingerprint in the loaded native
module before installation. Hooks started disabled, were enabled once, and
were made inert before the final census. They did not read candidate arguments,
dereference game objects, call native functions, change arguments/returns or
override decisions. Hook installation itself changes executable code and can
affect timing; an observation-only callback is not proof of non-perturbation.

Observed return addresses were checked independently against direct `E8` call
instructions in the exact installed DLL:

| Mapped caller | Return RVA | Direct target | Calls |
|---|---|---|---:|
| `CityBuild::DoTurnActivate` | `0x3e2941` | `CalculateDistrictValues` | 7 |
| `CityBuild::DoTurn` | `0x3e278a` | `QueueNextBuild` | 2 |
| `CityBuild::DoTurnActivate` | `0x3e2a2b` | `QueueNextBuild` | 3 |

Caller names use the published unique mappings and recorded function ranges;
the relative call destinations were verified directly from current DLL bytes.
This establishes observed call edges, not the full decision algorithm. There is
no per-player/city attribution or verified C++ argument interpretation yet.
`BuildDistrict=0` is absence of exposure in this early window, not a broken hook
or evidence that the function is unused generally.

## Comparison and limitations

The14 production-log records in `AI_CityBuild.csv` are byte-identical between
the runs, including Scout selections and later Builder/War Cart contracts.
That is bounded evidence of aligned production choices.

Broader logs are not identical:

- Behavior trees contain1,336 records in each run. Rome's Holy Site trigger value
  is87 in the control and83 in the traced run at turns4/5. Player1's876 behavior
  records match in the separately recorded per-player comparison.
- The control includes three player0 turn1 strategy-following records absent
  from the reloaded trace. They cannot be fabricated or silently discarded.
- Player0 Astrology valuation/contract records also differ. The supplemental
  per-player report includes the final turn6 boundary:227.3→223.3 and87→83.
- `POLICY_REVELATION` valuation differs15→3 for both major players in the
  supplemental policy comparison. These are real observed differences, even
  though production selections in this small window match.

The independent raw log comparison accepts turn1..5 records without rewriting
contract IDs. The supplemental per-player comparison includes1..6, trims CSV
fields and normalizes numeric contract IDs; its scope/normalization is explicit.
Do not mix their row counts without checking those boundaries.

The baseline reached native6 with three inactive/local0/human readbacks, but
its final census failed because `BuildQueue:GetSize` is unavailable in gameplay
Lua. It closed normally before Frida was attached. The control was **not replayed
to repair reporting**. Its original logs were preserved before the traced leg.
Consequently full final physical parity remains **UNOBSERVED**.

The trace's corrected collector records unavailable gameplay APIs explicitly
and reads queue details in UI separately. UI also reported6 and inactive.
It captured2 cities,13 units and1,144 plots, but those cannot substitute for the
missing control census. Gameplay/UI methods are not interchangeable:
`CurrentlyBuilding` was available in gameplay, whereas queue size/entries and
several progress getters required UI or remained unavailable.

## Lifecycle and restoration

Steam initially handed off a short-lived bootstrap process to its actual game
process (bootstrap exit53). This happened before any native command/preferences
mutation. The exact successor was reconciled; no second world was hosted.
The continuation records the same handoff explicitly at launch.

The Frida session was retained until supported Menu→ExitOK closure terminated
the game. No explicit detach/unload was issued. Its terminal detachment event
was `process-terminated` with native_alive=false. Native and daemon exit codes
were both0. Independently verified: all Civ/FireTuner/trace owners absent;
145 mod IDs/148 per-subscription entries and autostart=false restored through
actual native readback;31 executed source pins and12 dependency files unchanged.
No CSC/RH installation overlay, art rollback, tuning changes or automation was
created. Pre-existing unrelated work remains outside this probe.

## How this changes the next investigation

1. Establish a loaded-versus-loaded control, including hidden initialization
   exposure where observable, before attributing score changes to hooks or tuning.
2. Trace `QueueNextBuild` and its candidate-evaluation callers at a small mature
   city boundary. First validate city/candidate identity and Windows layouts;
   do not infer them from names or Linux signatures.
3. Only then record score components and connect a specific SQL input to its
   native consumer. Preserve native choices and add no production overrides.

The reference index matches some Linux signatures by qualified name and can
collapse overloads. `PresentValueOf`'s four overloads were deliberately excluded
from this first probe. Correct addresses alone do not establish their ABI.

## Evidence and reuse

Output root: `C:/Users/Shadow/Desktop/Codex/csc-ce-ai-tooling-probe-20261028`.
The root preserves failed baseline collector/bootstrap evidence and the exact
initial save. `trace-continuation/` contains the accepted tracing scripts,
archived sources/dependencies, raw logs, `trace-counts.json`,
`initial-parity.json`, `caller-evidence.json`, `player-log-comparison.json`,
`independent-audit.json`, and native cleanup/restoration receipts.

These scripts are a build-pinned lab prototype, not a general production
controller replacement. Reuse the maintained controller for native ownership,
transport and finite advancement. Keep thread-specific tracing outside shipping
CSC and do not enable multiple competing native clients.

Sources:
- [Pinned GameCore mapping](https://github.com/cru121/civ6-gamecore-reference/blob/7ddecbafa37b8d4598831f61ebc73538fd9fd987/data/old_to_new_offsets.tsv)
- [Frida lifecycle lessons](https://github.com/cru121/civ6-gamecore-reference/blob/7ddecbafa37b8d4598831f61ebc73538fd9fd987/tools/frida-live/LESSONS.md)
- [DevCE build fingerprint](https://github.com/cru121/civ6-dev-ce/blob/6eb7ef180b36c4517e96791279f9166ceb738c45/DevBridge.cpp)

## Follow-up: loaded-versus-loaded control

The [subsequent loaded control](csc-ai-native-loaded-control-20261028.md) completed
with identical exported endpoints and all 17 closed AI CSV files byte-identical.
It removes the fresh/load mismatch for that bounded pair; it does not revise this
first probe's missing baseline endpoint or differing logs, and it does not prove
general or richer-observer neutrality.
