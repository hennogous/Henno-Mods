# CSC Quarter lenses and placement overlay

_Updated 20 October 2026. Placement uses its own native tile-fill overlay, excludes tiles owned by the focused city, and has no More Lenses event or layer dependency. Automated checks and native cooking pass; in-game visual review remains open._

Selecting a CSC Quarter for placement automatically highlights its existing
Quarters, discovered base/specialty materials and points of sale. Bakers' and
Tailors' are implemented. Standard district and Wonder placement retain native
behaviour. Automatic placement highlights work without More Lenses.

Automatic placement highlights only relevant tiles outside the focused city's
territory: unclaimed tiles and tiles belonging to other cities, including other
cities of the same player. Revealed/known-resource restrictions still apply.
The manual Supply Chains lens continues to include all relevant revealed tiles.

The manual **Supply Chains** lens remains optional integration with astog's
**More Lenses** (`35f33319-ad93-4d6b-bf27-406fac382d06`). Both features use one
shared data/colour implementation.

## Supply Chains chooser

More Lenses has a flat button list with `SortOrder` and an `OnToggle` hook for
secondary options panels; it does not provide a built-in nested category menu.
CSC registers one `ML_CSC_SUPPLY_CHAINS` entry, labelled **Supply Chains**. Its
options panel offers Bakers' Quarter and Tailors' Quarter, derived from the shared
material configuration. New implemented Quarters appear automatically.

The first choice is Bakers'; the panel retains the selected Quarter for the
current UI session. Switching choices clears the previous colours, redraws the
selected Quarter and updates the modal legend/title. The panel closes when
another lens is chosen or modal-lens mode ends. Selecting Supply Chains again
reopens it with the previous choice. District placement still chooses its Quarter
from the selected production item, independently of this manual choice.

Quarter radio buttons use the native lens menu's checked texture frame
(`Controls_RadioButtonLarge.dds`, offset `0,140`). The earlier `0,35` frame did
not visibly mark the selected choice despite the Lua checked state changing.

`ModLens_CSC_Quarters.lua` registers the parent button and initial legend.
`CSC_SupplyChainsLensPanel.lua/.xml` owns the selector and selected Quarter, using
More Lenses' public lens/panel events. The parent's `NonStandardFunction` asks the
panel to refresh when More Lenses redraws. The panel also paints when entering
modal-lens mode, because More Lenses may turn Appeal on before changing modes.
Refresh is limited to the active Supply Chains manual lens and never paints while
placing a district. `CSC_QuarterLensSupport.GetLensLegend` supplies four rows: the selected Quarter,
base materials, specialty materials and points of sale. Material labels explain
that outlines indicate improved resources. No More Lenses source files are replaced.

## Source and loading

The original three files under `Civ Supply Chains/Lua_UI/Lenses/` had survived locally and
matched the remote `hennogous/Henno-Mods` main branch. Their project content and
action registrations were missing. Those registrations are restored in the
ModBuddy project and source action JSON.

- `CSC_QuarterLenses`: `ImportFiles`, importing `ModLens_CSC_Quarters.lua` and
  `CSC_SupplyChainsLensPanel.lua`.
- `CSC_SupplyChainsLensPanel`: `AddUserInterfaces`, loading its XML in `InGame`.
- `CSC_LensColors`: `UpdateDatabase`, loading `CSC_Lens_Colors.sql` into gameplay `Colors`.
- `CSC_LensText`: `UpdateText`, loading `CSC_Lens_Text.sql`.
- `CSC_QuarterOverlaySupport`: imports `CSC_QuarterLensSupport.lua` and
  `PlotInfo_CSC_QuarterPlacement.lua`, at order 490.
- `CSC_QuarterPlacementOverlay`: replaces the `PlotInfo` context with
  `PlotInfo_CSC_QuarterPlacement.lua`, at order 505.

