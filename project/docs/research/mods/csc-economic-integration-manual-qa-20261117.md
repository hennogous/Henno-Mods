# Ordinary-economy integration: gameplay changes and human QA

Roadmap Problems1 and2. This is Henno's next-step checklist after the three
Online250 results. It covers this economic integration, independently of other
art, lens, localization or Pedia work in the shared checkout.

## What changed in gameplay code

**Fixed transactions:** Mill/Granary, local producer exchanges and the Tailors
Workshop/Lighthouse relationships now declare amounts, recipients and native
gate bindings in shared gameplay tables. A processor generates the existing
native effects. Gold companion files append their legs to those definitions.
The intended payouts, ownership checks, building availability and modifier
identities are preserved. The model can now discover both external customers
and local transactions from those same declarations.

**Material transactions:** Base/Spec inputs and worked-plot returns use declared
directional legs and actual input hosts, including optional-mod hosts and M&C
Industry/Corporation increments. The native processor replaces copied amount
literals. Ordinary1/Industry2/Corporation3 input totals and existing return
increments are retained. Ownership, adjacency, improvement and damage gates are
preserved; AI reads those gates rather than creating its own economic version.

**Population transactions:** Bakers Bakery/Café and Tailors Tailor/Fashion House
partners and amounts are gameplay-owned. The shared refresh reads them for its
existing Q8 population properties. This retains the previously QAed rounding and
per-five-population behavior. The AI now includes Stage3 partners that its old
Stage2/4-only customer list missed.

**Observed trade:** native route definitions now feed one shared read-model and
eligibility kernel used by gameplay scanning, previews and AI. Native payout
rows remain unchanged. Preview corrections are intentional: Tailors requires its
intact producer, disabled transaction Gold disappears, and export previews omit
amounts when the receiving producer is absent or pillaged.

**AI:** whole-player candidate worlds now account for ordinary exchanges, shared
construction queues, suppliers, population rounding and observed workers/routes.
Customer siting uses signed differences against an ordinary-preferred reference;
Quarter siting uses a marginal economy plus calibrated planning preferences.
In placement forecasts, prospective Services, imagined future workers and
invented route renewal earn no income. Existing narrow Stage2 building guidance
is retained. These change decision guidance rather than economic rules.

**CE:** recurring-interval quote wrappers correct their time-zero origin; a
read-only steady clock measures policy wall time. The qualified early score
entry remains the customer delivery path. No upstream PR has been submitted.

## Existing regression evidence

The corrected mature-world migration reproduces all10,954 CSC native effect and
requirement rows, including137 fixed rows. Old/new population refresh agrees
across67 cities and42,210 property/bit readings. Gold-off/on and M&C alternatives
have focused offline graph checks. Material lifecycle tests observe real native
payout interruption and restoration. The final mature policy qualification
preserves those checks and closes/restores with native exit0.

Source reports retain the detailed scopes:
[population](csc-population-transaction-catalogue-20261116.md),
[fixed](csc-fixed-transaction-catalogue-20261116.md),
[materials](csc-material-transaction-catalogue-20261116.md),
[routes](csc-observed-routes-20261117.md), and
[integrated model](csc-customer-world-pricing-20261117.md).

## Focused manual checks

1. **Fixed exchanges, both Quarters:** compare an external customer and a local
   producer exchange with the documented amounts. Include Water/Wind alternatives
   and Workshop/Lighthouse; test a unique customer replacement where available.
   Check the city receiving each yield, not only the total empire yield.
2. **Base and Spec:** check an improved, worked supplier and an unworked one.
   Pillage/repair a supplier and its producer independently; the appropriate
   inputs/returns should clear and resume. Include one optional resource or M&C
   host if that configuration is part of the save being reviewed.
3. **Population customers:** check Bakery/Market, Tailor/Market or Temple, then
   Café/Zoo and Fashion House/Amphitheater or its exact Wonder customer. Around
   population5/10 and with two sellers/venues, check the established rounding
   and combined payout. City/Wonder attribution should remain correct.
4. **Routes and previews:** compare one ordinary domestic and international
   route preview with actual imports/exports. Damage/restore a Tailors producer;
   check Gold disabled in an appropriate setup. An origin Quarter should stop
   that family's imports from foundation, preserving the existing rule.
5. **Persistence:** reload one working chain, then damage/restore its producer
   or customer. Its ordinary transaction and existing Service behavior should
   resume normally. Guidance changes should not alter building availability.

Use these as a focused review of preserved behavior and the stated preview
corrections. The full-game campaign supplies AI placement, material, customer,
building, Service and timing results separately. Human gameplay validation
remains Henno's next step.
