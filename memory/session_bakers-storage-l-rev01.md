---
name: session_bakers-storage-l-rev01
description: Bakers Storage_L revision 01 (lean-to, roof monitor, hoist hood, landing + 27 reused props); crane deferred to an animated step; open items
metadata:
  type: project
---

On 25 Sep 2026 Henno asked for the large storage building's missing additions and props, based on his concept image. He asked that the crane be left for a later animated-element step and that the side entrance stay open (unlike the concept).

Revision 01 is in `Working Files/3D Art/Storage/Storage_L/Bakers/revision-01-additions-props/` (see its README). Henno's source `Storage_L/CSC_Storage_L.blend` is unchanged.

- Additions are `CSC_Fixed_` meshes on the `CSC_Storage_L` rig: roof monitor, hoist hood over the +X upper loading bay, landing, and Henno's `Props/CSC_Storage_LeanTo.blend` mesh at 0.8 on the −X gable. UV1 reuses Bakers building-atlas regions, and UV2 samples a white AO patch (AO still needs baking).
- The 27 prop placements add no new custom assets. `CSC_BAKERS_Flour_Closed/Open` are registered, but they are not in the CSC_Prop_Library catalogue, so the exporter cannot resolve them yet.
- Estimated exported vertices for building + fixed: ~1,493.

**Why:** Storage scenes and the crane are the next items in the art plan (`quarter-building-art-plan.md`, storage section).
**How to apply:** Continue from Henno's latest edited copy of this blend. The next steps are the crane (animated; check hood clearance), PIL decals and CON+PIL for the approved layout, AO bake, and cataloguing the flour sacks. Related: [[project_reusable-prop-library]].
