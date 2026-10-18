# Automated gameplay QA

> **Terrain review / testing deferred (15 October 2026):** Henno observed test
> placements in ocean areas. The old fixed-coordinate/terrain-forcing fixtures
> are not valid gameplay acceptance evidence. Do not resume an old run as a
> terrain-validated test. Henno is testing manually now; do not launch, mutate,
> advance or automate Civ until he resumes automated testing.


The live QA runner is `project/tools/qa/smoke.py`. It drives Civ through the native
FireTuner bridge; Computer Use is reserved for UI barriers the native path cannot
handle. Tests run in disposable games. They do not change Quarter acceptance gates.

**15 October 2026 trial:** native auto-start and material stacking passed. A real
tile-purchase event reproduced a stale adjacency bonus; gameplay fixes were
explicitly deferred by Henno. The full save/reload pipeline is not yet verified.
See [the bug report](gameplay-qa-findings-20261015.md).

## First regression slice

Start Civ VI at the main menu with a current installed CSC build, then run from
the repository root:

```powershell
python project/tools/qa/smoke.py --disposable-game --output "C:\Users\Shadow\Desktop\Codex\csc-qa-new-run"
```

Use a fresh output directory for a fresh run. The pipeline captures mod
preferences before selecting CSC alone, starts a new Gathering Storm game,
creates a Tailors district and three adjacent material sites, and asserts native
district Production changes of 0, 1, 2 and 3. It then removes/restores a resource
and purchases a prepared unowned resource tile through the native city command.
Repeated refresh must be idempotent. WorldBuilder ownership writes are silent;
they prepare the purchase test and are not treated as normal ownership events.
The fixture and its baseline are saved as game properties. Save/reload checks
reconstruct test helpers from source and read the persisted fixture; they do not
recreate it or explicitly refresh CSC before asserting the result.

The runner saves the fixture, returns to the menu, reloads it, repeats the native
assertion, captures logs, returns to the menu and restores mod/auto-start
preferences. The installed test package is retained. It uses the normal native
`Automation.SetAutoStartEnabled(true)` path, whose load-screen consumer runs after
the engine's load-complete event. It does not use the old environment-controlled
15-second LoadScreen patch.

`pipeline.json` records progress. A readiness timeout exits with code 20 and
records the missing state. Successful stages can be resumed with the same
command/output directory. An interrupted or failed action retains `in_flight`:
inspect its evidence before clearing that field. Mutations are never blindly
retried. A completed pipeline is a no-op when resumed; use a new directory for a
new regression run.

## Evidence and limits

- `results.json` records command outcomes; each command has a unique completion
  token and its own raw evidence file. Missing output cannot pass an assertion.
- `pipeline.json` must say `passed` to claim the full slice completed. Individual
  passing commands do not establish an end-to-end pass.
- The expected resource yields are literal design values, independent of CSC's
  count functions, generated modifiers and property bit values.
- Setup may force content into existence and explicitly refresh once. Subsequent
  mutations rely on normal engine events, with assertions in separate commands.
- The persisted baseline isolates district Production from fixed river bonuses.
  It does not establish correct delivery for building, plot, city or route yields.
- `save.json` records the original save path and SHA-256; the completed save is
  copied into the evidence directory. Dispatching a save alone is insufficient.
- Preserve `Database.log`, `Modding.log` and `Lua.log`. Classify known official
  frontend localization errors separately from CSC gameplay errors.
- The first slice covers material adjacency stacking and lifecycle only. It does
  not establish gameplay acceptance for an entire Quarter, visual quality,
  construction eligibility, compatibility mods, trade, Services or AI behaviour.

The gameplay/UI review package can be prepared using the existing
`project/tools/adjacencies/build_test_package.py` and
`install_test_package.py` tools. Use explicit Desktop/Codex output paths. The
installer preserves a full backup. Record its file hashes with the run; it reuses
installed cooked art, so it does not validate a new art cook.

## Expansion order

1. Customer population boundaries: 4/5/9/10/55, unequal producer/customer
   population, rounding each customer before summing, same-city transactions,
   multiple customers and suppliers, stale bit clearing.
2. Stage 2/3/4 local and bilateral building transactions, specialists, local and
   regional Amenities, service AND gates and persistent service structures.
3. Native trade-route lifecycle and Stage 3 + Stage 4 stacking; compare actual
   delivery with preview and supported UI breakdowns separately.
4. Wonder exact-plot placement, source stacking, removal/restoration, multiple
   Wonder construction orders and save/reload.
5. Unique replacements, M&C improvement tiers, settings and supported mod
   combinations. Record an explicit configuration matrix; unrun combinations
   remain untested.

Trace each case to the public design and contracted `runtime_scenarios`. Retain
offline Lua/SQL tests for fast feedback; native scenarios verify engine delivery
and normal event wiring. Force-refresh probes are diagnostic evidence, not
substitutes for normal event tests.


## Reload boundaries and native operations

After changing package action wiring, fully exit Civ before installing and
restarting it. A menu round trip can retain the previous manifest while reading
new SQL, producing a mixed configuration. Verify the expected current modifier
IDs and Database.log before accepting results.

Debug `CreateBuilding`/`RemoveBuilding` mutations are useful fixture operations,
but a failure that also reproduces on unchanged Bakers requires a normal native
purchase control before classifying a new gameplay defect. Use the
`producer_returns_native` group for material-return acceptance. Preserve failed
fixture observations separately; do not count them as passing native tests.

## Terrain-aware candidate planning (draft, not yet validated)

The read-only `project/tools/qa/plan_materials.py` searches existing owned cities
and the actual map. It does not terraform or place resources. Requirements name
the Quarter, material classes (or exact resources), and allowed improvements.
The planner checks passable land, native district eligibility, preserved
features, ownership and owning city, distance within three tiles, adjacency,
matching existing resources, and native improvement eligibility. It uses
backtracking to allocate distinct sites, so a flexible slot cannot consume the
only candidate for a more restrictive slot. The result includes coordinates,
terrain/features, river status, ownership, resource/improvement state and
rejection counts. It rechecks selected layouts before returning them.

The initial planner deliberately searches existing owned cities; it does not
claim to solve native city founding, native Builder operations, Wonder-specific
placement, or legal Industry/Corporation founding. No suitable arrangement means
an explicit blocked scenario, not permission to change the coastline. Candidate
feasibility is not a passing gameplay test.

The fixed-coordinate Tailors world and debug city creation are retired. Shared
helpers reject unaudited historical fixtures, water/impassable material sites,
illegal districts and improvements, and resource changes that do not fit the
existing terrain/features. The small material fixtures now request candidate
layouts. The old end-to-end smoke/full matrix still needs integration and native
validation before automated use resumes; do not treat it as ready to run.

**Execution status:** implementation draft saved; no offline or native tests of
these new planner/guard changes have run. Henno requested that automated testing
wait while he runs his own tests. Previously reported test counts refer to the
source before this terrain-planning draft.
