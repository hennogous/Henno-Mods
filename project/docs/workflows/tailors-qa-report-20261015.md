# Tailors Quarter QA report 15 October 2026

> **Correction from Henno, 15 October:** the material-return issues were false
> reports. Material returns work. The material-return findings below are retained
> as historical test observations, not current gameplay defects.

Follow-up: [source fixes, cross-Quarter audit and rerun status](tailors-qa-fixes-20261015.md).

The expanded QA run found **five confirmed defects**, including the previously
reported ownership bug. A sixth finding concerns the six-tile regional Amenity
boundary and needs confirmation in an ordinarily settled game. No gameplay fix
is retained. This is a broad core-mechanics run, with the remaining coverage
listed below; it is not full gameplay acceptance.

The tested configuration was Gathering Storm, CSC alone, with Monopolies and
Corporations enabled. Expectations come from `docs/content/quarters/tailors.md`
and the Tailors contracts. A disposable world provided controlled resources,
districts and customer populations. Real city purchase and trade commands were
used where specified. Forced setup does not establish construction eligibility.
Shadow's interruption was recovered from the completed checkpoint save.

## Confirmed defects

| ID | Issue | Circumstances | Expected and observed |
|---|---|---|---|
| CSC-QA-001 | Purchased material leaves district adjacency stale | Buy an unowned Base or Specialty resource tile adjacent to an existing Tailors' Quarter | With two existing material tiles, Production should rise from +2 to +3. It stays +2 until a refresh. |
| CSC-QA-002 | Quarter notifications fail after loading saved ability data | Save with established Quarter abilities, reload, then trigger a notification refresh | Refresh should compare saved and current abilities. It instead raises a Lua error and aborts. |
| CSC-QA-003 | New Tailor does not immediately deliver customer Culture | Purchase a Tailor beside existing Markets or Temples, without changing the customers' populations | The seller receives its returns, but customer Culture stays unchanged until a population update. |
| CSC-QA-004 | Base Industries and Corporations receive an extra Production and Gold | M&C enabled; a Base-material Industry or Corporation is adjacent to one Textile Workshop | Industry receives +3/+3 instead of +2/+2; Corporation receives +4/+4 instead of +3/+3. |
| CSC-QA-005 | Specialty improvements receive no Fashion House material return | An improved Specialty resource is adjacent to a Fashion House | Ordinary, Industry and Corporation improvements receive +0 Production/+0 Gold instead of +1/+1, +2/+2 and +3/+3 respectively. |

### CSC-QA-001 Purchased material leaves district adjacency stale

**Medium priority.** Prepare two owned adjacent material resources and a third
unowned one. Buy the third tile using the normal city purchase command. Confirm
the purchase succeeded and the tile's owner changed, then inspect native district
Production in a separate command. The bonus remains +2; an explicit adjacency
refresh makes it +3.

The gameplay listener registers `PlotOwnershipChanged`, which is absent in the
tested game. The purchase emits `CityTileOwnershipChanged`. A temporary live
subscription to that event made the same purchase update correctly; removing it
reproduced the failure. That diagnostic subscription and the temporary source
edit were removed. Recovery at the next normal turn was not measured.

See [the original reproduction report](gameplay-qa-findings-20261015.md).
Evidence is under the original evidence root's
`diagnostics/012-native-purchase-with-old-subscription.txt` and
`diagnostics/013-old-subscription-reproduces-stale-purchased-resource.txt`.

### CSC-QA-002 Saved ability keys break notification refresh

**Medium priority.** Establish Dockmaster, Sacristan or performance Services so
that the notification system caches their effects, save, and reload. Subsequent
building or improvement changes call `OnRefreshCityQuarters`, which errors at
`CSC_UI_Notifications.lua:209`. A normal Tailor purchase reproduced the error;
the purchase itself completed.

The loaded cache contains numeric hashes for effect identifiers and for the
nested `StackAmount` key. The handler indexes its current metadata using string
effect identifiers and reads `v.StackAmount`. For example, the saved Dockmaster
entry's numeric key maps back to its expected effect through `DB.MakeHash`, and
its hashed `StackAmount` key contains 1, while `v.StackAmount` is nil. The first
metadata lookup fails and the refresh cannot reach its final cache update.

