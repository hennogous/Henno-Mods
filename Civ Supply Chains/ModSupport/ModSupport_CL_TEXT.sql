-- ModSupport_CL_TEXT
-- Author: Shadow
-- DateCreated: 2025-08-09 12:32:49
--------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText

	(
	Language,
	Tag,
	Text
	)
VALUES
	(
	'en_US',
	'LOC_CLASS_CSC_INCOMING_GOODS_NAME',
	'Rural Community'
	);

UPDATE LocalizedText
SET Text = 'Effects apply to this city only.[NEWLINE][NEWLINE]Grants the Classical Borough +2 [ICON_PRODUCTION] Production for every adjacent unique Engineering district (Aqueduct, Dam, Canal, or Neighborhood). Allows the Prospectors'' Guild Urban improvement to be built by Builder units.[NEWLINE][NEWLINE]The Prospectors'' Guild provides +1 [ICON_Production] Production and an additional +1 [ICON_PRODUCTION] Production for every 2 adjacent districts. If built on a Mine or Quarry Strategic or Luxury resources, the city will gain use of that resource. Cannot be built adjacent to other Prospectors'' Guilds.'
WHERE Tag = 'LOC_BUILDING_COREXA_TIER2_SCI_DESCRIPTION';


UPDATE LocalizedText
SET Text = 'Prospectors'' Guild'
WHERE Tag = 'LOC_IMP_CL_CRAFTSMEN_QUARTER_NAME';

UPDATE LocalizedText
SET Text = 'Unlocks the Builder ability to construct the Urban improvement: Prospectors'' Guild.[NEWLINE][NEWLINE]+1 [ICON_Production] Production and an additional +1 [ICON_PRODUCTION] Production for every 2 adjacent districts. If built on a Mine or Quarry Strategic or Luxury resources, the city will gain use of that resource. Cannot be built adjacent to other Prospectors'' Guilds.'
WHERE Tag = 'LOC_IMP_CL_CRAFTSMEN_QUARTER_DESCRIPTION';