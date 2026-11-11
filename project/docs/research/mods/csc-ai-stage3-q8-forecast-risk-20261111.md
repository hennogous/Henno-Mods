# Stage 3 Q8 population-return forecast risk

11 November 2026. Read-only source/native-static review requested by Henno.
No game was run; the placement goal remains paused. This concerns inspected
worktree changes, not a qualified installed build.

The 15-bit change improves yield representation; it does not establish AI-safe
forecasting. It retains property-gated per-population consumers with a larger
coefficient range. Inflation is possible if an AI consumer reaches these roots
and drops the bit requirements. A new Quarter/building honeypot is unproved.

## Actual-state calculation

Lua sums functioning same-owner seller/customer transactions, deriving a total
from customer population times transaction amount. It divides by the receiver's
population, rounds upward once to 1/256 units and caps at 32767 units. SQL applies
active bits as Bit/256 yield per receiving citizen. For example, a 1.01 target
in a population-10 receiver becomes 26/256 per citizen, or 1.015625 total.
This is arithmetic, not live validation. Without saturation the rounding uplift
is less than receiver population/256 yield. Q8-suffixed properties prevent old
decimal-rate bits from being read with the new divisor. Stage 4 retains separate
whole-stack units.

## Native risk

Rechecked Ghidra reference SHA-256
324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c,
image base 180000000, per-population initializer RVA 467e00. It reads Amount as
fixed-point, tests and stores the value shifted right by eight. Positive
coefficients below one produce no descriptor here. This confirms AI-N076;
it is not a claim about gameplay discarding fractional yields.

| Encoding | All declared coefficients summed | Sum after this initializer's individual integer conversion |
| --- | ---: | ---: |
| Old twenty bits, Bit/10000 | 104.8575 | 101 |
| New fifteen bits, Bit/256 | 127.99609375 | 127 |

The eight new fractional coefficients drop out. The remaining seven are
1, 2, 4, 8, 16, 32 and 64. **127 is a conditional coefficient sum per payout
stream, not an observed yield, utility value, district score or score delta.**
Timing, recipients, population, weights and reachability still matter.
The inspected requirement compiler can omit unsupported plot-property gates
(AI-N028). Thus fewer bits alone does not prevent credit for inactive large
amounts. Dropping fractional coefficients can instead omit genuine income.

## Consumer boundary and next evidence

The generated payout bits attach to DISTRICT_CITY_CENTER through DistrictModifiers,
not to Bakery/Tailor BuildingModifiers. The inspected candidate routes do not
rerun CSC's transaction writer for a hypothetical chain. A producer-only capture
cannot establish these consumers' contribution or prove they inflate a Quarter's
future-building forecast.

Keep the gameplay rounding correction. Before adding an AI deduction, compare
old/new consumers with zero and actual transactions, identify the native caller,
and trace their contribution into district/building comparisons. Do not subtract
the encoding maximum as though it were a measured error.

## Source snapshot

Paths are relative to Civ Supply Chains. Gameplay edits belong to the separate
implementation; these hashes identify the reviewed worktree content.

| File | SHA-256 |
| --- | --- |
| Lua_UI/CustomerPopulationReturns/CSC_CustomerPopulationReturns.lua | 3bdc1dd36be7f3927601694cea46d1b194b36838134e8eb618fef4dbe540e981 |
| Data/CSC_Q_ALL.sql | 2ddc30b2dea4b3e9451a867274a2377522d4db77d075e7db68c7147aefac7f67 |
| Data/CSC_Q_BAKERS.sql | 463e8f284e31e75f69e6180292c9f7eceed9ec7f46250d998f876e282f405353 |
| Data/CSC_Q_BAKERS_GOLD.sql | 487fd6c0eaa84d76488859673d2229dda7c7317419aba7540e6a1f7e2448b3bc |
| Data/CSC_Q_TAILORS.sql | 2daba0ccd450d3e9c8a6f19ea28594bb0509a6210152b86cb46e839442c89706 |
| Data/CSC_Q_TAILORS_GOLD.sql | 49653683148f48f8dba17fd1684c625ce2c9123940e59b01b2a6e9ee2b1587ba |

Related: [coverage](../../civ6-ai/topics/csc/forecast-coverage.md),
[prior initializer evidence](csc-ai-late-placement-20261105.md),
[consumer boundaries](csc-future-economy-forecast-20261103.md).
