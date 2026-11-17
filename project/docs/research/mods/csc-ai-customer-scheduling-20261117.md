# Customer scheduling: first native preservation test

**The new scheduler prices more city/type groups at the same cost, while
preserving the already-good Hub choice.** This is the first native gate for the
active Problem2.1 goal, not its final outcome proof. **AI-C214**.

The matched150–155 replay starts from the same verified post-restructure save.
Control uses frozen d6a9114a policy; treatment changes only the main CSC economic
adapter (implementation7ea8820a). SQL private adjacency remains1, ordinary
economic coefficients and CE b7194a8 remain fixed. Both source structural gates
pass and both sessions close exit0 with preferences restored.

| Measure | Control | Pair-first |
|---|---:|---:|
|Visited city/type group windows|68 /92|92 /92|
|World forecasts over window|264|264|
|Maximum per-player forecast count|16|16|
|Native district decisions|44|44|
|Actual choices and selected scores matching control|—|44/44|
|Publication average,151–155|2.461s|2.455s|
|Publication maximum,151–155|2.641s|2.579s|
|Lua/policy/observer failures|0|0|

The target is player3 Magdeburg city262144, Bakers2228, Hub2227. Both native
selectors choose the linked Hub at150 with294,684Q8 (1,151.109utility), submit
contract2994 and start construction151. The full native selector matrix is
captured. Other positive owned Hub cells range694.918–1,122.828utility. The
hand-picked earlier reference2080 is already a Diplomatic Quarter at150; use
the captured current matrix for actual alternatives, not that stale reference.

Group counters describe work windows, not separate construction opportunities.
No choice changed in this pilot because the control already chose the good
connection. A genuine switching case and stronger ordinary-site control remain
required before the full-game comparison campaign.

## Next short window

The control100–130 replay has completed/restored. The treatment reached130,
but its passive recorder exhausted the32-matrix limit at129. Its held game was
frozen/inactive, then closed through an identity-checked shared-controller
cleanup, exit0 with preferences restored. The test follows a baseline unconnected capital
Hub at2024, where an alternative1949 beside Bakers2022 received positive economic
offers. A second scope records Magdeburg's earlier alternatives. The treatment
uses the identical source and the adapter-only package. Thirty turns include
the turn125 decision; physical follow-through is recorded separately. The guard remains
explicitly bounded. Shared-controller ownership and passive matrix recording
continue, with no extra policy or gameplay orders. In the control, Washington
chooses Hub2024 at125 (346,627Q8) over linked1949 (337,500Q8). Both are owned,
eligible native rows. The former has5Gold adjacency; the latter1Gold and
private-yield1. A35,853Q8 (+140.05utility) economic bid is published for1949
that turn; the native final difference is9,127Q8 (35.65utility). This is a useful
stronger-ordinary-site comparison.

### What the longer window taught us

The treatment changes Boston's district comparison at108, so later empire
development diverges before Washington's125 decision. At125 the treatment still
prefers a CL rural district; these Washington choices no longer isolate a site
switch. All data remains under `pairs100-130`; `failure.json` and
`interruption-reconciled.json` distinguish failed capture from successful
cleanup. The optional matrix payload now has a128-matrix bound for short
targeted windows; normal full-game capture requests no full matrices. A safely
frozen passive fault may explicitly permit cleanup, while the observation still
fails qualification and sequence/transport faults raise.

Astra recommends Buffalo156 next: baseline repeatedly priced linked2017 against
eventual Hub winner2015 through155, then omitted it156. The current control
replays150–160, including baseline foundation158. Native matrices and CE journal
entries distinguish missing residuals from delivered bids that lose. Economic
coefficients remain unchanged.

### Opportunity and score-lineage diagnostics

`customer_placement_watch.lua` observes the actual `CustomerCandidateSets` call:
changed legal/owned/unprotected linked and ordinary footprints, removals,
reference and publication freshness. It includes singleton sets, giving a
denominator beyond the priced shortlist, without another world forecast or map
enumeration. Native CE records retain raw kind, generation and ordinal. Full
games reuse the Quarter observer's journal pass; short customer replays own the
passive read. Neither path writes policy or gameplay state. Physical events and
native selector matrices remain the later outcome records. Eligibility is at
publication; later reservations/legality are checked separately. Diagnostic
faults or truncation fail observation qualification.43 relevant checks and an
additional frozen-fault cleanup check pass.

## Storage

On Henno's instruction, ten exact duplicate CE/CSC installed-package archives
from five closed surveys/replays were rehashed against retained immutable
sources and removed. Actual recovered space is1.896GiB, leaving38.62GiB at the
check. All saves, compact/raw records, baseline inputs and the current treatment
freeze remain. The deletion ledger with manifests/keepers is
`Desktop/Codex/csc-ai-customer-scheduling-20261117/storage-retirement-20261117.json`.
Retire further closed duplicate copies as work proceeds; preserve live inputs
and required comparison baselines. This removes redundant packages, not evidence
needed to rerun the current experiments.

A second retirement removed four exact duplicate package copies from the
closed/reconciled100–130 windows: another0.758GiB recovered,38.25GiB free while
the Buffalo control runs. Its separate ledger is
`storage-retirement-windows-20261117.json`. Total recovery so far:2.654GiB.

## Remaining goal gates

Native changed near-tie site/foundation; stronger ordinary-site win; invalidation;
opportunity-based outcome instrumentation; three preselected fresh Online250
treatment games and matched current-policy comparisons. Continue beyond this
first scheduler slice wherever evidence identifies a discovery, eligibility,
continuity, acquisition or valuation blocker. After Problem2.1 is proven, use
remaining usage for Problem3 research as requested in the updated goal.
