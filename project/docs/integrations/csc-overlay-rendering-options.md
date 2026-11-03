# Native overlay rendering options

Inspected 30 October 2026 against the installed Firaxis Lua, ArtDefs, SDK texture
sources and executable binding names. This is a source audit, not an in-game
validation of new CSC artwork. The earlier HTML comparison was a style mockup.

## Established rendering paths

| Treatment | Actual engine path | Work needed in CSC |
|---|---|---|
| Uniform coloured tile fill, with opacity | `BorderOverlay` + `ShowHighlights(true)`, `SetHighlightColor(channel, colour)`, `SetPlotChannel(plots, channel)` | Already used; change palette/classification |
| Direct RGBA coloured hexes | `HexHighlightOverlay` + `HighlightColoredHexes(plots, colour, channel)` + `SetChannelOn(channel)` | Shipped Black Death/WorldBuilder path; bypasses Appeal's caller-alpha replacement; new CSC visual trial still needed |
| Coloured tile borders, including two border colours | `BorderOverlay` + `ShowBorders`, `SetBorderColors(channel, backColour, frontColour)` | Already used; exact two-line mockup geometry is not established by this API |
| Chevron or diagonal-hatch artwork over a hex | `SpriteOverlay` + a `Texture` ArtDef style using `StaticTexture` / `OverlayTexture`, `GeomType=HEX_GEO`, `TintColor` and `NumTiles` | Author/package a pattern texture and CSC styles; create sprites for qualifying plots |
| A small ready icon/badge attached to a plot | `SpriteOverlay` with `RECT_GEO` / `RectDims`, or a `WorldAnchor` UI `Image` positioned with `UI.GridToWorld` / `SetWorldPositionVal` | Author/package the sprite texture or UI image and manage qualifying plots |
| A gradient designed into a tile overlay | The same textured-hex route; native placement includes a gradient texture | Author/package the desired gradient; not a newly discovered procedural gradient API |
| Animated arrows between two plots | PressureOverlay + native FormCorpsArrow + CreateLinearWaves | Add independent layers and valid source/target pairs; same effect family as waves, different artwork |
| Scrolling border artwork | SplineBorder material's SplineScrollSpeed | Configure the material; this scrolls along a spline, rather than identifying a valid economic connection |
| Pulsing/fading map markers | WorldAnchor UI with native AlphaAnim, Cycle=Bounce | Own marker instances and animation state; a pulse alone does not communicate direction |

Chevron/hatch artwork is supported as **texture content**, not a pattern enum or
flag on CSC's current `BorderOverlay`. A ready marker is supported as **a separate
UI image** (or sprite asset), not a built-in `ReadyBadge` feature. These distinctions
are necessary: ordinary fill/border calls alone cannot create those shapes.

The code demonstrates configurable image content and hex/rectangle geometry.
It does not establish pixel-for-pixel parity with the previous browser mockup,
or validate a new CSC texture on every terrain/camera/strategic-view combination.
Those remain implementation and in-game acceptance checks.

## Firaxis source evidence

Paths below are relative to the installed Civilization VI game root.

### Appeal ignores supplied opacity

31 October 2026: runtime SQL and Lua.log both showed the requested 10%/50%
colours, but Henno saw no readiness-opacity contrast in the manual Supply Chains
lens. Read-only inspection of `Base/Binaries/Win64Steam/CivilizationVI.exe`
(SHA256 `e7450823cc8e00468cff7b9d7b97c63140eae38ae1d774ba4efa437556c42d63`)
identified the actual dispatcher limitation:

- `0x1401f7a80` identifies `Hex_Coloring_Appeal_Level`; its branch targets
  `0x1401f7d1a` (also used for water availability).
- `0x1401f7d75` reads the requested packed colour from command offset 0x390.
- `0x1401f7d80` masks it with `0x00ffffff`, discarding alpha.
- `0x1401f7d8a` sets bit 31, making the new alpha byte `0x80` regardless of input.
- `0x1401f7da0` sends that changed colour to the plot-colour assignment function.

Thus this API cannot implement 10% versus 50% opacity on the Appeal carrier.
Earlier CSC source-only alpha assertions did not test this native operation.
The fix keeps native grey background/carrier handling and renders category fills
through an independent Texture/HEX_GEO SpriteOverlay, using baked 10%/50% masks.
The existing bright outline sprites remain separate. Tests now model the native
alpha clamp and check texture pixels/style assignments instead of treating
requested packed alpha as proof of rendered opacity. New fill playback still
requires native visual review after the art build.

