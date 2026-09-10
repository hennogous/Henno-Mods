# CSC_TAILORS_MC_MODE_TEXT
output: Civ Supply Chains/Text/CSC_TAILORS_MC_MODE_TEXT.sql
language: en_US

## Textile Workshop Monopolies & Corporations line
mode: raw

```sql
UPDATE LocalizedText
SET Text = REPLACE(
    Text,
    '+1 [ICON_Culture] Culture from each adjacent [ICON_CSC_BASE] Base Materials improvement, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.',
    '+1 [ICON_Culture] Culture from each adjacent [ICON_CSC_BASE] Base Materials improvement, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.[NEWLINE]+2 [ICON_Culture] Culture, [ICON_Production] Production and [ICON_Gold] Gold from an Industry, and +3 [ICON_Culture] Culture, [ICON_Production] Production and [ICON_Gold] Gold from a Corporation.'
)
WHERE Tag = 'LOC_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_DESCRIPTION';
```
