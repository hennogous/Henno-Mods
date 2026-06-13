# CSC Changes to the Ruivo/MAB Mod

**MAB local repo:** `C:\Users\Shadow\Documents\My Games\Sid Meier's Civilization VI\Mods\NEW_ADJACENCY_BONUS_BY_RUIVO`  
**Fork remote:** `fork` (Henno's GitHub fork — PRs submitted there)  
**Currently running:** local `test/all-features` branch (all features merged, plus current CSC-only integration commits)

_Last updated: 2026-06-13_

---

## Branch Structure

```
main                  ← upstream Ruivo (no CSC changes)
  ├── feature/ring-bands          ← MinRings/MaxRings support
  ├── feature/must-own            ← MustOwn ownership filter
  ├── feature/adjacent-edge-icons ← tile-edge icons during placement
  ├── feature/negative-adjacency  ← negative yield support
  ├── origin/pr_combined_5        ← upstream combined PR branch containing all four features + Ruivo optimization commit
  └── test/all-features           ← local integration branch used by CSC; currently has four extra local commits
```

Each feature branch has a matching `fork/` remote for the PR.

As of 2026-06-13, local `test/all-features` is clean and contains all four feature branch tips. It also has four newer commits that are **not** on `fork/test/all-features` and are not on any named `feature/*` branch yet:

- `63734e7` Add district typetag adjacency support
- `3d2c744` Preserve adjacency clone options for unique districts
- `6769da8` Preserve district modifier flag for unique adjacencies
- `fead90f` Fix signs in district adjacency tooltip text

Those four commits cherry-pick cleanly onto `origin/pr_combined_5`, but not directly onto `origin/main` without resolving conflicts in `UI/Common/AdjacencyBonusSupport.lua`. If submitting them as another PR before Ruivo merges the combined branch, create a stacked branch based on `origin/pr_combined_5` or a branch whose PR explicitly targets the combined PR branch. If the combined branch lands first, rebase/cherry-pick the four-commit slice onto the updated `main` and submit normally.

---

## Feature Branches

### `feature/ring-bands` (3 commits)

**What it does:** Adds `MinRings` and `MaxRings` columns to `Ruivo_New_Adjacency`, enabling ring-band targeting — "only count resources between ring 2 and ring 4", for example.

**Key commits:**
- `dbaf81e` feat: add MinRings/MaxRings ring-band support and distance-based localization
- `24b2205` fix: treat MaxRings==0 as local regardless of MinRings
- `c15869b` fix: show "the" instead of "1" in adjacency tooltips when count is 1

**Schema addition:**
```sql
ALTER TABLE Ruivo_New_Adjacency ADD COLUMN MinRings INTEGER NOT NULL DEFAULT 1;
-- (MaxRings is the existing Rings column, renamed conceptually)
```

**Tooltip strings added:** `LOC_RUIVO_RING_0`, `LOC_RUIVO_RING_SPECIFIC`, `LOC_RUIVO_RING_MIN_MAX`, `LOC_RUIVO_RING_MAX`, `LOC_ZEGA_ADJACENCY_LOCAL/ADJACENT/NEARBY`

**CSC usage:** Every Bakers' Quarter adjacency rule that needs ring-band targeting uses `MinRings`. The Wind Mill hills rule uses `MinRings=0` to mean "the placement tile itself" — without it, defaults to 1 and tooltip says "nearby" instead of "local" (bug fixed in CSC `e7b7ad1`).

---

### `feature/must-own` (2 commits)

**What it does:** Adds a `MustOwn` boolean column. When set, resource adjacency checks only count resources owned by the city's player — not unowned or enemy-owned tiles in range.

**Key commits:**
- `35dfcb3` feat: add MustOwn column for opt-in plot ownership filtering
- `6cf240c` fix: pass row.MustOwn to StatsModule_For_UI in RUIVO_MODULAR_UI.lua

**Schema addition:**
```sql
ALTER TABLE Ruivo_New_Adjacency ADD COLUMN MustOwn BOOLEAN NOT NULL DEFAULT 0;
```

**CSC usage:** All Bakers' Quarter resource adjacency rules use `MustOwn=1` — the supply chain only benefits from resources the player controls.

---

### `feature/adjacent-edge-icons` (many commits, includes ring-bands + must-own)

**What it does:** Shows tile-edge highlight icons during district placement, indicating which adjacent tiles are contributing to the adjacency bonus (same visual style as vanilla city adjacency highlights).

**Key capabilities:**
- `ArtdefOverlayEntry` column on `Ruivo_CAO` — per-class icon override so different Quarters using the same district type show different icons
- `ArtdefOverlayEntry` on `Ruivo_AdjacencyType` — fallback icon for non-CAO types
- Fixes: river icon deduplication, directional river edge mapping, hidden undiscovered resource icons, MustOwn respect in icon rendering, Rings=0 preservation

**CSC usage:** The `ArtdefOverlayEntry` column in `Ruivo_CAO` is why `CSC_MAB_DB.sql` populates that field — each Quarter gets its own visual overlay on placed tiles.

---

### `feature/negative-adjacency` (4 commits)

**What it does:** Supports negative `YieldChange` values — adjacency penalties rather than bonuses.

**Key commits:**
- `1dedbee` feat: support negative YieldChange values end-to-end
- `1f95b20` fix: generate negative Amount for binary modifiers when YieldChange < 0
- `804d4e4` fix: display sign correctly for negative adjacency tooltip values
- `08d6601` feat: show ICON_PressureDown for negative loyalty adjacency

**CSC usage:** Not currently used by Bakers' Quarter, but available for future Quarters that impose penalties.

---

### `test/all-features` (current working branch)

All four features merged. This is the branch installed in the Mods folder and loaded by Civ 6 during CSC development. Not intended for submission to workshop — it's a local integration test branch.

---

## What Has NOT Been Changed

The core MAB architecture is untouched:
- `Ruivo_New_Adjacency` table structure (aside from the new columns)
- The dispatch table / `RuivoAdjacencyDispatch`
- Binary-folding property system
- Modifier generation pipeline
- All existing adjacency types

---

## Submitting PRs to Ruivo

PRs go to Ruivo's workshop repo via Henno's fork. Each feature branch maps to one PR. The `test/all-features` branch is local only.

When Ruivo merges and releases a new workshop version:
1. Pull `origin/main` into local `main`
2. Rebase feature branches if needed
3. Run `patch_mab.py --dry-run` in the CSC repo to verify the CSC SQL patches still apply cleanly
4. Update CSC's `Lua_UI/Ruivo_Adjacencies/changes.md` if anything changed
