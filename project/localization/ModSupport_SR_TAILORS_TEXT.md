# ModSupport_SR_TAILORS_TEXT
output: Civ Supply Chains/ModSupport/ModSupport_SR_TAILORS_TEXT.sql
language: en_US

## Tailors Sukritact Gold Civilopedia mapping
mode: raw

```sql
UPDATE LocalizedText
SET Text = Text || '[NEWLINE][ICON_BULLET][ICON_RESOURCE_GOLD] Gold'
WHERE Tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCSPEC_PARA_1';

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text) VALUES
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_GOLD_CHAPTER_CSCQUAR_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_RESOURCES_PAGE_RESOURCE_GOLD_CHAPTER_CSCQUAR_PARA_1', 'Specialty Materials:[NEWLINE][NEWLINE][ICON_BULLET] [ICON_TAILORS] Tailors'' Quarter');
```
