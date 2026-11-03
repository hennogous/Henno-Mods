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

## More Lenses nil active-name crash — 15 October 2026

Henno asked about current Lua.log. Eight repeated ModalLensPanel.lua:206
nil-name concatenation errors, each preceded by MinimapPanel's no-entry warning.
Confirmed CSC placement's Appeal layer-on triggers actual More Lenses callbacks
while m_CurrentModdedLensOn remains nil before any manual selection. Reproduced
the exact crash using read-only installed Workshop callback source in regression.
PlotInfo wrapper now temporarily supplies existing Supply Chains parent + Quarter
legend for synchronous layer-on if previous name is nil/NONE, then restores prior
name or NONE for initial nil. No mode/menu activation, new entry or dependency.
Existing selected lens preserved. No art change needed. Regression extended with
--more-lenses; native callbacks now pass with zero warnings/errors. Full existing
checks and palette schema pass. Source-only fix: installed mod/Workshop untouched.
Lua.log also has duplicate CSC MCUIS registration warnings on load; separate
existing issue, not investigated/fixed in this lens-focused turn.

## Overlay unresponsiveness investigation — 19 October 2026

Henno reports map yields, Empire and other overlays becoming unresponsive after
Quarter placement highlighting. Latest Lua.log contains four
`MinimapPanel: WARN: Given lens has no entry` warnings (lines 728, 730, 805, 806
at inspection), around placement activity. No corresponding lens/PlotInfo Lua
exception; the one runtime exception is the startup TunerMapPanel.lua:136 nil
access. Duplicate MCUIS registrations and official Clickout localization
duplicates are separate observations, not established causes.

Installed/source PlotInfo_CSC_QuarterPlacement.lua SHA256 both
`d25082b905544efef413117e45ec8cb14b29d9ba93b022a3adf1d668bf67b3a9`.
The 15 October workaround temporarily supplies the CSC More Lenses identity
only during ToggleLayerOn, then immediately restores NONE/previous selection.
Current native PlotInfo + installed More Lenses regression passes, including
254 classifications, but assumes immediate layer callbacks. An in-memory test
variant queuing the real installed More Lenses OnLensLayerOn handlers until
after placement returns reproduces the exact logged warning and fails the
existing zero-diagnostics assertion. This proves the workaround is vulnerable
to deferred callbacks; it does NOT prove native events were deferred in Henno's
session or reproduce the full yield/Empire freeze. Treat shared Appeal-layer
ownership/timing as a suspect, not a confirmed root cause. Do not call it fixed.

Native StrategicView_MapPlacement sets DistrictPlacement active before emitting
the placement shadow-add event. PlotInfo's yield toggle independently calls
ToggleLayerOn/Off for Yield_Icons; the warning itself is a print, not an exception
that directly aborts those handlers. Need affected-session state or a controlled
native comparison to establish the broader failure mechanism.

Debug port 4318 refused; host listener is 4319, but LSQ returned an empty payload,
so no stuck-state inspection was possible. No game state/preferences, installed
scripts or production code changed during this investigation. Optional user
clarification pending: do buttons change their checked state while the map stays
unchanged, or do the controls themselves stop reacting?

## Independent placement overlay — 19 October 2026

Henno explicitly requested that district placement not depend on More Lenses.
Replaced the shared Appeal-layer integration with CSC's own initially hidden
`CSC_QuarterPlacement` BorderOverlay, registered alongside manual resource edges
in `CSC_QuarterResourceBorders.artdef`. Uses native MapSearch highlight colours
and plot channels, with borders disabled. No lens toggles, active-lens events,
legend registration or framework state changes. Deleted `CSC_Lenses.artdef`
and removed its source project/art-manifest registrations. Optional manual Supply
Chains lens remains on More Lenses. Shared classification/palette unchanged.

Native PlotInfo regression now runs without More Lenses and with immediate and
deferred real installed callbacks, rejects framework/shared-colour calls, checks
all exits/missing art/manual-overlay preservation and exercises native yield
toggle/Empire dispatch (Empire control rendering stubbed). All tests pass plus
254 classifications and nine colours on runtime gameplay schema. Action wiring
check passes. Native cooker with SDK `Civ6/pantry` cooks both overlay entries
and regenerates dependency without missing-reference warnings; dependency no
longer includes CSC_Lenses. Separate 496-file native-manifest review package:
`C:\Users\Shadow\Desktop\Codex\csc-placement-independent-20261019`.

No installed mod, Workshop files, game state/preferences or unrelated source
changed. Requires normal ModBuddy art cook and full game restart. Native visual
appearance and whether this resolves the reported yield/Empire freeze remain
unverified. Current durable description: `project/docs/integrations/csc-quarter-lenses.md`.

## Quarter selector checked appearance — 19 October 2026

Henno reports Quarter choices not visibly showing the active selection. Existing
SelectQuarter already sets exactly one checked button and retains it on reopen;
the XML used `CheckTextureOffset="0,35"` on Controls_RadioButtonLarge.dds. Changed
to `0,140`, matching the native MinimapPanel lens buttons (and its 35x35 checked
sprite). No selection/activation behavior changed. Existing chooser/native
placement regressions pass; native button appearance still needs a rebuild/reload
and visual confirmation. Source-only UI change; no installed or Workshop edits.

## Placement outside focused city only — 20 October 2026

Henno requested excluding the currently focused city's tiles from automatic
placement highlights. Wrapper filters shared colour buckets using native
Cities.GetPlotPurchaseCity and the focused city's owner+ID before colouring or
extending the shadow mask. Unclaimed and other-city tiles (same or other player)
remain eligible. Native valid/purchase tile mask stays intact; manual lens and
shared classifier unchanged. Ownership/focus is read afresh on each redraw.

Full regression passes with More Lenses absent and immediate/deferred callbacks.
New cases cover both Quarters, all highlight categories, same-player different
cities, cross-player city-ID collisions, unclaimed plots, focus/tile changes,
all-filtered cleanup, manual-lens coverage and native-mask preservation. No new
art cook needed for this filter; rebuild/reload Lua, visual review still pending.
Installed mod, game state/preferences and Workshop files unchanged.

## Standalone manual lenses — 30 October 2026

Henno explicitly removed the need to retain More Lenses integration, while
requiring compatibility if it replaces the same UI. Implemented additive UI
instead of replacing MinimapPanel/ModalLensPanel: one reparented Supply Chains
RadioButton in /InGame/MinimapPanel/LensToggleStack; selector child beside its
actual LensPanel; CSC-owned header/key in HUD. Shared Quarter discovery/colours,
manual improved-resource borders and yellow Wonder sales retained. Removed
ModLens_CSC_Quarters.lua, project/import reference and MoreLensesMod criterion;
manual imports/panel/text unconditional. No Workshop/installed edits.
CSC_QuarterLens is a new native BorderOverlay fill owner at priority15.4; existing
manual edges15.5 and placement overlay remain separate. Own neutral grey is new
COLOR_CSC_LENS_IGNORE, replacing external palette dependency (ten colours total).
Opening returns native lens Default and exits old modal mode normally, then
enters VIEW_MODAL_LENS with CSC overlays. It never turns Appeal on or uses More
Lenses registries/events. Native/More lens layer takeover clears only CSC; label
layers while Default active do not. Escape/button/mode/player changes and context
shutdown clear/reparentcleanup. Main menu grows only by inserted rowheight max40,
then restores original height if unchanged; no ever-growing reload menu.
Standalone public OpenPanel optional Quarter key supports later hotkeys; Q+number
was discussed but not implemented in this UI-independence pass.
254 classifications + actual native PlotInfo and More immediate/deferred callbacks,
new standalone-panel harness with/without actual More callbacks, palette schema,
actions pass. Native ArtDef cook and 603-file review manifest in Desktop/Codex/
csc-standalone-lenses-20261030 pass, current dirty worktree content preserved.
No game/FireTuner/settings/install/autoplay touched. Normal art build + restart
needed; menu/submenu positioning and rendered overlay appearance remain unverified.
Durable guide rewritten to current architecture: project/docs/integrations/
csc-quarter-lenses.md. No need to preserve the old registration in future work.

## Blue/red/yellow + ready chevrons requested; preview first — 30 October 2026

Henno wants Base blue, Specialty red, Sales yellow; improved resources use a
chevron variant, as do sales districts with the correct customer building and
mapped completed Wonders directly. Same styling for manual and placement views.
Do not retain old outlines as an additional requirement: chevrons supersede that
requested improved-state treatment unless Henno chooses otherwise. Placement's
focused-city exclusion is current behaviour; changing shared styling does not
by itself authorize changing that filter.
Customer mappings: reuse CSC_Stage3CustomerTransactions (Bakers Market; Tailors
Market/Temple). Stage2/4 still have explicit Quarter/gameplay relationships:
Tailors Lighthouse and Amphitheater; Bakers city-center Stage2 customer + Zoo,
Ferris Wheel; Garden compatibility separately. UI-only supplemental venue table
is the smallest safe next step, with tests against gameplay declarations. Do not
refactor active economic scripts just for highlighting without a concrete need.
Qualifying venue must be functioning on the actual district plot; unique building
and district replacements need direct one-level expansion. Existing Wonder table
remains valid; wonder matching is by GetWonderType, not generic district type.
NO blue/red/chevron or new building-mapping source changes implemented yet.
Henno steered to rendered comparison before proceeding. Created inline style
comparison quarter-highlight-comparison.html in this thread's visualization root:
plain + chevrons + double edge + diagonal hatch + ready badge, three categories,
with opacity/spacing/symbol Tweak options. It is a schematic style preview, NOT a
Civ engine capture. Browser QA:15tiles/15icons, zero JS errors or horizontal
overflow at1040/360; desktop/mobile screenshots alongside. Native chevrons/hatching
render path still unproven. EXE read-only strings confirm BorderOverlay InitializeStyles,
SetBorderStyle/SetPlotColor; Firaxis CivRoyale/Pirates source uses InitializeStyles
with border material hashes. This is NOT proof that arbitrary fill patterns work.
No game/FireTuner/automation/installed changes. Continue art/API investigation and
implement the shared classifier/styler after this preview review.

## Rendering options source audit — 30 October 2026

Henno challenged the preview's unverified options and requested actual code only.
Completed source audit in project/docs/integrations/csc-overlay-rendering-options.md.
Confirmed paths: native BorderOverlay fill/alpha and two-colour borders; native
SpriteOverlay with Texture StaticTexture/OverlayTexture, HEX_GEO, TintColor and
NumTiles (base Placement_ValidFill_Sprite / PlacementValidOverlay), and real
CreateSprites(plots,styleName,channel) in Firaxis Pirates/CivRoyale. Thus authored
chevron/hatch textures are a supported rendering route, NOT a BorderOverlay
chevron switch. NativeWorldAnchor32x32 Image + UI.GridToWorld + SetWorldPositionVal
in DistrictPlotIconManager proves small plot-anchored markers, including an
ordinary authored ready-image. Exact mockup corner position/scale not runtime
verified. NativeHexPlace512DDS inspected: actual gradient-edge and solid variants,
no builtin chevron/hatch asset asserted. Native EXE strings supplement only; Ghidra
currently GameCore XP2 notgraphicsEXE, didnot switch/analysewrongtarget. No livegame,
Frida/FireTuner, settings, installation or gameplay edits. Original new styling
and customer-building mapping implementation still pending; audit does not mean
new CSC art has been built or tested in-game. Report lists source locations and
what each establishes; keep future previews qualified accordingly.

## Shared blue/red/yellow styling implemented — 30 October 2026

Henno then chose an icon/sprite for improved Base materials. Implemented in main
mod source: Base blue fill + a compact blue circle/white check sprite when improved
and unpillaged; Specialty red fill + red chevrons when improved and unpillaged;
Sales yellow fill + yellow chevrons when a matching customer building functions
on the actual plot, or a mapped completed Wonder directly. Same shared renderer
for manual lenses and placement; old improved-resource borders removed. Pillaged
materials return to unimproved styling. Quarter own green/violet remains.
Placement's focused-city exclusion was preserved.

