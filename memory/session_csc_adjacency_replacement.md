# CSC adjacency replacement — 2 October 2026

User authorized building the first version after the source audit. Scope is current
Bakers/Tailors plus all fork additions/fixes and the self-contained exact-Wonder
matcher. Future Quarter design docs are stale/speculative; do not implement them.

Current implementation/status authority:
`project/docs/integrations/csc-adjacencies.md`.
Pre-migration source audit: `project/docs/integrations/mab-independence-plan.md`.

- New engine in `Civ Supply Chains/Lua_UI/Adjacencies/`. No external dependency,
  MAB globals/events or patch-helper step. Old Ruivo folder remains unregistered.
- New package generated with Firaxis manifest task; reuses existing cooked art.
  Installed CSC test build and complete original backup described in durable doc.
- Offline: 61 rules, 610 modifier bits, 55 source registry, 1,465 comparisons pass.
- Live CSC-only: 26 rules/260 modifiers, no Ruivo tables. Native yield deltas,
  BASE/SPEC, customer returns, ownership removal, remote mill gate/removal, all
  source evaluator calls, preview, dispatcher tooltip and edge dedup pass.
- Fixed actual city district manager API (indexed, not Members). Guard resets
  after errors. Native GetProperty can return no values; assign before tonumber.
- Unit GetExperience():GetLevel exists only in UI; use bundled read-only bridge
  through ExposedMembers.CSC_Adjacency. Gameplay alone writes properties.
- Firaxis discovers ToolTipLoader_* on the loading screen too. Guard absent
  gameplay DefenseTypes / custom table before including presentation.
- Clean restart/reload initialization passed: 26 rules initialized, UI bridge
  context loaded, zero Runtime Error entries in captured clean Lua log. Native
  yield tests (180 assertions) were completed before reload. Native actions cache across
  an in-process load; full restart required to discover newly registered UI context.
  Tuner can expose a listener on 4319 after reload; this observed endpoint did not
  answer LSQ, so do not assume it is a working replacement for 4318. --port added.
- Original enabled mods restored and verified with `restore_mod_preferences.py`;
  game left at main menu. Snapshot is `Desktop/Codex/csc-adjacencies/original-mod-preferences.json`.
  The new CSC test package remains installed; original package backup is intact.
- Original fork is read-only at d852b8466cf7152f4fd76cacec5fa8c2084d7c0a; no
  unpushed commits on checked-out integration branch. Do not claim PR currentstatus.
- Tailors foundation/stage3 gate hashes are stale in unchanged Git HEAD too.
  Migrated focused SQL assertions pass all three existing phases. Approval/design
  metadata untouched. Full contract validator fails only those pre-existing hashes.
- MAB coexistence UI not verified: global AdjacencyBonusSupport.lua import can
  override unrelated MAB preview support. No promises of old-save migration.
- No Git commit/publish. Ruivo and Zegangani credited in manifest/source/docs.

Installed CSC skill references still describing MAB are historical for this task;
current AGENTS.md and durable implementation doc take precedence.

## Tooltip regression follow-up

Henno's screenshot showed icon/+amount without localized yield names, generic
"from Source (count)" lines. User explicitly asked to inspect current MAB. Its
preview uses five localized arguments: signed amount, yield icon/name, count,
object, distance; source templates pluralize their nouns and use "the" for one.
Restored this contract in own Presentation and localization, including provider
names and singular/plural generic source labels. Six material/sales text cases
match MAB's English templates; river/local/range/negative/percent/detail cases and
full gameplay parity pass. Rebuilt/installed package. User must restart Civ for
the new text/Lua; did not disrupt the active DX11 test game or mod preferences.
DX11 PID11460 listened on4319 but no LSQ response; no live rendering verification
claimed. Future tooltip tests must assert actual wording, not merely nonempty text.

Henno narrowed localization to effects/tooltips actually authored by CSC. All
61 frozen rules use SelfBonus and five source families (resource tag, district
tag, specific district, hills, river edges). Removed unused provider labels,
named-source templates and generated source/terrain labels. Kept shared
formatting and native yield/entity names, river edges and hills; the full
evaluator/provider capabilities remain. Generator uses the generic fallback
for unused source metadata. Add dedicated text alongside future authored rules.

Latest user Lua.log check: 3 SourceName crashes at Presentation.lua:64 in
civic-tree, map-pin and world-tracker district tooltip paths; indexing an absent
GameInfo table. Fixed by guarding each table lookup. Tooltip regression now
disables the world mock's auto-empty-table behavior, removes ResourceClasses,
and exercises river descriptions and both native tooltip dispatch wrappers.
Passes. Fixed package installed; fresh native confirmation pending. Gameplay
initialized 61 rules in the reported log; separate TunerMapPanel.lua:136 error
is stock Firaxis code. Do not claim this old log is clean after installing files.

Henno clarified the tooltip request: restore MAB's behavior for now, rather than
remove its existing section. Restored heading Modular Adjacency Bonus:, bullet
placement-format source sentences with count one, parenthesized owner names,
and local-player ownership gating (mill rows hidden until owned). Removed our
extra MustOwn/Requires explanatory sentences and unused localization. Uses
KIND_DISTRICT dispatch and numeric ID normalization like MAB. Native district
source icons, Hills/River capitalization and yield icon/name spacing restored.
Direct read-only execution of MAB's actual detail builder/helpers now compares
all five CSC source families plus mill ownership false/true; passes. Native
visual confirmation of the restored format remains pending.

12 October 2026: Henno reversed the earlier static tooltip presentation decision.
Remove the MAB-style Modular Adjacency Bonus appendix because authored district
descriptions already explain the effects better. Deleted/unregistered the loader,
removed Description/RuleDescriptions and the heading localization. Keep placement
preview and edge overlays. Updated wiring helper and existing text/live fixtures
so they cannot silently reintroduce the block. Installed only the affected
Lua/text plus removal of the loader from the existing manifest (no art rebuild).
Focused placement text and manifest/localization checks pass. Workspace-wide
diff whitespace check reports unrelated existing art/SQL whitespace; scoped
checks are used for this change.
