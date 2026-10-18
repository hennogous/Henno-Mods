# CSC material geography survey

The [map viewer and offline resource experiments](../map_lab/README.md) inspect
these exports without launching Civ. Future dumps additionally include continent
IDs, river/lake flags, wrapping and map size; the original fifteen are unchanged.

Generate fifteen fresh Small Continents maps, with CSC and official content,
six civilizations, nine city states, Prince difficulty and Online speed. The
three groups reuse five map/game seed pairs and the original baseline rosters:

1. Vanilla Abundant, TAR disabled (`resources=3`).
2. TAR enabled with Abundant (`resources=3`).
3. TAR enabled with Truly Abundant (`resources=45`).

No game turns advance. Each map has a complete native tile dump, actual settings,
logs and command transcripts. Native saves are optional with `--save-maps`;
the default retains data and numbers only. Native neighbor lists avoid
inferring adjacency from a screenshot. No gameplay properties, terrain or AI
priorities are changed. The runner preserves and restores mod preferences and
native auto-start, and requires the main menu and exclusive FireTuner access.

## Paired luxury-type experiment

`luxury_study.py` creates an ignored private copy of the installed Gathering
Storm `Continents.lua` and passes an explicit `LuxuriesPerRegion` argument (4,
5 or 6). The engine accepts the private map's absolute path directly, so no
game or Workshop file, CSC gameplay file, or installed test mod is changed.
Use `--prepare-only` to inspect it, `--first-only` for a background smoke test,
or no mode switch for all fifteen paired maps. `--reference` points to the
original survey folder; `--output` is the explicit evidence destination.
The five original seed/roster pairs, CSC and vanilla Abundant are retained.

Run `continent_analysis.py --output FOLDER`, then
`verify_luxury_study.py --output FOLDER --reference ORIGINAL_SURVEY` and
`report_luxury_study.py --output FOLDER --report REPORT.md` after completion.
The census records Base-supported and both-class sites separately, counts
material terrain/features, permits cross-border support, and assigns each
candidate to its own native continent. Verification compares all four-type
controls to the original maps and checks paired terrain, continent IDs,
neighbor topology, runtime settings and SQL errors.

Read-only `calibration_capture.lua` observations were added during the study:
pre-resource, post-resource and post-start map layers, resource-phase RNG draws,
sampled native eligibility decisions, and placement events. It wraps native
functions temporarily, forwards their calls unchanged and makes no extra RNG
draws. See `map_lab/calibrate.py` for extracting and testing these fixtures.
Captured observations vary by map because calibration was requested mid-batch.
Do not treat recorded-draw replay as a standalone Civ RNG implementation.

```powershell
python project/tools/map_survey/run.py --output 'C:\Users\Shadow\Desktop\Codex\csc-map-material-opportunities-20261016' --rosters 'C:\Users\Shadow\Desktop\Codex\csc-ai-baseline-20261015'
python project/tools/map_survey/analyze.py --output 'C:\Users\Shadow\Desktop\Codex\csc-map-material-opportunities-20261016'
python project/tools/map_survey/verify.py --output 'C:\Users\Shadow\Desktop\Codex\csc-map-material-opportunities-20261016'
python project/tools/map_survey/publish_report.py
```

`materials.json` records definitions and their sources. Bakers/Tailors resolve to
the actual loaded material tags. The other six follow their individual public
design pages, including Hills for Stonemasons/Blacksmiths and Woods/Rainforest
for Carpenters. Current Carpenters design includes Copper/Iron base materials and
Aluminium/Silver among specialty materials; older overview/stubs differ.
Goldsmiths use Diamonds/Jade from their individual page, with a separate
Pearls-inclusive sensitivity count for the overview's additional material.

The principal count is a distinct passable land tile adjacent to both material
classes. Ownership, city reach, improvements, research and affordability are not
filters. All resources include strategically hidden deposits. A neighboring
terrain/resource tile may satisfy both classes. Separate counts require two
distinct supporting tiles and measure the increase from terrain/feature sources.

The common clearable-site count additionally removes occupied districts,
nonremovable features except GS floodplains, and luxury/strategic resources on
the candidate tile. It allows ordinary clearing after research and uses the same
filter across groups. The harvest-aware variant additionally recognizes the
loaded resource harvest rules, including TAR's luxury/strategic harvesting.
Neither is a full city-specific native legality test. Adjacent candidates can
share materials and are not independent settlements or simultaneous builds.

The runner can restart from the main menu and skips completed map folders. Never
start a second tuner client while it runs. Source hashes pin CSC, TAR, generator,
observer, definitions and the design pages. Keep generated evidence in the
explicit Desktop/Codex output directory.

For a loaded but unfinished turn-1 map, `--resume-current --resume-group GROUP
--resume-map N` re-reads that map with its observer and continues the batch.
The current mod configuration must already match the recorded settings. Native
mod preferences are restored at the final main menu.
