# Chain coordination — first offline integration

Pure standard-library Python over the maintained `site_evaluator`; no game, network, file writes, ranking, backend or action authority. This is a staged synthetic contract, not a native outcome or a complete archived-site ranking. The existing evaluator remains responsible for the site evidence envelope and its own unknown/rejection semantics.

## Snapshot schema

`coordinate(snapshot)` takes a dictionary with:

- `source`: nonempty snapshot provenance; `player`, `turn`: nonnegative integers, never booleans. All site and chain identities must match both, so a stale or mixed-player record fails closed.
- `mapping`: the existing evaluator's validated enabled mapping envelope (`validated` sourced true, `snapshot`, `quarter_classes`, `TypeTags`, `Improvement_ValidResources`). Its validated status is a caller assertion; this draft does not validate the original database extraction.
- `production_capacity`: sourced fact `{value: nonnegative finite number or None, source: nonempty string}`. None means unknown, not zero. Capacity is an opaque observation with units and allocation comparability unestablished; it is recorded but never spent or used to make a preference.
- `sites`: existing evaluator inputs. Identity requires sourced `player`, `city`, `turn`, `plot` and a nonempty `quarter`. Future entries have nonnegative integer `plot`, `kind` of `customer` or `material`, and `source`; all evaluator fields remain as defined in `EVALUATOR.md`. Site identity is `(city, quarter, plot)` within the snapshot; duplicates fail. An evaluator can return insufficient evidence without invalidating the snapshot.
- `chains`: explicit records with the same identity and quarter, sourced facts `state` (`complete`, `unfinished`, `pillaged`), `request_state` (`no_request`, `rejected`, `accepted_waiting`, `selected`, `unknown`), and `remaining_production` (nonnegative finite number or None). `material_dependencies` is a list of unique `{plot: integer, native_bound: {value: true, source: ...}}`; its provenance must establish the dependency in that player/city/chain context. An empty list is an explicit supplied inventory, not an inferred absence; capture completeness remains the caller's responsibility.
- Optional `customer_sharing`: pair-specific `{sites: [{city, quarter, plot}, {city, quarter, plot}], plot: customer_plot, shareable: sourced boolean}`. Both sites must contain that customer plan. Missing proof yields unresolved sharing; true and false are explicitly evidenced. This proof is input evidence, not validated native legality.

Site and chain numeric identities, dependencies, capacity and remaining production reject numeric booleans and invalid numbers. Required provenance and enums fail closed. All site evaluator facts retain its own validation and unknowns. The source must actually identify a current snapshot; strings are provenance pointers, not independent proof of freshness. If a future input comes from a different turn, the caller must not attach it to the current site.

## Output and semantics

Sorted `site_evidence` holds `evaluate_site` output and `chains` retains chain facts. `options` marks infeasible starts ineligible, insufficient-evidence starts deferred, and other starts for review; it carries evaluator reasons and a review flag. Finish/repair possibilities are review only. `site_relationships` gives symmetric pair relationships in canonical site order: exact footprint and competing footprint/material claims are incompatible; customer/customer sharing is unresolved without pair-specific evidence, and shared future material remains unresolved. Every relation involving future plans carries their evaluator statuses and a feasibility flag. A withheld plan makes the relationship conditional and unresolved, including when a sharing proof exists; the conditional status is preserved separately. Sharing proof does not independently establish plan feasibility. These are plot claims, not estimates of value or future execution. `chain_dependencies` reports a candidate footprint on a declared dependent material as a tradeoff with unknown loss value, never an unconditional ban. Unknown capacity leaves allocation and preference deferred, as does the draft generally. `action_authorization` is always false. Outputs and inputs are independent copies; no cost conversions, automatic budgets, quotas or finish-first rule exist.

The module deliberately does not resolve sharing of material dependencies between chains, assess whether capacity is adequate, calculate resource loss yields, rank alternatives, validate a snapshot against a live engine, or call a backend. Claims are descriptive, including future plans the evaluator may separately withhold; their presence does not make a future plan feasible. Review those evaluator statuses before interpreting relationships.

## Run focused tests on Shadow

From this folder in PowerShell:

```powershell
$env:PYTHONPATH='C:/Users/Shadow/Documents/Firaxis ModBuddy/Civilization VI/Henno Mods/project/tools/ai_tuning'
python -B -X utf8 -m unittest -v test_chain_coordinator
```

Tests import the existing synthetic fixture from `test_site_evaluator`, not archived game data. They cover conflicting sites, cross-chain material loss, accepted-waiting versus a high-band start with unknown capacity, customer sharing, invalid identity/evidence/enums, and input/output isolation.


## Integration status and research boundary

`chain_coordinator.py` is the first reusable coordination layer over the existing
site evaluator. It integrates candidate facts, existing chains, production/request
state and cross-site claims in one review result. It performs no selection,
ranking, spending, native calls or file writes. It is not connected to the live
Lua host. Missing current candidate adjacency, supply eligibility, credible
development/capacity and comparative costs still block a justified live policy;
the archived cases remain incomplete. This module must not be presented as an
implemented improvement in native AI behavior.

The [closed foundation observation](../../docs/research/mods/csc-ai-foundation-observation-20261029.md)
motivates the accepted-waiting/request distinction and cross-chain material
conflict review. It supplies no tuned capacity threshold, net-benefit coefficient
or unconditional finish-first/preservation rule. Producer forecast calibration
is a separate native experiment. Candidate starts overlapping an existing chain
footprint are deferred pending reconciliation; no replacement policy is inferred.

Nine focused synthetic tests establish the evidence handling and constraints,
not site quality or native efficacy. Run alongside existing evaluator tests from
this directory with the bundled Python:

```text
python -B -X utf8 -m unittest -v test_chain_coordinator test_site_evaluator test_offline_cases
```
