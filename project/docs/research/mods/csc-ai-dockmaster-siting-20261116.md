# Small Dockmaster siting adjustment

16 November 2026, Problems **1.2/1.4 and 2.1**. Henno chose a narrow first step
following the [completed coastal survey](csc-ai-customer-first-continents-20261116.md#coastal-tailors-and-the-missing-dockmaster).
Broader prospective Service valuation is queued as **14.3** in the roadmap.
This change is implemented/offline-qualified; no new game was launched.
The preceding turn-250 result used policy19e29a42, before this adjustment.

## Tailors beside an existing Harbor

A Tailors site rated **+1** may now receive a bid if a completed owned Harbor is
adjacent. Unique Harbor replacements qualify through loaded `DistrictReplaces`.
Lighthouse construction may follow; an unbuilt/planned Harbor, unfinished district,
foreign Harbor or City Lights Fishing Town cannot grant the exception. A pillaged
completed Harbor retains its physical adjacency, with repair/building readiness
remaining in the existing economic forecast. Other Quarter sites retain the
**+2 minimum / +3 preference**. Every site still requires a viable Base supplier,
positive net economics, ordinary eligibility and the shared material safeguards.

The facts snapshot reads the existing district inventory, so this adds at most
six local inventory lookups per Tailors candidate and no CE/UI crossings.
It records the completed Harbor plot. The same admission helper is used by the
cheap geometry screen, the final economic quote and continuity grace. This
prevents an early +2 filter from discarding the allowed +1 option or continuity
from keeping it eligible after its Harbor disappears from the owned inventory.

The actual +1 and real transaction streams remain unchanged. Only the siting
policy uses the ordinary minimum band:48 utility on the older CE fallback,
or8% of the native comparison reference times readiness. The ordinary weak-site
cap remains50% of that reference (300 at the early600 reference). Thus accepting
+1 does not extrapolate the +2/+3 preference formula backwards into a negative
bonus, nor grant a strong-site budget. Positive economic value is still required.
`CSC_AI_SPATIAL_BID` now includes `dockmasterHarborPlot`; the native receipt and
construction diagnostics remain the next steps in the delivery path.

## Harbor-first preparation

Material-aware customer guidance adds **8 extra utility** for a Harbor supporting
a concrete prospective Tailors footprint. Its contribution becomes **16–24**,
compared with8–16 for ordinary customer/Quarter links. It still counts once per
supplier city/Quarter type; distinct-footprint matching, shared-material support
and the **32 total utility cap** remain intact.

The reader identifies Tailors from the generated gameplay partner edge and its
existing Base/Spec tags, and resolves Harbor replacements from loaded definitions.
There is no second authored resource/customer interaction list. Existing eligibility,
owned supplier/Quarter footprints and fresh native adjacency remain mandatory.
The **best ordinary adjacency gate remains strict**: a Harbor at0 against a legal
+3 alternative receives no speculative preference, regardless of material counts.
Even a one-point ordinary-adjacency sacrifice remains outside this first step.
Other native forecasts and production choices continue to compete normally.

This is a modest placement preference, not a new estimate of Dockmaster income.
It does not add Service value to the economic ledger. The central model's existing
narrow ready-time Stage2 estimates remain unchanged. In particular, Dumbarton's
0-versus3 Harbor is still rejected; a higher preference cannot bypass that gate.
Sites tying the best ordinary adjacency get a stronger opportunity to complete
an eventual chain. If this remains too weak to win, observe the actual alternatives
before adding another incentive.

## Verification

**95 economy/Lua51 checks pass**, including five new behavior tests:

- Owned completed/unfinished/foreign Harbors, unique replacements and CL providers.
- +1 admission through both the initial screen and final publication, on owned
  and quoted frontier sites; missing Base, protection and below+1 still defer.
- Real adjacency/economic income unchanged, minimum premium, weak-site cap and
  refusal to resurrect a negative economic ledger.
- Harbor preference16/20/24, unchanged other links, rejection of0-versus3 and
 2-versus3, distinct supplier aggregation retaining the32 cap.
- Actual reverse-graph facts discover Tailors/modded materials and a unique Harbor.

Files: `CSC_AI_EconomyFacts.lua`, `CSC_AI_EconomyAdapters.lua` and
`project/tools/ai_economy/test_dockmaster_siting.py`. No CE/API, SQL, production
order or map change. Native acceptance/follow-through of these new values will
be recorded in the next requested live game.
