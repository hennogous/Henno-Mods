# ModSupport_CL_TEXT
output: Civ Supply Chains/ModSupport/ModSupport_CL_TEXT.sql
language: en_US

## LOC_CLASS_CSC_GOODS_PROVIDER_NAME
[ICON_CSC_GOODS] Rural Community

## Bakers Quarter district description patch
mode: raw

```sql
UPDATE LocalizedText
SET Text = REPLACE(REPLACE(
    Text,
    '+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] City Center and Commercial Hub, and +1 [ICON_Food] Food in return.',
    '+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] City Center, Commercial Hub and Urban Borough, and +1 [ICON_Food] Food in return.'
),
    '+1 [ICON_Gold] Gold from each adjacent City Center and Commercial Hub, and +1 [ICON_Food] Food in return.',
    '+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] City Center, Commercial Hub and Urban Borough, and +1 [ICON_Food] Food in return.'
)
WHERE Tag = 'LOC_DISTRICT_CSC_BAKERS_QUARTER_DESCRIPTION'
  AND Language = 'en_US'
  AND instr(Text, 'City Center and Commercial Hub') > 0;

UPDATE LocalizedText
SET Text = REPLACE(REPLACE(
    Text,
    '+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] City Center, Commercial Hub and Urban Borough, and +1 [ICON_Food] Food in return.',
    '+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] City Center, Commercial Hub and Urban Borough, and +1 [ICON_Food] Food in return.[NEWLINE]+1 [ICON_Production] Production from each adjacent [ICON_CSC_GOODS] Rural Community, and +1 [ICON_Food] Food in return.'
),
    '+1 [ICON_Gold] Gold from each adjacent City Center, Commercial Hub and Urban Borough, and +1 [ICON_Food] Food in return.',
    '+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] City Center, Commercial Hub and Urban Borough, and +1 [ICON_Food] Food in return.[NEWLINE]+1 [ICON_Production] Production from each adjacent [ICON_CSC_GOODS] Rural Community, and +1 [ICON_Food] Food in return.'
)
WHERE Tag = 'LOC_DISTRICT_CSC_BAKERS_QUARTER_DESCRIPTION'
  AND Language = 'en_US'
  AND instr(Text, 'City Center, Commercial Hub and Urban Borough') > 0
  AND instr(Text, 'adjacent Rural Community') = 0;
```

## Raw SQL 1
mode: raw

```sql
UPDATE LocalizedText
SET Text = CASE
    WHEN Text = '' THEN '[ICON_BULLET][ICON_DISTRICT_RURALCOMMUNITYA] {LOC_DISTRICT_RURALCOMMUNITYA_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_FRONTIER_TOWN] {LOC_DISTRICT_COREX_FRONTIER_TOWN_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_RURALCOMMUNITYB] {LOC_DISTRICT_RURALCOMMUNITYB_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_TROYU] {LOC_DISTRICT_COREX_TROYU_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_TSIKHE] {LOC_DISTRICT_COREX_TSIKHE_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_RURALCOMMUNITYC] {LOC_DISTRICT_RURALCOMMUNITYC_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_GYOSON] {LOC_DISTRICT_COREX_GYOSON_NAME}'
    ELSE Text || '[NEWLINE][ICON_BULLET][ICON_DISTRICT_RURALCOMMUNITYA] {LOC_DISTRICT_RURALCOMMUNITYA_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_FRONTIER_TOWN] {LOC_DISTRICT_COREX_FRONTIER_TOWN_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_RURALCOMMUNITYB] {LOC_DISTRICT_RURALCOMMUNITYB_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_TROYU] {LOC_DISTRICT_COREX_TROYU_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_TSIKHE] {LOC_DISTRICT_COREX_TSIKHE_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_RURALCOMMUNITYC] {LOC_DISTRICT_RURALCOMMUNITYC_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_GYOSON] {LOC_DISTRICT_COREX_GYOSON_NAME}'
END
WHERE Tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCGOODS_PARA_1';

UPDATE LocalizedText
SET Text = Text || '[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREEXPANSIONA] {LOC_DISTRICT_COREEXPANSIONA_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_XIAN] {LOC_DISTRICT_COREX_XIAN_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_UPAPITHA] {LOC_DISTRICT_COREX_UPAPITHA_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_VENICE_01] {LOC_DISTRICT_COREEXPANSIONA_VENICE_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREEXPANSIONB] {LOC_DISTRICT_COREEXPANSIONB_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_VENICE_02] {LOC_DISTRICT_COREEXPANSIONB_VENICE_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_FUERTE] {LOC_DISTRICT_COREX_FUERTE_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREEXPANSIONC] {LOC_DISTRICT_COREEXPANSIONC_NAME}[NEWLINE][ICON_BULLET][ICON_DISTRICT_COREX_ELYSEE] {LOC_DISTRICT_COREX_ELYSEE_NAME}'
WHERE Tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCSALES_PARA_1';
```

## LOC_BUILDING_COREXA_TIER2_SCI_DESCRIPTION
mode: update

Effects apply to this city only.

Grants the Classical Borough +2 [ICON_PRODUCTION] Production for every adjacent unique Engineering district (Aqueduct, Dam, Canal, or Neighborhood). Allows the Prospectors' Guild Urban improvement to be built by Builder units.

The Prospectors' Guild provides +1 [ICON_Production] Production and an additional +1 [ICON_PRODUCTION] Production for every 2 adjacent districts. If built on a Mine or Quarry Strategic or Luxury resources, the city will gain use of that resource. Cannot be built adjacent to other Prospectors' Guilds.

## LOC_IMP_CL_CRAFTSMEN_QUARTER_NAME
mode: update

Prospectors' Guild

## LOC_IMP_CL_CRAFTSMEN_QUARTER_DESCRIPTION
mode: update

Unlocks the Builder ability to construct the Urban improvement: Prospectors' Guild.

+1 [ICON_Production] Production and an additional +1 [ICON_PRODUCTION] Production for every 2 adjacent districts. If built on a Mine or Quarry Strategic or Luxury resources, the city will gain use of that resource. Cannot be built adjacent to other Prospectors' Guilds.
