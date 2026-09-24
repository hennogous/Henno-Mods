# Wonder-hosted Service exact-placement spike

This is an isolated, loadable Civ VI test mod for the Fashion House Stage Manager
hosting question. It does **not** edit CSC production content or the blocked Tailors
Stage 4 contract.

## Confirmed engine behavior

The first two versions established:

1. A hidden building with `PrereqDistrict = DISTRICT_WONDER` can exist on a Wonder
   tile and can be exposed coherently in City Breakdown and plot tooltips.
2. Wonder districts do not expose Citizen assignment, so a Wonder-hosted Service
   cannot provide a usable specialist slot.
3. SQL grant modifiers do not retain the granting Wonder's instance. Every granted
   building whose prerequisite is `DISTRICT_WONDER` is placed in the city's first
   existing Wonder district, even when each host grants a distinct building type.

The multi-Wonder test proved point 3 in both directions:

- Ottawa: Oracle `@833`; Oracle Service `@833`; Broadway `@760`; Broadway Service
  incorrectly `@833`.
- Cairo: Broadway `@2305`; later Bolshoi and Oracle Services also incorrectly
  `@2305`.

The UI displayed these actual stored locations and correctly marked the misplaced
variants `WRONG WONDER`; it did not cause the failure.

## Exact-placement hypothesis

Version 3 removes all SQL grant modifiers. A gameplay reconciler now uses:

```lua
city:GetBuildQueue():CreateBuilding(serviceIndex, wonderPlotIndex)
```

The second argument is the exact host Wonder plot. The reconciler runs during
initialization, load completion, Wonder completion, building-added events, and
player-turn activation.

For each host/Service pair it:

1. Finds the host Wonder's stored plot.
2. Keeps an already co-located Service unchanged.
3. Removes a misplaced v2 Service and recreates it on the host plot.
4. Creates a missing Service on the host plot.
5. Removes a laboratory Service whose host no longer exists.
6. Logs the resulting real location under `[CSC WSHS]`.

## Internal variants

| Host Wonder | Internal Service building |
|---|---|
| Oracle (laboratory only) | `BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE` |
| Bolshoi Theatre | `BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BOLSHOI` |
| Broadway | `BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BROADWAY` |
| Sydney Opera House | `BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_SYDNEY` |

All four retain `PrereqDistrict = DISTRICT_WONDER`, share the same visible name and
icon, and have no Citizen slot. Oracle remains a laboratory-only trigger and must
not be copied into the production Fashion House implementation.

## Critical test

1. Fully restart Civ VI after installing version 3; both gameplay data and the
   `.modinfo` changed.
2. Load the existing Oracle/Broadway disposable save. The reconciler should remove
   the misplaced Broadway variant from Oracle and recreate it on Broadway.
3. Search `Lua.log` for `[CSC WSHS]`. The desired entries are:
   - Oracle: `action=KEEP ... result=COLOCATED`
   - Broadway: `action=RELOCATE_EXPLICIT ... result=COLOCATED`
4. Open City Details -> City Breakdown. One Stage Manager should appear beneath
   Oracle and one beneath Broadway, with no `WRONG WONDER` row.
5. Hover both Wonder tiles. Each actual building list should contain one Stage
   Manager.
6. End a turn, then save/reload. Both locations should remain stable and later
   reconciliations should report `action=KEEP`.
7. Optionally repeat with Bolshoi Theatre and Sydney Opera House in the same city.

## Interpreting the result

- **Explicit creation yields `COLOCATED`:** the robust production architecture is
  distinct internal Service types plus a deterministic gameplay placement bridge.
- **`RECONCILE_ERROR`:** inspect the logged error; the exposed creation signature
  may differ in this gameplay context.
- **Creation succeeds but still reports `MISMATCH`:** the engine ignores the plot
  argument for ordinary non-Wonder buildings. Retain a conventional district host
  rather than spoofing false Wonder locations in the UI.

## Installation

Copy this directory into the user Civ VI `Mods` directory under a unique folder
name, fully restart Civ VI so `Mods.sqlite` is refreshed, and enable **CSC Lab:
Wonder-hosted Service**. Remove it after testing; it affects saved games.
