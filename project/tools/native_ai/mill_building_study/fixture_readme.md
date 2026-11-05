# Controlled native Mill fixture

`fixture.lua` supplies the explicit gameplay phases for a disposable research
world. It starts no process, opens no console, advances no turn and changes no AI
score. The maintained shared controller owns every command and archives replies.

The fixture implements the intended local-Mill contract directly:

- Wind: one Production on its Quarter's own hills plot, zero otherwise.
- Water: `floor(native river-edge count / 2)`, from zero through three Production.
- A functioning Mill affects only the functioning Quarter containing that Mill.

The oracle does **not** call CSC's count, eligibility, amount or preview helpers.
It reads native geometry, building presence/location/pillage and district state.
Acceptance compares actual native district Production differences and the new
Boolean properties, and checks that the ten retired numeric properties are zero.

## Host contract

Execute the source once in `CSC_AdjacencyGameplay`, in a fresh disposable turn-1
world, after the root driver creates two human-player cities and chooses two
empty owned ring-1 sites. Root must keep those two districts at least six tiles
apart. All mutations are restricted to human player 0; AI probe cities remain
outside this fixture.

```lua
CSC_MillFixture.Print(CSC_MillFixture.Prepare({
    schema=1, player=0, token='explicit-study-token',
    localCity=65536, localPlot=811,
    remoteCity=131072, remotePlot=831
}))
```

Those IDs and coordinates are illustrative. Use captured native bindings, never
copy them into a live test. Preparation rejects developed buildings other than
the Palace, improvements and other non-center districts touching either site.
It clears resources/features and normalizes nearby terrain, creates two complete
Bakers Quarters and verifies native district/type readback. Fixture changes are
deliberate test setup, not ordinary AI construction or legitimate build orders.

For each ID returned by `Describe().cases`, execute these phases in order:

1. `PrepareCase(id)` removes previous Mills, repairs the Quarters, sets geometry
   and creates the declared initial building state. It refreshes adjacencies but
   deliberately does **not** capture the yield baseline in the mutation command.
2. `CaptureBaseline(id)` samples native facts in a later command. It changes only
   fixture bookkeeping. Root takes at least two identical captures in separate
   commands, with a bounded settling window, before accepting a baseline. The
   last sample is the exact baseline used by `ApplyCase` and `FinishCase`.
3. `ApplyCase(id)` performs the single declared building/pillage/removal change
   and refreshes adjacency properties. A phase reservation precedes mutation.
   Repeating the command after success, failure or ambiguous acknowledgment is
   rejected; root must preserve the partial state rather than replay it.
4. `Capture(id)` samples the post-change facts without touching the world. Root
   again accepts two identical separate-command captures. Do not wait until the
   expected yield happens to appear: first establish stability, then compare.
5. `FinishCase(id, 'assert-local-contract')` checks fixed native yield differences,
   actual/encoded amounts, unit-step values and cleared legacy bits, records the
   receipt and permits the next case.

`Print(value)` emits one JSON marker, `CSC_MILL_FIXTURE=...`. Every sample contains
both target districts, native Production, building locations/health, native hill
and river geometry, neighbors, unit/legacy properties and the independent expected
local bonus. The root driver should archive mutation acknowledgments and every
settling sample, not just passing summaries.

## Cases and interpretation

There are 21 ordered cases: Wind flat/hills; Water zero through six river edges;
remote Wind/Water; local-and-remote Wind/Water; removal, building pillage and repair
for both Mills; Quarter pillage and repair with a Wind Mill present.
Quarter repair is an explicit continuation of the preceding, completed Quarter
pillage case. It retains the same district, Mill and geometry; its preparation
performs no world mutation. The expected restored bonus remains +1.

The first native attempt is preserved as a failed run after 20 accepted cases.
Its original final preparation removed/recreated a Wind Mill and pillaged its
Quarter within one Lua command. After repair, the native readback showed a
complete, unpillaged Quarter and unpillaged Mill, with expected/encoded +1 and
the +1 step enabled, but district Production remained zero across two samples.
The Mill itself was **not** auto-pillaged. The reason for the missing native
payout was not established by those facts. The revised paired case removes the
unsettled construction scenario; it does not change the +1 contract or turn the
earlier failure into a pass. A native rerun must still decide the repair result.

The zero-edge Water case uses the same explicit Tuner building-creation bypass
as the other fixture cases. It tests a forced building's effect, not inland Water
Mill availability. Real availability remains controlled by CSC's river flags.
The fixture does not modify those flag definitions or prove queue/UI legality.

An intentionally legacy comparison arm can call
`FinishCase(id, 'record-only')`. Its receipt is labeled `record-only`: it records
counterexamples and permits progression, but does not make a passing local-rule
claim. A legacy observation must never be counted as a successful unit-step test.

## Save/reload

After a completed case, `Export()` returns a descriptor with configuration and
all native facts. Root persists that returned descriptor outside the game, saves
the exact inactive world and later re-executes this source in the new gameplay
context. `VerifyReload(descriptor)` only reads native facts and compares them with
the descriptor; it does not recreate cities, districts, buildings or properties.

This is an exact same-package fixture comparison. A deliberate legacy-to-unit
migration changes properties and should have its own reviewed expectations;
identical-descriptor verification cannot establish that migration's correctness.

## API provenance and offline checks

- Existing `project/tests/adjacencies/live_fixture.lua` and `live_transitions.lua`
  demonstrate `CreateIncompleteDistrict`, exact-plot `CreateBuilding`, removal,
  terrain/resource mutation, refresh and native district yield reads.
- Shipped `Debug/City.ltp` lines 1083/1097 use
  `CityBuildings:SetPillaged(building.Index, boolean)`; line 336 uses
  `District:SetPillaged(boolean)`. The fixture checks these methods exist before
  starting its cases.
- Shipped `Base/Assets/Maps/Utility/RiversLakes.lua` supplies the three river
  setters and valid flow pairs. The six stored-edge ownership rules also appear
  in `CSC_AdjacencyPresentation.lua`. Every geometry change independently
  asserts the native `GetRiverCrossingCount()` result.
- Gameplay `GetBuildingLocation` is an exact plot index, as verified by the
  project's existing native fixtures; the older generic CSV's x/y description
  is not used as the contract.

Run the existing Python runtime with Lupa available on `PYTHONPATH`:

```text
python -B -m unittest discover -s project/tools/native_ai/mill_building_study -p test_fixture.py -v
```

Fifteen actual Lua 5.1 tests pass. The independent native-shaped model delays yield
publication and can inject erroneous empire-wide activation, wrong yield scale,
retained legacy bits or wrong building locations. The fixture rejects those
states and rejects mutation replay, wrong turns and wrong bindings. Tests also
cover exact read-only reload comparison and Civ's integral numeric type label.

These tests validate the fixture and oracle plumbing. They do not load Civ or
establish native yields, real modifier timing, UI visibility, general migration,
economic benefit or native AI decision quality.

The model now also admits a newly created source's district attachment only at
the next flush. It can reproduce the adverse create-then-pillage shape while
keeping the native health/property readbacks correct, and verifies that paired
repair performs no create/remove/geometry operation and retains object identity.
That is a regression model of the fixture risk, not recovered Civ internals or
proof of the first native failure's cause.
