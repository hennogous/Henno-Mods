# Customer-aware AI planner v2 — 1 November 2026

The planner is implemented in canonical source and verified offline. A [native pilot](csc-ai-customer-aware-planner-v2-native-20261101.md) is now underway, with actual2 independently verified; naturally eligible planner behavior and benefit remain unproven. This advances the [supply-chain objective](../../integrations/csc-ai-objectives.md);
it does not establish functioning chains throughout Basic and RH games.

Root promoted exactly four existing source files, two portable tests and one
small retrospective evidence fixture after confirming no native/controller owner.
The canonical copies passed **157 checks, zero failures/errors/skips**. Seven
independent bound-intent checks and an all-477-table SQL comparison also passed.
The reusable package helper separately passed its ten previous and five new tests.
Installed CSC, saved preferences, RH Workshop files and unrelated art were not
changed by this source promotion. No native game, automation, commit or push was
part of it. Prior completed-game pins describe archived executed code, not this
later source revision.

The declaration is one combined Both-or-real-P/G>=4 policy with a concrete customer
path. Astra's additional review required bounded named prerequisites rather than
requiring future buildings to exist already. That exposed a specific Bakers issue:
the unbuilt Quarter has not yet granted its River Access flag. The model now
credits that automatic flag conditionally from the actual site/grant contract.

The experimental planner remains private opt-in. Existing default and version1
paths are preserved except the declared shared removal of the generic BONUS12 cue.
This cue rewards wrong-industry resources; removal is a hypothesis about improved
native choices, not an observed benefit. The cap, direct Granary treatment and
Builder/economic policies are held fixed for the next comparison.

## Exact source scope

| Path | SHA256 |
|---|---|
| `Civ Supply Chains/Data/CSC_AI.sql` | `368be981c78fb69dbd1b6dece70bc02bdb76a2e6e7c9f73133fae2a6935499d7` |
| `Civ Supply Chains/Lua_UI/AI/CSC_AI_Assistance.lua` | `d1b02035e7f32de4044e3fe0c97ecd318dd0182d5683163e05bcf5fc9280c065` |
| `Civ Supply Chains/Lua_UI/AI/CSC_AI_OpportunityPolicy.lua` | `07d8d491b6be449d2281c8433e4428296f4c71795779f0123b9627e5c0f76abc` |
| `Civ Supply Chains/Lua_UI/AI/CSC_AI_AssistanceUI.lua` | `fb9f6752536d96605e255cd35fcebb68bc946f561936572073540ddf45f0603c` |

Tests: `project/tools/ai_tuning/test_customer_planner_v2.py`,
`test_runtime_customer_v2.py`, and the small source-hashed geometry fixture
`fixtures/customer_planner_v2_actual150.json`. The 157-check local run supplies
the explicit historical DB/shadow/before-source controls; missing optional
controls are skipped honestly, not compared to the implementation itself.

The shared SQL replay was compared across all 477 tables of the previous actual
candidate DB: exactly one `Adjacency_YieldChanges` row and two
`District_Adjacencies` rows for `CSC_AI_BONUS_RESOURCE` disappear. No other table
changes, a second replay is idempotent, and the source DB remains unchanged.

The prospective native test uses these four replacements plus the unchanged
previous direct-Granary append in CSC's RH support SQL: five temporary installation
deltas, restored from that test's exact backups. This does not authorize editing
RH Workshop code or copying an old package over newer art.

Next: review/freeze the driver and source pins, then the native source1/first
advance and first natural v2 evidence gates. Ordinary missing prerequisites at
the review horizon must support a same-worker review/continuation; they are not
a controller failure requiring a reload. Binding/evidence errors must preserve
the current world and stop further advancement. Actual customer conversion,
retention, native placements, costs and tradeoffs still need measurement.

Local raw packet and receipts are under
`H/customer-aware-planner-v2-20261101` (`promotion-manifest.json`,
`canonical-promotion.json`, `canonical-verification.json`, `root-policy-review.json`,
`root-sql-scope-review.json`, `driver/helper-canonical-verification.json`). The
H Lua extracts are readable review aids; canonical Policy/UI contain the actual
single implementations. No master Ghidra/DLL/DB archive clone was created.

## Behavior

The private opt-in remains `Game:SetProperty('CSC_AI_SELECTIVE_SCREEN_V1',
{version=2})`. The existing state property stays
`CSC_AI_SELECTIVE_SCREEN_STATE_V1`, state version 1. Nil config with no state
uses the legacy path. Version 1 retains its Both-only screen. Removed or malformed
config after activation cannot erase commitments or resume unrestricted starts;
pending financial reconciliation remains independent.

