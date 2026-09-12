# Baked Ambient Occlusion for a Shared Texture Atlas — A Retrofit Story

> **Documentation audit — 2026-09-12: Superseded.** Earlier narrative describes UV1-connected matching/twin ambiguity. Current shared-atlas-ao.md and csc_shared_atlas_ao_bake.py use UV2 pack connectivity, nearest-3D matching and least-squares transforms. Preserve the narrative, use the newer procedure.
> Classification: AO history. See the [full audit](../../DOCUMENT-AUDIT.md).

*How we replaced script-derived AO with true geometry-baked AO across a family of Civ VI building models that share one texture atlas — without giving up UV reuse, and fully scripted in Blender Python.*

---

## The setup

Like most strategy-game asset pipelines, ours leans hard on **texture atlases**. One 1K atlas serves a whole group of buildings: each building family gets a quadrant (~512×512 of effective space), and within that quadrant the base color, normal, gloss, and metalness content is shared by every model in the family.

A "family" here means: a **parent building**, plus variants derived from it by duplication and editing — a smaller version, a themed conversion (same house with a watermill bolted on), and construction/pillaged (damaged) versions of each. Six models, one atlas quadrant, one material.

To be efficient with texel space, the UVs **overlap aggressively**. Four identical wall segments map onto the same patch of atlas. The small variant reuses the parent's patches wholesale. This is the classic trick and it works beautifully for *material* properties: oak is oak, whichever wall it's on.

## The original AO approach, and why it existed

Civ VI's engine samples ambient occlusion through the **second UV channel** (TEXCOORD_1), separately from the tiling/overlapping first channel. Our models had UV2 as a straight copy of UV1, and the AO map was **derived from the base color** by a script — essentially a cavity/crevice-darkening pass over the painted atlas.

That wasn't laziness; it was forced. Real AO baking writes *into* the UV layout, and with overlapping UVs, multiple faces fight for the same texels — you get garbage. Derived-from-basecolor AO is the only self-consistent option when UV2 duplicates an overlapped UV1.

The cost: AO is not a material property, it's a **positional** one. It encodes where a face sits relative to everything around it. A plank tucked under a bench and an identical plank in open air have the same wood but opposite occlusion. Overlapped UVs force them to share one answer, so the best you can store is generic edge-dirt that follows the *painting*, not the *form*. This, it turns out, is exactly why the engine has a second UV channel at all: UV1 may tile and overlap for materials; UV2 exists so each face can have a unique patch for positional data.

## The retrofit, single-model version

For one model in isolation, the fix is a well-known recipe:

1. **Copy UV1 → UV2**, preserving island boundaries (important: export formats like Civ's CN6 split vertices at UV seams, so re-unwrapping from scratch inflates the final vertex count; re-*packing* existing islands adds no new seams).
2. **Pack Islands** on UV2 — overlapping duplicate islands separate, each face gets unique texels. Crucially, Blender's Pack Islands has a "Pack to: **Original Bounding Box**" mode (3.6+): since the copied islands already live inside the model's atlas quadrant, the pack stays inside the quadrant. No manual rescaling needed.
3. **Bake AO in Cycles** into a copy of the shared AO atlas, with *Clear Image off* so the bake writes only this model's islands and every other family's quadrant survives untouched.
4. Bake with the model **isolated** (everything else hidden from rendering) — AO rays test against the whole scene, and neighbors in the .blend will cast phantom shadows into your bake.

## The family problem

Doing that naively per model fails immediately: six models would each pack the *whole* quadrant for themselves, six bakes would overwrite each other, and texel space would be spent six times over.

The intent was always different: **variants should share the parent's bake.** The small variant is literally the parent's geometry — it should sample the parent's AO texels. Only faces that sample atlas regions the parent never touches (the watermill housing patches, the damage-state patches painted for the broken roofs) genuinely need their own texels and their own bake.

The question is how to know, programmatically, which faces those are.

## Insight 1: UV1 is an identity fingerprint

Because every variant was made by *duplicating* the parent mesh and editing it, shared faces carry **bit-identical UV1 coordinates** — nobody ever re-unwrapped them. So "same UV1 loop coordinates" ≡ "same logical kit piece." No geometric interpretation needed; the correspondence is already in the data.

Mechanically: for each face, take its loop UVs rounded to 4 decimals (tolerance ≈ 1/6500 of UV space — far below a texel, forgiving float dust, never merging distinct faces). Normalize the loop cycle by rotating it so the lexicographically smallest pair comes first — now two copies of a face compare equal regardless of which corner their loop order starts at. Also try the reversed sequence for mirrored faces. That normalized tuple is a dictionary key.

Build the map from the packed result: key → new UV2 loop coordinates (stored in the same rotation, so the correspondence is corner-exact) plus the face's 3D center. Apply to any variant face by key lookup, undoing the rotation offset on write-back.

One ambiguity: the parent itself contains **twins** — several faces with identical UV1 (that was the whole overlap trick), which end up with *different* UV2 islands after packing. So a key can map to multiple candidates. Tie-break on nearest 3D center. It's a safe call: twins have identical painted content and near-identical baked AO, so even a "wrong" twin is visually indistinguishable.

## Insight 2: faces that *partially* reuse a patch — island transforms

Exact matching missed a large class of faces. A damaged variant's half-broken wall face samples a *sub-region* of the parent's wall patch. Same painted content, different loop coordinates — no key match. First attempt classified ~120 such faces per damaged variant as "unique," wastefully duplicating texels (a sharp-eyed look at the UV editor caught this).

The fix comes from how packing works: Pack Islands moves each island **rigidly** — one similarity transform (rotation + uniform scale + translation) per island. So:

1. Cluster the parent's faces into UV islands (union-find over mesh edges whose loop UVs match on both faces).
2. For each island, recover its UV1→UV2 transform from two farthest point pairs (solve the 2D similarity as a complex division; we measured residuals of 0.001 px — the rigidity assumption is exact).
3. Any variant face whose UV1 footprint lies **inside a parent island's UV1 area** (point-in-polygon against the island's faces, points nudged 2% toward the centroid to forgive borders) inherits that island's transform: push its UV1 loops through it, and it lands on the correct sub-region of the parent's packed island — sharing texels perfectly.

