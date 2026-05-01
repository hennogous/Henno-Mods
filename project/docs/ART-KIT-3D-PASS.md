# CSC Art Kit - 3D Model Pass TODO

**Target:** Complete the art kit foundation using Bakers' Quarter as the reference implementation.

## GIMP Tasks

- [ ] **Complete 1K texture templates** — Finish templates for all texture types, keeping paths for accurate recoloring workflow for future Quarters
- [ ] **Scale down recolored 1K textures** — Export to 512x512 versions 
- [ ] **Create texture atlas** — Place 512px textures into quadrants of 1K atlas
- [ ] **Export atlas to DDS** — Final format for Asset Editor
- [ ] **Update Bakers' materials in AE** — Switch from individual textures to atlas system (versions with and without Emissive map)
- [ ] **Consider automated pipeline** — Evaluate automating the AE material update process (noting AE's DDS import processing)

## Blender Tasks

- [ ] **Position 3D models** — Move models to match road layout, bake positioning into geometries
- [ ] **Reference scaling** — Import Library or Market as scaling reference, apply consistent scale to all models
- [ ] **CON → CON+PIL model conversion** — Rename and restructure: remove separate PIL models, create combined CON+PIL models with same positioning and scaling as Worked versions
- [ ] **UV quadrant remapping** — Update UV1 and UV2 mappings to use only the right quadrant of texture atlas instead of full UV space
- [ ] **Create UV3 emissive mapping** — New UV map for shared 256x256 emissive texture
- [ ] **Texture paint emissive map** — Create the emissive texture using Blender texture painting
- [ ] **Export updated geometries** — Use automated pipeline to convert models to .fgx/.geo
- [ ] **Update Bakers' buildings in AE** — Apply new geometries to building assets

## Asset Editor Tasks

- [ ] **Add emissive texture** — Import and configure emissive map for Bakers' materials
- [ ] **Update building assets** — Apply new geometries and materials to Bakers' Quarter buildings
- [ ] **Test and validate** — Ensure all changes work correctly in-game

## Notes
- **Manual-first approach:** Complete Bakers' manually to identify edge cases and document real process
- **Automation for Tailors'+:** Use Bakers' as template to create automated workflows for subsequent Quarters
- **Reference implementation:** Bakers' becomes the gold standard for templating other Quarters