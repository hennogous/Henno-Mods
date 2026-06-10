-- CSC_Q_SETUP
-- Author: Shadow
-- DateCreated: 2026-06-10 16:57:32
--------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Vocabularies
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Vocabularies

		(    Vocabulary			)
VALUES	(	'DISTRICT_CLASS'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC processor config tables
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Quarter files declare how their material TypeTags become Ruivo/MAB adjacency rows.
-- CSC_Ruivo_AdjacencyProcessor.sql consumes this table after Quarter and ModSupport files have loaded.
CREATE TABLE IF NOT EXISTS CSC_QuarterMaterialAdjacencyConfig
    (
    QuarterKey      TEXT NOT NULL,
    SourceTag       TEXT NOT NULL,
    SourceFilter    TEXT NOT NULL DEFAULT '',
    YieldType       TEXT NOT NULL DEFAULT 'YIELD_PRODUCTION',
    YieldChange     REAL NOT NULL DEFAULT 1,
    AdjacencyType   TEXT NOT NULL,
    PRIMARY KEY
        (
        QuarterKey,
        SourceTag,
        SourceFilter,
        YieldType,
        AdjacencyType
        )
    );
