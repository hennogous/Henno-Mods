-- The ice art is a placeholder for the future mist/Rimfall exterior.
-- A distinct feature avoids climate-driven ice melt changing the boundary.
INSERT INTO Types (Type,Kind) VALUES ('FEATURE_DISC_VOID','KIND_FEATURE');
INSERT INTO Features (FeatureType,Name,Description,Impassable,Removable,NoResource,Settlement)
VALUES ('FEATURE_DISC_VOID','LOC_DISC_VOID_NAME','LOC_DISC_VOID_DESCRIPTION',1,0,1,0);
INSERT INTO Feature_ValidTerrains (FeatureType,TerrainType)
VALUES ('FEATURE_DISC_VOID','TERRAIN_OCEAN'),('FEATURE_DISC_VOID','TERRAIN_COAST');
