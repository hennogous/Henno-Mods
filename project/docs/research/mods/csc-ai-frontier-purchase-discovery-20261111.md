# Frontier purchase discovery in three existing worlds

## Purpose and scope

Problem **1.5** needs a credible Quarter footprint and an observed native
purchase, rather than another bid on Nicopolis's uncertain plot 401.
This diagnostic loaded three existing Online turn-200 checkpoints through
one exclusively owned shared-controller session. It advanced **zero turns**,
submitted no purchase or score treatment, and preserved the integrated policy.

The CE carrier SHA-256 was
`f8121151c787e4dcd4fea876eaaef5d6d1bb2b54561bc94d9d7da6385f21aa07`.
The patched stock GameCore was
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
Loaded module paths and identities were checked in every world. The frozen
CSC carrier replaced only its scanner and publisher with current main-mod
bytes. Two independent city/name/owned-plot tuples checked each loaded world
against its previous survey, in addition to exact save hashes and turn readiness.

Tools are `project/tools/native_ai/late_placement/frontier_discovery.py` and
`frontier_site_survey.lua`. Evidence is under
`Desktop/Codex/csc-ai-problems-1-2-20261110/frontier-discovery-three-saves-01`.
The controller verified exit zero, original preference restoration, absence of
remaining owned processes and retirement of the exact temporary packages.

## What was enumerated

For each alive major AI city without that Quarter, enumerate revealed,
unowned, district-free, radius-three sites with a same-player border neighbor
and a successful `CanHaveDistrict` geometry query. Keep leads with at least
one **known viable owned Base** from the actual CSC supplier reader.
Record loaded all-stage customer/provider relationships, alternative future
owned customer footprints, improvement readiness/working state, river edges,
producer unlock metadata, Treasury and raw income/maintenance fields.

These are leads, not assured investments. Future footprints are alternatives,
not benefits to sum together. Producer unlock metadata does not establish its
location-specific requirements, admission, cost or construction. Existing
reservations, active requests and district capacity still need native inspection.

Separately search for revealed unowned Base deposits beside existing Quarters.
Such deposits would need their own purchase and improvement qualification.

## Results

Counts are city/profile/plot pairs, so different cities or Quarter types can
refer to the same physical footprint.

| Saved world | Candidate pairs | Distinct plots | Future host geometry | Working Base | Both material classes | River edges present |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Continents | 4 | 4 | 1 | 0 | 0 | 0 |
| Pangaea baseline | 10 | 8 | 8 | 1 | 0 | 3 |
| Fractal baseline | 20 | 14 | 17 | 1 | 3 | 2 |

All 34 pairs had positive UI quotes. None had an existing mapped owned host;
26 had at least one future host alternative. No supplier-purchase lead met
the separate revealed/unowned/adjacent-Base enumeration in these checkpoints.
This does not establish an absence of supplier opportunities in earlier games,
unrevealed land, foreign land or supported configurations generally.

The two working-Base leads were:

- Pangaea, player 2, Takamatsu city 589832: Bakers plot 756, working Maize at
  829, quote 95 Gold, future host alternatives on 830 and 755.
- Fractal, player 2, Szeged city 589829: Tailors plot 1365, working Cotton at
  1366, two river edges, quote 85 Gold, future host alternatives on 1290.

That future host plot belongs to another friendly city, ID 524292, rather
than Szeged 589829. Resolve its identity and applicable cross-city customer
rules before treating it as a credible benefit. Its capacity and commitments
affect timing; immediate customer admission is not required for long-term
map potential. Quarter admission itself remains a separate native gate.

Szeged's player had 719.7734375 Treasury Gold, raw Gold yield 161.97265625
and maintenance 87 at this boundary. These are not its earmarked plot/slush
funds. The site still needs the canonical adjacency calculation, exact host
types, district capacity and current commitment checked. In particular, an
all-stage customer alternative does not establish a Stage 2 Harbor chain.

## Gameplay versus UI query context

The optional Gameplay quote call returned no numeric value for these pairs,
with `missing method: GetPlotPurchaseCost`. The same scoped UI reads returned
positive prices. The diagnostic preserves missing-input flags rather than
substituting zero, then joins independent UI values by player/city/plot.
This is a result for these contexts, not a universal claim about every Lua API.

The strict UI `CanStartCommand` query returned false for all pairs at the
inactive observer boundary. The archived field is named `canPurchaseNow`.
That name must not be taken as native Economic eligibility: we have not
isolated the effects of caller, player-turn state or overload semantics.
Native validation and actual spending remain separate observations. The
maintained tool uses the clearer label `uiCanStartAtBoundary` going forward.

## Qualification and next test

The six offline checks cover supply/visibility/ownership filtering, explicit
missing quotes, retained nonpositive quotes and deduplicated Gameplay/UI joins.
The live collection separately verifies the actual contexts and three source
worlds. Astra reviewed lifecycle, provenance, limits and candidate requirements.
Neither test category proves an AI choice, purchase or placement improvement.

Szeged is the first lead to inspect more deeply: verify its actual projected
adjacency and customer footprint, native district admission/reservation and
earmarked funds, and compare Takamatsu's working-Base lead. Positive frontier
offers are not implemented yet: production frontier handling currently supplies
deductions. After qualifying the model and native gates, implement the bounded
common-model offer, then compare it with a scoped ablation while observing
comparison, request, native payment, ownership and foundation.
Keep the existing native competition and actual own-funds constraints intact.

