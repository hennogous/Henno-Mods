# Problem2.1: customer-district placement

Active after Astra-approved1.7 closure. Acceptance: isolate the mapped
customer-site contribution and demonstrate a changed actual native district
choice/request toward an adjacent provider Quarter or a specific credible
future Quarter footprint. Preserve standalone value, legality, other policy
and material protection. Require dynamic main-mod reproduction. Construction
and broader coverage are separate.

## Implemented scope

Main QuarterPlacement.StageTwoProfiles builds customer mappings from
CSC_QuarterCustomerBuildings rows with ProducerStage2, including building
and district replacements. In current CSC that means City Center/Granary
for Bakers and Harbor/Lighthouse for Tailors.

AdjacencyScan excludes City Center from ordinary district nominations.
The existing-Quarter customer bid is40*256 Q8. It requires a complete,
unpillaged Quarter with viable owned Base, no adjacent placed mapped customer
host, and a resource-free, unprotected, owned native-legal customer footprint.
Several qualifying chains deduplicate the same pair rather than stacking bids.

The smaller16*256 future-Quarter bid requires an owned strong site, ready
Base and a selected future host in that current native target list. The
present guard withholds it when both population-requiring districts would
share a city. It is not a general bid for every projected customer footprint.

CSC_AI_Connectors.sql supplies another path: +1 private adjacency yield from
a mapped Quarter to its Stage2 customer, with DefaultYieldBias25. That is a
native yield signal, not a25-Q8 offer. It also excludes City Center.

Thus the ordinary customer-placement paths currently address Tailors→Harbor
and replacements. Bakers' later Entertainment/Water Entertainment customers
and Commercial goods-provider links can affect Quarter siting through the
broader siting registry, but do not receive these Stage2 customer-site bids
or SQL connectors. Zero customer offers in the early Bakers tests is expected.

## Existing observed comparisons

The old Fractal receipt run has28 written/eligible customer offers and five
city comparisons. Three exact site wins span two Harbor sites:

| Decision turn | Player | City ID | Offered plot | Exact site win |
| --- | ---: | ---: | ---: | --- |
| 141 | 4 | 589832 | 2383 | Yes |
| 167 | 2 | 524295 | 1437 | No |
| 169 | 2 | 524295 | 1437 | Yes |
| 176 | 2 | 524295 | 1437 | Yes |
| 178 | 5 | 65536 | 648 | No |

Receipts are read on the following turn. The141 CityBuild row submits
Harbor contract2644, priority693, for Ka Peyakwaskonam. These prove delivery
and observed native choices, not necessity of either customer signal.

Archive: C:/Users/Shadow/Desktop/Codex/csc-ai-native-receipts-20261108/fractal.
The runtime Fractal catalogue maps district4 to Harbor. The Continents
fixture maps4 to Holy Site. Join native indices to each world's catalogue;
do not carry a numbered type across configurations.

No preserved pre141 checkpoint was identified. The later pinned Fractal
200 source, observed through207 by host-choice-fractal-scout-01, produces
zero current customer offers. Washington22→24 and Nicopolis200→254 also
produce none. These windows therefore cannot establish customer-bid
causality merely by reusing their successful Quarter comparisons.

## Next unresolved dependency

Identify a source with a genuinely missing Tailors customer and resource-free
native-legal Harbor candidates at a known fresh comparison. Qualify the actual
main offer and native margin before selecting an ablation. Preserve the
private-yield path unless testing it explicitly; do not attribute its effect
to the CE bid. Existing native/CE readers are sufficient to begin; no new
address or score probe is justified yet.

No new live2.1 game or placement treatment has been run. No2.1 closure is claimed.
