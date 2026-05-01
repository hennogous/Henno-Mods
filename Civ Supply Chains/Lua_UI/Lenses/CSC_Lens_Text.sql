-- ===========================================================================
-- CSC Lens Localized Text
-- ===========================================================================

INSERT OR REPLACE INTO LocalizedText
    (Language,  Tag,                                                Text)
VALUES
    -- Bakers' Quarter Lens
    ('en_US',   'LOC_HUD_CSC_BAKERS_LENS',                         'Bakers'' Quarter'),
    ('en_US',   'LOC_HUD_CSC_BAKERS_LENS_TOOLTIP',                 'Shows Bakers'' Quarters, their mapped resources (bright = improved), and points of sale.'),

    -- Legend entries
    ('en_US',   'LOC_TOOLTIP_CSC_LENS_BAKERS_QUARTER',             'Bakers'' Quarter'),
    ('en_US',   'LOC_TOOLTIP_CSC_LENS_BAKERS_BASE_IMPROVED',       'Base Resources (Improved)'),
    ('en_US',   'LOC_TOOLTIP_CSC_LENS_BAKERS_BASE_UNIMPROVED',     'Base Resources (Unimproved)'),
    ('en_US',   'LOC_TOOLTIP_CSC_LENS_BAKERS_SPEC_IMPROVED',       'Specialty Resources (Improved)'),
    ('en_US',   'LOC_TOOLTIP_CSC_LENS_BAKERS_SPEC_UNIMPROVED',     'Specialty Resources (Unimproved)'),
    ('en_US',   'LOC_TOOLTIP_CSC_LENS_SALE_DISTRICT',              'Points of Sale');
