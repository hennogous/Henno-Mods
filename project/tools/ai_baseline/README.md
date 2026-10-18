# CSC natural autoplay baseline

## AI tuning trial

See [AI tuning v1](../../docs/integrations/csc-ai-tuning.md). `tuning_trial.py` subclasses the paired controller with distinct saves/output and native UI smoke checks. The observer/original baseline remain unchanged. `deploy_ai.py` installs only its allowed AI/UI delta with SDK-generated manifest/backups.

The [first completed trial](../../docs/research/mods/csc-ai-tuning-v1-20261017.md) retains the natural endpoint separately from the settled final-save state. `placement_probe.lua` reads completed and prospective native yields only after archiving. `analyze_tuning.py --trial <trial-root> --baseline <baseline-root> --map 1` writes the comparison/CSVs without connecting to Civ. Its adjacency probe is not a complete AI score and cannot determine prospective material recognition by itself.

```powershell
python project/tools/ai_baseline/tuning_trial.py --output '<Codex outputs>/csc-ai-placement-v1-20261017/trial' --captures '<Codex outputs>/csc-implemented-native-20261016' --baseline '<Codex outputs>/csc-ai-paired-standard-20261016' --map 1
```

## Paired Online baseline (16 October 2026)

`paired_standard.py` runs ten games to turn 250: five vanilla Standard, followed
by five with Truly Abundant Resources enabled and the same vanilla Standard
setting. It uses the exact five seed/leader pairs from the implemented-Quarter
native map study, Online speed, Prince, CSC v3 assistance, six majors and nine
city states. The first five initial maps must match those captures tile-for-tile.
The TAR group enables the mod without selecting its Truly Abundant preset.

```powershell
python project/tools/ai_baseline/paired_standard.py --output '<Codex outputs>/csc-ai-paired-standard-20261016' --captures '<Codex outputs>/csc-implemented-native-20261016'
python project/tools/ai_baseline/paired_standard.py --output '<Codex outputs>/csc-ai-paired-standard-20261016' --captures '<Codex outputs>/csc-implemented-native-20261016' --verify-only
python project/tools/ai_baseline/paired_analysis.py --output '<Codex outputs>/csc-ai-paired-standard-20261016'
```

The v3 read-only recorder (`paired_observer.lua`) explicitly enumerates six
native neighbour directions, fixing boundary truncation in the earlier observer.
It retains placement-time owned alternatives, improvements, sales-district
decisions, service flags, buildings and research. Each game runs continuously
from turn 1 to 250; read-only checkpoints are frozen in memory every 25 turns
and exported afterwards. This avoids returning a human player at intermediate
checkpoints, which can open pending human diplomacy sessions. Initial and final
saves are retained. A native PlayerDefeat handler and idempotent controller
polling keep autoplay's return player set to a surviving major, avoiding the
historical overrun when the initial return player was eliminated.
A playback watchdog releases visible disaster/diplomacy UI in observer mode,
without submitting diplomatic responses. A frozen native diplomacy session in
the initial checkpoint-controller trial was excluded and the world restarted.
Final-save preparation also closes visible playback after control returns at
250. The first-activation benchmark census remains intact; a separate
`save-state-turn-250.json` records the settled state before serialization.
Automatic city growth can finish during that same turn without an AI action or
turn advance. Game 6 documents one capital growing 10→11 after a disaster popup
was dismissed; its Quarter, plot, research, Service and event data were unchanged.
Installed gameplay and controller/TAR source hashes are pinned. Original mod
preferences and auto-start are restored after the batch. `--resume-current
--first N` resumes a paused live checkpoint only while its observer survives;
it does not load a save or reconstruct a lost event history. `--resume-running`
reconnects to still-active continuous autoplay without changing its remaining
turn count, retaining all in-memory checkpoints. Read-only console polls and
exports retry safely when the native simulation is busy. `--resume-blocked`
is only for a separately diagnosed frozen checkpoint with autoplay still active.
`--resume-map --first N` continues an already generated turn-one map whose
observer has not yet been injected; its saved setup and enabled-mod list must
already exist in the output.

The original five-game Standard-speed study below remains historical evidence.

The original five-game study used CSC with the standard game AI and ended
at turn 200. Games 1–3 were later continued to 400; the user cancelled further
advancement for games 4–5. Game 3's recovered endpoint has a documented event
history gap from 375–400. The original runner
uses the existing native FireTuner transport and native frontend setup APIs.
It requires Civ at the main menu and an installed current CSC build. Close the
FireTuner GUI first: the game accepts only one tuner client. Do not run another
native QA process concurrently.