Placement's `SetHighlightColor` route is separate: its binding at `0x14021fcc0`
unpacks all four RGBA bytes into floats and passes them to the highlight style.
The Appeal clamp is not evidence of a placement-opacity defect; no placement
rendering change was made in this fix.

Subsequent 31 October review confirmed improved texture opacity, with Tailors'
working normally, but reported stationary Bakers' highlight flicker. CSC now
retains unchanged native sprite/background assignments instead of tearing them
down on every GameCore publish. Exact-plot signatures invalidate on real state
changes; activation still forces the required deferred background repaint.
Ready fill alpha is now 70% (8-bit 178), with unready alpha still 10% (26).
Offline lifecycle checks pass; this flicker correction needs native review.

Latest 31 October styling request supersedes those trial opacities: unready fills
are now 20% (8-bit 51), ready fills 100% (255). Both manual lenses and Quarter
district placement use the same generated Texture/HEX_GEO fill styles, with
separate `CSC_QuarterLens_Fill` and `CSC_QuarterPlacement_Fill` owners. Placement
retains its city-territory filter, native legal/purchase masks and independent
cleanup. The previous BorderOverlay is retained only as a missing-new-art fallback.

### Fills and borders

### Readiness contrast investigation after the 20% / 100% trial

Henno confirms the manual lens is now stable, but screenshot review shows weak
contrast between the improved and unimproved flax plots. This is a rendering
acceptance failure despite correct input alpha, not proof of a classification
failure. Lua.log assigns separate ready/unready buckets. The installed
`CSC_LensPatterns.blp` exactly matches the review cook (SHA256
`6c4a9928038713288e7d8db3ac37e013ac1996cae4d21e128d472ac3a4b782c6`), whose masks
contain alpha 51/255. A stale texture package is excluded for this observation.
The exact final sprite shader/compositing equation has not been established;
100% **texture alpha** must not be reported as verified opaque screen coverage.

Read-only More Lenses inspection:

- `morelenses_colors.sql:1` explicitly comments that alpha does not seem to
  change anything. Its usual fills have alpha 0.5 with different RGB values.
- `Base/Assets/UI/minimappanel.lua:986` (`SetModLensHexes`) sends colour buckets
  through `UILens.SetLayerHexesColoredArea` on the Appeal layer.
- `Lenses/Resource/ModLens_Resource.lua:454` onwards assigns connected and
  unconnected resource groups different named colours through that same API.
  It does not supply a stronger-opacity renderer for CSC to copy.

There is a distinct, shipped native route which CSC has not yet visually tested:

```lua
local overlay = UILens.GetOverlay("MY_PRIVATE_HEX_HIGHLIGHT")
overlay:ClearAll()
overlay:HighlightColoredHexes(plots, UI.GetColorValue(r, g, b, alpha), 0)
overlay:SetChannelOn(0)
overlay:SetVisible(true)
```

Register a private layer with `Type=HexHighlightOverlay`, empty Material, and
normal terrain-following Pass 0. Base Overlay.artdef declares that type for
`HexHighlight` and `Worldbuilder_Continent_Overlay`. The actual WorldBuilder
caller is `Base/Assets/UI/WorldBuilderPlacement.lua:1538`; Black Death's normal
in-game caller is `DLC/BlackDeathScenario/UI/Replacements/MinimapPanel_BlackDeathScenario.lua:94–99`
(with `SetChannelOn(0)` at line 42). Thus it is not limited to the editor.

Read-only executable binding confirms this is separate from Appeal dispatch:
`HighlightColoredHexes` implementation `0x140225e10` reads the requested packed
colour into r13d at `0x140225f0b`, passes it unchanged in r8d at `0x1402260e6`,
and calls the same assignment function `0x140224af0` at `0x140226100`.
It does not apply Appeal's `AND 0xffffff` / `BTS 31` sequence. This establishes
that caller alpha is preserved to assignment; it still does not establish final
visual percentages on every renderer/terrain.

