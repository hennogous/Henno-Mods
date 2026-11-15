# Quarter bid calibration against ordinary districts

The baseline confirms a substantial difference between our Quarter bids and the
native values of ordinary districts with modest starting adjacency. Source and
native-code review identify concrete reasons: our replacement is a conservative
ordinary-exchange forecast, while native district totals include a broader,
heuristically weighted menu of future building benefits. Correct native yield
units alone do not make those whole bids comparable.

**Correction, implementation review15 November:** the current model already
enumerates bounded optional stage plans and removes unprofitable missing
customers. The initial audit overstated mandatory later investment as a defect.
The measured scores and remaining site-cost/coverage differences stand.

**Next action:** preserve and verify optional investment valuation and align site-cost accounting,
then price credible Service benefits and calibrate the resulting whole bid against
native competitors. Keep the spatial quality preference. A single multiplier
derived from pooled medians would hide these differences.

No policy values changed and no game started for this audit. Finding **AI-C190**.
This follows the [bid funnel](csc-ai-quarter-bid-funnel-20261115.md) and reuses the
[three-map controls](csc-no-csc-district-baseline-results-20261114.md).

## What the vanilla district records show

Controls are stock AI without CSC, with City Lights, Resourceful2 and Sukritact's
Resources retained. Original AI1–5, three preselected maps, Online250. There are
1,124 foundation records. The following rows select **exactly +2 actual adjacency
at the placement event**, in the district's ordinary yield. Exact types are kept
separate from unique replacements.

Entries show median native choice utility, with sample count in parentheses.
Q8 integers are divided by256. Periods use observed foundation-event turn; the
old raw `foundationTurn` field is invalid in these controls.

| District, actual adjacency +2 | Turns1–75 | Turns76–150 | Turns151–250 |
| --- | ---: | ---: | ---: |
| Campus, Science |554(10)|1,054(12)|1,920(16)|
| Commercial Hub, Gold |632(1)|1,544(6)|1,931(8)|
| Harbor, Gold |—|1,836(2)|2,616(4)|
| Industrial Zone, Production |—|1,030(4)|2,218(6)|
| Theater Square, Culture |624(6)|1,197(9)|2,112(13)|
| Holy Site, Faith |874(1)|—|—|

The pre-placement cached Campus values for those same period strata have
medians538/1,272/2,541; prior choice ages have medians2/3/4turns. Thus the
native scores are total investment forecasts, not adjacency points converted
by a single constant. The compact JSON contains both score clocks and counts.

For context, all positively published Quarter offers on the latest new seed
have these median **whole** bids:

| Prospective Quarter rating | Turns1–75 | Turns76–150 | Turns151–250 |
| --- | ---: | ---: | ---: |
|2 to below3|138(469)|247(1,763)|323(2,178)|
|3 or more|254(284)|433(1,209)|636(1,688)|

These Quarter samples repeat losing as well as winning offers. The ordinary
district sample contains selected investments that were subsequently founded.
They provide a useful scale and maturity reference, not a fitted multiplier.
The earlier same-city/round audit strengthens the comparison:918 observations
with owned+2 offers and ready/exempt slots have higher chosen ordinary district
values, medians2,539 against397 for the best matching Quarter offer.

### Starting adjacency and prospective Mill rating

Quarter policy ratings can include a future Mill's terrain contribution. They
must be distinguished from ordinary districts' actual starting UI adjacency.
The lifecycle observer records both. Original AI foundations on the new seed:

| Quarter | Turn | Initial eligible Production / Gold | Prospective rating | Published whole bid |
| --- | ---: | ---: | ---: | ---: |
|Ottawa Bakers|12|2 /1|3|283|
|Sheffield Bakers|38|1 /1|3|170|
|Meroë Tailors|39|2 /1|3|294|
|Niani Tailors|134|3 /1|4|1,404|
|Nioro Bakers|179|2 /1|3|242|

These are eligible rule amounts at foundation, before completion/pillage gates
on actual output. Sheffield starts at2 and forecasts3 with its local Water Mill.
The other four have equal current and prospective totals. Production+Gold also
needs native yield weights; it is not interchangeable with +2 Science or Faith.

