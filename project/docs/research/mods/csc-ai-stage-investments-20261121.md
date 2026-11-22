# CSC research and later-stage investment guidance

Problems 6.1, 7.1–7.2, 8.1, 9.1, 10.1–10.2, 11.1–11.2 and 12.1 are in scope for Bakers and Tailors. The strategy decisions in 6.2, 9.2 and 12.2 are deferred. The candidate reuses the native research, building and Wonder-site comparisons in CE. Gameplay SQL and the CE DLL are unchanged for this slice.

```mermaid
flowchart LR
    A[Gameplay definitions and live chain facts] --> B[Shared economic model]
    B --> C[Service and producer unlock offers]
    B --> D[Producer and customer building offers]
    A --> E[Wonder footprint and supplier offers]
    C --> F[Native research goal comparison]
    D --> G[Native building and production comparisons]
    E --> H[Native Wonder tile comparison]
```

| Decision | Candidate policy | Evidence |
| --- | --- | --- |
| 6.1, 9.1, 12.1 Service unlock | Offer the one remaining topic when the producer, customer and authored material requirements are already met. Pool distinct chains and combine Housing at the receiving city before pricing it. | Ordinary Fractal verified the Feudalism comparison, unlock and Storekeeper. Québec verified the same sequence for Opera and Ballet and Stage Manager. A ready Stage 3 chain with an outstanding civic still needs a targeted replay. |
| 7.1, 7.2 Stage 3 producer | From population 7, price the unlock against the expected exchange. From population 10, bid for the eligible building against other orders. Price working venues and the modeled local returns. | Offline tests cover the population gates, live eligibility and queued orders. Native Bakery construction verified. Unlock follow-through is open. |
| 8.1, 11.1 Customer building | Price an eligible mapped adjacent customer building for its operating producers, including unique replacements. Group links that share one customer order and round their population return together. | Tests cover shared recipients, population rounding and replacements. On ordinary Fractal, Urumqi's Market and Qaraqorum's Zoo both received their exact bids, completed and paid both sides of the exchange. |
| 10.1, 10.2 Stage 4 producer | Use the same population gates and require feasible Base and Specialty supply. Supplier readiness constrains material returns. Each distinct missing new improvement carries a share of a Builder's cost. | Offline tests cover missing or late supply, the charge cost, and repair. A treatment Café completed sooner. Humanism reached the civic comparison and completed at the same time in both arms. |
| 11.2 Wonder site | Use the existing native Wonder-site bid on adjacent owned tiles with viable Base and Specialty. Give more weight as each class becomes operational and preserve material protection. | Offline tests cover material admission and plot scoping. Live comparison, placement and exchange are open. |

Astra recommended pricing the effect of one physical queue order at a time through the existing ledger. The controlled replays will check how the applied bid competes with other research and production, then follow selection through to construction or a realised Service. The full games will keep Problem 3 supplier timing visible for both material classes.

## Fractal checkpoint from turn 150 to 165

Both arms reloaded the same verified ordinary save and used Steam GameCore build 26595377, the same CE package and identical gameplay content. The treatment differed in five existing CSC Lua files. The control retained the preceding CSC guidance for Problems 1–5. Both arms reached turn 165 and restored the local mod settings.

The treatment published 40 Stage 3 producer offers and 50 Stage 4 producer offers across the replay, with no later customer or research offers. Native queue receipts include Bakery and Café comparisons. Angkor Wat's Café score rose from 98,551 to 114,935 Q8 in one queue comparison. Both arms chose a Trader at turn 154. At turn 157 the treatment chose the Café, while the control chose a Theater Square project. The control first logged a Café production preference at turn 161. The treatment Café was complete at turn 165 on Bakers plot 2869 with working Flax and Berries. Its adjacent customer was the Stage 2 Granary, so this case qualifies producer construction while the later customer exchanges still need their own cases.

At Angkor Thom, the Bakery's queue comparison rose from 222,474 to 238,858 Q8. The Bakery appeared in the turn-153 production choice log and completed with 107.6 Production against an 80 cost on turn 154. Both arms built it. The treatment moved the Café ahead of the project while leaving the earlier Trader and this Bakery outcome intact.

| Working producers at turn 165 | Previous guidance | Combined candidate |
| --- | ---: | ---: |
| Stage 2 | 12 | 13 |
| Stage 3 | 7 | 7 |
| Stage 4 | 2 | 3 |

