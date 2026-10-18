# CSC continental resource helper — offline preview

The five captured native four-type Abundant maps now have an additive CSC preview. Helper seed **20261016** was fixed before inspecting the outcome. This is an overlay experiment: Civ was not run and no production mod, installed game file or native map export changed.

## Coverage

Continents with at least one both-class candidate, allowing ordinary future clearing. Fifteen named continents across five maps; the same definitions and filters as the native study.

| Quarter | Original | With additions | Approximate target |
|---|---:|---:|---:|
| Bakers | 12/15 | 12/15 | 10/15 |
| Tailors | 3/15 | 11/15 | 10/15 |
| Apothecaries | 9/15 | 9/15 | 10/15 |
| Stonemasons | 4/15 | 8/15 | 10/15 |
| Carpenters | 15/15 | 15/15 | 10/15 |
| Blacksmiths | 15/15 | 15/15 | 10/15 |
| Goldsmiths | 2/15 | 6/15 | 5/15 |
| Brewers | 11/15 | 11/15 | 10/15 |

The additions per map are **5, 2, 1, 3, 5: 16 deposits total**. Every successful repair in this draw uses a single added resource. No existing resource is replaced. Named continents finish with between four and seven land luxury types.

The targets guide probabilistic assistance, rather than enforcing a quota. Missing-continent selection probabilities are Tailors 7/12, Stonemasons 6/11, Apothecaries 1/6 and Goldsmiths 3/13, derived from the original deficits. Shared-material gains and terrain feasibility can alter expected coverage. These are starting hypotheses, not calibrated long-run guarantees. All six missing Apothecaries cases failed their assistance draw in this sample; the map was not rerolled to reach ten. Goldsmiths overshoot their intended rarity by one continent, while Stonemasons remain two short.

## Placement method

1. Use the native named continent IDs, preserving every original tile and deposit.
2. Allocate one soft resource palette per continent. Each assisted Quarter/material class gets a preferred feasible type. Existing local types receive more weight, and allocating the same resource to other continents lowers its weight. This encourages continental identity without a hard exclusion that can make a repair impossible.
3. Draw assistance once for each missing continent/Quarter combination. Already-supported industries receive no direct help. Shuffle the processing order and recompute all industries after each accepted repair, capturing shared benefits.
4. Enumerate successful arrangements: an ordinarily clearable Quarter center adjacent to both classes. Add a Specialty near an existing Base, a Base near an existing Specialty, or two resources if neither exists. Hills/Woods/Rainforest count as designed Base materials. Prefer one-deposit repairs. Resource combinations are drawn before positions so large habitat areas do not dominate resource selection by tile count alone.
5. Prefer the continental palette while allowing other eligible mapped types when necessary. Keep the new source tiles and intended Quarter center on the assisted continent. Existing cross-border sources can still support centers.
6. Protect reserved centers and each continent's last Base-supported and both-class opportunity for every Quarter. Limits are four deposits per continent and ten per map. This sample did not reach either cap.

Some otherwise valid candidate tiles become occupied by added luxuries. The sample loses four original both-class candidates: one Carpenters site on Map 1; one each for Tailors, Carpenters and Blacksmiths on Map 4. None was its continent's last such opportunity. The viewer shows these losses as red crosses, alongside green rings for new opportunities and orange numbered resource additions.

## Viewer

Open `project/tools/map_lab/viewer.html` or `project/snapshots/map-lab/index.html`. The default resource setup is **CSC helper · preview additions**, with five landscapes and ordinary clearing enabled.

- Switch **Placement comparison** between the original native resources and proposed additions while retaining the map view.
- Orange numbered outlines identify every proposed deposit, including its empty original location in the Before view. Hover or click for resource, coordinates and purpose.
- Choose an industry and continent using the existing controls. Green rings show new sites and red crosses show blocked original candidates in the After view.
- Below the map, compare all eight industries across the fifteen continents and examine the exact additions on the selected map. Coordinate buttons focus the deposit or its intended Quarter center. Continental palettes are expandable.
- Existing native 4/5/6-type maps and the original fifteen resource-survey maps remain available: 35 viewer entries in total.

Machine-readable results live under `project/snapshots/map-lab/helper-preview/`: `assistance-analysis.json`, `added-resources.csv`, `coverage-comparison.csv`, `preview-maps.json`, and `validation.json`. Preview entries include random draws, outcomes, preferred continental pools, exact resource IDs and coordinates, intended center, shared coverage gains, and source hashes.

## Verification and boundaries

The integration check reproduces the full preview from its seed, verifies preservation of every original resource/terrain/feature tile, checks all sixteen added deposits against both the Python habitat interpreter and the existing Lua adapter, confirms a successful final center for each repair, and protects last Base/both-class coverage. It also exercises the two-deposit and budget-rejection paths on a modified test landscape. The viewer's actual geometry functions pass 6,120 comparisons across all 35 entries. A DOM/canvas fixture runs the full viewer and verifies 1,920 before/after control/count combinations and deposit navigation. This is source-level UI verification, not a browser visual review.

Eligibility uses the frozen CSC-only SQL profile and the offline resource-rule interpretation previously checked against native samples. Native `CanHaveResource`, script load ordering and the eventual in-game pass remain untested for these proposals. No optional resource packs are active in these five maps; extra modded mappings need their own profile and validation. Bakers/Tailors use captured runtime material classes; the six unfinished Quarters retain their individual design-page definitions rather than incomplete SQL stubs.

Counts describe material geography, not guaranteed services. Candidate sites may share sources, bonus resources/features may need later removal, and research, improvements, ownership, city reach, customer districts and other service conditions still apply. Stage 2–3 Base supply remains distinct from Stage 4 both-class supply. These five reused landscapes are a development sample, not a holdout or a guarantee for other map scripts or sizes.
