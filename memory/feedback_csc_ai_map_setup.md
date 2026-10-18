# CSC AI experiments and map surveys

16 October 2026: Henno prefers **Online speed and Abundant resources** for future
AI autoplay tests. Truly Abundant Resources is a candidate distribution option,
not yet a standing default: compare TAR enabled with vanilla Abundant separately
from TAR's Truly Abundant preset.

For map-only surveys, native game saves are unnecessary. Retain the numbers and
complete lightweight tile data so definitions and counts remain auditable.

The 16 October survey used CSC in all three groups, Small Continents, six majors,
nine city states, five paired seed/leader setups, and all eight Quarter designs.
Use actual runtime tags for implemented Quarters and individual canonical design
pages for unimplemented ones. Hills and Woods/Rainforest can be materials.

Do not equate no both-class adjacency with a missed AI opportunity: some maps
omit an entire material class. Preserve resource availability denominators.

Results: `project/docs/research/mods/csc-map-material-opportunities-20261016.md`.

## Resource-distribution design direction — 16 October 2026

Henno explicitly wants uneven opportunities between players, industries and games.
Reading and adapting to the generated geography is central to CSC. Do not pursue
equal capital access or similar Quarter opportunity counts. The original
worldwide-only coverage direction is refined by the later continent preference
below; no numerical regional quotas are agreed. Quarters without adjacent materials remain meaningful through sales and
other ordinary building benefits.

Desired intervention is light touch: retain some geographically useful material
opportunities for all eight Quarters somewhere on each map, while preserving wide
variation in their number and location. No exact minimum or algorithm is agreed.
Increasing the default four land-luxury types per named continent is a candidate
to investigate before engineering targeted resource clusters. Terrain/feature
material Quarters may naturally have many more sites; address their relative
strength through gameplay balance rather than equalizing map distribution.

Source checks: implemented Bakers/Tailors adjacent-building transactions are not
material gated; Services and direct material interactions are. Domestic CSC
trade-route exports also require supplied Stage 3/4 buildings, so materials do
more than unlock Services. Some public Quarter prose does not spell out that
route-supply qualification; do not silently reinterpret runtime behavior as the
desired design. Both-material site counts describe full-supply geography, not
all useful Quarter locations.

Generator check: LuxuriesPerRegion is a Lua constructor argument defaulting to 4,
not a SQL setting. Luxury occurrence budget divides by that count; more selected
types generally means fewer copies per type at unchanged abundance. Selected
types are removed from a shared pool across continents, so raising the count also
needs checks for later continents and expanded resource packs. No gameplay or
map-generation implementation changed during this discussion.

## Native generation preferred over an external engine port

After discussing the work required for faithful external TAR/YnAMP/Oceans
generation, Henno proposed using the full game backgrounded, or running tests
while the machine is not in use. Prefer that practical native workflow; park
further standalone engine-emulation work. Keep the map viewer and native export
tools. Minimized generation must first be verified for progress and focus
behaviour; do not assume it will remain unobtrusive or start foreground batches
while Henno is working. No idle-monitoring automation or schedule is agreed.

## Continental coverage refinement

Henno subsequently said he is okay with / likes different continents being
"equally friendly to all industries", with no massive redistribution. Working
interpretation communicated in chat: broad availability of each industry on each
substantial continent, preserving unequal site counts, site quality and player
access. No exact minimum or strict guarantee for tiny/inhospitable regions is
agreed. This refines the earlier worldwide-only target; do not silently retain
the previous prohibition on all regional coverage aims.

Proposed route: native background/away batches; capture continent IDs and
measure class presence plus separate viable clusters; compare 4/5/6 land luxury
types at fixed abundance; address limited cross-continent repetition if coverage
requires it; only then add a bounded CSC audit/repair for missing classes or
isolated pairs. Original generator removes selected land luxury types from a
shared pool, so raising the per-continent count alone cannot guarantee every
continent covers narrow classes such as Goldsmiths' Diamonds/Jade.

## Authorized native diversity study and offline calibration

Henno approved native background generation, then 4/5/6 luxury types per continent
on the same five seeds, CSC plus vanilla Abundant, with continental results in
the viewer. Keep the intervention cautious: Base supply supports Stages 2–3;
only Stage 4 requires both classes, and Stage 4 scarcity may be desirable.

During the run Henno also requested using these results to identify the
approximations needed for map generation outside Civ. Native phase captures and
API/RNG/sort comparisons are now authorized supporting work; they do not imply
an exact same-seed external generator or full arbitrary-mod compatibility.
Henno confirmed Civ was backgrounded while he used the machine. Computer Use
window access was denied; FireTuner worked without input. A later capture bug
attempted to modify read-only `table.sort`, producing a startup error. Henno
closed that popup; the corrected capture observes generator methods instead.

## Both-class coverage targets and continental additions

Henno clarified the desired Abundant-resource target: roughly 10/15 named
continents should have both-class Quarter opportunities for each industry,
except Goldsmiths at roughly 5/15 because they are intentionally very rare.
He proposed randomly selecting from the mapped Specialty resources (including
active modded resources) and placing near selected Base materials, borrowing
Sukritact's Oceans' approach. He explicitly accepts CSC additions taking a
continent above the stock four luxury types, and suggested a separate addition
pool per named continent. These are design targets, not authorization yet for
a production distribution implementation or a new native test batch.

Installed Oceans source confirms AddGameplayScripts plus a persistent once-only
guard; weighted continental resource selection reduces repeat weights elsewhere
without excluding the type. Its sea-luxury pass actually removes and replaces
sea luxuries, so a light CSC pass should borrow regional selection/placement
principles, not copy that replacement behaviour. Proposed CSC refinement is to
enumerate successful district-site/resource placements, use local feasible
resource palettes with soft cross-continent reuse, permit Base-side help when
needed, preserve existing last viable sites, and recalibrate probabilistic
assistance on both coverage and number of extra deposits. No code installed.

Henno subsequently authorized the five-four-type-map offline overlay prototype
with exact added-deposit inspection and before/after coverage in the viewer,
explicitly before native testing. This is now implemented; the previous absence
of authorization applies only to production installation and a new Civ batch.
See the continental helper preview research report for actual sample results.

Henno then authorized the five paired **native** helper API tests and confirmed
Civ remained backgrounded after the hidden-window launch. Completed; see native
comparison report. No production Lua helper was installed: Python selection/RNG
was retained while Civ supplied actual eligibility, setters and final exports.

Henno then authorized converting the helper into CSC Lua and testing automatic
execution on the same five seeds, still backgrounded. Implemented, installed and
verified; the previous Python-only boundary is superseded. The first shipped
scope is new Abundant maps with an On-by-default setup toggle. The pure planner
uses its own deterministic Lua stream; native automatic choices exactly replay
offline with captured eligibility, while draws differ from the Python prototype.