Stage 3 customer readiness reads CSC_Stage3CustomerTransactions; supplemental
UI-only CSC_QuarterCustomerBuildings schema in CSC_Q_ALL, data in Bakers/Tailors
and conditional Garden patch covers Granary/Zoo/Ferris Wheel, Lighthouse/
Amphitheater, Conservatory. Market/Temple are not duplicated. Direct one-level
building/district replacements supported; no economic effects changed.
Important: UI does NOT expose GetBuildingLocation. Use the native UI
GetBuildingsAtLocation(plotIndex), as CitySupport/PlotToolTip and existing CSC
Wonder UI do. Harness throws if gameplay-only GetBuildingLocation is invoked.

Native SpriteOverlay owners CSC_QuarterLens_Ready and CSC_QuarterPlacement_Ready
use ready styles BASE/SPEC/SALE on channels0/1/2. BASE uses RECT_GEO14x14, white
tint and authored128px blue badge. Other styles use HEX_GEO and authored512px
white alpha chevron mask with red/yellow tints. Shared S.DrawOverlay/ClearOverlay
manage both native fill/sprite objects independently. Missing sprite keeps fills;
missing fill art preserves native placement. No native/More overlay data touched.

Deterministic project/tools/lenses/build_chevron_art.py generates DDS/TEX/XLP and
ArtDef entries, --check verifies palette-linked output. Art.xml adds package
Overlay/CSC_LensPatterns under OverlayTexture; civ6proj adds real sources.
Initial one-level Pillow DDS cooked exit0 but reported zero-sized big-data block;
fixed with Firaxis RGBA header and full mip chains (DDS count10/8; TEX last-index9/7).
Native XLP cook now clean, real BLP1,522,688bytes, ArtDef/dependency cook passes.
Source badge visually inspected. Native manifest build609files includes cooked
Windows BLP and dep at Desktop/Codex/csc-chevron-lenses-20261030/package/Civ Supply Chains.
build_test_package.py gained optional --cooked-blps for focused Windows art input.

Final checks pass:256SQL-backed classifications; actual native PlotInfo with no
More/immediate/deferred More callbacks; standalone panel with/without real More
callbacks; exact-plot/pillage/unique/customer checks; shared sprite channels and
cleanup; eight runtime Colors rows; deterministic art/localization/action checks;
scoped diff whitespace check. Durable integration guide updated. No installation,
settings, game, FireTuner, Frida or automation changed. Normal ModBuddy art build
and restart required to review in-game layout/size/occlusion/zoom/rendering; native
cook + mocked Lua are not visual runtime proof. Q+number hotkeys still not added.

## Q+1 / Q+2 implemented — 30 October 2026

Henno explicitly requested implementation after confirming they were absent.
CSC_SupplyChainsLensPanel's existing input handler now tracks hold-Q then top-row
1/2, fixed to BAKERS/TAILORS regardless of menu sort. Calls the same local Open
controller as the existing public event; no global handler/UI replacement,
native/More code edits, new dependency or rebindable action registration.
Uses Keys.Q and tonumber(Keys["1"]/["2"]), InputSupport.World input context,
native input key/modifier messages and SetAppLostFocusHandler. Both key edges and
repeat consumed for recognized chords, including Q-first release. A number held
before Q does not become a shortcut through repeat. Hold Q across presses to
switch Quarters. Ctrl/Alt/Shift pass through. No auto-closing by same shortcut.

Q normally toggles resources; handler captures Q to avoid that during chords.
A Q-only tap reproduces native WorldInput's ShowMapResources toggle/refresh/sound
on release, only if ToggleResources enabled and Q remains one of its display
bindings. Thus Q is the reserved prefix; no generic replay of arbitrary custom
Q-only rebindings. Bare 1/2 pass through. Disabled while recording gestures,
WorldBuilder, non-World contexts, no local player, placement/building/other modes,
or visible focused text. Recursive visible control scan uses native GetChildren /
IsVisible / optional HasFocus, only on candidate keystrokes; accommodates modded
unnamed/reparented text fields rather than hardcoding chat paths. Mode/player/app
focus cancellation preserves captured releases; fresh presses clear stale captures
if OS dropped a release while unfocused. Shutdown resets all state.

Expanded standalone harness exercises both no-More and actual More callbacks,
plain Q/binding removal/action disabled, number pass-through, both release orders,
held/repeated numbers, same-Q switching, all modifier/context/focus/editor/observer
guards and interrupted/recovered keys. Full256classification/placement suite passes.
Tooltips now teach shortcuts; generated localization, whitespace checks pass.
609-file native manifest review package refreshed with new Lua/text, existing
cooked sprites unchanged. Installed mod/settings/game untouched. In-game input
dispatch ordering and mod interaction still require review after normal build/
restart; mocks establish handler state/consumption, not engine dispatch timing.

## Human QA failure; routing correction and debug logs — 30 October 2026

Henno reported submenu visible but Quarter choices do not launch; Q+1 toggles
resource icons then Religion. Installed panel hash matched current source;
Lua.log contained the AddUI load entry and no script errors. No Civ process was
running during the corrective pass. Prior direct-handler mocks were inadequate
to establish routing before native actions; do not cite that earlier green check
as runtime success. Henno also explicitly requested debug logging.

Submenu callbacks now call Open(key), not SelectQuarter's active-only repaint.
Open publishes active ownership after synchronous UI mode cleanup completes.
Added DEBUG=true / CSC Lenses: log lines: load/Quarter count, parent and Quarter
clicks, activation requests/result, plot count/fill availability, close reason,
input key/message/Q-held/context/mode/eligibility reason, recognized shortcut,
World mask and restored context. No per-frame logging.

Native SDK LUA Input docs say context true is confined to its root; extended=true
only selects InputStruct signature. Read-only Capstone/PE inspection of current
DX11 EXE (SHA E7450823CC8E00468CFF7B9D7B97C63140EAE38AE1D774BA4EFA437556C42D63)
finds SetGlobalInputHandler native registration/wrapper and single-InputStruct
observer. Delegate0x14088b940 discards Lua return and alwaysreturnsfalse. Global
loop0x140892870 precedes ordinary context traversal. Main Ghidra remained XP2
GameCore and was not confused with graphics/UI executable. Native InputConfig
marks Q/1/2 actions as World; XP2 InGame demonstrates PushActiveContext/PopContext.

Revised route: UIManager:SetGlobalInputHandler observes Q/digits independently
of reparented UI controls. For a handled event push private0x20000000 input mask
so World native gestures do not match; release via queued refresh, SystemUpdateUI
or beginning of next input. Only pop our own top mask, preserving nested popup
contexts until it resurfaces. Never change saved gestures/settings. Global return
is not relied upon. Escape remains local so focused text/popups can consume it.
More Lenses and current installed Workshop Lua use no global slot, but another
mod claiming it will need coordination; no getter/chaining API assumed. Source
method and shared-slot limitation documented in csc-quarter-lenses.md.

Updated harness ignores global callback return, dispatches fake native actions
before local input, and verifies context-based exclusion instead. Added inactive
submenu selection, synchronous layer cleanup, deferred input batching, missing
context refresh/SystemUpdate restoration, nested popup context ownership, debug
evidence and shutdown cleanup. Full256classifications/nativePlotInfo/More callback
suite passes; action/whitespace checks pass.609file native review package refreshed.
No game launch, FireTuner, settings or installed-file edits. This is a source fix
backed by inspection and improved offline coverage, still awaiting native QA after
rebuild/restart. Do not claim Q+1/2 fixed in-game until that rerun demonstrates it.

## Native log identifies queued mode-close bug — 30 October 2026

Henno rebuilt and retested both menu and Q+1/Q+2: still no visible lenses. Read
fresh Lua.log (explicit real host path; sandbox LOCALAPPDATA redirects elsewhere).
Load/Quarter count2 present, global keycodes Q17/1=28/2=29 and messages down0/up1
confirm actual engine enums differ from simple fixture numbers (production uses
Keys/KeyEvents correctly). Both shortcuts recognized correct Quarter. Parent and
Quarter clicks reach Open and draw32revealedplots with fillAvailable=true.
Immediately after each activation: close reason=mode -1615000917 (Selection),
but UI.GetInterfaceMode() printed4552534 (VIEW_MODAL_LENS). Thus this is not a
working on-screen lens despite successful activation callbacks; tell user that
distinction clearly. No CSC Lua exception; unrelated early TunerMapPanel error.

Root cause evidenced by log: queued intermediate Selection event from Open's
modal -> Selection -> modal transition arrives after the new modal activation.
OnModeChanged blindly closes on event argument even though actual mode is newer.
Patched to compare event target with UI.GetInterfaceMode and ignore mismatches,
logging ignored stale mode notification. Current actual exits still close.
Expanded fixture queues mode notifications independently of state updates: menu
and chord survive delayed Selection/modal events; genuine exit closes and stale
modal notification cannot repaint/reopen. Both no-More/actualMore callback tests
and full256classification/placement suite pass. Documentation updated; review
package refreshed. No live changes or install; latest fix still awaits native QA.

## Headings work; blank overlays, uppercase and persistent submenu — 30 October 2026

Henno rebuilt again: headings/manual UI now launch from Q+1/2 and submenu, but
all map overlays still blank. Wants large heading ALL CAPS and submenu to remain
open when switching Quarters. Log confirms latest stale-selection notifications
are ignored, active session survives, GetOverlay/draw33plots available. Subsequent
native layer takeover logs correspond to changing native lens choices; no new
CSC exceptions. ArtDef log shows CSC overlay BLP loaded, no CSC-specific error.
Never equate fillAvailable=true with rendered pixels.

Shared fill path now calls InitializeStyles(numberOfColourBuckets+1, MapSearchBorder
hash), reserves0 and assigns colours on positive channels as XP2 PowerCityPlots
does. Previously it set channel colours without explicitly allocating style slots.
Read-only current DX11 EXE: Lua InitializeStyles wrapper0x14021e960 resolves to
native0x14021e740, which resizes .178 style vector by count then fills each0x5c
style record. Native scenario source demonstrates InitializeStyles(count,hash).
This is a supported allocation correction, NOT confirmed cause/runtime resolution
of the blank map. Same renderer serves placement, preserving existing tile filter.
Logs now report style/channel/sprite counts, base/spec/sales/ignored categories
and packed-colour=plot-count buckets for actual runtime diagnosis.

Large title uses native ModalLensPanel's Locale.ToUpper(Locale.Lookup()) + SetText.
Active CSC Quarter switching updates in place, avoiding needless modal->Selection
->modal cleanup and keeping submenu open. Initial/native takeover still cleans up
normally. One-shot SystemUpdateUI finalization re-shows menu and repaints after
queued cleanup; cancels on Close/shutdown and checks actual current lens/mode.
No permanent repaint loop. Mock event dispatch snapshots callback list so removing
a one-shot callback doesn't incorrectly skip a different registered callback.

Tests validate allocated positive colour slots, real mixed-case localization
converted to ALL CAPS, no mode roundtrip on active switches, native deferred exit
hiding the chooser followed by queued restoration, no stale reopen after exit,
old deferred notification guards, input masks, both owners and More callbacks.
Full256classification suite passes; scoped diff/action/art source checks pass.
Review package refreshed. Game was closed during inspection; no runtime mutation,
installation or settings edits. Next build/restart native review is still needed
for actual fill/sprite visibility; do not claim overlay fixed from mocks.

## Follow More Lenses' actual native fill path — 30 October 2026

Latest Lua.log adds a second native load/session: draws29plots, base1/ignored28,
sprites0, styles3/channels2, packed blue1540453667 and grey2134851391. Colours
are valid/nontransparent; UI remains active, but Henno still sees no fill. No
activation-settled receipt from the SystemUpdateUI one-shot. Do not claim style
allocation fixed native rendering. Henno explicitly pointed back to working More
Lenses implementation. Game closed during current read/source pass.

Compared actual More minimappanel SetModLensHexes/ToggleModLens: it uses native
Hex_Coloring_Appeal_Level + SetLayerHexesColoredArea, NOT BorderOverlay, and
SetActive(Appeal) + enters modal only if needed, with NO Selection round trip.
Critical native WorldInput.OnInterfaceModeChange_Selection calls SetActive(Default)
itself: ignoring the stale event only in CSC could not prevent that graphics reset.

Manual S.DrawOverlay now uses that native coloured-hex carrier; manual custom
BorderOverlay hidden/retained in art source (underlying blank cause unproven).
Placement still uses its independent BorderOverlay and never borrows a shared
colour layer. Ready Base sprite/red Specialty/yellow Sales chevrons remain private.
Shared classification/palette/customer data unchanged. Missing private art no
longer prevents manual native fills. Native fill ownership tracked explicitly;
normal close clears owned fill, takeover relinquishes without clearing new data.