The 64-utility ceiling applied to 87 of 90 producer offers. Later replays retain the raw prices and per-building native receipts to assess calibration. Raw evidence is under `Desktop/Codex/csc-ai-stage6-12-20261121/fractal-150-165-v2`.

## Fractal checkpoint from turn 100 to 115

The treatment published 13 Stage 4 producer research offers for player 5's Humanism. The native civic comparison recorded five uses. The applied amounts ranged from 12,998 to 14,335 Q8. The stock goal stayed ahead at each comparison. In the last recorded comparison, Humanism was the immediate research step toward the higher-scoring goal. Both arms owned Humanism by the turn-113 observation. This is a representative research bid that reached the selector and deferred to ordinary priorities.

The same replay published 52 later building offers and recorded 22 exact building receipts. The passive Service observer read 33 gameplay effect attachments with no catalogue omissions. It verified one operating Storekeeper link for each of the 14 sampled turns in both arms. Raw evidence is under `Desktop/Codex/csc-ai-stage6-12-20261121/fractal-100-115`.

Astra identified Québec's ready Stage Manager as the clearest Service-unlock replay. The city starts with a working Fashion House, adjacent Amphitheater, Flax and Silver and still needs Opera and Ballet. A separate turn-200 Fractal checkpoint has a live Café at Bakers plot 1503 and an adjacent Entertainment Complex at 1576 missing a mapped customer building. These are the next targeted replay cases.

## Québec's Stage Manager from turn 250 to 265

The original turn-250 world already had the working Fashion House at 545, Flax at 544, Silver at 620 and the adjacent Amphitheater at 471. Québec's player lacked Opera and Ballet. Both arms preserved those facts and let the AI research normally.

The treatment published 14 Opera and Ballet offers worth 12,373 Q8 for this ready chain. The native civic receipt identified this topic in five publication windows. Several other civic goals stayed ahead. In the turn-263 receipt, Opera and Ballet was the stock and adjusted goal and the immediate step. Both arms owned the civic and activated the Stage Manager effect on the same Amphitheater at turn 264. The native Service watcher observed all 14 interior turns. This establishes delivery and actual operation for 12.1, with equal timing in the two arms.

Raw evidence is under `Desktop/Codex/csc-ai-stage6-12-20261121/quebec-250-265`.

## Missing customers from turn 200 to 215

The ordinary replay kept the Café at plot 1503 and Entertainment Complex at 1576 intact. Neither arm built the mapped Zoo, and the treatment offered no bid on that venue. A controlled replay can supply its Arena prerequisite and verify the Zoo's immediate eligibility before judging delivery.

The same treatment found a different opportunity for player 5's Market. It published 12 customer offers worth 16,384 Q8 each against a raw estimate of 26,940 Q8. Native receipts show both queue and ordinary nominations applied to that Market. The Market remained out of production during the sample, so the controlled Market replay exercises selection and the realised exchange separately.

The CSC publisher averaged 2.046 seconds per turn in control and 2.097 seconds in treatment over 15 complete measurements. Maximums were 2.502 and 2.330 seconds respectively. This short replay measures the whole publisher during each world’s play. The ordinary campaign will measure longer-run overhead. Raw evidence is under `Desktop/Codex/csc-ai-stage6-12-20261121/entertainment-200-215`.

## Early research and the controlled Market rebuild

In the turn-50 trial both arms received the same missing Water Mill at Bakers plot 2497. The preparation verified two working Base suppliers, its adjacent Granary and unowned Feudalism and Guilds. The treatment sent and reached the native comparisons for both topics. Feudalism completed and Storekeeper activated at another intact Quarter for the same player on turn 71 in both arms. Both prepared suppliers had stopped working by the turn-72 census. The Guilds receipt on turn 71 identifies it as the immediate step toward a longer goal. The replay ended before it recorded the completed civic.

In the Market fixture, removing the Stage 3 customer at plot 913 removed both observed population payments. The treatment's exact offer reached both building selectors in player 5's city, and neither arm rebuilt this Market by turn 215. The same treatment offered a Market in Mahendraparvata, where CE applied the bid in the production selector and the queue finished the Market on turn 205. The control also built that Market. The ordinary campaign now logs positive population-payment quantities for both sides of each assembled Stage 3 and 4 exchange.

Raw evidence is under `Desktop/Codex/csc-ai-stage6-12-20261121/storekeeper-50-72` and `market-200-215-v2`.

## Legal Zoo and Wonder qualification