The manual button/panel/text actions use the `MoreLensesMod` / `ModInUse` criterion
at order 501. Colours also load at 501 but are unconditional because automatic
placement uses them. Support imports and the placement override are unconditional.
More Lenses is an optional integration, with no hard dependency. Its minimap and
modal legend panels each include `ModLens_*` scripts in their own context.
The CSC script registers whichever of `g_ModLenses` and `g_ModLensModalPanel`
is present, and returns immediately if neither is present.

## Shared data contract

`CSC_QuarterLensSupport.lua` discovers implemented Quarters from `CSC_QuarterMaterialAdjacencyConfig`,
checking that the corresponding district exists in `GameInfo.Districts`.
Duplicate material configuration rows create only one selector choice per Quarter.

Material membership comes from each configuration row's `SourceTag`, resolved
against `TypeTags` and actual `Resources` rows. `_BASE` and `_SPEC` tags choose the
two material categories. `SourceFilter` follows the adjacency processor's SQL
`LIKE` semantics for ASCII resource identifiers, including `%`, `_` and case
insensitivity. Optional-mod tags are included after their conditional SQL loads.

Points of sale use `CLASS_CSC_<QUARTER>_SALES` TypeTags directly. The bundled
`CSC_AdjacencyProcessor.sql` propagates these to direct unique district
replacements. The lens no longer infers relationships from adjacency ID text or
reads the old `District_Adjacencies` rows for this purpose.

The lens imports `CSC_AdjacencyCore` when needed and shares its `ResourceVisible`
check. Discovery is queried on every redraw. Only revealed plots are painted;
undiscovered resources are grey in the manual lens and uncoloured in placement.
An unpillaged improvement selects the slightly brighter material shade and a
tile outline; unimproved or pillaged resources use the subdued shade without
an outline. Pillage is not a separate legend category.
The lens is a planning overlay over revealed plots, not a computation of active
ownership-gated adjacency yields. Quarter and sale-district colours take priority
over resource colours.

Membership is cached per UI context after all database actions have loaded.
Plot improvements, pillage, discovery and visibility are read at redraw time.
There is no additional lens-specific gameplay configuration table.

A future implemented Quarter needs its own district colour, matched to atlas
index 0, and Quarter name/tooltip localization. Material/sales colours are shared
and need no Quarter-specific entries. Localization is authored in
`project/localization/CSC_Lens_Text.md`, then regenerated with `loc_md_to_sql.py`.
No Lua Quarter/resource/customer list needs to be extended.

## Native placement integration

The replacement includes Firaxis' original `PlotInfo` script before adding the
Quarter behaviour. It rebinds the existing placement-shadow add/clear and
interface-mode callbacks, which the native script registers during initialization.

`StrategicView_MapPlacement` emits the add callback after building native valid
and purchaseable tiles, adjacency art and preview data. When the current mode is
district placement and the selected district is a configured Quarter, CSC paints
relevant plots through the independent `CSC_QuarterPlacement` BorderOverlay.
It uses the native Map Search highlight API: `SetHighlightColor`, `SetPlotChannel`,
`ShowHighlights(true)` and `ShowBorders(false)`. One channel per nonempty colour
bucket preserves the shared Quarter/material/sales palette. The overlay is
registered, initially hidden, in `ArtDefs/CSC_QuarterResourceBorders.artdef`, which
is loaded by the Overlay art consumer. It uses the game's `MapSearchBorder`
material; no new textures or BLP assets are required.

Placement never toggles a native lens layer, activates Appeal, queries or changes
More Lenses' active selection, or registers its legend. The old
`CSC_Lenses.artdef` permission patch and its source registrations are removed.
More Lenses remains optional only for the manual Supply Chains lens.

The wrapper extends the native unshadowed plot list with the highlights and asks
native `RealizeShadowMask` to redraw, preserving other mask categories. It
copies/deduplicates the list without changing the caller's native placement data.
Before colouring or extending that mask, placement removes plots whose purchase
city matches both the focused city's owner and city ID, using native
`Cities.GetPlotPurchaseCity`. It rechecks ownership on every redraw so changing
cities or swapping tiles updates the highlights. Native valid/purchaseable tiles
remain in the original placement mask even when they belong to the focused city.
For a standard district, Wonder or missing cooked overlay, the callback passes
through to the original handler. Native plot-purchase redraws refresh Quarter
colours. Native placement validation, adjacency previews and queue handling
remain native.

