-- Disposable forecast probe. Give each Quarter a Builder improvement legal
-- only on its real Base materials. The paired arm changes only the private
-- adjacency amount. Keep this file out of the CSC manifest.
CREATE TEMP TABLE CSC_ProbeSupplier AS
SELECT DISTINCT m.QuarterKey, q.DistrictType, t.Type AS ResourceType,
       'IMPROVEMENT_CSC_PROBE_' || m.QuarterKey AS Improvement
FROM CSC_QuarterMaterialAdjacencyConfig m
JOIN TypeTags t ON t.Tag = m.SourceTag
JOIN Resources r ON r.ResourceType = t.Type
JOIN Districts q ON q.DistrictType = 'DISTRICT_CSC_' || m.QuarterKey || '_QUARTER'
WHERE m.SourceTag = 'CLASS_CSC_' || m.QuarterKey || '_BASE'
  AND m.SourceFilter = '' AND m.AdjacencyType = 'FROM_RINGS_TYPETAG_RESOURCE';

INSERT INTO Types (Type, Kind)
SELECT DISTINCT Improvement, 'KIND_IMPROVEMENT' FROM CSC_ProbeSupplier;
INSERT INTO Improvements (ImprovementType, Name, Buildable, PlunderType, Icon)
SELECT DISTINCT Improvement, Improvement, 1, 'PLUNDER_GOLD', 'ICON_IMPROVEMENT_FARM'
FROM CSC_ProbeSupplier;
INSERT INTO Improvement_ValidResources (ImprovementType, ResourceType)
SELECT Improvement, ResourceType FROM CSC_ProbeSupplier;
INSERT INTO Improvement_ValidBuildUnits (ImprovementType, UnitType)
SELECT DISTINCT Improvement, 'UNIT_BUILDER' FROM CSC_ProbeSupplier;

INSERT INTO Adjacency_YieldChanges
       (ID, Description, YieldType, YieldChange, TilesRequired, AdjacentImprovement)
SELECT DISTINCT Improvement, 'LOC_CSC_AI_PLACEMENT_NAME', 'YIELD_CSC_AI_PLACEMENT',
       __PROBE_WEIGHT__, 1, Improvement FROM CSC_ProbeSupplier;
INSERT INTO District_Adjacencies (DistrictType, YieldChangeId)
SELECT DISTINCT DistrictType, Improvement FROM CSC_ProbeSupplier;
DROP TABLE CSC_ProbeSupplier;
