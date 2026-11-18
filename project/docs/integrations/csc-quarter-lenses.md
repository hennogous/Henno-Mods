# CSC Quarter lenses and placement overlay

_Updated 31 October 2026. Manual Supply Chains lenses are now standalone CSC UI.
There is no More Lenses requirement or registration, and no replacement of its
minimap or modal legend scripts. Offline UI/regression checks, native ArtDef cook
and review manifest build pass. Manual native fills are confirmed in-game;
Tailors’ texture fills are confirmed; the Bakers’ stationary-flicker correction
and latest 60% ready fills need native review._

## Manual Supply Chains menu

The reparented CSC radio belongs to its own UI context, so it does not join the
native minimap's `ActiveLens` radio group automatically. When showing a Quarter,
CSC clears checked sibling lens controls in the actual menu, including nested
optional mod rows, while preserving its own entry. It changes check state only;
it does not click the old lens or cause a Selection mode round trip. The settled
activation callback repeats that check cleanup after deferred native/More hooks.
This fixes Empire and Supply Chains appearing selected simultaneously.

`CSC_SupplyChainsLensPanel.lua/.xml` adds one **Supply Chains** radio button to
`/InGame/MinimapPanel/LensToggleStack` after `LoadScreenClose`. This is an additive
control insertion into the existing lens list. The same control IDs exist in the
native and installed More Lenses minimap layouts. CSC does not replace either
`MinimapPanel` or `ModalLensPanel`, create a `ModLens_*` registration, access More
Lenses' registries. Two optional Lua events coordinate the shared native colour
carrier; they are inert without More Lenses. There is one menu entry in either setup.

The entry opens a Quarter selector beside the lens list. Choices come from
`CSC_QuarterMaterialAdjacencyConfig` and real district definitions; currently
Bakers' and Tailors'. Selecting a Quarter updates the fills, ready markers,
title and eight-row key. The choice persists within the UI session.
Opening the menu again uses that selection. Missing menu controls leave the
entry unattached rather than raising an error. Context reloads remove reparented
controls and listeners, and attachment is idempotent.

The large Quarter heading uses native `Locale.ToUpper(Locale.Lookup(...))`.
Switching between already-active CSC Quarters updates the existing modal session
without a Selection round trip, keeping both menus open. Takeover from other
modal lenses also changes the active lens directly, following More Lenses. A
one-shot native context update restores the chooser and repaints after cleanup.
A context refresh provides an additional repaint opportunity. The update removes itself;
closing or native takeover cancels it, so it cannot reopen a dismissed lens.

The new row enlarges the menu by only its own layout height (capped at 40 pixels),
preserving a modded menu's scroll viewport. The selector is a child of the actual
lens panel; CSC's key is reparented to the live native ModalLensPanel. CSC reuses
that panel's actual heading and hides its ordinary key while active, avoiding the
brown TopPanel seam exposed by the earlier HUD header copy. A native-styled
fallback header is used only if the native heading is unavailable. All reparented
controls are explicitly removed at shutdown; the original menu height is restored
if another script has not changed it in the meantime.

### Activation and compatibility

