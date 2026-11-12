# CE ownership-prerequisite integration

Active **1.5**: reproduce the paid Quarter-footprint workflow using reusable
main CSC and CE code, without the external acknowledgement writer. The separate
supplier acquisition/improvement route remains open.

The [preceding controlled experiment](csc-ai-nuremberg-acquisition-20261112.md)
isolated the missing acknowledgement: native Economic paid 40 Gold and annexed
the intended site, but its purchase contract stayed accepted and waiting. A
tracked state transition released normal reservation/request/construction.

## Implementation and delivery

- CE fork branch `codex/ce-purchase-ownership-ack`, commit
  `d8df45989165d243e66498cd8b58ee44125dde53`, based on reviewed `d8df47d`.
  Checkout: `Desktop/Codex/csc-gamecore-hotfix-20261106/ce-purchase-ownership-review`.
- Generic API: `CE_AIDistrictPurchaseCompletionStage(player,city,district)`,
  `...Status()` and `...Receipt(version,player,city,district)`. Scopes share the
  existing Begin/Allow/Commit lifetime; duplicate keys coalesce and invalid
  staging poisons the packet. The exact receipt is not limited to first samples.
- Main CSC's publisher enumerates live original-AI cities and supported Quarter
  profiles, excluding founded Quarters. The bridge validates all numeric scopes
  before staging. There are no test-city/plot/contract IDs in production policy.
- Unsupported optional API leaves ordinary score guidance available. Scope
  overflow drops the complete supplemental batch and reports every dropped row.
  Exact previous-scope receipts are queried only after native status reports
  an acknowledgement, before the next commit retires those counters.

CE follows its existing C++/Runtime hook and HKS conventions. Its typed six-
argument `UpdateContract` wrapper forwards every argument and calls the original
once. It filters the known purchase-contract class/state, validates the executing
tree trigger and bounded root identity, and checks actual owner and purchase-
city ID against that city. It acknowledges an already-fulfilled prerequisite
through native archive-aware assignment, then leaves the original decorator
responsible for progression and cleanup. It supplies no funds, scores, purchase,
reservation or construction command. Cultural acquisition can also fulfil
ownership, so an acknowledgement receipt is not a payment receipt.

Every new native address/offset is named in `native/purchase_ownership_completion.inl`.
The file and native README record ABI, binary scope, pure getter paths and
failure behavior. Native callbacks retain no game pointers across calls or loads.
The short tracked leaf assignment is explicitly documented as the narrow lock
exception; original functions and pure lookups execute outside the policy lock.

WildW develop was rechecked before the live test and remains
`2986a746b396eb93aad14f9afffb043a09c2c489`. No PR has been created.

## Offline checks and build identity

Supported MSVC solution/project build uses the existing dependency environment,
not the retired alternate compiler route. Build 02 completed with zero errors;
reported warnings are from the existing project/header declarations. DLL:
`73eed1070742ba9a8bb9ba722a09b0229aebcc35c7423e81b7e8f075928d1eed`.
Logs: `Desktop/Codex/csc-ce-develop-port-20261105/environment/outputs/ownership-api-20261112-02`.

The isolated host passes **114 native checks**, four shared-hook failure-path
checks and the instruction-call byte/delivery/restoration check. New C++ tests
exercise the actual predicate with typed fake native leaves: disabled or missing
scope, unowned/other-city target, invalid control, tracked success/deduplication,
exact/stale receipts, invalid staging and context retirement. JS diagnostic tests
are not substituted for these C++ tests.

Four new Lua tests cover missing/unready capability, live city/profile fanout,
receipt timing after foundation, complete overflow reporting and fail-closed
rejection. Five existing publisher tests and 13 source/fixture guards pass.
Astra's review caught an empty-table fallback bug; both bridge and publisher
are corrected, and the absent-API case is now a regression fixture.

## First integrated replay

`nuremberg-ownership-integrated-01` closes normally after 202–216, using the same
qualified released save as the earlier diagnostic. Main source files are staged
without probe policy changes. CE is the new supported build. The Frida tools are
read-only: `repairOwnedPurchase` is false and no external acknowledgement runs.

Preflight reports ready/faults **1/0**, 45 scopes and the exact target scope
staged. Main's receipt at 204/version 2 records player 3 / city 458758 / district
36, contract 4316 / plot 788, considered=owned=acknowledged=1, state **3→7**.
Physical snapshots show the Bakers foundation at 209 and independently report
**IsComplete=true from 213**, with no pillage. This supplies the physical flag
missing from the earlier diagnostic's native COMPLETED row.

The sealed [fresh-run audit](csc-ce-ownership-completion-20261112-integrated.json)
records exact agreement for 38 purchase and 17 selector records, no native faults
or pending pairs, one linked 40-Gold debit and verified terminal cleanup. Only
the CE DLL and two main CSC Lua files differ from the unchanged baseline; the
first native selection, including all 36 Bakers site rows, is identical.

## Retained-plan reload

`nuremberg-ownership-reload-01` loads the verified inactive turn-205 source
`6977d48d856ea1f08f8f1876371898495a3e182d9b8d7cffbee0de09fdab1a03`.
The site is already owned by the intended city and empty. The retained purchase
contract 4316 predates this process: no fresh creation-registry entry authorizes
the acknowledgement. Main CSC stages 46 dynamically derived scopes before AI
activation; its exact receipt at 206/version 1 records contract 4316, plot 788,
considered=owned=acknowledged=1 and state 3→7. CE reconstructs the relevant
identity from the live native tree and current ownership checks. A null cached
handle is left to the original resolver; no cross-load pointer cache is used.

The ordinary request 4408 is submitted at 205, selected at 208 and logged
COMPLETED at 212. Physical foundation appears at 209 and IsComplete=true from
213. The 13 purchase and 12 selector records exactly match their journals;
faults are null, all pending counters are zero, and cleanup is verified.
There is **no new payment for 788**: this is recovery of the already-paid plan,
not another acquisition. Other purchases in this replay are separate events.
The [reload audit](csc-ce-ownership-completion-20261112-reload.json) pins the
terminal artifacts and paused endpoint `43f3aaaa…e62cc10`.

## Scope

Astra independently audited both terminal runs and source/package identities.
**The Quarter-footprint part of 1.5 meets levels 1–3. Problem 1.6 also meets
levels 1–3 at this representative scope.** AI-C160 supplies the causal Quarter
preference; AI-C161 isolates the downstream acknowledgement effect, reproduced
here by generic CE and dynamic main-CSC policy through physical completion.

**1.5 remains open for separate supplier acquisition and improvement.** No
Service, universal purchase reliability or overlapping-buyer solution is
claimed. The agreed footprint acceptance does not add a BUY-versus-NOT-BUY gate;
the earlier promotion-necessity negative remains documented. Broader seeds and
configurations remain separate qualification. See [AI-C162](../../civ6-ai/findings.md#ai-c162).
