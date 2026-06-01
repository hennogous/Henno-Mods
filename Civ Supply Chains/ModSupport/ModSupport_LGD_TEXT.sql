-- ModSupport_LGD_TEXT
-- Author: Shadow
-- DateCreated: 2025-08-09 12:32:31
--------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText

(   Language,   Tag,                                                                Text    )   VALUES
(   'en_US',    'LOC_CSC_GARDEN_GOLD_TO_BAKERS',                                    '+{1_num} [ICON_Gold] from the adjacent {1_num : plural 1?Garden; other?Gardens;}.' ),

(   'en_US',    'LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION_GARDEN',                  '[ICON_BULLET]+1 [ICON_Production] Production from the local Flour Mill.[NEWLINE][ICON_BULLET]+1 [ICON_Production] Production from each adjacent specialty materials improvement.[NEWLINE][ICON_BULLET]+3 [ICON_Food] Food, with a -3 [ICON_Gold] Gold maintenance cost.[NEWLINE][ICON_BULLET]+1 [ICON_Food] Food bonus to all [ICON_TradeRoute] trade routes to the city, and +2 [ICON_Gold] Gold in return from international routes.[NEWLINE][ICON_BULLET]+1 [ICON_Culture] Culture for every 5 [ICON_Citizen] Citizens in the city to each adjacent Zoo, Ferris Wheel or Conservatory, and +1 [ICON_Gold] Gold to the Café in return.[NEWLINE][NEWLINE]At Urbanization, a Café adjacent to improved base and specialty materials resources establishes a service in each adjacent Entertainment Complex with a Zoo, Water Park with a Ferris Wheel and Garden with a Conservatory.'   ),

(   'en_US',    'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME',              'Horticulturist'),
(   'en_US',    'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_DESCRIPTION',       'Growing visitor numbers, in no small part driven by the proximity of the adjacent Café, has created the need for someone to perform some much-needed maintenance on the district''s attractions.'),

(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_SERVICE_GARDEN',                            '[NEWLINE]{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service: +2 [ICON_Tourism] Tourism from each adjacent supplied Café and +1 [ICON_Citizen] Citizen slot if the district has a Conservatory.'),
(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_CIVIC',                                     'A Zoo adjacent to a supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service, a Ferris Wheel adjacent to a supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service, and a Conservatory adjacent to a supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service: +2 [ICON_Tourism] Tourism from each adjacent supplied Café and +1 [ICON_Citizen] Citizen slot in the district.'  ),

(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN',                 '{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME}: {1_iBonus} [ICON_Tourism] Tourism.[NEWLINE]Supply Chain: {2_StackAmount} supplied {2_Num : plural 1?Café; other?Cafés;} [ICON_ARROW] adjacent Conservatory.'  ),
(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN_NEW',             'a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service:[NEWLINE]{1_iBonus} [ICON_Tourism] Tourism and +1 [ICON_Citizen] Citizen slot in the Garden'  ),
(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN_INCREASED',       '{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service: {1_iBonus} [ICON_Tourism] Tourism'  ),
(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN_DECREASED',       '{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service: {1_iBonus} [ICON_Tourism] Tourism'  ),
(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN_REMOVED',         '{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service: {1_iBonus} [ICON_Tourism] Tourism'  ),

--(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_SERVICE_GRANT_GARDEN_NEW',                  'A {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} has been appointed.'  ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_CAFE_CHAPTER_HISTORY_PARA_3',
    'The sales interaction of a Café with the local Zoo, Ferris Wheel, or Conservatory is a reflection of the rise of leisure culture and the "day out." As cities grew and the middle class expanded, public entertainment venues became popular destinations. A café adjacent to these attractions would have been a natural fit, offering a place for people to relax and socialize as part of their visit. This connection demonstrates how the Café was not just a place for intellectual discussion, but a vital part of a burgeoning urban entertainment industry, catering to a public seeking new forms of recreation and social engagement.'   ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_CAFE_CHAPTER_CSCHAIN_PARA_1',
    'The Café procures flour from the Water Mill or Wind Mill in the Quarter, as well as various specialty materials from adjacent improvements on those specific resources, and transforms them into fine baked goods and drinks for sale to select customers visiting the adjacent Entertainment Complex, Water Park or Garden.'   ),

(   'en_US',
    'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_LEU_GARDEN_CHAPTER_CSCHAIN_TITLE',
    'Supply Chains'   ),

(   'en_US',
    'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_LEU_GARDEN_CHAPTER_CSCHAIN_PARA_1',
    'The Garden offers a point of sale for an adjacent Café.[NEWLINE][NEWLINE]At Urbanization, each supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service in an adjacent Garden with a Conservatory: +2 [ICON_TOURISM] Tourism from each adjacent supplied Café and +1 [ICON_CITIZEN] Citizen slot in the Garden.'   ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_LEU_CONSERVATORY_CHAPTER_CSCHAIN_TITLE',
    'Supply Chains'   ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_LEU_CONSERVATORY_CHAPTER_CSCHAIN_PARA_1',
    'Some visitors to the Conservatory also enjoy some refreshments from the adjacent Café.[NEWLINE][NEWLINE]At Urbanization, a supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service in an adjacent Garden with a Conservatory: +2 [ICON_TOURISM] Tourism from each adjacent supplied Café and +1 [ICON_CITIZEN] Citizen slot in the Garden.'   );
