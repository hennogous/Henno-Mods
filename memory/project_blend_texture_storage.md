# Working Files packed-texture audit — 26 October 2026

Human initially requested a read-only search for Blender files containing textures
outside active model shading, with potential storage savings. The audit itself
made no source changes. A separate background Blender 5.1.2 audited all 431
`.blend` and 109 `.blend1` files under Desktop/Working Files, including archives.
Source SHA-256, size and timestamp were unchanged across each file's inspection.

Measured potential saving: **578,311,055 bytes / 551.520 MiB** in 31 files:

- Regular `.blend`: 18 affected, 264,274,617 bytes / 252.032 MiB.
- `.blend1` backups: 13 affected, 314,036,438 bytes / 299.488 MiB.
- Of the total, 369,412,490 bytes / 352.299 MiB comes from images with zero real
  datablock users (excluding fake users). Remaining ~199.2 MiB is in disconnected
  shader nodes or unassigned materials and merits authoring/export review.
- Another 13.388 MiB of non-shader image references is protected/excluded.

Method: trace active material/world outputs through nested groups, group inputs
and muted-node bypasses; conservatively protect all material slots on all objects,
hidden variants, all scenes, overrides, Geometry Nodes materials and other uses.
Only packed local images contribute savings; external/linked-library image bytes
are not counted. Pair matched temporary resaves with source compression enabled
or disabled as appropriate, retaining image IDs in both controls to isolate packed
payload savings. Unpack REMOVE only in temporary copies; never save source files.
Nine synthetic graph/packed-size checks passed. All 540 final records succeeded.

Tools: `project/tools/blender/audit_packed_texture_storage.py`,
`test_packed_texture_audit.py`, `report_packed_texture_audit.py`.
Report and full file/image details:
`Desktop/Codex/Working-Files-packed-texture-audit-20261026/report.html`,
`summary.json`, `candidate-files.csv`, `graph-tests.json`.
Largest candidates: Storage S decal backup ~80 MiB; Storage M decal backup and
archived Storage L decal blend ~60 MiB each; Level 1 S decal blend ~56.3 MiB.

## Approved unreferenced-image cleanup — same day

Human then instructed: **“remove the 352MB”**. Removed only the audited completely
unreferenced packed-image group. The Bakery decal `.blend1` had independently
disappeared since the audit (its ~40 MiB image payload was not recreated).
Remaining **111 images in 23 files** were removed; actual net source-file saving
was **329,035,688 bytes / 313.793 MiB**. The ~199.2 MiB disconnected/unassigned
material group was preserved.

Staged copies in Desktop/Codex were made using matching source-format Blender
(3.1 for `BLENDER-v301`, 5.1.2 for newer files). Reopened every cleaned copy and
compared object placement/parenting, mesh positions/topology, UVs, materials and
nodes, weights/rigs, scenes, and every non-target image including packed SHA-256.
Unused materials and unrelated nonpacked image references needed fake-user
retention markers to prevent Blender's automatic orphan cleanup from dropping
them during the save. Geometry and shading remained unchanged.

Each original still matched its audited SHA-256 immediately before replacement;
installed files matched the verified staged bytes. Temporary originals were kept
through final verification, then removed, and the staged directory is empty.
Receipt: `Desktop/Codex/Working-Files-unreferenced-texture-cleanup-20261026/cleanup-receipt.json`.
Tools: `project/tools/blender/clean_unreferenced_packed_images.py` and
`commit_verified_texture_cleanup.py`. The initial audit report remains historical
evidence and its 352.3 MiB group is now handled; do not run that original removal
selection again against the changed hashes.