Cancellation, confirmation, switching to another district or interface mode,
and context shutdown clear only CSC's own overlay and placement-mask entry.
Manual More Lenses colours and resource borders, yield icons and Empire details
are separate and are never cleared by placement cleanup. Missing overlay art
falls back to ordinary placement without extra highlighting.

### Retired Appeal-layer integration — 19 October 2026

Earlier versions reused `Hex_Coloring_Appeal_Level` and extended
`DistrictPlacement_PermissionMask`. That triggered More Lenses layer listeners,
including a nil-active-name crash reported on 15 October. A temporary active-name
workaround fixed the immediate-callback test but remained vulnerable to delayed
callbacks: queuing the real installed callbacks reproduced the 19 October
`WARN: Given lens has no entry` warning. Henno also reported yield/Empire overlay
unresponsiveness; that broader native failure was not reproduced or established
as the warning's consequence. Independent overlay ownership removes this shared
layer interaction. It still needs an in-game check of appearance and the reported
freeze; automated tests cannot prove the renderer or session behavior.

## Minimal palette and improved-resource outlines

Henno requested parity between the two views and removal of the effect sampler.
The prototype panel, badges, waves, pulsing, cursor polling and distance fade are
removed from source and ModBuddy actions/content. Placement now adds only the
shared tile fills to native placement previews. Improved-resource outlines belong
only to the manual More Lenses view.

| Category | Fill family | More Lenses improved-resource treatment |
|---|---|---|
| Base materials | Dark brown-orange, following Civilization VI's Production icon | Slightly brighter shade plus warm amber edge |
| Specialty materials | Brighter orange | Slightly brighter shade plus pale orange edge |
| Points of sale | Yellow, following the Gold icon | District tint only |
| Quarter district | Its own icon colour | District tint only |

Atlas index 0 is green for Bakers' (`CSC_BAKERS_256.dds`) and violet for Tailors'
(`CSC_TAILORS_256.dds`), as confirmed from the current source atlas previews and
`IconDefinitions`. Those are the two implemented/icon-registered Quarters. Their
material and sales shades are identical. The palette has nine RGBA rows: five
shared material/sales fills, two shared outline colours and two district colours.
Unimproved/pillaged resources are subdued; improvement state changes brightness
and opacity within the same colour family. The native Appeal colour API exposes
one tint per hex, so this is tonal variation, **not a within-hex gradient texture**.
No gradient texture or new BLP asset has been introduced.

`CSC_QuarterLensSupport.DrawImprovedBorders(owner, key)` classifies revealed plots
with the same helper used for fills. Only `BASE_IMPROVED` / `SPEC_IMPROVED` resources
receive outlines. Separate plot channels retain edges between neighbouring
improved resources. `SetBorderColors` uses the fill colour behind a lighter warm
front edge, using native `MapSearchBorder` art. Unrevealed, undiscovered,
unimproved, pillaged, Quarter and sale-district plots are excluded from this edge
list. Changes are read again whenever the manual lens is redrawn.

`ArtDefs/CSC_QuarterResourceBorders.artdef` registers two initially hidden
BorderOverlays: `CSC_QuarterLens_Improved` for manual resource edges and
`CSC_QuarterPlacement` for automatic placement fills. Placement never draws or
clears the manual overlay.
More Lenses clears its edges on lens changes, layer-off,
mode exit and shutdown. Closing its selector alone can retain edges while the
Supply Chains lens remains active. Missing cooked border art falls back to the
working colour fills.

The file is registered in the Overlay art consumer and ModBuddy Content. Both
surfaces use the same tile classifier; automatic placement remains independent of
More Lenses. Native placement validation, purchase markers, actual adjacency
yield previews and queue handling are preserved.

The earlier 11–12 October flow sampler and its reliability follow-up are retired
experiments. Their review packages remain historical outputs; they are not the
current main-mod implementation.

## Colour loading correction

