# Builder score consumer review — 28 October 2026

This additive review follows `builder-consumer-review.md`. It uses only the copied DLL (SHA256 `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`) and saved Ghidra project. All exports reopened with `-noanalysis`. No game process or live memory was accessed; no hooks, FireTuner, Frida, settings, installed assets, or gameplay edits were involved.

## Coherent link established: Units Value adds to contract priority

The prior parser result is now connected to a concrete consumer:

`AiFavoredItems.Value (column3) → Units integer accumulator4a2360 → GrandStrategic unit-indexed vector+3f8 → UnitRequestContract::Initialize3f9300 → Contract::InitializeBase3fd790 → m_priority value+C8`.

The first three stages are evidenced in the preceding report. Newly verified Windows assembly at RVA `3f9300`:

- `3f93d9`: load player `+0x670` (GrandStrategic pointer).
- `3f93e7`: load GrandStrategic `+0x3f8` (unit preference vector).
- `3f93ee`: read signed32-bit element indexed by desired unit.
- `3f93f2`: load the caller's base request priority.
- `3f93f6`: add the unit preference integer to that priority.
- `3f942c–3f9433`: pass the sum as the fifth argument to `Contract::InitializeBase`.

`InitializeBase3fd790` copies its fifth argument into archived wrapper `+0xb8`, whose scalar value is contract `+0xc8`. Base constructor `3fc9d0` explicitly names this member **m_priority**. These are recovered Windows field names plus assembly, not a conclusion inferred from the list name.

Therefore an applicable Units list row Value50 contributes **+50 integer priority units at unit-request initialization**, through the accumulated vector. If other applicable rows contribute, their integer sum is used. This is not a50% multiplier, not automatically +50 to the logged VALUE field, and not proof that a Builder wins against all competing construction. Applicability and runtime vector contents still require separate evidence.

Evidence: `builder-score-link-exports/UnitRequestContract_Initialize_Unit_3f9300.txt`, `builder-priority-exports/Contract_InitializeBase_3fd790.txt`, `builder-priority-exports/Contract_Constructor_3fc9d0.txt`.

## Request priority and present value are separate inputs

The same unit initializer separately shifts caller argument7 left8 and writes archived wrapper `+0x148`, scalar **m_extraPresentValue** at `+0x158`. Constructor `3fc9d0` names it. It does this before reading the preference vector. Thus the confirmed Units path adds to priority `+0xc8`; it does not directly add to `+0x158` in this initializer.

`BuildFromCityNode::Execute55ba40` obtains a request priority from an optional node override, `BehaviorTree::GetRequestPriority4cf390`, or tree field `+0x1e0`. Its direct call at `55be97` passes that priority as argument6 of unit initializer `3f9300`, separately from the extra present-value input. This makes the priority origin concrete for a unit BuildFromCity request. The node also passes its own signed32 field `+0x94` as required-city argument8. Unit initializer copies that into the named m_requiredCity archived wrapper `+0x1c8`, scalar `+0x1d8`. The final BehaviorTree definition/Defn2 name-to-node-field binding is still untraced; this report does not claim it.

Evidence: `builder-priority-exports/BuildFromCityNode_Execute_55ba40.txt`, especially C around its call to `3f9300` and assembly around `55be97`.

A second vector reader exists in `ValueManager::Value533190`: it adds preference*256 in a specific religious-unit branch guarded by definition flags and an inquisition check. This is not a general Builder valuation rule. Do not transfer that branch to UNIT_BUILDER merely because it reads the same vector. Evidence: `builder-score-link-exports/ValueManager_Value_UnitPreferenceCandidate_533190.txt`, C around lines250–263.

## Remaining boundary: priority versus final city queue choice

Existing `CityBuild::QueueNextBuild3e8190` compares offered contract scalar values at `+0x158` after validation/update; this pass has not proven how m_priority controls which contracts are offered, accepted, or allocated to a city before that point. The coherent result is a verified **request priority boost**, not a final score formula for every step of the scheduler. Existing `UnitRequestContract::Update3fa5e0` can refresh m_extraPresentValue using CityBuild::PresentValueOf and production turns; that remains distinct.

`Control::Manager::RecruitUnits403190` was exported, but its entry iterates existing player units, applies a callback/filter, and assigns control. It must not be treated as the city-production allocation loop without further evidence. No further recursive exports were performed after the priority link was established.

## Minimal Windows identity plan for a future read-only trace

These fields and entry points are statically verified for this DLL hash. They are a design for future observation only; no trace code or hooks were deployed.

| Object | Field | Type and evidence |
|---|---|---|
| CityBuild | `+0x90` | City pointer; used by Validate, Execute and LogContract |
| City | `+0xa8` | signed32 city ID; compared against required city by Validate3fa8e0 |
| City | `+0xd8` | signed32 owner/player ID; LogContract reads it and resolves player manager |
| Contract | `+0x110` | signed32 displayed contract ID; LogContract3f97e0 and returned handle construction |
| Contract | `+0x140` | signed32 player ID; named m_player in base constructor |
| Contract | `+0x128` | signed32 owner/control ID; named m_owner in base constructor |
| Contract | `+0xb0` | signed32 status; named m_status in base constructor |
| Contract | `+0xc8` | signed32 priority; named m_priority, Units preference addition lands here |
| Contract | `+0x158` | signed32 fixed-point extra present value,8 fractional bits; named m_extraPresentValue; production logger decodes it |
| UnitRequestContract | `+0x178` | signed32 desired unit index, default−1; named m_desiredUnit |
| UnitRequestContract | `+0x190` | signed32 desired building index, default−1; named m_desiredBuilding |
| UnitRequestContract | `+0x1a8` | signed32 desired district index, default−1; named m_desiredDistrict |
| UnitRequestContract | `+0x1c0/+0x1c4` | signed32 desired-location coordinate pair, default−9999; named m_desiredLocation |
| UnitRequestContract | `+0x1d8` | signed32 required city ID, default−1; named m_requiredCity |
| Handle | `+0/+8/+0xc` | contract pointer/player ID/contract ID; returned by InitializeBase,16-byte handle |