Manual activation uses More Lenses' proven carrier, `UILens.SetActive("Appeal")`.
Only unrelated grey plots use `UILens.SetLayerHexesColoredArea` on
`Hex_Coloring_Appeal_Level`. The native Appeal dispatcher discards caller alpha
and forces 0x80: changing palette alpha alone cannot distinguish readiness.
Category fills now use private `CSC_QuarterLens_Tint` /
`CSC_QuarterPlacement_Tint` HexHighlightOverlay layers and direct RGBA through
`HighlightColoredHexes`, with channel 0 explicitly enabled. The caller supplies
20% unready / 60% ready alpha; final native appearance still needs visual review.
The previous `_Fill` SpriteOverlay layers retain matching masks as fallback art.
Eight palette-tinted styles cover Base, Specialty, Sales and Quarter readiness.
See the native evidence in [overlay rendering options](csc-overlay-rendering-options.md#appeal-ignores-supplied-opacity).
The previous independent `CSC_QuarterLens` BorderOverlay stayed blank in native
QA despite valid plot counts, packed colours and explicit style allocation. Its
ArtDef remains packaged but it is hidden and no longer supplies manual fills.
Ready plots use `CSC_QuarterLens_Ready`, a SpriteOverlay drawing thin hex-edge
artwork through the native placement Texture/HEX_GEO path. Placement has its own fill SpriteOverlay using the same texture masks. Both the borrowed MapSearchBorder and the private spline
material attempts remained invisible in native review despite nonzero assignment
counts. Those ready spline layers are retired; the new sprite edge still needs
native visual confirmation.

CSC owns the heading, legend, menu and shortcuts; no More Lenses registration or
UI replacement is required. When More Lenses is present, activation requests its
normal `VANILLA_APPEAL` carrier through `MinimapPanel_SetActiveModLens` and closes
its old auxiliary panels through `ML_CloseLensPanels`. This avoids stale modded
lens painters and missing-entry diagnostics. On activation CSC registers its
layer-on listener after the loaded native or More Lenses listeners. If Appeal
fires again while CSC owns the carrier, CSC clears the stock colors and restores
the Quarter title in that event. A one-shot `ContextPtr:SetUpdate` still handles
deferred hooks.
The native context refresh also repaints while activation is pending. The latest
runtime log contained no earlier `SystemUpdateUI` finalization receipt, so that
was not retained as the activation renderer's only scheduling path.

Changing a modal lens no longer makes an intermediate Selection transition.
Firaxis `WorldInput.OnInterfaceModeChange_Selection` itself calls
`UILens.SetActive("Default")`; a queued transition can therefore reset graphics
regardless of CSC's own stale-notification guard. More Lenses' direct activation
pattern avoids creating that transition in the first place.

Shared-layer ownership is explicit. Closing CSC clears its own native background,
private textured fills and outlines. Native/More takeover relinquishes ownership and clears only CSC's
private art, preserving the new owner's colour data. Carrier-off, native lens
hotkeys, the menu radio check changing, and More Lenses' modded-lens selection
signal all dismiss CSC. The check handler defers its response so clicking the CSC
parent off still closes normally. Escape, player/mode changes and shutdown clean
up; pending frame updates are cancelled so they cannot repaint a new owner.
Unrelated label layers do not dismiss the active CSC carrier.

Henno confirmed native manual fills now work. No claim is made that the independent BorderOverlay's
underlying native graphics failure was conclusively identified.

The public events `CSC_SupplyChainsLens_OpenPanel(quarterKey)` and
`CSC_SupplyChainsLens_Refresh()` now target this standalone controller. The first
accepts an optional key such as `BAKERS` or `TAILORS`.

### Q+number shortcuts

Hold **Q** and press **1** for Bakers' or **2** for Tailors'. These are fixed
Quarter identities, independent of menu sort order. Each submenu choice now
explicitly opens its Quarter, even if native mode/layer cleanup has already
deactivated the controller. Ownership is set after synchronous mode cleanup.
The shortcuts use a global input observer and the same activation controller as
the menu/event; no native UI replacement is added. More Lenses does not register
a global input handler in the installed source inspected for this integration.
Pressing a number repeatedly while holding Q can switch Quarters, but key repeat
does not reopen a lens. Both edges of captured keys are consumed, including when
Q is released before the number, to avoid native 1/2 lens actions.
The 1 November human log showed repeated delivery of the same number-up, with
World-context restoration between deliveries; the first delivery was masked but
the second launched Religion. Capture now stays latched after release until the
next fresh press of that key. Repeated releases therefore remain masked without
capturing a subsequent standalone 1/2 press. Regression tests replay each edge
twice and three times, in both release orders, with and without More Lenses;
the previous release-clearing code fails that case. A repeated plain-Q release
also toggles resources only once. Human in-game acceptance remains pending.

Shortcuts apply only in World input context, in selection/manual-lens mode, with
a local player; they are disabled during district/building placement, WorldBuilder,
gesture recording, other input contexts, and focused visible text controls.
Visible-control traversal happens on candidate keystrokes only, accommodating
unnamed or reparented text fields. Ctrl/Alt/Shift combinations pass through.
Excluded-mode/player/focus changes cancel pending chords; transitions between
allowed map modes retain the held Q prefix. A number must be pressed after
Q; a previously held number's repeat does not qualify.

Q serves as the prefix. A Q tap alone reproduces the native resource-icon toggle
on release if Q is still bound to `ToggleResources` and that action is enabled.
Using a chord never toggles icons. Bare 1/2 retain their native handling. These
chords are currently fixed in Lua, not entries in the game's rebinding menu.

The first context-only shortcut implementation failed in Henno's game: Q toggled
resources and 1 launched Religion. A handler's `true` only stops later handling
inside the same UI root (SDK `LUA Input`); it is not a global interception promise.
The native global Lua callback also discards the Lua return. Consequently the new
observer uses `Input.PushActiveContext(0x20000000)` to exclude World actions for
handled key events. A deferred refresh or native `SystemUpdateUI` tick restores
the previous context, and the next input also drains any previous mask first.
Only the owned top context is popped; a newer popup above it is preserved until
the owned mask resurfaces. No saved bindings are rewritten. The global callback
is a shared native slot; another mod using that slot would need coordination.
No such use was found in the installed Workshop Lua inspected here.

Firaxis itself uses this slot: `Base/Assets/UI/Utilities/TunerUtilities.lua`
registers `TunerUtilities.OnInputHandler`. The native setter replaces a single
Lua reference at UIManager `+0x5948`; it does not chain observers. A later
registration can therefore remove CSC's observer before Q is pressed, even from
default map view. CSC now reattaches after `LoadScreenClose`, UI-context reload,
and app focus returns, with one additional `SystemUpdateUI` handoff callback.
It does not reinstall every frame. Shutdown removes a queued repair. This covers
load/focus ordering; an unrelated later replacement still needs coordination.

Offline regression replaces the global slot during game-load/focus handoffs,
then presses Q+1/Q+2 from selection mode. The previous package fails; the repair
passes with and without More Lenses, without leaking native resource/digit actions.
The 31 October log examined belongs to an automated game with no human shortcut
attempts, so its absent key messages are not evidence of a lost observer. Native
acceptance of this repair remains pending a human rebuild/manual test.

The updated test dispatches native Q/1/2 actions before the ordinary context
handler and ignores the global callback return. It covers masks/restoration,
multiple events before refresh, missing refresh ticks, nested popup contexts,
inactive submenu activation and synchronous layer cleanup. Native QA confirms
that both chords now launch the heading. Latest tests additionally model the
native Selection handler resetting the engine lens to Default, verify that
activation avoids this transition, and exercise delayed More Lenses painting
followed by CSC's context-update repaint. Takeover preserves replacement colours.

When a native Appeal hotkey follows CSC, the controller relinquishes ownership
and restarts the already-active carrier through Default -> Appeal without an
interface-mode change. Vanilla's same-name SetActive is otherwise a no-op, so
its layer-on handler never restores the actual Appeal colours. More Lenses has
the same restart in ToggleAppealLens. Tests model the no-op, both Quarters and
native callback ordering; replacement colours survive CSC cleanup.

### Diagnostics

Hotkey diagnostics are off by default. Set `DEBUG_HOTKEYS = true` in
`CSC_SupplyChainsLensPanel.lua` to trace observer
installation/reattachment; physical key edges and eligibility reasons; recognized
Q+1/Q+2 shortcuts and their activation result; plain-Q resource toggles;
cancelled prefixes; and native-lens actions while a Quarter or Q prefix is active.
Look for `shortcut Q+1 -> BAKERS` followed by
`shortcut result quarter=BAKERS active=true`.

Mask diagnostics occur once per physical key edge, even when the native bridge
delivers that same edge repeatedly. Routine context-restoration, overlay palette,
fill/outline, service-marker counts, animation rebuilds and menu/lifecycle traces
are silent. Their debug-only summaries/counters were removed. Service UI and
MCUIS startup/Civilopedia-click traces are also silent. Invalid explicit flow
style commands still print their usage warning. Tests verify that repeated
refreshes and duplicate key delivery stay quiet with the default setting.

Read-only native inspection used `CivilizationVI.exe` SHA256
`E7450823CC8E00468CFF7B9D7B97C63140EAE38AE1D774BA4EFA437556C42D63`.
Its `SetGlobalInputHandler` registration resolves through `0x14088eb00` to
`0x140896b30`; delegate `0x14088b940` calls the Lua input bridge then returns
false unconditionally. The global delegate loop at `0x140892870` precedes ordinary
context traversal in the UI input dispatcher. This establishes observation order
within that dispatcher, not a completed runtime test of the World action matcher.
Native `InputConfiguration.xml` assigns ToggleResources/LensReligion/LensContinent
to World context, and XP2's `InGame.lua` demonstrates paired context push/pop.

## District placement

`PlotInfo_CSC_QuarterPlacement.lua` preserves native PlotInfo and augments Quarter
placement only. Its separate `CSC_QuarterPlacement_Tint` HexHighlightOverlay and
`CSC_QuarterPlacement_Ready` hex-edge SpriteOverlay draw 40% outlines on
every relevant tile, with 40% fill for ready tiles and 20% for unready tiles.
Standard district and Wonder placement pass through. Placement validation,
purchase markers, adjacency previews and queue operations remain native.

Automatic placement highlights all relevant revealed plots, including the focused
city's own materials, customer sites and Quarters, other cities and unclaimed
territory. The former focused-city exclusion is removed. These coloured planning
plots extend the brightness mask only, including the faint fill on
unready sites. These plots never become legal placement
or purchase tiles. Confirmation, cancellation, direct switches and shutdown clear
placement's own fills and outlines. Missing fill art preserves ordinary native
placement; missing outline art leaves CSC fills available. Placement shows only
static fills, outlines and the native adjacency preview. Service medallions and
animated links are exclusive to the manual lens.

The manual lens preserves the map's saturation. A 45% black shade sits below
the coloured fills and outlines on revealed unrelated tiles and tiles outside
the selected Service chain. The shade, fills and outlines use terrain Pass 0,
like the placement overlays, so 3D models draw above the tile highlights.

## Shared data and palette

Both overlay views and the legend share Base `#813a00`, Specialty `#ea8706` and
Sales `#b6a835`. Goods Providers use grey `#999999` when their
Quarter has City Lights Goods Provider tags. The same RGB is used for the
placement and lens fills, edges and legend swatches.
Unimproved Base uses 30% opacity; other unready sites use 20%, and ready sites use 60%. Quarter identity colours are:

| Quarter | Colour |
|---|---|
| Bakers | `#5f821c` |
| Tailors | `#9037aa` |
| Apothecaries | `#0e54a9` |
| Carpenters, Stonemasons, Blacksmiths | `#be6b0a` |
| Brewers, Goldsmiths | `#c2af38` |

Quarter fill, edge and legend all use the selected Quarter's identity hue.
The art generator executes the palette SQL to resolve its derived colours,
then emits matching Quarter edge styles and both fallback fill states.

`CSC_QuarterLensSupport.lua` classifies plots for both surfaces. Material membership
comes from `CSC_QuarterMaterialAdjacencyConfig.SourceTag` plus `TypeTags` and
actual resource definitions. `SourceFilter` follows SQLite LIKE behaviour. Resource
discovery and revealed-plot checks apply in both views. Sales districts come from
`CLASS_CSC_<QUARTER>_SALES` tags, including the adjacency processor's propagation
to direct unique district replacements.

`CSC_QuarterWonderSales` in `Data/CSC_Q_ALL.sql` maps Quarter keys to Wonder
building types. Tailors' SQL declares Bolshoi Theatre, Broadway and Sydney Opera
House, matching its existing Stage 4 Wonder customer Services. The classifier
paints their revealed, completed plots yellow in both views. It accepts the
plot completion flag or the city's ownership of the Wonder identified by the
plot, as the stock tooltip does. On a Wonder district with no plot Wonder type,
the city's exact-plot building list can supply the completed mapped Wonder.
This planning metadata grants no adjacency or Service. Additional mappings belong
in owning Quarter or compatibility SQL, without Lua edits.

Customer-building readiness reuses `CSC_Stage3CustomerTransactions`, keyed by
seller Quarter district. The supplemental UI-only `CSC_QuarterCustomerBuildings`
table covers other stages: Bakers' Granary, Zoo and Ferris Wheel; Tailors'
Lighthouse and Amphitheater; the conditional Garden patch adds Conservatory.
Stage 3 supplies Market for Bakers', and Market/Temple for Tailors'. Direct
one-level unique building/district replacements are accepted. A building must be
on that specific plot, present and unpillaged; the district must also function.
The native UI query is `GetBuildingsAtLocation(plotIndex)`; do not use the
gameplay-only `GetBuildingLocation` from these UI contexts. These mappings do not
change economic effects or guarantee that every other gameplay gate is satisfied.

The palette is shared across Quarters:

| Category | Treatment |
|---|---|
| Base materials | Brown outline; 30% fill before improvement, 60% when improved and unpillaged |
| Specialty materials | Orange outline; 20% fill before improvement, 60% when improved and unpillaged |
| Customer districts | Yellow outline and 20% fill without a functioning customer building |
| Customer buildings / Wonders | Yellow outline and 60% fill when a matching customer building functions; mapped completed Wonders qualify directly |
| All Quarter districts | Opaque identity-colour outline; 20% fill without a functioning Quarter building, 60% with one |
| Unrelated revealed plots | CSC-owned neutral grey in the manual lens only |

All relevant sites have a category-coloured fill: alpha 0.30 for unready Base,
0.20 for other unready sites, and 0.60 after readiness, with opaque bright outlines in both states. Only unrelated plots
receive neutral grey in the manual lens. Placement includes relevant sites in
its brightness mask, so unready sites receive their faint category colour without
extra native dimming. Each Quarter identity colour follows the same 20%/60% rule, using exact-plot
functioning Stage 2/3/4 buildings; automatic river flags and hidden Service grants
do not upgrade the state. Fills are uniform hex tints, not procedural gradients.
Each edge layer uses `CreateSprites` with four category groups. One HEX_GEO
sprite is created per relevant material/customer/Quarter plot, so adjacent plots retain separate
edges. `CSC_Lens_HexOutline` is a 512-pixel white alpha mask matching the native
HexPlace_ValidFill_Overlay UV footprint, with only a thin ring and a transparent
centre. The styles supply category/Quarter identity RGB; no extra fill, gradient,
badge or chevron is drawn. Ready layer type, empty Material, priority 0, HEX_GEO
and RectDims 20/20 follow native PlacementValidOverlay/Placement_ValidFill_Sprite.
`S.DrawOverlay` and `S.ClearOverlay` own separate fill/outline pairs for Lens and
Placement. Both clear on exits; one owner never clears another.

Static sprite groups are cached by exact plot indices, style and channel.
Unchanged GameCore/UI refreshes do not clear, recreate or hide the native fill
and outline sprites. A readiness change replaces only the affected sprite layer;
Quarter switches and close/reopen invalidate the relevant assignments. Native
grey background assignments are also retained when unchanged, with an explicit
settled activation repaint after deferred Firaxis/More Lenses callbacks.
Fill/outline diagnostics were retired in the 4 November log cleanup. Caching
addresses repeated teardown/recreation found after Henno reported stationary
flickering in Bakers' while Tailors' remained fine; native confirmation is pending.

Both views use the shared `CSC_Lens_HexFill_Unready` and
`CSC_Lens_HexFill_Ready` masks, generated from the same palette's alpha values.
Their centre pixels have alpha 51 and 153 (20% and 60%). Base unready styles
use a separate `CSC_Lens_HexFill_BaseUnready` mask with 30% alpha (76/255),
so the sprite fallback matches the direct RGBA fill. They stop
inside the outline ring so render order cannot soften its opaque colour.
If the new fill layer is unavailable, Lua falls back to native coloured hexes.
Routine fallback diagnostics are silent. A full art rebuild/restart is required
to review the corrected opacity; a Lua-only update cannot supply new artwork.
Placement owns `CSC_QuarterPlacement_Tint` independently of the manual tint layer.
Both native tint layers cache exact colour/plot assignments. The `_Fill` sprite
layers use the same palette as fallback art; the previous BorderOverlay remains
the final placement fallback.
If its direct tint art is unavailable, the sprite path remains usable;
standard district placement and the native legal/purchase overlay are preserved.

The eight legend entries contain plain text without text icons: Quarter without
Buildings, Quarter with Buildings, unimproved
and improved Base, unimproved and improved Specialty, Customer District, and Customer Building / Wonder.
Unready rows use native `Controls_KeySwatchHexEmpty`; ready and Quarter rows use native
`Controls_KeySwatchHex`. No nested/resized swatches remain: they drew visibly
offset overlapping hexes in user review. This is Firaxis AddKeyEntry's own
hollow-swatch mechanism. Dedicated opaque legend colours keep the key legible independently
of terrain-fill opacity. Labels are short phrases, e.g. Unimproved Base Materials,
Improved Base Materials, Customer District and Customer Building / Wonder; natural
wrapping replaces forced two-part labels. The larger scrollable key accommodates the separate readiness rows.

The palette has 48 gameplay RGBA rows, including all eight Quarter identity
colours with 20%/60% fills and opaque outline/legend variants, six yield-flow
colours, the shared material/customer palette, neutral grey and generic fallback
colours. `CSC_LensQuarterColors` maps each Quarter key to its colour family;
these mappings do not enable a lens without the normal adjacency configuration.
It is independent of
`COLOR_MORELENSES_GREY`. Use `UpdateDatabase` for this legacy gameplay `Colors`
schema consumed by `UI.GetColorValue`; `UpdateColors` targets a different schema
and caused the original missing tints/white legends.

`project/tools/lenses/build_chevron_art.py` deterministically generates the fill, outline and retained prototype
DDS/TEX pairs, `XLPs/CSC_LensPatterns.xlp` and the overlay styles/layers. The earlier
badge and chevron textures remain packaged but are no longer drawn. Ready styles
all reference the new outline mask. Use
`--check` to verify reproducibility and palette-linked tint values. The DDS files
have complete native RGBA mip chains; TEX stores the last mip index. A one-level
DDS produced a zero-sized BLP block despite cooker exit 0, so inspect cooker logs
as well as the return code. `Civ Supply Chains.Art.xml` registers the new package.

## Loading

### Directional connection prototype

Both views now add independent `CSC_QuarterLens_Flow` /
`CSC_QuarterPlacement_Flow` layers. These are native PressureOverlay layers,
Pass 1 / Priority 20, using CSC's private `CSC_Lens_FlowArrow` material. The
effect is animated arrows rather than the religious-pressure wave artwork.
It uses `CreateLinearWaves` at native speed 2; CSC does not borrow or clear the
native FormCorps, religion or loyalty layers. Animation is world-map only,
matching the native layer's ShowOnMap=false / ShowOnWorld=true settings.
The SDK's `Civ6.cfg` defines higher priority as drawing over lower priority.
Pass 1 folds into the terrain pass when grayscale is disabled. The former 5.5
priority was below CSC's Tint fill (15) and fallback border fill (15.5); 20 puts
the arrows over both. A full ArtDef rebuild is required for this ordering change.

`GetFlowLinks` derives links from the selected Quarter's revealed plot entries:

- Improved owned Base material → adjacent completed, unpillaged Quarter with
  its functioning Stage 2 buyer building (either Bakers mill, or Textile Workshop).
- Improved owned Specialty material → adjacent completed, unpillaged Quarter
  with its functioning Stage 4 buyer (Café or Fashion House).
- Quarter with matching functioning producer → adjacent owned functioning
  customer district with the required building. Stage 3 reads exact seller and
  customer building pairs from `CSC_Stage3CustomerTransactions`.
- Completed mapped Tailors Wonder → treated as a customer endpoint supplied
  by the adjacent Fashion House; the animated direction is Quarter → Wonder.

Arrow colours describe the delivered yield, independently of the tile colours.
Base and Specialty inputs use the Quarter's material flow yield from
`CSC_LensQuarterColors`: Food for Bakers and Culture for Tailors. Outgoing
district links read `CLASS_CSC_<QUARTER>_SALES_<YIELD>` tags, the same return-yield tags used by
the adjacency processor, including propagated unique districts. Bakers' Granary/
Market flows use Food; Zoo/Ferris Wheel/Garden use Culture. Tailors' Lighthouse
uses Production; Market/Temple/Amphitheater use Culture. `CSC_LensFlowYieldColors`
maps yields to CSC's exact UI palette rows: Production `#894000`, Gold `#fdec5d`,
Food `#468419`, Culture `#bb44bd`, Science `#0873e1`, Faith `#a7bede`. Unmapped
yields do not invent a generic outgoing colour.

`CSC_QuarterWonderSales.CustomerYieldType` supplies the corresponding Wonder
yield; all three Tailors' Wonder customers receive Culture, matching their
existing gameplay modifiers. They use the same Quarter-to-customer direction,
producer/readiness checks and purple arrows in both views. The mapping changes
UI metadata only; it does not create new economic effects.

Both ends must belong
to the local player; cross-city connections are allowed. Building locations,
district completion, building/district pillage and resource discovery are checked
through native UI APIs. No UI hover/placement candidate is invented as an active
producer or buyer. Placement includes selected-city sites too, so existing
working connections within that city can be shown alongside cross-city links.

`CSC_QuarterFlowBuildings` records UI stage membership in owning Quarter SQL.
`ProducerStage` on supplemental customer/Wonder mappings supplies Stage 2/4
relationships, including the additive Garden patch. This metadata changes no
economic effects. The arrows establish adjacency/ownership/building readiness;
they do not compute yields or assert every additional Service unlock condition.

Native user review established that positive-speed arrows travel from `pos1` to
`pos2`. The earlier interpretation from pointer variable names was backwards.
CSC now uses pos1=source / pos2=target, anchoring material flows at the resource
tile and outgoing sales at the Quarter. Link records retain explicit source/target
fields independently of the renderer.
Per-owner sorted signatures prevent repeated UI refreshes from restarting an
unchanged effect. Changing a connection resets/rebuilds it once; leaving a lens,
placing/cancelling a district or shutting down clears that owner's waves. Missing
flow art leaves static colours/outlines usable. Effect-layer and connection
signatures remain available internally; routine rendering logs are silent.

The narrower native-arrow material uses the unchanged shipped FormCorpsArrow
texture recovered from the installed BLP, including all eight mip levels. The
private `CSC_Lens_FlowArrow` material changes only SplineWidth 20 -> 14 (70%);
segment length 15, scroll .1 and alpha 128 are retained. This solves the previous
SDK missing-texture/default-substitution problem without overriding native art.
`extract_native_flow_texture.py` is build-hash-pinned, and a control extraction
matched the SDK HexPlace texture's pixels exactly.

Native CreateLinearWaves positions remain integer plot indices; there is no wave
offset/scale parameter. Native v2 trial QA confirmed visible world-line chevrons,
but reported thin/fast strokes and offset crossings. The v3 comparison replaces
them with private native PathOverlay comparison layers. The current default uses
thick forward chevrons on native PressureOverlay with its quartic fade. Width 18
and wave density 3 give an 8-unit stride with 67% stroke and 33% gap. The
6 November update increased the point rise from 2 to 2.2 world units and the
material scroll from 0.10 to 0.11. Per-wave RGBA defaults to alpha 128 (50% peak).
The 48-unit quad's transparent padding shifts its visible 5.36-unit slat forward16.
This compensates the native wave footprint and places the fade band across the
shared edge: fade in on the origin side, peak at the border, fade out on the
destination side. The shader and quad/UV mapping are verified from native files;
exact terrain appearance still needs native review. V9 uses white RGB for the
conveyor. Existing logical endpoints and
chain gates remain; yield colours are retained in the semantic link records and
the optional earlier comparison styles.
No per-frame UI Lines or host sizing code is active.
V8 replaces the rectangular links with white thick chevrons; a follow-up halves
point depth from4 to2 while retaining width18, stroke5.36 and 80% peak opacity.
The complete glyph centroid retains the +16 offset that centers the native band
on the shared edge. Its pointed tip faces V=0, verified as forward in the native
quad. This is not a half-length belt: the requested16-unit travel band remains
unimplemented. CreateLinearWaves fixes offset/length to32, and its fixed quartic
fade has no separate start/end duration or cutoff parameter. Overall opacity
and scroll speed cannot shorten that spatial band; texture alpha follows each
moving glyph. The native backend is retained while these alternatives are being discussed.

V9 adds a slight black drop shadow beneath the chevron and Service foregrounds:
28% source alpha, small offset, Gaussian blur; this is part of each texture and
not a sun-driven world shadow. Chevron RGBA is now0x66ffffff (40% peak), so the
shadow receives the same native fade and opacity multiplier. Original chevron
foreground width, shallow point, white colour, 67/33 stroke/gap and travel span
remain. Service quads double both dimensions to48x48; opaque notification-icon
pixels are unchanged and their antialiased edges composite over the shadow.
Both views share these styles. Full texture/art rebuild is required.

Human QA refined the Religion-only jump to an apparent animation reset within
half a second. Offline native inspection found a matching render-stage change:
Religion sets desaturation to 1, its exit sets the target to 0, and the renderer
interpolates at two units/second. While positive, the primary overlay stage uses
mask1 (Pass0 only); at zero it uses mask3 (Pass0 and Pass1). Our old Pass1 flows
therefore changed stages mid-animation. Pressure clocks are per-layer, and
ResetAllWaves clears only the addressed layer's records, not a shared clock.
V7 puts both conveyor and fallback flows in Pass0, priority20 above fills15/15.5.
Activation is immediate; the V6 delay is removed (the human log showed it
starting without finishing in the logic-only context). The temporary rebuild
counts and clock traces were removed in the 4 November logging cleanup. Static native evidence and cook
checks pass; native visual confirmation remains pending.

Use `LuaEvents.CSC_QuarterFlowTrial_SetStyle("trade")` or `("chevrons")` in a UI
console after opening a lens; either enables that style. `Enable(false)` restores
normal CSC pressure arrows; `SetStyle("conveyor")` restores the new default.
The conveyor is enabled on initial load. Four private path layers and two private
`_FlowConveyorWaves` layers keep all three styles/owners separate from stock
TradeRoutes. The new identity avoids wave calls on the former cooked PathOverlay.
Missing new art
preserves the normal effect; unchanged path assignments retain animation state.
See [native API evidence, materials and review steps](csc-overlay-rendering-options.md#supply-chain-path-rendering-trial-v3).
A full art rebuild/restart is required for the V7 pass changes.

### Functional Service pins � current, 1 November 2026

The manual lens uses camera-facing **hinge-free notification circles**
(option B from the 2 November backing comparison, selected 4 November), with the
actual registered `AbilityIcon` for each working Service. The native frame is
`ActionPanel_Notification2`, also used by the game's own Action/Notification UI.
Quarter and Service image controls use `SetIcon(name, 256)`, so the
game picks the registered slot from the existing Quarter atlas. The GIMP atlas
exporter adds all 11 mip levels to the 1024 px sheet with 256 px icon slots.
The four 256 px map atlases use the UI texture cook parameter
`IsScalable=true` to match stock resources. The Windows cooker otherwise
packs only the base level into its UI block format, even when the DDS has a
full chain. The scalable cook generates its own mip pixels from the base.
A 9 November control test replaced the source lower levels with magenta
and produced the same cooked payload. The complete cooked package contains
10 levels for Flax and Flax FOW and 11 for Bakers and Tailors.
Smaller sheets serve other UI contexts and have one level. Both backings draw
the brass from a bevel profile, with the stock texture sampled only for the
navy gradient. The hex rim uses a single bevel highlight. Backings have their
own 256 px mip chains.
Both pin types use the stock resource icon's world position (`worldY - 16`)
and a scaled, camera-facing WorldAnchor. A 256 px image control at 0.037
world units per pixel keeps the visible badge footprint close to Flax. The
383 px backing control preserves the earlier 120 px control at 0.118 world
units per pixel. One Service is
centred at the anchor. Two sit side by side, three form a triangle and four
form a square. Their spacing scales with the pins. Only the selected Quarter's
Services appear.

`CSC_QuarterServicePins` remains the internal WorldAnchor context name. It draws
UI above district models, without saved player map-pin objects. It joins
`/InGame/WorldViewControls` and explicitly calls `SetHide(false)`: native InGame
loads added UI contexts hidden. `LoadScreenClose` retries a missing parent.
Routine marker initialization and attachment logs are silent as of 4 November. Human screenshots confirmed the prior pointed pins render;
notification-circle placement and visual proportions still require in-game review.

`CSC_ServicePresentation.lua` is the shared reader and formatter for MCUIS and
pins. It reads the existing `CSC_AbilityAttachModifiers` registry and active
`GameEffects` district subjects, including Wonder Service anchors. SQL owns all
civic/material/producer requirements. Neither persistent Service grants nor
city-wide art flags prove that an exact owner/city/district currently receives
a Service. Duplicate producers contribute to the current benefit total without
creating duplicate pins of that Service on the same plot.

Hover uses the same `AbilityDesc` localization and total-amount/signed-stack/
plural-count parameters as MCUIS: Service name, cumulative current city effect,
and supporting Supply Chain line. A pin is restricted to its exact served
customer district, while its tooltip deliberately retains MCUIS's city totals.
When multiple effect branches share one Service target (e.g. Water/Wind mills),
that Service's pin combines their existing MCUIS tooltip sections. It does not
invent a separate benefit calculation. Right-click sends `OpenCivilopedia` with
that same `AbilityIconTarget`, just like the MCUIS icon.

Left-click focuses the exact Service and customer plot. Clicking the focused
pin again restores the full lens. Clicking another pin switches focus.
Removing the selected Service also clears focus. Other medallions use a
grayscale copy of the SDK notification backing with their glyphs at 50% opacity.

The flow registry identifies adjacent working producers for the Service stage.
Stages 2 and 3 include improved, unpillaged Base feeders. Stage 4 also includes
improved, unpillaged Specialty feeders. A Stage 3 or 4 producer without a working
Stage 2 building still gets its Base feed during focus. Focused tiles retain
their ordinary fills and outlines. Other relevant tiles, including unimproved
and pillaged materials, use 30% outlines over the shaded terrain. Ready tiles
have 30% fills and unready tiles have 10% fills. Chevrons peak at 80% for
the selected chain and 10% elsewhere.

Each highlighted Quarter tile also has a camera-facing district icon. Clicking
it focuses that exact plot and adjacent materials, Goods Providers and
customers, including unready sites. Only working transaction links touching the
selected Quarter get focused animations. Quarter focus and Service focus share
one selection. Quarter pins use the 256px atlas faces inside their brass hex
frames. Bakers and Tailors use slot 0 for the color face and slot 2 for the
grayscale face. Unfocused Quarters switch both the icon and frame to grayscale.
The 12 November round-glyph trial was reverted on 16 November. Re-export the
Quarter XCFs with the Civ VI atlas exporter when changing the icon artwork.
Regenerate the custom backings with
`project/tools/lenses/build_quarter_badges.py` and the SDK's
`ActionPanel_Notification2.dds` as input.

The Quarter tooltip builds on hover and is cached for the current lens snapshot.
Adjacency reads CSC's encoded amounts once. Only registered stock adjacency
rules use the native plot query, since the built-district read can already include
CSC's effects. Outbound contributions are attributed to this plot. Transactions use active yield
modifiers with a Quarter building as a source or receiver. Direct adjacent
payouts are read from the gameplay attachments and matched to the working
producer and the exact recipient plot. This includes Gold and Production
paid to improvements and the Food paid by a Mill to a Granary. Each direct
payout is counted once even if the same effect appears in the UI's active
modifier list. Stage 3 reads the
rates encoded by CustomerPopulationReturns and decodes them against the city
receiving that effect. The customer population sets the original target on both
sides. Customer aggregates and trade imports are apportioned across their
eligible suppliers. The Service list joins active recipient pins to the exact
Quarter's outgoing stage links and checks the producer eligibility property.
Ordinary district Services can also use the mirrored art flag if the source
property is unavailable. Wonder Services use the Fashion House's separate
eligibility property.
Specialist yields use the stock plot-tooltip worker count and per-worker yield.
Maintenance uses district and building costs from their database rows, as in
Better Report Screen's building expense breakdown.
Trade-import Food, Culture and Amenities read the active route-count leaves,
including the BIT_2/4/8/16 companions. Their native amounts already include the
bit weight. Attribution to supplying Quarters is proportional to eligible route
counts, rather than just counting distinct supplier cities.

The Amenities line includes local building amenities and regional amenities
received across the owner's cities. Regional totals use distance from each
building's district to each recipient City Center, extra regional range and
entertainment, pillage state and powered bonuses. For the same building type,
each recipient takes the strongest in-range source. Equally strong sources
share attribution evenly in the ledger. This is a UI accounting convention;
the game supplies one benefit without assigning a unique source. Regional
attribution is cached per owner/building in the current lens snapshot.

Native evidence for this rule is the reference XP2 Windows GameCore
City::Growth::GetAmenitiesFromEntertainment, RVA 0x1239a0, SHA-256
324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c.
Its regional branch scans the receiving player's cities, checks each working
copy's building-plot distance plus district extra range, and retains the maximum
entertainment for each building type, including power and district bonuses.
The installed 12 November GameCore has SHA-256
092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f;
the native inspection used the reference binary. Lua regression tests cover
route bits, route weighting, regional overlap, range, extra entertainment,
power, pillage and snapshot caching. Live-save comparison remains outstanding.

Service medallion tooltips show current effects and supply-chain details
regardless of focus.

White chevrons use the native wave renderer and peak at 50% without focus.

Mapped Wonder links use the completed host plot and the producer stage. A
functional Wonder pin requires an active benefit and its co-located Service
building. The lens, map tooltip and City Details share the exact-plot Service
lookup. The tooltip and City Details also show persistent inactive Services. Goods
Providers come from the City Lights adjacency tags. They have a static lens
highlight and use the existing Goods art for placement adjacency. Lens
animations represent transactions.

The manual lens reads each Quarter on first open. GameCore publishes coalesce
into one UI refresh. Map changes and unclassified publishes invalidate the
map snapshots. Name, population and policy updates can refresh Service
medallions alone. A single active-modifier read is shared across Quarter
snapshots until the next publish.

The lens caches each Service's chain with its Quarter snapshot. A single shade
layer covers unrelated and unfocused Quarter tiles. The background assignment
key is cached with the Quarter snapshot. Native waves animate without
per-frame Lua polling. The pin UI reads the published Service snapshot and
reuses pooled controls.

Offline validation covers actual registry metadata, exact recipient gates,
MCUIS/pin icon and cumulative tooltip equality, right-click page targets, cold
context snapshots, pooling, layouts, both owners, Stage 2-4 focus and opacity,
current-effect changes and teardown. Native review requires a full ModBuddy
rebuild and reload to include the updated chevron art.

### Action wiring

Source actions are in `project/modbuddy/CivSupplyChains.actions.json`:

- `CSC_QuarterLenses`: imports `CSC_SupplyChainsLensPanel.lua`, order 501.
- `CSC_SupplyChainsLensPanel`: adds its XML to `InGame`, order 501.
- `CSC_LensColors`: gameplay palette SQL, order 501.
- `CSC_LensText`: localization SQL, order 501.
- `CSC_QuarterOverlaySupport`: imports shared support, Service presentation, pin/trial Lua and PlotInfo wrapper, order 490.
- `CSC_QuarterFlowTrial`: adds the passive comparison UI to InGame, order 502.
- `CSC_QuarterServicePins`: adds its WorldAnchor UI to InGame, order 503.
- `CSC_QuarterPlacementOverlay`: replaces only the PlotInfo context, order 505.

All lens actions are unconditional. The old `MoreLensesMod` criterion and
`ModLens_CSC_Quarters.lua` source/content/import have been removed. Regenerate
ModBuddy CDATA using `project/tools/modbuddy/civ6proj_actions.py patch` and verify
with `check`. Localization source remains `project/localization/CSC_Lens_Text.md`.

## Verification and review

Run `project/tools/lenses/test_quarter_lenses.py --dependencies <lupa-folder>
--game <game-root> --more-lenses <Workshop-folder>
--gameplay-database <read-only-DebugGameplay.sqlite>`.

The suite checks 256 SQL-backed plot classifications, resource discovery/pillage,
unique districts, optional resource tags, Wonder scope/completion/visibility,
unconditional build wiring and 48 palette rows against the runtime schema.
It runs the complete native PlotInfo with mocked APIs, both without More Lenses
and with its actual immediate/deferred callbacks. Standalone panel tests cover
one-row attachment, reattachment, Quarter/legend switching, yellow Wonder fills,
ready outlines, native heading reuse, eight-row key, native takeover, unrelated labels, Escape, mode/player exits,
missing UI/art, placement isolation and shutdown cleanup. Actual More Lenses
layer callbacks are also exercised against standalone activation/takeover.
Customer tests cover both registries, exact plots, direct unique replacements,
pillaged buildings/districts, adjacent ready plots, alpha-mask geometry, category
sprite styles, API-type correctness and native hollow legend textures in both views. Mock colours use actual packed RGBA so
actual fill buckets are exercised. Tests include unready 20% placement fills,
pillaged sites keeping edges while reverting to 20%, Quarter building/hidden-helper
states, source-anchored arrow records and hollow/filled legend states. These mocks
do not render native shaders or prove runtime widget placement.

The revised ArtDef and new texture package cooked successfully with Firaxis's
native cooker; the Windows BLP is 2,921,472 bytes. A review package built
with its native manifest task is at
`C:\Users\Shadow\Desktop\Codex\csc-chevron-lenses-20261030\package\Civ Supply Chains\`.
Other current worktree content was preserved. No installed mod, Workshop files,
settings or running game were changed. Build normally with art cooking and restart
Civ VI for review: inspect the menu/submenu position, legend, colours and cleanup,
then repeat with More Lenses enabled and verify only one Supply Chains entry.
The latest outline treatment, Quarter identity fills and header/legend revisions
have not yet been observed in Civ VI. The native cooker accepts the revised
SpriteOverlay layer types and the new hex-ring mask; build with art cooking so
older BorderOverlay types and the earlier texture package do not remain installed.

## Historical context

The original lens restoration re-used More Lenses' registry and Appeal colour
layer. Its startup nil-name error and later placement freeze led to the independent
placement overlay on 19 October. The 30 October change removes the remaining
manual-lens dependency. The earlier placement effect sampler (waves, badges,
pulses and cursor polling) remains retired. Dated investigation/review evidence
is retained in `memory/session_quarter_lenses.md` and Desktop/Codex review outputs.


## Radio-button shutdown crash fixed — 31 October 2026

Native dump/unwind evidence resolved the apparent Menu hang to
RadioButtonControl:SetCheck(false) and a HavokScript access violation. The panel
now mirrors the checked state, skips redundant entry writes and suppresses them
during shutdown. Source and installed panel are updated; no ArtDef/cook or
rendering/input policy change was part of the fix. Baseline lifecycle fixtures
fail, the corrected fixtures pass, and two unopened plus one active-lens zero-AI
native Menu/ExitOK regressions all exit0 with exact settings restoration.
See [diagnosis, evidence and acceptance](../research/mods/csc-ui-exit-crash-20261031.md).
This is the reproduced shutdown regression, not a blanket claim that every UI
unresponsiveness or input-stack concern has been eliminated.
