-- Complete ordinary supplier -> producer attachments from resource mappings
-- loaded by479, including the supported CL/R2/Suk stack. These are real Food/Culture exchanges, used by
-- players and AI alike; they are independent of CE and AI policy settings.
--
-- A resource tag says WHAT a supplier provides. Improvement_ValidResources
-- says WHICH improvements can develop that resource. Joining both prevents
-- optional resource packs/City Lights from qualifying as supply while missing
-- the incoming producer yield. Existing roots retain their plot, adjacency,
-- local producer and material requirements; this adds only their missing hosts.
--
-- Industry/Corporation have separate transaction roots. Preserve those special
-- paths rather than attaching an additional ordinary payment on the same plot.
CREATE TEMP TABLE CSC_MaterialTransactionRoots (
    MaterialClass TEXT NOT NULL,
    ModifierId TEXT NOT NULL
);

INSERT INTO CSC_MaterialTransactionRoots
        (   MaterialClass,              ModifierId   )
VALUES  (   'CLASS_CSC_BAKERS_BASE',    'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER'   ),
        (   'CLASS_CSC_BAKERS_BASE',    'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND'   ),
        (   'CLASS_CSC_BAKERS_SPEC',    'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'CLASS_CSC_TAILORS_BASE',   'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'CLASS_CSC_TAILORS_SPEC',   'MOD_CSC_TAILORS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   );

-- DISTINCT coalesces resources sharing the same improvement/root. NOT EXISTS
-- makes reapplication safe even on a fixture without a unique constraint.
-- Only defined improvements and producer roots are attached; dormant Quarters
-- or absent optional mods contribute no rows. Later compatibility generators
-- must attach their own roots or arrange a second reconciliation after loading.
INSERT OR IGNORE INTO ImprovementModifiers
        (   ImprovementType,   ModifierId   )
SELECT DISTINCT i.ImprovementType, r.ModifierId
FROM CSC_MaterialTransactionRoots r
JOIN Modifiers m ON m.ModifierId = r.ModifierId
JOIN TypeTags t ON t.Tag = r.MaterialClass
JOIN Improvement_ValidResources v ON v.ResourceType = t.Type
JOIN Improvements i ON i.ImprovementType = v.ImprovementType
WHERE i.ImprovementType NOT IN ('IMPROVEMENT_INDUSTRY', 'IMPROVEMENT_CORPORATION')
AND NOT EXISTS (
    SELECT 1 FROM ImprovementModifiers existing
    WHERE existing.ImprovementType = i.ImprovementType
    AND existing.ModifierId = r.ModifierId
);

DROP TABLE CSC_MaterialTransactionRoots;
