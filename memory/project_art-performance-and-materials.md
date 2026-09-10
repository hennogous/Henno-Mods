---
name: project_art-performance-and-materials
description: CSC building-art performance priorities and the E/NE/Props material architecture (state-swap, not concurrent)
metadata:
  type: project
---

Value-for-effort ladder for CSC/Civ6 mod art performance (established July 2026 while
reviewing the Storage_L building). Optimize in this order; do NOT invert it:

1. Draw calls / material count (batching) — the dominant cost. Shared per-family 1K atlas is the key win; never let a prop/variant silently introduce a new material or texture.
2. Texture / VRAM (BC compression, mips, resolution honesty).
3. Engine instancing — reuse identical mesh+material across tiles; differentiate via material/texture, not unique geometry.
4. Transparency / overdraw — model props as geometry on-atlas, not alpha cards. Building material binds `CSC_Atlas_O` to Opacity, so confirm it's alpha-*test* (cutout), not alpha-*blend*.
5. LODs — the only place reducing vertices actually pays (author a crude far-LOD, don't shave LOD0).
6. LOD0 vertex count — lowest value. A ~1,350-vert building is noise; skip.

**Vertex count is the cheapest resource.** Props are ~free on the axis that matters as long
as they sample the existing atlas and share the building's material — no need to "buy vertex
budget" for them. Welded vs Firaxis floating-quad topology is irrelevant to *export* count
(CN6 pre-splits at every UV/normal seam anyway; proven on Storage_L: island-splitting the
welded shell left the export estimate unchanged). Only safe automated vertex win on existing
retopo meshes is a UV-delimited limited dissolve (~8% on Storage_L). Buried foundation can't be
deleted (hills expose it) and resists auto-decimation (already single-height flat walls following
the leg outline). Future authoring lesson: model foundations as coarse solid boxes from the start.

**Material architecture (per Quarter): E / NE / Props.** These are 3 material *definitions* but
only ~2 are ever concurrent on one building instance:
- **E** = completed state, emissive atlas `CSC_Atlas_E` bound (windows/lights drawn in, black elsewhere).
- **NE** = CON/PIL states, emissive slot empty → lights off. E and NE are byte-identical except the
  Emissive texture slot. They are a **temporal state swap** (Civ6 ArtDef `BuildStates` /
  `UsesDistrictState` swaps material bindings), NOT concurrent submeshes — so NE is not an extra
  draw call, just an extra definition. Do NOT try to "merge" E and NE; the NE variant is the
  lights-off mechanism. Standard Firaxis pattern.
- **Props** = separate texture set (`*_Props_B/N/AO/M/G`), the one genuinely additional concurrent
  material. A completed building = E + Props = 2 concurrent draw calls (optimal).

Open optimization: one shared project-wide Props atlas/material instead of per-Quarter props —
wins on VRAM + state-changes (not draw-call count, since different building meshes don't auto-batch).
