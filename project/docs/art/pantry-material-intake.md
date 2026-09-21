# Approved pantry material intake

Henno approved the pantry candidate previews on 14 September 2026, excluding camp hide racks and fish because CSC is animal-friendly. Exclude these subjects from future prop suggestions.

111 reviewed pantry assets were added to `Working Files/3D Art/Props/CSC_Prop_Library/`. The library now contains 150 individual blends. Its existing 39 blends were preserved byte-for-byte. Seven catalogue entries for absent older CSC_Attached files were removed, and the duplicate Workbench_Narrow entry was resolved in favour of its later corrected material/UV metadata. The original catalogue and notes remain in the intake metadata snapshot.

The six excluded reviewed identities are `IMP_Camp_AN_Rack_LG`, `IMP_Camp_AN_Rack_SM_A`, `IMP_Camp_AN_Rack_SM_B`, `IMP_Camp_AN_Rack_SM_C`, `IMP_Camp_IND_Rack_LG`, and `DIS_HBR_Lg_Fish_Bin`. The eight previously unrendered candidates remain outside the library; their extraction/XML issues have not been resolved.

All additions retain original source geometry, UVs, normals, local coordinates, component mappings, material/state bindings and exact source IDs. No object transforms or AE placement conversions were applied. Source bone/authoring transforms are retained as metadata and hidden references. External shared DDS/PNG textures and source dependency records are included. The Blender material nodes use scalar red channels and decal alpha as in the approved preview renderer; source material IDs, texture bindings and texture data remain unchanged.

Eleven additions are native Construction-state props. Their saved previews use that state, while other additions use Worked. All source state components remain present, with explicit Construction/Pillage visibility/material/burn metadata in `catalogue.json` and `STATE_BEHAVIOR.md`. Native Movie-source and registration caveats remain in the catalogue. Approval of a preview does not establish runtime state availability.

Every new blend was reopened and checked twice: once in staging and once at the final library location. Checks compared vertices, topology, UV channels, normals, exact IDs, component/material assignments, unmodified transforms, relative external texture paths and original texture resolutions. All 111 passed. Existing file hashes were unchanged. This intake did not register duplicate pantry assets in CSC, cook assets, or test them in Asset Editor/in game.

Tool: `project/tools/blender/intake_pantry_candidates.py`. Local selection, conversion and final-location verification reports are under `project/pantry-candidate-review/`; final catalogue and state notes are in the library. The contact-sheet exploration package remains a record of the original review, including rejected candidates; consult the live library catalogue for accepted availability.
