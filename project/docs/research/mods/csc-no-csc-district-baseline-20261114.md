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

**Continuation, 14 November:** Continents reached250 and saved/closed with exit0.
The final observer assertion stopped the campaign because a queued event remained
unresolved. The archived-log audit recovers all ten censuses and377 original-AI
foundations, all with UI adjacency. The six extra UI additions are existing City
Centers changing owner, accounted for by Core ownership records. No native or
Lua observer faults.357 factory-entry cached totals read successfully.

Continents has156 slot-consuming native foundations without CSC versus158 with
CSC,49 versus48 final cities, and572 versus602 population. These are the first
map's comparison, pending the other two maps. Raw failure and the offline recovery
audit remain together; the missing original Finish acknowledgement is preserved.

Henno authorises the remaining Pangaea and Fractal controls. `--remaining`
preserves the first-stop ledger, checks its completed250/save/closure and starts
only these two preselected games. Future endpoint observers print unresolved
event details and finish; analysis keeps their coverage visible. Pending-event
completeness alone no longer discards a completed game or blocks the next map.

The optional factory-return flag now masks AL, with high-register-bit regression
cases passing, before launching the remaining games. Their source pins record
the diagnostic revision; the original Continents return flag stays excluded.
Construction counts continue to come from physical events in all arms.

One additional archived field correction: the no-CSC observer's `foundationTurn`
can contain an extra native event argument rather than a turn. Use the journal's
actual `turn`, as the comparison already does. Correct the callback boundary
after the two running games finish; keep their pinned source unchanged.

Artifacts: `offline-observation-audit.json` and
`full-game-observation-complete.json` in `continents250-01`; original
`failure.json` and `campaign-progress-first-stop.json` remain available.

**Pangaea completed / Fractal started, 14 November, 15:32 UTC:** Pangaea
reached250 and closed with exit0, retaining all ten censuses and323 original-AI
foundations with323 matching UI adjacency identities. Three extra UI additions
are City Center ownership changes.129 slot-consuming native foundations versus
124 with CSC. Native reader frozen cleanly, no observer faults/messages.

The final checkpoint permission stayed false because the observer's local turn
was inactive, although Core was idle and the return seat was human. No SaveGame
request was sent. The50/100/150/200 saves and complete250 observations survive;
an offline audit qualifies the measurements and preserves the raw failure.
No additional gameplay was performed to enable a save.

Shared checkpoint handling now exposes `SavePermissionUnavailable` for that
specific pre-request timeout. Observation-only controls log the unavailable
optional checkpoint and continue. Timeouts after submitting a save remain errors.
The callback timestamp boundary was also corrected before starting Fractal;
extra native event payloads are discarded, and pending rows retain the real
callback turn.16 observer/database/native-VM and6 checkpoint-phase tests pass.
Fractal runs directly under the shared controller; the ledger preserves the
second stop and both offline recoveries.

**Speed snapshot:** Continents autoplay took35.59 minutes.49 observed inactive
gaps before the next autoplay activation total6.09 minutes (median6.27 seconds),
covering controller handoffs, native readbacks and checkpoint work. Calculated
from `command-begin.started_unix` and the first completed inactive-state reply
file timestamp for each window. This identifies controller idle time separately
from engine simulation. At Pangaea cleanup, C: had25.41GB free, RAM2.71GB free,
with no disk queue in the sample. Optimise controller overhead after the controls.

### Initial preparation and recording history

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