Recommended next trial: private direct hex-highlight fills for both owners,
20% unready and 50% ready, retaining current opaque outlines, readiness rules and
assignment caches. Keep the stable sprite treatment as a fallback during that
trial. Another verified way to distinguish readiness is texture coverage
(outline-only versus filled, or a ready hatch/chevron) rather than opacity alone.
Those are visual alternatives, not implemented changes in this investigation.

The following user-authorized implementation now uses private
`CSC_QuarterLens_Tint` and `CSC_QuarterPlacement_Tint` layers (HexHighlightOverlay,
Pass 0, priority 15, empty Material), supplying 20% unready / 60% ready RGBA
(the latest user adjustment after the 50% and 80% trials).
Every batch uses enabled channel 0, as in Black Death. Exact colour/plot caches
retain stable assignments; independent cleanup and existing opaque edge sprites
remain. The stable `_Fill` sprites and legacy placement BorderOverlay are kept as
fallbacks for older cooked art. Debug output identifies the direct renderer,
requested alpha, assigned packed colours/plot counts and actual rebuilds.
Offline tests and cook checks are separate from the pending native visual trial.

Following the accepted 20%/80% shading trial, the user requested selected-city
sites during Quarter placement too. The placement wrapper now passes all relevant
revealed entries to the shared renderer instead of excluding the focused city's
territory. Native legal/purchase decisions and mask ownership are unchanged.

The cooker schema documents Pass 0 as terrain-following with colour-key/post
processing. Pass 1 uses a flat full-colour plane when grayscale is active;
Pass 2 always uses a flat full-colour plane and lacks MSAA. Changing pass is
therefore not a free opacity correction: it changes terrain following/aliasing.

### Border highlight source

`Base/Assets/UI/Popups/MapSearchPanel.lua:1056–1061` obtains `MapSearch`, makes it
visible, enables highlights, sets two border colours and sets the highlight
colour. This is direct shipped Lua usage, not just an executable string.

CSC uses the same native calls for its owned tile-fill overlays; its earlier
improved-resource borders used them too. Alpha comes from the packed colour supplied to them.
The two border colours should not be described as two independently positioned
concentric outlines without a rendered test of the chosen material.

### Textured hexes and sprites

`Base/ArtDefs/Overlay.artdef`, the `Placement_Valid` / `Texture` /
`Placement_ValidFill_Sprite` entry ending at line 3944, declares:

```text
StaticTexture: OverlayTexture / HexPlace_ValidFill_Overlay
GeomType: HEX_GEO
RectDims: 20,20
NumTiles: 1,1
TintColor: 55,232,14
```

Its `PlacementValidOverlay` layer has `Type=SpriteOverlay`. This establishes
the native textured-hex geometry and configurable texture/tint fields.

`DLC/PiratesScenario/UI/Replacements/MinimapPanel_PiratesScenario.lua:161–170`
obtains an overlay and calls:

```lua
pOverlay:ClearAll()
pOverlay:CreateSprites(spritePlots, SPRITE_PIRATE_TREASURE, 0)
```

`DLC/CivRoyaleScenario/ArtDefs/Overlay.artdef`, `PirateTreasureOverlay`, supplies
the corresponding world-sprite example with a `StaticTexture`, `RECT_GEO`,
`RectDims=80,80`, `NumTiles=1,1`, and white `TintColor`. Its layer is explicitly
`SpriteOverlay`. Rectangle and hex styles are existing engine options.

The SDK documentation's XLP class table describes `OverlayTexture` as the package
for cooked overlay textures used by in-game UI. This is the packaging route for
new CSC pattern artwork; using the rendering primitive does not require activating
the scenario or copying its gameplay logic.

The native SDK source texture `Textures/HexPlace_ValidFill_Overlay.dds` is a
512×512 white hex edge with a vertical gradient. `HexPlace_ValidSolid.dds` is
another native solid-filled variant. These files were opened and inspected;
they are not chevron/hatch textures.

### Ready markers

`Base/Assets/UI/WorldView/DistrictPlotIconManager.xml:2–14` declares a
`Context Layer="WorldAnchor"`, a per-plot `WorldAnchor`, and a 32×32 `Image`.
The image is separate from the ground overlay.

`Base/Assets/UI/WorldView/DistrictPlotIconManager.lua:47–55` creates a plot
instance, converts its plot index with `UI.GridToWorld`, and positions the anchor:

