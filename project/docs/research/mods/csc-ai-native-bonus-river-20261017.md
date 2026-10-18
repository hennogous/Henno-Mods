# CSC native bonus-resource and river tuning — matched-seed trial

17 October 2026. One unchanged retry completed to the beginning of turn 250. **Actual Base placement improved strongly in this seed; Builder follow-through and resource preservation remain limiting.** This is an exploratory combined-treatment comparison, not proof across maps or evidence of deliberate Service planning.

## Treatment and setup

Implemented Bakers/Tailors only: native private-yield adjacency +12 per adjacent bonus-class resource, +4 native river access, existing reciprocal sales adjacency +10, and major-civ improvement preference 50 (previously 25). No exact material modifier, marker feature, new real yield, research preference or scripted AI construction. Resource classes include every bonus resource, irrespective of actual Quarter mappings; real Service rules remain unchanged.

Map seed 830102, game seed 940104; Small 74×46 Continents, Online, Prince, vanilla Standard resources, six majors/nine city states. CSC material assistance v3 and animals enabled; TAR/RH/M&C disabled. Kristina, Ludwig, Amanitore, Dido, Lady Trieu and Pericles. All 3,404 starting tiles matched the baseline over 13 world fields; player identities and starting research matched. Quarter/building definitions, material tags/configuration and global pseudo-yields matched. The original read-only observer v3 was unchanged.

## Interpretation

- Bakers chose actual owned Base access 24/27 (89%), versus 14/25 baseline and 16/28 v1. Restricting to non-human-flagged players gives 20/22, versus 12/21 and 12/23; the result is not driven solely by the local autoplay player.
- Bakers chose Base plus sales 21/24 (88%), versus 11/21 and 16/26. River choice rose to 20/27 (74%), versus 10/22 and 13/23; with mixed river/non-river alternatives it was 16/23 (70%), versus 7/19 and 8/18.
- The sales tradeoff is visible: Bakers chose sales adjacency 49/55 (89%), below v1's 54/54 but above the baseline's 31/46. Later sales still chose Bakers adjacency 56/57 (98%).
- Tailors chose Base in 5/5 cases, versus 1/1 baseline and 1/4 v1. These denominators remain small. Only two completed Tailors retained Base access, and neither adjacent Base plot was improved. No Tailors Service source was active.
- Active Bakers Growth Service cities rose 1 → 2 → 6; Housing was 0 → 3 → 3. No other native Service source flags were active, and both-class owned access was zero for both Quarters at the endpoint. These observations do not establish Service-aware planning.
- Owned improved plots were 223 → 331 → 357, but cities/population also grew. Improved plots per city were 4.65 → 5.81 → 5.85 and per 100 population 40.5 → 48.3 → 48.6. There is no clear additional improvement-density benefit from raising the preference from 25 to 50 in this combined test.
- Bakers' adjacent owned Base improvement share was 2/9 → 3/6 → 6/15. Ten original supporting plots were later lost under districts, matching v1's count; exposure was larger (28 original unique supporting plots versus 19 v1). The covered share was 36% baseline, 53% v1, 36% new. Material preservation is still unresolved.
- The approximation has substantial false matches at the endpoint: 8/21 bonus-adjacent Bakers and 10/12 bonus-adjacent Tailors had only unmapped bonus neighbours. These are endpoint geography counts, not reconstructed placement-time choices.

Keep this as a promising first candidate for placement. More matched seeds should precede coefficient calibration. The remaining problems are supplying existing Quarters with improvements and preserving resources; increasing the broad improvement preference alone has not demonstrated a distinct solution here.

## Run reliability and verification

The first attempt crashed natively after the last Tuner report at 92, with an autosave through 94. The user confirmed the Firaxis Crash Reporter. That attempt is excluded; logs, commands and four autosaves remain in `../trial/`. Cause is unknown. No installed CSC file changed during that attempt, and no gameplay SQL error was logged. The unchanged retry passed that point and completed. A later pause at 168 recovered without restarting or modifying the game.

