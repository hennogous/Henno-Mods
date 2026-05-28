# Notification UI Notes

- Services are the named socio-economic capstones of completed supply chains. They are hidden service buildings that add a citizen slot in the external customer district or City Center once goods are reliably available there.
- Current Bakers services: Stage 2 `Storekeeper` for supplied mill -> Granary, Stage 3 `Innkeeper` for supplied Bakery -> Market, Stage 4 `Groundskeeper` / `Ride Technician` / LGD `Horticulturist` for supplied Cafe -> Zoo / Ferris Wheel / Conservatory.
- Service notifications should be folded into the main Quarter effect notification: service name first, then effect amount and a concise supply-chain line. Avoid standalone `*_SERVICE_GRANT_*` notifications unless the notification Lua path is deliberately restored.
- 2026-05-28: Commented out the separate specialist-slot grant notification path in `Civ Supply Chains/Lua_UI/Notifications_Suk_MCUIS`. Bakers' Stage 3 citizen-slot messaging is being folded into `LOC_CSC_BAKERS_STAGE_3_EFFECT_DESCRIPTION_NEW` instead.
- The commented Lua block also contains the previous Aristocrat-on-3-specialist-slots helper. Restore or separate that helper before relying on the Aristocrat notification/grant path again.
- 2026-05-28: Bakers' Stage 2 Storekeeper service now follows the same folded-notification pattern: the grant is a SQL modifier chain on the Water/Wind Mill Feudalism effect, while the MCUIS notification text lives on `LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_*`.
- 2026-05-28: Bakers' Stage 4 service text now follows the same standard for core Zoo/Ferris Wheel and LGD Conservatory support: named service first, supply-chain line in MCUIS, and no standalone service-grant notification text.
