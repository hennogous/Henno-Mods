-- ModSupport_LGD_TEXT
-- Author: Shadow
-- DateCreated: 2025-08-09 12:32:31
--------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText

(   Language,   Tag,                                                                Text    )   VALUES

(   'en_US',    'LOC_DISTRICT_CSC_BAKERS_QUARTER_DESCRIPTION',                      'A district in your city specializing in baking.[NEWLINE][NEWLINE]+1 [ICON_PRODUCTION] Production from each adjacent Base or Specialty Materials resource from this supply chain, and +1 [ICON_GOLD] Gold in return.[NEWLINE][NEWLINE]+1 [ICON_GOLD] Gold from each adjacent City Center and Commercial Hub, and +1 [ICON_FOOD] Food in return. +1 [ICON_GOLD] Gold from each adjacent Entertainment Complex, Water Park and Garden district, and +1 [ICON_CULTURE] Culture in return.[NEWLINE][NEWLINE]+1 [ICON_PRODUCTION] Production from every 2 adjacent river segments once the Water Mill is built, or +1 [ICON_PRODUCTION] Production if built on a Hills terrain once the Wind Mil is built.'   ),

(   'en_US',    'LOC_CSC_GARDEN_GOLD_TO_BAKERS',                                    '+{1_num} [ICON_Gold] from the adjacent {1_num : plural 1?Garden; other?Gardens;}.' ),

(   'en_US',    'LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION_GARDEN',                  '+1 [ICON_Production] Production from the local Flour Mill.[NEWLINE]+1 [ICON_Production] Production from each adjacent specialty materials improvement.[NEWLINE]+3 [ICON_Food] Food, with a -3 [ICON_Gold] Gold maintenance cost.[NEWLINE]+1 [ICON_Food] Food bonus to all [ICON_TradeRoute] trade routes to the city, and +2 [ICON_Gold] Gold in return from international routes.[NEWLINE]+1 [ICON_Culture] Culture for every 5 [ICON_Citizen] Citizens in the city to each adjacent Zoo, Ferris Wheel, or Conservatory, and +1 [ICON_Gold] Gold to the Café in return.[NEWLINE][NEWLINE]At Urbanization, a Café adjacent to improved base and specialty materials resources can establish services in adjacent Entertainment districts with Zoos, Water Parks with Ferris Wheels, and Gardens with Conservatories.'   ),

(   'en_US',    'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME',              'Horticulturist'),
(   'en_US',    'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_DESCRIPTION',       'A Service established in the Garden at Urbanization when a supplied Café serves an adjacent Conservatory, adding tourism and staffing the Garden.[NEWLINE][NEWLINE]+2 [ICON_Tourism] Tourism from each adjacent supplied Café, and +1 [ICON_Citizen] Citizen slot in the district.'),

