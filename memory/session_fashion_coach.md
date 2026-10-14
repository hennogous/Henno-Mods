# Fashion House coach — 13 October 2026

Current master: `C:/Users/Shadow/Desktop/Working Files/3D Art/Props/Tailors/Fashion Coach/revision-02/CSC_TAILORS_Fashion_Coach.blend`.
Standalone installed asset `CSC_TAILORS_Fashion_Coach`: 937 exported vertices,
771 triangles, one shared material. Revision 02 removes fine trim at Henno's
request; use the [standing feedback](feedback_prop_geometry_detail.md).

Shared atlas release r023 follows r022 coach additions and reconciles Henno's
pre-existing five-cell AO edits. Current, immutable snapshots, source patches,
portable textures and installed DDS are synchronized. Source/native checks pass;
AE/game appearance unreviewed. No Fashion House placement or existing AST changed.

Full details: [durable coach notes](../project/docs/art/fashion-house-coach.md).
Package: `C:/Users/Shadow/Desktop/Codex/Fashion-coach-20261013/`.
AE held a DDS mapped open; in-place copy failed. Atomic sibling replacement
completed without closing AE; old data may remain cached until reload.
AE subsequently re-imported the DDS files. Their full-resolution pixels are
identical to the staged maps; native headers, complete mip chains and canonical
TEX paths validate. See `final-live-verification.json`; byte hashes differ because
AE regenerated lower mip levels and headers.
