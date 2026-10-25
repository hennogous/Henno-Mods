-- CSC_Q_BAKERS_REMOVE_WATER_MILL.sql
-- Removes the vanilla Water Mill after other mods have finished editing it.
--------------------------------------------------------------

-- The CSC Water Mill replaces the vanilla building's role rather than using a
-- BuildingReplaces entry, so the vanilla Water Mill is removed outright.
-- This runs in its own action with a LoadOrder above Better Balanced Game's
-- BBG_LoadLast (200000000). Other mods still insert rows such as
-- BuildingModifiers for BUILDING_WATER_MILL; deleting it before them leaves
-- those rows without a parent and fails foreign key validation. Deleting it
-- last lets the cascade remove them instead.
DELETE FROM Buildings WHERE BuildingType='BUILDING_WATER_MILL';