## Exact model inspection and future-type correction

The zero-turn `frontier-model-two-saves-01` inspection loaded the same Fractal
and Pangaea saves and called the live scanner's shared read-only adjacency
function. None of their 30 known-Base frontier pairs reached +4, even taking
the maximum of one future neighbor alternative. This diagnostic maximum is
not the live planner's traversal choice, nor a native utility score.

Szeged plot 1365 is **2 Production + 1 projected Gold = +3**: Cotton supplies
one Production, two river edges supply another, and one future Holy Site or
Commercial Hub can add one Gold. Neither alternative is a Stage 2 Harbor.
Takamatsu plot 756 is **1 Production + 1 projected Gold = +2**. Its flat inland
site gets no extra adjacency from its projected Wind Mill branch.

The unfiltered geometry query also accepted Lavra and Suguba for Hungary,
and Street Carnival, Suguba and Hippodrome for Japan. Consequently the earlier
26 future-host leads in AI-C142 mean raw geometry, not verified actor eligibility.

The main scanner now applies civilization/leader traits (including inherited
leaders), direct unique replacements, explicit exclusions, existing district
families and mutual exclusion to prospective empty footprints. It follows
shipped `Civ6Common.lua` and `TechAndCivicUnlockables.lua` conventions. It does
**not** require the future district's current unlock or population capacity.
An existing native customer target remains authoritative for an immediate bid.
Missing required metadata leaves a supplied site neutral, with no invented
no-host deduction or city-deferral count. This is a scoped planning filter,
not a reproduction of every native district-admission rule.

### Matched zero-turn filter inspection

`frontier-filter-two-saves-01` advanced zero turns and verified normal exit,
preference restoration, process absence and exact package retirement.
The same 30 city/profile/plot pairs remained. Future alternatives changed:

| World | Raw alternatives | Filtered alternatives | Pairs with changed alternatives | Pairs losing all future hosts | Maximum forecast changed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fractal | 94 | 42 | 17 | 0 | 0 |
| Pangaea | 60 | 26 | 8 | 0 | 0 |

These counts include multiple district types/footprints per Quarter site;
they must not be added together as future adjacency. Szeged retained only
Holy Site/Commercial Hub at Debrecen plot 1290. Takamatsu retained Commercial
Hub/Entertainment Complex at its two other-city footprints. Their +3/+2
maxima were unchanged. This demonstrates removal of invalid possibilities,
**not** a changed native decision, acquisition or closure of Problem 1.2.

UI capacity reads succeeded where Gameplay's optional getters were absent:

| Player 2 city | Population | Allowed specialty districts | Zoned specialty districts | Current production |
| --- | ---: | ---: | ---: | --- |
| Fractal Szeged | 5 | 2 | 2 | Settler |
| Fractal Debrecen | 10 | 4 | 3 | University |
| Pangaea Takamatsu | 1 | 1 | 0 | Nothing |
| Pangaea Yokohama | 4 | 2 | 1 | Industrial Zone |
| Pangaea Shizuoka | 7 | 3 | 2 | Lighthouse |

These counts inform timing; they do not invalidate a future footprint merely
because a city needs to grow first. They are not proof of all reservations or
requests. The loaded Quarter definitions do not require specialty capacity.

The archived filter scanner SHA-256 is
`a0fb022f8078371455e7b43378990137ae76f0b416ab39dbff675db51de83253`.
The unfiltered model scanner is
`4045300c94eda59e37642cfab26760e678c7b7eb7aadf5d67f2c6e1c614d7325`.
Subsequent Astra review corrected replacement ordering to suppress the base
before exclusions, made family expansion one level, and hardened unknown
metadata handling. Those refinements pass eight helper tests, ten grouped
scanner checks and seven discovery checks. They were made **after** the live
run staged its bytes and are not claimed as live-tested final source.
Astra independently checked the source corrections and archived counts.

Filtered survey SHA-256 values:

- Fractal: `b2bd552ad291e2407b4ec4ed3adebb98122b59a13b27470ba1a27227b5d688b0`
- Pangaea: `57b9c4b62250383897224b438c1e00360406d71c03cdc1a38724295f33eabb44`

The next purchase fixture can use a transparently labelled viable +3 site or
an earlier genuinely +4 opportunity; do not rename either discovered lead a
strong site to force a demonstration. A discriminating native comparison is
also still needed for the future-host policy. Capture actual Treasury and
Economic's accounted balance/accounts alongside the quote; the
[savings mechanism](civ6-economic-plot-savings-20261111.md) is now traced statically.

### Artifact identities

| World | Save SHA-256 | Survey SHA-256 |
| --- | --- | --- |
| Continents | `e333251ec7318fb6b170678a956c28e02e2f9b01c4c4753c99e84b1a112fe19a` | `f7a4ab0b54936a22480ca1c03c6c675b10c0f554d4d29041480c2b5c3b61c549` |
| Pangaea | `efa19eeaf9ed4312f548d18500cb67e9ae77cf3d6af8be33efd653621e25f980` | `fb665c323ce0babff54f56c93a07543ad2de400fc7120a6c1720cb3768ed46e2` |
| Fractal | `c50976621de17e38f998fad916b22a1bd219f4cdc9af508d90b8846d011fbf91` | `cb4f1feff4fdeca59f10128c62216031c472a98bd3c46a4f7e75f15b9e661392` |