Version 2 catalogs typed Both and Base-only intents. Every intent needs credible
mapped Base and an exact registry Stage2 or Stage3 customer family. Both cannot
waive customer evidence. Base-only additionally needs estimated real Production
plus Gold at least 4, current or explicitly conditional projected; private planning
yields never fill that threshold. Customer readiness is actual functioning building,
existing complete/functioning district with a named missing-building branch, or a
specific currently native-legal future district plot. A selected customer footprint,
producer, transaction/stage and Base/Spec identity are bound before mutation and
revalidated fresh; the host cannot silently switch them on a later purchase.

The shared Basic/RH SQL removes only the BONUS12 definition and its attachments,
including replay cleanup. This declared shared change applies even without v2.
River4, private40, customer10/reverse30, real adjacency rules, Granary treatment,
Builder policy, economic limits and all native zero-percent foundation readbacks
remain unchanged. No new modinfo, content entry, action or module registration is
needed: Policy contains the authoritative pure implementation, and the existing UI
payload contains the read-only adapter. The separate H Lua extracts are review aids
and are not promotion targets.

The cap, physical Stage2-or-Stage3 release, repair/maintenance, failed-sunk history,
one-shot receipts, pending tokens, cooldowns, reserves and site/rolling300 limits
remain. Typed records can contain one material only for a validated Base-only
intent. An operational record stops reserving an old future customer plot against
compatible actual-customer reuse. Its actual physical qualifying paths remain
distinct from the original promise; a different actual path may legitimately
release the cap. This is structural evidence, not payment or net-benefit proof.

## Read interfaces and capture fields

`U.ReadPlannerV2(pid,cid,key,source,base,spec,originalAI,fresh)` uses scalar arguments
and returns a packet, or `nil,error`. `spec=nil` represents Base-only. It issues no
commands or writes. Original AI evidence comes from the host's persisted original
role mask; it is not inferred from a temporary autoplay flag.

The packet includes `turn`, `identity`, `base`, optional `spec`, `materials`,
`both_credible`, source legality/CanProduce/conflict fields, `customer_paths`,
`quality.current`, `unknown_secondary_costs`, `value_scope`, and explicit
`native_context_validation='PENDING bounded native preflight'`. Each customer path
has the exact registry identity, readiness, source producer, customer city/plot,
district/building, current physical facts, named construction/unlock conditions,
and its own current/projected real-component model. Conditional producer assumptions
are named under `quality.assumptions.producer_steps` and `horizon`.

`M.InspectPlannerV2(c)` returns detached packet/result/error and
`action_authorization=false`. It does not persist natural-callback evidence.
`M.InspectScreen(pid)` keeps the existing lifecycle interface and adds:

- `planner_version=2` while explicitly active, including empty source1.
- `planner_diagnostics.evidence_error_count`: cumulative essential evidence/binding
  failures, with bounded `first_error` and `last_error` (`turn,site,reason`).
- Detached `first_packet` and `first_candidate` snapshots from natural AI callbacks:
  capture turn, identity/status/kind, selected customer, current/projected real
  components, assumptions, conditional status and limitations. No inspection can
  manufacture these observations.
- `last_planner_discovery`: per-callback candidates, rejection counts, last missing
  fact and errors. At most 16 distinct reason buckets plus a capped remainder;
  error strings are limited to 300 characters.
- Records retain `intent_version`, compact `v2_intent`, `admission`,
  `first_admission`, `planned_customer_fulfilled`, and fresh physical `facts`.
  Admission values have `captured_turn`, an ADMISSION-TIME `value_scope` and named
  `horizon`; they are not relabelled as current checkpoint yields.

Before any natural callback, active v2 inspection supplies zero evidence-error
count and `initialization='no natural callbacks observed'`, without a write or
candidate claim. A native driver must distinguish ordinary declines from evidence
errors, hold on the latter, and wait for a real natural packet to validate bindings.

## Native facts and limits

The adapter initializes the adjacency core once in its own UI context and requires
nonempty Quarter rules. It uses UI district `Members()` and never the Gameplay-only
district-location getter or the unavailable UI building-location getter. CityCenter
functioning follows the existing normalization while retaining raw pillage.

The model ports the durable attachment-instance projection: complete named source
inventories count functioning source buildings per attachment, per city/empire,
instead of boolean mill presence. Unsupported collections/eligibility/amounts stay
unknown. No failed native unbuilt Plot-preview getter is used. Its eleven captured
existing controls match; an unbuilt total native yield getter remains unvalidated.

