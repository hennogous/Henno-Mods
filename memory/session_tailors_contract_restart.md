# Tailors contract-first restart

- Clean Tailors gameplay baseline committed as `0fcfe09`.
- Canonical Tailors design Markdown and existing art were retained.
- Existing optional-mod resource mappings to `CLASS_CSC_TAILORS_BASE` and
  `CLASS_CSC_TAILORS_SPEC` were retained and are validator-controlled inputs.
- Old Tailors gameplay SQL/localization/wiring and the first contract experiment
  were removed.
- Replacement workflow lives in `project/docs/QUARTER-CONTRACT-WORKFLOW.md`.
- Proposed contracts live in `project/specs/tailors/`.
- Contract validation command:
  `py -3 project/tools/quarter_contracts/validate_quarter.py tailors`.
- Existing Tailors SQL outputs are also checked against the Bakers-derived
  visual/architectural profiles in `bakers-sql-style.yaml`.
- Tailors is intended to become the normal Quarter reference after it passes
  static and runtime validation; Bakers then remains the specialized fallback.
- D.STAGE3 was implemented on 2026-09-07 and its gate is `ready_for_review`.
  The slice includes the Tailor, population-scaled Market/Temple exchanges,
  Sacristan, domestic trade-route effects, localization/UI previews, icons, and
  the Tailor alternate-art property bridge.
- Automated handoff validation passes with zero warnings; in-game acceptance
  remains user-owned under the contract.
- Stage 3 tooltip feedback on 2026-09-08 established a reusable presentation
  rule: authored building descriptions omit intrinsic Citizen slots,
  specialist yields, and local/regional Amenities because Civ VI renders them
  below the description. Cross-city transaction effects, including the Tailor
  trade route's +1 Amenity to the origin city, remain explicit.
- Quarter icon atlas positions are a reusable implementation convention rather
  than design data: district normal/FOW 0/1; stage 2/3/4 buildings 4/5/6; stage
  2/3/4 services 8/9/10. Tailors inherits the catalog default with no override.
- The Buildings ArtDef also requires a Quarter BuildingChain. Tailors uses
  CSC_TAILORS_BuildingChain with its district plus Textile Workshop/Tailor/
  Fashion House at Buildings Level 1/2/3 (corresponding to gameplay Stages
  2/3/4). Contract assertions are cumulative and permit only future levels to
  remain empty.
