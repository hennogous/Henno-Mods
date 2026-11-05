# Late district score adjustment and Bakers calibration

The late placement experiment uses the exact Online turn-1 checkpoint from the
Mill and building study. The shared controller runs each arm to turn 2 with the
archived CSC package. Delhi's Bakers candidate is plot 1210 at (26, 16). It is
owned, revealed, empty, flat and inland. The scope is this city's district-site
choice. [Mill and building study](csc-ai-mill-building-study-20261105.md)

## Placement boundary

In the pinned XP2 DLL, `DoTurnActivate` calls `CalculateDistrictValues` at RVA
`3e293c` and later reaches `CheckForDistrict`. The completed district matrix is
at CityBuild `+0x518`. Both `GetBestDistrict` and plot-specific `PresentValueOf`
read the district values through row `+0x20`. The trial verifies that the target
row aliases the matrix on entry and return. It checks native row eligibility,
ownership and reservation state, a positive pre-aggregation score, and an exact
pre/post match to the control before changing the one writable cell.

```mermaid
flowchart LR
  A["Native site forecast"] --> B["Future building addition"]
  B --> C["Completed district-site score"]
  C --> D["One measured CSC correction"]
  D --> E["Native district selection"]
  E --> F["Present value and district preparation"]
```

Static evidence uses the pre-existing Ghidra project for XP2 SHA-256
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
Functions `3e2820`, `3dfee0`, `3e0ee0`, `3e4a50` and `3e7f40` establish the
ordering and the row readers. The runtime test establishes whether they consume
a real adjustment in the game.

## Native control and pulse

Both arms matched the saved source, live district map, unmodified site value
of 77,534 Q8 and completed Bakers value of 104,621 Q8. The control selected
Neighborhood at plot 1358 with 248,223 Q8 and submitted a production contract
with logged value 969. The pulse added 143,858 Q8 to the Bakers cell after the
building pass. Its resulting 248,479 Q8 was one utility unit above the control
winner. This deliberately large pulse tests the score boundary.

The native selector chose Bakers at plot 1210 and plot-specific present value
returned the same 248,479 Q8. The native `Build City District` tree decoded
Bakers at 970 utility, reserved (26, 16), and accepted a Craftsmanship civic
goal. The pulse's first automated audit required an immediate construction
contract. The tree instead entered the prerequisite branch. The verified
closure, matching source, exact reader values and tree receipts allow the
calibrated arm to reuse the control and pulse evidence.

## Calibrated flat inland Bakers forecast

The independently reconciled native building ledger traces the actual consumed
roots and the three raw values admitted to the district. Values are signed Q8
utility, with 256 Q8 per utility unit. Delhi's original site score is 77,534 Q8
before building aggregation and 104,621 Q8 after it.

| Forecast | Raw value | Inapplicable credit | Revised raw value | Revised district contribution |
| --- | ---: | ---: | ---: | ---: |
| Wind Mill | 1,838 | 2,560 for its hill Production | −722 | 0 |
| Bakery | 14,269 | 1,536 for returns to Water Mill | 12,733 | 12,733 |
| Café | 10,980 | 1,024 for returns to Water Mill | 9,956 | 9,956 |
| Building total | 27,087 | | | 22,689 |

The Wind deduction is 1,838 Q8 at the district layer because Civ only adds
positive raw building forecasts. Water is unavailable on the inland plot and
its own forecast was also excluded by native mutual-exclusion ordering. The
Bakery and Café deductions remove only their measured Water recipient credit.
The total correction is −4,398 Q8, giving a score of 100,223 Q8. All five roots
are attributed to their enclosing buildings and reconciled to the consumed
native modifier values before calculating this difference.

The first correction replay exposed an alias in the native building cache.
The guard looked for the raw Wind value after the pass and safely rejected
the write. This calculation uses the same backing storage for the raw input
and the mutable prerequisite vector. Wind's slot holds 1,838 Q8 on entry and
27,087 Q8 on return, after Bakery and Café values have been rolled into it.
The writer now compares the three raw building values captured at entry and
the completed district-site score captured at return.

