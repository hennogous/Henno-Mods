# CSC Grand Eras compatibility proposal

Draft for Henno, 10 October 2026. Scope: Bakers' and Tailors' Quarters only.

Move the Bakery and Tailor to Merchant Leagues, then use Medieval Faires and Guilds respectively to unlock their Services. Keep the early processing buildings and specialty buildings at their existing unlocks. Move the Café's regular Services to Conservation so the Ferris Wheel's Natural History unlock is a prerequisite of the Service civic. Keep every Tailors' Wonder Service at Opera and Ballet, as Henno requested.

This is a design proposal, not an implemented patch or an amendment to the Quarter contracts. Research positions below describe the installed Grand Eras version 31, in its normal unshuffled trees. They indicate research availability, not guaranteed construction dates or equal Science and Culture progress.

## Principles and scope

Regular Services should normally complete a prepared supply chain: the Quarter building and customer become available, the player can build and supply them, and a later research unlock activates the Service. Prefer actual prerequisite ancestry within one tree over simply choosing a node farther to the right. Where a relationship crosses the Science and Culture trees, preserve material and customer requirements and use era spacing to allow preparation; research ordering cannot be guaranteed across the two trees.

Henno explicitly exempts the three Wonder Services from that ordering preference. Ballet Dancer, Musical Actor and Opera Singer retain their common Opera and Ballet gate. Their Wonder hosts can arrive afterward.

The proposal preserves building costs, effects, construction dependencies, resource requirements and customer definitions. Stage 3 and Stage 4 buildings continue to require the Stage 2 building; the proposed research sequence does not add a requirement to construct Stage 3 before Stage 4.

## Proposed Bakers mapping

| Content | Current unlock | Proposed Grand Eras unlock | Position in Grand Eras |
| --- | --- | --- | --- |
| Bakers' Quarter | Craftsmanship | Craftsmanship | Middle Ancient |
| Water Mill | Wheel | Wheel | Late Ancient |
| Wind Mill | Wheel | Wheel | Late Ancient |
| Storekeeper | Feudalism | Feudalism | Late Post-Classical |
| Bakery | Guilds | **Merchant Leagues** | Early Medieval |
| Innkeeper | Medieval Faires | Medieval Faires | Late Medieval |
| Café | The Enlightenment | The Enlightenment | Late Renaissance |
| Groundskeeper | Urbanization | **Conservation** | Late Modern |
| Ride Technician | Urbanization | **Conservation** | Late Modern |
| Horticulturist, with Leugi's Garden | Urbanization | **Conservation** | Late Modern |

Merchant Leagues puts the Bakery into an economy of organized merchants and urban food supply. Medieval Faires then adds hospitality for visitors to an established Market. In Grand Eras, Guilds and Medieval Faires are parallel late Medieval civics, so retaining both original gates would permit the Innkeeper's research before the Bakery's research. Merchant Leagues is an actual prerequisite of Medieval Faires.

Keep both Mills at Wheel. Moving the Wind Mill alone to Grand Eras' Mechanics would put it in middle Medieval and create a large disadvantage for Quarters without a river. Moving both Mills would delay the whole early food chain. The existing abstraction keeps the two terrain options equivalent.

Keep the Café at The Enlightenment. Coffeehouse culture remains an excellent thematic match, and the customer transactions extend its progression: Zoos become available in early Industrial, optional Conservatories in late Industrial, and Ferris Wheels in early Modern. The late Modern Service adds tourism and staffing to those established destinations.

### Why Conservation is proposed for the Café Services

Grand Eras moves the Zoo to Biology, the Garden Conservatory to Medicine, and the Ferris Wheel remains at Natural History. Urbanization is late Modern, later in position than Natural History, but Natural History is not one of its ancestors. A player can complete Urbanization and only later research the Ferris Wheel.

Conservation is also late Modern and requires Natural History. The Enlightenment is also an ancestor of Conservation, so the Café and Ferris Wheel research precede this shared Service gate within the civic tree. The Zoo and Conservatory remain Science unlocks from the preceding era; they are not guaranteed ancestors of a civic.

Conservation fits the Groundskeeper, Horticulturist and tourism from maintained attractions well. It is a weaker thematic match for a Ride Technician than Urbanization. **The conservative alternative is to keep all three at Urbanization**, accepting nominal era/column spacing for the Ferris Wheel rather than guaranteed prerequisite ancestry. The proposed Conservation mapping prioritizes Henno's stated Service ordering preference while keeping the three Services together and at the same broad date.

Keeping the shared gate avoids introducing different research timing for the Café's three customer branches and its existing shared art activation. This proposal does not split their requirement sets.

## Proposed Tailors mapping