This absorbed 84–88 faces per damaged variant and cut the "genuinely unique" counts to almost nothing: the small variant shares 100%, one damaged variant kept a *single* unique face.

## Packing without "reserving space"

There's no reservation step. Build one temporary **union mesh**: the parent's complete face set *plus* the genuinely-unique faces from all variants (mesh connectivity preserved so they remain coherent islands; uniqueness is checked *sequentially* across the family, so the second damaged variant's damage faces match the first's contributions and don't duplicate them). One Pack Islands call lays out all islands **simultaneously** inside the quadrant — parent and variant islands negotiate space in the same pass. Then each island's final position is written back to whoever owns it, and shared faces resolve through the key map and island transforms.

## Baking: overwrite order instead of masks

Each unique island must be baked from *its own* geometry — the parent can't produce AO for a broken rafter it doesn't have. But bakes write every texel their object's islands cover, including shared ones. Rather than masking, use ordering with Clear Image off:

> **damaged variants → themed variant → parent last**

Every model bakes in isolation and stamps its islands; the parent, baking last, overwrites the *shared* islands with canonical intact-geometry AO — and since it has no faces mapping onto the variant-only islands, those texels survive with their owner's bake. Variants that own nothing (the small version) are never baked at all.

Known trade-off, accepted deliberately: shared faces on a damaged variant show *parent-baked* AO — a surviving roof half reads as if the missing half still shaded it. Invisible at strategy-camera distance, and inherent to "one bake from the parent."

## Write-back and shipping

The final UV2s were computed once on appended copies, then written into each source .blend as raw per-loop float arrays by index (meshes are identical, so index-addressing is exact and avoids re-running any matching in-file). Materials got the new AO texture wired through a UV2 map node, color space **Non-Color**. Every mesh's UV2 changed, so every model needs re-export; the game keeps working on the old data until then.

## Gotchas that actually bit us

- **Bake writes into the *active image node* of the material and reads the *active UV layer* of the mesh** — get either wrong and you overwrite your base color or bake against scrambled coordinates.
- **AO rays see the whole scene.** Isolate the model (hide others from *rendering*, not just viewport) unless mutual occlusion is genuinely wanted.
- **New images default to sRGB** in Blender; every data map (AO/N/G/M) must be Non-Color or your preview lies to you.
- **Files saved in Edit Mode** expose empty mesh loop data to scripts — check and switch to Object Mode programmatically.
- **Auto-pack**: if a .blend has "Automatically Pack Resources" on, your carefully-external textures silently embed on the next save.
- **Region margins**: keep a few pixels of inset at quadrant borders (bake margin bleeds), and remember mipmaps don't respect quadrant boundaries — benign for low-frequency AO, but it's why regions get inset at all.
- **AO ray distance is scale-relative** — rescale your world-space AO distance if the mesh scale changes, and re-bake.

## Was it worth it?

One family: ~2,400 faces across six models, resolved to 457 uniquely-baked islands in one quadrant — every shared face sampling the parent's true geometric contact shadows, every damage patch baked from its own broken geometry, zero manual UV work. The whole pipeline is ~300 lines of `bpy`/`bmesh` and runs unattended per family. The difference on-screen is what baked AO always buys: pieces sit *in* the world instead of floating on it — eaves cast onto walls, timbers seat into stone — at zero runtime cost.
