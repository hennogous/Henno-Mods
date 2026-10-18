# CSC latest resource/AI setup — turn250 snapshot results

One Online/Prince/vanilla Standard game reached turn250 with resource pass4, native placement12/4/10 and Builder settings90/900. CSC enabled; TAR/RH disabled. Original map seed830102 and game seed940104; six original leaders. The previous comparison used resource pass3 with the same AI settings.

**Archive caveat:** the final named save was not confirmed. This is a failed save/export step, not evidence of a gameplay crash. All11 snapshots through250 and six Builder censuses passed offline checks. The final settled250 census is identical to the primary250 snapshot. Autosaves248/249/250 and failure logs are preserved. Original141 mod flags and auto-start false were restored. Full-trial validation is not claimed.

| Metric | Previous200 | Latest200 | Latest250 |
|---|---:|---:|---:|
| Cities | 49 | 47 | 57 |
| Population | 634 | 537 | 702 |
| Owned unpillaged improved plots | 380 | 315 | 370 |
| Improved plots/city | 7.76 | 6.7 | 6.49 |
| Improved plots/100 population | 59.9 | 58.7 | 52.7 |

## Bakers

| Metric | Previous200 | Latest200 | Latest250 |
|---|---:|---:|---:|
| Completed | 44 | 44 | 46 |
| Chose mapped Base when available | 22/26 (85%) | 17/21 (81%) | 22/26 (85%) |
| Base access at endpoint | 14/44 (32%) | 15/44 (34%) | 12/46 (26%) |
| Both materials at endpoint | 0/44 (0%) | 0/44 (0%) | 0/46 (0%) |
| Adjacent owned Base improved | 12/16 (75%) | 10/16 (62%) | 7/13 (54%) |
| Adjacent owned Specialty improved | 0/0 | 2/2 (100%) | 2/2 (100%) |
| Sales adjacency | 42/44 (95%) | 44/44 (100%) | 45/46 (98%) |
| Non-center sales adjacency | 33/44 (75%) | 22/44 (50%) | 26/46 (57%) |
| Later sales chose Quarter when available | 39/45 (87%) | 27/33 (82%) | 33/40 (82%) |
| Supporting material plots covered by districts | 5/23 (22%) | 6/19 (32%) | 10/22 (45%) |
| Stage2 /3 /4 buildings | 43 / 24 / 11 | 40 / 17 / 9 | 43 / 33 / 15 |

## Tailors

| Metric | Previous200 | Latest200 | Latest250 |
|---|---:|---:|---:|
| Completed | 23 | 20 | 25 |
| Chose mapped Base when available | 1/1 (100%) | 3/7 (43%) | 5/9 (56%) |
| Base access at endpoint | 1/23 (4%) | 1/20 (5%) | 2/25 (8%) |
| Both materials at endpoint | 0/23 (0%) | 0/20 (0%) | 0/25 (0%) |
| Adjacent owned Base improved | 1/1 (100%) | 0/1 (0%) | 1/2 (50%) |
| Adjacent owned Specialty improved | 0/0 | 0/0 | 0/0 |
| Sales adjacency | 23/23 (100%) | 18/20 (90%) | 22/25 (88%) |
| Non-center sales adjacency | 23/23 (100%) | 18/20 (90%) | 22/25 (88%) |
| Later sales chose Quarter when available | 37/44 (84%) | 34/44 (77%) | 40/51 (78%) |
| Supporting material plots covered by districts | 0/1 (0%) | 2/3 (67%) | 3/5 (60%) |
| Stage2 /3 /4 buildings | 22 / 17 / 9 | 17 / 8 / 5 | 23 / 15 / 10 |

## Active Service source cities

| Service | Previous200 | Latest200 | Latest250 |
|---|---:|---:|---:|
| CSC_BAKERS_STAGE_2_EFFECT_GROWTH | 7 | 7 | 4 |
| CSC_BAKERS_STAGE_3_EFFECT_HOUSING | 2 | 1 | 2 |

## Builder telemetry

Cumulative events use the original six-player cohort, retaining player0 after defeat. Current alive/charge censuses cover surviving units. The original analyzer used the current living-player list, which would incorrectly drop defeated-player production from cumulative totals.

| Census | Trained | Purchased | Alive | Charges | Added to map |
|---|---:|---:|---:|---:|---:|
| Previous200 | 145 | 58 | 26 | 55 | 230 |
| Latest1 | 0 | 0 | 0 | 0 | 0 |
| Latest50 | 27 | 4 | 14 | 28 | 36 |
| Latest100 | 72 | 7 | 16 | 37 | 91 |
| Latest150 | 117 | 18 | 26 | 69 | 153 |
| Latest200 | 144 | 44 | 39 | 101 | 229 |
| Latest250 | 161 | 69 | 33 | 88 | 280 |

## Interpretation limits

- One seed; same initial terrain, roster and research; resource placement intentionally differs on16 tiles.
- Unchanged AI90/900 and native placement12/4/10; this does not isolate AI effects.
- Prior run has no250 endpoint; compare at common200.
- Snapshots validated independently; final named save failed. Autosaves248/249/250 preserved but not load-tested.
- Builder additions can include capture/grants; training and purchases are separate events.
- Owned improvements include non-Builder improvements. Services count active city/Service combinations.

## Findings

At common200, improvement density is6.70/city versus7.76 previously, but58.7 versus59.9 per100 population. The new world has47 cities/537 population versus49/634. AI settings are unchanged, so this is a divergent resource/world trial, not evidence of an AI-tuning regression. Baker adjacent Base improvement is10/16 versus12/16; Tailor0/1 versus1/1. Active Services are7 Baker Growth and1 Housing versus7/2, with no Tailor Services.

Extra Tailor geography increased observed decisions with an owned legal Base alternative from1 to7 by200, but only3/7 chose Base (previous1/1). By250 it is5/9, yet only2/25 completed Tailors retain Base access;3/5 historically supporting material plots were covered by districts. None have both classes. These denominators are small and the caches do not prove affordability.

At250,9 of11 Tailors next to any bonus resource have only bonus types unmapped to Tailors. Native bonus-class guidance remains a broad proxy. More map resources alone have not solved mapped-material placement, material preservation or Tailor Services on this seed. Later sales placements still use adjacency often:33/40 for Bakers and40/51 for Tailors.

Evidence: C:/Users/Shadow/Desktop/Codex/csc-ai-density-v4-20261017/trial. Independent checks: snapshot-validation.json. Original failed job-status/batch files are preserved; no game was restarted.
