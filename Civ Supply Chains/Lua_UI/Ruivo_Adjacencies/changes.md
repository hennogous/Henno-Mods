# CSC ↔ MAB Integration Notes

_Last updated: 2026-04-17. See git log for full history._

## Current State

As of April 2026, CSC's footprint in MAB is minimal. The large Lua overrides were removed in `c907090` after the features were contributed upstream to MAB (`feature/ring-bands-must-own`).

### Files CSC loads from this folder

| File | Purpose |
|---|---|
| `CSC_MAB_DB.sql` | Registers CSC resource classes and DISTRICT_COMMERCIAL_HUB in `Ruivo_CAO` so MAB tooltips show readable names |
| `CSC_MAB_Text.sql` | Localization strings for those CAO names |

### Current CSC_MAB_DB.sql (what it does)

```sql
INSERT OR IGNORE INTO Ruivo_CAO (CustomAdjacentObject, Name, ArtdefOverlayEntry) VALUES
    ('CLASS_CSC_BAKERS_BASE',   'LOC_CLASS_CSC_BAKERS_BASE_NAME',   'CSC_BAKERS_Base_Materials'),
    ('CLASS_CSC_BAKERS_SPEC',   'LOC_CLASS_CSC_BAKERS_SPEC_NAME',   'CSC_BAKERS_Spec_Materials'),
    ('DISTRICT_COMMERCIAL_HUB', 'LOC_CSC_SALES_DISTRICT_COMMERCIAL_HUB_NAME', 'CSC_Sales');
```

As each Quarter is added, its `CLASS_CSC_[Q]_BASE` and `CLASS_CSC_[Q]_SPEC` entries go here.

---

## MAB Dependency

CSC requires MAB to include the `feature/ring-bands-must-own` features:

- `MinRings` column on `Ruivo_New_Adjacency` (ring-band targeting: "tiles between ring X and ring Y")
- `MustOwn` resource ownership filter (only counts resources the player owns)
- Ring integrity fix (`UPDATE ... SET Rings = MinRings WHERE MinRings > Rings`)
- Tooltip descriptors: `LOC_RUIVO_RING_*`, `LOC_ZEGA_ADJACENCY_*`
- `FROM_RINGS_SPECIFIC_WONDER` adjacency type

These used to live in CSC as Lua overrides and `CSC_MAB_DB_RingFix.sql`. They don't anymore.

**If MAB hasn't merged that PR yet**, CSC breaks silently — adjacency bonuses that use `MinRings` will calculate incorrectly and ring-range tooltips won't display.

---

## Key Gotcha: MinRings=0 means "the placement tile"

In `CSC_Q_BAKERS.sql`, the Wind Mill hills adjacency rule uses `MinRings=0`:

```sql
-- Wind Mill: +1 Production per hills tile in ring 0 (i.e. the placement tile itself)
MinRings = 0, Rings = 0
```

Ring 0 = the district's own tile. Without `MinRings=0` explicitly set, it defaults to 1, which makes the tooltip show "nearby" instead of "local". Fixed in `e7b7ad1`.

When writing new adjacency rules: if the rule is about the placement tile itself, set both `MinRings=0` and `Rings=0`.

---

## Re-patching MAB on Updates

When Ruivo releases a new version of MAB, run `patch_mab.py` to re-apply CSC's additions:

```bash
# Dry run first:
python patch_mab.py --dry-run

# Then apply:
python patch_mab.py
```

The script patches `RUIVO_STAT_MODULE_GP.lua` and `NEW_ADJACENCY_BONUS_BY_RUIVO_GP.lua` in the Steam workshop folder. `.bak` files in this folder are backups from the last run — not loaded by the game.

If `feature/ring-bands-must-own` has been merged into the MAB release, most patches will already be present and the script will skip them.

---

## History

| Commit | Date | What changed |
|---|---|---|
| `e7b7ad1` | 2026-04-14 | Set `MinRings=0` on Wind Mill hills rule so tooltip shows "local" |
| `c907090` | 2026-04-12 | Removed CSC's Lua overrides; `MinRings`/`MustOwn` now live in upstream MAB |
| `259de18` | 2026-01 | Big update — MAB integration with full Lua overrides in CSC |
| `3c3f972` | 2025-09 | Initial Ruivo/MAB integration |