Controller now directly SetActive(Appeal), SetModeModal only if not already there.
Retains one standalone menu/submenu/heading/key + Q shortcuts; no More dependency,
registry/menu registration or native UI file replacement. Optional More events
ML_CloseLensPanels + SetActiveModLens(VANILLA_APPEAL) coordinate native carrier and
avoid stale mod painters/missing-entry diagnostics. Listen ModdedLensOn, native
lens action IDs, carrier off, deferred own-entry unchecked to yield safely. Entry
check defers so own click-off callback still closes normally. Native/More repaint
layer events queue a context update rather than immediately overwriting new owner.
Pending finalization now ContextPtr:SetUpdate/ClearUpdate, with extra context
refresh repaint; no reliance on SystemUpdateUI alone for activation. Close/shutdown
cancel updates, shutdown clears native fill owned by CSC and restores modal UI.

Tests model native Selection resetting Default and ensure activation avoids the
roundtrip; native palette has exclusive plot assignment; actual More callbacks
tested immediate + delayed vanilla painter followed by context-update CSC repaint.
Tests cover native Appeal hotkey/new owner preservation, More Builder takeover,
own radio click-off, native fills with no private art, uppercase/menu, input masks,
both ready-sprite owners and independent placement. Full256classification suite,
action/art generation and whitespace checks pass.609file review package refreshed.
No installed mod/Workshop/settings edits, game launch or runtime mutation. Latest
manual native rendering still needs visual QA; report source changes/evidence and
this remaining uncertainty clearly rather than calling it proven in-game.

## Muted fills, ready outlines and native header — 30 October 2026

Henno confirms the native Appeal manual fills now render correctly. Latest
requests replace bright/prototype styling with muted blue Base, red Specialty
and yellow Sales, outlines on improved/functioning plots, plain legend labels
and separate readiness entries, shared white Quarter overlays, and a seamless
native heading (thin brown seam above the previous copied header).

Both renderer owners now use pending fill alpha .14, ready fill .24, outline
alpha .95 with dark backing; Quarter white alpha .28. Ready layers changed from
SpriteOverlay to BorderOverlay/MapSearchBorder, three category channels with
highlights disabled and borders enabled. No runtime sprites/chevrons remain;
their old packaged source assets are retained dormant. Contiguous ready plots
in the same channel share a perimeter. Placement's existing outside-focused-city
territory filter remains unchanged. Pillaged resources/buildings lose outlines;
mapped completed Wonders qualify directly for yellow ready fill/outline.

Seven-row scrollable legend: Quarter, pending/ready Base, pending/ready Specialty,
pending/ready Sales. Ready swatches use an outer ring, dark inset and muted fill;
all legend labels omit text icons. Narrow localizer exemption permits icon-free
LOC_TOOLTIP_CSC_LENS_* labels and rejects icons there; ordinary tooltip prose
retains its relationship-icon checks. Lens localization generation/check passes.
Whole-repo localization check reports unrelated pre-existing stale Bakers/M&C/
LGD outputs; those were left untouched.

Controller now reuses live ModalLensPanel/LensText and hides native KeyPanel;
CSC's key is parented into that native panel. The earlier HUD header copy drew
before TopPanel and exposed its edge. Fallback header is native-styled and used
only without native title controls. Deferred native/More paints restore CSC's
heading/key; close/takeover restores carrier header without clobbering a new lens.

Full256classification suite passed with noMore and actualMore callbacks, native
PlotInfo placement, customer readiness, both ready-border owners, seven-row key,
live native header and palette12. Native revised ArtDef cook passed; generator
reproducibility, scoped whitespace, lens localization and action checks pass.
Latest styling/header is not yet visually observed in-game. No installed mod,
Workshop content, settings or running game changed. Normal art build/restart is
required so old Ready SpriteOverlay definitions are replaced by BorderOverlay.

## User review: missing outlines and dark/verbose key — 30 October 2026

User screenshot shows the seven-row key but swatches too dark and labels verbose;
map outlines still invisible. Latest real Lua.log reports outlined=1/2 without
errors, proving assignment only. Installed dep/ArtDef include the current layers.
No running CivilizationVI process was found; no native visual test was attempted.

Revised border setup now owns a full CSC_QuarterReadyBorder SplineBorder copied
from native MapSearch: AOEBorder texture, width4/segment16, visible/revealed FOW
alpha1. Previously CSC only named the external style and defined dormant sprite
styles; exact cause of native invisibility is not established. Layer Material
and InitializeStyles reference our private material. SetVisible precedes style
initialization. Reserve style0 and assign one positive channel per ready plot,
preserving shared edges between adjacent improved hexes. Diagnostics add layer
availability/material/style count; draw summary now changes with readiness/palette.

Both map surfaces now use alpha.12 for blue/red/yellow in either readiness state,
with lighter saturated outlines at alpha1. White Quarter/grey ignore unchanged.
Four opaque legend-only palette entries separate UI readability from map alpha.
Removed dark legend inset; opaque24x27 inner fill matches32x36 outer aspect ratio.
Labels: Unimproved/Improved Base Materials, Unimproved/Improved Specialty Materials,
Customer District, Customer Building / Wonder. Quarter label unchanged. Generated
lens SQL verified equal to Markdown generator output (sandbox text write Errno22
worked around by exact generated-content patch, then --check).

Full256classification suite passes with native PlotInfo, noMore/actualMore hooks,
customer/Wonder states, standalone lifecycle, private spline fields, separate
adjacent ready channels and palette16. Test mock now packs actual RGBA instead of
assigning unique IDs to equal colours, exercising merged readiness fill buckets.
Art generator, localization/action checks pass; native ArtDef cooker exit0 and
private border definition exported. Ghidra held GameCore (wrong module for graphics)
so was not used to infer rendering. Read-only EXE binding inspection confirmed
InitializeStyles material lookup/default path, not actual native visibility.
Latest visual outcome still needs rebuild/art cook and in-game review. No installed
mod/Workshop/settings/game changes.

## Second outline review: native hollow swatches and edge sprites — 30 October 2026

Latest user screenshot still has no map outlines and ready swatches visibly
look like overlapping offset hexes. Latest Lua.log confirms own private spline
material is used, layerAvailable=true, outlined1/styles2, no exception. No running
game found. The previous private material change did not solve native visibility.

Inspected shipped ModalLensPanel.AddKeyEntry: it explicitly uses native
Controls_KeySwatchHexEmpty for hollow swatches. CSC now does exactly that; no
nested LegendTint or fillColor metadata. Plain labels and opaque colours retained.
Previously resizing image boxes without changing native image stretch drew
offset native-sized inner textures; do not keep guessing inset dimensions.

Ready outlines now use independent SpriteOverlay owners, empty Material and
priority0 matching native PlacementValidOverlay. Three Texture/HEX_GEO styles,
RectDims20/20, tint from blue/red/yellow OUTLINE colours, all reference a new
CSC_Lens_HexOutline white ring texture.512x512 full mip chain, native placement
UV footprint, transparent centre, no gradient/check/chevrons. Each qualifying plot
gets a sprite and therefore its own edge, including adjacent improved tiles.
ClearAll clears only this owner's sprites; manual/native fills and placement
territory filter remain unchanged. Retired private spline definition removed.
Older prototype DDS files remain dormant; ready styles now use the new mask.
New DDS/TEX registered as project Content and in existing OverlayTexture XLP.

Full256classification suite passes, noMore/actualMore/native PlotInfo lifecycle,
exact customer/Wonder states, Sprite-vs-Border API guards, category style/UV/tint,
transparent-centre/edge alpha coverage, adjacent plots and hollow swatch selection.
Generator/action checks pass. Mask visually inspected from actual DDS. Firaxis
texture cook + ArtDef cook both exit0, Windows BLP2921472bytes (previous1522688).
These verify source/packaging, not native rendered appearance. No installed
mod/Workshop/settings/game changes; latest sprite outlines need user rebuild
with art cooking and native review.

## Styling direction inverted during implementation — 30 October 2026

Henno changed direction before the sprite-edge review was delivered: outline
unimproved materials/customer districts, add tile fill for improvements/buildings.
Applied to both views: all relevant materials/sales have category edge sprites;
ready sites additionally have .12 fill. Pillage removes fill but keeps edge.
Completed mapped Wonders directly receive both. Quarter white unchanged.

Classifier retains readyStyle as actual readiness, adds outlineStyle for all
materials/sales and filled flag. Renderer skips unready fill assignments entirely
(not just alpha0 calls); legacy unready colour IDs have alpha0. Outline-only
DrawOverlay returns active so placement confirmation/cancellation cleans up even
without any filled tiles. Legend direction inverted too: unready native hollow
swatches, ready native filled swatches. Tooltips regenerated from Markdown.

Full256classification/actualMore/nativePlotInfo suite passes with explicit
outline-only cleanup and pillage-keeps-edge/no-fill assertions. Generator,
localization/action and scoped whitespace checks pass. No art RGB/geometry changed
after the successful ring texture/ArtDef cook; those cooked inputs remain current.
Latest native sprite visibility is still not observed. No install/game changes.

## Stronger fills and neutral fade on unready sites — 30 October 2026

Latest user request sets material/customer and white Quarter map fill opacity to
30%. All four active map-fill colour rows now alpha.30; legend/edge RGB and alpha
unchanged. Unimproved/pillaged resources and empty customer districts retain the
same faded overlay as unrelated neighbours. Manual DrawOverlay puts those sites
into the exact IGNORE grey bucket (no coloured fill); placement keeps native
shadowing by extending its brightness mask only for entry.filled sites. Native
legal/purchase tiles are preserved. Edges remain on all relevant sites.

Full256classification/nativePlotInfo/noMore/actualMore suite passes, including
grey fallback, unready placement mask omission, filled customer Wonder brightness,
30% palette values, state changes and cleanup. Art generator/action checks pass;
geometry/texture RGB unchanged, so existing cooked ring art is still current.
No installed mod, Workshop, settings or running-game changes.

## Working connection animation prototype and 40% fills — 30 October 2026

Latest user asks to try animation again, showing value flow, then clarifies
incoming links require the buyer: improved BASE -> Stage2 building; improved
SPEC -> Stage4 building. Outgoing Quarter -> customer requires matching producer
and customer buildings. Further steering raises coloured and white Quarter fills
to40%; unready neutral fade/bright outlines and legend unchanged.

Implemented shared GetFlowLinks over existing revealed entries: local-player
ownership, adjacency1, completed/unpillaged districts, unpillaged exact-plot
buildings using UI IsComplete(type,plot) + GetBuildingsAtLocation. Inputs require
appropriate Stage2/4 buyers; outbound Stage3 uses gameplay transaction Seller/
CustomerBuildingType, other stages use UI ProducerStage metadata. Added shared
CSC_QuarterFlowBuildings stage membership; owning Bakers/Tailors SQL populates
it. Supplemental customer/Wonder mappings add ProducerStage, Garden additive
patch usesCafeStage4. Mapped completed Tailors Wonders requireFashionHouse and
flow Quarter->Wonder. No gameplay effects changed; arrows indicate structural
building readiness, not all extra Service unlock gates or computed yield amounts.

Independent CSC_Quarter{Lens,Placement}_Flow PressureOverlay layers, Pass1/5.5,
native FormCorpsArrow material. Native pointer caller uses pos1=destination,
pos2=origin (older prototype guessed opposite). API adapters tested with explicit
source/target fields; blueBASE/redSPEC/yellowSALE, native speed2. Sorted signature
cache avoids restarting unchanged animations; per-owner ResetAllWaves on actual
connection changes/exits. Missing flow art preserves static UI. No invented hover
quarter; both endpoints must survive placement's existing territory filter.
Debug logs include layer availability, count and source:target:type pairs.

Native evidence: current game WorldInput FormCorps, Pirates AddUnitWaves, current
Base/ArtDefs/Overlay. SDK pantry is older: cloning native FormCorpsArrow BLPEntry
cooks exit0 but warns missing XLP entry and silently substitutes default. Removed
that clone; reference built-in material string directly. Final native ArtDef cook
exit0 WITHOUT substitution warnings. No new BLP/texture needed. Confirmed other
options: native pressure textures, scrolling spline textures, WorldAnchor AlphaAnim
Bounce pulses (CityReligionInstances.xml72). No speculative arbitrary shaders.

