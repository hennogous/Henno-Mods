-- Complete ordinary supplier -> producer attachments from resource mappings
-- loaded by800010, including the supported CL/R2/Suk stack. These are real Food/Culture exchanges, used by
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
CREATE TEMP VIEW CSC_MaterialTransactionRoots AS
SELECT DISTINCT t.MaterialClass, b.RootModifierId AS ModifierId
FROM CSC_MaterialTransactions t
JOIN CSC_MaterialTransactionYields y USING (TransactionId)
JOIN CSC_MaterialTransactionBindings b USING (TransactionId, LegKey)
WHERE y.Recipient = 'PRODUCER' AND y.ImprovementScope = 'REGISTERED_INPUT';

-- DISTINCT coalesces resources sharing the same improvement/root. NOT EXISTS
-- makes reapplication safe even on a fixture without a unique constraint.
-- Only defined improvements and producer roots are attached; dormant Quarters
-- or absent optional mods contribute no rows. Later compatibility generators
-- must attach their own roots or arrange a second reconciliation after loading.
-- R2 creates Sawmill at799990/800000; CL adds improvement resource links at9999.
-- An early479 pass misses these hosts even though their resources already exist.
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

DROP VIEW CSC_MaterialTransactionRoots;

-- Session-static read-model for actual incoming hosts, not another authored
-- list. Include legacy registrations and exact M&C roots. The facts adapter
-- consults this per observed improvement; valid-pair jobs remain separate.

DELETE FROM CSC_MaterialTransactionInputHosts;
INSERT INTO CSC_MaterialTransactionInputHosts
SELECT DISTINCT b.TransactionId, b.LegKey, i.ImprovementType
FROM CSC_MaterialTransactionBindings b
JOIN CSC_MaterialTransactionYields y USING (TransactionId, LegKey)
JOIN ImprovementModifiers i ON i.ModifierId = b.RootModifierId
WHERE y.Recipient = 'PRODUCER';
