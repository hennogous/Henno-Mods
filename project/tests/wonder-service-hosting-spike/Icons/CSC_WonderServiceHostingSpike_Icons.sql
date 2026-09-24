-- Reuse the Amphitheater icon in this throwaway proof; no production art is
-- introduced by the spike.
INSERT OR REPLACE INTO IconDefinitions
        (   Name,                                                  Atlas,   'Index'   )
SELECT      ServiceIcon,                                           Atlas,   "Index"
FROM IconDefinitions
JOIN (
    SELECT 'ICON_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE' AS ServiceIcon
    UNION ALL SELECT 'ICON_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BOLSHOI'
    UNION ALL SELECT 'ICON_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BROADWAY'
    UNION ALL SELECT 'ICON_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_SYDNEY'
) AS ServiceIcons
WHERE Name = 'ICON_BUILDING_AMPHITHEATER';
