# Modern Level 1 construction and pillage states

**AO correction, 28 October:** buildings atlas is now **r009**. The initial retake
had inconsistent wall-edge winding and inward-facing end walls, causing the
black mottling Henno found in AE's AO view. Four upper wall solids were reoriented
outward in both saved masters, without moving vertices or changing wall UVs.
AO was rebaked at 128 samples with surface normals disconnected and UV2 explicitly
selected. Shortened Wind tie-in beams now have their own AO cell; their newly
exposed ends must not inherit the full shelter's contact-darkened endcaps.
Native AO-only front/back and Water comparisons verify the fix. Evidence:
`Desktop/Codex/modern-l1-ao-fix-20261028`; producers `fix_ao_blender.py`,
`fix_ao_native.py`, `fix_ao_review.py`. All ASTs/placements remain byte unchanged.
For further edits start from these corrected saved masters, not the initial build
recipe. Colour renders at reduced AO strength are insufficient AO acceptance.

28 October 2026. This retake replaces the historical/prototype state shells that
had fallen behind the current modern worked geometry. The worked masters remain
the revision-04 reusable base, revision-10 silo and revision-02 Water Mill.

## Editable masters

Paths below are relative to `C:\Users\Shadow\Desktop\Working Files\3D Art`.

| Master | Path |
|---|---|
| Reusable building and complete shelter | `Level 1/modern/CON+PIL/revision-01/CSC_Level_1_S_Modern_CON+PIL.blend` |
| Separate silo specialization | `BAKERS/Wind Mill/modern/CON+PIL/revision-01/CSC_BAKERS_Mill_Silo_Modern_CON+PIL.blend` |
| Water Mill derivative | `BAKERS/Water Mill/modern/CON+PIL/revision-01/CSC_BAKERS_Water_Mill_Modern_CON+PIL.blend` |

The Water shell is generated from the reusable master by the same rigid placement
as its worked building: translation (-34,20.5,6.15) after undoing the Wind kit frame.
It retains the current river foundation and platform, with their existing AO.
Edit the reusable shell first and regenerate that derivative; do not independently
redesign its walls or roof frame. Current source hashes are recorded in the handoff.

The shells retain the current lower masonry, entrance opening and buried footings
(base and silo reach Z=-30). Upper walls have open, thick edges and exposed roof
framing. The silo retains its worked centre/radius and footings, with an open rim
and shortened elevator. No sack/trolley/pallet debris is authored: Henno owns those
decal placements in AE.

## State assembly

The existing four assets receive the new state GEOs:
`CSC_Level_1_S_Modern`, `CSC_BAKERS_Mill_Silo_Modern`,
`CSC_BAKERS_Wind_Mill_Modern` and `CSC_BAKERS_Water_Mill_Modern`.
Use their Construction/Pillaged selectors in AE. No new standalone AST/XLP entry
is needed for these GEOs. Historical assets and ArtDefs are unchanged.

- Construction shows the shell and scaffolding; Pillaged shows the shell and
  assigns `DefaultBurnMaterial`. All new state groups are hidden in Worked,
  Unworked and Unbuilt.
- The reusable building and Water Mill have the complete shelter front frame.
  Wind hides `SiloFrontFrame` and uses `WindTieIn` shortened members, avoiding
  beams through the now-open silo. The conflicting right-hand building scaffold
  is independently controlled as `ScaffoldSiloSide` and hidden only on Wind.
- The silo specialization contributes its own shell and construction scaffold.
- Existing worked model rows, all saved attachments/placements, Water FX/timelines,
  and Water pillage decals are preserved semantically. Worked GEOs are byte
  unchanged. AE remains the placement authority.

## Timber and shared textures

All B/N/G/M/E artwork remains unchanged. Exposed timber samples the existing
painted wood region of the modern building atlas; U follows each beam's length,
including rotated rafters, with comparable sampling across members. Small end
faces use compact samples, rather than stretching an entire grain patch across
them. `timber-UV-audit.json` records longitudinal alignment and pixels per unit.
Existing aligned wood normal relief follows those UVs.

Only geometry AO changes. New independent cells in the 2048² maps are:

| AO atlas | Shell | Pixel rectangle (top-left origin) |
|---|---|---|
| Buildings | Reusable Level 1 CON+PIL | [0,512,512,1024] |
| Props | Silo CON+PIL | [0,512,512,768] |
| Buildings | Wind-only shortened beam ends | [512,512,640,640] |

Water reuses the building shell's AO after rigid placement. Its river foundation
retains the worked AO. Alternative Wind framing and construction scaffolds are
excluded from the shared shell bake, preventing coincident variants from creating
false dark patches. The shortened Wind members have a separate bake with the
Wind-visible structural context. All unrelated occupied AO rectangles are
pixel-identical; only the state shell and new tie-in cell change in r009.

Published library versions are buildings `2026-10-28_Modern_r009` and props
`2026-10-28_Modern_r005`. Each immutable release includes the prior AO source,
new baked patches, allocation manifest and `scripts/apply_state_ao.py` recipe.
The L2 candidate quadrant and architectural prop candidates are unaffected.

## Firaxis scaffolding check

The native Modern Market (`DIS_COM_Market_Modern`) construction state was rendered
and uses timber scaffolding with `Pillage_Construction_01`. Modern Bank and the
Electronics Factory also bind that material on their construction scaffold meshes.
The separately supplied `PROP_Scaffold_A/B/C` assets are timber and use
`Construction_props`; no specifically modern scaffold set was found in the
survey. Retaining the existing authored timber scaffold sections is consistent
with those references. This is a bounded pantry survey, not a claim about every
Firaxis asset. Native scaffold UVs/materials were preserved and only placement,
uniform scale and section visibility changed.

## Verification and evidence

Evidence root: `C:\Users\Shadow\Desktop\Codex\modern-l1-states-20261028`.
Producer scripts: `project/tools/art/modern_states/`.

Checks cover saved Blender sources, longitudinal timber UVs, exact native FGX
position/normal/tangent/UV/topology readback, one-bone bindings and weights,
all five state resolutions, unchanged worked geometry/attachment data, unchanged
occupied AO pixels, and isolated SDK cooking. The reusable and Water CON masters
exceed the advisory 2,200-vertex target when their scaffold and mutually exclusive
groups are counted together; the scene validator treats this as a warning.

`Modern_L1_State_Comparison.png` is reconstructed from the saved staged ASTs on a
dark background with common framing within each row and emission disabled. It
shows geometry and materials, not runtime burn overlays, debris decals or water FX.
The source update is not a game deployment and does not establish in-game acceptance.

Publication verified 102 file hashes and three saved masters. AE subsequently
regenerated the two AO maps' lower mip levels using the existing `FT_GAUSSIAN`
settings. Their DDS headers and full-resolution AO pixels were identical to the
published files. Those native mip versions were accepted, recorded separately,
and included in a final successful isolated cook.