This is a notification failure, not evidence that all associated gameplay
benefits disappear. The affected cache held Dockmaster, Sacristan and all four
performance Service effects. Evidence:
`closing-probes/002-diagnose-serialized-notification-cache.txt`, plus the event
stack traces in `recovery-final/007-purchase-tailor-normally.txt`.

### CSC-QA-003 Customer Culture waits for a population update

**Medium priority.** Use an existing customer city with a Market and Temple at
population 10, and a second customer city with a Market at population 6. Their
districts are adjacent to the supplier's Quarter. Start without the supplier's
Tailor and capture the customers' Culture after population recalculation.
Purchase the Tailor through the normal Gold purchase command.

The population-10 customer should gain approximately +2 Culture and the
population-6 customer approximately +0.6. The combined assertion repeatedly
failed on the first customer: its delta was **0**. The seller's Production and
Gold correctly gained approximately +3.6 each, including its local Workshop
exchange. Thus the purchase and supplier-side transactions worked.

Changing the customer populations and returning them to 10 and 6 produced
Culture deltas of **2.03125** and **0.60764**, within the native fixed-point
tolerance used for the declared +2/+0.6 effects. This confirms an update problem
on the customer side. Its exact recovery time without population changes remains
unmeasured. The first failed assertion does not independently establish the
second customer's immediate pre-refresh delta.

Evidence: `recovery-clean/045-purchase-tailor-normally.txt`, samples
`046` through `049`, `050-purchased-tailor-receives-customer-returns-plus-local-exchange.txt`,
and `052-population-refresh-preserves-intended-customer-culture.txt`.

### CSC-QA-004 Base Industry and Corporation returns stack too high

**Medium priority.** In M&C mode, put a Cotton Industry adjacent to exactly one
Textile Workshop. Measure the native resource plot's Production and Gold with
the Workshop absent, then add the Workshop and measure again. Keep the resource
and improvement unchanged between the two measurements. Repeat with a
Corporation.

An ordinary improvement correctly receives **+1 Production/+1 Gold**. The
Industry instead receives **+3/+3**, and the Corporation **+4/+4**. Both tiers
were reproduced with stable improvement baselines. These are CSC deltas, with
the improvement's own yields already present in the baseline.

The ordinary Workshop attachment matches the material on either advanced
improvement and grants +1. The M&C attachments additionally grant the full +2
or +3 rather than reaching the designed totals. The Gold companion repeats the
same structure. No multiplier from multiple Workshops was needed.

Evidence: `final-diagnostics/006-observe-both-material-yields-improvement-industry.txt`
and `010-observe-both-material-yields-improvement-corporation.txt`.
The earlier failing assertions are in `closing-probes/`.

### CSC-QA-005 Specialty improvements have no material return

**Medium priority.** Put a Dyes Plantation adjacent to a Fashion House. Compare
the native resource plot's yields with that Fashion House absent and present,
leaving the improvement unchanged. Repeat for a Dyes Industry and Corporation.
All three measured deltas were **0 Production and 0 Gold**.

The expected ordinary return is +1/+1, rising to total +2/+2 and +3/+3 in M&C.
Source inspection also finds no Fashion House attachment delivering those plot
yields. The Specialty improvement attachments deliver Culture **to the Fashion
House**, which is the opposite side of the transaction. That Culture working
does not establish delivery to the material producer.

Evidence: the three `observe-specialty-tier` files in `final-specialty/`.
Those final commands also recorded unrelated vanilla Minimap errors from the
artificial world; the missing plot-yield implementation is independently visible
in the tested SQL.

## Additional findings requiring validation

**Six-tile regional Amenity boundary.** With only one Fashion House supplying
regional Amenities, cities at distances 2 and 5 gained +1, a city exactly 6 tiles
away gained 0, and one 7 tiles away gained 0. The six-tile assertion failed in
four samples. A normal Fashion House purchase repeated the same pattern.
The native building location was verified as the Quarter plot, and the boundary
city was distance 6 from both that plot and the supplier's city centre. This is
a reproducible failure in the fixture. It still needs an ordinary settlement
reproduction because the fixture forces terrain, cities and district placement.
Evidence: `recovery-clean/081` through `084`, and the source-location and
purchased-regional-Amenities probes in `closing-probes/`.