New test_supply_chain_flows covers both Quarter buyers/producers, exact gameplay
Stage3 pairing, wrong/missing/pillaged source and destination buildings, incomplete
districts/Wonders, ownership/visibility/range/location, unique customers/Garden,
semantic/native endpoint directions, cache and independent lifecycle. Full256
classification+nativePlotInfo/noMore/actualMore suite passes. SQL formatting
checks (including token-preserving new-row normalization), localization, art
reproducibility and action checks pass. No installed mod/Workshop/settings/game
changes; animation appearance/direction still needs normal art build/restart QA.

## Native arrow feedback and unified 10% / 50% states — 30 October 2026

User confirms arrows render/have potential, but native direction was reversed:
CityCenter->Quarter and Quarter->Farm. Corrected adapter to pos1=semantic source,
pos2=target; Farm anchors incoming arrows, Quarter anchors outgoing. Prior inference
from Pirates/corps variable names was wrong; actual user-native review takes priority.
Graph direction itself unchanged. Revised playback still needs in-game confirmation.

Latest steering consolidated: all relevant tiles outlined; unready materials,
empty customers and empty Quarters get category-coloured10% fill; improved/working
sites get50% (supersedes intervening40%). Quarter outline opaquewhite, with10/50white
fill depending on functioning real Stage2/3/4 building at exactplot. River/access
flags and hidden Service buildings do not count. Pillaged buildings revert10%.
Removed manual unready-grey substitution and restored placement brightness-mask
inclusion for all relevant tiles. Static classifications now expose ready rather
than filled flag. Existing adjacency/working-flow building gates remain intact.

Added QUARTER empty/outline palette rows (palette18), white QUARTER hex-edge style
on existing ring mask. Legend8rows now explicitly Quarter without Buildings /
Quarter with Buildings plus existing Base/Specialty/Sales state pairs. Native
hollow/filled swatches preserved; key/scroll height430/360 fits the extra row.
Tooltips regenerated for10/50states. Tests cover palette18, Quarter normal/pillaged/
hidden-helper states, opaquewhite style, per-owner outlines, no unready grey,
placement masks, eight-row key and corrected source-tile arrow positions.

Read-only current CivilizationVI.exe CreateLinearWaves registration -> wrapper
0x14022ca90. Parser reads only pos1,pos2,color,speed,type; position fields numeric
plot IDs converted via0x1400f1c00, not free-world coordinates. No per-wave size,
width or offset keys. Native FormCorps material has SplineWidth20/SegmentLength15/
ScrollSpeed.1, but control through a custom material is unverified and SDK lacks
its texture entry; do not invent Lua sizing/offset parameters. Native size unchanged.

Full256classification/noMore/actualMore/nativePlotInfo/flow regression suite passes;
art reproducibility, generated lens localization, actions and palette SQL style pass.
New Quarter white style native-cooked cleanly without substitution warnings. No
new texture/BLP required. No installed mod/Workshop/settings/game changes.

## Manual opacity root cause and texture-alpha fix — 31 October 2026

Human reports no improved-fill opacity increase, observed in manual Supply Chains
lens; placement has not been tested (do not infer it is unaffected visually).
Read-only installed/runtime palette both contain10/50, Lua packed colours contain
alpha25/127, so stale SQL/build excluded. Native EXE dispatcher explicitly strips
Appeal alpha: Appeal branch1401f7a80->1401f7d1a, colour read1401f7d75, ANDffffff at
1401f7d80, BTSbit31 at1401f7d8a, assignment1401f7da0. Thus ALL requested alpha
becomes0x80. Executable SHA/evidence recorded in overlay rendering doc. Earlier
mock-only requested-alpha checks did not prove rendered opacity.

Fixed manual relevant tiles via new independent CSC_QuarterLens_Fill SpriteOverlay,
same native Texture/HEX_GEO path as confirmed edges. Two shared white centre masks
HexFill_Unready/Ready bake nearest8bit10/50 (26/128);8styles tint BASE/SPEC/SALE/
QUARTER from same palette. Masks inset to avoid dulling opaque existing edges.
Only unrelatedgrey remains on native Appeal; carrier/menu/hotkeys/header unchanged.
Clear/reset/takeover clears privatefill while preserving new owner's native data.
Missing newart falls backnativefixedalpha, explicitlylogged. Placement keeps existing
RGBA BorderOverlay fills/edges; no speculative change there. Extra debug reports
texturedfillavailability/count and10/50. Requires fullartbuild/restart, notLuaonly.

Full256classifications/nativePlotInfo/noMore/actualMore/flow/lifecycle suite passes;
fixtures now emulate actualforcedalpha and verify readiness sprite/style assignments,
texturecentre26/128, clear edges, nativebackground and independentcleanup. Generator
--check/actioncheck/scoped whitespace pass. Native XLP+ArtDef cooks exit0 with no
missingentry/defaultsubstitution warnings; newBLP5718528bytes. Desktop reviewpackage
refresh follows. No installedmod/Workshop/settings/game mutations or nativevisual
acceptance. Correctedmanual10/50 appearance still needs user's normal review.

## Bakers stationary flicker and 70% ready fills — 31 October 2026

Human confirms texture opacity improved; Tailors lens is fine. Bakers highlights
flicker even with camera stationary. Native log confirms texturedfill path active;
last sampled connection count0, so do not blame flow waves. Visual cause not yet
proven. Source found every GameCorePublish/activation Refresh clearing/hiding and
recreating identical fill+edge sprites, and clearing/repainting nativegrey.

Added exact plot/style/channel SpriteSignatures per owner/layer. Unchanged redraws
perform no native sprite clear/create/visibility calls. Readiness changes replace
only affectedfill; same-count/differentplot swaps are detected. Close/reopen,
Quarter switches and absent/restoredart invalidate appropriately. Native grey
assignments also cache exactcolour/plots; activationPending and FinishActivation's
explicitforce preserve required settled repaint after deferredMore/Firaxis hooks.
New stats/debug rebuilt,outlinesRebuilt,backgroundRepainted show actual render churn.
Only logs state changes, not every unchangedrefresh. Placement fill backend remains
BorderOverlay; its outlines benefit from same stable sprite lifecycle.

Human requests70% instead50 for ready sites. Four ready palette rows (materials,
customers,whiteQuarter) now.70; unready stays.10, outlinesopaque, IGNOREgrey unchanged.
Generated readyDDSalpha178/unready26, same SQL/RGB driven generator; localization
Markdown/tooltips regenerated and durable current docs updated. Full256classification,
nativePlotInfo,noMore/actualMore,flows/lifecycle suite passes including20unchanged
refreshes/noClearCreateHide, inputreorder, equalcountreadinessswap, forcedbackground
settle and native takeover. Generator/localization/action/SQLstyle/scopedwhitespace
checks pass. NativeXLP+ArtDef cooks clean; Desktopreviewpackage refresh follows.
No installedmod/Workshop/settings/game mutations. User-native review of70% and
Bakersflicker correction still pending; do not claim flicker definitively fixed.

## Shared manual/placement texture fills at 20% / 100% — 31 October 2026

Human requests20%unready/100%ready, explicitly in districtplacement too. Updated
all4ready+4unready palette rows (Quarter/materials/sales); opaqueedges/IGNOREgrey
unchanged. Generatedsharedmasks now51/255alpha. Placement now owns independent
CSC_QuarterPlacement_Fill SpriteOverlay using the exactsame8 fillstyles/masks as
manualLens. Existing edge/flow owners and caches remainseparate. Wrapper selects
newfill first; legacyCSC_QuarterPlacement BorderOverlay only missingnewartfallback.
S.DrawOverlay supports newplacementfill evenlegacyoverlayabsent; ClearOverlay clears
bothowners'Fill/Ready/Flow. Focusedcityterritoryfilter/nativelegalpurchasebrightness
masks remainunchanged; standarddistricts/Wonders retain nativeplacement.

Tooltips source/regeneratedSQL and currentdurabledocs updated20/100. Full256
classification/nativePlotInfo/noMore/actualMore/customerWonder/flow/lifecycle suite
passes: bothownerssame5readinessstylebuckets, placementmasks/cleanup/manualisolation,
20unchangedplacementrefreshes and legacyfallback/newfillwithoutlegacy tests.
Generator/localization/action/SQLstyle/scopedwhitespace checksPASS. NativeXLP+ArtDef
cooksclean; Desktopreviewpackage615filesrefreshed. Noinstalledmod/Workshop/settings/
gamemutations. User-native20/100placementreview and priorBakersflickerQA pending.

## Stable lens, weak contrast: verified direct hex-highlight alternative — 31 October

Human confirms stablemanual lens. Screenshot improved/unimproved flax lacks clear
contrast despite20/100inputs; asks actualdrawingalternatives and MoreLensescomparison,
open to50ready ifbetterpath. Read-onlyinvestigation only; no renderingcode/palette
changes this turn. InstalledCSC_LensPatternsBLP matchesreviewcookSHA6c4a9928...782c6
exactly, masks51/255; LuaReady/Unreadybucketsseparate. Notstalebuild. Our prior
"100%opacity" wordingoverstated texturealpha as finalopaqueimage; exactSprite
shader/compositingnotestablished. NativePass0 has colourkey/postprocessing.

MoreLensesmorelenses_colors.sql FIRSTLINE explicitly saysalpha doesn'tseemtochange
anything; normalfills useAppeal SetLayerHexesColoredArea anddifferentRGBs. Resource
connected/unconnectedusesdifferentnamedcolors. No specialMLopacitybackendfound.

New VERIFIEDshippedpath HexHighlightOverlay + HighlightColoredHexes(plots,color,0),
SetChannelOn(0),SetVisible. WorldBuilderPlacement1538 AND BlackDeath normalingame
MinimapPanel_BlackDeathScenario94–99/42. BaseOverlaydeclaresHexHighlight andWBtype,
emptyMaterial,Pass0. Nativebinding225e10 readsfullpackedcolor intoR13D225f0b,
passesunchangedR8D2260e6->224af0 at226100; unlikeAppeal ANDffffff/BTS31. Actual
finalvisualpercentages stillunverified. RecommendedNEXTtrial20unready/50ready with
privateHexHighlightowners,currentopaqueedges/cache retained, stableSpritefallback.
Noimplementationyet: humanaskedchecking/options. Otherrealoptionscoveragechange
(outlineonlyvsfill orreadyhatch); Pass1/2 flatplanes tradeoffterrainfollowing/MSAA,
notfreeopacityfix. Durableevidence csc-overlay-rendering-options.md updated.

## Direct native RGBA trial implemented; stale radio selection fixed — 31 October

Human authorizes20unready/50ready directhexhighlight approach, and reportsEmpire
radio remainsselectedwhenQuarteropens. Implemented CSC_Quarter{Lens,Placement}_Tint
privateHexHighlightOverlay, Pass0/priority15/emptyMaterial. DrawTintGroups uses
HighlightColoredHexes(groups,color,0),SetChannelOn(0),SetVisible; exactcolor/plot
cache skipsunchangedClear/assign/visibility calls. Readyalpha50/unready20 inpalette
andtooltipsource/generatedSQL; whiteQuarter followsbuildingstate asbefore. Existing
opaqueedges,flows,independentlifecycle andfocusedcityterritorymask preserved.
OldFillSpriteart retained asfallback, thenlegacyBorderplacement ifnewartabsent.
TwoTintlayersgenerated inexistingOverlayArtDef (noextraimport/action). Debugclearly
identifiesnativeTintavailability/count, requestedalpha, packedcolors and rebuilds.
Finalnativecontrast stillnotconfirmed; do notcallrequestedalpha verifiedscreenopacity.

Radioissue iscrosscontextgroup: reparentedCSCentry doesnotjoinnativeActiveLensgroup.
ShowLensControls now recursivelyuncheckscheckedchoicesinactualLensToggleStack,
skipsownCSCentry, neverclickschoices/changesmode. CoversstockEmpire/Appeal and
optionalnestedmodrows. One-shotsettledactivationrepeatclearsdeferredstaleradio.
NoUIteardown/keyboard/nativebindingchanges; preserveexistingentryshutdownguard.

