# Tailor revision 10 export settings — 7 October 2026

Henno's bare-path export reached discovery, then failed because the published
`Working Files/3D Art/TAILORS/Tailor/revision-10-vertex-budget` lacked both
settings sidecars. Building scene metadata has no Quarter/stage, the authored
CON+PIL master is marked ignored without the sidecar, and four previously
installed standard prop identities are not in the default replacement list.

Added `export-contract.json` (adapted from Desktop Codex's Tailor revision09
contract, adding Work Area Decals to required sources) and
`export.defaults.json` (CSC defaults plus explicit replacement of Dress Form,
Folded Stock, LeanTo and Table Contents). Saved blends were not modified.
Normal command excludes optional Tailor_2 group; `--include-optional` includes it.

Both discovery modes pass. Full optional-group decode, build and Windows
conversion passed with zero report blockers, 11 FGX outputs and 18 placements.
Source hashes checked unchanged. Staged only; no installation, ArtDef/cache/cook
updates or new appearance review. Review output:
`C:\Users\Shadow\Desktop\Codex\Tailor-revision10-export-check-20261007\export-run`.

Expanded models belong to the optional Art Pack under current project boundaries;
the exporter itself does not perform that subsequent integration.
