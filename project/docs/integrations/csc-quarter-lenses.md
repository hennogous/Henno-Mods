# CSC Quarter lenses and placement overlay

_Updated 12 October 2026. Placement sampler retired at Henno's request. Minimal shared palette and improved-resource outlines pass automated checks and native cooking; visual review remains open._

Selecting a CSC Quarter for placement automatically highlights its existing
Quarters, discovered base/specialty materials and points of sale. Bakers' and
Tailors' are implemented. Standard district and Wonder placement retain native
behaviour. Automatic placement highlights work without More Lenses.

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
interface-mode callbacks, which the native script registers during initialization,
and listens for the colour layer turning off.

`StrategicView_MapPlacement` emits the add callback after building native valid
and purchaseable tiles, adjacency art and preview data. When the current mode is
district placement and the selected district is a configured Quarter, CSC paints
relevant plots using `Hex_Coloring_Appeal_Level`, the same colour-capable layer as
More Lenses. `ArtDefs/CSC_Lenses.artdef` adds that layer to the native
`DistrictPlacement_PermissionMask`; the Lenses consumer in the art specification
loads it. This is an additive permission, preserving native placement layers and
not activating Appeal for standard districts. The wrapper extends the
native unshadowed plot list with those highlights and asks native `RealizeShadowMask`
to redraw, preserving all other mask categories. It copies/deduplicates the list
and does not change the caller's native placement data.

For a standard district or a Wonder, the callback passes through to the original
handler. No extra colouring calls are made unless an existing CSC highlight layer
needs to be cleared. Native plot-purchase redraws also refresh the Quarter colours.
The native clear event removes CSC's highlights; an explicit mode-change handler
also clears them on confirmation/cancellation even if that event is absent.
Switching directly to a standard district also clears them. Native lens changes
release ownership as soon as the colour layer turns off. If a manual Appeal/More
Lenses lens has already taken over the layer, later mode cleanup preserves its
contents. The context shutdown clears owned highlights and unregisters the
replacement callbacks before invoking native shutdown.

Native and More Lenses listeners may fill Appeal when its layer turns on. The
wrapper clears/repaints after that notification, then redraws the native placement
mask. On cleanup it redraws the mask after turning the layer off, since More
Lenses clears the shadow mask in its off handler.

The placement overlay does not activate a More Lenses lens or use its grey colour.
Irrelevant plots keep their native appearance. Valid/purchaseable tile indicators,
adjacency previews, placement validation and queue operations remain native.

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

`ArtDefs/CSC_QuarterResourceBorders.artdef` registers one initially hidden
BorderOverlay: `CSC_QuarterLens_Improved`. Placement never draws or clears it.
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

## Placement colour and cleanup correction

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
checks additive art permissions, pins colour calls to the More Lenses layer,
models competing layer notifications and verifies confirmation, modal-lens
takeover and shutdown. These pass; the mock does not render native shaders.
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