## What is aligned, and what differs

| Component | Current Quarter replacement | Native ordinary district path | Assessment |
| --- | --- | --- | --- |
|Units and yield weights|CE prices each real yield in native Q8, including player yield preference|NormalizeYields applies yield DefaultValue and strategic yield bonus|Aligned; no missing ×256 found|
|Online time preference|50turn horizon, discount4.0|GlobalAI speed-adjusts base100 horizon and base2.0 discount to50/4.0|Aligned for these Online games|
|Construction cost|Delays income, with maintenance and a once-only purchase payment|Costs influence ready time; site costs have separate terms|No universal missing capital-cost debit or double charge found|
|Construction schedule|Current Production, serial Quarter/producer/customer jobs; stage customers precede the next stage|Item-specific production estimates and prerequisite delays|Our schedule can greatly postpone later income; item modifiers/future Production deserve review|
|Optional later investment|Already compares bounded stage subsets and greedily removes unprofitable missing customers|Only qualifying **positive** building values enter district aggregation|Implemented before this audit; preserve it and rank plans by the final bidding objective|
|Ordinary exchange|Producer/material/customer returns, population payouts, upkeep, local/regional amenities, reciprocal customer adjacency|Supported intrinsic yields, pseudo-yields, modifiers and other building branches|Our ordinary ledger is substantial but covers a narrower benefit set|
|Services, specialists, trade|Explicitly omitted from the Quarter placement ledger|Native buildings can receive specialist/GPP/trade-related or other supported value|Real missing coverage; Service-aware building nominations do not restore it to the whole placement bid|
|Material work|Producer input credited; outward tile returns require an observed worker; unavailable supplier jobs have unknown ETA|Improvement loss branch has no citizen-work gate|Conservative staffing is a policy assumption, not native valuation parity|
|Displaced land|All observed ordinary income of a worked footprint is debited|DistrictNetValue has an intact-improvement value branch, independent of citizen staffing, plus resource/clearance terms|An unimproved worked tile can be charged by us without that native improvement debit; intact unworked improvements differ in the other direction|
|Future building weighting|No prerequisite-depth amplification|BuildingValue multiplies an early benefit subtotal by **1+2d**, first-prerequisite depth d; later additions are separate|A structural bidding heuristic absent from our replacement|
|Future customer district space|Bounded layout preference, no transaction income before the customer district exists|The native building aggregate is broader, with actual eligibility/requirement gates|Preserve Henno's completed-customer rule; do not solve calibration by inventing transactions|

The footprint difference remains for initial, unselected sites. The Pella
continuity fix only preserves an initially unworked **native-confirmed** plan
against a later temporary citizen assignment. It does not harmonise admission
costs for every worked candidate. Critical-material protection is a separate
CSC externality and must remain even if ordinary land costs are revised.

The depth heuristic is quite specific. Library→University→Research Lab gives
depth0/1/2 and factors1/3/5 on the early subtotal. It does not multiply every
building effect. An active positive district preference can also multiply an
earlier site term; its presence in each archived comparison was not captured.
Do not apply a universal1.5 to all native totals.

## A measured example of the timing effect

Historical read-only component captures track the same Lingapura Bakers2992
site: starting2, prospective local Water Mill rating3. These captures predate
the current siting premiums; only the economic ledger is used below.

| Turn | Current Production | Quarter ready in | Mill ready in | Whole economic utility before siting preferences |
| --- | ---: | ---: | ---: | ---: |
|155|1.20|26|60|16.6|
|160|2.40|13|30|51.8|
|180|3.90|8|19|89.8|
|200|8.40|4|9|399.4|

At155 the Mill misses the50turn horizon. The ledger contains direct adjacency,
reciprocal customer return and Quarter upkeep, with no operating chain income.
At160 the missing Granary completes at44; its three Stage2 sales streams together
are worth only about2.7utility in the remaining window. At200 more of the
chain fits, while player yield/amenity weights and other conditions have also
changed. Each complete component sum exactly matches its recorded economic Q8.
This demonstrates the model's maturity sensitivity; exact native ETA differences
for these sites require a targeted component comparison.

