# CSC Builder tuning — matched turn-200 comparison

The matched turn-200 comparison gives a useful positive signal despite the
interruption. With only the two RH-aligned Builder settings changed from v3,
improvement density rose from5.22 to7.76 plots/city (+48.7%) and45.6 to59.9
plots per100 population (+31.4%). All six autoplay players had higher
improvements/city than their v3 counterparts. The new run has49 cities versus51,
so the aggregate gain is not explained by more cities. Later wars and research
still diverged.

Bakers' adjacent owned mapped Base plots improved:12/16 (75%), versus8/15
(53%) with v3,4/8 with v1,4/11 with baseline. At-200 Base placement choice
was22/26 (85%), versus20/22 (91%) in v3. The unchanged placement guidance
still performs reasonably, but this single run does not show better placement.
Among initially unimproved Baker material links,9/23 were improved later versus
8/24 in v3; the median wait among improved links fell from37.5 to10 turns.
Those small, selected samples do not establish a general response-time effect.

Services did not increase relative to v3: both have7 Growth and2 Housing source
cities at200, and no Tailor Service sources. Tailor Base access occurs only
once in the new endpoint; its1/1 improved result has too little exposure to
support a strong conclusion. Fewer Tailor Quarters were completed:23 versus29
in v3. Baker completions were44 in both. Broader economic/military tradeoffs
need more seeds before choosing final weights.

New-run telemetry records145 Builder training completions and58 purchases by
turn200;26 Builders remained with55 charges.230 added-to-map events also
include capture/grant possibilities and must not be equated with production.
Historical runs lack this telemetry, so the evidence of improvement is the
matched tile outcomes, not a measured increase in Builder unit production.
The90/900 values are worth retaining for further validation; no further
changes or native games were started during this analysis.

All four runs evaluated at the beginning of turn 200. The new run was interrupted later when the user reports Shadow died. This is a valid partial checkpoint comparison; its turn-250 test remains incomplete. Same map, leaders and starting research; CSC with standard AI, Online/Prince/vanilla Standard, TAR/RH disabled.

| Metric | Baseline | V1 modifiers | Native bonus/river | RH Builder values |
|---|---:|---:|---:|---:|
| Cities | 43 | 51 | 51 | 49 |
| Population | 427 | 568 | 583 | 634 |
| Owned unpillaged improved plots | 145 | 237 | 266 | 380 |
| Improved plots per city | 3.37 | 4.65 | 5.22 | 7.76 |
| Improved plots per 100 population | 34.0 | 41.7 | 45.6 | 59.9 |
| Recorded improvement additions | 258 | 394 | 437 | 588 |

## Bakers

| Metric | Baseline | V1 modifiers | Native bonus/river | RH Builder values |
|---|---:|---:|---:|---:|
| Completed Quarters | 37 | 45 | 44 | 44 |
| Chose mapped Base when available | 13/22 (59%) | 16/26 (62%) | 20/22 (91%) | 22/26 (85%) |
| Endpoint mapped Base access | 10/37 (27%) | 8/45 (18%) | 12/44 (27%) | 14/44 (32%) |
| Adjacent owned Base plots improved | 4/11 (36%) | 4/8 (50%) | 8/15 (53%) | 12/16 (75%) |
| Adjacent owned Specialty plots improved | 1/2 (50%) | 2/2 (100%) | 2/2 (100%) | 0/0 |
| Covered supporting material plots | 2/14 (14%) | 10/19 (53%) | 8/23 (35%) | 5/23 (22%) |
| Base improvement median wait among completed follow-ups | 31.5 | 10 | 37.5 | 10 |
| Later sales chose Quarter when available | 6/15 (40%) | 43/44 (98%) | 50/51 (98%) | 39/45 (87%) |
| Stage 2 / 3 / 4 buildings | 34 / 8 / 5 | 43 / 22 / 7 | 41 / 18 / 4 | 43 / 24 / 11 |

## Tailors

| Metric | Baseline | V1 modifiers | Native bonus/river | RH Builder values |
|---|---:|---:|---:|---:|
| Completed Quarters | 19 | 25 | 29 | 23 |
| Chose mapped Base when available | 1/1 (100%) | 1/4 (25%) | 4/4 (100%) | 1/1 (100%) |
| Endpoint mapped Base access | 1/19 (5%) | 0/25 (0%) | 3/29 (10%) | 1/23 (4%) |
| Adjacent owned Base plots improved | 0/1 (0%) | 0/0 | 1/3 (33%) | 1/1 (100%) |
| Adjacent owned Specialty plots improved | 0/0 | 0/0 | 0/0 | 0/0 |
| Covered supporting material plots | 0/1 (0%) | 1/1 (100%) | 1/4 (25%) | 0/1 (0%) |
| Base improvement median wait among completed follow-ups | None | None | 4 | None |
| Later sales chose Quarter when available | 9/17 (53%) | 25/29 (86%) | 47/51 (92%) | 37/44 (84%) |
| Stage 2 / 3 / 4 buildings | 15 / 3 / 4 | 21 / 12 / 6 | 26 / 19 / 7 | 22 / 17 / 9 |

## Service source cities

| Metric | Baseline | V1 modifiers | Native bonus/river | RH Builder values |
|---|---:|---:|---:|---:|
| CSC_BAKERS_STAGE_2_EFFECT_GROWTH | 2 | 3 | 7 | 7 |
| CSC_BAKERS_STAGE_3_EFFECT_HOUSING | 0 | 4 | 2 | 2 |

## Improvement density over time

| Turn | Baseline | V1 modifiers | Native bonus/river | RH Builder values |
|---|---:|---:|---:|---:|
| 50 | 3.21 | 2.60 | 2.24 | 3.81 |
| 100 | 3.48 | 3.47 | 2.61 | 5.47 |
| 150 | 3.72 | 4.56 | 3.93 | 7.07 |
| 200 | 3.37 | 4.65 | 5.22 | 7.76 |

Values are owned unpillaged improved plots per city.

## Builder telemetry — new run only

| Turn | Alive | Charges remaining | Added to map | Trained | Purchased |
|---|---:|---:|---:|---:|---:|---:|
| 1 | 0 | 0 | 0 | 0 | 0 |
| 50 | 11 | 20 | 38 | 32 | 3 |
| 100 | 20 | 43 | 109 | 85 | 14 |
| 150 | 27 | 64 | 171 | 125 | 26 |
| 200 | 26 | 55 | 230 | 145 | 58 |

## Interpretation limits

- One matched seed with diverging later wars, expansion and research. Matching the time horizon does not isolate causal effects.
- Both improvement valuation and Builder production priority changed together. Historical runs lack Builder production/remaining-charge telemetry; production totals cannot be compared directly.
- Added-to-map events can include captures/grants. Training and purchase event totals are reported separately; operation starts are not completed work.
- Improved plots count all owned unpillaged improvements, including non-Builder improvements. Recorded improvement additions may include rebuilding/captures and are not distinct Builder charges.
- Quarter improvement fractions concern owned mapped resource plots next to completed Quarters, deduplicated within each industry. Opportunities are owned native plot-legal alternatives; affordability is not proven.
- Service source counts are city/Service combinations and need not represent distinct cities.
- No post-200 state is inferred from the archived data; autosaves232/233/234 remain preserved for possible later use.
