# What we’re investigating

We have identified a specific valuation mismatch. The next step is to correct it at an appropriate boundary, then test what changes. The CE/Lua port restored our development capability; it did not itself improve the placement formula.

## Answer found: the Mill’s adjacency encoding becomes a phantom forecast

In the earlier Delhi case, our deduction left an initial site value of **1,207**, yet the final cached value reached **1,358,358**. In Majapahit, **32,200** became **1,623,830**. These are internal fixed-point utility values, not yields.

The old captures did not itemise each building. A new **read-only observation across turns 80–81** of that archived world now does. In both cities, the Wind Mill accounts for more than 99.8% of the building contribution. Bakery and Café contribute much smaller values; native mutual-exclusion handling leaves Water Mill out of the district sum.

The dominant Mill term comes from ten generated adjacency modifiers with magnitudes 1, 2, 4, …, 512. Gameplay enables only the bits representing its actual hills/river bonus. The hypothetical evaluator omits the property gates and credits all ten magnitudes. The observed 512 contribution is positive even while that gameplay bit is disabled on every captured owner district plot.

That is a forecast error, not real income. Other building benefits—amenities, correctly gated exchanges and development—still matter. The small remaining terms are not all independently attributed, so we should not erase the entire future-building sum. The observation changed no scores and proved no improvement in decisions.

[Read the exact breakdown and evidence](../../research/mods/csc-ai-bakers-forecast-components-20261104.md), or [the technical score explanation](../topics/native/district-score-anatomy.md).

## Current question: what is the cleanest targeted correction?

We need to exclude or replace the false encoding-bit contribution while preserving justified native value. Our current district adjustment happens **before** this building pass. A large opposing subtraction can cross a sign gate and discard real benefits too; a precise correction may need a building/modifier forecast boundary or an explicit final-component contract.

No correction has been implemented yet. The useful next comparison would show the isolated forecast change first, then whether a different opportunity wins and gets built. A focused comparison can answer that before another broad 100-turn screen is needed.

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

The CE proposal is a draft. Actual Workshop subscription, broader compatibility and supported versions need qualification before a release claim. Those delivery questions differ from whether the economic policy is good.

This page carries the short current agenda. The [technical roadmap](../roadmap.md) and [broader question backlog](../topics/history/open-questions.md) retain detail and history.

**Back to:** [Start here](../index.md) · **Supporting material:** [Research library](../library.md).