```lua
local worldX, worldY = UI.GridToWorld(plotIndex)
pInstance.Anchor:SetWorldPositionVal(worldX, worldY - 17, 0)
```

This is direct precedent for a custom ready marker and an offset relative to
its map plot. A custom check-in-circle image is ordinary authored image content.
Its final offset, size, stacking and zoom behaviour still need CSC review.

## Limits of the inspection

### Animation evidence added for the connection prototype

Current `Base/Assets/UI/WorldInput.lua` lines 2892–2933 create/reset FormCorps
linear arrows with explicit plot endpoints, colour and speed. The current
`Base/ArtDefs/Overlay.artdef` defines FormCorps as PressureOverlay (Pass 1,
Priority 5.5) with the FormCorpsArrow SplineBorder material and scrolling texture.
`DLC/PiratesScenario/UI/Replacements/MinimapPanel_PiratesScenario.lua`,
AddUnitWaves, supplies pos1=targetPlotIndex / pos2=unitPlotIndex. Those variable
names did not establish playback direction: native user review found CSC's first
adapter backwards. The corrected adapter uses pos1=source / pos2=destination.

Read-only inspection of the current Windows EXE CreateLinearWaves binding at
0x14022ca90 confirms five record keys: pos1, pos2, color, speed, type. Position
values are plot indices, converted to tile coordinates. The call has no per-wave
size or arbitrary-position offset fields. Native material width/spacing fields
exist, but changing those is separate art work, not an extra Lua record parameter.

`Base/Assets/UI/WorldView/CityReligionInstances.xml:72` uses a native AlphaAnim
with AlphaBegin=1, AlphaEnd=0.3, Speed=2 and Cycle=Bounce for a map marker. Thus
native UI pulses are an established alternative, but they do not show direction.
The connection prototype chooses the animated-arrow artwork, not marker pulses.

The SDK's older base Overlay/overlay.xlp lacks the current FormCorpsArrow texture.
The earlier failed clone referenced that absent source and silently substituted
its default. The 31 October width trial resolves this by recovering the original
128x64 RGBA artwork and all eight mip levels from the installed base Overlay.blp,
then packaging that unchanged texture under CSC's own entry name. The adjacent
HexPlace_ValidFill_Overlay was extracted as a control and matches its SDK source
pixel-for-pixel. The extractor pins the actual BLP SHA256 and texture-header/
payload values, failing on an uninspected game build instead of guessing offsets.

### Arrow position, size and draw order — 31 October 2026

The native wave call supports source/destination **plot indices**, packed colour,
speed and type. It still does not accept width, scale, offset or arbitrary world
endpoints. The native adapter retains pos1=source/pos2=destination. These plot
anchors do not establish visible glyph extent on either tile.

The private `CSC_Lens_FlowArrow` SplineBorder now preserves the shipped texture
and material settings except `SplineWidth`: **20 -> 14 (70%)**. Segment length
stays 15, scroll speed .1, and material alpha 128. Both CSC Flow layers reference
this private material; native FormCorps/other mods' arrows are unchanged. The
native cooker accepts it without missing-source/default substitution. This is a
verified material setting, with actual visible width still an in-game checkpoint.

#### Supply-chain path rendering trial (v3)

Native v2 QA confirmed that the world-line chevrons cross borders, but found
thin strokes, fast playback and shifted crossing points. V3 replaces those UI
Lines with the game's **PathOverlay**, used by the stock TradeRoutes layer.
Both trial styles now run from the actual source plot centre to the destination
centre, putting half the path on either side of the shared edge. This replaces
v2's floating zero-height UI geometry and narrower 25%-75% animation interval.
Terrain following and projection use the native path renderer. Native v3 visual
alignment, playback direction and final weight remain review checkpoints.

