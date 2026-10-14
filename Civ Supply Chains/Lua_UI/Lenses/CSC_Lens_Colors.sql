-- Shared production/gold palette for both Quarter lens surfaces.
-- Gameplay Colors (UpdateDatabase), matching More Lenses' legacy RGBA schema.
-- Improved materials keep their hue with a small lift in brightness/opacity;
-- pillaged resources revert to the unimproved fill and lose their outline.
-- Quarter identity follows atlas index 0: Bakers green, Tailors violet.
INSERT OR REPLACE INTO Colors (Type, Red, Green, Blue, Alpha)
VALUES
    ('COLOR_CSC_LENS_BAKERS_QUARTER',  0.43, 0.63, 0.16, 0.48),
    ('COLOR_CSC_LENS_TAILORS_QUARTER', 0.59, 0.25, 0.72, 0.48),
    ('COLOR_CSC_LENS_BASE_IMPROVED',   0.57, 0.31, 0.13, 0.48),
    ('COLOR_CSC_LENS_BASE_UNIMPROVED', 0.51, 0.28, 0.12, 0.32),
    ('COLOR_CSC_LENS_SPEC_IMPROVED',   0.91, 0.57, 0.13, 0.52),
    ('COLOR_CSC_LENS_SPEC_UNIMPROVED', 0.80, 0.47, 0.11, 0.36),
    ('COLOR_CSC_LENS_SALE_DISTRICT',   0.90, 0.79, 0.25, 0.48),
    ('COLOR_CSC_LENS_BASE_OUTLINE',    0.79, 0.52, 0.24, 0.88),
    ('COLOR_CSC_LENS_SPEC_OUTLINE',    0.99, 0.74, 0.34, 0.90);
