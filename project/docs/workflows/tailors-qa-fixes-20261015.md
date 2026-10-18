# Tailors QA fixes and cross-Quarter audit — 15 October 2026

> **Correction from Henno, 15 October:** the material-return issues were false
> reports. Material returns work; the older unresolved-material conclusions below
> are superseded and must not be used as limitations of the AI baseline.

> **Terrain qualification, 15 October:** Henno observed ocean-based test setups.
> The forced-terrain fixtures did not establish legal placement. Their
> placement-dependent results, including apparent passes, must be treated as
> diagnostic observations rather than gameplay acceptance. This also prevents
> concluding that material-return failures are gameplay defects. The saved-cache
> normalization test and static modifier arithmetic are independent evidence.
> Terrain-aware planner/guards are now drafted but untested. Automated reruns
> are deferred while Henno performs manual tests.


Follow-up to [the original five-issue report](tailors-qa-report-20261015.md).
The user authorized fixes, regression testing, and contract/validator updates.
The five source corrections are present. Native acceptance is partial: the
ownership, saved-notification-cache and customer-purchase regressions pass; material returns remain
unresolved. See the native results below before treating the work as complete.

| Issue | When it occurs | Source correction |
|---|---|---|
| CSC-QA-001 | Buy an unowned material tile adjacent to an existing Quarter. | The shared adjacency handler subscribes to the real `CityTileOwnershipChanged` event. |
| CSC-QA-002 | Reload a save containing established Quarter ability cache entries, then refresh notifications. | The shared notification reader normalizes serialized effect-name hashes and nested `StackAmount` hashes before comparing stacks; retired effects are ignored. |
| CSC-QA-003 | Buy a Tailor next to existing Markets/Temples without changing their populations. | Register customer Culture properties with the existing population scanner, and deliver Culture through customer-owned city-center property bits. Remove the old seller-owned Culture attachments. |
| CSC-QA-004 | A Base-material Industry/Corporation is adjacent to one Textile Workshop in M&C mode. | Keep the existing ordinary +1 and change the M&C additions from +2/+3 to +1/+2, independently for Production and Gold. |
| CSC-QA-005 | An ordinary/Industry/Corporation Specialty improvement is adjacent to a Fashion House. | Add the missing producer-return attachments, following Bakers Cafe: ordinary +1 and M&C additional +1/+2. Reuse the existing Tailors yield-effect children. |

## Bakers and project-wide scope

Bakers already uses the correct material-return arrangement: Water/Wind Mills
return Production/Gold to Base improvements; Cafe returns them to Specialty
improvements. Ordinary +1 combines with M&C additions +1/+2 to reach totals
1/2/3. Bakers gameplay SQL is unchanged. The same offline graph evaluator checks
both Quarters, including every overlapping active attachment, rather than only
checking individual Amount arguments.

Bakers already uses customer-owned property delivery for its active Bakery
population sale. Its old direct Food modifier definitions are not attached.
Tailors now uses that existing delivery approach while retaining its own Culture
amounts and customer families. Ownership and notification defects live in shared
handlers, so their fixes also cover Bakers and future consumers.

The other six Quarter core files do not yet implement comparable active producer
return or population-sale graphs. Apply the reusable validators when those
mechanics are implemented; do not scaffold a runtime system in anticipation.

A proposed new material-return registry/compiler was removed after Henno's scope
clarification. The final approach reuses the proven SQL pattern and strengthens
contracts and validators. There is no Bakers migration or new material engine.

## Contracts and regression checks

`mechanism_bindings` declares the material pattern, both source buildings,
complete tier totals, and separate Production/Gold yields, as well as the
existing customer delivery and shared event/notification handlers. Cumulative
phase validation checks these declarations against active wiring.

Negative tests deliberately restore the original M&C overcount, remove the
Fashion House return, remove customer activation/property connections, restore
the invalid ownership event, or use the original serialized-cache reader. Each
must fail. A duplicated material attachment is also rejected by total evaluation.

The Lua notification fixture runs the shipped handler against serialized cache
keys and tests unchanged, increased, decreased and removed stacks. Native tests
are still required for actual engine delivery and save/load behavior.

