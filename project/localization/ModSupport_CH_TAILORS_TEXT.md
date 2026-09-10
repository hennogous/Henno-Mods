# ModSupport_CH_TAILORS_TEXT
output: Civ Supply Chains/ModSupport/ModSupport_CH_TAILORS_TEXT.sql
language: en_US

## Tailors Hemp Civilopedia mapping
mode: raw

```sql
UPDATE LocalizedText
SET Text = Text || '[NEWLINE][ICON_BULLET][ICON_RESOURCE_AOM_HEMP] Hemp'
WHERE Tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCBASE_PARA_1';

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text) VALUES
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_AOM_HEMP_CHAPTER_CSCQUAR_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_AOM_HEMP_CHAPTER_CSCQUAR_PARA_1', 'Base Materials:[NEWLINE][NEWLINE][ICON_BULLET] [ICON_TAILORS] Tailors'' Quarter');
```
