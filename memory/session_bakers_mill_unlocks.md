# Bakers mill unlocks — 21 October 2026

User approved updating both design and implementation after discussing historical progression and alignment with other Quarters: Water Mill at Engineering (Classical), Wind Mill at Machinery (Medieval). River milling precedes milling away from rivers; Quarter placement itself remains available at Craftsmanship.

Updated `docs/content/quarters/bakers.md` and the two Buildings.PrereqTech values in `Civ Supply Chains/Data/CSC_Q_BAKERS.sql`. Costs, effects, terrain restrictions and downstream prerequisites are unchanged. Localization has no authored Wheel unlock statement; native technology/Civilopedia fields use the building prerequisites. Refreshed only the matching Bakers core reference hash in `project/specs/tailors/control.yaml` for this user-authorized amendment.

Offline validation passed: executed the complete 10-row Buildings insert against the actual game table schema in memory, compared before/after rows (only the two PrereqTech values differ), checked technology existence/eras, design consistency, reference hash, SQL layout/style and diff whitespace. Evidence: `C:/Users/Shadow/Desktop/Codex/bakers-mill-unlocks-20261021/validation.json` plus before snapshots and focused SQL diff.

Source-only change: no ModBuddy build, installed-mod update, game interaction or public-site deployment. The concurrent AI guidance test was left undisturbed. A new build and in-game review remain pending.