Adding only the missing Arena on both copies made the Zoo eligible at the Entertainment Complex beside the Café. The treatment then made 15 offers for that exact Zoo. Three receipts show a queue write, and two show a write in the ordinary nomination selector. Both cities still pursued other work through turn 215. This verifies delivery for 11.1 while leaving construction and payment open. Keep the current 64-utility cap while observing more opportunities.

The same archived map had no admissible Bolshoi footprint beside a Tailors layout with both material classes in the Wonder scout. That case ended before any placement score comparison. The ordinary runs will record Wonder placement and exchange quantities and provide new candidate worlds for a matched placement case. Raw evidence is under `Desktop/Codex/csc-ai-stage6-12-20261121/zoo-200-215` and `wonder-200-220`.

The Sacristan trials lacked a valid starting opportunity. The first city's adjacent plots did not admit a Holy Site. The second archive already had Divine Right for the player with a supplied Tailors and Temple. Both setups ended before editing a copy. Keep 9.1 open and look for unowned topics in the ordinary samples.

REA and Ghidra also established a narrow experimental reset for this case. On Steam XP2 `4de40abf`, the Lua `SetCivic` entry at RVA `6f12f0` forwards the Boolean to the native setter at `284870`. Clearing the ownership flag returns before the completion broadcast. The `SetCulturalProgress` thunk at `6f13a0` uses the numeric Q8 argument converter at `6f0450` and the progress writer at `284bb0`. A diagnostic can clear both fields on copies of the same archived world, then create the missing Tailor so its attachment was never active under the old civic state. The actual AI must choose and complete the civic again. This setup has no role in ordinary play or shipping guidance.

## Preselected full-game pairs

Each pair uses a fresh Small Online game through turn 250 on the shared controller, with the same map and game seed, gameplay and UI mods, and pinned Firaxis GameCore and CE build. The control retains CSC gameplay with guidance and private customer adjacency disabled. The treatment runs the integrated CSC policy. Both use stock AI. Seeds are fixed before qualification begins.

| Map | Map seed | Game seed |
| --- | ---: | ---: |
| Continents | 793412556 | 1390346751 |
| Fractal | 28111119 | 38111119 |
| Pangaea | 27061117 | 37061117 |

Report placement, suppliers, producer and customer completions, Wonders, working exchanges, active Service turns, unlock timing, missed opportunities, competing work and guidance processing time for each pair. Count Service duration from active native effects on specific recipients.

Campaign artifacts and the frozen package are under `Desktop/Codex/csc-ai-stage6-12-20261121/campaign`.

## Continents through turn 250

Both games matched the opening map, roster, start plots and units and reached the endpoint. The stock arm kept CSC gameplay and withheld the publisher and private customer placement bonuses. Both arms sampled 200 shared Service turns. The UI watcher omits a number of controller handoff turns, so the table reports active links only on shared clocks.

| Turn-250 count | Bakers stock | Bakers combined | Tailors stock | Tailors combined |
| --- | ---: | ---: | ---: | ---: |
| Completed Quarters | 13 | 14 | 13 | 3 |
| Working Base supplier links | 2 | 15 | 1 | 3 |
| Working Specialty supplier links | 0 | 3 | 0 | 0 |
| Stage 2 / 3 / 4 working producers | 11 / 8 / 5 | 13 / 11 / 3 | 9 / 8 / 6 | 3 / 1 / 1 |
| Stage 2 / 3 / 4 working customer hosts | 4 / 0 / 0 | 12 / 7 / 1 | 0 / 1 / 2 | 0 / 2 / 3 |
| Stage 2 physical exchange pairs | 3 | 12 | 0 | 0 |
| Stage 3 / 4 exchanges with positive quantities on both sides | 0 / 0 | 5 / 0 | 0 / 0 | 1 / 1 |
| Active Stage 2 / 3 / 4 Service link-turns | 54 / 0 / 0 | 801 / 154 / 0 | 0 / 0 / 0 | 0 / 47 / 0 |

The combined arm observed 11 distinct Storekeeper, six Innkeeper and one Sacristan links. A Tailors Fashion House at 2692 paid an adjacent Amphitheater at 2693 in both directions at the endpoint. Both arms had zero mapped Wonder customer links. The combined arm published 590 later building offers and logged 234 exact receipt rows. This seed produced no later producer or Service research offers and no Wonder offers. The combined publisher's wall time averaged 1.195 seconds and reached a maximum of 2.887 seconds across 250 publications. The separately timed managed native scoring averaged 14.13 milliseconds and reached 27.97 milliseconds.

## Fractal through turn 250