FullsuitePASSbothnewTintandoldartfallback: nativeRGBA20/50 distinctbuckets/channel0,
20unchangedrefreshes, pillage/cache/cleanup, Quarterandstandardplacement/native
masks/territory, immediate+deferredMorehooks, Empire/nestedmodradio clearing for
clickandQ+number, lifecycleinclshutdown. Art/localization/action/SQLstyle/scoped
whitespacechecksPASS. NativeXLP/ArtDefcooksclean(noentrysubstitutions), Desktop
reviewpackage615refreshed and verified including final sourceheadercomments.
Noinstalledmod/Workshop/settings/gamechanges. Rebuildart/restart/nativeQA pending.

## Direct shading adjusted to 20% / 80% — 31 October 2026

Human requests20/80withsameHexHighlight shadingmethod. All4ready palette rows
now.80;unready.20/opaqueedges/IGNOREgrey unchanged. Bothownersusepaletteautomatically.
Fallback readytexture nowalpha204(unready51), generatedtooltips/debug/currentdocs
updated. No renderer/menu/cache/territory behavior changes. FullnewTint+fallback
regressionsPASS; added signed32bitpackedRGBAcoverage for strongalpha's signbit.
Generator/localization/SQLstyle/scopedwhitespacePASS. Nativeartcook/reviewpackage
615refresh passed and verified forcurrent20/80. No installedmod/Workshop/settings/gamechanges;
nativeappearance pending normalhumanbuild/restart review.

## Selected-city Quarter placement sites included — 31 October 2026

Human confirms current20/80shading looksgood and requests overlaysalsoinside
selectedcity whileplacingQuarters. REMOVESpreviousoutside-focused-city-onlyrule.
PlotInfo wrapper nowusesallS.GetPlotEntries(quarter,false), preservingdiscovery,
classification/readiness,20/80directRGBA+edges, nativelegalpurchaseandbrightness
maskdedup/cleanup. Existingvalidworkingflowsinsidecity noweligible too; standard
district/Wonder placement unchanged. Noart/palette/rendererchanges.

Existingplacementregressionsupdated torequireQuarter/materials/customersinside
focusedcity, othercities/foreign/unclaimedterritory, focuschanges, tileswaps and
allplotsownedbyfocusedcity. FullnewTint+fallback/nativePlotInfo/noMore/immediate+
deferredMore/flow/lifecycle suitePASS, scopedwhitespacePASS. Durablecurrentdocs
updated. Noartcookneeded. Reviewpackage615refreshed/Luaverified; normalModBuddyrebuild/
reloadneededforgame. Noinstalledmod/Workshop/settings/gamechanges.

## Direct shading adjusted to 20% / 60% — 31 October 2026

Humanrequests20/60. Fourready palettealphasnow.60, unready.20 unchanged; primary
directHexHighlightbothviews includingSELECTEDCITY stays. Existingedges/readiness/
flow/menu/cache rules unchanged. FallbackDDS51/153; tooltips/debug/currentdocs
updated. FullnativeTint+fallback/PlotInfo/More/lifecycle+signedRGBA suitePASS;
generator/localization/SQLstyle/scopedwhitespacePASS. Artcook/reviewpackage615
refreshpassedandverified. Noinstalledmod/Workshop/settings/gamechanges; rebuild/reloadreviewneeded.

## Crash investigated: missing City Center, green-highlight reproduction pending

31Oct humanreportsAVswitchingvanilla->Bakers/extra green tiles, then confirms
manuallyremovedCityCenter andaskswhethergreenmightrelate. ActualfreshnativeDMP
Base/Binaries/Win64Steam/CivilizationVI.exe.dmp296902bytes/16:16:32 archivedwith
logs+installed/sourceLensfiles toDesktop/Codex/csc-lens-switch-crash-20261031-161632.
Gamealreadyabsent. RealExceptionStream thread23460/READ0xc0/GameCore+52d00;
originalexceptioncontext(notlaterthreadsnapshot) recovered. GenuineofflineWindows
unwind12frames: mapread->DistrictGetComponentID191616->CityCommandBaseStart133a9
->SetFocus67f270->Manager13ea1->MessageExecute33f44->Receive37e67->Process37358.
ExactGameCorehash324c51e9...c2e98cmatchesGhidra; basehandlerGetCityDistrictreturns
NULL thenunguardedGetComponentIDcomputesnull+c0, matchinguserremovedCityCenter.
DifferentfromearlierHavokRadioUIexitcrash; no renderer/radiocall on actualfaultstack.
FinalnetmessagesCityCommand2; installedlogs20/80, notnewsource20/60.

Greenmaybestaledamaged-citydisplay OR borrowedAppealpainter; notindependently
confirmed. Humanasks"againcouldrelatemissingcenter"; answeredyespossiblebutdump
provesonlycrash. DoNOTblindlypatch/rollbacklens. RetestintactCityCenterworldfirst.
Noimplementation/palette/art/installed/save/settings/gamechanges ornativelaunch.
Durablereportproject/docs/research/mods/csc-lens-switch-crash-20261031.md.

## Yield-coloured delivery arrows and draw priority — 31 October 2026

Human requests arrows over tile fills; investigate 50/50 border placement and
size; both material inputs orange Production; outgoing delivery colours follow
the customer's yield, including Wonders. Implemented in both Lens/Placement:

- Private PressureOverlay Flow priority raised 5.5 → 20, keeping Pass 1 and
  the shipped FormCorpsArrow material. SDK Civ6.cfg says higher priority draws
  over lower; Pass 1 folds into terrain pass when grayscale is off. Tint=15,
  final border-fill fallback=15.5. No native/shared material is overridden.
- New UI table CSC_LensFlowYieldColors maps yields to native UI palette names.
  Production uses STANDARD_ORANGE_MD (255,129,18), Culture PURPLE_LT
  (183,128,230); Food uses YIELD_FOOD. Other Science/Gold/Faith mappings included.
  Explicit orange/purple avoid dark-brown/magenta aliases. Tile palette remains
  accepted 20/60 blue/red/yellow/white with opaque outlines.
- District deliveries reuse CLASS_CSC_<Q>_SALES_<YIELD> tags already propagated
  by the adjacency processor, rather than duplicating yield metadata. Existing
  building, owner, range, completion/pillage/discovery gates remain in force.
- CSC_QuarterWonderSales adds nullable CustomerYieldType. All three Tailors
  Wonder rows set YIELD_CULTURE, matching their existing gameplay modifiers.
  Fashion House → completed adjacent Wonder arrows are purple in both views.
  These are UI metadata changes, not new economic effects.
- Link records/signatures include yield and resolved colour. Unchanged refreshes
  keep animations stable; missing yield mappings do not invent a generic arrow.
  Tooltips now explain delivered-yield colours.

Position/size investigation: actual EXE CreateLinearWaves binding at 0x14022ca90
reads ONLY pos1/pos2/color/speed/type. Positions are plot indices, no offset,
scale, arbitrary world endpoint, width or centre field. Anchors remain source →
target, speed 2; **exact 50/50 visible glyph extent is not implemented/proven**.
Current FormCorpsArrow material has SplineWidth=20, SegmentLength=15,
ScrollSpeed=.1, Color_Alpha=128. Fields exist but effect on CSC custom material
not native tested. Private material + authored packaged texture would allow size
trials; SDK lacks exact shipped texture and prior cloned BLPEntry silently
defaulted. WorldAnchor supplies arbitrary positions/image sizes as another
implementation option, requiring its own animation and camera/zoom/occlusion
prototype. Do not invent wave API parameters or globally replace FormCorpsArrow.

Full SQL-backed/Lua/native PlotInfo/actual More callbacks/new Tint/old fallback/
lifecycle suite PASS. Added outgoing Food/Culture/Production colour cases,
Base/Spec inputs, unique customers/Garden, all three Wonders, missing-yield
handling, colour signature invalidation and priority > Tint assertion. Native UI
palette values checked against installed XML. Generator/localization/actions/
SQL style/scoped whitespace checks PASS. Native cooker exits 0 with no missing
texture/default-substitution errors; Desktop csc-chevron-lenses-20261030 review
package refreshed (615 files) and Lua/SQL/cooked ArtDef+BLP equality verified.
No installed mod/Workshop/settings/game changes. Normal ModBuddy rebuild WITH
art cooking + restart needed to review draw order/colours; no new in-game visual
claim. Durable docs: csc-quarter-lenses.md and csc-overlay-rendering-options.md.


## Exact material, Quarter and flow palette — 31 October 2026

Human supplied new hex colours. Implemented exact RGB across both owners,
outline sprites, fallback fill styles and legend; retained 20% unready / 60%
ready fills, opaque edges/legend and all current connection gates/order/caches.
Base #451301, Specialty #ea8706, Sales #b6a835. Flow Production #894000,
Gold #fdec5d, Food #468419, Culture #bb44bd, Science #0873e1, Faith #a7bede.
Replaces previous native UI colour aliases with private CSC gameplay Colors rows.

New CSC_LensQuarterColors mapping holds all eight identities: Bakers #5f821c,
Tailors #9037aa, Apothecaries #0e54a9, Carpenters/Stonemasons/Blacksmiths #be6b0a,
Brewers/Goldsmiths #c2af38. All Quarter tile fills/edges/legend now use that hue,
superseding earlier all-white treatment. Table alone does not enable stub lenses.
Ready RGB literals normalized from bytes; EMPTY/OUTLINE derived in SQL. Generic
white fallback retained for future unmapped keys. 48 CSC palette rows total.

Shared Lua classifier and empty-bucket adapter now use selected Quarter colours;
renderer uses its specific generated edge/fallback styles (four stable channels,
separate Lens/Placement owners). Art generator executes palette SQL in memory to
resolve derived colours instead of fragile literal regex; emits all eight Quarter
style families. No new action/file registrations needed. Tooltips/current docs
updated for brown/orange/Quarter identity palette.

Existing full regressions pass: 256 classifications, native PlotInfo and actual
More callbacks, hotkeys/menu/lifecycle, direct Tint plus sprite fallback, flows
including Wonders, static/cached rendering and exact RGBA. Palette regression
checks exact requested byte colours/all eight identities and matching cooked-source
sprite tints, all six yield mappings, unchanged alpha/readiness. Native XLP/ArtDef
cook exits0 without missing/default errors. Desktop review package refreshed;
no install, Workshop, settings or game action. Normal full-art rebuild/restart
required for native appearance review. Position/size remains the previous native
plot-endpoint implementation; no 50/50 glyph extent claim.


## Width-14 arrows, Base #7a3700 and midpoint trial (31 October 2026)

Human requested 70% arrow width, centring investigation/custom rendering trial;
follow-up Base colour now #7a3700, superseding #451301. All four Base RGB rows,
art, legend, existing palette assertions and current docs updated; alpha20/60.

Native effect now uses private CSC_Lens_FlowArrow SplineBorder with WIDTH14
(20*.7), original segment15/scroll.1/alpha128/FOW/tint, Flow priority20. Solved
older SDK missing-source blocker by recovering native FormCorpsArrow DDS from
installed Base Overlay.blp read-only: SHA807a6a384068c6be91c528421b9fc26571dcaf1a0c9bd22c49d6843569e0c2dd.
Pinned extractor records exact serialized TextureEntry38157/nameSlot32, DXGI29,
128x64,8mips,raw43692bytes; all original mip payload preserved. Control extraction
of preceding HexPlace_ValidFill_Overlay matches SDK pixels EXACTLY. New extractor
project/tools/lenses/extract_native_flow_texture.py fails on uninspected source.
Native XLP/ArtDef cook clean (no default/missing warnings), full original43692byte
payload found in own BLP at2922496; outputBLP5763072bytes. Source texture preview
inspected at Desktop/csc-chevron-lenses-20261030/native-flow-arrow.png. No stock
material/game/installedmod/settings/Workshop change; width material verified,
in-game visible width not yet observed.

Main mod adds concrete opt-in CSC_QuarterFlowTrial.lua/.xml (Import490/AddUI502).
Support publishes cached gated wave records and owner clears. ExposedMembers
Enabled flag suppresses only CSC native waves during comparison, without reset.
Default FALSE. After rebuild/restart/opening Quarter lens, UI FireTuner command:
LuaEvents.CSC_QuarterFlowTrial_Enable(true); false restores narrower native.
Alternatively set ENABLED_BY_DEFAULT=true in trial Lua before build.

