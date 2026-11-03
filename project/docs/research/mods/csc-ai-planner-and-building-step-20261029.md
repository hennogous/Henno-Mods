# First planner and building-decision increment — 29 October 2026

This increment follows the user's direction to cover the major useful mechanisms
without attempting a complete reconstruction of the AI. It implements an offline
evidence evaluator and observes one fresh native building-versus-unit decision.
No shipping tuning, installed CSC/RH content or purchase/foundation policy changed.

## Offline evaluator

New maintained tools under `project/tools/ai_tuning/`:

- `site_evaluator.py`: pure site evidence evaluation and conservative comparisons.
- `test_site_evaluator.py` and `EVALUATOR.md`: reviewed contract and focused checks.
- `archived_site_cases.py` and its test: explicit partial archive adaptation.

Current real Production/Gold adjacency, conditional future increments, mapped
Base/Specialty supply and Service option potential remain separate. Source-bound
facts carry provenance. Unknown ownership/eligibility, access, capacity, costs or
delays do not become zero or free development credit. Future resources must
already be observed on the specified plots; occupied/conflicting plots are
withheld. Customer development requires actual adjacency and matching customer
mapping. Footprint impacts include materials relevant to other Quarter types.
A Both option is not an active Service or a complete chain.

The evaluator does not authorize purchases, place districts, score victory
strategy, compute monetary ROI or apply a universal utility coefficient. It
reports review categories and conservative dominance only when comparable facts
are complete. Geometry potential and execution readiness remain separate concepts.

All 29 focused checks pass: 21 evaluator scenarios, 5 existing comparison checks,
and 3 tests of actual archived cases. The archive uses Basic A turn100 and its
same-run database; source hashes and pointers are retained in the Desktop report.

| Actual archive case | Useful fact | Preserved limitation |
|---|---|---|
| AI1 Meroe, existing Tailors2678 | Owned, unpillaged mapped Flax/Silk improvements; observed district totals P4/G2 | District GetYield totals are not a new site's adjacency forecast; full bound supply eligibility and placement costs remain unknown. |
| AI4 Lisbon, existing Bakers2564 | Pillaged Flax/Maize Farms plus unimproved Honey; observed district totals P5/G0 | Totals cannot establish functioning material supply or a quantified repair return. |
| Original-human0 candidate Tailors2934 | Adjacent unimproved Flax2860 is already a City Center | Explicitly excluded from AI recommendations; future Farm withheld because the plot is occupied. |

All three are partial and return insufficient evidence for a new placement;
zero complete archived sites are ranked. That is a coverage limit, not a claim
that the existing chains are bad. Footprint loss denotes lost material-development
or supply opportunity; it must not imply that every resource is physically
removed. The archive itself retains Iron under an existing district.

Output: `Desktop/Codex/csc-ai-next-step-20261029/archive-review/` and
`offline-evaluator/`. The next CSC observation should capture candidate-specific
real adjacency, feasibility and cost facts directly, rather than reinterpreting
old district totals to manufacture a complete example.

## Native building exposure

One existing vanilla turn1 save was loaded once and advanced naturally to turn2,
where the predeclared useful-decision condition was met. The maximum was21; no
extension, replacement world, forced queue item, incentive treatment, production
boost or follow-on arm occurred. The maintained finite controller owned the
console; other agents worked only with source and artifacts.

Actual AI player1, Uruk city65536:

| Evidence | Observation |
|---|---|
| Native QueueNextBuild | Call1, with nested GetBestBuilding call2; sequences1 < 2 < 3 < 4; direct caller RVA3e849c |
| Best building returned | Monument, native building index0 |
| Returned building value | Signed Q8 6713 / 256 = **26.22265625** |
| Native selection in that just-closed turn1 | Scout, Default Specialization, logged value **31.2** |
| Boundary2 actual queue | Native unit index20, independently mapped to UNIT_SCOUT |
| Boundary2 Monument check | Cost30, built=false, CanProduce=true |

There was no Uruk city at initial boundary1, so the UI CanProduce read is explicitly
post-decision boundary evidence, not a measurement at the hook instant. The native
function flags were r8=1/r9=0; the observer does not reinterpret them as a new API.
The original-human player0 is not pooled with this actual-AI decision.

This establishes an ordinary building candidate reaching fresh queue competition
and a different item being selected. It does not establish the effect of changing
an incentive, the current effective favored-state sign, or the value of a CSC
producer. In particular, do not infer that a new Favored row necessarily doubles
26.22: the existing effective preference was not captured and the static sign
route does not strengthen indefinitely with repeated positive entries.

## Audit and restoration

Independent audit: `Desktop/Codex/csc-native-building-exposure-20261029/run-01/`
contains `independent-audit.json`, `.md` and `independent-process-audit.json`.
Candidate, nested call, boundary queue and raw selection records are retained in
`instrumented/exposure-2.json`, `citybuild-delta-2.csv`, building readbacks and
closed logs. The observer captured two complete pairs with no errors, drops,
reentrant skips or identity changes. Negative building returns cannot read an
unwritten output score; frozen callbacks do not continue reading game fields.

All49 source/evidence pins,12 dependencies and604 installed files match. The
source-save and XP2 DLL hashes match the pinned inputs, and exported initial1
state matches the existing oracle. Both Uruk turn1 CityBuild rows match the frozen
prior loaded baseline. There is no captured baseline Core2 endpoint, so full
endpoint parity or general observer neutrality is not claimed. Steam used the
user's current DX11 executable, whereas prior controls used DX12; no graphics
setting was overridden. The exact loaded GameCore and entry fingerprints were
verified independently of the renderer choice.

Worker, native and observer exited zero. Supported Menu/ExitOK restored the fresh
145 mod IDs,148 subscription/file entries and AutoStart=false. The sole detach
receipt is process-terminated with native_alive=false; there was no explicit
unload/detach. A final process check used executable identity and creation evidence,
not PID alone (a former worker PID had been reused by an unrelated conhost).
No study owner remains and no installed assets were swapped or rolled back.

## Next useful decision

The ordinary building selection route is exposed sufficiently to stop this
instrumentation step. The next building experiment should be one declared
preference/forecast comparison for a genuine CSC producer with a legal fresh
choice, while capturing the evaluator's missing candidate facts in the same
scheduled observations. Test current effective preference and competing values;
do not spend another broad game merely trying a larger numeric Buildings Value.
Builder tuning and strategic Service alignment remain separate investigations.

Links: [roadmap (historical)](https://github.com/hennogous/Henno-Mods/blob/819b67c/project/docs/integrations/csc-ai-roadmap.md),
[native contract observation](csc-ai-native-contract-observation-20261028.md),
[evaluator contract](../../../tools/ai_tuning/EVALUATOR.md).
