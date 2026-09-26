-- ModSupport_R2_SR_TEXT
-- Generated from project\localization\ModSupport_R2_SR_TEXT.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

-- Tailors Gold Civilopedia mapping when both resource mods are active
-- Gameplay keeps Sukritact's Gold; remove Resourceful 2's now-unused listing.
UPDATE LocalizedText
SET Text = REPLACE(Text, '[NEWLINE][ICON_BULLET][ICON_RESOURCE_GOLD2] Gold', '')
WHERE Language = 'en_US'
  AND Tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCSPEC_PARA_1';
