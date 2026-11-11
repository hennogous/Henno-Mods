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

### Artifact identities

| World | Save SHA-256 | Survey SHA-256 |
| --- | --- | --- |
| Continents | `e333251ec7318fb6b170678a956c28e02e2f9b01c4c4753c99e84b1a112fe19a` | `f7a4ab0b54936a22480ca1c03c6c675b10c0f554d4d29041480c2b5c3b61c549` |
| Pangaea | `efa19eeaf9ed4312f548d18500cb67e9ae77cf3d6af8be33efd653621e25f980` | `fb665c323ce0babff54f56c93a07543ad2de400fc7120a6c1720cb3768ed46e2` |
| Fractal | `c50976621de17e38f998fad916b22a1bd219f4cdc9af508d90b8846d011fbf91` | `cb4f1feff4fdeca59f10128c62216031c472a98bd3c46a4f7e75f15b9e661392` |
