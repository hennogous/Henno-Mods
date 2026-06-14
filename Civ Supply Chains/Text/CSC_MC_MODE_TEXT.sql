-- CSC_MC_MODE_TEXT
-- Author: Henno
-- DateCreated: 2025-08-09 18:24:19
--------------------------------------------------------------

-- M&C Industry/Corporation wording only. Specialty Products text moved to Taxes And Politics.

UPDATE LocalizedText
SET Text = '+1 [ICON_Production] Production from each adjacent Base Materials improvement, increased to +2 [ICON_Production] Production from an Industry, and +3 [ICON_Production] Production from a Corporation.[NEWLINE]+1 [ICON_Food] Food, with a -1 [ICON_Gold] Gold maintenance cost.[NEWLINE]+1 [ICON_Gold] Gold from the local Bakery and Café.[NEWLINE]+1 [ICON_Food] Food bonus to [ICON_TradeRoute] trade routes to the city, and +1 [ICON_Gold] Gold in return from international routes.[NEWLINE]+1 [ICON_Food] Food to an adjacent Granary, and receive +1 [ICON_Gold] Gold in return.[NEWLINE][NEWLINE]At Feudalism, a supplied Water Mill or Wind Mill can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service in an adjacent City Center with a Granary.'
WHERE Tag = 'LOC_BUILDING_CSC_BAKERS_WATER_MILL_DESCRIPTION' OR Tag = 'LOC_BUILDING_CSC_BAKERS_WIND_MILL_DESCRIPTION';

UPDATE LocalizedText
SET Text = '[ICON_BULLET]+1 [ICON_Production] Production from the local Flour Mill.[NEWLINE][ICON_BULLET]+1 [ICON_Production] Production from each adjacent Specialty Materials improvement, increased to +2 [ICON_Production] Production from an Industry, and +3 [ICON_Production] Production from a Corporation.[NEWLINE][ICON_BULLET]+3 [ICON_Food] Food, with a -3 [ICON_Gold] Gold maintenance cost.[NEWLINE][ICON_BULLET]+1 [ICON_Food] Food bonus to all [ICON_TradeRoute] trade routes to the city, and +2 [ICON_Gold] Gold in return from international routes.[NEWLINE][ICON_BULLET]+1 [ICON_Culture] Culture for every 5 [ICON_Citizen] Citizens in the city to each adjacent Zoo and Ferris Wheel, and +1 [ICON_Gold] Gold to the Café in return.[NEWLINE][NEWLINE]At Urbanization, a Café adjacent to improved base and Specialty Materials resources can establish services in adjacent Entertainment districts with Zoos and Water Parks with Ferris Wheels.'
WHERE Tag = 'LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION';

UPDATE LocalizedText
SET Text = '[ICON_BULLET]+1 [ICON_Production] Production from the local Flour Mill.[NEWLINE][ICON_BULLET]+1 [ICON_Production] Production from each adjacent Specialty Materials improvement, increased to +2 [ICON_Production] Production from an Industry, and +3 [ICON_Production] Production from a Corporation.[NEWLINE][ICON_BULLET]+3 [ICON_Food] Food, with a -3 [ICON_Gold] Gold maintenance cost.[NEWLINE][ICON_BULLET]+1 [ICON_Food] Food bonus to all [ICON_TradeRoute] trade routes to the city, and +2 [ICON_Gold] Gold in return from international routes.[NEWLINE][ICON_BULLET]+1 [ICON_Culture] Culture for every 5 [ICON_Citizen] Citizens in the city to each adjacent Zoo, Ferris Wheel and Conservatory, and +1 [ICON_Gold] Gold to the Café in return.[NEWLINE][NEWLINE]At Urbanization, a Café adjacent to improved base and Specialty Materials resources can establish services in adjacent Entertainment districts, Water Parks and Gardens.'
WHERE Tag = 'LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION_GARDEN';