Trial uses 3 moving world-line chevrons, WIDTH14/CENTER.5/SPAN.5/PERIOD1.2,
stroke2UIpixels. Whole glyph stays within25%-75% of centre-to-centre path, centred
on boundary, source->target, fades atends. Own passive WorldAnchor context30Hz
while active; independent Lens/Placement, unchanged-link caching, strategic hide,
X/Y seam suppression, player/owner clears and callback-only/no-widget shutdown.
Uses existing working chain records/colours/Wonders; no new economic data.

Actual EXE inspection confirms LineControl self+3numeric API: Start registration
14001a9a3 -> Lua1408db320 -> parser1408d91c0 -> native1408dc390; End14001a943
->1408db300 ->1408dc2e0. Native setters allocate/update WorldAnchor endpoints.
No invented per-wave offsets or UI angle APIs. Native camera/terrain compositing
still needs visual review; trial is wire UI artwork, different from pressure shader.
Primary BLP reflection website was research aid; actual serialized offsets and
pixel parity established locally, with provenance in durable overlay options doc.

Full SQL/Lua/nativePlotInfo/actualMore/newTint+fallback/lifecycle/flow suitePASS;
new actual-trial-Lua mocks verify geometry,width14,colours,source->target motion,
cache/native compare without wave restart,bothowners,strategic,X/Yseams,shutdown.
OriginalDDS/allmips equality and manifest wiringPASS. Generator/actions/SQLstyle/
scopedwhitespace checksPASS. Desktopreviewpackage619files refreshed+verified
against current source, width14cookedArtDef and exactmipBLP. No game/install action.
Normal full-art rebuild/restart required. Current docs: csc-quarter-lenses.md and
csc-overlay-rendering-options.md (trial commands/constants/evidence/review steps).


## Invisible midpoint trial: native evidence and v2 host patch (31 October 2026)

Human reports trial draws nothing. Read-only current Lua.log first showed false,
then updated during QA to actual enabled=true links=2, no trial Lua errors. Source
matches installed script. Native working links were resource1713 -> Quarter1639
Production and Quarter1639 -> customer1712 Food. Separate TunerMapPanel.lua136 nil
startup error exists; no evidence it caused this trial rendering failure. Do not
blame activation/readiness or claim v1 rendered based on mocked geometry.

More offline EXE inspection: Line world setters call1408dc440 to project private
WorldAnchor endpoints into2D coordinates/control bounds, then1408dc7d0 schedules
updates. These are ordinary UI Line controls, distinct from an actual XML
WorldAnchor instance. Native interface exists; visual path still needs QA.

V2 removes Context Layer=WorldAnchor, uses normal passive full-screen Context;
attaches only FlowTrialContainer to actual /InGame/WorldViewControls. Explicit
viewport-sized host and per-chevron Root frames, updates them on resize, explicitly
shows context/container on attachment. XML seed Lines use nonzero1x1 geometry.
This addresses hosting/clipping hypothesis, NOT a confirmed native root cause.
Ready flag preserves native arrows if hostmissing/empty even when trialEnabled;
Enable(true) now retries rather than returning when already enabled. State checks
and Support suppression use Enabled+Ready. No colour/gate/economic/art changes.

Debug loadedv2; rebuild logs received/accepted counts/hostsize; one firstframe
log per rebuild with strategic flag, root/line hide+dimensions, world coords and
alpha (no perframeflood). Tests expand actual trial script mocks with fullscreen
parent attachment, dimensions/resize, missing/zero host native fallback/retry,
all earlier geometry/lifecycle/owner cases; fullsuite PASS. No native render claim,
no game/control/liveTuner/deployment/settings/Workshop action. Human owns QA.
Only3runtimeUI files changed; normal rebuild/restart and enable(true) needed,
no new art cook required. Desktop review package refreshed; current docs updated.


## Unimproved Base raised to 30% (31 October 2026)

Human confirms visually different intensity for both20% fills, then requests
unimproved Base30%. Changed BASE_UNIMPROVED alpha .20 -> .30 only, both owners
via shared classifier. BaseRGB#7a3700, otherunready20%, allready60%, opaqueedges
andlegendunchanged. Updated tooltip numeric descriptions/debug/currentdocs.
Fallback generator now shares masks where alpha matches and emits dedicated
BaseUnready30% DDS/TEX for Base exception; ArtDef style/XLP and Content registered.
Existing opacity/mask assertions updated; full regression suitePASS. Normal art
rebuild/restart needed for complete source+fallback change; no install/game action.


## Native v2 visual confirmation; v3 native path/trade comparison (31 Oct 2026)

Human screenshot confirms v2 DOES render across borders (hosting fix succeeded),
but thin/fast and crossing offset from edge midpoint. Also requests trade-route
animation/material option. Changed trial renderer to native PathOverlay for both
styles, preserving existing chain records/colours and standard pressure fallback.
Avoids unsupported ground-height assumptions: UI GridToWorld gives z0 and actual
EXE UI.GetWorldZ is a constant-zero stub, so no invented terrain sampler/offset.

Actual ABI inspected: CreatePathAlongSpline registration140008b73 -> wrapper
140227f20 ->140228d00, receiver + integer plot-index table + packed RGBA thirdarg.
Indices through1400f1c00, builder1402274c0 wraps map coordinates; thirdargunpacked
RGBAbytes by1409789f0. Direct native method, not hardcoded UILens TradeRoutes API.
Stock TradeRoutes PathOverlay Pass0 materialTradeRoute verified; native template
TradeRouteOverlay/SplineBorder has textureTradeRoutePrimary, width12,repeat32,
scroll.65. SDK source/Overlay.xlp entry EXISTS (unlike older FormCorpsArrow gap).

Generator now emits4private layers CSC_Quarter{Lens|Placement}_Flow{Chevrons|Trade}
PathOverlay/Pass0/priority20. Private styles CSC_Lens_PathChevrons / PathTrade:
width18,repeat32,scroll.13 (one-fifth stocktrade),alpha224,white multiplier + yield
colour per path. Chevrons reuse recovered stockarrow; Trade references shipped
TradeRoutePrimary/Overlay library. No native material/global TradeRoutes touched.
Full centre-to-centre path replaces v2's25%-75% interval: half lies each side of
sharededge, rendererowns terrain/projection. This addresses offset hypothesis;
actualv3direction/weight/edgealignment still nativeQA, not claimedobserved.

TrialLua rewritten as passive native-path controller, no widget/tick/movingwire.
Enabletrue uses currentstyle, defaultoff/initialchevrons. New event:
LuaEvents.CSC_QuarterFlowTrial_SetStyle("trade") or("chevrons") bothenablestyle;
Enable(false) restores normalwidth14Pressure waves. Existing Enabletrue works.
Perlayerexactwave signatures/cache, switch clearsoldlayer, separateowners,
Readyfallbackifmissingnewart, nativewraphandoff, safeevent-onlyshutdown.

Existing full suitePASS plus rewritten actualtrialcontroller mocks: source/target
andcolour matching, two private materials/layers, cache/noreset, switching/missing
artfallback/ownercleanup/nativewrap/invalidstyle/shutdown.14overlaylayers total;
ArtDefsettings/nativeAPIcontract checked. XLP/ArtDef nativecook0 no default/missing
errors. Normal fullartbuild+restart needed; no installedmod/Workshop/settings/
gameaction. Currentdocs updated; Desktopreviewpackage refreshed separately.


## Q prefix observer lifecycle repair (31 October 2026)

Human reports Q+1 sometimes launches vanilla Religion from default map view.
Read-only source/native inspection: UIManager global handler is one replaceable
Lua reference (+0x5948), not a chain; Firaxis TunerUtilities.lua also sets it.
Candidate cause is a later load/focus registration replacing CSC's init handler.
IMPORTANT: inspected Lua.log is from ANOTHER AUTOMATED GAME with no manual Q
attempts, per human clarification. Absence of key logs proves nothing here.
Leave that game, console, installed files, settings and key input untouched.

Source-only panel repair: reattach on LoadScreenClose, context reload, app focus
return, plus one settled SystemUpdateUI tick. No polling/per-frame takeover.
Preserve Q state on settled callback; cancel at actual focus loss/return. Remove
queued repair on shutdown. Added observer-install/key-code/cancel-reason logging.
Regression reproduces overwritten slot from selection: old Desktop package fails
Lost Q observer after game-load handoff; patched source passes complete suite
with/without actual More Lenses callbacks. Also cover no steady tick installs,
fast chord before deferred tick, shutdown cannot resurrect observer. Human native
validation pending rebuild; no proof this is their actual intermittent cause.
Lua-only change needs no art recook. Review-package refresh not performed in
this follow-up; current repo source is authoritative. No game/deployment actions.


## Native material contact sheet (31 October 2026)

Human requests actual native animation candidates. New offline generator
project/tools/lenses/native_animation_contact_sheet.py inventories all shipped
base/DLC Overlay.artdef nonzero-scroll SplineBorder styles, dedups18textures,
extracts checked104byteTextureEntry RGBA + padded name table from4nativeBLPs.
12/18 exactSDKpixelcontrols; remaining6noSDKDDS. Source package/pixelhashes,
allstylevariants/settings, nativePNGs retained. Sheet18cells+48frameGIF study
at Desktop/Codex/native-lens-materials-20261031. Visually inspected sheet; labels
and swatches legible. GIF/dimensions/18sourceexports verified. GIF normalized
UVscroll only, NOTnativegameprojection/shader/orientation/timing. Rawredgreen
bordermasks intentional.8flowcandidates include5newer recovered nativeeffects
(corps,zombie,warning,Piratepointer/dowsing),10borders. Scenarioart explicit
packaging needed; outgoingreligionstockwidth0. No runtime/modsettings/console/
gameinteraction; ongoingautomatedgame untouched. Currentrenderingdoc updated.


## Conveyor default + live Service check marks (1 November 2026)

Human wants small square/rectangular links inspired by the Service notification
ring, and the EXACT check-mark notification icons on functional customer tiles.
Clarified selected Quarter ONLY, then explicitly removed multi-icon layouts.
Use one centered Quarter EFFECT_NEW icon per served tile, not MCUIS job icons.

Implemented v4 defaultEnabledtrue/Styleconveyor in existing passive flow context.
New white128x64 rectangle DDS/fullmips, private Conveyor PathOverlay per owner:
width18/repeat16/scroll.10/alpha224, unchanged link/yield colours and gameplay
chain gates. Older chevrons/trade still selectable; Enablefalse normalpressure;
missingnewartfallsthrough. Native projection/timing still human review.

GetServicePlots reads existing CSC_AbilityAttachModifiers benefit anchors and
live GameEffects active exactDistrict subjects (same notification authority and
complete SQL requirements as art-source flags). NO separatecivic/materialgate,
NO persistent hiddenServicebuilding or aggregatecityartflag used as proof. Exact
owner/city/district, selectedquarter, revealedreadycustomerentries; one icon even
severalproducers/anchors. ThreeWonderanchors reuse same reader. Allread-only.
SharedLens+Placement Services RECT_GEOsprites centered24x24includingpadding,
priority25abovefills/flows, cachedsignature + independentcleanup. Atlas100px
BAKERS0/TAILORS8 copiedpixelidentical into128padding, no redraw/resample/tint.
6newContentfiles; generatedXLP/ArtDef updated; no actions/gameplaySQL changes.

Complete256classification/lifecycle/manual/nativePlotInfo/actualMorecallbacks/
flows suitesPASS; newservice tests real11anchors inclWonders, active/lost/missing/
malformed/wrongidentity/duplicate/filter/QuarterSwitch/cachedlifecycle/oldart and
exactcroppixelcontrols. Artgeneratorcheck and ModBuddyactionsroundtripPASS.
Isolatednativecook exits0withoutmissing/defaultsubstitutions; full3newDDSmip
payloads foundbyteidentical in cookedBLP; sixContentrows once. Output
Desktop/Codex/csc-conveyor-service-lenses-20261101 (art,BLP,dep,logs,validation,
sourceartpreviewvisuallychecked). Noinstalledmod/Workshop/settings/game/console
interaction; no fullpackage refresh. Human fullartrebuild+restart for nativeQA;
noFireTunerenable needed for conveyor. Earlier v3off-default notes superseded.