Future building credit follows one bounded exact database prerequisite branch
(depth limit 8), with required unlocks already owned or exactly the currently
selected technology/civic. There is no arbitrary future tree or completion date.
The Bakers RiverAccess/NoRiverAccess assumption comes from the actual site IsRiver
and SQL grant/requirement contract, with mutually exclusive buildings checked.
Missing flags are conditional engine grants, never Lua grants. Missing buildings
are construction steps; existing pillaged buildings are labelled repair with
unknown repair cost, not priced as a new build. Trait-restricted future buildings
are conservatively deferred without a recipient proof.

Future NEW customer districts in this first prototype require current native plot
potential, current unlock/capacity, CanProduce, exact operation target and
CanStartOperation separately. CanHaveDistrict receives exactly districtIndex,
player and city; there is no fourth future flag. Capacity uses the shipped zoned
and allowed population-requiring district getters, including a planned Quarter
slot only when required and in the same city (both current Quarters require 0).
Locked/unknown district permission is deferred, not declared permanently illegal.
Generic customer-family live contrast is still untested. Future customer plots are
currently owned clear plots; customer land purchases and removals are not added.
Building construction burdens may be conditional even where current building
CanProduce would be false because a named prerequisite is absent; that future
building queue permission is explicitly unobserved.

Future district type commitments withhold credit. No native alternative score API
was invented: absent scores are explicitly UNAVAILABLE/unverified, never zero.
The pure policy rejects a supplied known better alternative, but the live adapter
does not claim an unchosen plot is native-best. Future footprints are planner
bookkeeping, with existing/committed supply protected; they make no native
reservation, purchase or district order. Secondary travel, worker commitment and
opportunity costs remain unknown rather than universally vetoing all plans.

Callback caching shares registry definitions, named census, source previews,
district lookup and future exact facts within the existing UI scope only. Discovery
bypasses the old 25-turn map-only catalog cache. Every actual admission bypasses UI
planning caches; CSC mutations use the existing Invalidate. This is no new event,
world callback or transport roundtrip. Work remains bounded by owned cities, the
existing radius3 Quarter sources, their adjacent material combinations and six
customer neighbors. Fresh action checks can repeat a full named player census;
no runtime timing or full150 performance claim is made yet.

## Verification

`verification.json`: 157 tests, zero failures/errors/skips. These are the existing
119 route/economics/profile/UI/pilot/lifecycle regressions, 11 pure/model/SQL checks,
and 27 runtime/archive checks. `root-policy-review.json`: the independent seven
Root checks pass, including fulfilled-reservation reuse. Root's separate all-table
SQL receipt verifies only the expected BONUS definition/attachments change.

The six legacy NativeSchemaSQL fixtures expect a pre-RH database and fail their
setup if run against the actual RH database (RHAITags already exists). That initial
attempt is retained separately. They are excluded from the same 119 prior
regression groups; the new SQL test uses the actual native schema read-only with
an in-memory copy and verifies idempotence/non-BONUS equality. No native DB is
copied to H or changed.

Portable tests default to canonical Lua under `Civ Supply Chains/Lua_UI/AI` and
SQL under `Data`; `CSC_V2_SOURCE_DIR` explicitly selects H. The receipt/differential
test requires `CSC_V2_BEFORE_DIR`, honestly skipping without an archive. Optional
accepted shadow/native DB controls also skip explicitly when paths are absent.
All these paths were supplied for the zero-skip local run. The evidence fixture
has portable selected rows plus original source paths/hashes, not a live dependency
on Desktop captures. The runtime fixture intentionally omits the Gameplay-only UI
getter.

The six archived150 cases are retrospective geometry controls. The four failed
assisted sites cannot obtain customer credit from Both alone. Choir's adjacent
CityCenter2710/missing Granary remains an existing-district path with missing
unlock/queue evidence in that geometry fixture, not proof that a Granary could
never be built. The inland reference Temple paths are recognized without Harbor
or Stage2 customer. These terminal observations do not reconstruct T1/T40 legality,
prove a payment, isolate efficacy, or show the new planner will succeed in a game.

Run the H receipt harness with bundled Python, the existing Lua51 PYTHONPATH,
`CSC_V2_REPO_ROOT`, `CSC_V2_NATIVE_DATABASE`, and `CSC_V2_SHADOW_CAPTURE` explicitly
set. Root source promotion passed as described above. Native preflight/test remains a separate gate.
