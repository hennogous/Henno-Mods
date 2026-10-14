-- CSC_Lens_Text
-- Generated from project\localization\CSC_Lens_Text.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText
    (Language, Tag, Text)
VALUES
    ('en_US', 'LOC_HUD_CSC_SUPPLY_CHAINS_LENS', 'Supply Chains'),
    ('en_US', 'LOC_HUD_CSC_SUPPLY_CHAINS_LENS_TOOLTIP', 'Choose a Quarter to highlight its materials and points of sale. Outlines mark improved resources; pillaged resources use the unimproved treatment.'),
    ('en_US', 'LOC_HUD_CSC_BAKERS_LENS', 'Bakers'' Quarter'),
    ('en_US', 'LOC_HUD_CSC_BAKERS_LENS_TOOLTIP', 'Shows Bakers'' Quarters in their icon colour, base materials in brown-orange, specialty materials in bright orange, and points of sale in yellow. Outlined resources are improved.'),
    ('en_US', 'LOC_TOOLTIP_CSC_LENS_BAKERS_QUARTER', 'Bakers'' Quarter'),
    ('en_US', 'LOC_HUD_CSC_TAILORS_LENS', 'Tailors'' Quarter'),
    ('en_US', 'LOC_HUD_CSC_TAILORS_LENS_TOOLTIP', 'Shows Tailors'' Quarters in their icon colour, base materials in brown-orange, specialty materials in bright orange, and points of sale in yellow. Outlined resources are improved.'),
    ('en_US', 'LOC_TOOLTIP_CSC_LENS_TAILORS_QUARTER', 'Tailors'' Quarter'),
    ('en_US', 'LOC_TOOLTIP_CSC_LENS_BASE', 'Base Materials (Outlined = Improved)'),
    ('en_US', 'LOC_TOOLTIP_CSC_LENS_SPEC', 'Specialty Materials (Outlined = Improved)'),
    ('en_US', 'LOC_TOOLTIP_CSC_LENS_SALE_DISTRICT', 'Points of Sale');
