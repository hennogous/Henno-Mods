# Fashion House implementation review

The approved Stage 4 design is implemented and covered by the Tailors phase
validator. In-game acceptance is pending. Build CSC in ModBuddy, fully restart
Civ VI, and use a game with the current build for the scenarios below.

## Building and material exchange

- Fashion House unlocks at Humanism after the Textile Workshop; cost 250,
  maintenance 3, one Citizen slot yielding 1 Culture and 2 Gold.
- The local Textile Workshop supplies 1 Culture and receives 1 Production and
  1 Gold from the Fashion House.
- Adjacent improved Specialty Materials supply 1 Culture. With M&C enabled,
  Specialty Industries supply 2 and Corporations 3 instead.
- The Fashion House provides 1 regional Amenity within six tiles. Compare
  eligible cities at distances five, six and seven.

## Customer population exchange

Each adjacent functioning Amphitheater (including its direct replacement),
Bolshoi Theatre, Broadway or Sydney Opera House uses **its own city's population**.
The customer building receives Culture; the Fashion House receives Production
and Gold. Each receives the following amount for that customer site:

| Customer population | Each yield |
|---|---:|
| 4 | 0 |
| 5 | 1 |
| 9 | 1 |
| 10 | 2 |
| 55 | 11 |

Test a population-15 seller serving a population-5 customer, then reverse the
populations. Expect one stack, then three. Two population-9 customer cities
contribute two stacks altogether. Multiple customer sites in one city and
multiple Fashion Houses serving one site contribute independently. Same-city
transactions also work. Pillage/remove a building, change ownership, or cross
a population threshold and confirm both sides update.

## Performance services

At Opera and Ballet, supply the Fashion House with improved Base **and** Specialty
Materials. An adjacent Theater Square with an Amphitheater establishes the normal
Stage Manager with one usable Citizen slot. The three named Wonders establish
their own performance services on their actual tiles, with zero Citizen slots.

Every eligible destination gains 2 Tourism and one Great Artist point per
adjacent supplied Fashion House. Check several Wonders in one city and different
build orders, then save/reload. Each service must stay on its own host tile.
Losing supply deactivates the effects while the established service persists.

City Breakdown nests the service beneath its actual Wonder. Check both the
standard plot tooltip and Simple UI Adjustments tooltip, each service's Civilopedia
page, and a separate MCUIS icon/notification stream for each venue type.
Multiple supplied Fashion Houses from different cities stack within each venue's
ability. Two sources give that venue +4 Tourism and +2 Artist points; losing
one source leaves +2 Tourism and +1 Artist point and sends a DECREASED transition for that venue.

Regression checks cover the native API returning no values for an unset property
and unavailable city collections during startup. Both previously stopped the
Wonder reconciler before establishment. The script retries after loading and
in response to building, improvement, district, ownership and civic changes.
For a previously affected save, reload with Opera and Ballet and both material
supplies present: missing services must be established without Lua errors.
The player scan must also tolerate an alive player with no city collection and
nonconsecutive player IDs. It enumerates actual alive players, sorts their IDs,
and processes each available city collection independently. A non-city player
must never silently stop grants to other players. The read-only FireTuner check
at `project/tools/firetuner/inspect_wonder_services.lua` reports player collections,
supplied Fashion Houses, adjacent plots, and each Wonder's actual service location
and readiness properties.
Quarter pillage checks must use the gameplay district instance returned by
`CityDistricts:GetDistrict`, then `district:IsPillaged()`. The collection's
`IsPillaged` method is unavailable in gameplay and must not appear in this path.
Four mechanically real Tourism anchors present the Theater Square, Bolshoi,
Broadway and Sydney service abilities separately. Their icons use Tailors atlas
indices 12â€“15, with each icon linking to its own service Civilopedia page. Each anchor totals
its contributing Fashion Houses independently; repeated refreshes with unchanged
state must not send duplicate notifications. Great Artist point attachments
share the corresponding Tourism gates and do not create additional icons.

### Live verification, 8 October 2026

In Henno's running save, Pokrovka (player 0, city 65536) had a supplied Fashion
House, Opera and Ballet, and adjacent Bolshoi and Broadway, but neither service.
The game reported 17 players with actual alive IDs 0â€“14, 62 and 63, confirming
that a player count cannot serve as an ID range. The gameplay district collection
also lacked the UI pillage method.

After loading the corrected production reconciler, Ballet Dancer was created on
Bolshoi's actual plot 796 and Musical Actor on Broadway's actual plot 794. Both
city and plot readiness flags and establishment flags were 1. Their Culture
attachments and leaves were active with one subject each. MCUIS returned the
distinct venue icons and +10% Culture/+1 Great Artist point descriptions, and
the notification cache held one stack for each venue. Refreshing it preserved
those counts. Sydney was not present in this save; its shared placement path is
covered by the automated scenarios. This evidence does not constitute acceptance
of all Stage 4 review scenarios.

## Domestic trade

A qualifying domestic route from a city without a functioning Tailors' Quarter
to a supplied Fashion House grants the origin 1 Culture and 1 Amenity; the
Fashion House receives 1 Production and 1 Gold. This is an independent transaction
from the Tailor's: with both supplied buildings present, expect two complete
transactions. Check multiple routes, route termination, and origin exclusion.
Better Trade Screen and Unit Panel previews include both channels; Simple UI
Adjustments classifies both Culture contributions under Outgoing Trade Routes.

## Automated verification

`project/tools/quarter_contracts/validate_phase.py tailors stage4 --handoff`
checks current SQL against an in-memory copy of the gameplay cache, localization
generation and chapter structure, modifier graphs, service destination rules,
actual-location UI consumers, ModBuddy wiring, and production Lua scenarios.
The cache is a schema fixture; passing these checks is not live-game acceptance.

