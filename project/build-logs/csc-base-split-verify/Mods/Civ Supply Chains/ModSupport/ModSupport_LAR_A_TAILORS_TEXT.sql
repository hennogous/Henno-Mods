-- ModSupport_LAR_A_TAILORS_TEXT
-- Generated from project\localization\ModSupport_LAR_A_TAILORS_TEXT.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

-- Tailors Llamas Civilopedia mapping
UPDATE LocalizedText
SET Text = Text || '[NEWLINE][ICON_BULLET][ICON_RESOURCE_LEU_P0K_LLAMAS] Llamas'
WHERE Tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCBASE_PARA_1';

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text) VALUES
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_LEU_P0K_LLAMAS_CHAPTER_CSCQUAR_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_LEU_P0K_LLAMAS_CHAPTER_CSCQUAR_PARA_1', 'Base Materials:[NEWLINE][NEWLINE][ICON_BULLET] [ICON_TAILORS] Tailors'' Quarter');
