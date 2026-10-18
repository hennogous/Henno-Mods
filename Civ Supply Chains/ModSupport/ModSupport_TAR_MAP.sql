-- TAR's generator uses 29 rather than vanilla's 30 as its density baseline.
-- Conditional action: read-only compatibility with its current generator;
-- no replacement of TAR scripts or resource distribution rules.
INSERT OR REPLACE INTO GlobalParameters (Name, Value)
VALUES ('CSC_MATERIAL_MAP_STANDARD_DENSITY', 29);
