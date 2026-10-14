# Quarter lens restoration — 10 October 2026

Henno requested restored lenses, shared adjacency data, More Lenses-only
activation and Tailors' coverage. The files were present and matched remote main;
ModBuddy content/actions were missing. Restored them without changing other work.

Implementation and evidence: [Quarter lenses](../project/docs/integrations/csc-quarter-lenses.md).
252 plot classifications and action/localization checks pass. Native Firaxis
manifest built a 470-file review package under Desktop Codex. No installed mod,
game preferences, commits or remote writes changed. Native visual review pending.

Follow-up: Henno requested automatic material/customer highlighting during Quarter
production placement, with standard districts unchanged. Added one PlotInfo wrapper
and factored the classifier into CSC_QuarterLensSupport. Placement works without
More Lenses; manual lens imports/text remain gated, shared colours now unconditional.
Tests execute full native PlotInfo with UI mocks and pass standard/Wonder pass-through,
both Quarters, mask preservation, redraw, cancellation and no-framework scenarios.
Latest 470-file review package: Desktop Codex/csc-quarter-placement-20261010.

Live review caught missing tints/white legend. Gameplay cache has no CSC colours,
while More Lenses grey is present. Corrected palette action from UpdateColors to
UpdateDatabase, matching installed More Lenses' RGBA SQL pattern. The original
mock loaded SQL directly and masked this action-routing mistake. Tests now pin the
correct action and verify eleven colours against the actual gameplay schema.
Both manual and placement overlays use this fix. Rebuild/full restart required.

Further live review: both overlays now work, but placement was uniformly bright
green and persisted after production confirmation. Replaced fixed-colour
Hex_Coloring_Placement with More Lenses' Hex_Coloring_Appeal_Level. Native
DistrictPlacement does not permit Appeal by default, so added an additive
ArtDefs/CSC_Lenses.artdef permission and registered it with the Lenses art consumer
and project content. Native cooker succeeds against SDK Assets/Civ6/pantry.
Wrapper now cleans up on all exits from district-placement mode as well as native
clear events; LensLayerOff releases ownership, and modal Appeal takeover keeps
its newly painted contents. Paint runs after layer-on notifications and shadow
mask redraw runs after layer toggles to account for More Lenses handlers.
252 classifications and expanded native PlotInfo/lifecycle/permission tests pass.
471-file review package contains the cooked lens ArtDef and generated dependency;
other cooked art reused. Installed mod untouched. Normal ModBuddy art build and
full restart required; corrected placement appearance still awaiting live review.

11 October: Henno approved grouping the manual lenses under a parent named
"Supply Chains". Installed More Lenses supports a flat SortOrder and OnToggle
options panels, not built-in nested categories. Implemented one ML_CSC_SUPPLY_CHAINS
entry with a gated InGame options panel and dynamic Quarter radio choices. Shared
support now supplies legends. The panel owns the selected Quarter, remembers it
for the UI session, updates colours/legend on selection, and closes on another
lens/mode. NonStandardFunction bridges More Lenses refresh to the panel; entry into
VIEW_MODAL_LENS redraws after initial layer-on occurs before mode switching.
Refresh ignores district placement. All classification/placement/chooser tests and
localization/action checks pass. 473-file isolated review package updated; install
and in-game panel appearance remain unverified, require normal build/restart.

11 October, placement effect prototype: Henno clarified that the requested
prototype belongs in actual game code/main mod, not an inline HTML mockup.
Extended PlotInfo's existing override with Show/Clear/refresh events and added an
unconditional InGame CSC_QuarterPlacementPrototype context. Six default-on toggles:
soft colours, per-plot native borders, distance opacity fade, WorldAnchor badges,
nearby badge/border pulses and directional native flow waves. Shared classifier
now exposes GetPlotEntries; original 252 classifications and chooser/native
placement regressions still pass. Prototype regressions cover switches, wave
direction, scope/discovery, hover/pillage, both Quarters, standard districts,
manual takeover, confirmation/cancellation, missing art and cleanup. Prototype
localization has its own Markdown source/generated SQL/action. New initially
hidden Overlay instances reuse pantry border/pressure materials, registered in
the main art manifest and ModBuddy content; native cooks and 477-file manifest
build pass. Review package: Desktop/Codex/csc-placement-prototype-20261011.
No installed files or running game changed. Normal ModBuddy art build/full restart
is needed; panel/shaders/flow shapes remain unreviewed in-game. Distinguish distance
fade across hexes from a within-hex gradient texture; prototype plans opportunities
and does not promise actual gated yields. Details in the durable lens doc.

