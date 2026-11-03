# Placed by CSC versus placed by the AI — final observed175

The test ended partial175. The uncontrolled post-defeat interval through192 is excluded. Only the two tested Quarter types and the five studied major AIs are compared. Captured sites are traced to their first recorded origin; capture events are not additional placements.

## Material quality at actual placement

Counts below use the exact native DistrictAddedToMap resource observations: revealed resources mapped to that Quarter, owned by its original player. Unimproved materials remain valid types. Enabled modded resources, including CSC Flax, are included.

| Origin | Quarter | Placed | Both | Base only | Specialty only | Neither |
|---|---|---:|---:|---:|---:|---:|
| CSC placed | Bakers | 8 | 8 | 0 | 0 | 0 |
| CSC placed | Tailors | 3 | 3 | 0 | 0 | 0 |
| AI placed | Bakers | 40 | 0 | 18 | 2 | 20 |
| AI placed | Tailors | 25 | 1 | 7 | 1 | 16 |

CSC placed11 (8Bakers/3Tailors); AI itself placed65 (40Bakers/25Tailors). All11 CSC sites had Both by design. Only1/65 AI sites had Both;36/65 had neither owned material type. Even counting neighbouring unowned resources,29/65 still had neither type. So this is not simply an inability to buy land.

There are four additional Quarters in the final AI census captured from the observer/city-state: two Bakers and two Tailors. They are excluded from those76 original placements. Two of the65 original AI sites later changed owners between studied AIs; they remain labelled by original placement provenance.

## Construction and working supply at175

| Origin | Quarter | Original completion observed | Unpillaged producer now | Working Base now | Working Both now |
|---|---|---:|---:|---:|---:|
| CSC placed | Bakers | 8/8 | 8 | 1 | 1 |
| CSC placed | Tailors | 3/3 | 2 | 1 | 1 |
| AI placed | Bakers | 40/40 | 33 | 9 | 0 |
| AI placed | Tailors | 24/25 | 15 | 4 | 0 |

Working requires a completed, unpillaged Quarter/producer plus owned, unpillaged native-valid resource improvements. Producer columns reflect the current studied AI owner; the JSON also requires original owner/city identity separately. Neither transactions nor exact Service payments are inferred.

The AI completed64/65 of its own placements. All52 unassisted placements at least25 turns old had an original completion observation, as did all11 assisted sites. Construction ability is much stronger than material siting. Assisted foundations retained only2/11 working Base chains and2/11 Both chains; unassisted sites had13/65 working Base and0/65 working Both. Thus handholding produced all observed working Both chains among these original-placement cohorts, but did not maintain a broad Base-supply advantage.

## Adjacent resource spread at175

This is current resource identity, not a retroactive placement-time count. Exact placement events did not export unmapped resources, so those placement-time numbers remain unobserved. Counts are Quarter/resource adjacency links, not distinct world tiles. Shared material plots can count beside multiple Quarters. Unmapped means unusable by this Quarter, not intrinsically worthless; hidden resources and non-improvable markers such as antiquity sites are excluded.

| Origin | Quarter | Mapped resource links | Unmapped resource links | Only unmapped nearby | No revealed improvable resource nearby |
|---|---|---:|---:|---:|---:|
| CSC placed | Bakers | 9 | 1 | 0 | 0 |
| CSC placed | Tailors | 4 | 3 | 0 | 0 |
| AI placed | Bakers | 22 | 30 | 15 | 9 |
| AI placed | Tailors | 12 | 24 | 14 | 3 |

The AI sites include Rice/Wheat/Maize beside Tailors and Silk/Silver/Dyes beside Bakers, plus unrelated mineral/sea resources. Those neighbours can still be useful city yields, but do not feed the placed Quarter. A valid but unowned, unimproved or pillaged material is kept separate from these unmapped types.

## What happened to our initially guaranteed Base tiles?

