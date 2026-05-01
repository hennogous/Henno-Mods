-- ===========================================================================
-- CSC Lens Colors
-- Used by More Lenses integration (ModLens_CSC_Quarters.lua)
--
-- Each Quarter has: _QUARTER, _BASE_IMPROVED, _BASE_UNIMPROVED,
-- _SPEC_IMPROVED, _SPEC_UNIMPROVED colors.
-- Bright = improved/active, Dim = unimproved/opportunity.
-- ===========================================================================

INSERT OR REPLACE INTO Colors
    (Type,                                          Red,    Green,  Blue,   Alpha)
VALUES
    -- Bakers' Quarter (warm brown)
    ('COLOR_CSC_LENS_BAKERS_QUARTER',               0.72,   0.45,   0.20,   0.5),

    -- Base resources: grains — bright (improved) vs dim (unimproved)
    ('COLOR_CSC_LENS_BAKERS_BASE_IMPROVED',         0.95,   0.82,   0.15,   0.55),
    ('COLOR_CSC_LENS_BAKERS_BASE_UNIMPROVED',       0.60,   0.52,   0.18,   0.30),

    -- Specialty resources: luxury ingredients — bright vs dim
    ('COLOR_CSC_LENS_BAKERS_SPEC_IMPROVED',         0.92,   0.58,   0.10,   0.55),
    ('COLOR_CSC_LENS_BAKERS_SPEC_UNIMPROVED',       0.55,   0.38,   0.12,   0.30),

    -- Points of sale (shared across all Quarters)
    ('COLOR_CSC_LENS_SALE_DISTRICT',                0.20,   0.65,   0.80,   0.5);