Two brief controller reconnects archived already-frozen checkpoints through 100 and 200 while native autoplay continued. No gameplay state or AI choices were scripted; the executed read-only commands are retained. The first-activation benchmark census and settled save census at 250 are identical. Eleven snapshots, 1,431 events, zero observer errors, two saves, installed gameplay and controller/tuning source hashes passed verification. Final logs contain no gameplay DB errors. An initial preference-restoration command lacked an acknowledgement during the menu transition; a separate restore and fresh native check succeeded for all 141 unique mod IDs and auto-start=false. Civ is left at its background main menu; no controller remains active.

The endpoint prospective native probe matched the bonus/river formula in all 29 district-isolated plot-legal candidate rows, including 14 with a nonzero bonus-resource signal. None of those isolated rows had river access, so this does not independently test river scoring. It verifies prospective bonus adjacency rather than a complete internal AI score. The gameplay DB and four UI contexts passed the startup rule/filter checks. The marker experiment is a modified 20-turn fixture and is excluded from the numerical natural-game comparison.

Evidence: `C:/Users/Shadow/Desktop/Codex/csc-ai-native-bonus-river-20261017/retry-01/`. Key records: `comparison.json`, CSVs, `validation.json`, `native-database-validation.json`, `placement-probe.json`, `preferences-restored.json`, `completion-recovery.json`, command transcripts, source hashes, initial/final saves and logs. The initial map, resource catalog and earlier matched trials are retained unchanged.

Controls: [paired baseline](csc-ai-paired-standard-20261016.md), [v1 modifier trial](csc-ai-tuning-v1-20261017.md), [rejected marker experiment](csc-ai-markers-rejected-20261017.md). Implementation: [current AI tuning](../../integrations/csc-ai-tuning.md).

## Detailed comparison

| Metric | Baseline | V1 modifiers | Native bonus/river |
|---|---:|---:|---:|
| Cities | 48 | 57 | 61 |
| Population | 551 | 686 | 735 |
| Owned unpillaged improved plots | 223 | 331 | 357 |
| Improved plots per city | 4.65 | 5.81 | 5.85 |
| Improved plots per 100 population | 40.5 | 48.3 | 48.6 |

## Bakers

| Metric | Baseline | V1 modifiers | Native bonus/river |
|---|---:|---:|---:|
| Completed | 45 | 49 | 51 |
| Chose actual Base when available | 14/25 (56%) | 16/28 (57%) | 24/27 (89%) |
| Chose actual Base + sales when available | 11/21 (52%) | 16/26 (62%) | 21/24 (88%) |
| Chose river when available | 10/22 (45%) | 13/23 (57%) | 20/27 (74%) |
| Chose river with mixed alternatives | 7/19 (37%) | 8/18 (44%) | 16/23 (70%) |
| Chose actual Base + river when available | 5/11 (45%) | 3/10 (30%) | 12/13 (92%) |
| Quarter chose sales when available | 31/46 (67%) | 54/54 (100%) | 49/55 (89%) |
| Later sales chose Quarter when available | 9/28 (32%) | 49/51 (96%) | 56/57 (98%) |
| Endpoint actual Base | 8/45 (18%) | 6/49 (12%) | 13/51 (25%) |
| Endpoint river | 10/45 (22%) | 11/49 (22%) | 21/51 (41%) |
| Endpoint non-City-Center sales | 9/45 (20%) | 37/49 (76%) | 38/51 (75%) |
| Adjacent owned Base plots improved | 2/9 (22%) | 3/6 (50%) | 6/15 (40%) |
| Supporting material plots later covered by districts | 5 | 10 | 10 |
| Covered supporting plots / all original supporting plots | 5/14 (36%) | 10/19 (53%) | 10/28 (36%) |
| Endpoint bonus adjacency | 13/45 (29%) | 9/49 (18%) | 21/51 (41%) |
| Endpoint bonus adjacency, all bonus neighbours unmapped | 5/13 (38%) | 3/9 (33%) | 8/21 (38%) |
| Endpoint bonus adjacency without actual owned Base | 5/13 (38%) | 3/9 (33%) | 8/21 (38%) |
| Stage 2 / 3 / 4 buildings | 44 / 15 / 9 | 45 / 30 / 16 | 46 / 27 / 15 |

