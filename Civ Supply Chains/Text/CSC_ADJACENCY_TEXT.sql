-- CSC_ADJACENCY_TEXT
-- Generated from project\localization\CSC_ADJACENCY_TEXT.md by project/tools/localization/loc_md_to_sql.py
-- Edit the Markdown source, then regenerate this file.
--------------------------------------------------------------

INSERT OR REPLACE INTO LocalizedText
        (   Language,   Tag,                                    Text   )
VALUES  (   'en_US',    'LOC_CSC_ADJ_PREVIEW_LINE',             '{1_Amount} {2_Yield} from {3_Count : plural 1?the; other?{3_Count};} {5_Distance} {4_Source}.'   ),
        (   'en_US',    'LOC_CSC_ADJ_PREVIEW_NAMED_RESOURCE',   '{1_Amount} {2_Yield} from {3_Count : plural 1?the; other?{3_Count};} {5_Distance} {4_Source} {3_Count : plural 1?resource; other?resources;}.'   ),
        (   'en_US',    'LOC_CSC_ADJ_PREVIEW_NAMED_DISTRICT',   '{1_Amount} {2_Yield} from {3_Count : plural 1?the; other?{3_Count};} {5_Distance} {4_Source} {3_Count : plural 1?district; other?districts;}.'   ),
        (   'en_US',    'LOC_CSC_ADJ_PREVIEW_NAMED_TERRAIN',    '{1_Amount} {2_Yield} from {3_Count : plural 1?the; other?{3_Count};} {5_Distance} {4_Source} {3_Count : plural 1?terrain; other?terrains;}.'   ),
        (   'en_US',    'LOC_CSC_ADJ_DISTANCE_ADJACENT',        'adjacent'   ),
        (   'en_US',    'LOC_CSC_ADJ_DISTANCE_LOCAL',           'local'   ),
        (   'en_US',    'LOC_CSC_ADJ_DISTANCE_NEARBY',          'nearby'   ),
        (   'en_US',    'LOC_CSC_ADJ_SOURCE_GENERIC',           'matching object'   );
