# Stage 3 precision baseline

16 November2026. This records the existing working-tree gameplay implementation
that Henno had QAed before the building-transaction catalogue migration.

Stage 3 customer demand uses0.101 per customer citizen. Lua sums each receiving
city/property target, converts it to a per-citizen rate rounded upward to1/256,
and caps the stored rate at32767. Fifteen bit consumers use exact binary fractions;
Stage4 retains its whole-number twenty-bit range. Amount properties have a Q8
suffix to distinguish them from the earlier decimal-bit encoding. The next
synchronized refresh initializes the new properties in saved worlds.

This replaces the previous committed0.105/decimal-bit implementation. It was
already present in the gameplay code when the population migration began;
the migration preserves this baseline rather than introducing a further rate
or rounding change.

The separate baseline commit preserves the exact pre-migration Lua/Quarter SQL
for review and repeatable regression. The migration's288 property-world fixtures,
selected native graph hashes and67-city zero-turn native comparison use that
source. See [the migration and manual QA report](../research/mods/csc-population-transaction-catalogue-20261116.md).