| Content | Current unlock | Proposed Grand Eras unlock | Position in Grand Eras |
| --- | --- | --- | --- |
| Tailors' Quarter | Craftsmanship | Craftsmanship | Middle Ancient |
| Textile Workshop | Construction | Construction | Late Classical |
| Dockmaster | Naval Tradition | Naval Tradition | Late Post-Classical |
| Tailor | Guilds | **Merchant Leagues** | Early Medieval |
| Sacristan | Divine Right | **Guilds** | Late Medieval |
| Fashion House | Humanism | Humanism | Early Renaissance |
| Stage Manager | Opera and Ballet | Opera and Ballet | Early Industrial |
| Ballet Dancer at Bolshoi | Opera and Ballet | Opera and Ballet | Early Industrial research gate |
| Musical Actor at Broadway | Opera and Ballet | Opera and Ballet | Early Industrial research gate |
| Opera Singer at Sydney | Opera and Ballet | Opera and Ballet | Early Industrial research gate |

The Textile Workshop remains an early textile preparation and processing building. Its adjacent Lighthouse unlocks at Celestial Navigation in middle Classical. Naval Tradition follows in late Post-Classical, leaving time for both buildings before the Dockmaster.

Merchant Leagues represents the Tailor's professional, commercial market. Guilds then represents the specialization and organization needed to supply ceremonial clothing and staff a Temple. This transfers Guilds from constructing the Tailor to activating its specialized Service. The Temple's Theology unlock is an ancestor of Guilds, as is Merchant Leagues. The Sacristan consequently follows both customer and producer research in the civic tree.

Retaining Divine Right would put the Sacristan and proposed Tailor in the same early Medieval research column on different branches. Retaining the Tailor at Guilds would put its research after Divine Right. Neither gives the desired prepared-building-then-Service rhythm as cleanly as Merchant Leagues followed by Guilds.

Keep Humanism for the Fashion House: Renaissance patronage, individual presentation and elaborate dress remain a strong fit. Opera and Ballet then unlocks the Stage Manager in early Industrial, after both Humanism and the Amphitheater's Drama and Poetry in the prerequisite graph.

Grand Eras' Spinning Wheel is attractive by name but is late Medieval. Putting the Textile Workshop there would make its research later than the Dockmaster's Naval Tradition and compress it against the Tailor and Fashion House. It represents a later technological development than this Quarter's initial processing workshop. No extra Spinning Wheel bonus is proposed.

### Wonder exception

Keep the current common Opera and Ballet gate and the corresponding placement Lua behavior. Grand Eras' ordinary host unlocks are:

| Wonder host | Grand Eras host unlock | Position |
| --- | --- | --- |
| Bolshoi Theatre | Opera and Ballet | Early Industrial |
| Broadway | Mass Media | Late Modern |
| Sydney Opera House | Cultural Heritage | Late Atomic |

Grand Eras moves Sydney Opera House to Pop Culture if the Phanta Louvre building is present. That optional change still does not change CSC's Opera Singer gate. The Wonder Services remain conditional on an existing, supplied adjacent Fashion House and their actual host, rather than gaining separate late research unlocks.

## Customer sequencing check

| Regular Service | Quarter building research | Customer research in Grand Eras | Proposed Service research |
| --- | --- | --- | --- |
| Storekeeper | Wheel, late Ancient | Granary: Pottery, early Ancient | Feudalism, late Post-Classical |
| Innkeeper | Merchant Leagues, early Medieval | Market: Currency, early Classical | Medieval Faires, late Medieval |
| Groundskeeper | The Enlightenment, late Renaissance | Zoo: Biology, early Industrial | Conservation, late Modern |
| Ride Technician | The Enlightenment, late Renaissance | Ferris Wheel: Natural History, early Modern | Conservation, late Modern |
| Horticulturist | The Enlightenment, late Renaissance | Conservatory: Medicine, late Industrial | Conservation, late Modern |
| Dockmaster | Construction, late Classical | Lighthouse: Celestial Navigation, middle Classical | Naval Tradition, late Post-Classical |
| Sacristan | Merchant Leagues, early Medieval | Temple: Theology, late Classical | Guilds, late Medieval |
| Stage Manager | Humanism, early Renaissance | Amphitheater: Drama and Poetry, early Classical | Opera and Ballet, early Industrial |

The Innkeeper, Ride Technician, Sacristan and Stage Manager have prerequisite ancestry enforcing the relevant producer/customer research sequence within the civic tree. The other relationships cross research trees and use chronological spacing. No mapping alone guarantees that players have physically built the customers before completing the Service research. Tech and Civic Shuffle also removes the normal prerequisite-order guarantee.

## Compatibility and text implementation after approval