Minimal useful entry points:

- `UnitRequestContract::Initialize3f9300`: RCX=contract, RDX=output handle, R8D=desired unit, R9D=player. At Windows function entry, stack arguments5..9 are at `[RSP+0x28..0x48]`: control owner, base request priority, extra present-value integer, required city, keep-control flag. Ghidra mislabels some argument widths; assembly and destination scalar types govern. For safe later observation, capture arguments at entry and completed fields after return, without calling native methods.
- `UnitRequestContract::Validate3fa8e0`: RCX=contract, RDX=candidate CityBuild; return AL is acceptance. Record identity and predicate result. Required city−1 skips only the city-ID equality gate; other validation remains.
- `UnitRequestContract::Execute3f8310`: RCX=contract, RDX=CityBuild for the city-production overload. Record identity and status before/after to distinguish assignment from validation.
- `CityBuild::QueueNextBuild3e8190`: RCX=CityBuild. Useful for city identity and offered/selected contract snapshots, but its internal archived-vector wrappers should not be traversed using guessed layouts. Prefer correlating the verified Validate/Execute entry points.

Identity should be `(playerId,contractId)` plus generation/lifecycle evidence, not a raw pointer alone. Resolve desired-unit labels from a separately pinned database, not by assuming an index. City owner+ID identifies the city; do not infer location or district validity from requiredCity alone. A bounded observer should distinguish candidate city ID, required city ID, and actual executing city ID.

## Outcome and outstanding links

The missing Units Value-to-request link is closed: the accumulated integer is an additive request priority contribution. Final priority-based allocation and scheduling remain a concrete next boundary. Native lifetime, synchronization, module-base relocation and the validity of any future instrumentation still need runtime preparation; no such instrumentation is part of this static pass. All requested artifacts are local Desktop output and gameplay sources are unchanged.

## Durable context

This supersedes the unresolved Value-to-request link in the [earlier Units consumer review](csc-ai-native-builder-consumers-20261028.md). The subsequent priority-to-allocation path remains unresolved. Export-relative paths above resolve under `Desktop/Codex/csc-native-ai-analysis-20261028`. See [the source audit](csc-ai-profile-source-audit-20261028.md) and [roadmap](../../integrations/csc-ai-roadmap.md). No runtime test of these new fields was performed by this static investigation.

## Subsequent bounded scheduler review

The copied-image follow-up (`scheduler-priority-review.md/json` under the same
Desktop analysis root) connects `SubmitContract403c70` through player signal
`+0x798/+0x270` to the registered `CityBuild::ReceiveContract3e9500` callback.
The receiver validates the candidate city, retains an accepted handle and uses
`+0x158` in a subsequent queue-clear comparison. These functions do not directly
read the separate priority field `+0xc8`. Signal delivery and acceptance do not
establish exclusive allocation or a highest-priority winner.

A direct priority consumer was found in `CityBuild::OddsOfBuilding3e7c80`:
existing production progress returns Q8 256; inability to train returns zero;
otherwise it takes the maximum nonnegative priority among matching unit contracts
and encodes `0.2f * priority + 0.5f` as Q8. Both constants were checked in the
copied PE. There is no 0..1 clamp in this function, so its name is insufficient
to call the result a probability. The observed direct caller is
`AdjustUnitProductionEffect::Analyze464600`; its downstream meaning was not
expanded in this bounded pass. This is not the city queue's final score formula.

The remaining scheduling boundary is the registered callbacks in the control
manager's phase/signal machinery: whether and how they sort or gate contracts by
priority before offering them to cities. Five small additional exports did not
resolve that edge. Static findings neither prove runtime availability nor justify
raising Builder weights. No native interaction or gameplay change accompanied
this follow-up.

## Calibration context, not a tuning conclusion

Shipped `Base/Assets/Gameplay/Data/Leaders.xml` binds UnitPriorityBoosts to the
major-civilization trait with System=Units and includes a Settler Value=1 row.
CSC Basic explicitly sets Builder Value=50. This comparison makes the units of
the knob worth calibrating; it is not proof that 50 is excessive, beneficial or
optimal, since request origin, other active lists and downstream consumers matter.
The current vanilla observation control does not load CSC Basic. A subsequent
vanilla field trace cannot certify the CSC +50 intervention merely because it
successfully reads a Builder contract. Keep native request priority and the
logged present value separate in both reports and future tests.

## Subsequent runtime observation

The [separate short native trace](csc-ai-native-contract-observation-20261028.md)
observed the Settler's priority addition, Builder priority/value separation and
required-city binding in actual AI requests. CSC was disabled, so it does not
verify the CSC +50 intervention. The static-only claims above retain their scope;
the runtime report supplies its own controls, missing-event limits and receipts.
