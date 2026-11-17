# Perth: the Tailors offer loses before a construction request

**Perth is primarily a ranking/calibration case.** Its Tailors score reaches the
native cache at the published value, but another district wins each of the20
matched comparisons with a positive Quarter offer. The Quarter is never selected
and no Tailors construction request is submitted. The earlier expectation of an
accepted Quarter plan stuck on its way to production should be replaced by this
measured result.

17 November2026; Problems1.4/1.6/2.1, **AI-C211**.
[Comparison records, economic terms and hashes](csc-ai-perth-followthrough-20261117.json).
Read-only analysis of the completed post-restructure Continents250 run. No game,
replay, native patch or tuning change was needed.

## What actually happened

Player4, Perth city327684; proposed Tailors plot1313 beside Base1239 and Harbor1387.

| Turn | Observed development |
|---|---|
|78–95|Candidate footprint is unowned; no adjacency sufficient for our offer.|
|96|Local rating+1, still unowned.|
|123|Footprint owned; local rating still+1.|
|142–143|Harbor founded142; Quarter rating becomes+2 and first positive offer appears143.|
|149–150|Harbor contract completes149. The next district comparison150 prefers a Rural Community.|
|153|Native Lighthouse construction request appears; Lighthouse is working at250.|
|177,196,215,220|Our policy withdraws the Quarter on a negative economic estimate.|
|203–204|Adjacent City Lights Rural Community C founded203; Quarter rating becomes+3 at204.|
|214|First logged positive+3 offer; Campus wins the district comparison.|
|230–250|Further+3 offers remain below observed competing Rural Community bids. No Quarter is founded.|

The source rating observations explicitly exclude future customers. The Harbor
and CL provider foundations already exist when those increases appear; the
loaded gameplay adjacency system permits such sources before completion. The
endpoint's+3 should therefore not be projected back onto the earlier+2 window.

The existing Harbor tree is working through149. Score refreshes can happen
while a district tree is occupied;42 score writes do not represent42 free
construction opportunities. This matches the documented native cadence.

## Scores at the actual native comparison

All values below are native utility, dividing recorded Q8 integers by256.
The candidate value is a final managed write earlier in the same native journal
generation than the winner, not a published value borrowed from a later turn.

| Native call turn | Quarter rating | Delivered Tailors value | Winning district | Winner value |
|---|---:|---:|---|---:|
|150|+2|683.6|City Lights Rural Community A|2,468.3|
|163|+2|858.6|Water Park|2,832.9|
|172|+2|705.8|Spaceport|4,454.3|
|214|+3|1,574.1|Campus|3,696.5|
|230|+3|2,219.4|City Lights Rural Community A|4,276.5|

There are74 recorded district selections over Perth's lifetime.57 have a retained
same-generation target-cell write before the winner.20 of those target values
are positive; **all20 exactly equal the corresponding published Quarter bid and
all20 lose to a higher winner**. The other37 fresh target values are negative.
Seventeen decisions lack that precise fresh-write join and are retained as such
in the JSON, rather than assigned a later proposal's value.

Native district winners over the full city history:

| District | Selections |
|---|---:|
|CL Rural Community A|57|
|CL Rural Community C|9|
|Spaceport|3|
|Encampment|2|
|Harbor, Water Park, Campus|1 each|
|Tailors|0|

The independent CityBuild log has zero submitted Tailors requests and the
physical observer has zero Tailors foundations in Perth. Its production queue
instead develops the Harbor, Water Park, Theater, Encampment and Campus, alongside
Wonders, ships, other units and projects. Unit/project competition is downstream
of the point where this Quarter lost.

## How our valuation produces that result

At150 the Tailors bid is approximately:

| Component | Utility |
|---|---:|
|Net ordinary joint-economy marginal|319.5|
|Native-style building forecast-depth premium|189.8|
|Spatial adjacency preference|158.3|
|Customer-layout preference|16.0|
|Final bid|683.6|

Its+2 quality ceiling is791.4 and does not bind that offer. In four of the20
matched positive comparisons the ceiling does bind, but removing that deduction
alone would still leave the Quarter below the recorded winner in every case.
This is arithmetic sensitivity on fixed observations, not another played arm.

The model's negative-economic withdrawals are also deliberate policy decisions,
not missing native receipts. All four record a staffed footprint and native-site
opportunity-cost accounting;177 is the largest negative estimate. These terms
are worth inspecting in the next economic audit before increasing bonuses.

The pre-replacement candidate value exceeds the recorded winner in10 of the20
positive comparisons. Our complete valuation therefore changes the numerical
ordering materially. Those old native forecasts should be checked against actual
CSC transactions before treating their larger values as the right answer.

City Lights supplies many of the stronger alternatives. Its tree repeatedly
tries clearing/build-charge workflows on Rural Community sites. These records
show repeated choices, not a diagnosed CL bug. Preserve its own AI tuning while
checking whether the compared investments and our Quarter forecasts are valued
in a sensible common range.

## Next useful work

**The original Perth delivery question is answered:** the positive score lands
and loses before a Quarter plan/request. A reservation rewrite is not indicated
by these comparisons.

Next1.4 calibration: audit the ordinary income, costs and staffed-footprint loss
behind one+2 and one+3 Perth quote against the competing district's native value.
Keep prospective Service valuation on its existing deferred roadmap item. This
will distinguish a sensible preference for a stronger investment from a missing
or mis-scaled ordinary Quarter benefit. Change a demonstrated valuation gap,
rather than ensuring that this particular Quarter wins at any price.

Coastal material assistance remains a separate design option. This site has only
one Base and no Spec; it needed later customer/provider placement to reach+3.
Improving genuinely good early coastal layouts would align with the existing
placement objective without lifting every weak Quarter bid.

## Provenance and audit method

Source: `Desktop/Codex/csc-ai-restructure-regression-20261117/continents250-02`;
initial seeds18461107/29461107; stock AI with CL/R2/Suk resources and BRS/EPC UI.
The source game closed/restored exit0. AI source d6a9114a; CE DLL SHA256
`b7194a83569283033a7c9687ae6d92c33cef7b7d04daaf8e115c641077cd7da9`.

`district_followthrough_results.py` pairs all74 CE winner records with the
independent native observer by ordered district/plot/value identity. The latter
provides the actual native call turn; CE drains often label the next round.
Candidate joins require an earlier journal ordinal in the same generation.
Receipt counts deduplicate by packet version. The analyzer reads source logs,
the loaded district catalogue and physical construction records; it connects to
no game. Three focused tests guard ordering, later-write exclusion and numeric
line-ending parsing. Raw inputs are hashed in the compact JSON.
