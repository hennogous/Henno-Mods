-- CSC_TAILORS_MC_MODE_TEXT
-- Generated from project\localization\CSC_TAILORS_MC_MODE_TEXT.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

-- Textile Workshop Monopolies & Corporations line
UPDATE LocalizedText
SET Text = REPLACE(
    Text,
    '+1 [ICON_Culture] Culture from each adjacent [ICON_CSC_BASE] Base Materials improvement, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.',
    '+1 [ICON_Culture] Culture from each adjacent [ICON_CSC_BASE] Base Materials improvement, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.[NEWLINE]+2 [ICON_Culture] Culture, [ICON_Production] Production and [ICON_Gold] Gold from an Industry, and +3 [ICON_Culture] Culture, [ICON_Production] Production and [ICON_Gold] Gold from a Corporation.'
)
WHERE Tag = 'LOC_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_DESCRIPTION';
