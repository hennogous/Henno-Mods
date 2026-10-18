-- CSC_TAILORS_TEXT
-- Generated from project\localization\CSC_TAILORS_TEXT.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText
    (Language, Tag, Text)
VALUES
    ('en_US', 'LOC_DISTRICT_CSC_TAILORS_QUARTER_NAME', 'Tailors'' Quarter'),
    ('en_US', 'LOC_DISTRICT_CSC_TAILORS_QUARTER_DESCRIPTION', 'A district in your city specializing in tailoring.[NEWLINE][NEWLINE]+1 [ICON_Production] Production from every 2 adjacent river segments.[NEWLINE]+1 [ICON_Production] Production from each adjacent [ICON_CSC_BASE] Base or [ICON_CSC_SPEC] Specialty Materials resource from this supply chain.[NEWLINE]+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] Harbor, and +1 [ICON_Production] Production in return.[NEWLINE]+1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] Commercial Hub, Holy Site and Theater Square, and +1 [ICON_Culture] Culture in return.'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_NAME', 'Textile Workshop'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_DESCRIPTION', '+1 [ICON_Culture] Culture from each adjacent [ICON_CSC_BASE] Base Materials improvement, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.[NEWLINE]+1 [ICON_Production] Production and +1 [ICON_Gold] Gold from the local Tailor and Fashion House, in exchange for +1 [ICON_Culture] Culture.[NEWLINE]+1 [ICON_Production] Production and +1 [ICON_Gold] Gold from each adjacent Lighthouse, and +1 [ICON_Production] Production in return.[NEWLINE][NEWLINE]At Naval Tradition, a supplied Textile Workshop establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME} service in an adjacent Harbor with a Lighthouse.'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_TAILOR_NAME', 'Tailor'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_TAILOR_DESCRIPTION', '+1 [ICON_Culture] Culture from the local Textile Workshop, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.[NEWLINE]+0.1 [ICON_Production] Production and +0.1 [ICON_Gold] Gold per [ICON_Citizen] Citizen from each adjacent Temple or Market, in exchange for +0.1 [ICON_Culture] Culture per [ICON_Citizen] Citizen to the customer city.[NEWLINE]+1 [ICON_Production] Production and +1 [ICON_Gold] Gold from each incoming [ICON_TradeRoute] Trade Route, in exchange for a +1 [ICON_Culture] Culture bonus to the [ICON_TradeRoute] Trade Route, if the origin city itself does not have a Tailors'' Quarter. +1 [ICON_Amenities] Amenity to the origin city.[NEWLINE][NEWLINE]At Divine Right, a supplied Tailor establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME} service in an adjacent Holy Site with a Temple.'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_FASHION_HOUSE_NAME', 'Fashion House'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_FASHION_HOUSE_DESCRIPTION', '+1 [ICON_Culture] Culture from each adjacent [ICON_CSC_SPEC] Specialty Materials improvement.[NEWLINE]+1 [ICON_Culture] Culture from the local Textile Workshop, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.[NEWLINE]+1 [ICON_Production] Production and +1 [ICON_Gold] Gold per 5 [ICON_Citizen] Citizens from each adjacent Amphitheater, Bolshoi Theatre, Broadway or Sydney Opera House, in exchange for +1 [ICON_Culture] Culture per 5 [ICON_Citizen] Citizens to the customer building. Both sides use the customer city''s population.[NEWLINE]+1 [ICON_Production] Production and +1 [ICON_Gold] Gold from each incoming [ICON_TradeRoute] Trade Route, in exchange for a +1 [ICON_Culture] Culture bonus to the [ICON_TradeRoute] Trade Route, if the origin city itself does not have a Tailors'' Quarter. +1 [ICON_Amenities] Amenity to the origin city.[NEWLINE][NEWLINE]At Opera and Ballet, a Fashion House supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME} service in an adjacent Theater Square with an Amphitheater, or a venue-specific performance service on an adjacent Wonder: {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME} at Bolshoi Theatre, {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME} at Broadway, {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME} at Sydney Opera House.'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME', 'Dockmaster'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_DESCRIPTION', 'A Service established in the Harbor at Naval Tradition when a supplied Textile Workshop serves an adjacent Lighthouse.[NEWLINE][NEWLINE]+20% [ICON_Production] Production toward Renaissance Era or earlier naval units and +1 [ICON_GreatAdmiral] Great Admiral point from each adjacent supplied Textile Workshop.'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME', 'Sacristan'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_DESCRIPTION', 'A Service established in the Holy Site at Divine Right when a supplied Tailor serves an adjacent Temple. +10% [ICON_Faith] Faith, +1 [ICON_GreatProphet] Great Prophet point from each adjacent supplied Tailor, and +1 [ICON_Citizen] Citizen slot in the Holy Site.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_3_MARKET_EFFECT', '+0.1 [ICON_Culture] Culture per [ICON_Citizen] Citizen to the city from each adjacent Tailor, in exchange for +0.1 [ICON_Production] Production and +0.1 [ICON_Gold] Gold per [ICON_Citizen] Citizen to the Tailor city.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_3_MARKET_EFFECT_APPEND', '[NEWLINE][NEWLINE]+0.1 [ICON_Culture] Culture per [ICON_Citizen] Citizen to the city from each adjacent Tailor, in exchange for +0.1 [ICON_Production] Production and +0.1 [ICON_Gold] Gold per [ICON_Citizen] Citizen to the Tailor city.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_3_TEMPLE_EFFECT', '+0.1 [ICON_Culture] Culture per [ICON_Citizen] Citizen to the city from each adjacent Tailor, in exchange for +0.1 [ICON_Production] Production and +0.1 [ICON_Gold] Gold per [ICON_Citizen] Citizen to the Tailor city.[NEWLINE][NEWLINE]At Divine Right, a Temple adjacent to a supplied Tailor establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME}: +10% [ICON_Faith] Faith and +1 [ICON_GreatProphet] Great Prophet point from each adjacent supplied Tailor, and +1 [ICON_Citizen] Citizen slot in the Holy Site.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_3_TEMPLE_EFFECT_APPEND', '[NEWLINE][NEWLINE]+0.1 [ICON_Culture] Culture per [ICON_Citizen] Citizen to the city from each adjacent Tailor, in exchange for +0.1 [ICON_Production] Production and +0.1 [ICON_Gold] Gold per [ICON_Citizen] Citizen to the Tailor city.[NEWLINE][NEWLINE]At Divine Right, a Temple adjacent to a supplied Tailor establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME}: +10% [ICON_Faith] Faith and +1 [ICON_GreatProphet] Great Prophet point from each adjacent supplied Tailor, and +1 [ICON_Citizen] Citizen slot in the Holy Site.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_3_CIVIC', 'A Temple adjacent to a supplied Tailor establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME}: +10% [ICON_Faith] Faith and +1 [ICON_GreatProphet] Great Prophet point from each adjacent supplied Tailor, and +1 [ICON_Citizen] Citizen slot in the Holy Site.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_3_CIVIC_APPEND', '[NEWLINE][NEWLINE]A Temple adjacent to a supplied Tailor establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME}: +10% [ICON_Faith] Faith and +1 [ICON_GreatProphet] Great Prophet point from each adjacent supplied Tailor, and +1 [ICON_Citizen] Citizen slot in the Holy Site.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION', '{LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME}: {1_TotalAmount}% [ICON_Faith] Faith and {2_TotalStack} [ICON_GreatProphet] Great Prophet {3_TotalStackCount : plural 1?point; other?points;}.[NEWLINE]Supply Chain: {3_TotalStackCount} supplied {3_TotalStackCount : plural 1?Tailor; other?Tailors;} [ICON_ARROW] adjacent Temple.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION_NEW', 'a new {LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME} service: {1_NewAmount}% [ICON_Faith] Faith, {2_NewStack} [ICON_GreatProphet] Great Prophet {3_StackCount : plural 1?point; other?points;} and +1 [ICON_Citizen] Citizen slot in the Holy Site'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION_INCREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME} service increased: {1_IncreaseAmount}% [ICON_Faith] Faith and {2_IncreasedStack} [ICON_GreatProphet] Great Prophet {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION_DECREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME} service decreased: {1_DecreaseAmount}% [ICON_Faith] Faith and {2_DecreasedStack} [ICON_GreatProphet] Great Prophet {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION_REMOVED', '{LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME} effects deactivated: {1_LostAmount}% [ICON_Faith] Faith and {2_LostStack} [ICON_GreatProphet] Great Prophet {3_StackCount : plural 1?point; other?points;}. The established service and its [ICON_Citizen] Citizen slot remain'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME', 'Stage Manager'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_DESCRIPTION', 'A Service established in a Theater Square with an Amphitheater at Opera and Ballet when an adjacent Fashion House is supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials.[NEWLINE][NEWLINE]+2 [ICON_Tourism] Tourism and +1 [ICON_GreatArtist] Great Artist point from each adjacent supplied Fashion House. +1 [ICON_Citizen] Citizen slot in the Theater Square.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_AMPHITHEATER_EFFECT', '+1 [ICON_Culture] Culture per 5 [ICON_Citizen] Citizens from each adjacent Fashion House, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold per 5 [ICON_Citizen] Citizens to the Fashion House. Both sides use this city''s population.[NEWLINE][NEWLINE]At Opera and Ballet, an adjacent Fashion House supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME} service here.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_AMPHITHEATER_EFFECT_APPEND', '[NEWLINE][NEWLINE]{LOC_CSC_TAILORS_STAGE_4_AMPHITHEATER_EFFECT}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_CIVIC', 'An Amphitheater or one of the named Wonders adjacent to a Fashion House supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials establishes a performance service: {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME} in the Theater Square, {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME} at Bolshoi Theatre, {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME} at Broadway, {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME} at Sydney Opera House. Each provides +2 [ICON_Tourism] Tourism and +1 [ICON_GreatArtist] Great Artist point from each adjacent supplied Fashion House. Only the Theater Square service provides +1 [ICON_Citizen] Citizen slot.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_CIVIC_APPEND', '[NEWLINE][NEWLINE]{LOC_CSC_TAILORS_STAGE_4_CIVIC}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME}: {1_TotalAmount} [ICON_Tourism] Tourism and {2_TotalStack} [ICON_GreatArtist] Great Artist {3_TotalStackCount : plural 1?point; other?points;}.[NEWLINE]Supply Chain: {3_TotalStackCount} supplied {3_TotalStackCount : plural 1?Fashion House; other?Fashion Houses;} [ICON_ARROW] adjacent Amphitheater.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_NEW', 'a new {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME} service: {1_NewAmount} [ICON_Tourism] Tourism, {2_NewStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;} and +1 [ICON_Citizen] Citizen slot in the Theater Square'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_INCREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME} service increased: {1_IncreaseAmount} [ICON_Tourism] Tourism and {2_IncreasedStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_DECREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME} service decreased: {1_DecreaseAmount} [ICON_Tourism] Tourism and {2_DecreasedStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_REMOVED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME} effects deactivated: {1_LostAmount} [ICON_Tourism] Tourism and {2_LostStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}. The established service and its [ICON_Citizen] Citizen slot remain'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BOLSHOI', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME}: {1_TotalAmount} [ICON_Tourism] Tourism and {2_TotalStack} [ICON_GreatArtist] Great Artist {3_TotalStackCount : plural 1?point; other?points;}.[NEWLINE]Supply Chain: {3_TotalStackCount} supplied {3_TotalStackCount : plural 1?Fashion House; other?Fashion Houses;} [ICON_ARROW] adjacent Bolshoi Theatre.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BOLSHOI_NEW', 'a new {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME} service: {1_NewAmount} [ICON_Tourism] Tourism and {2_NewStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BOLSHOI_INCREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME} service increased: {1_IncreaseAmount} [ICON_Tourism] Tourism and {2_IncreasedStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BOLSHOI_DECREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME} service decreased: {1_DecreaseAmount} [ICON_Tourism] Tourism and {2_DecreasedStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BOLSHOI_REMOVED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME} effects deactivated: {1_LostAmount} [ICON_Tourism] Tourism and {2_LostStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}. The established service remains'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BROADWAY', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME}: {1_TotalAmount} [ICON_Tourism] Tourism and {2_TotalStack} [ICON_GreatArtist] Great Artist {3_TotalStackCount : plural 1?point; other?points;}.[NEWLINE]Supply Chain: {3_TotalStackCount} supplied {3_TotalStackCount : plural 1?Fashion House; other?Fashion Houses;} [ICON_ARROW] adjacent Broadway.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BROADWAY_NEW', 'a new {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME} service: {1_NewAmount} [ICON_Tourism] Tourism and {2_NewStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BROADWAY_INCREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME} service increased: {1_IncreaseAmount} [ICON_Tourism] Tourism and {2_IncreasedStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BROADWAY_DECREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME} service decreased: {1_DecreaseAmount} [ICON_Tourism] Tourism and {2_DecreasedStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BROADWAY_REMOVED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME} effects deactivated: {1_LostAmount} [ICON_Tourism] Tourism and {2_LostStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}. The established service remains'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_SYDNEY', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME}: {1_TotalAmount} [ICON_Tourism] Tourism and {2_TotalStack} [ICON_GreatArtist] Great Artist {3_TotalStackCount : plural 1?point; other?points;}.[NEWLINE]Supply Chain: {3_TotalStackCount} supplied {3_TotalStackCount : plural 1?Fashion House; other?Fashion Houses;} [ICON_ARROW] adjacent Sydney Opera House.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_SYDNEY_NEW', 'a new {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME} service: {1_NewAmount} [ICON_Tourism] Tourism and {2_NewStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_SYDNEY_INCREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME} service increased: {1_IncreaseAmount} [ICON_Tourism] Tourism and {2_IncreasedStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_SYDNEY_DECREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME} service decreased: {1_DecreaseAmount} [ICON_Tourism] Tourism and {2_DecreasedStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_SYDNEY_REMOVED', '{LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME} effects deactivated: {1_LostAmount} [ICON_Tourism] Tourism and {2_LostStack} [ICON_GreatArtist] Great Artist {3_StackCount : plural 1?point; other?points;}. The established service remains'),
    ('en_US', 'LOC_CSC_WONDER_SERVICES_PLOT_TOOLTIP_HEADER', ''),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_2_EFFECT', '+1 [ICON_Production] Production from an adjacent Textile Workshop, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold to the Textile Workshop.[NEWLINE][NEWLINE]At Naval Tradition, a Lighthouse adjacent to a supplied Textile Workshop establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME}: +20% [ICON_Production] Production toward Renaissance Era or earlier naval units and +1 [ICON_GreatAdmiral] Great Admiral point from each adjacent supplied Textile Workshop, and +1 [ICON_Citizen] Citizen slot in the Harbor.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_2_CIVIC', 'A Lighthouse adjacent to a supplied Textile Workshop establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME}: +20% [ICON_Production] Production toward Renaissance Era or earlier naval units and +1 [ICON_GreatAdmiral] Great Admiral point from each adjacent supplied Textile Workshop, and +1 [ICON_Citizen] Citizen slot in the Harbor.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_2_CIVIC_APPEND', '[NEWLINE][NEWLINE]A Lighthouse adjacent to a supplied Textile Workshop establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME}: +20% [ICON_Production] Production toward Renaissance Era or earlier naval units and +1 [ICON_GreatAdmiral] Great Admiral point from each adjacent supplied Textile Workshop, and +1 [ICON_Citizen] Citizen slot in the Harbor.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION', '{LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME}: {1_TotalAmount}% [ICON_Production] Production toward Renaissance Era or earlier naval units and {2_TotalStack} [ICON_GreatAdmiral] Great Admiral {3_TotalStackCount : plural 1?point; other?points;}.[NEWLINE]Supply Chain: {3_TotalStackCount} supplied {3_TotalStackCount : plural 1?Textile Workshop; other?Textile Workshops;} [ICON_ARROW] adjacent Lighthouse.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_NEW', 'a new {LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME} service: {1_NewAmount}% [ICON_Production] Production toward Renaissance Era or earlier naval units and {2_NewStack} [ICON_GreatAdmiral] Great Admiral {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_INCREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME} service increased: {1_IncreaseAmount}% [ICON_Production] Production toward Renaissance Era or earlier naval units and {2_IncreasedStack} [ICON_GreatAdmiral] Great Admiral {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_DECREASED', '{LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME} service decreased: {1_DecreaseAmount}% [ICON_Production] Production toward Renaissance Era or earlier naval units and {2_DecreasedStack} [ICON_GreatAdmiral] Great Admiral {3_StackCount : plural 1?point; other?points;}'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION_REMOVED', '{LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME} effects deactivated: {1_LostAmount}% [ICON_Production] Production toward Renaissance Era or earlier naval units and {2_LostStack} [ICON_GreatAdmiral] Great Admiral {3_StackCount : plural 1?point; other?points;}. The established service and its [ICON_Citizen] Citizen slot remain'),
    ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCBASE_TITLE', 'Base Materials'),
    ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCBASE_PARA_1', ''),
    ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCSPEC_TITLE', 'Specialty Materials'),
    ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCSPEC_PARA_1', ''),
    ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCGOODS_TITLE', 'Goods Providers'),
    ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCGOODS_PARA_1', ''),
    ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCSALES_TITLE', 'Sales Districts'),
    ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCSALES_PARA_1', ''),
    ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_HISTORY_TITLE', 'Historical Context'),
    ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_HISTORY_PARA_1', 'Textile making was among the most widespread urban industries long before the factory age. Spinning, weaving, dyeing, fulling and finishing demanded distinct skills, tools, and dependable supplies of fibre, color, water and trade. In medieval and early modern towns these crafts often gathered around workshops, markets and waterfronts, where merchants could turn local materials into cloth that travelled much farther than the field or flock that supplied it. The Tailors'' Quarter represents that first concentration: a practical neighborhood of makers transforming raw material into a durable, valuable good.'),
    ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_HISTORY_PARA_2', 'Fibres processed in a workshop become tailored consumer goods, then fashion and performance goods sold into the institutions where a city presents itself to its people and the wider world. And so, as the chain develops, cloth becomes more than a necessity: tailors serve religious ceremony, civic display, theaters and commerce; fine dyes, silk, silver and gold make dress a visible language of wealth, office and taste.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_CHAPTER_CSCHAIN_PARA_1', 'From nearby cotton fields and flax plots, bundles of fibre arrive at the Textile Workshop; wool joins them where flocks are kept. Spinning wheels draw the fibres into thread, and looms turn that thread into sturdy lengths of cloth. The local Tailor cuts these bolts into everyday clothing, while the Fashion House selects finer weaves for elaborate dress. Heavier canvas passes to an adjacent Lighthouse for the harbor''s sails and stores, carrying the Quarter''s work from loom to waterfront.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_CHAPTER_HISTORY_TITLE', 'Historical Context'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_CHAPTER_HISTORY_PARA_1', 'Before cloth could be cut into a garment, raw fibre had to be cleaned, spun into yarn and woven. Dyeing, fulling and other finishing work could follow. Each task called for its own tools and practiced hands, and the quality of one step shaped what the next craftsperson could make. Textile workshops helped bring these skills together and gave tailors dependable bolts of cloth rather than an uncertain assortment of household pieces.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_CHAPTER_HISTORY_PARA_2', 'That output served more than clothing. Towns needed plain fabric for daily wear and finer cloth for ceremonial and fashionable dress, while ports depended on strong canvas for sails, awnings and coverings. Merchants carried fibre in from fields and flocks and sent woven goods onward through markets and harbors. The textile workshop stood between those worlds, turning rural materials into something that could be worn at home or carried across the sea.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_CSCHAIN_PARA_1', 'The Textile Workshop draws on improved Tailors'' [ICON_CSC_BASE] Base Materials nearby, turns their fibres into cloth and sail canvas, and sends that steady flow to the adjacent Lighthouse.[NEWLINE][NEWLINE]This gives a Citizen the opportunity to take up employment as a Dockmaster in the Harbor, coordinating crews, stores and waterfront traffic so the city can fit out early naval vessels more efficiently and cultivate experienced Great Admirals.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_HISTORY_TITLE', 'Historical Context'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_CHAPTER_HISTORY_PARA_1', 'Busy harbors required more than quays and warehouses. Dockmasters allocated berths, coordinated loading crews, supervised stores and repairs, and kept vessels moving through limited waterfront space. As maritime states expanded, this everyday administration became part of naval power: fleets could be built and supplied more reliably, while officers gained the logistical experience on which successful commands depended.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TAILOR_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TAILOR_CHAPTER_CSCHAIN_PARA_1', 'Cloth arriving from the local Textile Workshop becomes fitted garments, work clothes and ceremonial dress in the Tailor''s hands. Nearby Temples and Markets draw those finished goods into religious and commercial life, while domestic trade routes carry the Quarter''s craft to cities without workshops of their own.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TAILOR_CHAPTER_HISTORY_TITLE', 'Historical Context'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TAILOR_CHAPTER_HISTORY_PARA_1', 'Tailoring emerged as a specialized urban trade wherever woven cloth became valuable enough to cut and fit rather than use in simple lengths. Tailors measured customers, shaped panels and coordinated the work of apprentices and finishers, concentrating skills that distinguished made clothing from household sewing.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_TAILOR_CHAPTER_HISTORY_PARA_2', 'Guilds protected standards and training, while religious houses commissioned vestments and civic markets widened demand for recognizable styles. Together, institutional orders and everyday commerce allowed specialist tailors to serve a broader public and made clothing an increasingly visible sign of occupation, devotion and status.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_CHAPTER_CSCHAIN_PARA_1', 'The Tailor draws on cloth from the local Textile Workshop, turns it into garments and vestments, and supplies those finished goods to the adjacent Temple.[NEWLINE][NEWLINE]This gives a Citizen the opportunity to take up employment as a Sacristan in the Holy Site, caring for the material life of worship so the city deepens its Faith and supports the work of Great Prophets.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_CHAPTER_HISTORY_TITLE', 'Historical Context'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_CHAPTER_HISTORY_PARA_1', 'Sacristans cared for vestments, sacred furnishings, records and the daily material needs of worship. Their work linked textile crafts and other urban suppliers to religious institutions, ensuring that ceremony could be sustained through orderly preparation, maintenance and stewardship.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_FASHION_HOUSE_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_FASHION_HOUSE_CHAPTER_CSCHAIN_PARA_1', 'The Fashion House brings the Textile Workshop''s cloth together with improved [ICON_CSC_SPEC] Specialty Materials: dyes give it colour, silk lends lustre and fine metalwork finishes the garment. Designers, cutters and embroiderers turn these supplies into distinctive dress for the audiences and performers of nearby Amphitheaters, the Bolshoi Theatre, Broadway and Sydney Opera House. Demand grows with the population of each customer city, while domestic trade routes carry fashionable goods to cities without a Tailors'' Quarter of their own.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_FASHION_HOUSE_CHAPTER_HISTORY_TITLE', 'Historical Context'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_FASHION_HOUSE_CHAPTER_HISTORY_PARA_1', 'Fashion houses grew from the workshops of dressmakers, tailors and merchants who served courts and prosperous cities. A reputation for a particular cut or finish could draw customers beyond the neighbourhood; by the nineteenth century, leading houses increasingly presented coordinated collections and made the designer''s name part of the garment''s appeal. Their work still depended on a wide circle of skilled cutters, seamstresses, embroiderers and finishers.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_FASHION_HOUSE_CHAPTER_HISTORY_PARA_2', 'Fine clothing joined ordinary textile production to costly and far-reaching supplies. Silk, rich dyes, lace and silver ornament required specialist knowledge and dependable trade, while fashions changed the value of colours, fabrics and silhouettes. Dress advertised rank, wealth and belonging, but its spread through shops, illustrations and imitation also gave wider audiences a share in styles once associated with a small elite.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_FASHION_HOUSE_CHAPTER_HISTORY_PARA_3', 'Performance made clothing a public art. Theater and opera workshops used costume to establish character, period and spectacle, while the dress of patrons turned the auditorium into another stage for social display. Fashion houses supplied and interpreted both worlds, drawing ideas from celebrated performers and bringing theatrical effects into everyday dress. Their place in the city rested as much on cultural visibility as on the garments they sold.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_CHAPTER_CSCHAIN_PARA_1', 'The Fashion House draws on cloth from the local Textile Workshop and improved [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials nearby, turns them into costumes and performance dress, and supplies the adjacent Amphitheater.[NEWLINE][NEWLINE]This gives a Citizen the opportunity to take up employment as a Stage Manager in the Theater Square at Opera and Ballet, coordinating performers, costumes and production work so that each performance contributes to the city''s Tourism and the development of Great Artists.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_CHAPTER_HISTORY_TITLE', 'Historical Context'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_CHAPTER_HISTORY_PARA_1', 'Theater depended on someone who could turn the work of many crafts into a performance that began on time and unfolded in the right order. Stage managers coordinated performers, costumes, scenery, rehearsals and cues, keeping practical records and resolving the small disruptions that could bring a production to a halt. As urban theaters and opera houses developed larger companies and more elaborate staging, this coordination became an enduring profession: less visible than the actors or designers, but essential to the venue''s artistic life.'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME', 'Ballet Dancer'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_DESCRIPTION', 'A Service established on Bolshoi Theatre at Opera and Ballet when an adjacent Fashion House is supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials.[NEWLINE][NEWLINE]+2 [ICON_Tourism] Tourism and +1 [ICON_GreatArtist] Great Artist point from each adjacent supplied Fashion House. This Wonder service has no Citizen slot.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_BOLSHOI_EFFECT', '+1 [ICON_Culture] Culture per 5 [ICON_Citizen] Citizens from each adjacent Fashion House, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold per 5 [ICON_Citizen] Citizens to the Fashion House. Both sides use this city''s population.[NEWLINE][NEWLINE]At Opera and Ballet, an adjacent Fashion House supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME} service on this Wonder.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_BOLSHOI_EFFECT_APPEND', '[NEWLINE][NEWLINE]{LOC_CSC_TAILORS_STAGE_4_BOLSHOI_EFFECT}'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME', 'Musical Actor'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_DESCRIPTION', 'A Service established on Broadway at Opera and Ballet when an adjacent Fashion House is supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials.[NEWLINE][NEWLINE]+2 [ICON_Tourism] Tourism and +1 [ICON_GreatArtist] Great Artist point from each adjacent supplied Fashion House. This Wonder service has no Citizen slot.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_BROADWAY_EFFECT', '+1 [ICON_Culture] Culture per 5 [ICON_Citizen] Citizens from each adjacent Fashion House, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold per 5 [ICON_Citizen] Citizens to the Fashion House. Both sides use this city''s population.[NEWLINE][NEWLINE]At Opera and Ballet, an adjacent Fashion House supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME} service on this Wonder.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_BROADWAY_EFFECT_APPEND', '[NEWLINE][NEWLINE]{LOC_CSC_TAILORS_STAGE_4_BROADWAY_EFFECT}'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME', 'Opera Singer'),
    ('en_US', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_DESCRIPTION', 'A Service established on Sydney Opera House at Opera and Ballet when an adjacent Fashion House is supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials.[NEWLINE][NEWLINE]+2 [ICON_Tourism] Tourism and +1 [ICON_GreatArtist] Great Artist point from each adjacent supplied Fashion House. This Wonder service has no Citizen slot.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_SYDNEY_EFFECT', '+1 [ICON_Culture] Culture per 5 [ICON_Citizen] Citizens from each adjacent Fashion House, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold per 5 [ICON_Citizen] Citizens to the Fashion House. Both sides use this city''s population.[NEWLINE][NEWLINE]At Opera and Ballet, an adjacent Fashion House supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials establishes a {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME} service on this Wonder.'),
    ('en_US', 'LOC_CSC_TAILORS_STAGE_4_SYDNEY_EFFECT_APPEND', '[NEWLINE][NEWLINE]{LOC_CSC_TAILORS_STAGE_4_SYDNEY_EFFECT}'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_CHAPTER_CSCHAIN_PARA_1', 'The Fashion House draws on cloth from the local Textile Workshop and improved [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials nearby, turns them into ballet costumes and ribbons, and supplies the adjacent Bolshoi Theatre.[NEWLINE][NEWLINE]This gives a Citizen the opportunity to take up employment as a Ballet Dancer at the Bolshoi Theatre at Opera and Ballet, bringing movement and costume together in performances that contribute to the city''s Tourism and the development of Great Artists.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_CHAPTER_HISTORY_TITLE', 'Historical Context'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_CHAPTER_HISTORY_PARA_1', 'Ballet developed from European court entertainments into a professional stage art supported by schools, companies and a demanding daily practice. Dancers learned to tell stories through movement, often performing as part of a closely rehearsed ensemble. Their costumes helped establish character while allowing the body''s movements to remain visible. The profession joined artistic expression to sustained physical training, and large theaters such as the Bolshoi gave dancers a lasting place in a city''s public cultural life.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_CHAPTER_CSCHAIN_PARA_1', 'The Fashion House draws on cloth from the local Textile Workshop and improved [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials nearby, turns them into operatic costumes and performance dress, and supplies the adjacent Sydney Opera House.[NEWLINE][NEWLINE]This gives a Citizen the opportunity to take up employment as an Opera Singer at Sydney Opera House at Opera and Ballet, giving voice and character to staged works that contribute to the city''s Tourism and the development of Great Artists.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_CHAPTER_HISTORY_TITLE', 'Historical Context'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_CHAPTER_HISTORY_PARA_1', 'Opera grew into a distinctive form of theater during the seventeenth century, placing the sung voice at the center of dramatic storytelling. Singers combined musical training with the work of portraying a character, supported by orchestras, scenery and costumes. Dress could establish a role''s social position, period or personality before a word was sung. The Opera Singer became a professional interpreter of this shared stagecraft, giving audiences a story through both the sound of the voice and the presence of the performer.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_CHAPTER_CSCHAIN_PARA_1', 'The Fashion House draws on cloth from the local Textile Workshop and improved [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials nearby, turns them into theatrical costumes, and supplies the adjacent Broadway.[NEWLINE][NEWLINE]This gives a Citizen the opportunity to take up employment as a Musical Actor at Broadway at Opera and Ballet, joining acting, song and movement in performances that contribute to the city''s Tourism and the development of Great Artists.'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_CHAPTER_HISTORY_TITLE', 'Historical Context'),
    ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_CHAPTER_HISTORY_PARA_1', 'Musical theater brought acting, song and dance into the same performance. As songs became more closely integrated with dramatic stories, performers needed to carry a character through dialogue, music and movement rather than present each skill as a separate attraction. Broadway became a prominent setting for this demanding combination of crafts. Costumes helped make quick changes of character and scene legible to the audience, while the Musical Actor brought the written role to life through a performance shared with the company.');

-- Stage 4 customer Civilopedia integration
CREATE TEMP TABLE TAILORS_STAGE4_CUSTOMERS (BuildingType TEXT, ServiceNameTag TEXT, Overview TEXT);
INSERT INTO TAILORS_STAGE4_CUSTOMERS (BuildingType, ServiceNameTag, Overview) VALUES
    ('BUILDING_AMPHITHEATER', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME', 'The Amphitheater gives fashionable dress a public setting: the Fashion House supplies performers and patrons, connecting the textile trades to the city''s cultural life.'),
    ('BUILDING_MARAE', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME', 'The Marae brings the Fashion House''s craft into a gathering place where performance, ceremony and community give clothing its public meaning.'),
    ('BUILDING_BOLSHOI_THEATRE', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME', 'The Bolshoi Theatre draws on the Fashion House for the costumes and ceremonial dress that join textile craft to the spectacle of opera and ballet.'),
    ('BUILDING_BROADWAY', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME', 'Broadway brings the Fashion House into the lively exchange between theatrical costume, celebrated performers and the fashions of the street.'),
    ('BUILDING_SYDNEY_OPERA_HOUSE', 'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME', 'Sydney Opera House gives the Fashion House a prominent venue for performance dress, linking specialist craft to a city''s cultural identity.');

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US', 'LOC_PEDIA_BUILDINGS_PAGE_' || BuildingType || '_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'
FROM TAILORS_STAGE4_CUSTOMERS;

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US', 'LOC_PEDIA_BUILDINGS_PAGE_' || BuildingType || '_CHAPTER_CSCHAIN_PARA_1',
    Overview || '[NEWLINE][NEWLINE]+1 [ICON_Culture] Culture per 5 [ICON_Citizen] Citizens from each adjacent Fashion House, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold per 5 [ICON_Citizen] Citizens to the Fashion House. Both sides use this city''s population.[NEWLINE][NEWLINE]At Opera and Ballet, an adjacent Fashion House supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials can establish a {' || ServiceNameTag || '} service here.'
FROM TAILORS_STAGE4_CUSTOMERS;
DROP TABLE TAILORS_STAGE4_CUSTOMERS;

-- Tailors' Quarter Civilopedia data
CREATE TEMP TABLE TAILORS_RESOURCES (
    ResourceName TEXT,
    ResourceCategory TEXT,
    DisplayName TEXT
);

CREATE TEMP TABLE TAILORS_SALES_DISTRICTS (
    DistrictType TEXT,
    NameTag TEXT,
    SortIndex INTEGER,
    Overview TEXT
);

INSERT INTO TAILORS_RESOURCES (ResourceName, ResourceCategory, DisplayName) VALUES
    ('RESOURCE_COTTON', 'CLASS_CSC_TAILORS_BASE', 'Cotton'),
    ('RESOURCE_SHEEP', 'CLASS_CSC_TAILORS_BASE', 'Sheep'),
    ('RESOURCE_CSC_FLAX', 'CLASS_CSC_TAILORS_BASE', 'Flax'),
    ('RESOURCE_DYES', 'CLASS_CSC_TAILORS_SPEC', 'Dyes'),
    ('RESOURCE_SILK', 'CLASS_CSC_TAILORS_SPEC', 'Silk'),
    ('RESOURCE_SILVER', 'CLASS_CSC_TAILORS_SPEC', 'Silver');

INSERT INTO TAILORS_SALES_DISTRICTS (DistrictType, NameTag, SortIndex, Overview) VALUES
    ('DISTRICT_HARBOR', 'LOC_DISTRICT_HARBOR_NAME', 10, 'Bales of cloth move naturally through the Harbor, where dockside demand and overseas trade draw the work of nearby textile makers toward the waterfront.[NEWLINE][NEWLINE]An adjacent Tailors'' Quarter gains +1 [ICON_Gold] Gold, and the Harbor gains +1 [ICON_Production] Production in return.'),
    ('DISTRICT_COMMERCIAL_HUB', 'LOC_DISTRICT_COMMERCIAL_HUB_NAME', 20, 'The Commercial Hub brings staple provisions and finished cloth into the same busy exchange, giving bakers and tailors a common place to reach the city''s buyers.[NEWLINE][NEWLINE]An adjacent Bakers'' Quarter gains +1 [ICON_Gold] Gold and the Commercial Hub gains +1 [ICON_Food] Food in return; an adjacent Tailors'' Quarter gains +1 [ICON_Gold] Gold and the Commercial Hub gains +1 [ICON_Culture] Culture in return.'),
    ('DISTRICT_HOLY_SITE', 'LOC_DISTRICT_HOLY_SITE_NAME', 30, 'Vestments, hangings and ceremonial cloth tie the work of the Tailors'' Quarter to the ritual and visual life of the Holy Site.[NEWLINE][NEWLINE]An adjacent Tailors'' Quarter gains +1 [ICON_Gold] Gold, and the Holy Site gains +1 [ICON_Culture] Culture in return.'),
    ('DISTRICT_THEATER', 'LOC_DISTRICT_THEATER_NAME', 40, 'Costumes, drapery and fashionable display make the Tailors'' Quarter a natural partner to the stages and audiences of the Theater Square.[NEWLINE][NEWLINE]An adjacent Tailors'' Quarter gains +1 [ICON_Gold] Gold, and the Theater Square gains +1 [ICON_Culture] Culture in return.');

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US',
    CASE ResourceCategory
        WHEN 'CLASS_CSC_TAILORS_BASE' THEN 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCBASE_PARA_1'
        WHEN 'CLASS_CSC_TAILORS_SPEC' THEN 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCSPEC_PARA_1'
    END,
    '[ICON_BULLET]' || GROUP_CONCAT('[ICON_' || ResourceName || '] ' || DisplayName, ' [NEWLINE][ICON_BULLET]')
FROM TAILORS_RESOURCES
GROUP BY ResourceCategory;

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
VALUES ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCGOODS_PARA_1', '');

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_TAILORS_QUARTER_CHAPTER_CSCSALES_PARA_1',
    '[ICON_BULLET]' || GROUP_CONCAT('[ICON_' || DistrictType || '] {' || NameTag || '}', ' [NEWLINE][ICON_BULLET]')
FROM (SELECT DistrictType, NameTag FROM TAILORS_SALES_DISTRICTS ORDER BY SortIndex);

UPDATE LocalizedText
SET Text = Text || '[NEWLINE][ICON_BULLET] [ICON_TAILORS] Tailors'' Quarter'
WHERE Tag IN (SELECT 'LOC_PEDIA_RESOURCES_PAGE_' || ResourceName || '_CHAPTER_CSCQUAR_PARA_1' FROM TAILORS_RESOURCES);

INSERT OR IGNORE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US', 'LOC_PEDIA_RESOURCES_PAGE_' || ResourceName || '_CHAPTER_CSCQUAR_TITLE', 'Supply Chains'
FROM TAILORS_RESOURCES;

INSERT OR IGNORE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US', 'LOC_PEDIA_RESOURCES_PAGE_' || ResourceName || '_CHAPTER_CSCQUAR_PARA_1',
    CASE ResourceCategory
        WHEN 'CLASS_CSC_TAILORS_BASE' THEN '[ICON_CSC_BASE] Base Materials:[NEWLINE][NEWLINE][ICON_BULLET] [ICON_TAILORS] Tailors'' Quarter'
        WHEN 'CLASS_CSC_TAILORS_SPEC' THEN '[ICON_CSC_SPEC] Specialty Materials:[NEWLINE][NEWLINE][ICON_BULLET] [ICON_TAILORS] Tailors'' Quarter'
    END
FROM TAILORS_RESOURCES;

UPDATE LocalizedText
SET Text = Text || '[NEWLINE][NEWLINE]' || (
    SELECT Overview FROM TAILORS_SALES_DISTRICTS
    WHERE 'LOC_PEDIA_DISTRICTS_PAGE_' || DistrictType || '_CHAPTER_CSCHAIN_PARA_1' = LocalizedText.Tag
)
WHERE Tag IN (
    SELECT 'LOC_PEDIA_DISTRICTS_PAGE_' || DistrictType || '_CHAPTER_CSCHAIN_PARA_1'
    FROM TAILORS_SALES_DISTRICTS
    WHERE DistrictType <> 'DISTRICT_COMMERCIAL_HUB'
);

INSERT OR IGNORE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US', 'LOC_PEDIA_DISTRICTS_PAGE_' || DistrictType || '_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'
FROM TAILORS_SALES_DISTRICTS;

INSERT OR IGNORE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US', 'LOC_PEDIA_DISTRICTS_PAGE_' || DistrictType || '_CHAPTER_CSCHAIN_PARA_1', Overview
FROM TAILORS_SALES_DISTRICTS
WHERE DistrictType <> 'DISTRICT_COMMERCIAL_HUB';

-- The Commercial Hub is a shared sales district. Curate its complete section as
-- one integrated passage rather than stacking independent Quarter fragments.
INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US',
    'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_COMMERCIAL_HUB_CHAPTER_CSCHAIN_PARA_1',
    Overview
FROM TAILORS_SALES_DISTRICTS
WHERE DistrictType = 'DISTRICT_COMMERCIAL_HUB';

-- Stage 3 customer-building pages use one integrated Supply Chains section.
CREATE TEMP TABLE TAILORS_STAGE3_CUSTOMERS (
    BuildingType TEXT,
    BaseBuildingType TEXT
);

INSERT INTO TAILORS_STAGE3_CUSTOMERS (BuildingType, BaseBuildingType) VALUES
    ('BUILDING_MARKET', 'BUILDING_MARKET'),
    ('BUILDING_SUKIENNICE', 'BUILDING_MARKET'),
    ('BUILDING_GRAND_BAZAAR', 'BUILDING_MARKET'),
    ('BUILDING_TEMPLE', 'BUILDING_TEMPLE'),
    ('BUILDING_STAVE_CHURCH', 'BUILDING_TEMPLE'),
    ('BUILDING_PRASAT', 'BUILDING_TEMPLE');

INSERT OR IGNORE INTO LocalizedText (Language, Tag, Text)
VALUES ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_MARKET_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'),
       ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_TEMPLE_CHAPTER_CSCHAIN_TITLE', 'Supply Chains');

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
VALUES ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_MARKET_CHAPTER_CSCHAIN_PARA_1',
        'Markets bring staple provisions and finished cloth into the same daily exchange. Fresh goods from adjacent Bakeries feed the population, while garments from adjacent Tailors answer household, professional and ceremonial demand.[NEWLINE][NEWLINE]Each adjacent Tailor grants +0.1 [ICON_Culture] Culture per [ICON_Citizen] Citizen to the Market city, in exchange for +0.1 [ICON_Production] Production and +0.1 [ICON_Gold] Gold per [ICON_Citizen] Citizen to the Tailor city.'),
       ('en_US', 'LOC_PEDIA_BUILDINGS_PAGE_BUILDING_TEMPLE_CHAPTER_CSCHAIN_PARA_1',
        'Temples draw on the Tailor for vestments, hangings and other ceremonial cloth, joining material craft to the city''s religious life.[NEWLINE][NEWLINE]Each adjacent Tailor grants +0.1 [ICON_Culture] Culture per [ICON_Citizen] Citizen to the Temple city, in exchange for +0.1 [ICON_Production] Production and +0.1 [ICON_Gold] Gold per [ICON_Citizen] Citizen to the Tailor city.[NEWLINE][NEWLINE]At Divine Right, an adjacent supplied Tailor can establish a {LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME} here.');

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US', 'LOC_PEDIA_BUILDINGS_PAGE_' || CivUniqueBuildingType || '_CHAPTER_CSCHAIN_TITLE', 'Supply Chains'
FROM (
    SELECT BuildingType AS CivUniqueBuildingType
    FROM TAILORS_STAGE3_CUSTOMERS
    WHERE BuildingType <> BaseBuildingType
);

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US', 'LOC_PEDIA_BUILDINGS_PAGE_' || BuildingType || '_CHAPTER_CSCHAIN_PARA_1',
    CASE BaseBuildingType
        WHEN 'BUILDING_MARKET' THEN (SELECT Text FROM LocalizedText WHERE Language='en_US' AND Tag='LOC_PEDIA_BUILDINGS_PAGE_BUILDING_MARKET_CHAPTER_CSCHAIN_PARA_1')
        WHEN 'BUILDING_TEMPLE' THEN (SELECT Text FROM LocalizedText WHERE Language='en_US' AND Tag='LOC_PEDIA_BUILDINGS_PAGE_BUILDING_TEMPLE_CHAPTER_CSCHAIN_PARA_1')
    END
FROM TAILORS_STAGE3_CUSTOMERS
WHERE BuildingType <> BaseBuildingType;

DROP TABLE TAILORS_RESOURCES;
DROP TABLE TAILORS_SALES_DISTRICTS;
DROP TABLE TAILORS_STAGE3_CUSTOMERS;

-- Keep the Theater Square's existing Quarter overview and add one service pointer.
UPDATE LocalizedText
SET Text = Text || '[NEWLINE][NEWLINE]At Opera and Ballet, an Amphitheater served by an adjacent Fashion House supplied with both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials can establish a {LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME} service.'
WHERE Language = 'en_US' AND Tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_THEATER_CHAPTER_CSCHAIN_PARA_1';

INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT Language, 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_ACROPOLIS_CHAPTER_CSCHAIN_TITLE', Text
FROM LocalizedText WHERE Tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_THEATER_CHAPTER_CSCHAIN_TITLE';
INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT Language, 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_ACROPOLIS_CHAPTER_CSCHAIN_PARA_1', Text
FROM LocalizedText WHERE Tag = 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_THEATER_CHAPTER_CSCHAIN_PARA_1';
