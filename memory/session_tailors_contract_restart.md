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
- Tailors is intended to become the normal Quarter reference after it passes
  static and runtime validation; Bakers then remains the specialized fallback.
