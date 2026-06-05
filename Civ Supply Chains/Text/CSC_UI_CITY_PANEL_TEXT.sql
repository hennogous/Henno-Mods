-- ===========================================================================
--  CIV SUPPLY CHAINS: CITY PANEL UI TEXT
-- ===========================================================================
-- Renames the city details "Buildings and Districts" section to better match
-- CSC's framing of district/building networks as infrastructure and services.
-- Sukritact's Simple UI Adjustments reuses LOC_HUD_CITY_BUILDINGS_AND_DISTRICTS
-- in its city panel overview, so this override covers both vanilla and SUIA.

INSERT OR REPLACE INTO LocalizedText
    (   Language,   Tag,                                           Text                                )
VALUES
    (   'en_US',    'LOC_HUD_CITY_BUILDINGS_AND_DISTRICTS',        'Infrastructure and Services'       ),
    (   'en_US',    'LOC_PRODUCTION_PANEL_SCROLL_TO_BUILDINGS',    'Scroll to Infrastructure and Services' );
