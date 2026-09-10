# Baked AO for shared texture atlases

How CSC bakes geometry-correct ambient occlusion into a **shared** building atlas
without giving up UV1 texture reuse. Tool: [`project/tools/blender/csc_shared_atlas_ao_bake.py`](../tools/blender/csc_shared_atlas_ao_bake.py).

## The problem

Each building family shares one 1K atlas split into 512-px quadrants (top-left =
Level 1, top-right = Level 2, bottom-left = Level 3, bottom-right = Storage). Within
a quadrant the base-colour / normal / gloss / metal / AO content is shared across
several models, and UV1 **overlaps aggressively** — identical wall segments stacked
on one atlas patch; a smaller variant reuses the parent's patches wholesale. That's
correct for *material* properties: oak is oak wherever the plank sits.

AO is not a material property, it's **positional** — it encodes where a face sits
relative to everything around it. Two identical planks, one under a bench and one in
open air, have the same wood but opposite occlusion. With overlapping UV1 they are
forced to share one texel, so the best you can store is generic edge-dirt that
follows the *painting*, not the *form*. That's what the old "derive AO from base
colour" script produced — and with overlapping UVs it was the *only* self-consistent
option, because baking real AO into overlapped UVs has many faces fighting for the
same texels.

The engine samples AO through the **second UV channel** (UV2 / TEXCOORD_1),
separately from the tiling UV1. So the fix is: give UV2 a non-overlapping layout,
bake geometric AO into it, and let variants **share** the parent's baked texels
wherever they reuse the parent's UV1 content.

## Model families

A *family* is a **parent** building plus **variants made by duplicating it** — a
CON+PIL (construction/pillaged) damage state, a smaller version, a themed
conversion. Because variants inherit UV1 by duplication, "same UV1 coordinates" ==
"same kit piece", and that identity is what drives sharing.

Two family shapes occur in CSC:
- **Related family** (Level 1/2/3): variants genuinely reuse the parent's geometry
  and should share the parent's AO. Level 1 is the archetype (a small version, a
  water-mill conversion, plus CON+PILs of each).
- **Independent buildings sharing a quadrant** (Storage S/M/L): three *unrelated*
  buildings that merely co-inhabit one quadrant. They must have **no shared or
  overlapping** texels between them; each shares only with its own CON+PIL. The
  packer allocates quadrant area by size (small takes less, large more) — no manual
  layout needed.

## Pipeline

1. **Append** every family member into a scratch scene.
2. **Classify** each variant face: does it reuse a parent patch (share texels) or
   sample atlas content the parent never touches (own texels)?
   - *exact reuse*: bit-identical UV1 to a parent face (duplication preserved it).
   - *coverage reuse*: the face's UV1 footprint lies **inside** a parent island —
     e.g. a broken half-wall sampling part of the intact wall patch.
   - Independent families reset the shared set so S/M/L never match each other.
3. **Union + pack**: build one temp mesh = parent's full faces + only the
   genuinely-unique variant faces, copy UV1→UV2, and **Pack Islands once** so all
   islands negotiate the quadrant together (no reservation step). Remap the packed
   0-1 layout into the family's quadrant.
4. **Bake** AO into the shared atlas, one model at a time, **Clear Image off** (so
   other quadrants survive), **variants first, parents last** — so the parent's
   bake is canonical on every shared texel while variant-only islands (damage
   patches) keep their own bake. Isolate each model from *rendering* so neighbours
   don't cast phantom shadows.
5. **Resolve** each member's UV2: exact-reuse faces get the parent's slot; coverage
   faces get pushed through their parent island's UV1→UV2 transform; own faces keep
   their baked slot.
6. **Write back** UV2 to each source `.blend` (auto-pack disabled), grouped by file.

Re-running only steps 5–6 after a resolver change is safe: parent UV2 and the baked
atlas are already valid, so no repack or re-bake is needed.

## Two subtle bugs (both fixed in the tool)

**1. First-hit bias.** Where several parent islands can host a coverage face, pick
the one **nearest in 3D**, not the first found. Otherwise a ground-level fragment
may sample the AO of a look-alike twin patch up under the eaves. Positional only —
never flings faces — but worth doing.

**2. UV2-connectivity islands (the important one).** Island transforms *must* be
derived from **UV2 connectivity** (the actual pack units), not UV1 connectivity.
The twin tie-break can cross-assign UV2 slots between twin faces, so a single
UV1-connected cluster ends up pointing into **two different packed islands**. No
single similarity transform fits that, and any coverage face assigned to such a
cluster gets a garbage transform — scaled and rotated wildly, spilling outside the
quadrant. Symptom seen in L2CP / L3CP: a handful of faces at ~100–160× the median
UV2 area, some at v = −0.03 (below the quadrant). Clustering by UV2 gives clean
single-pack-unit islands (least-squares residual ~0.001 px) and the problem
vanishes. The transform is a least-squares complex similarity (robust to sliver
islands), not a two-point solve.

## Gotchas (all handled in the tool, all seen in real CSC files)

- Bake targets the **active image node** of the material and the **active UV layer**
  of the mesh — wrong active node overwrites base colour; wrong active UV scrambles
  the bake.
- **AO rays see the whole scene** — isolate each model (hide others from *render*).
- New Blender images default to **sRGB**; every data map (AO/N/G/M) must be
  **Non-Color** or the viewport lies (the game reads the DDS directly and ignores
  this, but bake/preview care).
- Files saved in **Edit Mode** expose empty mesh data to scripts — force Object Mode.
- **Auto-pack** silently embeds external textures on save — disable it; keep the
  atlas external per the CSC texture-iteration rule.
- **AO ray distance is scale-relative** (~20% of the model's largest dimension;
  30 units for the ~148-unit houses) — rescale and re-bake if mesh scale changes.
- Degenerate zero-area-UV dummy faces are left untouched.

## Running it for a new family

Fill in a CONFIG block (families, quadrant, bake order) and call `run_atlas(...)`
in the tool — see the worked Storage example in its docstring. The output is the
updated `Textures/CSC_Atlas_AO2.png` plus new UV2 on every member `.blend`.

## Shipping to the game

Every mesh's UV2 changes, so **re-export the CN6/FGX** for each touched model, and
convert `CSC_Atlas_AO2.png` → DDS once (replacing/beside `CSC_Atlas_AO.dds`). Until
then the game keeps using the old UV2 (= UV1) with the old DDS, so nothing breaks in
the interim.

## Status (2026-07)

All four quadrants converted to geometric AO: Level 1, Level 2, Level 3, and the
Storage trio. Level 1 was done before the two fixes landed; it renders well and is
in a verified-good state, so it is intentionally **not** being re-run — the fixes
only matter where variant UVs drifted from the parent (L2/L3) or where independent
buildings share a quadrant (Storage). If Level 1 is ever reworked for another
reason, it inherits the fixed pipeline for free.
