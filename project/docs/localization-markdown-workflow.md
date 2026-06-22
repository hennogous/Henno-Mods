# Localization Markdown Workflow

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
