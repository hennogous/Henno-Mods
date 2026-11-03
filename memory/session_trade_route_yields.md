# Trade-route Food/Amenity and SUIA — 24 October 2026

Human clarified: normal rules prevent duplicate routes between the same city pair;
each route to a different supplied Bakery city must grant the full +1 Food and
+1 Amenity. Previous assistant explanation that +1 was intentionally capped was
wrong: it described a source bug. Cafe imports are a second independent channel.

Native turn8 manual game: Alexandroupoli196609 -> Pella65536, owner0. Bakery
supply=1; import/export/revision properties all nil, native Food only workedtiles5,
Amenities0. Empty scanner UI context hidden=true suppressed SetUpdate. With human
FireTuner closed, woke existing context via SetHide(false), no turns/routes added;
native import/export1, revisions1, Food+1 modifier, Amenities1. Human confirmed
correct SUIA reclassification and Amenity visible. Game remains open/human-owned.

Permanent source SetHide(false)+LoadScreenClose queue. Bakery/Cafe import receiver
now derives count bits; UI reconciles missing legacy bits; owning Bakers SQL pays
Food/Amenities per bit, SUIA registry tracks corresponding Food bits. Source only,
no build/deploy/restart. Existing Bakery CitizenSlots user edit preserved. Four
focused+11lifecycle actualLua51 tests and18phase regressions PASS; SQL layoutPASS.
Native multiple-destination stacking after rebuild/reload still pending.

Durable evidence/contract: project/docs/integrations/csc-trade-route-yields.md.
Human explicitly requested fixing Tailors too. Tailor/FashionHouse Culture and
Amenity now use the same count-bit payouts in owning Quarter SQL; shared receiver
and missing-bit reconciliation cover all4importchannels. SUIA registry includes
all Culturebits; implementation contract/E.TRADE_STACKING and assertions updated,
including checking every companion registry amount/propertygate. Six focused+
11lifecycle actualLua51+18phase regressions=35PASS. Full validators retain their
baseline blockers: BakersreferenceSHA drift and Bakersmaterials declaration needs
reconciliation. No control/hash/acceptance changes and no native install/build.
All four current channels' stacking corrected SOURCE ONLY; do not deploy into
human game or claim native multiroute validation.

Human then requested equal international exchanges and UI treatment. Removed
owner-equality restrictions from shared scanner, BTS previews and Trader panel
for Bakers/Tailors. Source gates/flat amounts/countbits unchanged. BTS adds CSC
after native international multipliers, matching real city/building payouts.
SUIA already nationality-neutral; executed test proves combined domestic/foreign
Food/Culture reclassification preserves totals. Host updates foreign-owner city
snapshots through existing bridge, no gameplay shortcut. Pattern renamed to
GP.TRADE.SUPPLIED_ROUTE with implementation/validator/catalog wording updated;
localization format IDs remain legacy LP.TRADE.DOMESTIC_* but prose has no gate.
Four new cross-owner/UI tests;39focused totalPASS,21actualLua51. Source ONLY;
no build, deploy, game commands or native international-route claims this turn.
Six route-contract validator regressions alsoPASS; finalfocused total45PASS.
Installed CSC trade-route skill reference updated for allroute eligibility,
fixedamount UI parity, currentpaths and hiddencontextlesson. Latest fullvalidator
also reports concurrently changed Bakerslocalization sourceSHA and generatedtext
outofdate in addition to prior coreSHA/material blockers. Neither localization
source/output nor control locks was changed by this trade task; preserve them.