Each owner has private layers `CSC_Quarter{Lens|Placement}_FlowChevrons`,
`CSC_Quarter{Lens|Placement}_FlowTrade`, Pass 0 /
priority 20. Chevrons use CSC's
unchanged recovered arrow texture. Trade uses Firaxis's `TradeRoutePrimary`
texture, present in the SDK's Overlay.xlp and the game's native Overlay package.
Both use private SplineBorder styles: width18, segment length32, scroll speed.13
and alpha224. This gives filled/bolder artwork instead of2px wire strokes and
one-fifth of the stock trade style's .65 scroll speed. Normal CSC pressure arrows
remain width14/alpha128; the trial never replaces the game's TradeRoute material.
The art generator owns these settings. No per-frame Lua timer is used.
V5 uses native PressureOverlay for the default conveyor, on private
`CSC_Quarter{Lens|Placement}_FlowConveyorWaves` layers (now Pass0/priority20 in V7).
`CSC_Lens_ConveyorWave` uses Pressure's V travel axis (Path uses U), with
transparent padding for the offset described below. Broad sides still follow
one another. Private material `CSC_Lens_ConveyorWaves` uses width18, quad length48
and scroll.10; native wave density3 gives stride8. Its visible slat length5.36
retains the 67% slat / 33% gap ratio. V10 uses white RGB with alpha102 for every
conveyor wave, giving a 40% peak; comparison styles retain yield RGB. This is the
enabled initial default; all three styles share the same logical working links.

Read-only inspection of the shipped DX11 shader library confirmed the distinction.
Pressure pixel shader at library offset0xd7fc8 computes
`fade = 1 - (2*t - 1)^4`, where `t=(distance-offset)/length`, then multiplies
sampled RGBA by the per-wave colour and fade. The Path pixel shader at0xd5140
only multiplies texture RGBA by per-path tint; it has no endpoint envelope.
Setting Border-style `Color_Alpha` alone did not establish 80% native opacity.
V5 explicitly sets the wave alpha and leaves that material field neutral.
`project/tools/lenses/inspect_native_overlay_shaders.py` reproduces the shader
extraction/disassembly and records library/blob hashes; review evidence is in
Desktop/Codex/csc-conveyor-service-lenses-20261101/native-fade-evidence.

Native CreateLinearWaves fixes its offset and length to32 at0x14022d03b–49;
these are not exposed Lua positioning fields. Native LinearWaveVB init at
0x14022c090 loads four position/UV records (data at0x140fcb840/850/860/880):
V=0 maps to quad y=+0.5, and V=1 maps to y=-0.5. Therefore a 48-unit quad
with its glyph centered at V=1/6 shifts that visible glyph +16 along travel:
`(0.5 - 1/6) * 48 = 16`. The 128x256 padded wave texture places a 5.36-unit slat
at that location. This shifts the visible native band onto both sides of the
normal shared edge instead of reverting to the old origin-half footprint.

For a normal 64-unit neighbor step, the visible glyph centres cover16..48:
fade0 at16 (origin tile), peak40% at32 (shared edge), fade0 at48 (destination).
The quartic envelope acts on whole moving slats, preserving their solid faces.
The native density factor is `log(1+speed)*log2(e)`; speed3 gives2, so native
stride is32/(2*2)=8. Fading, visible thickness, spacing and forward offset are
separate controls. Padding and peak opacity are regression-checked, and native
quad evidence is saved as `native-fade-evidence/native-quad.json`. Native terrain
projection and final border placement remain in-game visual review checkpoints.
Human review accepted the fade, then clarified the Religion-only jump as an
apparent reset within half a second. The V6 hold is removed in V7: it did not
finish in the empty UI context, and the user requires immediate animation.

`inspect_native_lens_transitions.py` verifies the pinned DX11 executable's bytes:
SetDesaturation binding0x14019bac0 queues command0x2b; its render handler at
0x140545d80 writes target0x14232a52c. The update at0x140556b70 moves current
0x14232a528 toward the target at two units/second (one-to-zero takes0.5sec).
At0x14054efd3 the current value selects primary overlay mask1 when positive,
mask3 at zero. The loader encodes an ArtDef Pass as1<<Pass at0x14021ac14;
the render loop tests that bitmask at0x14021c01a. Consequently Pass1 migrates
into the primary stage at the end of Religion's fade; Pass0 remains there
throughout. Pressure UV phase samples each layer's own clock at+0x144, advanced
at0x14022c380; ResetAllWaves at0x14022b7d0 clears that object's counts at+0x158
and+0x170. No shared-clock reset was found in those paths.