Henno's in-game screenshots exposed missing map tints and initially white legend
swatches. The running `DebugGameplay.sqlite` contained More Lenses' grey colour but
zero `COLOR_CSC_LENS_*` rows. `Modding.log` showed the palette SQL being dispatched
as `UpdateColors`. That action targets a separate colour-manager database; it does
not supply the RGBA rows consumed by this integration's `UI.GetColorValue` calls.
The installed More Lenses loads its own `morelenses_colors.sql` through
`UpdateDatabase` into gameplay `Colors` (Type, Color, Red, Green, Blue, Alpha).

CSC's palette action now follows that working pattern. This fixes the shared
palette loading for manual lenses and Quarter placement. The earlier mock tests
loaded palette SQL directly and missed the database routing error. The regression
now requires `UpdateDatabase` and can execute the palette against the runtime
gameplay schema in an isolated fixture with `--gameplay-database <DebugGameplay.sqlite>`.
It verifies nine named, nontransparent RGBA colours without changing the
running database. A rebuild and full game restart are needed to load the corrected
action; switching lenses in the existing session is insufficient.

## Historical placement colour and cleanup correction

The following records the superseded Appeal implementation; current placement
uses the independent BorderOverlay described above.

Henno subsequently confirmed both features were visible, but placement painted
all categories bright green and left those hexes behind after selecting production.
`Hex_Coloring_Placement` uses native fixed-colour art rather than the palette used
by More Lenses. The earlier UI mock accepted colour calls on every layer and did
not model that restriction. Placement now uses Appeal's colour layer, and the
native permission mask is extended because it does not ordinarily permit Appeal
while placing a district. No new textures or overlay materials are needed.

The native cooker successfully resolved the Appeal layer reference against the
SDK's `Civ6/pantry` and produced the cooked permission ArtDef and dependency
registration. A **normal ModBuddy build with art cooking**, followed by a full
game restart, is needed for this change; copying the Lua file alone is insufficient.
The mode-change cleanup fixes the missing dismissal independently of the native
shadow-clear callback. The updated tests cover confirmation without that callback,
switching to Wonder placement, native layer notifications, manual lens takeover
and shutdown. Native in-game appearance remains a separate check.

## Verification

Run `project/tools/lenses/test_quarter_lenses.py --dependencies <lupa-folder>
--game <installed-game-root>`
with the same `lupa` dependency used by the adjacency tests. The regression reads
the real Bakers/Tailors SQL, shared schema, optional Sukritact material tags and
unique district propagation statement. SQLite supplies the independent material
membership/filter expectations; the Lua lens runs against native-style UI mocks.

Result: **254 plot classifications passed**, plus independent registry contexts,
hidden plots, resource discovery transitions, pillage, unique customer districts,
optional resources, localization/colour keys and conditional build wiring.
ModBuddy action round-trip and generated localization checks pass.

The placement regression executes the complete installed Firaxis `PlotInfo.lua`
with mocked UI APIs and the replacement callback wiring. It checks both Quarters,
standard districts/Wonders, absence of More Lenses registries/colours, native mask
preservation, unique sale districts, hidden resources, redraw/pillage, direct
switching, cancellation, missing city and invalid district parameters. It also
checks the independent overlay registration, rejects any placement access to
More Lenses events or shared lens colour calls, and verifies confirmation,
modal-lens takeover, missing-art fallback and shutdown. With `--more-lenses`, it
runs both immediate and deferred installed callbacks, verifies no active-name
changes or diagnostics, and exercises native yield/Empire event handlers after
placement cleanup. These pass; the mock does not render native shaders.
The Supply Chains chooser regression also checks one parent registry entry in
each framework context, dynamic choices, initial activation timing, palette/legend
switching, retention, panel dismissal, placement isolation and event cleanup.

