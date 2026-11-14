# No-CSC district-slot controls

Requested after the completed [three-map CSC campaign](csc-ai-planning-campaign-results-20261114.md).
Henno wants to distinguish displacement of vanilla district investment by
slot-consuming Quarters from poor valuation or placement. The three treated
games and their report closed before the Shadow interruption; source/report
commit `8bc627cf` and engine-skill commit `5a0af20` are pushed and verified.

## Fixed protocol

Three fresh Small/Prince/Online games through250. Same three preselected map
and game seeds as treatment; explicitly select the original six leaders in
their original seats through normal game setup. Five original AI seats are the
cohort. City Lights, Resourceful2 and Sukritact's Resources remain at their
exact treated hashes; **CSC is absent**, not merely untuned. This holds other
mods constant so the comparison addresses removing CSC. No RHAI5 or other AI
policy. CE provides passive facilities with all tuning policies disabled.

| Map | Map seed | Game seed |
|---|---:|---:|
| Continents |18461107 |29461107 |
| Pangaea |18431267 |28681391 |
| Fractal |19672039 |29812257 |

Removing CSC also removes its resources/map effects, so matching seeds and
leaders does not establish identical generated maps or identical subsequent
choices. Record actual starts, resource rules and surviving AI separately.
These are seed/configuration controls, not a claim that every difference is
caused solely by district slots.

The shared controller owns every launch, console command, five-turn autoplay
window, checkpoint and exit. Manual checks remain about15 minutes apart.
Archive50/100/150/200/250 saves,25-turn censuses, native journals, UI events,
mod/file identities and exact preference restoration. Stop rather than silently
retrying a failed child or substituting a favourable seed.

## Measurements and native qualification

Record every district foundation, completion and ownership change, plus native
UI adjacency at its own placement notification. Keep native types, CL types,
City Centers and Wonder footprints distinct; a completed Wonder district object
does not prove its building completed. Record district slot metadata in the
loaded catalogue. Verify absent CSC districts/private yields in read-only SQLite
and Lua, and verify CE's enabled/version/entries/changed/managed counters stay0.

The existing passive reader captures a native cached total at district selection
(XP2 RVA3e0f3c). Continue to report its age relative to foundation for the same
comparison used in the treated games. Add an optional **before-placement cached
snapshot** at BuildQueue::PreCreateDistrict entry, RVA1029c0. This is not a forced
recalculation and does not prove the forecast was recomputed on that turn.

Ghidra reference SHA324c51e9: full1257-byte function matches actual XP2
SHA092abfbb, body SHA256
`c6b12fc601d6b76ca3aa9633dbe60097f3b7acd37885ed588577e39503cca402`.
Windows x64: RCX=BuildQueue*, RDX=DistrictDefinition*, R8=borrowed int32 XY pair.
Queue+1e8 resolves City*, definition+14 gives the district index, City+1948
resolves the already-qualified CityBuild matrix. Lua's CreateIncompleteDistrict
wrapper independently passes the address of its local int32 coordinate pair.
No native game functions are called by the observer. It changes no game data,
scores, return values or registers; observational trampolines remain installed
until controller-owned process exit.

The cached read validates current city/player, loaded district index extent,
bounded row/matrix lengths and selected-row pointer alias. Missing/unreadable
data remains explicitly unavailable. A factory may handle an existing district
or return failure: its record is not a new foundation without the matching
physical event. Pairing and clocks remain explicit. The new boundary has static
and synthetic-register qualification; live coverage must be measured in the
first control, not assumed.

Artifacts:
`C:/Users/Shadow/Desktop/Codex/csc-no-csc-district-baseline-20261114/`.
`placement-entry-ghidra.json` and `placement-entry-code-parity.json` retain the
decompile/ABI and whole-function parity. Maintained implementation is
`project/tools/native_ai/late_placement/vanilla_district_run.py`, its passive Lua
observers and the optional capture in `economy_savings_watch.*`. The serial
campaign wrapper contains no game commands. No CE rebuild or upstream PR.

## Status

Preparation:12 offline observer/database/native-VM tests pass, including19-hook
compatibility, the optional20th placement snapshot, changed-after-entry values,
failed/repeated factories, no-CSC SQL guards and distinct foundation/completion/
ownership events. All treated archives survived the Shadow interruption.
Control outcomes pending; no construction or balance result claimed yet.

The serial runner is now active, starting with Continents. It is deliberately
independent of CSC's gameplay contexts; no CSC package is installed/enabled.
The live preflight,20 passive hook installation and first normal autoplay window
have acknowledged. Outcome/coverage assessment waits for recorded physical events.

**Return-field qualification correction while recording stays frozen:** assembly
at102e6f/102e8c writes only AL for the factory's boolean result. The optional
`returnedSuccess` field currently tests the wider int32 register and is therefore
not a qualified success/failure measurement; ignore it in all control arms.
Before-entry cached totals, coordinates and physical-event records are separate.
Join construction from physical foundations, not this optional flag. Correct
the capture to mask the low byte after the frozen campaign and add an upper-bit
regression fixture. This affects passive classification only, not game policy or
recorded entry values; do not mutate live source pins mid-run.
