# Tailors' Quarter Implementation Brief

Phase 1 draft, created before gameplay implementation.

| Topic | Decision |
|---|---|
| Quarter key | `TAILORS` |
| District | `DISTRICT_CSC_TAILORS_QUARTER` |
| Main yield | `YIELD_CULTURE` |
| Quarter maintenance | 1 Gold |
| Base materials | Cotton, Sheep; Bamboo (R2), Flax (CSC), Hemp (CH), Llamas (LAR) |
| Specialty materials | Dyes, Silk, Silver; Cashmere (R2), Gold (R2 / SR) |
| Stage 2 building | Textile Workshop |
| Stage 2 maintenance | -2 Gold |
| Stage 2 customer | Lighthouse in Harbor |
| Stage 2 service | Sailmaker in Harbor with Lighthouse; +20% Production toward Renaissance Era or earlier naval units and +1 Great Admiral point |
| Stage 2 unlock gate | Naval Tradition; Textile Workshop supplied by improved Base Materials |
| Stage 3 building | Tailor |
| Stage 3 customers | Temple in Holy Site; Market in Commercial Hub |
| Stage 3 service | Robemaker in Holy Site with Temple; +10% Faith and +1 Great Prophet point |
| Stage 3 unlock gate | Divine Right; Tailor supplied by improved Base Materials |
| Stage 4 building | Fashion House |
| Stage 4 customers | Amphitheater in Theater Square; Bolshoi Theatre; Broadway; Sydney Opera House |
| Stage 4 service | Couturier serving Theater Square or Wonder destination; +10% Culture, +1 Citizen slot, and +1 Great Artist point when established in a Wonder |
| Stage 4 unlock gate | Opera and Ballet; Fashion House supplied by improved Base and Specialty Materials |
| Trade route behavior | Stage 2: +1 Production to routes to the city, +1 Gold return to Quarter. Stage 3: +1 Culture to routes, +1 Gold return. Stage 4: +1 Culture to routes, +2 Gold return. |
| Art plan | Start with Quarter district art scaffolding in Phase 2; building kit assignments TBD per slice. |

## Resource Mapping Notes

The public materials table and existing SQL support files agree on the intended Tailors' mapping, but the current `CSC_Q_TAILORS.sql` stub only contains part of the standard-game mapping. Phase 2 should consolidate the live Quarter file around the full mapping above, preserving optional animal-resource and ModSupport criteria.

Current producers found during Phase 1:

- `Civ Supply Chains/Data/CSC_Q_TAILORS.sql`: Cotton, Dyes, Silver
- `Civ Supply Chains/Data/CSC_A_RESOURCES.sql`: Sheep, Silk
- `Civ Supply Chains/Data/CSC_RESOURCES.sql`: Flax
- `Civ Supply Chains/ModSupport/ModSupport_R2.sql`: Bamboo, Gold
- `Civ Supply Chains/ModSupport/ModSupport_R2_A.sql`: Cashmere
- `Civ Supply Chains/ModSupport/ModSupport_CH.sql`: Hemp
- `Civ Supply Chains/ModSupport/ModSupport_LAR_A.sql`: Llamas
- `Civ Supply Chains/ModSupport/ModSupport_SR.sql`: Gold

## Open Questions Before Later Phases

- Confirm the implementation host for Couturier service effects when the customer is a Wonder rather than a normal district building.

## Parked Taxes & Politics Notes

The older Haute Couture Product/project concept has been moved to `TaxesPolitics/docs/starter-docs.md` with the other initial Quarter specialty commission ideas. It is not active CSC design for the Tailors' implementation pass.