An earlier **473-file** review package was built using Firaxis' native manifest
task, existing cooked art and the newly cooked lens permission/dependency at:
`C:\Users\Shadow\Desktop\Codex\csc-quarter-placement-20261010\package\Civ Supply Chains\`.
The generated `.modinfo` includes the correctly typed manual and placement actions
with their appropriate criteria. Other art was reused without recooking. The
installed mod and game/mod preferences were not changed. The review builder accepts
`--cooked-artdefs` and `--cooked-dependency` for this focused cook.

For visual review, build/install CSC normally and restart Civ VI. Select each Quarter
from production, inspect material/customer colours alongside the native placement
markers, buy a tile, confirm production, cancel placement and select a standard
district. Check that highlights disappear and that selecting a manual lens during
placement preserves the newly chosen lens. Repeat without
More Lenses: automatic placement should still work and the manual entry/panel should
be absent. With More Lenses enabled, open **Supply Chains**, inspect both Quarter
choices and their legends, switch back and forth, and reopen the panel to check
that it retains the selection. Tailors'
materials include Cotton, Sheep, Flax, Dyes, Silk and Silver; points of sale include
Harbors, Commercial Hubs, Holy Sites and Theater Squares, plus tagged unique
replacements. Native UI appearance remains unverified by the automated tests.

The minimal version additionally checks individual improved-resource edges,
shared material hues, distinct Quarter identity, pillage removing outlines,
manual layer-off, selector-only closure, fill-only placement,
missing art and retirement of prototype actions/content. The border ArtDef cooks
successfully with Firaxis' native tool. The current native manifest review package
is at `C:\Users\Shadow\Desktop\Codex\csc-lens-minimal-20261012\package\Civ Supply Chains\`.
This follow-up leaves the installed mod and game preferences untouched.

The subsequent fill-only placement / Wonder sales follow-up cooked the revised
single-overlay ArtDef and built a 487-file native review package at
`C:\Users\Shadow\Desktop\Codex\csc-lens-fill-only-20261012\package\Civ Supply Chains\`.
The installed mod remains unchanged.

For the revised visual review, build with art cooking and fully restart Civ VI.
Compare Bakers'/Tailors' icon-coloured district tiles, brown-orange base materials,
bright orange specialty materials and yellow sale districts in both views. Check
improved resources have individual edges in More Lenses, placement has fills only,
and pillaging returns resources to the
unimproved treatment. Confirm/cancel placement and switch lenses to check cleanup.

### Wonder points of sale

`CSC_QuarterWonderSales` in `Data/CSC_Q_ALL.sql` explicitly maps Quarter keys to
Wonder building types. Tailors' declares Bolshoi Theatre, Broadway and Sydney Opera
House in its Quarter SQL, matching the existing Stage 4 Wonder customer Services.
The shared classifier checks `GetWonderType()` and `IsWonderComplete()` on each
revealed plot, applying the same yellow `SALE` fill in both views. Looking only at
`GetDistrictType()` cannot distinguish these sites: they all use `DISTRICT_WONDER`.
The mapping grants no gameplay effects and does not infer customers from Wonder
placement prerequisites. Unknown, incomplete and unrevealed Wonders are excluded.
Additional Wonder sales sites can be declared in Quarter/compatibility SQL through
this table without changing Lua. Regression checks cover the declared sites,
Quarter scope, visibility and completion, plus native placement's colour/mask path.

## Independent placement validation — 19 October 2026

The full regression passes 254 classifications and all Wonder/manual-chooser/edge
checks, plus native PlotInfo placement with More Lenses absent and present
(immediate and deferred callbacks). Placement tests reject calls to the framework
selection/legend events and shared colour-layer API. They check masks, redraws,
all mode exits, missing art, native yield toggles and Empire event dispatch,
manual selection/overlay preservation, and shutdown. Empire control rendering
is stubbed; no native visual or full freeze reproduction is claimed.

Firaxis' native cooker successfully cooks both registered BorderOverlays against
the SDK `Civ6/pantry` and generates the dependency file without missing-reference
warnings. Review output: `C:\Users\Shadow\Desktop\Codex\csc-placement-independent-20261019`.
The normal ModBuddy build must cook art, followed by a full game restart; a Lua-only
copy does not register the new overlay or remove the old permission patch.
Installed mod, Workshop files and game preferences are unchanged by this edit.
