# CSC bundled adjacencies — first implementation

_2 October 2026. Implemented and locally tested; not a Workshop release._

## Scope and provenance

CSC now ships its own adjacency schema, modifier compiler, gameplay evaluator,
placement preview, descriptions, overlays and localization. Its ModBuddy project
no longer declares MAB as a dependency. Players of this build do not need a fork
or a patch helper. Normal ModBuddy packaging includes the replacement.

The scope is implemented Bakers' and Tailors' gameplay, all additions/fixes in
Henno's MAB integration branch, and the historical specific-Wonder capability.
Future Quarter designs do not define additional requirements for this version.
This is a CSC engine, not a general replacement for every inherited MAB feature
or an API for other mods that write Ruivo's tables.

Credit **Ruivo** for [Modular Adjacency Bonuses Core](https://steamcommunity.com/sharedfiles/filedetails/?id=3429735059)
and its [source architecture](https://github.com/revoltl/NEW_ADJACENCY_BONUS_BY_RUIVO):
declarative rules, plot counting, ring traversal and property-backed modifiers
made this work possible. Credit **Zegangani** for the specific-Wonder approach.
The shipped manifest includes both acknowledgments. The new engine is independently
implemented; MAB source is used read-only by differential tests, not vendored.
The renamed stock adjacency support file preserves Firaxis' native UI behavior.
Keep these credits in CSC's release notes and Workshop description.

Reference: clean local `test/all-features` at
`d852b8466cf7152f4fd76cacec5fa8c2084d7c0a`, compared against upstream base
`e978e6c`. See the [audit and migration plan](mab-independence-plan.md) for the
commit inventory and distinction between fork work and the older Wonder helper.

## Source layout and loading

All shipped engine files are under `Civ Supply Chains/Lua_UI/Adjacencies/`.

| File | Responsibility | Order |
|---|---|---|
| `CSC_AdjacencySchema.sql`, `CSC_AdjacencySources.sql` | Own rules, objects, providers, bits and source metadata | 90 |
| Quarter / ModSupport SQL | Existing resource and district tags, material config | Existing orders |
| `CSC_AdjacencyProcessor.sql` | Generate CSC rules and object labels from those tags | 3000 |
| `CSC_AdjacencyModifiers.sql` | Unique clones, signed bit modifiers, requirements, attachments | 4000 |
| `CSC_AdjacencyCore.lua` | Shared matching, ring traversal, eligibility, amounts | Imported 490 |
| `CSC_AdjacencyGameplay.lua` | Event refresh; sole writer of plot properties | 501 |
| `CSC_AdjacencyPresentation.lua` | Shared signed previews, descriptions and edge selection | Imported 490 |
| `AdjacencyBonusSupport.lua` | Native placement support plus CSC preview/overlays | Imported 501 |
| `ToolTipLoader_CSCAdjacency.lua` | Firaxis tooltip extension hook; skips loading-screen contexts | Imported 501 |
| `CSC_AdjacencyUI.xml/.lua` | Native UI unit-level read exposed to gameplay | InGame 501 |
| `Text/CSC_ADJACENCY*_TEXT.sql` | Generated from `project/localization/` Markdown | 4000 |

Edit `project/modbuddy/CivSupplyChains.actions.json`, then run the normal ModBuddy
action check/patch tools. Localization is regenerated with `loc_md_to_sql.py`.
The old `Lua_UI/Ruivo_Adjacencies/` directory remains historical reference but
is unregistered and absent from the new package, including `patch_mab.py`.

## Coverage matrix

| Behavior | Implementation | Evidence |
|---|---|---|
| Bakers/Tailors BASE and SPEC materials, ownership, optional material tags | Own processor plus visible resource tag matcher | 61 frozen rules equal; native BASE/SPEC production and ownership transition |
| Quarter sales and customer return yields, unique customer tags | District tag matcher; processor propagates tags to replacements | Frozen generated rows and 610 modifier effects/collections; native yields |
| Water Mill river bonus and Wind Mill hill bonus | Building ownership gate retains authored collection | Native remote-city Water Mill activation/removal; hill source fixture |
| Tailors river segments, fractional totals | Native river count; truncate total toward zero | Native yield delta; positive/negative fractional fixture |
| Ring min/max bands, ring zero, wrapped-map deduplication | BFS over native neighbors | 7×7 and tiny wrapped worlds; ring bounds and ownership combinations |
| MustOwn across changed gameplay source families | Per-source ownership semantics | Differential comparisons to fork; native resource ownership removal |
| UI ring sources retain fork ownership semantics | UI ring variants ignore MustOwn as the fork does | Differential comparisons; all 55 sources execute live |
| District TypeTags and vocabulary | Cached tags plus district/resource vocabulary validation | Synthetic tags and real frozen database tags |
| Unique clones retain options, including DistrictModifiers/NewMethod | Copy complete authoring row before modifier generation | Dormant SQL clone fixture |
| Negative provider amounts and ten-bit encoding | Signed modifier amounts; magnitude bits; cap 1023 | Negative SQL fixture, fractional values, overflow, decreasing to zero |
| Signed details and negative loyalty icon | Shared presentation helpers | Negative loyalty text fixture and live district tooltip dispatcher |
| Overlay priority and ring-1 applicability | Object icon before source fallback; native icons retain priority | Synthetic priority/ownership/visibility/band tests; native face deduplication |
| River overlay on all six directions | Shared geometric edge matcher | Six-direction fixture; native overlay call |
| Resource visibility changes | Query current tech/civic knowledge on each evaluation | Discovery transition without cache rebuilding |
| Exact named Wonder | Completed, player-owned BuildingType presence in band, capped at one | Wrong/incomplete/foreign/out-of-band dormant fixture; no external helper |
| Property matching and absent keys | Forward key correctly; absent native values count zero | Independent correction tests; all property sources execute live |
| Unit levels in gameplay and UI | Bundled UI read bridge for native UI-only GetLevel | Mock bridge regression; live read matched UI; UI context loads on clean restart |
| Refresh after errors, incomplete/removed districts | Native indexed city district manager; reset guard even on error | Entry-point regression, injected failure/retry, completion/removal |

The 55-source registry is declared explicitly in `CSC_AdjacencySources.sql` and
checked against the evaluator registry. Inherited MAB city population, governor,
and other unrelated statistical sources are not promised by this inventory.
Unused provider types are compiled, with native effect existence checked; their
individual effects have not all been exercised in a live game.

## Important semantics

- Rings are inclusive; `MaxRings` takes precedence over `Rings`. Max zero means
  the placement tile. A positive max below min normalizes up to min.
- Resource quantities count matching plots, not deposit units. Hidden resources
  contribute only after the owning player's required technology/civic.
- Mill rows intentionally use `COLLECTION_PLAYER_DISTRICTS`: a mill elsewhere
  in the empire enables the authored bonus. Do not silently narrow to city scope.
- Negative amounts are generated in SQL. Bits store magnitude; raw/encoded
  amount properties retain sign. The signed encoded magnitude caps at 1023.
- The gameplay script refreshes relevant districts across alive major players.
  It clears removed/changed rules and writes only changed properties. City district
  managers use `GetNumDistricts()/GetDistrictByIndex()`, not `Members()`.
- UI previews evaluate without writing gameplay properties. Unit-level reads
  use a bundled InGame UI bridge because native gameplay lacks `GetLevel()`.
- The property argument forwarding, empty-key handling and stale-bit clearing
  are deliberate corrections. Do not preserve fork crashes as parity behavior.

## Tests and reproducibility

Tools are under `project/tools/adjacencies/`; fixtures under
`project/tests/adjacencies/`. Review outputs are in
`C:\Users\Shadow\Desktop\Codex\csc-adjacencies\`.

1. `capture_baseline.py` records an immutable runtime database and rule inventory.
   `mab-rules.json` pins the database SHA and fork commit.
2. `test_parity.py --reference <fork> --database <snapshot> --dependencies <test-deps>
   --output <review-folder>` reads the reference, never edits it. Result: **61 rules,
   610 bit modifiers, 55 sources, 1,465 differential comparisons passed**, plus
   independent correction, gameplay-entry and UI formatting tests. All 24 provider
   effect/collection mappings match the reference; dormant negative rules verify
   signed bits and provider-specific arguments for each provider.
3. `build_test_package.py` uses Firaxis' native manifest task and existing cooked
   art to create a gameplay/UI package. It does not perform a new art cook.
   `install_test_package.py` backs up the installed CSC first, overlays the package
   and verifies file hashes. Final package: **404 files**, no MAB dependency/helper.
4. `test_live.py --disposable-turn-1-game --output <review-folder>` explicitly
   requires a disposable fresh game. It mutates cities, districts, resources,
   ownership, rivers and mills. It compares actual native district yields against
   a separately captured baseline with CSC properties cleared, rather than only
   checking Lua counts. Result: **passed** with CSC alone, **26 base-game rules /
   260 bit modifiers**, no Ruivo tables. **180 native yield assertions** passed.
   Preview, tooltip and edge-face checks pass.
5. The saved fixture was loaded after a full process restart. Both gameplay and
   the new UI bridge initialized, with **zero runtime errors** in the clean Lua log.
   In-process reload had retained cached action metadata; restart was needed to
   discover the new UI registration. `reload-report.json` records initialization
   evidence; yield delta assertions were run before the reload.

Installed test build:
`C:\Users\Shadow\Documents\My Games\Sid Meier's Civilization VI\Mods\Civ Supply Chains\`.
Recoverable original:
`C:\Users\Shadow\Desktop\Codex\csc-adjacencies\installed-mab-backed-backup\`.
Disposable fixture save: `CSC adjacency parity 2026-10-02.Civ6Save`.
Original mod preferences are recorded in `original-mod-preferences.json` and were
restored and verified after testing (`restored-mod-preferences.txt`). Civ VI was
left at the main menu. The CSC test package remains installed. For another CSC-only
test, capture/restore preferences again; `restore_mod_preferences.py` uses the native
Modding API. Do not mistake a test's disabled optional mods for a user's preferences.

## Remaining release checks

### Tooltip regression corrected (2 October)

Henno's screenshot caught a wording regression: the initial placement line omitted
localized yield names, distance, and source nouns, and appended the count in
parentheses. CSC class labels themselves were already localized. MAB's current
preview passes signed amount, yield icon/name, count, object name and distance to
localized source templates. The bundled presentation now follows that contract
with CSC-owned text, including singular/plural resources/districts and native
localized yield names. District detail lines also include the yield name.

Localization is scoped to authored CSC gameplay: all 61 captured rules use
`SelfBonus`, with resource tags, district objects/tags, hills and river edges.
Only resource/district/terrain preview templates, river-edge and hill labels,
the shared fallback template and the tooltip heading are shipped.
Unused effect names and source labels were removed at Henno's request. The
55 evaluators and 24 provider mappings remain; unused source metadata points to
the generic fallback label. Add dedicated text when CSC first authors rules
using another family, rather than prewriting speculative localization.

`test_tooltip_text.py` compares six material/sales sentences to the read-only MAB
English templates and checks river, local terrain, wider ranges, signed yields
and detail wording. It also verifies the reduced label inventory; negative
loyalty icons and percentage encoding remain covered separately. These text
checks pass; native visual review of the
corrected package remains pending. The updated package is installed; restart Civ
VI before loading the test game to refresh Lua and localization. Gameplay parity
remains unchanged and passes. The running DX11 game's 4319 debugger endpoint did
not answer this client's queries, so no live session or mod selection was changed.

### Release checklist

Henno subsequently requested restoration of MAB's district tooltip presentation.
It now uses **Modular Adjacency Bonus:**, bullet lines using the placement source
sentence with count one, and owner names in parentheses. Building-owned lines
appear only when the local player owns the required building, as in MAB.
The replacement's extra ownership and building-requirement sentences and their
localization were removed. Native district source icons, Hills/River capitalization
and yield icon/name spacing follow MAB. The loader uses `KIND_DISTRICT` dispatch
and normalizes numeric district identifiers, matching MAB's hook.
`test_tooltip_text.py` executes MAB's detail builder and helpers read-only and
compares all five authored source families plus a mill with ownership off/on.
The comparisons pass; updated native visual review remains pending.

The subsequent live Lua log exposed a missing-table lookup in `SourceName`,
triggered by river descriptions through the civic tree, map-pin popup and world
tracker. The lookup now skips unavailable `GameInfo` tables before indexing.
The text regression uses strict native-style missing tables and exercises both
tooltip dispatch paths; the original mock's automatic empty-table creation had
hidden the failure. The corrected package is installed; confirmation in a fresh
native session is still pending. The same log also contained an unrelated
Firaxis `TunerMapPanel.lua:136` startup error.

- Human visual review of placement icons/tooltips and usual playtesting.
- Live optional-mod smoke test; the 61-rule SQL fixture already covers the
  captured optional integrations, but it does not prove every active mod combination.
- Coexistence with MAB used by unrelated mods is **not verified**. CSC currently
  imports the global `AdjacencyBonusSupport.lua`; this can replace MAB's placement
  UI support even though gameplay IDs/properties do not collide. Resolve/test that
  combination before advertising coexistence. Do not add a dependency to hide it.
- Old MAB-backed campaigns are not claimed to migrate. Test with a new game.
- Current Tailors contract validation reports pre-existing stale foundation and
  stage3 design-slice hashes (also present in Git HEAD). The migration does not
  change design approval metadata. Focused migrated SQL assertions pass foundation,
  materials/stage2 and stage3 independently.

No Workshop publication or Git commit was made by this implementation.
