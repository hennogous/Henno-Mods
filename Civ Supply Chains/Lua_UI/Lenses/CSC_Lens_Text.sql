-- CSC_Lens_Text
-- Generated from project\localization\CSC_Lens_Text.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText
        (   Language,   Tag,                                        Text   )
VALUES  (   'en_US',    'LOC_CSC_LENS_QUARTER_ADJACENCY',           'Adjacency Bonuses'   ),
        (   'en_US',    'LOC_CSC_LENS_QUARTER_TRANSACTIONS',        'Transactions'   ),
        (   'en_US',    'LOC_CSC_LENS_QUARTER_SERVICES',            'Services'   ),
        (   'en_US',    'LOC_CSC_LENS_QUARTER_SPECIALISTS',         'Specialists ({1_Num})'   ),
        (   'en_US',    'LOC_CSC_LENS_QUARTER_AMENITIES',           '{1_Amount} Amenities'   ),
        (   'en_US',    'LOC_CSC_LENS_QUARTER_MAINTENANCE',         'Maintenance'   ),
        (   'en_US',    'LOC_HUD_CSC_SUPPLY_CHAINS_LENS',           'Supply Chains'   ),
        (   'en_US',    'LOC_HUD_CSC_SUPPLY_CHAINS_LENS_TOOLTIP',   'Choose a Quarter to highlight its materials, [ICON_CSC_GOODS] Goods Providers and customers. Hold Q and press 1 for Bakers'' or 2 for Tailors''. Improved materials and functioning sites have a stronger fill. Click a Quarter or Service icon to focus its supply chain. Click it again to restore the full lens.'   ),
        (   'en_US',    'LOC_HUD_CSC_BAKERS_LENS',                  'Bakers'' Quarter'   ),
        (   'en_US',    'LOC_HUD_CSC_BAKERS_LENS_TOOLTIP',          'Shows Bakers'' Quarters in green, [ICON_CSC_BASE] Base materials in brown, [ICON_CSC_SPEC] Specialty materials in orange and [ICON_CSC_SALES] customers in yellow. City Lights [ICON_CSC_GOODS] Goods Providers appear in light grey when available. Hold Q and press 1 to open this lens.'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_BAKERS_QUARTER',      'Bakers'' Quarter'   ),
        (   'en_US',    'LOC_HUD_CSC_TAILORS_LENS',                 'Tailors'' Quarter'   ),
        (   'en_US',    'LOC_HUD_CSC_TAILORS_LENS_TOOLTIP',         'Shows Tailors'' Quarters in purple, [ICON_CSC_BASE] Base materials in brown, [ICON_CSC_SPEC] Specialty materials in orange and [ICON_CSC_SALES] customers in yellow, including mapped Wonders. City Lights [ICON_CSC_GOODS] Goods Providers appear in light grey when available. Hold Q and press 2 to open this lens.'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_TAILORS_QUARTER',     'Tailors'' Quarter'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_BASE',                'Unimproved Base Materials'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_QUARTER_EMPTY',       'Quarter without Buildings'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_QUARTER_READY',       'Quarter with Buildings'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_BASE_READY',          'Improved Base Materials'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_SPEC',                'Unimproved Specialty Materials'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_SPEC_READY',          'Improved Specialty Materials'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_SALE_DISTRICT',       'Customer District'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_SALE_READY',          'Customer Building / Wonder'   ),
        (   'en_US',    'LOC_TOOLTIP_CSC_LENS_GOODS',               'Goods Provider'   );
