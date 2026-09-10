# Model geometry must carry the Civ VI shape hierarchy

Henno's 2026-09-10 review of the first blacksmith: the textured model was a good start but less chunky than the approved concept. In particular, the sloping front roof-edge timber (bargeboard) read as thin trim. He reiterated the supplied Firaxis diagrams: big/intermediate/fine hierarchy, fun and wonky contours, unequal forms, and the rolling-marble principle.

Lesson: inspect a clay render before approving texture work. Large and intermediate shapes should visibly carry the silhouette and weight. More painted detail cannot compensate for thin structural members. The 3:2:1 guidance is visual hierarchy, not a polygon-allocation formula.

Specific modelling lesson: a vertical offset on a steep sloping bargeboard produces very little perpendicular width. Use an offset normal to the roof profile, with mitered corners, and enough depth for the member to read as substantial timber. Thickening/reshaping existing vertices can improve the style without increasing the export budget.

Version 4 in `output/blacksmith-v4/` applies this feedback, with a clay v3/v4 comparison and the same 1,491 CN6 vertices / 781 triangles. Keep taking Henno's visual review as the art-direction reference; this iteration is not a universal numeric template.