The corrected replay evaluated the main CSC Lua library in `GameCore_Tuner`
and returned −4,398 Q8. The writer changed the one Bakers cell from 104,621 to
100,223 Q8 and read it back. The independently captured ledger matched the
control, including the five consumed root credits. Neighborhood remained the
winner at 248,223 Q8 and Delhi submitted the same five requests as the control.
This arm verifies the measured deduction and the unchanged decision in this
fixture. The pulse establishes that the same boundary can change a decision.

These credits belong to Delhi's calculation. The companion city in the same
study credited its Wind hill step at 2,304 Q8. Calibration uses the current
building's consumed root result, including its timing and rounding. A shared
Q8 format alone cannot supply a price for missing material returns, customer
sales or specialist work. [Forecast coverage map](../../civ6-ai/topics/csc/forecast-coverage.md)

`Civ Supply Chains/Lua_UI/AI/CSC_AI_QuarterPlacement.lua` implements the two
rules using measured inputs. The main CSC mod imports this policy library
alongside `CSC_AI_AdjacencyScan.lua`, the existing scanner moved from test tooling.
`project/tools/native_ai/late_placement` owns the saved-world fixture, accounting
checks and Frida adapter. The later [CE development implementation](csc-ce-late-score-api-20261105.md)
adds a Lua API at this boundary. A recurring CSC policy still needs fresh
component evidence for the current calculation.

## Evidence and restoration

The shared controller replayed the same saved world from turn 1 to 2 in each
successful arm. Under `Desktop/Codex/csc-late-placement-20261105`, the control
and pulse are in `run-02`, the guard rejection is in `run-03`, and the verified
correction is in `run-04`. The correction result and frozen trace have these
SHA-256 digests:

| Receipt | SHA-256 |
| --- | --- |
| `run-04/result.json` | `85a37d725d973512df58efd5a095fd0abb5d71a4da2463875b4a3d472df115f9` |
| `run-04/correction/trace-frozen.json` | `3b71fdde7affae94a0f00ba90b0fdb3985df45636dc4e92ae29879416ae10e00` |

The correction closed with native exit code 0, verified preferences and a
verified retirement of the isolated package. The interrupted guard-rejection
worker preserved the exit acknowledgement and restored preferences. Its
package was later retired by hash with no native owner present. The original
worker did not leave a native exit-code receipt for that rejected arm.

## Pricing the next missing effects

The fixed-point timing kernel at `528310` and interval wrapper at `528660` apply
the income stream across readiness and the forecast horizon. The reconstruction
matches all 24 captured reduced-step Mill callbacks. Effect-specific valuation
still determines the amount sent to that kernel, the recipient and rounding.

| Relationship | Native analogue and calibration boundary |
| --- | --- |
| Producer returns to an improved plot | `485a10` discounts a raw yield stream, halves it, normalizes by the yield default and rounds to whole utility. Using that analogue, one eligible plot with +1 Production and +1 Gold prices at 1,792 Q8 with the captured Delhi Wind timing and 1,024 with Café timing. These are model values. The missing improvement iterator did not deliver an observed credit. Recipient eligibility, sustained use and overlap still need evidence. |
| Incoming material yield to a producer | `475a50` uses the player's yield bonus and applies half value for an absent building recipient. A captured +1 Food root in Delhi's Wind context has value 1,280 Q8. Current delivered material income can also enter through `GetYieldChange`. Its overlap must be resolved before pricing a new addition. |
| Population sales | A qualifying population-15 Market gives the gameplay seller and customer streams 1.575 each per turn. The hypothetical initializer at `467e00` shifts its coefficient right by eight before rejecting zero, so sub-unit positive bit coefficients are discarded on that path. The City Center consumers were outside the producer capture, and larger bit coefficients can survive. A placement correction needs current recipient income and a measured native overlap. |

[Native forecast interpreter evidence](csc-future-economy-forecast-20261103.md)