1 November conveyor orientation correction: human requests broad sides following
one another, 90deg from initial preview. Exact texture rotation128x64 ->64x128;
material width/repeat/speed unchanged. General DDS helper now uses maxdimension
and reaches1x1, so portrait has all8mips; TEX lastmip7. Generator/checkPASS,
thresholdbbox24x80 verified, isolatedXLPcook0 + fullpayloadBLPcheckPASS. Desktop
reviewpreview refreshed/visuallychecked (vertical slats along horizontal path).
Only ConveyorDDS/TEX actual generated changes; no installed/game action.

1 November conveyor density/opacity: human requests thicker pieces than gaps,80%opacity. Slat travel coverage24/64 ->48/64 (75%solid/25%gap,3:1); broadsideorientation retained. PrivateConveyor Color_Alpha224->204 only; no doubledtexturealpha. Runtime debug nowreports204. Fullregression/generatorcheckPASS; isolatedtexture+ArtDefcook0/fullpayloadBLPcheck+bbox(8,24,56,104)PASS. Desktoppreview+receipt refreshed/visuallyreviewed; fullartrebuild/restartfornativeQA. Otherstyles/overlays/settings/installedgame untouched.

1 November spacing refinement: human requests70/30. Conveyor generator supersampled10x for exact70%slat/30%gap, broadsideorientation and80%materialopacity unchanged. Generator/check+measured70.0%centerline coveragePASS; isolatedtexturecook0/fullDDSmippayloadinBLPPASS. Reviewpreview/receipt refreshed. No game/installed/console/AI changes. Earlier75/25 note superseded.


## Native conveyor fading, v5 (1 November 2026)

Human explicitly requests native-chevron fade on origin/destination. Read-only
native shader analysis (no game/console): shipped DX11 .bs4.5MB has932DXBC blobs.
D3DDisassemble confirmed Pressure PS0xd7fc8: fade=1-(2t-1)^4, t=(distance-offset)/
length, multiplied by texture RGBA + per-wave g_vColor. Path PS0xd5140 only
texture*tint, NO endpointfade. Prior Color_Alpha204 material alone did NOTprove
80% nativeopacity; corrected to actualperwaveRGBAalpha204 preservingyieldRGB.

Default v5 conveyor now private PressureOverlay Pass1priority20 called
CSC_Quarter{Lens|Placement}_FlowConveyorWaves. NEWidentity avoids oldcookedPath
objects receiving wave methods afterLuaonlybuild. Chevrons/trade comparison
remainPath, defaultEnabledtrue, Enablefalse returnsoldnormalpressure. Cache/
independentowners/oldartfallback maintained. No perframeLua/UIline/timer added.

Native fixedoffset32/length32 at14022d03b..49 would returnorigin-half footprint.
Solved via padded nativequad artwork: LinearWaveVB init14022c090 dataquad
140fcb840=(-.5,+.5,0,0),850=(+.5,+.5,1,0),860=(-.5,-.5,0,1),880=(+.5,-.5,1,1).
V0isforward+.5. Quadlength48 + visibleglyphcenterV1/6 shiftsforward16. New
ConveyorWave128x256DDS has visible5.6unitsslat so stride8 gives70/30. Native
speedrecord3 yields densitylog2(1+3)=2 =>stride32/(2*2)=8; global scroll.10,
width18; materialalpha255neutral, perwavealpha204peak80%. For64unitneighbors,
visibleglyphcentres16..48 straddleboundary32, fade0/80/0. Projection/frame
appearance stillnativeQA (mathematical/nativefileproof, NOTobservedgameplay).

Added inspect_native_overlay_shaders.py --shader-library --output; records
library+blobhashes/Pressure+Pathdisassemblies. Desktop/Codex/
csc-conveyor-service-lenses-20261101/native-fade-evidence includesquadJSON +
actualEXEhash. Onecandidatequadaddress-orderassert failed; correctedchecked
840/860 ordering, orientationformulaunchanged. Both nativecooks0, fullnewDDSmip
payloadinBLPverified; generatorcheck/actionroundtrip/uniqueContentPASS.
Full256classification/nativePlotInfo/actualMorecallbacks/serviceicons/cache/
flows suitePASS, including2owners, explicitRGBA/sign handling, correct70/30
waveUVaxis/forwardoffset/cachednativefade/backend/cleanup. No installedmod,
Workshop, playerprefs, sourceAI, liveconsole/game actions. Human fullartbuild+
restart required. Sourcecurrentdocs updated; older v4Path/defaultalpha claims
superseded. Existing staticartpreview shows artwork only, not nativefade.

1 November67/33 refinement + colour clarification: both conveyor textures now share fill=.67 (visible native slat5.36/stride8), 80%perwavepeak/nativefade/forward16 retained. Full regressions/generatorcheckPASS; isolatedtexturecook0/bothmippayloadBLP checksPASS. Currentcolour remains peryieldRGB from CSC_LensFlowYieldColors passedunchanged through ConveyorWave; white is sourceartonly (preview nowlabels this). Docs/receipt/preview updated, no gameplay/installed/AI/console actions. Earlier70/30notes historical.

## 1 November: repeated shortcut release regression

Human reports Q+1 opens Bakers while 1 is held, then Religion on release.
Read-only Lua.log shows repeated key=28/message=1 delivery: first masked,
World context restored, second unmasked, then close reason=native lens hotkey.
CapturedKeys was cleared on first up. Keep capture latched through all ups until
the next fresh down; existing fresh-down reset also handles interrupted chords.
Observer v3 and captured=true/false edge diagnostics identify rebuilt code.
No global observer replacement strategy, saved bindings, native game or installed
files changed. Tests now replay each edge 2/3 times with intervening refresh,
both release orders, both Quarters, fresh bare number after chord, and duplicate
plain-Q release. Old code FAILED the new case; fixed full lens suite PASS with
actual More Lenses callbacks and without More Lenses. Human rebuild/manual QA
still pending. Other chat's automated game and pinned AI sources untouched.

## 1 November: white conveyor and provisional Religion-exit hold, v6

Human accepts native fade, requests white belt and reports sub-second jump/loss
of height/depth ONLY from Religion, not Default/other lenses. ConveyorWave now
sets 0xccffffff in both owners; 80% peak/fade/67:33/geometry unchanged. Underlying
semantic yield-colour records and earlier optional comparison styles retained.
Read-only shipped Pressure VS0xd6748 uses shared OverlayGlobals matrices and no
per-wave Z. Religion native Lua also calls SetDesaturation1/0 on layer on/off;
neither observation proves projection root cause or native transition duration.
No invented height parameter or arbitrary forced terrain mode was added.

Provisional workaround: panel detects Religion before Appeal takeover and signals
flow trial; fills/icons immediate, flows hidden for1second then created once.
Short-lived ContextPtr update counts delta only, no perframegeometry/repainting;
close/reopen/player/shutdown cancel. Support also suppresses native fallback
during hold, including missingart. Other lens entry immediate. Logs v6 tintwhite
settling and guardstart/finish. This conceals transient if settled withinwindow;
NOT established native depth repair. Human rebuild/nativecheck pending.

Full suite PASS incl actual More Lenses listeners/nonMore, bothowner whiteRGBA,
delayedcreation once/no churn, close cancellation, Default immediate, player and
shutdown cancellation, controller events before carrier from submenu/hotkey.
No texture/artdef changes/cook required. Docs current. Native REA standalone EXE
xrefs investigation produced no result; canceled waiting exec and close_binary
returned resultnull. Original Ghidra GUI database was GameCore from another task,
read-only programinfo only; not switched/mutated. No native investigation claim
from REA. No game/FireTuner/install/settings/AI changes.

## 1 November: V7 native render-pass correction and vanilla Appeal handoff

Human rejects delay; animation from Religion vanished with V6 and lens3 Appeal
after either Quarter was blank until4->3. Log has V6 guardstart/nofinish. Removed
all delay/transition fields/events/update gating; immediate white80% nativewaves
restored. Human refined original jump to apparent reset within<0.5sec, asked if
Religion also uses pressure waves. Yes same renderer, private overlay objects.

Offline DX11 EXE trace (pinned E745...D63) via pefile2024.8.26/Capstone5.0.9;
temporary deps AppData/Local/Temp/csc-lens-native-deps, not source/runtime install.
REA Rizin unavailable; no target launched/attached. SetDesaturation wrapper
19bac0 -> command2b -> renderhandler545d80 target14232a52c; current14232a528
interpolates at2units/sec (556b70, constant2 at140fa4048). At54efd3 when current>0
primaryrender mask1 (Pass0), at0 mask3(Pass0+1), passed to21bbc0; loader21ac14
encodes1<<Pass, loop21c01a testsbit. This explains a discontinuity at0.5sec:
our oldPass1 migrated between stages, not established sharedanimationclockreset.
Pressure clocks perobject+144 (22c380), ResetAllWaves22b7d0 onlycounts158/170.
Changed conveyor AND fallbackPressure flows toPass0/priority20 bothowners, above
fills15/15.5, nativefade/geometry/67:33/white80% unchanged. Added rebuild-only
layer/count/links/time logs, no perframecallbacks. Helper
project/tools/lenses/inspect_native_lens_transitions.py verifies exactbytes,
instructions,masks,thresholdzero/rate. Evidence Desktop/Codex/
csc-conveyor-service-lenses-20261101/native-transition-evidence.json.

Appeal: vanilla SetActive(Appeal) no-ops on our existingcarrier, never emits
layeron to nativepaint. On nativeAppealaction relinquish then lens-only
Default->Appeal restart, no interfaceSelection roundtrip. Same pattern as More
Lenses ToggleAppealLens. Tests now model same-name no-op, bothQuarters and
nativecallback before/afterCSC, plus actualMore listeners/nonMore.

Human screenshot Service mark underMarketmodels: Services nowPass2/priority25,
native latepass used by MapLabel overlays, instead ofterrainPass0. Bothviews,
unchangedpixelart,size,anchor,gates. CooksourceANDcookedXMLPass0flows/Pass2icons
verified, isolatedArtDefcook0, fullregressions/generatorcheck/actionroundtripPASS.
Output cook-artdef-stable-pass0-service-pass2.log/validation.json updated. Full
ModBuddyARTbuild+restart required; nativevisualacceptance stillpending (rootpath
confirmed statically forDX11; no renderedQA/claimsDX12observed). No installedmod,
Workshop/settings/game/FireTuner/sourceAI changes. Earlier V6guardnotes historical.


## 1 November: V8 thick shallow chevrons; half-span remains unresolved

Human requests thick chevrons and half-length whole belt centered on hexedge.
Native binding22d042/49 fixes offset/length32; material quad/glyphsize does NOT
halve fade band. Asked native/current-span vs custom-renderer preference. Human
asks about using opacity/longer fades; explained positional quartic formula,
no exposed duration/cutoffs; scroll changes time not spatialspan, texturealpha
travelswithglyph. No custom-renderer choice inferred. Halfspan16
NOT implemented; explicitly documented/logged/receipt. Do not claim it is done.

Implemented authorizedshape: white thick openchevrons replaceslats, 67%stroke/
33%gap ineachcrosspathcolumn, pitch8/stroke5.36; nativewidth18/fade80/Pass0/speed
unchanged. Pointdepth initially4, human then asks lesspointy ->2. Supersampled
polygon in canonical64x128 and actualpadded128x256wave DDS, V0forward. Wholearea
centroid+16offset (ratherthanold center-column test), tipaheadarms. Bothowners.
Onegeneratorrun hit memorymappedArtDef InvalidArgument22; unchangedArtDef not
rewritten now, only changed outputs. Failedtestthenwas oldDDS beforegenerator
reachedcustomtextures. Fixedgeneratorrun/fullregressionsPASS; nativeXLPcook0,
bothfullDDSpayloadsincookedBLP verified. Generatorunchanged-outputskip preserves
AE/ModBuddy mappedfiles. No sourceArtDefsemantics changed inV8.
Desktop/Codex/csc-conveyor-service-lenses-20261101 has initial/shallow artwork
previews (actualtextureprojectedquad proportions, NOTgameplay), latestreceipt,
cook-textures-shallow-chevron-v8.log. Visuallycheckedshallowerglyph. Source/docs
updated; no installed/settings/game/console/AI changes. Human artbuild/restart
for visualQA; original halfspanrequest unresolved under nativebackend.


## 1 November: V9 doubled Service icons, fake shadows, 60% chevrons