**Pillage invalidation.** Forcing a Fashion House into the pillaged state left
its Amphitheater customer with +2 Culture instead of clearing that transaction.
The customer returned to the expected active value after repair. This used a
debug state mutation; a real enemy pillage event was not reproduced. A forced
Broadway pillage also left returns unchanged, but Wonders are not an ordinary
pillage target, so that sample is not a gameplay bug reproduction. Evidence:
`closing-lifecycle/037` through `040` and the corresponding setup files.

**Great Person point delivery.** Immediate Admiral, Prophet and Artist rate
comparisons did not change as expected. Vanilla Writer and other point rates
also read 0 in the final fixture, and the bounded autoplay attempt stayed on turn
1. These samples do not isolate a CSC defect. Actual point accrual across a
completed turn, service deactivation and overlapping supplier GPP remain open.

## Verified coverage and remaining work

| Area | Result |
|---|---|
| Offline production-script suites | 39 tests passed: Fashion House 21, Stage 3 bridge 4, Stage 4 population returns 14. |
| Material and local exchanges | Native resource adjacency counts 0/1/2/3; Workshop Culture from ordinary/Industry/Corporation Base supply; Fashion House Specialty Culture; settled Workshop, Tailor, Fashion House and Lighthouse exchanges checked. Material producer defects are listed above. |
| Fashion House population scaling | Native customer populations 4/5/9/10/55 passed for all four customer venue types, with customer-side Culture and supplier-side Production checks. Each site's actual vanilla Culture was baselined independently. |
| Services | Establishment and persistent structures checked; supply loss/restoration toggled Tourism; overlapping Fashion Houses stacked Tourism per adjacent venue and removing one supply preserved the other. Sacristan +10% Faith passed. GPP remains open. |
| Citizen slots | Workable Quarter 2 total, Harbor 2 including Lighthouse, Holy Site 3 including Shrine and Temple, and supplied Theater Square 2 including Amphitheater passed. Three Wonder Services have zero declared slots; their exact saved host locations survived reload. Worker yield delivery was not tested. |
| Trade | A real domestic route delivered both stages' Culture and Amenity transactions and both Production export channels; removing the Trader cleared both import flags. More routes, foreign routes, origins with a Quarter, pillage and capture cases remain open. |
| Save and load | Completed checkpoint reloaded after Shadow's interruption. Local exchanges and all three Wonder service locations persisted. Notification cache failure is listed above. |
| Remaining native scope | River-edge combinations, full district bilateral yields, Dockmaster naval production by era/class, actual specialist yields, normal turn accrual, capture/removal and ordinary pillage lifecycle, unique replacements, optional mods, settings combinations, AI and visual/UI acceptance. |

Phase validation for Stages 3 and 4 stopped on the existing locked-source hash
mismatch for `project/localization/CSC_BAKERS_TEXT.md`. This is a validation
blocker, not a gameplay defect; no gate or source lock was altered.

Early raw failures include incorrect vanilla yield/slot baselines, an out-of-range
Theater fixture, queued Corporation/Wonder popups, and interrupted setup. They
are retained as diagnostics and are not additional confirmed bugs. A completed
normal turn was not established; vanilla Minimap errors followed the forced
terrain setup and autoplay attempt.

## Evidence and repeatability

Expanded evidence root:
`C:/Users/Shadow/Desktop/Codex/csc-tailors-qa-20261015/`.
Original ownership evidence root:
`C:/Users/Shadow/Desktop/Codex/csc-gameplay-qa-20261015/`.
Evidence paths above are relative to the expanded root unless stated otherwise.

The completed recovery save is
`run/CSC Tailors full QA checkpoint 20261015.Civ6Save`, SHA-256
`f6c5577028df4757d3bdfd829926a64c1e70e0bcb9dda7c3b47d99d4c29f8981`.
`tested-source-metadata.json` inventories 54 SQL/Lua source files. The 53 present
in the installed package matched the workspace; the retired, unregistered Ruivo
processor was absent from that package. Existing user
gameplay edits were preserved; this QA work adds tools, fixtures and reports.

Native startup and reload can pass Begin/Continue through Firaxis's
`Automation.SetAutoStartEnabled(true)` path. This run therefore needed no
successful Computer Use click. Popup handling is scripted through FireTuner.
The matrix still needs fixture validation and an interruption journal before it
can be treated as an unattended full acceptance run; its raw command pass count
must not be presented as a gameplay pass count. Original mod preferences and the
native auto-start preference are restored after testing. The installed test
package and evidence are retained.
