# Localization Markdown Workflow

> **Documentation audit — 2026-09-12: Current.** Source folder, loc_md_to_sql.py and Markdown-to-SQL ownership match the repository. This audit checked the local workflow, not a new localization build or in-game rendering.
> Classification: Tool workflow. See the [full audit](../DOCUMENT-AUDIT.md).

Long Civ VI localization strings can be authored in Markdown and generated into SQL with `project/tools/localization/loc_md_to_sql.py`.

The generated SQL is still normal Civ VI `UpdateText` SQL. Inline icons such as `[ICON_Food]`, localization references such as `{LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME}`, and positional placeholders such as `{1_num : plural 1?Hub; other?Hubs;}` are preserved literally.

## Commands

Generate all sources under `project/localization/`:

```powershell
py -3 project\tools\localization\loc_md_to_sql.py
```

Check whether generated files are current:

```powershell
py -3 project\tools\localization\loc_md_to_sql.py --check
```

Preview one source without writing:

```powershell
py -3 project\tools\localization\loc_md_to_sql.py project\localization\examples\CSC_MC_MODE_TEXT.md --stdout
```

## Source Format

Each Markdown file has top-level metadata:

```markdown
# File Title
output: Civ Supply Chains/Text/CSC_MC_MODE_TEXT.sql
language: en_US
```

Each `##` heading is one localization entry. A heading that starts with `LOC_` is used as the tag unless `tag:` or `tags:` is supplied.

```markdown
## LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION
mode: update

- First effect line with [ICON_Food] and {LOC_SOMETHING}.
- Second effect line.

Paragraph after a blank line.
```

Generation rules:

- `mode: upsert` emits `INSERT OR REPLACE INTO LocalizedText`; this is the default.
- `mode: update` emits `UPDATE LocalizedText`.
- `mode: raw` passes a fenced SQL block through unchanged; use it for dynamic SQL, pedia table setup, or legacy statements that are not plain localization rows.
- `tags: A, B` emits one update with `WHERE Tag IN ('A', 'B')`.
- `where:` can be used for a custom `WHERE` clause when tag matching is not enough.
- `text-prefix:` and `text-suffix:` can preserve intentional leading/trailing tokens such as `[NEWLINE][NEWLINE]`.
- Consecutive Markdown bullet items become single `[NEWLINE]`-separated lines.
- Blank lines between blocks become `[NEWLINE][NEWLINE]`.
- Wrapped prose lines inside a paragraph are joined with spaces.
- A line ending in `\` forces a single `[NEWLINE]`.
- SQL single quotes are escaped automatically, so write normal text like `Bakers' Quarter`.

Raw SQL entries look like this:

````markdown
## Dynamic resource pedia rows
mode: raw

```sql
INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US', 'LOC_EXAMPLE', SomeGeneratedText
FROM SomeConfigTable;
```
````

## Migration Pattern

For existing loaded files, migrate one file at a time:

1. Create a matching source under `project/localization/`.
2. Set `output:` to the real loaded SQL path, for example `Civ Supply Chains/Text/CSC_MC_MODE_TEXT.sql`.
3. Run the generator.
4. Review the SQL diff. It should only change formatting and quote escaping unless the source text changed.
5. Run `py -3 project\tools\localization\loc_md_to_sql.py --check` before committing generated SQL.

The example at `project/localization/examples/CSC_MC_MODE_TEXT.md` writes only to `project/localization/examples/generated/` and is not loaded by ModBuddy.


## Relationship icons and MCUIS service labels

Henno's 15 October 2026 correction applies across Quarters and compatibility text:
every visible reference to Base Materials, Specialty Materials, Sales Districts
or Goods Providers carries its matching category icon immediately before the
term. This includes singular/plural and lowercase references, reverse resource-role
labels, descriptions, narrative prose and lens labels. Native Civilopedia chapter
headings stay plain and must never contain texticons. Shared-noun references use both icons, for example
`[ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials`.
Resource role labels inside chapter body text keep their category icons; they
are not native chapter headings.

MCUIS effect labels use the canonical service name without a host suffix:
Ballet Dancer, Musical Actor and Opera Singer. Notification labels follow the
same rule. The separate Preview Supply Chain line still identifies the customer
Wonder, and service descriptions/Civilopedia prose may explain the location.
Venue-specific ability keys, icons and service objects remain distinct.

`loc_md_to_sql.py` rejects missing/wrong category icons and venue-qualified MCUIS
service labels before writing generated text. Raw SQL display literals are also
checked; SQL comments and INSTR search needles are not display text. The shared
localization pattern catalog records both rules, and Tailors phase assertions
verify decorated resource groups, plain chapter headings and generated MCUIS label prefixes.
Regression coverage lives in `test_localization_editorial_rules.py`; the tests
also exercise comments/search predicates, raw display strings, shared material
nouns and all three Wonder service notification families.
