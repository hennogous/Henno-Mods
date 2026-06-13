-- TAP_SPECIALTY_PRODUCTS_TEXT
-- Author: Henno
-- DateCreated: 2025-08-09 18:24:19
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	ENGLISH */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Bakers' Quarter
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText

(   Language,   Tag,                                                            Text    )   VALUES

(   'en_US',    'LOC_CSC_BAKERS_CAFE_DESCRIPTION_COMMISSION',                   '[NEWLINE][NEWLINE]Unlocks the Commission Fine Pastries project in cities with a Café. Fine Pastries can be displayed in the private collection of an Aristocrat.'),
(   'en_US',    'LOC_RESOURCE_CSC_BAKERS_SPECIALTY_NAME',                       'Fine Pastries'    ),
(   'en_US',    'LOC_GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_X_NAME',            'Fine Pastries'    ),
(   'en_US',    'LOC_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_NAME',         'Commission Fine Pastries'      ),
(   'en_US',    'LOC_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_SHORT_NAME',   'Commission Fine Pastries'      ),
(   'en_US',    'LOC_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_DESCRIPTION',  'Fine Pastries can be placed in the private collection of an Aristocrat.'   ),
(   'en_US',    'LOC_GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_RESOURCE_EFFECT',   'TBD'           ),

-- PEDIA: CAFÉ

(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_CAFE_CHAPTER_CSCHAIN_PARA_2',
    'At Urbanization, the Café enables the Commission Fine Pastries project in the city. Fine Pastries can be placed in the private collection of an Aristocrat.'   ),

-- PEDIA: ARISTOCRAT

(   'en_US',
    'LOC_BUILDING_CSC_ARISTOCRAT_DESCRIPTION',
    'Can commission specialty goods from local Quarters through projects, or obtain them through domestic and international trade, and displays such items in its private collection.'),
/*
(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_ARISTOCRAT_CHAPTER_CSCHAIN_TITLE',
    'Supply Chains'   ),
(   'en_US',
    'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_ARISTOCRAT_CHAPTER_CSCHAIN_PARA_1',
    ''   ), */

-- PEDIA: COMMISSION FINE PASTRIES PROJECT

(   'en_US',
    'LOC_PEDIA_WONDERS_PAGE_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_CHAPTER_CSCSPEC_TITLE',
    'Supply Chains'   ),
(   'en_US',
    'LOC_PEDIA_WONDERS_PAGE_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_CHAPTER_CSCSPEC_PARA_1',
    'Unlocks with Urbanization in cities with a Café, which produces a Fine Pastries product.'   ),
(   'en_US',
    'LOC_PEDIA_WONDERS_PAGE_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_CHAPTER_HISTORY_TITLE',
    'Historical Context'   ),
(   'en_US',
    'LOC_PEDIA_WONDERS_PAGE_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_CHAPTER_HISTORY_PARA_1',
    'Historically, commissioning specialty items like art, architecture, and other luxury goods was a primary way for aristocrats to demonstrate their wealth, power, and prestige. This practice, known as patronage, dates back to ancient Rome with figures like Gaius Maecenas, but it became a dominant force in European culture during the Middle Ages and Renaissance. Aristocrats would commission everything from grand palaces and castles to intricate tapestries, paintings, sculptures, and illuminated manuscripts. The objects they commissioned weren''t just for aesthetic pleasure; they were carefully designed to reflect the patron''s status, family history, and political ambitions. For example, a commissioned portrait might include symbols of their lineage or a battle they won, while a new church or chapel would be a public display of their piety and a bid for salvation. The Medici family in Florence is a classic example, using their immense wealth from banking to fund masterpieces by artists like Michelangelo and Leonardo da Vinci, thereby cementing their political and social dominance.'   ),
(   'en_US',
    'LOC_PEDIA_WONDERS_PAGE_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_CHAPTER_HISTORY_PARA_2',
    'As markets developed and the power of the aristocracy waned, the nature of commissioning began to shift. By the 18th and 19th centuries, the rise of a bourgeois merchant class and the establishment of public art institutions meant that artists were no longer solely dependent on a single aristocratic patron. While nobles continued to commission works, the market for art and luxury goods became more democratic, with artists able to sell their work to a wider audience. This transition marked a move away from the feudal-era patronage system, where artists were often seen as craftsmen in service to a master, to a more modern model where they were viewed as independent creators. However, the legacy of aristocratic patronage remains, as many of the world''s most famous and valuable works of art were originally conceived and created to fulfill the ambitious visions of a powerful and wealthy noble class.'   );
