# Fashion House mustard dress — 13 October 2026

Henno requested the ivory gown in front of the privacy screens become mustard yellow. Installed the colour-only change in the two active revision-12-garden-path Fashion House Blender files and `CSC_TAILORS_Fashion_House_Fitting.fgx`.

- Shared atlas Current is now `2026-10-13_Shared_01_r024`. New embroidered mustard region28 preserves the prior ivory embroidery region23 for screens/other garments. Sleeves reuse existing ochre22. Original generated image, exact prompt, and companion-map provenance are retained in the release sources. All previous surface pixels and all AO/emissive bytes are preserved.
- Only gown/sleeve UV1 changed in Blender; all geometry, transforms, other UV channels and materials match saved pre-edit sources. Native patch changes only UV0 on141 existing vertices in3 meshes. Reloaded native buffers and complete before/after CN6 comparison verify every other vertex field, topology and skeleton unchanged.
- All existing ASTs, GEOs, shared material and Tilebases XLP preserved byte-for-byte. AE placements and visibility/state edits remain authoritative.
- Saved final building validator: zero errors; prior2630/2200 advisory budget remains. Current close-up inspected: mustard separates the gown from ivory screens, embroidered borders remain visible, AO unchanged. This is a source preview, not an AE assembly render. No cook/in-game appearance claim.
- Backups, source/native parity reports, final installed-file checks and preview: `C:\Users\Shadow\Desktop\Codex\Fashion-dress-mustard-20261013`.
- Source tools: `project/tools/art/fashion_dress_mustard.py`, `fashion_dress_blender.py`, `PatchFashionDressUV.cs`. Native colour-only edit avoids rebuilding assembly metadata or altering legacy rig/tangent data.

Editable sources: `C:\Users\Shadow\Desktop\Working Files\3D Art\TAILORS\Fashion House\revision-12-garden-path\CSC_TAILORS_Fashion_House.blend` and `CSC_TAILORS_Fashion_House_Fitting.blend` beside it. Surface B/N/G/M snapshots updated to r024; local AO kept unchanged. Backups kept in the task output.