(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_SERVICE_GARDEN',                            '[NEWLINE]{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service: +2 [ICON_Tourism] Tourism from each adjacent supplied Café and +1 [ICON_Citizen] Citizen slot if the Garden has a Conservatory.'),
(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_CIVIC',                                     'A Zoo adjacent to a supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service, a Ferris Wheel adjacent to a supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service, and a Garden with a Conservatory adjacent to a supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service: +2 [ICON_Tourism] Tourism from each adjacent supplied Café and +1 [ICON_Citizen] Citizen slot in the district.'  ),

(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN',                 '{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME}: {1_iBonus} [ICON_Tourism] Tourism.[NEWLINE]Supply Chain: {2_StackAmount} supplied {2_Num : plural 1?Café; other?Cafés;} [ICON_ARROW] adjacent Garden with a Conservatory.'  ),
(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN_NEW',             'a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service:[NEWLINE]{1_iBonus} [ICON_Tourism] Tourism and +1 [ICON_Citizen] Citizen slot in the Garden'  ),
(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN_INCREASED',       '{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service: {1_iBonus} [ICON_Tourism] Tourism'  ),
(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN_DECREASED',       '{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service: {1_iBonus} [ICON_Tourism] Tourism'  ),
(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN_REMOVED',         '{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service: {1_iBonus} [ICON_Tourism] Tourism'  ),

--(   'en_US',    'LOC_CSC_BAKERS_STAGE_4_SERVICE_GRANT_GARDEN_NEW',                  'A {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} has been appointed.'  ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_CAFE_CHAPTER_HISTORY_PARA_3',
    'The sales interaction of a Café with the local Zoo, Ferris Wheel, or Garden is a reflection of the rise of leisure culture and the "day out." As cities grew and the middle class expanded, public entertainment venues became popular destinations. A café adjacent to these attractions would have been a natural fit, offering a place for people to relax and socialize as part of their visit. This connection demonstrates how the Café was not just a place for intellectual discussion, but a vital part of a burgeoning urban entertainment industry, catering to a public seeking new forms of recreation and social engagement.'   ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_CAFE_CHAPTER_CSCHAIN_PARA_1',
    'The Café procures flour from the Water Mill or Wind Mill in the Quarter, as well as various specialty materials from adjacent improvements on those specific resources, and transforms them into fine baked goods and drinks for sale to select customers visiting the adjacent Entertainment Complex, Water Park or Garden.'   ),

(   'en_US',
    'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_LEU_GARDEN_CHAPTER_CSCHAIN_TITLE',
    'Supply Chains'   ),

(   'en_US',
    'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_LEU_GARDEN_CHAPTER_CSCHAIN_PARA_1',
    'Some visitors to the Garden also enjoy refreshments from the adjacent Café.[NEWLINE][NEWLINE]At Urbanization, an adjacent supplied Café can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service if this district has a Conservatory. See the {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} Civilopedia page for full requirements and effects.'   ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_LEU_CONSERVATORY_CHAPTER_CSCHAIN_TITLE', 
    'Supply Chains'   ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_LEU_CONSERVATORY_CHAPTER_CSCHAIN_PARA_1',
    'The Conservatory completes the Garden side of the Bakers'' Quarter service chain, much as the Zoo and Ferris Wheel complete the Entertainment and Water Park sides.[NEWLINE][NEWLINE]At Urbanization, an adjacent supplied Café can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service in this Garden: +2 [ICON_Tourism] Tourism from each adjacent supplied Café and +1 [ICON_Citizen] Citizen slot in the district.'   ),
/*
(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_CHAPTER_CSCDESC_TITLE',
    'Description'   ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_CHAPTER_CSCDESC_PARA_1',
    'A {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME} service represents the gardeners, guides, glasshouse attendants, and plant specialists needed when cafés help turn public gardens into regular civic destinations. In game terms, it is established in a Garden with a Conservatory when an adjacent supplied Café serves its visitors.'   ),
*/
(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_CHAPTER_CSCHAIN_TITLE',
    'Supply Chains'   ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_CHAPTER_CSCHAIN_PARA_1',
    'The Café draws on dependable flour from the local Water Mill or Wind Mill and improved Bakers'' specialty materials nearby, turns them into pastries and drinks, and offers that steady flow of refreshments to the growing numbers of visitors to the adjacent Conservatory.[NEWLINE][NEWLINE]This gives a Citizen the opportunity to take up employment as a Horticulturist in the Garden, tending rare plants, guiding curious visitors, and keeping the living collection healthy enough to become part of the city''s public life.'   ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_CHAPTER_HISTORY_TITLE',
    'Historical Context'   ),

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_CHAPTER_HISTORY_PARA_1',
    'Public gardens became more than pleasant green spaces when growing cities had the wealth and leisure to maintain them as destinations. Conservatories added spectacle: rare plants, glasshouse engineering, careful climates, and a steady stream of curious visitors. Cafés made those visits longer and more social, turning a stroll among plants into an afternoon out. The horticulturist is the quiet professional behind that transformation, keeping the living attraction alive while the city learns to treat leisure as part of urban life.'   );
