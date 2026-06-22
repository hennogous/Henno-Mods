-- CSC_A_RESOURCES_TEXT
-- Generated from project\localization\CSC_A_RESOURCES_TEXT.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText
    (Language, Tag, Text)
VALUES
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_CATTLE_CHAPTER_CSCQUAR_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_CATTLE_CHAPTER_CSCQUAR_PARA_1', 'Base material: [ICON_BAKERS] Bakers'' Quarter'),
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_HONEY_CHAPTER_CSCQUAR_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_HONEY_CHAPTER_CSCQUAR_PARA_1', 'Specialty material: [ICON_BAKERS] Bakers'' Quarter');

UPDATE LocalizedText
SET Text = 'Dairy'
WHERE Tag = 'LOC_RESOURCE_CATTLE_NAME';

UPDATE LocalizedText
SET Text = 'Wool'
WHERE Tag = 'LOC_RESOURCE_SHEEP_NAME';

-- Raw SQL 1
UPDATE LocalizedText
SET Text = Text || '[NEWLINE][ICON_BULLET][ICON_RESOURCE_CATTLE] Dairy'
WHERE Tag='LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCBASE_PARA_1';

-- Raw SQL 2
UPDATE LocalizedText
SET Text = Text || '[NEWLINE][ICON_BULLET][ICON_RESOURCE_HONEY] Honey'
WHERE Tag='LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCSPEC_PARA_1';