Both arms reached turn 250 from the verified common opening. The Service watcher provided 199 shared clocks.

| Turn-250 count | Bakers stock | Bakers combined | Tailors stock | Tailors combined |
| --- | ---: | ---: | ---: | ---: |
| Completed Quarters | 13 | 13 | 9 | 5 |
| Working Base supplier links / adjacent links | 0 / 2 | 12 / 15 | 2 / 2 | 5 / 6 |
| Working Specialty supplier links / adjacent links | 0 / 1 | 2 / 4 | 0 / 1 | 2 / 2 |
| Stage 2 / 3 / 4 working producers | 11 / 8 / 5 | 13 / 10 / 8 | 7 / 7 / 4 | 3 / 3 / 3 |
| Stage 2 / 3 / 4 working customer hosts | 5 / 2 / 0 | 9 / 5 / 1 | 0 / 1 / 0 | 0 / 2 / 2 |
| Stage 2 physical exchange pairs | 3 | 9 | 0 | 0 |
| Stage 3 / 4 exchanges with positive quantities on both sides | 2 / 0 | 4 / 1 | 1 / 0 | 2 / 1 |
| Active Stage 2 / 3 / 4 Service link-turns | 0 / 0 / 0 | 573 / 80 / 0 | 0 / 0 / 0 | 0 / 193 / 0 |

The combined arm observed seven distinct Storekeeper, four Innkeeper and two Sacristan links. None of the four completed ordinary games had a mapped Wonder customer link. On Fractal the treatment published 919 later building offers and logged 340 exact receipt rows. The publisher averaged 1.325 seconds and peaked at 2.410 seconds across 250 publications. The separate native managed-cell timing averaged 15.74 milliseconds and peaked at 28.83 milliseconds.

- **6.1, Feudalism.** Player 3 received eight offers from turn 62 through 69. The native turn-68 receipt records Feudalism as the immediate research step toward the longer goal. Player 3 first owned Feudalism at the turn-71 observation, when Storekeeper also operated from the offered Bakers source `655367`.
- **8.1, Market.** Player 4's Urumqi (city `262147`) published a Market offer on turn 203. The next receipt records the exact queue write at 16,384 Q8. The native chooser nominated it on turn 203, and the queue reached 117.6 of 60 production on turn 205. The turn-225 and turn-250 censuses record the Bakery at 1823 and Market at 1748 paying 26 units on each side. The turn-200 census precedes the exchange.
- **11.1, Zoo.** Qaraqorum (player 4, city `65536`) went from no Zoo exchange to a native Zoo submission on turn 209. The exact receipt records a queue write and the ordinary nomination receipt records a write. Production reached 245 of 180 on turn 213. The turn-250 census records the Café at 2189 and Zoo at 2115 paying four units each.
- **11.2, Wonders.** Repeated publications produced 924 offers and zero exact native matches. The CE counter records an exact match before checking the score sign or applying the cap, so the next check is candidate admission. Astra traced two natural orders. Angkor Thom built Broadway two tiles from its Tailors, with both plots touching the Quarter and its Theater already occupied. Qaraqorum had both materials earlier and later pursued Sydney Opera House. The nearest Harbor was three tiles from the Quarter, beyond the range for one site to touch both. Scout the turn-200 checkpoint for an admissible footprint before evaluating the premium.

Evidence is under `Desktop/Codex/csc-ai-stage6-12-20261121/campaign/fractal-combined` in the native receipts, `AI_CityBuild.csv`, `City_BuildQueue.csv`, `full-census-{200,225,250}.json` and `observed-services.json`.

### Supplier timing across the first two pairs

Among buyers with legal Base work still needed when a supplier first became actionable, working Base at buyer completion plus ten turns went from 2 of 3 to 3 of 8 on Continents and from 0 of 3 to 5 of 10 on Fractal. All eight on-time treatment cases were Bakers. Tailors reached zero of three across the two treatment arms in that cohort, with more Tailors already supplied when first actionable. For Specialty, the comparable work-needed cohort contained two treatment Bakers on Fractal and one made the deadline. World divergence changes which buyers and plots get into this cohort.

The supplier survey detected three outages in each of the four arms. The stock arms recorded no recovery by turn 250. The treatment recovered two Continents Tailors Base links in 7 and 22 turns and one Fractal Tailors Specialty link in 3 turns. Three treatment outages were still unresolved in those surveys at turn 250. These are working supplier links while the buyer remains eligible, independent of whether the Service is active.
