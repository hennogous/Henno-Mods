-- ModSupport_LAR_TEXT
-- Generated from project\localization\ModSupport_LAR_TEXT.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText
    (Language, Tag, Text)
VALUES
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_LEU_P0K_QUINOA_CHAPTER_CSCQUAR_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_LEU_P0K_QUINOA_CHAPTER_CSCQUAR_PARA_1', 'Base material: [ICON_BAKERS] Bakers'' Quarter');

-- Raw SQL 1
UPDATE LocalizedText
SET Text = Text || '[NEWLINE][ICON_BULLET][ICON_RESOURCE_LEU_P0K_QUINOA] Quinoa'
WHERE Tag='LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCBASE_PARA_1';
