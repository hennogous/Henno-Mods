# ModSupport_R2_SR_TEXT
output: Civ Supply Chains/ModSupport/ModSupport_R2_SR_TEXT.sql
language: en_US

## Tailors Gold Civilopedia mapping when both resource mods are active
mode: raw

```sql
-- Gameplay keeps Sukritact's Gold; remove Resourceful 2's now-unused listing.
UPDATE LocalizedText
SET Text = REPLACE(Text, '[NEWLINE][ICON_BULLET][ICON_RESOURCE_GOLD2] Gold', '')
WHERE Language = 'en_US'
  AND Tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCSPEC_PARA_1';
```