Human explicitly requests doubled Service icons, slight fake drop shadows on
both icons/chevrons, and60% chevron peak. Implemented sharedstyles bothviews:
RECT_GEO Service RectDims24->48 in bothaxes, Pass2/priority25 retained. Foreground
100pxnotificationcells notredrawn/resampled; softblackshadow alpha28% maximum,
offset3/4px blur2px compositedbelow. Opaqueoriginalpixels exact; antialiasededge
premulcolour preserved. Chevrons samegeometry/67:33/offset/speed/Pass0, shadow
worldoffset.42/.56 mappedtoquadtexturepixels, blur2px at128width, alpha28%source.
PerwaveRGBA0xccffffff->0x99ffffff (153=60%); nativefade affects shadowtoo. No
extraoverlay/animationtimer/gameplay logic. V9logs alpha153, stylescomparison
unchanged. Halfspan16 remains unresolved/nativeband32 unchanged.

FullsuitePASS incl foreground geometry measured withpremultwhitecoverage so
blackshadowdoesn'tfalsifycentroid/strokefraction. Iconopaque/edgecolour/shadow/
doubleddim/owner/gates testsPASS. Bothisolatednativecooks0; all4DDSfullmippayloads
foundbyteidenticalinBLP. Firstcookreceiptassert expectedstring48 butcookwrites
48.000000; correctednumericread, cookedsize48 verified withoutunneededrecook.
Preview shadowed-chevron-service-v9.png visuallychecked andvalidation.json
updated inDesktop/Codex/csc-conveyor-service-lenses-20261101. Fullartbuild/restart
fornativeQA pending. No installedmod, game, FireTuner, prefs, Workshop, AIedits.


## 1 November: upright Service-marker options contact sheet

Human says flat Service sprites unlikely towork; asks badges/pins/optionssheet.
Read-only native UI source confirms WorldViewIconsManager WorldAnchor Scaling1/
UnitsPerPixel.06/Billboard1 and GridToWorld/SetWorldPositionVal; MapPinManager
WorldAnchor/Image/MapPin/MapPinFlag with native tint; UnitFlagManager ZoomAnchor;
DistrictPlotIconManager WorldAnchor/Grid/Label and DistrictBonusBack style.
All6proposals are feasible UIcompositions, NOT shipped CSC presets or native
screenshots. No game/modmarker implementationchanged. Native sourceart used:
MapPin,MapPinFlag,CityBannerProdCircle,UnitFlagBase_Combo,Controls_FrameInfo;
existingBakersServiceDDS used asforeground. Screenshot798702 Entertainmenttile
hasnoexistingServicebadge; samecropbackground6times, no scene erasure.

Output Desktop/Codex/service-marker-options-20261101/service-marker-contact-sheet.png
1512x1292 + sixindividualcards + source-evidence.json hashes/exactnativeUIlines.
Options01barefloating,02darkroundbadge,03goldmedallion,04mappin,05unitflag,
06compactstatusbanner. Allcamera-facing; customsize/height/zoom/pulse possible,
finalnativeQAneeded. Sourcegeneratorproject/tools/lenses/service_marker_contact_sheet.py.
Visuallyreviewedfullsheet/cards; fixed02toactualnativewhitebase tintednavy (raw
atlas150,0iswhite, notdark), removedbrightselectionrim. Final02dark/readable.
Suggested02forreadabilityor04fortileanchoring; no choiceinferred. No installed,
settings, game, console, AI edits. Nativeasset frameoffsets/cellcrops verified.


## 1 November: service-specific upright pins and MCUIS parity

Human selected option04 MapPin, actual Service icon (not generic checkmark),
MCUIS cumulative current-effect+Supply Chain tooltip, and right-click Service
Civilopedia page. Implemented source-only CSC_QuarterServicePins WorldAnchor UI
native MapPin71x95 + serviceicon50; plotcentre tip, screen-space above3D;
1centre/2paired/3triangle/4square. Shared CSC_ServicePresentation reader/formatter
extracted from MCUIS; both views use same AbilityDesc signed total/stack/plural
parameters and AbilityIcon/AbilityIconTarget. Exact active District subject gates
retained, selectedQuarter only; citytotal tooltip perMCUIS; same Service target
branches concatenate original tooltip sections under one pin. No gameplay flags
or persistent grants as proof. Flat _Services sprites hidden (art leftunused).
Independent Lens/Placement UI snapshots, placementprecedence, GameCore refresh,
instancepool/icon/text caching, cleanup/rightclick reset, no nativecalls inpin
shutdown. NewImportFiles+AddUI503 and Content items; actionCDATA regenerated.
FullSQL/nativePlotInfo/actualMoreLenses/hotkey/lifecycle/flow/service suite PASS;
21FashionHouse gameplay/notification/MCUIS tests PASS; nativeQA pending normal
humanModBuddy rebuild/reload. No installedmod/game/console/settings/AI edits.


## 1 November: invisible Service pin context fixed (v2 source)

Human reports no pins. Read-only current Lua.log confirms v1 loaded, valid
pins1/2BAKERS created, no runtimeerror; installedsource matches. Actual native
InGame.lua Initialize passes isHidden=true to all LoadNewContext AddUI calls.
Our pin context never called SetHide(false); child instance visibility cannot
show a hidden ancestor. Fix InitHandler attaches context to native
/InGame/WorldViewControls (same group as MapPinManager), explicitly unhides,
LoadScreenClose fallback if parent unavailable, unregister on attach/shutdown.
Uses existing native UI and read-only CQUI PlotInfo_Citizens attachment pattern;
no override/Workshop edits. v2 loaded+attached/contextVisible log. Test now
models hidden AddUI ancestor, disallows instancecreation until attached/shown,
earlymissingparent+LoadScreenClose retry, reload preservesinstances, teardown.
Fulllens/actualnativePlotInfo+MoreLenses regression suite PASS. Panel stale
check-mark diagnostic renamed pins. No gamecontrol/installedmod/artcook edits;
human rebuild/reload/nativeappearance confirmation pending.


## 1 November: smaller/lower inner Service glyph only

Human clarified outer pin must retain size/position. Inner glyph now38px (native
registered atlas, formerly50), topoffset28 instead15 (13px lower, ~25%original
50px height). OuterMapPin71x95/hitbox61x75/anchor/multipinspacing unchanged.
Discarded interrupted wholepinresize/translation; noPinOffset wrapper remains.
Fulllens regression checks PASS; no installed/game actions. Native review after
human rebuild/reload.


Inner Service glyph follow-up: requested 15px below original rather than13;
topoffset now30 (original15), glyph38px and outerpin unchanged. XML verified.

Inner Service glyph follow-up: also 2px left; offset now-2,30. Size38px,
vertical displacement15px fromoriginal and outerpin unchanged. XML verified.


## 2 November: Q mode restriction fixed and gold medallions selected

After investigation-onlyturn, human authorizesfix+contactsheetoption3. Current
log has2Q/1downattempts rejectedmode372882022;17successfulQuarterchords. No
modeenumnameclaim; nativeMinimapacceptsmoremapmodes. Replace Selection/modal
allowlist with named exclusions District/BuildingPlacement,Cinematic,Fullscreen;
keepWorld/localplayer/text/modifier/WorldBuilder/recordingguards. OnModeChanged
uses samepredicate so allowedmaptransitions retainprefix. v4observerlog. No
mask/inputtiming/animationchanges. Tests addactualfailedvalue+debug/city/move
modes, bothchords, bare1nativeReligion, prefixacrossallowedtransition; placement/
cinematic/fullscreen exclusionsretained. FullSQL/nativePlotInfo/actualMoreLens/
UI/service/flow suite PASS. No claimthisaddressesunobservedcapturecauses.

ServiceUIchanges MapPin71x95 to nativeCityBannerProdCircle80x80 goldmedallion;
confirmed textureentryinBaseWindowsUI/InWorld.blp. ExistingServiceglyph38px,
centrevertically/-2pxX; pin-specific15pxdownshiftretired. Slotcentrespacing88px
avoidsframeoverlap (1centre,2paired,3triangle,4square). Tooltip/Pedia/gates/
WorldViewvisiblecontext/pooling intact. v3medallionloadlog. Build/actioncheck andscopeddiffcheck PASS; normalhumanrebuild/reload/nativeappearanceQA
remains pending.
No installedmod/game/console/settings/Workshop/AIchanges.


2 November medallionsizefollowup: humanwantssmallerframe,sameServiceglyph.
Frame/hitbox60x60 (was80), centredwithinunchanged80x80 root toretainexisting
glyphposition. Icon38px/-2,0, slots andcallbacksunchanged. XMLverified.


## 2 November: broader native UI inspiration sheet

Human wantscloservanillaUI, uninspiredbyearlier6options. Created24nativeart
source+Servicecompositecards: unlockhex/building/seal, hollowhex, faithcrest,
pennant, heraldicframe, pantheonlozenge, engravedsquare, insetgold, inkornament,
cartouche, thingoldseal, compass/Pedia, softdisc, pendant, portraitflourish,
openprogress, notificationhinge, promotionribbon, yieldplaque/status/questbubble.
All24texturenamesfoundBaseUIBLP;19exactXMLrefs,5SDK-onlyusage(labelled).
ActualBakersStage3Serviceicon50atlasindex9,cropped/resized38, notgenericcheck.
Leftsourceunrepainted/proportional, rightillustrativeUIcomposition;4tintslabelled,
2panels9sliced. No nativecaptures/implementationselectionimplied.
Desktop/Codex/native-ui-service-inspiration-20261102/native-ui-service-inspiration.png
1712x1990 +24cards/inventory/source-evidence.json. Sourcegenerator
project/tools/lenses/native_ui_inspiration_sheet.py. Visuallycheckedfinalsheet;
count/package/source/XMLchecksPASS. No modasset/game/installed/settingschanges.


## 2 November: native directional effects / pressure contact sheet

Human asksmoregameequivalentschevrons inclReligion/Loyalty. New16cards: native
FormCorps, ReligiousIn, LoyaltyIn, TradePrimary/Secondary, MoveValidstatic,
ZombieSense(RedDeathscenario), ReligiousOut(stockwidth0visualoverride), SVroute/
adjacencystatic, religiondirectionmodel/conversionhalo, actualnativeTourism
Religion_PressureHigh/Medium/Low flipbooks(41/41/71frames), pressurestatussymbols.
ReadsactualBLPviaexistingvalidatedRGBAreaderfornativeoverlaytextures, SDKother
art; sourcehashes/ArtDefvariants/SDKpixelchecks retained. CorePressurestudy uses
Vtravelform+nativewidth:lengthratio, rotatesright, quarticendpointfade. Paths
Uscroll; staticassetsstaystatic, UIflipbooksactual80cells8/10columns. Normalised
cycles/spacing/projection: NOTnativecapture/timingclaim; clearlylabelled.
Desktop/Codex/native-directional-effects-20261102/native-directional-effects.png
1712x1542 +16cards, native-directional-motion.gif (48frames/9effects),
source-evidence/validation.json andmotion-review3frames. Fullsheet+motionreview
visuallychecked, count/frame/sourcechecksPASS. Reusablescript
project/tools/lenses/native_flow_inspiration_sheet.py. No modart/game/installed/
settings/consolechanges.


2 November: humanrequests chevrons40%peak. V10 per-wavewhiteRGBA0x66ffffff
(alpha102) inbothowners; nativefade/geometry/speed/shadow unchanged. Fulllens/
flow/input/placement/actualMoreLenses regressions PASS. No newartcook needed;
normalhumanrebuild/reload. No installed/game changes.


2 November backingvariants PREVIEWONLY: user22-25%height/-50%width =>46x44
(round43.5), nativeCityPanel_YieldBacking9slice(6,12). Alternative20hingeless
alreadyexistsnativeActionPanel_Notification2 (50pxsource ->60pxdisplay), so no
repainting/hingeremovalneeded. BothactualBakersStage3glyph38px/-2X.
Desktop/Codex/service-backing-variants-20261102/service-backing-comparison.png
1200x866, twoindividualcards/previewmarkers/source-evidence. Visuallychecked
3xdetails+screen-sizecomposite; exactframe/glyphchecksPASS. Sourcegenerator
project/tools/lenses/service_backing_variants.py. No selectionimplemented, no
mod/runtime/gamechanges.