Every assisted site began with one owned Base resource and one owned Specialty resource. By175, nine had lost that Base resource from the adjacent tile. Eight former Base tiles now contain districts; the ninth is a resource-less Mine. Both retained Base resources are correctly improved and support the two working Both chains.

| Assisted Quarter source | Original Base tile | Base resource | Observed later tile use | Native placement observation |
|---|---:|---|---|---:|
| Bakers 2052 | 2051 | RESOURCE_WHEAT | DISTRICT_SPACEPORT | 173 |
| Bakers 2711 | 2636 | RESOURCE_CSC_FLAX | DISTRICT_THEATER | 142 |
| Tailors 2752 | 2826 | RESOURCE_CSC_FLAX | DISTRICT_GOVERNMENT | 69 |
| Bakers 2045 | 2119 | RESOURCE_CSC_FLAX | DISTRICT_CAMPUS | 62 |
| Tailors 2165 | 2166 | RESOURCE_CSC_FLAX | IMPROVEMENT_FARM | 103 |
| Bakers 2785 | 2860 | RESOURCE_CSC_FLAX | DISTRICT_AQUEDUCT | 171 |
| Bakers 1278 | 1353 | RESOURCE_RICE | DISTRICT_GOVERNMENT | 81 |
| Bakers 2419 | 2420 | RESOURCE_WHEAT | DISTRICT_THEATER | 159 |
| Tailors 2939 | 2865 | RESOURCE_SHEEP | IMPROVEMENT_MINE | 160 |
| Bakers 1862 | 1863 | RESOURCE_MAIZE | DISTRICT_COMMERCIAL_HUB | 109 |
| Bakers 2572 | 2497 | RESOURCE_MAIZE | IMPROVEMENT_FARM | 147 |

A concrete conflict: CSC placed Bakers1862 at97 beside Maize1863; the AI placed a Commercial Hub on1863 at109. The customer district became adjacent to the Quarter while its required Base disappeared. Other losses were Government Plazas, Campuses, Theaters, an Aqueduct and a Spaceport. These are physical occupation/placement facts; the exact harvest mechanism for Sheep2865 becoming a Mine is not inferred without a matching operation record.

This is not solely a new-adjacency problem: in the preceding V7 comparison, Maize1863 was also gone by150, under a Tailors Quarter. The stronger customer incentive cannot alone be blamed for the loss. The unresolved general issue is opportunity cost and preservation of a sole material tile.

## Interpretation and limits

The handholding is effective at selecting and securing Both sites, and the AI generally finishes the construction. It is ineffective at preserving most of those initial inputs. The most useful next guidance target is retention of the last Base material and avoiding customer/other district placement on it, rather than simply increasing Quarter priority again.

AI placed here means no CSC foundation injection. It is not vanilla: RH, CSC signals and type preferences remain active. One unassisted Bakers placement was on/near a previously CSC-purchased tile; no unassisted Tailors placement had that direct purchase proximity. Broader economy spillovers remain possible. The natural cohort younger than25 turns should not be judged against older assisted sites without the age breakdown; CSV/JSON expose each placement age.

For six of the36 placements with neither owned material, a native candidate scan zero/one turn earlier recorded alternative owned-Base sites in the same city. These are useful ranking leads, not simultaneous proof that every alternative remained legal at selection. The observer/city-state samples, captured origins, source data limitations and no pure control arm are explicit in the JSON.

All inputs were analysed offline. No game was launched, replayed or modified for this report. Financial data after170 is unobserved, but every original placement in the two compared cohorts was recorded before170, so the confirmed foundation journal covers their provenance.

Files: quarter-cohorts.json, quarter-sites.csv and assisted-base-fate.json contain the per-site evidence and full resource-type distribution.


Important selection bias: CSC deliberately claims Both opportunities before the AI may choose them; the same-type per-city exclusion then removes that Quarter option from the AI's remaining choices. The1/65 unassisted Both rate therefore does not establish what the AI would have achieved without handholding. It describes the placements left to it in this combined run. A no-injection matched arm would be needed for a clean counterfactual.