## Wave reliability follow-up — 12 October 2026

Henno saw some waves in-game but intermittently, with no clear sale-district
animation. Audited the current native StrategicView_MapPlacement and WorldInput
implementations. Original native shadow list excludes purchasable sites; added
the native purchase-target/CanHaveDistrict check. Preview now retains last valid
focus across UI/unrelated cursor plots; unrelated effect toggles do not reset
cached waves. Panel shows materials-in / sales-out counts, retaining outgoing
Quarter-to-sale direction and immediate-adjacency scope. Changed flow material
from religious waves to the current game FormCorpsArrow used with this API,
alpha to 1 and speed to 1; appearance still requires in-game verification.
Tests cover unique Tailors harbor and Bakers city center, purchase eligibility,
zero links, retained focus and unchanged wave reset/create counts. Full lens
regressions, runtime palette, localization/action checks and native cooker pass.
477-file native manifest review package: Desktop/Codex/csc-placement-flow-20261012.
Installed mod and game/preferences untouched during this follow-up; native rebuild
with art cooking and restart required for the changed material.

## Current direction: minimal parity — 12 October 2026

Henno retired the placement sampler in favour of parity with the manual lens.
Removed its Lua/XML/localization/ArtDef and all actions/content; no panel, badges,
waves, cursor polling, pulses or distance fade remain. Both surfaces now use a
shared brown-orange base / bright orange specialty / yellow sales palette, with
small improved/unimproved shade changes. Pillage uses unimproved fill/no edge.
Native fills cannot provide within-hex gradients; kept gentle tonal variation and
two-tone improved-resource edges instead, and explained this limitation.
Follow-up: Quarter district colour follows atlas slot 0. Inspected source DDS
previews: Bakers green, Tailors violet (the two current icon-registered Quarters).
Shared material/sales colours are identical across them; district identity is
separate. Legend reduced to four rows with outlines explained on material rows.
Shared Draw/ClearImprovedBorders uses independent manual/placement BorderOverlays,
one channel per improved plot and native MapSearchBorder art. Separate owners
preserve manual takeover. More Lenses edge cleanup handles layer-off, mode/lens
exit and shutdown; selector-only closure can retain an active lens's edges.
252 classifications plus native PlotInfo/chooser/outline lifecycle, pillage,
discovery, missing art, palette schema, localization/actions pass. Native new
border ArtDef cook and 488-file review manifest pass (other worktree content
preserved). Desktop/Codex/csc-lens-minimal-20261012 contains atlas previews and
review package. Installed mod unchanged by this turn. Rebuild with art cooking
and restart needed; revised palette/edges still need visual game review.

## Fill-only placement and Wonder sales — 12 October 2026

Henno corrected placement scope: keep material outlines only in More Lenses.
Removed all outline calls from PlotInfo override and removed its placement
BorderOverlay from CSC_QuarterResourceBorders.artdef. Shared helper guards reject
non-Lens owners, preserving manual-lens outlines during placement cleanup.
Added declarative CSC_QuarterWonderSales table and Tailors rows for the existing
Bolshoi Theatre, Broadway and Sydney Opera House Stage 4 customers. No broader
Wonder mapping existed in source/runtime DB; asked asynchronously for additional
intended mappings and proceeded with the three proven customers. Both views now
classify revealed completed Wonder plots by GetWonderType, use yellow SALE fill,
and exclude unmapped/incomplete Wonders. This is planning UI metadata, not new
gameplay adjacency or Service activation. Additional mappings belong in Quarter
or compatibility SQL. Regression also verifies mapping matches Service host list.
254 classifications, Wonder scope/completion/visibility, real native PlotInfo and
manual chooser yellow fills, fill-only placement, edge lifecycle and palette
schema passed. Native cook and 487-file review build in Desktop/Codex/
csc-lens-fill-only-20261012 passed; installed mod untouched. Normal ModBuddy build
with art cooking plus restart still needed for visual verification.
