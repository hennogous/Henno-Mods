---
name: Skill inaccuracy — decal geometry visibility states
description: The civ6-modding art-pipeline.md note "DecalGeometry added directly = always visible" is misleadingly scoped
type: feedback
originSessionId: 17774f60-24d5-4541-bd37-5769e695f7f3
---
The note in `references/art-pipeline.md` (around line 845):

> "DecalGeometry added directly = always visible"

is **only about the reveal animation phase**, not about general visibility. Decal geometry in an `.ast` has full `GroupStates` (Worked/Pillaged/Construction) just like any other `ModelInstance`.

**Why:** Confirmed by user (Henno) who has hands-on experience with the asset system.

**How to apply:** When comparing baked decal geometry vs. attachment-based decals, do not claim baked decal geometry lacks visibility states. The actual distinction is only about reveal animation keying — attachment points can be individually animated in the reveal track; baked decal geo cannot. Both support full GameState-driven visibility via GroupStates.
