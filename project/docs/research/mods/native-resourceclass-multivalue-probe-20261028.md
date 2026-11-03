# Native multi-value resource-class probe — 28 October 2026

**Result: none of the tested encodings creates multiple class memberships.**
For native Campus adjacencies, Civ treats each combined string as one class
identifier. A rule containing the identical whole string matches; rules for
the individual constituent names do not.

This follows the [single custom-class probe](native-custom-resourceclass-probe-20261028.md),
which established that a new class name works. One TEXT column alone did not
prove that the game could not parse lists, so this follow-up tested that behavior
instead of inferring it from the schema.

## Setup

One disposable Gathering Storm DX11 world, official content and the standalone
probe only. Native control uses the maintained `FullGameController` and
`native_profile_test` preference helpers. No computer use or autoplay.

Individual Campus adjacency rules:

- `RESOURCECLASS_CSC_PROBE_WHEAT` (A): +10 Food.
- `RESOURCECLASS_BONUS`: +10 Faith.
- `RESOURCECLASS_CSC_PROBE_SECOND` (B): +10 Gold.
- Each distinct combined class string: +10 Culture, as an exact-string control.

All rows use `AdjacentResource=0`, `TilesRequired=1`. No scripted yield grants,
TypeTags, or extra class registration. The rules also test the adjacency-field
side of parsing: literal-string Culture rules do not match the constituent
single-class resources.

Twelve resource assignments were loaded together. Each candidate was placed
alone beside the same Campus plot, first before district placement and then
after completing it. Empty, paired single-class controls, and removal were also
measured in each stage: 15 phases × 2 stages = **30 samples**.

## Results

BONUS and A/B below abbreviate the full names above. All values are native
Campus adjacency; preview and completed-district readings agreed.

| Stored class form | Resource | Food | Faith | Gold | Exact-string Culture |
|---|---|---:|---:|---:|---:|
| BONUS | Rice | 0 | 10 | 0 | 0 |
| A | Cattle | 10 | 0 | 0 | 0 |
| B | Cotton | 0 | 0 | 10 | 0 |
| BONUS,A | Wheat | 0 | 0 | 0 | 10 |
| A,BONUS | Sheep | 0 | 0 | 0 | 10 |
| BONUS, A | Bananas | 0 | 0 | 0 | 10 |
| BONUS;A | Stone | 0 | 0 | 0 | 10 |
| BONUS\|A | Copper | 0 | 0 | 0 | 10 |
| BONUS A | Salt | 0 | 0 | 0 | 10 |
| JSON array `["BONUS","A"]` | Deer | 0 | 0 | 0 | 10 |
| A,B | Sugar | 0 | 0 | 0 | 10 |
| JSON array `["BONUS","A","B"]` | Silk | 0 | 0 | 0 | 10 |

The paired Rice + Cattle control yielded 10 Food / 10 Faith / 0 Gold / 0 Culture.
Empty and removal phases returned zero for all four tested yields.

The full comma string on Wheat is
`RESOURCECLASS_BONUS,RESOURCECLASS_CSC_PROBE_WHEAT`. Its +10 Culture confirms that
the stored value was usable as a class identifier; the zero Food and Faith are
not merely a broken resource placement or an unloaded SQL row.

The verifier independently checks actual neighboring resources/classes, native
database assignments, positive controls and agreement among placement
`Plot:GetAdjacencyYield`, completed `District:GetAdjacencyYield`, and
`District:GetYield`. All samples were within turn 1; city/player economic ticks
and unrelated native class consumers remain outside this probe's scope.

## What SQLite contributes

The schema has `ResourceType` as the primary key and `ResourceClassType` as TEXT.
An offline replay rejected a second Wheat row with
`UNIQUE constraint failed: Resources.ResourceType`.

SQLite string concatenation produces the same comma-containing text as a
literal. JSON arrays can be stored as text too. Neither storage form makes the
game split a field automatically; the native observations above show that it
does not split these tested forms. A separate membership table would require a
consumer that reads it, such as CSC's TypeTags-based evaluator.

The practical conclusion is scalar class matching for the tested native path.
This is evidence against the enumerated formats, not a proof about every
conceivable undocumented syntax. TypeTags remains the established mechanism
for overlapping Quarter memberships without replacing bonus/luxury/strategic.

## Evidence and cleanup

Root: `C:\Users\Shadow\Desktop\Codex\resourceclass-multivalue-probe-20261028`.

- `package/Probe.sql`, `prepared.json`: exact assignments and twelve rules.
- `sqlite-storage.json`: storage replay and duplicate-row rejection.
- `native-database.json`, `DebugGameplay.sqlite`: actual loaded definitions.
- `results.json`, `verification.json`: all 30 native observations and checks.
- `commands/`, `controller-journal.ndjson`, `logs/`: raw evidence.
- `cleanup.json`, `preferences-restored.json`: 145 IDs / 148 installed entries
  and auto-start false restored with independent native readback; game absent;
  original standalone probe files restored byte-for-byte.

An initial preflight wrongly assumed the existing probe's enabled flag would
still be false. It exited before any hosting or preference changes. The actual
pre-run state was then captured, and the same main-menu process hosted the one
test world. The captured probe flag was true and was restored as captured.
The original failed assumption is retained in `failure.json`; it is not a native
syntax failure. No existing CSC source or installed CSC package files changed.