### Venue-specific service identities (8 October 2026)

The Theater Square retains Stage Manager. Bolshoi Theatre uses Ballet Dancer, Broadway uses Musical Actor, and Sydney Opera House uses Opera Singer. Each has its own name, notification strings, icon and Civilopedia page; ability links and City Breakdown right-clicks open the corresponding page. Culture and Great Artist point effects are unchanged. Only Stage Manager adds an assignable Citizen slot. The Tailors XCF bottom row remains indices 12, 13, 14, 15 in that venue order.

## Stage 4 Tourism amendment — 13 October 2026

Henno revised the canonical design and explicitly requested implementation of
+2 Tourism in place of each service's +10% Culture bonus. All four venue branches
now use the Bakers Stage 4 modifier type,
`MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE`, with `Amount=2` and no
`YieldType` argument. The subject is the eligible Theater Square or the exact
Wonder district instance selected by that venue's existing plot readiness gate.
Each supplied adjacent Fashion House contributes independently; two sellers give
+4 Tourism and +2 Great Artist points, falling to +2 Tourism and +1 point when
one loses supply. Service descriptions, civic text, Civilopedia service prose,
ability previews and all notification states use Tourism.

The canonical file hash and approved foundation/stage4 slice hashes were updated
for this authorized amendment. Foundation includes the full `buildings` subtree,
so the service effect change also changes its slice hash. User runtime acceptance
remains pending. Earlier dated Culture observations describe the previous build
and do not validate the revised Tourism behavior. Rebuild and reload before
checking Tourism at all four venues and the two-seller decrease transition.

Automated verification of the amendment passes: Quarter contract validation,
Stage 4 cumulative handoff validation (including executable Lua stacking and
notification scenarios), localization generation, SQL style and ModBuddy wiring.
These checks do not replace in-game Tourism review.

## Stage Manager Citizen-slot notification correction — 13 October 2026

The Theater Square Stage Manager NEW notification now states +1 Citizen slot
in the Theater Square. Its REMOVED notification states that the established
service and slot remain, matching Sacristan's persistent-building wording.
Supplier increases/decreases affect Tourism and Artist points only; Wonder
services have no Citizen slots.

The shared LP.NOTIFICATION.SERVICE_STATE pattern previously specified state
families, signs and punctuation but omitted intrinsic-slot disclosure. The
Stage 4 checks verified Buildings.CitizenSlots separately from notification
existence, Tourism wording, venue identity and dynamic signs. They therefore
passed incomplete NEW/REMOVED text. The shared pattern and Stage Manager
contract now explicitly require slot disclosure/persistence, and executable
text assertions tie those requirements to the actual building rows. Regression
checks reject missing NEW slot text, missing REMOVED persistence text, supplier
increases claiming another slot, and Wonder notifications falsely granting one.

## Read-only live Wonder district verification — 13 October 2026

In Henno's running Tenochtitlan save (player 0, city 65536), enumeration of
`player:GetDistricts():Members()` confirmed separate DISTRICT_WONDER instances:

| Host | District ID | Plot index |
|---|---:|---:|
| Bolshoi Theatre | 262146 | 672 |
| Broadway | 327683 | 599 |
| Sydney Opera House | 393220 | 600 |

All three host-plot service READY properties were 1. The loaded game's
BuildingModifiers contained the Theater Tourism attachment and all four
Artist-point attachments, but none of the three Wonder Tourism attachments.
It was therefore still running the temporary baseline configuration even
though the source had been re-enabled. This verifies distinct district instances
and exact host markers; it does not verify re-enabled Tourism delivery or a
remote earlier-Wonder build-order scenario. Rebuild/reload for that check.

Debug context IDs were resolved with LSQ: GameCore_Tuner was 9 and
CSC_UI_Notifications was 140 in this session. CityDistricts had no Members
method; the player's district collection supplied the actual instances.
The requested FireTuner2 process was closed to free the connection. All queries
were read-only; no building, property or save changes were made.

## Shared SQL eligibility for normal and Wonder services — 14 October 2026

To prevent unlock/supply drift, normal Stage Manager and Wonder service effects
share this SQL gate graph:

- `REQSET_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ`: improved Base AND Specialty supply.
- `REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ`: nested supply set AND Opera and Ballet.
- `REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ`: nested producer set AND an eligible
  adjacent service customer.

The existing normal-service grant and all Tourism/Artist-point attachment
modifiers retain that complete EFFECT_PREREQ owner gate. Their subject gates
select the appropriate Theater Square or exact ready Wonder plot.

A Fashion House-owned SQL modifier uses only PRODUCER_PREREQ to write
`CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE=1`. Wonder placement Lua consumes
that authoritative result; it no longer names Opera and Ballet or separately
reads the material-supply flag. Lua retains physical producer/host functioning,
same-owner adjacency, exact Wonder location and persistent-building handling.
It then writes the existing venue-specific READY markers.

The producer gate deliberately excludes customer readiness, since readiness is
computed from producer eligibility. Using the full effect gate for the source
property would create a circular dependency and prevent initial establishment.

All 21 Fashion House executable Lua scenarios and the cumulative Stage 4
validator pass. SQL graph assertions enforce both nested set targets, the exact
producer property modifier and shared normal/effect owner gates. New scenarios
prove that the Lua follows SQL output without a duplicate civic/supply rule,
and preserves services when eligibility clears. The fixture simulates SQL
property outputs; live nested-set/property evaluation still requires a rebuilt
Civ VI game. Review unlock, either material loss/restoration, producer pillage,
and reload against both normal and Wonder services.