All 127 offline tests pass. Foundation, Materials/Stage 2, Stage 3 and Stage 4
phase validators pass with zero warnings; ModBuddy action regeneration checks
pass. The existing art-bridge test expectation was corrected to match the current
approved CSC-owned gameplay property bridge. Physical art remains a separate
check. The reviewed Bakers localization reference hash reflects pre-existing
movement of generic Quarter concepts to the shared localization source.
No phase acceptance or user approval state was advanced.

## MAB comparison for issue 001

Ruivo's read-only reference refreshes on completed district construction and the
first player-turn activation. It has no ownership-purchase listener. That is a
turn-based fallback, whereas CSC now updates immediately on the native tile
ownership event. See the `DistrictBuildProgressChanged` and
`PlayerTurnActivated` registrations near lines 312–314 of
`NEW_ADJACENCY_BONUS_BY_RUIVO_GP.lua`.

## Native rerun

**Passed in a clean process:**

- Real purchase of an unowned material tile immediately updates district yield.
- Real Tailor purchase immediately delivers customer Culture to both customer
  families and the independent second customer city, with unchanged population.
- Seller Production/Gold returns, including the local Workshop exchange, have
  the expected totals after that native purchase.
- A subsequent population update preserves the intended customer Culture.
- Removing the supplier clears customer Culture without a population change.

Evidence: `clean-native/` under the output folder below. Do not equate successful
setup commands or earlier failed/retried samples with passing assertions.

**Material returns remain unresolved.** Both the restored Bakers-style Tailors
graph and unchanged Bakers controls report zero plot-yield deltas in the
artificial world. Ordinary native building purchases also report zero. A small
fixture around a normally founded capital reproduces zero for all six Tailors
source/tier combinations; crossing a turn boundary does not resolve it.
The parent modifier is active and selects the correct owned improvement, but
its `COLLECTION_SINGLE_PLOT_YIELDS` child reports no subjects. The cause has not
been established. These observations do not establish a new Bakers gameplay
bug or establish that the Tailors material fixes work in game. Issues 004/005
must remain unaccepted pending a reliable comparison, ideally using a normally
builder-created improvement in a known gameplay save.

The large fixture's direct debug building recreation also failed several local
return assertions that passed through a normal Tailor purchase. Forced
Corporation placement caused a vanilla Corporation-banner error during an
autoplay control. Treat forced pillage, Wonder pillage, regional boundary and
Great Person point probes from the earlier report as inconclusive where their
normal gameplay preconditions have not been reproduced. No speculative fixes
were made for them.

**Saved notifications passed:** loaded the original
`CSC Tailors full QA checkpoint 20261015` save that reproduced issue 002.
The native reader contained serialized hashed entries, and the fixed handler
refreshed them without error. Instrumenting the actual notification sender on
an unchanged repeat recorded zero notifications. This establishes backward
compatibility for the original failing cache; deterministic tests additionally
cover increases, decreases, removal and retired effect IDs.
A fresh service-cache attempt contained no entries and is not counted as a
successful reload test. Evidence: the two final assertions in `cache-native/`.

**Acceptance summary:** 001, 002 and 003 pass native regressions. The targeted
source corrections for 004 and 005 pass static checks but fail native plot-yield
checks. They are not accepted as fixed. A joint check of a normally built
material improvement in an ordinary gameplay save is the next useful control;
no additional runtime architecture is proposed without resolving this gap.

The first simplified package was installed while Civ retained obsolete
experimental manifest actions in memory. Those attempts are invalid for final
acceptance; the clean process verified the current definitions and loaded
without gameplay database errors.

Generated evidence: `C:/Users/Shadow/Desktop/Codex/csc-qa-fixes-20261015/`.
Relevant folders: `clean-native`, `native-purchases`, `capital-native`,
`capital-diagnostics`, `cache-native`, and `offline-final.txt`.
Original mod preference settings and native auto-start=false were restored
after the checkpoint check. Civ is at the main menu. The installed CSC test
package retains the targeted source fixes; the source remains uncommitted.


## Automation limits exposed by this run

Native purchases and save loading are deterministic through FireTuner, including
native auto-start past Begin Game. No Computer Use was required for this rerun.
Debug map/building/improvement creation is cheaper setup but does not substitute
for validating normal engine behavior. GPP counters need an independently
verified turn-based control; debug pillage needs a real eligible pillage event;
forced Corporation placement needs a valid founding/name state. The unexpected
material-return failure still requires investigation rather than an assumed
fixture explanation or speculative gameplay rewrite.
