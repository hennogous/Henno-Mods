# How Civ VI prices an improvement displaced by a district

On the Windows Gathering Storm build, a fresh district-site score includes an
explicit adjustment when the site has an intact improvement. The main term is
the improvement's estimated remaining benefits from the district's forecast
ready turn. Civ uses the same improvement evaluator for ordinary improvement
decisions. The adjustment varies with the improvement, the plot, the empire
and timing.

## The district's arithmetic

The district branch of `AI::ValueManager::NetValue` (`0x52a440`) computes
ordinary clearance and harvest terms before reaching the improvement. A
visible resource without a harvest definition returns a zero district value
before this branch. For candidates reaching it, the adjustment is:

```text
site subtotal -= Value(existing improvement, plot, city, ready, horizon)
site subtotal -= GainResourceValue(visible resource, -1, ready, horizon)
site subtotal += discounted positive district-creation yield, when applicable
```

The arithmetic uses signed Q8 utility. The resource helper receives a removal
quantity of `-1` and the scorer subtracts its returned value as-is. A missing
visible resource and the bonus-resource branch return zero from that helper.
The helper has separate class-specific logic for luxury amenities, available
copies and strategic supply and demand. The visible-resource legality gate
limits which classes and definitions can reach it. This is distinct from the
one-off harvest credit and does not imply a positive resource debit on every
improved site.

`GetDistrictCreationYield` checks registered effects for the new district and
the existing improvement. A positive amount is converted using default yield
weights and discounted as a one-time award at the ready turn. One shipped
example is the Gathering Storm Public Transport policy's Gold when a
Neighborhood replaces a farm, scaled by plot appeal. Its registration and
arguments are in `DLC/Expansion2/Data/Expansion1_Policies.xml` under
`PUBLICTRANSPORT_FARMREPLACEGOLD`.

A missing improvement or a set pillage bit skips all three lines. The Lua
`Plot:IsImprovementPillaged()` wrapper reads the same bit. The district branch
has no check for whether a citizen is working the improvement. The branch
returns to ordinary district valuation before preference scaling and the
later city/type future-building addition.

## What the improvement value contains

`Value` at `0x530690` uses the existing improvement definition, the real plot
and the evaluating city. The improvement's ordinary yield rows and applicable
plot-dependent improvement adjacency feed the calculation. `NormalizeYields`
uses each yield's default weight and the player's current strategic yield
bonus. The helper also includes applicable terms for housing, tourism, combat
benefits and supported improvement modifiers. For example, a farm's own Food,
eligible farm adjacency and housing can all matter. This is an improvement
valuation, with no Builder charge or plain terrain yield added in the traced
improvement term. Other district valuation terms have their own inputs.

The recurring subtotal uses `DiscountIncomeStream(horizon)` minus
`DiscountIncomeStream(ready)`. The caller's ready time is construction turns
plus the larger of the technology and civic wait estimates. The improvement
helper can shorten its end horizon for flood or feature timing and return zero
for a relevant active drought. It does not add value for an eventual repair of
a pillaged improvement in this branch. Applicable housing and modifier terms
have their own valuation paths. The result is a forecast in native utility,
so even improvements showing the same yields can have different debits.

## CSC application

The native debit establishes a price for the improvement. We have yet to
attribute the separate cost of crossing a CSC material requirement from one
supplier to zero. The improvement evaluator does call native modifier analysis
with plot and city context. The [building forecast study](csc-ai-mill-building-study-20261105.md)
observed other paths with different context, so its zeros alone cannot price
the loss of an existing supplier here.

Bakers and Tailors use adjacent mapped improvements for their material gates.
Their Stage 2/3 Services require Base supply and their Stage 4 Services require
both Base and Specialty. Other gates, including the producer, customer and
civic where applicable, still govern which Services would actually turn off.
The current SQL places the adjacency and resource-tag conditions on a
`COLLECTION_PLAYER_IMPROVEMENTS` count of at least one. The Quarter lens
distinguishes functioning improvements from pillaged ones. The historical
[Tailors preservation case](csc-ai-material-preservation-and-repair-review-20261023.md)
shows how later district construction can erase supply after a Quarter has
already been built.

Henno's requested placement behavior applies to any district that would
consume a material site. Compare each adjacent Quarter's qualifying Base and
Specialty counts with and without the candidate footprint. Apply the strongest
discouragement when the last working supplier of either class is lost,
especially when an operating Service would switch off. One supplier may serve
multiple Quarters. Count their real affected benefits once each. Keep a
qualifying customer's adjacency benefit on a safe alternative tile. An
unrelated district on a safe tile gets no CSC preservation adjustment.
Use the lost CSC contribution as the target for calibration, keeping the
native improvement debit and ordinary district competition intact. A routine
late adjustment also needs fresh native values and coverage of all relevant
district types; the [existing CE proof](csc-ce-late-score-api-20261105.md) used a
caller-supplied delta for one controlled case.

## Evidence and limits

Static Ghidra trace of XP2 SHA `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
The installed November hotfix is SHA `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
The earlier [full code-section comparison](csc-ai-xp2-november-hotfix-20261106.md)
establishes instruction equivalence across those binaries.

| Native evidence | RVA |
| --- | --- |
| Candidate analysis computes readiness and calls district `NetValue` | `0x3e30b9` |
| Existing-improvement type and pillage gates | `0x52a6dc`–`0x52a6ed` |
| Improvement valuation and subtraction | call `0x52a731` → `0x530690`, subtraction `0x52a74f` |
| Resource valuation and subtraction | call `0x52a764` → `0x528700`, subtraction `0x52a77b` |
| District-creation yield and credit | call `0x52a784` → `0x2c4470`, credit `0x52a7c7` |
| Pillage accessor and setter | `0x1e140`, `0x25cfa0` |
| Improvement adjacency, yield conversion and income discount | `0x25f890`, `0x52b110`, `0x528310` |
| Improvement housing, modifier and separate improvement `NetValue` | `0x5298e0`, `0x529ed0`, `0x52a8c0` |

The earlier `ValueManager_NetValue_District_52a440.txt` export in
`Desktop/Codex/csc-native-ai-analysis-20261028/final-helper-exports/` corroborates
the two subtracts and one addition in disassembly. The analysis is static.
The exact Q8 debit in a played city, the handling of individual CSC supplier
effects in this helper, and the strength of a preservation adjustment still
need a controlled comparison.