V7 changes conveyor AND fallback flows to Pass0/priority20 in both views,
keeping them above CSC fills15/15.5. Native fading, width, geometry, spacing and
white/80% RGBA are unchanged. Service sprites now use late Pass2/priority25,
as native map labels do, to appear above district models. Rebuild diagnostics
log count/links/time only when geometry is recreated. Offline evidence is saved
to Desktop/Codex/csc-conveyor-service-lenses-20261101/native-transition-evidence.json.
This addresses the observed timing with a stable native pass; visual acceptance
still requires a full art rebuild/restart and human in-game review.

V8 replaces the conveyor slats with thick open chevrons: stroke5.36 along
travel at each cross-path sample, pitch8, point rise2 after human requests a
less-pointy shape (initial rise4). Whole-area centroid and bounding-box midpoint
retain the previous +16 offset; smaller V is forward. Native width18, white80%,
quartic fade, Pass0 and speed are unchanged. Both source DDS textures are rebuilt.
Tests check stroke coverage, the whole glyph centroid and tip ahead of arms.

V9 bakes a subtle offset black shadow under both the chevrons and original
Service-icon artwork (28% source shadow alpha with Gaussian blur). The chevron
uses per-wave0x66ffffff, reducing its peak to40%; the shadow follows the native
fade. Foreground geometry and centering are unchanged. Service quads double
from24x24 to48x48 world units in both views and remain in late Pass2. Tests use
premultiplied foreground coverage to verify geometry independently of shadow
alpha, preserve original opaque icon pixels/edge colour and check cooked size.
This is a fixed texture effect, not native sunlight shadow casting.

The request to halve the whole belt to16 units is not implemented by this shape
change. The native binding fixes its fade interval at32; its shader computes
1-(2t-1)^4 from position, with no exposed end mask or fade-duration controls.
Slower scrolling stretches time, not distance; global opacity scales every
position equally. Per-texture transparency travels with the glyph and cannot
trim fixed ends of the connection. A different renderer/mask would be required
for a genuinely narrower envelope; no such replacement is enabled here.

After a **full art rebuild/restart** and opening a Quarter lens, enter in a UI
FireTuner console:

```lua
LuaEvents.CSC_QuarterFlowTrial_SetStyle("conveyor")  -- restore default rectangular links
LuaEvents.CSC_QuarterFlowTrial_SetStyle("trade")     -- enable trade-route pattern
LuaEvents.CSC_QuarterFlowTrial_SetStyle("chevrons")  -- enable filled arrow pattern
LuaEvents.CSC_QuarterFlowTrial_Enable(false)         -- restore normal CSC waves
```

`Enable(true)` enables the last selected style (initially conveyor). Choosing a
style also enables the renderer. It is enabled on initial load. Native working
chain records and yield colours are shared, including qualifying Wonder customers;
no gameplay gates or yields change. Unknown style names log guidance and do not
change the current selection. The UI XML is a passive controller context only.

The direct native method is `overlay:CreatePathAlongSpline({source,target},color)`.
Local read-only EXE inspection confirmed the actual signature, not just a method
name: registration0x140008b73 -> wrapper0x140227f20 -> binding0x140228d00 reads
receiver, integer plot-index array (arg2), and numeric packed colour (arg3).
Indices pass through0x1400f1c00; native path builder0x1402274c0 handles wrap and
stores the points. It passes the third argument to0x1409789f0, which unpacks all
four RGBA bytes to floats. Thus no high-level TradeRoutes layer dispatcher is
borrowed and no free-coordinate arguments are invented. `ClearAllPaths` clears
only each private path layer. Native TradeRouteChooser.lua supplies the reference
for the stock renderer/material, although it calls the higher-level lens API.

Sorted wave signatures preserve unchanged path instances/scrolling. Style changes
clear the previous private layer; both owners clean up independently. Missing
new path art leaves normal CSC waves visible through the Ready guard. Native
path wrapping replaces v2's seam suppression. Shutdown removes callbacks without
accessing native widgets. Native stock TradeRoutes, UI headings/hotkeys, static
fill/outline styling, and production selection are unchanged.

The current v5 log reports selected style, ready state, active link count, missing layer
names and width/repeat/scroll/alpha. Geometry/lifecycle/data/API mocks and clean
native cooking establish the implementation contract; in-game v5 appearance is
not proved by those checks. Compare the styles at rest, rotate/zoom, inspect hills
and coast, verify resource -> Quarter -> customer direction, then switch lenses
and confirm/cancel Quarter placement to review cleanup.

