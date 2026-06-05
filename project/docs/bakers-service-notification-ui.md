# Bakers Service Notification UI

Bakers' service notifications are folded into the main Quarter effect notification path rather than emitted as standalone service-grant notifications.

## Design rule

Services are the named socio-economic capstones of completed supply chains. They are represented as hidden service buildings that add a citizen slot in the external customer district or City Center once goods are reliably available there.

For UI, the service name should appear first, followed by the effect amount and a concise supply-chain line.

Avoid standalone `*_SERVICE_GRANT_*` notifications unless the notification Lua path is deliberately restored and tested.

## Current Bakers services

| Stage | Service | Chain |
|---|---|---|
| Stage 2 | Storekeeper | supplied Water/Wind Mill → Granary |
| Stage 3 | Innkeeper | supplied Bakery → Market / Commercial Hub |
| Stage 4 | Groundskeeper | supplied Café → Zoo / Entertainment Complex |
| Stage 4 | Ride Technician | supplied Café → Ferris Wheel / Water Park |
| Stage 4 LGD | Horticulturist | supplied Café → Conservatory / Garden district |

## Current implementation notes

- Separate specialist-slot grant notification logic in `Civ Supply Chains/Lua_UI/Notifications_Suk_MCUIS` is commented out.
- Bakers' Stage 3 citizen-slot messaging is folded into `LOC_CSC_BAKERS_STAGE_3_EFFECT_DESCRIPTION_NEW`.
- Bakers' Stage 2 Storekeeper messaging follows the same folded-notification pattern: the grant is a SQL modifier chain on the Water/Wind Mill Feudalism effect, while MCUIS notification text lives on `LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_*`.
- Bakers' Stage 4 service text follows the same standard for core Zoo/Ferris Wheel and LGD Conservatory support: named service first, supply-chain line in MCUIS, and no standalone service-grant notification text.

## Aristocrat helper warning

The commented Lua block also contains the previous Aristocrat-on-3-specialist-slots helper. Restore or separate that helper before relying on the Aristocrat notification/grant path again.

## Related documentation

- `bakers-service-pedia-pages.md` in the `civ-supply-chains` skill documents the Civilopedia page pattern for Storekeeper, Innkeeper, Groundskeeper, and Ride Technician.
- `Text/CSC_QUARTERS_TEXT.sql` contains the user-facing service descriptions and pedia chapters.
- `Text/CSC_MC_MODE_TEXT.sql` can override Bakers building text in M&C mode; check it after changing service wording.
