# Ruivo Adjacency Processor

`Civ Supply Chains/Lua_UI/Ruivo_Adjacencies/CSC_Ruivo_AdjacencyProcessor.sql` is the late SQL processor that turns CSC semantic tags into Modular Adjacency Bonuses rows.

The intended split is:

- Quarter SQL and ModSupport SQL **tag resources, terrain/features, and districts**.
- Quarter SQL declares material adjacency rules in `CSC_QuarterMaterialAdjacencyConfig`.
- The processor reads those declarations and emits `Ruivo_New_Adjacency` / `Ruivo_CAO` rows after tags have loaded.

This keeps Quarter files mostly declarative and avoids repeating Ruivo boilerplate in every Quarter.

## Load Order

The processor must run after all tag producers:

- `CSC_Q_ALL.sql` creates shared config tables.
- Quarter and ModSupport SQL files insert `Tags`, `TypeTags`, and material config rows.
- `CSC_Ruivo_AdjacencyProcessor.sql` runs late and generates Ruivo/MAB rows.

Current project wiring uses `LoadOrder=3000` for the processor.

## Material adjacency config

Material adjacency behavior is declared in `CSC_QuarterMaterialAdjacencyConfig`:

```sql
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
```

Example:

```sql
INSERT OR IGNORE INTO CSC_QuarterMaterialAdjacencyConfig
    (QuarterKey, SourceTag, SourceFilter, YieldType, YieldChange, AdjacencyType)
VALUES
    ('BAKERS', 'CLASS_CSC_BAKERS_BASE', '', 'YIELD_PRODUCTION', 1, 'FROM_RINGS_TYPETAG_RESOURCE'),
    ('BAKERS', 'CLASS_CSC_BAKERS_SPEC', '', 'YIELD_PRODUCTION', 1, 'FROM_RINGS_TYPETAG_RESOURCE');
```

`SourceFilter` filters the tagged object type before generating a row:

| Filter | Typical `AdjacencyType` |
|---|---|
| `''` | Use all objects tagged with `SourceTag` |
| `RESOURCE_%` | `FROM_RINGS_CAO_RESOURCE` |
| `FEATURE_%` | `FROM_RINGS_CAO_FEATURE` |
| `TERRAIN_%` | `FROM_RINGS_CAO_TERRAIN` |

Bakers currently uses `FROM_RINGS_TYPETAG_RESOURCE`, which passes the class tag itself to MAB so ModSupport resources inherit automatically. Future Quarters can use either typetag mode or CAO-by-object rows depending on their object mix.

## District-facing tag grammar

The processor recognizes these district-facing tag shapes:

| Tag shape | Meaning |
|---|---|
| `CLASS_CSC_<QUARTER>_SALES` | Adjacent tagged district gives `+1 Gold` to the Quarter. |
| `CLASS_CSC_<QUARTER>_INCOMING_GOODS` | Adjacent tagged district gives `+1 Production` to the Quarter. |
| `CLASS_CSC_<QUARTER>_<SOURCE>_TO_QUARTER_<YIELD>` | Adjacent tagged district gives `+1 <YIELD>` to the Quarter. |
| `CLASS_CSC_<QUARTER>_SALES_<YIELD>` | Tagged customer district receives `+1 <YIELD>` from adjacent Quarter. |

Examples:

```sql
('DISTRICT_CITY_CENTER', 'CLASS_CSC_BAKERS_SALES')
('DISTRICT_CITY_CENTER', 'CLASS_CSC_BAKERS_SALES_FOOD')
('DISTRICT_RURALCOMMUNITYA', 'CLASS_CSC_BAKERS_INCOMING_GOODS')
('DISTRICT_MARKET', 'CLASS_CSC_BAKERS_MARKET_TO_QUARTER_CULTURE')
```

The `<QUARTER>` token assumes the existing CSC quarter keys without underscores: `BAKERS`, `TAILORS`, `APOTHECARIES`, `STONEMASONS`, `CARPENTERS`, `BLACKSMITHS`, `GOLDSMITHS`, `BREWERS`.

## Unique replacement districts

Before generating district-facing adjacencies, the processor propagates CSC district-facing tags from base districts to unique replacement districts via `DistrictReplaces`.

This applies only to district-facing tags:

- `_SALES`
- `_SALES_<YIELD>`
- `_INCOMING_GOODS`
- `_TO_QUARTER_<YIELD>`

Do not use this propagation for material/resource/feature/terrain tags; those are controlled by `CSC_QuarterMaterialAdjacencyConfig`.

## Adding a new Quarter relationship

1. Register the needed `Tags` in the Quarter or ModSupport SQL file.
2. Add `TypeTags` for participating resources, features, terrain, or districts.
3. For material inputs, add rows to `CSC_QuarterMaterialAdjacencyConfig` in the Quarter file.
4. For district/customer relationships, use the tag grammar above and let the processor generate Ruivo rows.
5. If a new tag shape is needed, update this document and the processor together.