Evidence for the recovery layout is corroborated against the actual package and
SDK control; the [reflected BLP TextureEntry fields](https://cru121.github.io/civ6-gamecore-reference/exetypes/blp.html)
were a research aid. The package's serialized record offsets were established
locally and are build-pinned, not inferred solely from that reference.

Draw order does have a supported control. The SDK cooker `Civ6.cfg` documents
that higher overlay priorities draw over lower priorities; Pass 1 joins the
terrain pass when grayscale is off. CSC's two Flow layers now have Priority 20,
above its Tint fills at 15 and final border-fill fallback at 15.5 (previously
arrows were 5.5). This preserves the existing animation and source/destination
semantics. Native cooker and data/API regressions can validate the asset and
assignment; final appearance above terrain fills still needs in-game review.

Read-only executable strings confirm binding names including `SetHighlightColor`,
`SetBorderColors`, `InitializeStyles`, `SetBorderStyle`, `CreateSprites` and
`HighlightColoredHexes`. Strings alone were not used as proof of signatures or
visual output. The active Ghidra program was confirmed to be GameCore XP2, which
is not the graphics executable; it was not switched or treated as rendering code.

No new CSC pattern/badge was installed or visually tested in Civ VI during this
audit. No game, settings, installed mod or Workshop content was changed.

## Applying this to the requested CSC styling

Both views can share one classifier and style assignment: dark-brown base materials,
orange specialty materials, yellow sales; a second transparent hex-edge overlay receives
only improved materials and qualifying customer/Wonder plots. Manual/placement
owners retain separate overlay instances and cleanup, as they do now.

The earlier prototype used a blue check badge for improved Base materials
(`SpriteOverlay`, `RECT_GEO`, 14×14 world units), red chevrons for improved
Specialty materials, and yellow chevrons for ready customer districts/Wonders.
That prototype is now retired in favour of muted fills and category-coloured
hex-edge sprites for all relevant material/customer plots in both views; improvements
and functioning customers add the soft tile fill. Native spline border attempts
stayed invisible in repeated user review; the replacement uses Texture/HEX_GEO
with a transparent-centred ring matching the native placement UV footprint. The
older badge/chevron textures remain dormant. Quarter districts use their mapped identity colours.
Both views share classification/rendering while retaining separate native owners.
Customer-building metadata reuses Stage 3 transaction rows and supplements other
UI mappings separately; economic effects are unchanged.

The new DDS/TEX sources, OverlayTexture XLP/BLP and ArtDef styles passed native
cooking on 30 October. The Base source image was inspected, and mocked Lua checks
verify marker assignment and cleanup. None of this establishes in-game size,
occlusion or zoom behaviour. A normal ModBuddy art build and restart are still
needed for reviewing the latest outline layers; no prototype was installed by this source-audit work.


## Native scrolling material contact sheet (31 October 2026)

`project/tools/lenses/native_animation_contact_sheet.py` inventories installed
base/DLC `Overlay.artdef` SplineBorder styles with nonzero scroll, groups by
texture, and recovers their actual RGBA pixels from the matching Windows BLP.
Current installation has 18 distinct textures in four packages: eight flow/marker
candidates and ten border patterns. All material variants/settings and source
package/pixel hashes are retained in the generated `native-materials.json`.

Flow candidates: FormCorpsArrow, TradeRoutePrimary, ReligiousPressureIn,
LoyaltyPressureIn, ReligiousPressureOut, ZombieSense, PS_English_Pointer,
PS_Dowsing_Rod. The Pirates assets contain actual ship/coin emblems rather than
abstract arrows. ReligiousPressureOut's stock SplineWidth is zero; a visible
private variant needs explicit width. Scenario textures need explicit packaging
for use outside their native scenario; availability in the default game is not
established merely by finding their files.

The sheet preserves raw RGB/alpha, including channel-packed red/green border
masks; those are shader inputs, not intended final map colours. Repeated strips
and the optional GIF are texture studies with normalized geometry/timing, not
native shader/terrain/direction/timing captures. 12/18 recovered textures match
SDK source pixels exactly; the other six have no corresponding DDS in this SDK.
Full mip sizes/name indices/payload bounds are validated for the inspected v2
serialization. Review output: Desktop/Codex/native-lens-materials-20261031.
No game interaction, live console, deployment or runtime acceptance occurred.
