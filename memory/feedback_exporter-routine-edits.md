# Routine Blender export edits — 7 October 2026

Henno finds export_assets unreliable and overburdened with contracts/metadata
checks for simple prop moves and rotations. Treat initial asset preparation as
setup that the tool remembers, not work the user must repeat after placement edits.
Preserve checks required for accurate geometry, materials and game-supported
transforms; avoid blocking export on preview-only authoring conventions.

Implemented automatic settings snapshots inside each run. When explicit settings
and revision sidecars are absent, normal runs can recover the newest successful
setup for the same mod from that source folder's export-runs history. Explicit
and local settings retain precedence. Custom output locations are not searched.
World/color-management/Review Sun findings are export warnings; the standalone
authoring validator still treats its prescribed lighting as requirements.

Validation: 104 exporter tests pass, seven Blender-dependent skips. An isolated
Tailor copy was exported, its crate controller moved +1 Y and rotated +10 degrees,
preview lighting changed, and its local sidecars moved aside. A second full
decode/build/conversion recovered prior setup, passed with zero blockers and
serialized the expected placement. Original blend hashes unchanged; no install.
Evidence: Desktop Codex/Exporter-routine-reexport-check-20261007/verification.json.

Asked whether Henno moves visible meshes or their parent/controllers; no answer
yet. The live test covers controller edits. Mesh-child relative placement changes
still hit canonical assembly checks; do not claim these are solved by setup reuse.
