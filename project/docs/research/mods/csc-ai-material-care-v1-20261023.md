# Material care v1: first native-incentive pilot

Authorized23October after the own-first pilot and the tuning-only comparison.
Earlier work is committed/pushed; old games and monitors remain closed.

The candidate combines independently authored ideas from the read-only AI-mod
review: RH-style state-sensitive demand, AI+ Builder production-contract freedom,
and Real Strategy's distinction between job demand and Builder production.
It does not copy their code or import their general Farm/Mine preference skews.

- Existing exact-material presence40 and matching improvement-owned80 remain.
- A player-owned raw-supply signal adds160 for a Quarter's last Base,80 for its
  last Specialty, or20 for redundant supply. Only the strongest category applies
  to a physical tile, even if several Quarters share it. This private planning
  value persists through pillage and includes unfinished Quarters. It is a soft
  valuation hypothesis, not a resource reservation or replacement veto.
- A plot backlog distinguishes working, repair, legally developable, unsafe,
  inaccessible, unknown legality, and locked/illegal supplies. Missing improvements
  count only when native CanHaveImprovement and research gates pass. Repairs do
  not consume a charge. Existing total Builder charges are a conservative upper
  bound on capacity, not evidence of nearby idle units or safe paths.
- A native strategy raises Builder preference100 and improvement valuation100%
  only while missing-work count exceeds total charges, or repairs exist without
  any Builder. Existing global Builder50/improvement90 remain unchanged.
- Build City Improvement production nodes13/23 may contract a Builder in any city
  (Required City=-1). No unit is assigned, purchased, granted or moved by this code.
- Native events invalidate cached player scopes. Activations/callbacks rescan
  only Quarter neighbors and Builder units; one initial property cleanup scans
  the map. Work-state changes and material loss are retained in a compact ledger.

The first test targets225, the common comparison checkpoint. Same seeds830405/
940411, roster, Ancient/Online/Prince/Small Continents and resource pass as the
previous own-first game. Its player0 was defeated232, so225 is the declared endpoint,
not a relabeled250 pass. Keep actual AI-funds-first/shortfall-only donations,
quoted assisted assignment, legal0% foundations and light25-turn outcome captures.
No strategy-to-Service matching, forced research or direct Builder orders.

Validate Lua5.1 guards, native-schema/replay, loaded modifier attachments, tree
rows and actual runtime callbacks before calling the mechanism native-validated.
Offline success does not show that replacement/repair evaluators consume the
signals. The test must measure last-Base losses, improvement/pillage/repair state,
Builder capacity/demand, Both retention, customer buildings and eligible sales
links; payments remain unobserved. Report unsafe/locked work separately and do
not infer exact paths or repair actors from a changed endpoint.

Run evidence: Desktop/Codex/csc-material-care-v1-20261023/run-01. Installation is
an isolated512-file candidate over the preserved current510-file package. After
audit, normal exit and all Civ processes absent, restore the pretest510 package
and original144 preferences. Preserve source fixes and unrelated work.

## Startup evidence

Native turn2+ verified. Supervisor21440/worker15460/exactDX12Civ20880; all88
executed source pins unchanged. Loaded native3trait modifiers/2production tree
rows and a real material-care strategy callback were verified with zero care
errors. This is startup/plumbing proof, not decision-level preservation evidence.
Independent-startup-verification.json retains the details. Automation
csc-material-care-test is active for the human-requested15-minute updates.
Offline15actualLua5.1 guards and SQL replay/native-schema checks pass; unchanged
shared planner203/controller78 and contract167 checks passed before launch.

## Turn25 interruption and iterator correction

The first worker stopped at25 because CityDistricts has indexed GetNumDistricts/
GetDistrictByIndex, not Members. The mock had incorrectly provided Members; it
now uses the native interface. Fifteen Lua5.1 checks pass after correction.
Do not call material care active through1–24: callback errors prevented a valid
city scan. Original Lua/errors/pins remain archived. Buying/foundation receipts
are independently retained:2sites,5tiles,170Gold=76own+94fallback. The host then
powered off18:35:22Europe/Warsaw and rebooted19:13:37. No corresponding Civ
Application crash record was found. All old controller/native identities absent.

Prepare same-world resume-025-district-iterator-v2 from exact AutoSave0025
SHA256 f371f302c5837bb124c223754853d7b28e307235dd67b9d82673db7529e6c8c2.
Before advancing require complete world/gold/2physical+UI/nativeDB/512package/
5native ledgers parity. No recreated sites, new world or AI-turn replay. Inherit
120research rows through24 and observer prefixes. Cycle25 already completed with
no economic/foundation action; first new cycle26. Label25censuses as reload source.
Continuation native validation is pending until actual readbacks.

## Recovery and first post-fix observations

Exact25 recovery PASSED fullworld, treasury, both physical/UI sites, five saved
economic ledgers, nativeDB and120research prefix. Builder units/charges/positions
also match the archived25 reply; restored Builder event prefix is verified at50.
One load, no earlier AI-turn replay or recreated site; first new cycle26.
Current91pins frozen; worker3588/supervisor12264/DX12Civ8996. Native60+ observed.

Care50: zero errors,151native strategy callback invocations. Native operation
records identify actual AI UNITOPERATION_REPAIR (nativeTypes.Hash147469951) at
JoaoFlax2489turn28 and GenghisRice1619turn36, matching repair-to-working state
changes. RiceFarm remains intact50; Flax improvement is absent again50. These
prove repairs occurred, not that this candidate caused them or ensured retention.

Two supporting resources were lost despite the soft signal: Maize2563 under a
natural Tailors Quarter31, and TamarRice1353 gone35. The latter reported raw
district13 at loss, with no district remaining50; do not infer a harvest actor or
a permanent Wonder from that alone. No preservation guarantee or causal gain.
Proof: current child independent-recovery-and-care50-confirmation.json.
Continue the unchanged225 test; no midrun coefficient tuning. Generic state-read
metadata may say endpoint250; declared225/supervisor/driver loop remain authority.