## Recommended calibration work, in order

1. **Preserve the option to develop a Quarter.** The model already compares
   bounded stage subsets/customer investments. Verify that introducing forecast
   weights ranks their final bids consistently, while retaining prerequisites,
   shared queues and upkeep. This is a robustness check, not a missing feature.
2. **Align land-cost treatment.** Separate native-compatible ordinary improvement
   displacement from CSC's critical-material externalities. Quantify the removed
   worked-terrain debit in candidate diagnostics. The native route already
   supplies an improvement valuation; avoid reconstructing its arithmetic in Lua.
3. **Price credible Service benefits.** Add unlock/time/chain/recipient-aware
   marginal value for actual Bakers and Tailors Services. Dockmaster remains
   era-limited. Keep staffing and trade omissions explicit until priced. No
   assumed future customer districts are needed to do this.
4. **Review readiness, then whole-bid strength.** Use item-specific Production
   rates where available, and test a bounded Production-feedback estimate.
   Compare the resulting ledgers with a few same-city ordinary districts at the
   actual comparison boundary. Keep any native-style strategic weighting in the
   decision adapter, separate from truthful CSC transactions.
5. **Verify consequences.** A small matched saved-state comparison should show
   corrected bids reaching native comparisons and identify changed winners.
   Then use a fresh full game to measure foundations, materials/customer quality
   and later chain outcomes. Keep unit/project competition native.

The4096 ceiling is a secondary issue: only three outgoing observations reached
it in the current run. Raising it cannot explain the widespread low bids.

**Separate delivery gap:**50/4 is hard-coded. Standard's native ordinary horizon
is100 and discount2; longer speeds require longer horizons as well. The current
CE quote horizon limit100 also needs review for Epic/Marathon. This is real
portability work, but did not cause the observed Online score gap.

## Evidence, binary scope and reproduction

Current CSC policy9f450233; native XP2 SHA
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
Ghidra reference SHA
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
The **entire .text section is byte-identical**, SHA
`d5bc8feddb8c030dbf2afc3fa9d9110eadbdb349cdb8aa56d5928625290c3d79`;
the inspected discount constants also match. Native code findings therefore
apply to the current XP2, with configuration values read from the archived DB.
No native addresses or hooks were changed.

| Named native role | RVA | Audit use |
| --- | --- | --- |
|GlobalAI initializer|49c7c0|Speed-adjusted discount and horizon array|
|Game-speed linear / inverse scaling|36f620 /36f7b0|Horizon / discount scaling|
|Player discount accessor|4b38f0|Reads initialized GlobalAI discount|
|City evaluation job|3e2aa0|Ordinary horizon array[1], Wonder array[2], research and item timing|
|Yield normalization|52b110|Default yield value and strategic weighting|
|District net value|52a440|Improvement/resource/clearance site costs|
|Building value|52b900|Early prerequisite-depth heuristic, maintenance and timed valuation|
|District aggregation|3dfee0|Qualifying positive future-building sum|

Source: main CSC `CSC_AI_EconomyFacts.lua`, `CSC_AI_EconomyModel.lua` and
`CSC_AI_EconomyAdapters.lua`; installed CE pricing implementation
`native/economy_pricing.inl`. Read-only decompilations are preserved at
`Desktop/Codex/csc-ai-district-value-audit-20261115/ghidra-functions.json`.
Speed/accessor helpers are preserved beside it in `speed-functions.json`.
Large logs and captures stay in the dated Desktop evidence roots recorded in
the [compact data](csc-ai-district-value-audit-20261115.json), with source hashes.

Reproducer: `project/tools/ai_economy/audit_district_value_calibration.py` accepts
the control campaign root, current CSC run, historical component directory, both
DLL paths and an output JSON path. It reads archives only, checks binary hashes
and code parity, and verifies component sums. Reproduction yields1,124 native
foundations,7,591 positive Quarter publication observations and five AI Quarter
foundations. Per-adjacency/type/period strata include both native score clocks.
