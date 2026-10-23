-- ISOLATED DIAGNOSTIC ONLY. Not registered in CSC modinfo or the live game.
-- Test the native resource-forecast path against the conditional plot-modifier
-- path. Existing live presence40 motivates Base40; Specialty20 is deliberately
-- lower. These are private planning units, not economic yields or transactions.
-- Raw resource values also affect unowned plots/other planning. Measure those
-- effects; do not adopt this broad diagnostic as targeted preservation proof.
-- Use only the already registered/UI-filtered private channel. No new type,
-- real yield, unit, research, purchase, resource or improvement is granted.
CREATE TEMP TABLE CSC_AI_ForecastTrial (ResourceType TEXT PRIMARY KEY, Amount INTEGER);
INSERT OR IGNORE INTO CSC_AI_ForecastTrial
        (   ResourceType,   Amount   )
SELECT r.ResourceType, MAX(CASE WHEN t.Tag IN ('CLASS_CSC_BAKERS_BASE','CLASS_CSC_TAILORS_BASE') THEN 40 ELSE 20 END)
FROM Resources r JOIN TypeTags t ON t.Type=r.ResourceType
WHERE t.Tag IN ('CLASS_CSC_BAKERS_BASE','CLASS_CSC_BAKERS_SPEC','CLASS_CSC_TAILORS_BASE','CLASS_CSC_TAILORS_SPEC')
GROUP BY r.ResourceType;
INSERT OR REPLACE INTO Resource_YieldChanges
        (   ResourceType,   YieldType,   YieldChange   )
SELECT ResourceType, 'YIELD_CSC_AI_PLACEMENT', Amount FROM CSC_AI_ForecastTrial;
DROP TABLE CSC_AI_ForecastTrial;
