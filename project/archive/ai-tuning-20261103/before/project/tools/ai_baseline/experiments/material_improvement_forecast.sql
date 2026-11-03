-- DIAGNOSTIC ONLY: direct resource-compatible improvement forecasting.
-- Unregistered experiment; use only in a declared, pinned same-save comparison.
-- All owners, including humans, receive this native improvement table signal.
-- It has no currency conversion but may change citizen allocation and ordinary
-- city output indirectly. This is not AI-only release tuning.
-- Keep the raw resource40/20 control shared; add no Farm/Mine bonus or harvest
-- prohibition. Current native schema makes these three improvements resource-bound.
-- Loaded definitions are not proof of job creation, Builder execution or safety.
INSERT OR IGNORE INTO Improvement_YieldChanges
        (ImprovementType,           YieldType,                  YieldChange)
VALUES  ('IMPROVEMENT_PASTURE',     'YIELD_CSC_AI_PLACEMENT',   80),
        ('IMPROVEMENT_CAMP',        'YIELD_CSC_AI_PLACEMENT',   80),
        ('IMPROVEMENT_PLANTATION',  'YIELD_CSC_AI_PLACEMENT',   80);
UPDATE Improvement_YieldChanges
SET YieldChange=80
WHERE ImprovementType IN ('IMPROVEMENT_PASTURE','IMPROVEMENT_CAMP','IMPROVEMENT_PLANTATION')
  AND YieldType='YIELD_CSC_AI_PLACEMENT';
