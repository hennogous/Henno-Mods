# What we’re investigating

We have identified a specific valuation mismatch. The next step is to correct it at an appropriate boundary, then test what changes. The CE/Lua port restored our development capability; it did not itself improve the placement formula.

## Answer found: the Mill’s adjacency encoding becomes a phantom forecast

In the earlier Delhi case, our deduction left an initial site value of **1,207**, yet the final cached value reached **1,358,358**. In Majapahit, **32,200** became **1,623,830**. These are internal fixed-point utility values, not yields.

The old captures did not itemise each building. A new **read-only observation across turns 80–81** of that archived world now does. In both cities, the Wind Mill accounts for more than 99.8% of the building contribution. Bakery and Café contribute much smaller values; native mutual-exclusion handling leaves Water Mill out of the district sum.

The dominant Mill term comes from ten generated adjacency modifiers with magnitudes 1, 2, 4, …, 512. Gameplay enables only the bits representing its actual hills/river bonus. The hypothetical evaluator omits the property gates and credits all ten magnitudes. The observed 512 contribution is positive even while that gameplay bit is disabled on every captured owner district plot.

That is a forecast error, not real income. Other building benefits—amenities, correctly gated exchanges and development—still matter. The small remaining terms are not all independently attributed, so we should not erase the entire future-building sum. The observation changed no scores and proved no improvement in decisions.

[Read the exact breakdown and evidence](../../research/mods/csc-ai-bakers-forecast-components-20261104.md), or [the technical score explanation](../topics/native/district-score-anatomy.md).

## Implemented in source: local, small Mill bonuses

The follow-up has confirmed that **both Mills** inflate through the same mechanism. Their large numerical differences come from forecast timing, while native mutual-exclusion handling decides which one enters the district sum. MAB’s broad encoding range is unnecessary for CSC’s current local rules.

The first correction is now implemented in source: one conditional +1 switch for Wind and three +1 steps for Water, preserving the actual geometry and payouts. A Mill must be built and functioning in the receiving Quarter. A remote Mill no longer enables it. MAB supports this local scope; CSC had inherited its generic player-wide default by omitting the override.

The source bounds the adjacency capacity exposed through a building from 1023 to 1 or 3. It does not make the AI obey the conditions it omits. The focused offline tests exercise the actual SQL compiler and Lua evaluator, including local/remote ownership, pillage, stale properties and the planned-Mill scanner. Old modifier definitions remain available for saved references, but their building attachments are disconnected.

Henno chose to keep FireTuner open and finish offline checks only. No installed package or game was changed. The next native comparison must verify real yield transitions, saved-game reconciliation and the isolated forecast change before asking whether a different opportunity wins and gets built. [Implementation and evidence](../../research/mods/csc-ai-local-mill-unit-steps-20261104.md).

## Continue the building ledger: real benefits and hidden markers

Before another tuning change, the remaining building ledger must distinguish
real Mill/Bakery/Café benefits from implementation scaffolding. The hidden River
Access markers have zero own value in our capture, yet their prerequisite and
mutual-exclusion links can still change the forecast. The source audit confirms
their gameplay purpose and the Wind-on-river asymmetry; their exact early-income
and timing contribution is still open. [River Access findings](../../research/mods/csc-ai-river-access-flags-20261104.md).

## Next: cover candidates before commitment

Our scanner excludes some opportunities native planning considers. Two earlier poor placements entered requests before our policy covered them. We need to establish the precise admission gap and cover relevant candidates early enough.

Existing requests may retain an older higher value. Changing that persistence needs its own native contract and validation; refreshing the site table does not automatically solve it.

## Then: correct a relationship and test a choice

Once the ledger identifies a specific mismatch, apply a bounded correction and compare competing opportunities. The useful result is a traceable choice change, followed by construction and eventually returns—not just a lower number.

| Later question | Why it matters |
| --- | --- |
| Does the first producer win production? | A Quarter without development may remain a poor investment. |
| Do materials and customers develop and survive? | Placement cannot substitute for Builder jobs, customer construction and repair. |
| Does the chain improve empire outcomes? | Benefits must justify costs and displaced opportunities, under standalone CSC and RH. |

## Release work continues separately

The earlier CE draft is closed. An API-only `develop` port is prepared for fresh supported-build and native checks; toolchain installation is deferred until Henno is at the keyboard. We will agree on the capability scope before a later PR. Actual Workshop subscription and broader compatibility remain separate from both this port and the economic policy. [Contribution status](../../research/mods/csc-ce-develop-port-20261105.md).

This page carries the short current agenda. The [technical roadmap](../roadmap.md) and [broader question backlog](../topics/history/open-questions.md) retain detail and history.

**Back to:** [Start here](../index.md) · **Supporting material:** [Research library](../library.md).