## Tailors

| Metric | Baseline | V1 modifiers | Native bonus/river |
|---|---:|---:|---:|
| Completed | 22 | 29 | 33 |
| Chose actual Base when available | 1/1 (100%) | 1/4 (25%) | 5/5 (100%) |
| Chose actual Base + sales when available | 0/0 | 0/2 (0%) | 3/3 (100%) |
| Chose river when available | 5/12 (42%) | 6/16 (38%) | 11/20 (55%) |
| Chose river with mixed alternatives | 5/12 (42%) | 6/16 (38%) | 10/19 (53%) |
| Chose actual Base + river when available | 0/0 | 0/0 | 0/0 |
| Quarter chose sales when available | 2/8 (25%) | 22/23 (96%) | 11/11 (100%) |
| Later sales chose Quarter when available | 12/25 (48%) | 27/32 (84%) | 51/58 (88%) |
| Endpoint actual Base | 1/22 (5%) | 0/29 (0%) | 2/33 (6%) |
| Endpoint river | 4/22 (18%) | 6/29 (21%) | 10/33 (30%) |
| Endpoint non-City-Center sales | 10/22 (45%) | 26/29 (90%) | 27/33 (82%) |
| Adjacent owned Base plots improved | 1/1 (100%) | 0/0 | 0/2 (0%) |
| Supporting material plots later covered by districts | 0 | 0 | 1 |
| Covered supporting plots / all original supporting plots | 0/1 (0%) | 0/0 | 1/4 (25%) |
| Endpoint bonus adjacency | 5/22 (23%) | 7/29 (24%) | 12/33 (36%) |
| Endpoint bonus adjacency, all bonus neighbours unmapped | 4/5 (80%) | 7/7 (100%) | 10/12 (83%) |
| Endpoint bonus adjacency without actual owned Base | 4/5 (80%) | 7/7 (100%) | 10/12 (83%) |
| Stage 2 / 3 / 4 buildings | 19 / 7 / 5 | 26 / 15 / 9 | 30 / 22 / 14 |

## Native Service source cities

| Property | Baseline | V1 modifiers | Native bonus/river |
|---|---:|---:|---:|
| CSC_BAKERS_STAGE_2_EFFECT_GROWTH | 1 | 2 | 6 |
| CSC_BAKERS_STAGE_3_EFFECT_HOUSING | 0 | 3 | 3 |

## Actual Base choices excluding human-flagged player 0

| Quarter | Baseline | V1 modifiers | Native bonus/river |
|---|---:|---:|---:|
| Bakers | 12/21 (57%) | 12/23 (52%) | 20/22 (91%) |
| Tailors | 0/0 | 0/3 (0%) | 4/4 (100%) |

## Native probe

{"turn": 250, "status": "observed", "isolated_checks": 29, "isolated_matches": 29, "errors": {}, "isolated_nonzero_checks": 14, "isolated_nonzero_matches": 14, "isolated_bonus_checks": 14, "isolated_river_checks": 0}

## Limits

- One matched starting world; later expansion, wars and material retention diverge.
- Combined treatment: bonus, river and improvement weights are not isolated.
- Placement alternatives are owned native-plot-legal scans at most one turn old; affordability and future purchases are not proven.
- Bonus proxy statistics describe the endpoint, not resource state at the time of placement.
- Marker experiment is a modified 20-turn fixture and is excluded from the natural-game comparison.
- Primary tables retain all six autoplay majors. V1 conditional material modifiers excluded human-flagged player 0; native signals apply during its autoplay too. Nonhuman-only choices are retained separately.