```powershell
python project/tools/ai_baseline/run.py --output 'C:\Users\Shadow\Desktop\Codex\csc-ai-baseline-20261015'
python project/tools/ai_baseline/capture_reference.py --output 'C:\Users\Shadow\Desktop\Codex\csc-ai-baseline-20261015\mechanics-reference.json'
python project/tools/ai_baseline/analyze.py --output 'C:\Users\Shadow\Desktop\Codex\csc-ai-baseline-20261015'
python project/tools/ai_baseline/verify.py --output 'C:\Users\Shadow\Desktop\Codex\csc-ai-baseline-20261015'
```

## Turn 400 continuation

`continue_saved.py` loads each archived turn-200 save, checks its checksum and
verifies that the reloaded cities and plots exactly match the original snapshot.
It checks the original installed-file hashes before starting. Use a separate
output folder so the original archive remains intact:

```powershell
python project/tools/ai_baseline/continue_saved.py --source 'C:\Users\Shadow\Desktop\Codex\csc-ai-baseline-20261015' --output 'C:\Users\Shadow\Desktop\Codex\csc-ai-baseline-turn400-20261016'
python project/tools/ai_baseline/analyze.py --output 'C:\Users\Shadow\Desktop\Codex\csc-ai-baseline-turn400-20261016' --turn 400
python project/tools/ai_baseline/longitudinal.py --output 'C:\Users\Shadow\Desktop\Codex\csc-ai-baseline-turn400-20261016'
python project/tools/ai_baseline/verify.py --output 'C:\Users\Shadow\Desktop\Codex\csc-ai-baseline-turn400-20261016' --turn 400
```

The read-only observer is re-injected after loading; Lua recorder memory does
not persist in saves. Each new snapshot includes the original turn-200 event
prefix plus events recorded after reload. The copied original snapshots remain
byte-identical. New checkpoints are 225, 250, 275, 300, 325, 350, 375 and 400.
Verification checks snapshot coverage, event prefixes, reload identity, save
checksums, observer identity, SQL logs and unchanged installed files.

`longitudinal.py` exports endpoint comparisons, placement decisions separated
before/from turn 200, building progression and Service civic exposure. Research
timestamps are bounded by snapshots; building readiness is observed at those
snapshots and does not include affordability or every production restriction.

Capture the reference while a baseline game is loaded. Generated evidence belongs
in the explicit output folder. The source scripts do not write into mod content,
the game install, or the mod discovery database.

## Setup and evidence

The original setup uses Continents.lua on a Small map, six major civilizations, nine city states,
Standard speed and Prince difficulty. Map seed is `830001 + game*101`; game seed
is `940001 + game*103`, for games 1 through 5. Actual leader rosters and map
dimensions are retained. Standard victory conditions remain available. Turn 200
means the beginning of turn 200 after 199 advances from turn 1.

The runner preserves mod preferences and native auto-start, enables CSC and
official content, and restores preferences at the final main menu. It never
creates a controlled world, grants content, forces adjacency refreshes, writes
gameplay properties, or adjusts AI priorities. The observer only reads state and
stores records in its own Lua memory. All civilizations, including player 0,
play through native autoplay.

Snapshots at turns 1, 25, 50, 75, 100, 125, 150, 175 and 200 record major players,
cities, research, districts/buildings, relevant source properties, material
adjacency and owned/resource plots. Event records retain district placements and
improvement creation. A completed final save, logs, command transcripts and
installed gameplay file hashes provide audit evidence.

## Resume and interpretation

The runner stops on failed observations. Inspect `batch.json`, command evidence
and live state before resuming. Do not replay setup or other mutations blindly.
If the correct game and observer remain loaded with inactive autoplay, resume
with `--resume-current --first N --last 5`. The runner tolerates the native delay
between autoplay becoming inactive and its final turn-counter tick. Cleanup at
the main menu is available with `--restore-only`.

Autoplay returns to the first surviving major player. Returning to an eliminated
player can leave an observer-only game advancing after autoplay reports inactive.
In the 15 October batch this occurred in game 5: the recovered intermediate
snapshot is correctly labelled turn 126 rather than 125, with the exception in
`checkpoint-exceptions.json`. Final endpoints are independently checked at 200.

Only folders with `complete.json` enter aggregate analysis. Repeated appearances
of the same district type on the same plot, such as capture, are excluded from
new-placement choices. City-state events remain in raw evidence; the primary
statistics concern major civilizations. Current placement statistics use
completed Quarters, including separately identified pillaged districts.