The existing `Civ Supply Chains/ModSupport/ModSupport_6T.sql` is a comment-only placeholder. Its ModInUse criterion already targets the correct Grand Eras ID, but its database action has LoadOrder 102. Grand Eras rewrites its prerequisites at 12000, its ordinary unlocks at 13000, and Wonders/late compatibility at 10000005. Use a compatibility pass after the relevant rewrites; 10000010 is a clear candidate for the final database pass after auditing CSC's other actions. The patch belongs in CSC; Workshop files remain reference inputs.

Implementation needs four substantive research changes:

1. Bakery construction: `CIVIC_GUILDS` to `CIVIC_6T_MERCHANT_LEAGUES`.
2. Tailor construction: `CIVIC_GUILDS` to `CIVIC_6T_MERCHANT_LEAGUES`.
3. Sacristan activation: `CIVIC_DIVINE_RIGHT` to `CIVIC_GUILDS`.
4. Shared Café regular-Service activation: `CIVIC_URBANIZATION` to `CIVIC_CONSERVATION`, if this recommendation is adopted.

The Café art source modifiers already reuse its Service requirement set, and the Lua art mirror has no independent civic gate. Changing the shared requirement should carry the alternate art timing with it. Keep material, customer, ownership and pillage requirements intact.

Move CSC's research descriptions/addenda to the new nodes and remove obsolete CSC claims from the old nodes while preserving vanilla and Grand Eras content. Do not leave Divine Right advertising a Sacristan that now unlocks at Guilds, or Urbanization advertising Services moved to Conservation. Check the Grand Eras tree tooltip presentation as well as the underlying database.

Create conditional 6T localization overrides through the existing Markdown localization workflow. The text audit includes:

- `project/localization/CSC_BAKERS_TEXT.md`: shared late-Service requirement text; Café, Groundskeeper and Ride Technician descriptions; effects and relevant Zoo/Entertainment Complex/Water Park/Ferris Wheel Civilopedia entries.
- `project/localization/ModSupport_LGD_TEXT.md`: Garden-aware Café description, Horticulturist description/effect and Conservatory/Garden entries. These load with the combination of Grand Eras and the Garden integration.
- `project/localization/CSC_TAILORS_TEXT.md`: Tailor and Sacristan descriptions, Temple effect/addendum and relevant Civilopedia entries. Preserve the common Opera and Ballet wording for Stage Manager and Wonder Services.
- Quarter summaries and any explicit construction-unlock instructions that mention Guilds. Distinguish gameplay instructions from historical prose: ordinary discussion of medieval guilds or Enlightenment coffeehouses need not be replaced mechanically.

Preserve the normal-game localization when Grand Eras is absent. Prefer localized research-name references for explicit unlock instructions. Update Tailors' compatibility contracts to describe the approved optional mapping without rewriting its baseline design unlocks.

Bakers' route state reads supply properties; its existing Medieval Faires/Urbanization Lua constants are diagnostic labels, not the eligibility checks in `CSC_GetBakersTradeRouteState`. Audit the SQL property owners before deciding whether a changed Service gate also changes export timing, and refresh diagnostics if they become misleading. Do not introduce a second independent civic check in Lua.

Validation should cover the final loaded construction and activation rows, conditional localization, civic descriptions, the prepared regular-customer scenario before/after each Service civic, supply loss/pillage, and Service art activation. Check CSC alone, CSC with Grand Eras, and the combined Garden case. Wonder Service behavior remains a regression check, not a redesigned progression.

## Evidence and limits

Grand Eras' [Workshop description](https://steamcommunity.com/sharedfiles/filedetails/?id=2769967307) describes its added Post-Classical era and redesigned trees. Exact positions and prerequisites in this proposal come from the installed Workshop source, version 31, rather than inferring them from names or screenshots.

Reference root on Shadow: `C:\Program Files (x86)\Steam\steamapps\workshop\content\289070\2769967307\`.

- `Data/6T_Technologies.sql` and `Data/6T_Civics.sql`: eras, research costs and renamed research nodes.
- `Data/6T_TechnologyPrereqs.sql` and `Data/6T_Civic_Prereqs.sql`: complete prerequisite graphs.
- `Data/Unlocks/6T_Unlock_Buildings.sql`, `6T_Unlock_Districts.sql`, `6T_Unlock_Wonders.sql`: changed customers and hosts, including the optional Sydney/Louvre condition.
- `6T_Eras.modinfo`: identity, version and action load orders.
- CSC's Bakers/Tailors SQL, Garden integration, current localization sources, Tailors design contract and Wonder Service placement Lua: current unlocks and behavior.

The customer inventory was checked by replaying the tree definitions and relevant building/district updates into an in-memory copy of the current runtime database, then traversing the prerequisite graph. The original database was opened read-only; neither the installed mods nor the live game were changed. This was a targeted unlock analysis, not a full mod load, gameplay test or compatibility implementation.
