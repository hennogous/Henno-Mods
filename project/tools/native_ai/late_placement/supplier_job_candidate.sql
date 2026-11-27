-- Qualification overlay. Use the same stock improvement-to-district adjacency
-- shape as the Farm next to Korea's Seowon. Here the yield has no currency
-- conversion. Its role is to raise the hypothetical improvement's site value
-- before Civ chooses the improvement type and reserves a Builder job.
CREATE TEMP TABLE CSC_AI_SupplierJobEdges AS
WITH FirstSuppliers AS (
    SELECT DISTINCT q.DistrictType AS Quarter, host.ImprovementType AS Improvement
    FROM CSC_MaterialTransactions t
    JOIN CSC_QuarterFlowBuildings flow ON flow.BuildingType = t.ProducerBuildingType AND flow.Stage = 2
    JOIN CSC_MaterialTransactionInputHosts host ON host.TransactionId = t.TransactionId
    JOIN TypeTags material ON material.Tag = t.MaterialClass
    JOIN Improvement_ValidResources v ON v.ResourceType = material.Type AND v.ImprovementType = host.ImprovementType
    JOIN Districts q ON q.DistrictType = 'DISTRICT_CSC_' || t.QuarterKey || '_QUARTER'
    WHERE t.MaterialClass = 'CLASS_CSC_' || t.QuarterKey || '_BASE'
), SpecificFamilies AS (
    SELECT districts.DistrictType AS Quarter, rule.AdjacentImprovement AS Improvement
    FROM District_Adjacencies districts
    JOIN Adjacency_YieldChanges rule ON rule.ID = districts.YieldChangeId
    WHERE rule.ID GLOB 'CSC_AI_SUPPLIER_*' AND rule.TilesRequired = 1
)
SELECT f.Quarter, f.Improvement, CASE WHEN s.Improvement IS NULL THEN 1 ELSE 2 END AS Amount
FROM FirstSuppliers f LEFT JOIN SpecificFamilies s USING (Quarter, Improvement);

-- Reuse the forward material-family classification from CSC's gameplay data.
-- A selective resource-only family receives two private units per neighboring
-- Quarter. Others receive one. A Farm can compete on empty terrain; a Tailors
-- Plantation can serve unrelated luxuries. Both must remain eligible because
-- Flax Farms and Cotton Plantations supply that Quarter's Stage 2 buyer.
-- The improvement still needs ordinary build eligibility, a slot and a Builder.
INSERT OR IGNORE INTO Adjacency_YieldChanges
        (   ID,   Description,   YieldType,   YieldChange,   TilesRequired,   AdjacentDistrict   )
SELECT 'CSC_AI_SUPPLY_JOB_' || Quarter || '__' || Improvement, 'LOC_CSC_AI_PLACEMENT_NAME',
       'YIELD_CSC_AI_PLACEMENT', Amount, 1, Quarter
FROM CSC_AI_SupplierJobEdges ORDER BY Quarter, Improvement;

INSERT OR IGNORE INTO Improvement_Adjacencies
        (   ImprovementType,   YieldChangeId   )
SELECT Improvement, 'CSC_AI_SUPPLY_JOB_' || Quarter || '__' || Improvement
FROM CSC_AI_SupplierJobEdges ORDER BY Quarter, Improvement;

DROP TABLE CSC_AI_SupplierJobEdges;