Candidate comparisons use already owned tiles passing native plot placement
checks at the preceding player-turn scan, at most one turn old. They exclude
future purchases and tile swaps, and do not prove affordability or full production
eligibility. Maximum-material comparisons with no material-bearing alternatives
are excluded from the nontrivial comparison denominator. City Centers and other
sales districts are reported separately.

Resource improvement follow-up matches the original player and resource;
retention compares initial materials with final resources and district occupation.
Neither metric alone proves a builder preference or the reason for clearing a
resource. Research/building/material/venue gates and current supply flags are
separate from persistent hidden Service buildings. This is an observational
baseline, not a causal test of whether the AI reads custom adjacencies.

## Current tuning and rejected markers

Current `CSC_AI.sql` uses native bonus-resource (+12), river (+4) and reciprocal
sales adjacency (+10), with RH-aligned improvement base 90 and Builder unit priority 900. CSC's former +50% improvement preference has been removed. Bonus resources are a
broad material proxy; actual mapped/improved supplies still control Services.
Bakers/Tailors only, with no marker features. See [current integration notes](../../docs/integrations/csc-ai-tuning.md).
`validate_tuning.py` checks current SQL, while historical trial source pins refer
to the earlier combined candidate and must not be treated as current-source checks.

The `marker_*` fixtures, `marker_trial.py`, `validate_markers.py`,
`analyze_markers.py` and `experiments/rejected_CSC_AI_MaterialMarkers.lua` are
retained research artifacts for the [rejected feature experiment](../../docs/research/mods/csc-ai-markers-rejected-20261017.md).
They are not deployed or part of ordinary baseline generation. Marker validation
requires explicit archived SQL. The revision-3 Builder guard was never tested
with additional AI turns. Do not resume its controller or re-register the module.

## Native bonus/river trial

`native_tuning_trial.py` is the historical v3 candidate's matched-seed runner;
its controller, observer, gameplay pins and baseline comparison stay distinct from
the v1 trial. `native_guidance_probe.lua` reads prospective native bonus/river
values without writing gameplay state. `analyze_native_tuning.py` takes explicit
`--trial`, `--baseline`, `--previous`, and `--resource-catalog` paths and compares
actual materials, river alternatives, improvements, retention, Services and
endpoint bonus-proxy matches. It includes nonhuman-only Base choices separately.

The [17 October trial](../../docs/research/mods/csc-ai-native-bonus-river-20261017.md)
completed in `Desktop/Codex/csc-ai-native-bonus-river-20261017/retry-01/`.
The first native crash is excluded under `trial/`. Read-only checkpoint archive
reconnects and the final preference-restore acknowledgement recovery are recorded.
Do not resume a completed trial or use the old v1 probe formulas on this candidate.

## Sparse Builder trial (v4)

`run_builder_job.py` orchestrates one native game plus `analyze_builder_tuning.py`
without model polling. Supply `--output`, `--captures`, `--baseline`, `--previous`
(v1), `--placement` (v3), and `--resource-catalog`. Run the job as a hidden
background process after a focused deployment and a fresh Civ launch.

The runner retains the unchanged primary observer and adds Builder unit
telemetry. `sparse_builder_controller.py` archives 50-turn milestones while
polling locally every 20 seconds, tolerates short transient connections and
bounds stalls to ten minutes. It saves at 250 and restores native preferences.
Read `job-status.json`, `live-status.json` and `progress.log` for scheduled
assistant follow-ups. Do not run a second Tuner client during the job. On failure,
inspect the archived evidence; do not blindly replay configuration or autoplay.
Historical Builder production counts are unavailable; compare actual improvement
density and material follow-through across runs, and report new unit counts separately.

## Interrupted-run checkpoint comparisons

`analyze_checkpoint_tuning.py` compares real snapshots at an explicitly selected
`--turn` (default200), using the four run roots, resource catalog and a separate
`--output`. It retains historical tool files and source pins. Initial world,
leaders/research, observer errors and event prefixes are checked. Future
timeline rows are excluded and material exposure uses the selected endpoint.
Outputs never mark an interrupted250 run complete or overwrite its raw data.
See the RH Builder turn200 report for the first use.

## Latest resource pass plus AI trial

`run_density_job.py` supervises `density_game_trial.py` and
`analyze_density_game.py` with explicit output/captures/baseline/previous roots.
It uses original AI seed1 with pass4 resources, preserving terrain/leader/research
checks but allowing intended resource differences. Dedicated archive/save
methods keep historical tools/source pins unchanged and archive every25 turns.
The supervisor detects process exit, preserves failure evidence and never
automatically reruns. Successful analysis reports250 plus a real common200
comparison to the interrupted RH Builder trial. Follow-up reads local status
about15min apart; do not run a competing native client.
