-- ModSupport_R2_A_TAILORS_TEXT
-- Generated from project\localization\ModSupport_R2_A_TAILORS_TEXT.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

-- Tailors Cashmere Civilopedia mapping
UPDATE LocalizedText
SET Text = Text || '[NEWLINE][ICON_BULLET][ICON_RESOURCE_CASHMERE] Cashmere'
WHERE Tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCSPEC_PARA_1';

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text) VALUES
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_CASHMERE_CHAPTER_CSCQUAR_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_CASHMERE_CHAPTER_CSCQUAR_PARA_1', 'Specialty Materials:[NEWLINE][NEWLINE][ICON_BULLET] [ICON_TAILORS] Tailors'' Quarter');
