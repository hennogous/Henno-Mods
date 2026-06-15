-- ModSupport_LGD_GOLD
-- Author: Henno
-- DateCreated: 2026-05-01
--------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
--  +1 Gold for every 5 Citizens in the city for each adjacent Cafe (Conservatory side)
--  MOD_CSC_BAKERS_GOLD_TO_CAFE_AT_POP_*_ATTACH is defined in CSC_Q_BAKERS_GOLD.sql (LoadOrder 101); Production return lives in ModSupport_LGD.sql.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO BuildingModifiers (BuildingType, ModifierId)
SELECT
    'BUILDING_LEU_CONSERVATORY',
    'MOD_CSC_BAKERS_GOLD_TO_CAFE_AT_POP_' || Pop || '_ATTACH'
FROM CSC_PopulationLevels
WHERE Pop > 0;
