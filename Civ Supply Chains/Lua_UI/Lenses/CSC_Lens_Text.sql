-- CSC_Lens_Text
-- Generated from project\localization\CSC_Lens_Text.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText
        (   Language,   Tag,                                        Text   )
VALUES  (   'en_US',    'LOC_HUD_CSC_SUPPLY_CHAINS_LENS',           'Supply Chains'   ),
        (   'en_US',    'LOC_HUD_CSC_SUPPLY_CHAINS_LENS_TOOLTIP',   'Choose a Quarter to highlight its materials and points of sale. Hold Q and press 1 for Bakers'' or 2 for Tailors''. Outlines mark [ICON_CSC_BASE] Base materials, [ICON_CSC_SPEC] Specialty materials, and [ICON_CSC_SALES] customer districts. Improved materials, functioning customer buildings, and completed customer Wonders have a stronger tile fill. Unimproved [ICON_CSC_BASE] Base materials have a 30% tile fill; other unimproved or empty sites have a 20% fill; improved or functioning sites have a 60% fill. All relevant sites have an opaque outline. Quarters use their own colours, with a 20% fill until they contain a functioning building and 60% thereafter. Animated arrows run from improved materials to their matching buyer building, and from producer buildings to matching customers. Arrow colours show the delivered yield: orange for Production, green for Food, and purple for Culture.'   ),
        (   'en_US',    'LOC_HUD_CSC_BAKERS_LENS',                  'Bakers'' Quarter'   ),
        (   'en_US',    'LOC_HUD_CSC_BAKERS_LENS_TOOLTIP',          'Shows Bakers'' Quarters in green, [ICON_CSC_BASE] base materials in dark brown, [ICON_CSC_SPEC] specialty materials in orange, and points of sale in yellow. Hold Q and press 1 to open this lens. All relevant sites have opaque outlines, with 30% fills for unimproved [ICON_CSC_BASE] Base materials, 20% for other unimproved or empty sites, and 60% for improved or functioning sites. Quarters follow the same rule, depending on whether they contain a functioning building. Animated arrows run from improved materials to their matching buyer building, and from producer buildings to matching customers. Arrow colours show the delivered yield: orange for Production, green for Food, and purple for Culture.'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_BAKERS_QUARTER',      'Bakers'' Quarter'   ),
        (   'en_US',    'LOC_HUD_CSC_TAILORS_LENS',                 'Tailors'' Quarter'   ),
        (   'en_US',    'LOC_HUD_CSC_TAILORS_LENS_TOOLTIP',         'Shows Tailors'' Quarters in purple, [ICON_CSC_BASE] base materials in dark brown, [ICON_CSC_SPEC] specialty materials in orange, and points of sale in yellow. Hold Q and press 2 to open this lens. All relevant sites have opaque outlines, with 30% fills for unimproved [ICON_CSC_BASE] Base materials, 20% for other unimproved or empty sites, and 60% for improved or functioning sites, including completed customer Wonders. Quarters follow the same rule, depending on whether they contain a functioning building. Animated arrows run from improved materials to their matching buyer building, and from producer buildings to matching customers. Arrow colours show the delivered yield: orange for Production, green for Food, and purple for Culture.'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_TAILORS_QUARTER',     'Tailors'' Quarter'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_BASE',                'Unimproved Base Materials'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_QUARTER_EMPTY',       'Quarter without Buildings'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_QUARTER_READY',       'Quarter with Buildings'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_BASE_READY',          'Improved Base Materials'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_SPEC',                'Unimproved Specialty Materials'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_SPEC_READY',          'Improved Specialty Materials'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_SALE_DISTRICT',       'Customer District'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_SALE_READY',          'Customer Building / Wonder'   );
