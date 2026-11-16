# Shared CSC economic definitions

The gameplay definitions and AI model must describe the same economy. Both may
change to achieve this; gameplay changes require regression checks. This is the
16 November 2026 decision following Henno's concern about gaps between incremental
implementations and Astra's source audit.

## Contract

Ordinary building transactions should have one gameplay-owned identity, source
and partner building families, spatial/ownership rule, functioning-object gates,
quantity rule and payout legs. Gold companions add Gold legs to that identity.
Gameplay, UI, private native adjacency and AI consume generated projections of
those definitions. They must not maintain independent lists of partners or rates.

Use finite patterns matching the implemented game rather than a general Civ
modifier interpreter: fixed exchanges, customer-population rate exchanges and
whole stacks per customer-population threshold. Retain existing modifier and
property identities during migration. Shared properties accumulate each
transaction once; Production and Gold consuming one property do not double its
quantity. Unique replacements inherit once.

Adjacency remains authoritative in the bundled adjacency system. Its partner
edges join building transaction edges for placement guidance. Material exchanges,
observed trade and observed specialist income need explicit coverage too; an
unbuilt customer, unassigned worker or hypothetical route earns no automatic
income. Services remain outside the new Quarter/customer placement forecasts.

## Audit findings to close

| Channel | Current gap / required correction |
| --- | --- |
| Stage 2 and local fixed building exchanges | Planning metadata and native modifier graph are authored separately; model assumes unit terms. Declare terms and bind/generate their native effects. |
| Stage 3 | Gameplay registry is authoritative, but some AI/UI readers missed it. Preserve aggregate Q8 rounding and shared-property behavior while bringing it into the common catalogue. |
| Stage 4 | Gameplay hardcodes venue lists separately from UI metadata. Include all Café venues, LGD Conservatory and Fashion House Wonder venues. |
| Functioning gates | Stage 3/Café require a functioning partner building; Fashion House district partners additionally require an unpillaged district. Preserve or deliberately change/test this distinction. |
| Customer forecasts | Evaluate the new customer against all affected suppliers together, including district adjacency externalities and shared rounding/queues. Remove ordinary prerequisite upkeep already priced natively. |
| Native overlap | Identify CSC contributions already present in the native building forecast before adding a residual. Never subtract the entire ordinary Market/Bank/Stock Exchange forecast. |
| Materials | Existing amount checks do not validate complete modifier attachments/gates. Extend the same contract/regressions to resource/improvement transactions. |
| Trade and specialists | Cover observed activity and opportunity costs explicitly; defer invented future activity. |

Stage 4 Culture is the correct current customer yield for both implemented
Quarters and their venues. The issue is duplicated definitions, not a demonstrated
wrong Culture payout. Ordinary sales do not inherit Service material/civic gates.

## Migration and regression gates

1. Preserve a reference graph and payout fixtures before changing gameplay.
2. Move population transactions first: shared declarations, generic scanner and
   generated output/read-model data. Preserve properties, modifier IDs, Q8 rate
   ceiling/cap and per-customer Stage 4 floor.
3. Migrate fixed exchanges and their narrow native gate templates. A checked
   binding to old requirements is an intermediate state, not full gate ownership.
4. Make the central model read actual payout legs, then aggregate a proposed
   customer against every affected chain before pricing a native residual.
5. Qualify native reception with a bounded matched replay before another full run.

Required cases: same/cross-city ownership; two suppliers sharing a customer;
Market and Temple in one city; population 4/5/9/10; all ordinary Wonder venues;
unique replacements; alternative Mills; independent source/partner building and
district pillage; capture/removal/reload clearing; absent Gold companion; optional
LGD/City Lights; ordinary sales with Services locked. Compare native modifier
attachments, leaf arguments and requirement graphs before/after, not just totals.

Scope remains roadmap Problems 1 and 2. This contract supports later execution
adapters without expanding this pass into research, Builder or building-order
tuning.
