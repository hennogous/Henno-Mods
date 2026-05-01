# Districts & Buildings: Art Guide

This chapter covers the art pipeline for getting custom 3D districts and buildings into Civ VI. If you've been doing database modding and want to now see your district actually rendered as a 3D hex on the map, rather than a placeholder or retextured vanilla asset, this is for you.

Fair warning — the art side of Civ VI modding is significantly more painful than the database side. The tooling is old, documentation is scarce, and Asset Editor has... opinions about how you should work. But it is doable, and the result of seeing your custom buildings appear on the hex grid is worth the suffering.

## Overview of What's Involved

To get a custom district or building rendering in-game, you need to wire up a chain of files from your 3D model all the way through to the game engine. The full chain looks like this:

```
3D Model (.blend)
  → CivNexus6 format (.cn6)
    → Granny 3D format (.fgx) + Geometry wrapper (.geo)
      → Asset file (.ast) — binds geometry + materials + textures
        → XLP package (.xlp) — names the asset for referencing
          → ArtDef files (.artdef) — tells the engine when/where to render it
            → Mod.Art.xml — declares everything to the game
              → ModBuddy Cook → .blp (binary package the engine loads)
```

Each step has its own file format, its own quirks, and its own ways of failing silently. We'll work through them from the bottom up — starting with what the game expects, then working back to your 3D model.

## ArtDef Mapping: Districts & Buildings

ArtDefs are XML files that define how the game engine maps your database types (like `DISTRICT_MY_DISTRICT`) to visual assets. For a district mod, you'll typically need entries in several ArtDef templates.

### The ArtDefs You Need

For a district with buildings, you'll be creating or modifying these ArtDef files:

| ArtDef Template | What It Does |
|----------------|--------------|
| `Districts` | The Xref — maps your `DistrictType` to a Landmarks entry and StrategicView states |
| `Buildings` | The Xref — maps your `BuildingType` to StrategicView states and attachment info |
| `Landmarks` | The big one — defines how the district looks in the 3D world view. Tilebases, attachments, era/culture variants |
| `StrategicView` | 2D sprites for the flat map view (three states per district/building: Completed, Pillaged, UnderConstruction) |
| `Icons` (UserInterfaceBLPs) | UI icons for Civilopedia and city panel |

### Districts.artdef

Each district entry needs three things:
1. A **Landmark** reference — cross-references your Landmarks.artdef entry for 3D placement
2. **StrategicView** entries — one per build state (Completed, Pillaged, UnderConstruction)
3. **Audio** — usually fine to leave empty for a first pass

The entry's `m_Name` **must exactly match** your `DistrictType` from your gameplay SQL. `DISTRICT_MY_DISTRICT` in the database means `DISTRICT_MY_DISTRICT` in the ArtDef. A misspelling here causes a silent rendering failure — no error, just no district.

### Buildings.artdef

Each building entry maps to StrategicView states, similar to districts. Key fields to know about:

| Field | What It Does |
|-------|-------------|
| `IsWonderBuilding` | Set `true` only for wonders |
| `UsesDistrictState` | Whether building appearance changes when district is pillaged |
| `AffectsDistrictBuildingSet` | Whether building changes the district's landmark appearance. This is what makes buildings appear/disappear on the hex as they're built |
| `AttachmentPointName` | The named slot in the district tilebase where this building attaches |

Again, `m_Name` must match `BuildingType` exactly.

### Landmarks.artdef

This is where things get serious. The Landmarks ArtDef is by far the most complex, and Firaxis' own documentation describes it as *"Abandon hope all ye who enter here"*. It contains the actual 3D asset references and all the logic for how districts visually evolve.

A district landmark entry has:

- **BaseVariants**: How the district looks at its base level, filtered by era and culture. Each variant references a TileBase entry in your XLP.
- **BuildingVariants**: How the district changes as buildings are constructed. Each building variant adds or replaces assets on the tilebase.

Each variant references an XLP entry like this:
```xml
<Element class="AssetObjects..BLPEntryValue">
    <m_EntryName text="_MyDistrict_Ancient_Base_01"/>
    <m_XLPClass text="TileBase"/>
    <m_XLPPath text="my_tilebases.xlp"/>
    <m_BLPPackage text="Landmarks/My_Tilebases"/>
    <m_LibraryName text="TileBase"/>
    <m_ParamName text="Asset"/>
</Element>
```

### The Xref System

The engine has a translation layer between your GameCore database types and ArtDef entries. If your database defines `DISTRICT_MY_DISTRICT` but there's no corresponding Districts.artdef entry, the asset won't render. You'll get a red data error internally, but nothing obvious in-game — it just won't appear. This "silent failure" pattern is the source of most art debugging pain.

## The 3D Model Pipeline: Blender → Game

Getting a 3D model from Blender into the game involves several conversion steps. Here's the pipeline:

### Step 1: Build in Blender

Your Blender model needs to follow specific conventions:

- **Armature**: Every model needs a single armature parent with at least one bone. Bone names must not contain `: / < > |` — these characters break the FGX format.
- **Mesh**: Single mesh object, parented to the armature via an Armature modifier. The game works with single-mesh objects; if you have multiple objects, join them first.
- **Vertex Groups**: Every single vertex must be assigned to at least one vertex group (bone). Unweighted vertices silently prevent `DefaultBurnMaterial` from working — your building won't show burn damage when pillaged, and the engine gives you zero feedback about why.
- **UV Maps**: You need exactly three UV layers:
  - UV1 = albedo/normal mapping
  - UV2 = lightmap
  - UV3 = tint mask
- **Materials**: Single material per mesh. The material name becomes the mesh group name in the resulting .geo file.
- **Pivot**: The top-level mesh pivot should be at 0,0,0. Any offset you want needs to be baked into the mesh geometry itself.

**Poly counts**: Think chunky toy models, not realistic architecture. Official Firaxis guidelines say *"simple, exaggerated, chunky — imagine them as toy models"*. A building typically sits around 300-600 triangles. The ratio should be 3 Big Shapes : 2 Intermediate Shapes : 1 Fine Detail. Only the big and intermediate shapes should affect the silhouette. Roof detail matters a lot because of the camera angle.

### Step 2: Export to CivNexus6 Format (.cn6)

The Blender-to-game path goes through CivNexus6, a community tool that converts between Blender and Firaxis' Granny 3D format. You export from Blender using the `io_export_cn6` addon to produce a `.cn6` file.

There's also a fully automated pipeline script (`csc_export_pipeline.ps1`) that handles the entire chain from `.blend` to `.fgx` + `.geo` headlessly, including:
- Validating and adding missing UV maps
- Fixing unweighted vertices
- Validating bone names for illegal characters
- Triangulating the mesh
- Calling CivNexus6's conversion internally

If you're doing this manually, the CivNexus6 GUI works fine — import your .cn6, set the vertex format to "No Bone Bindings, 3 UVs" (7 vertex fields: Position, Normal, Tangent, Binormal, UV0, UV1, UV2), and export as FGX.

### Step 3: FGX → GEO → Asset (.ast)

The `.fgx` file is the raw Granny 3D mesh. It needs a `.geo` wrapper (an XML file describing vertex/primitive counts, bones, mesh names, and geometry class). For buildings, the geometry class is `LandmarkModel`.

The `.ast` (asset) file is the central hub that binds everything together — geometry, materials, textures, behaviours, animations. It's an XML file that defines model instances with group states:

```xml
<m_ModelInstances>
  <Element>
    <m_Name text="MyBuilding"/>
    <m_GeoName text="MyBuilding"/>
    <m_GroupStates>
      <Element>
        <m_StateName text="Worked"/>
        <!-- Material, Visible=true, FOWMaterial, BurnMaterial, SnowMaterial -->
      </Element>
      <Element>
        <m_StateName text="Pillaged"/>
        <!-- Usually Visible=false for base, or separate PIL geometry -->
      </Element>
    </m_GroupStates>
  </Element>
</m_ModelInstances>
```

**Pillaged/Construction states**: The typical pattern is to create a separate geometry with roof sections removed (your "ruined" version). Add it as a second ModelInstance in the .ast. Set `Visible=true` only in the Pillaged state, with `BurnMaterial=DefaultBurnMaterial`. The intact base geometry gets `Visible=false` in the Pillaged state. Construction can share the pillaged geometry or have its own.

### Step 4: Materials and Textures

Materials use a PBR metalness workflow. For each building, you'll typically create:

| Texture | Class | Purpose |
|---------|-------|---------|
| `_B.dds` | `Generic_BaseColor` | Diffuse color (sRGB) |
| `_N.dds` | `Generic_Normal` | Normal map |
| `_AO.dds` | `Generic_AO` | Ambient occlusion (linear greyscale) |
| `_G.dds` | `Generic_Gloss` | Roughness — white=shiny, black=dull (linear) |
| `_M.dds` | `Generic_Metalness` | Metal mask (linear greyscale) |

Optional but useful:
- `Generic_Emissive` — lit windows at night
- `Generic_TintMask` — for tinting buildings per civilization (districts use this for culture colors)
- `Generic_LightMap` — pre-computed GI for buildings
- `Generic_BurnMap` — alternate base color for the burn effect

Each `.dds` file gets a `.tex` wrapper, and the `.tex` files are referenced by a `.mat` (material) file. The material class for buildings is `Landmark`.

**Tip**: Normal maps should be generated via a tool like Crazybump or Ndo from a simplified heightmap — never just desaturate your base color. Baked shadows in base color textures are viable and often look better than relying on real-time shadows at game camera distance.

## Asset Editor: The Necessary Evil

Asset Editor is Firaxis' tool for creating and managing `.ast`, `.mat`, `.tex`, `.geo`, and related files. You will use it. You will not enjoy it. But there's no real alternative for certain operations.

### What It Does Well
- Creating `.ast` files that wire together geometry, materials, and textures
- Previewing how your asset looks with proper materials in the viewport
- Setting up attachment points for tilebases
- Hot-loading changes into a running game (Asset Editor + game running → modify → save → Build → Hot Load)

### What It Does Badly
- **Startup time**: Slow. Very slow to load the asset cloud.
- **Cache management**: Assets created outside Asset Editor (e.g., via scripts) don't appear in the browser until registered in the dependency cache at `%APPDATA%\AssetCloud\mod-<ModName>-asset-deps.json`. This is a JSON file mapping mod-relative paths to their dependencies. If your scripted assets are invisible in AE, this is probably why.
- **Crash-prone**: Save often. AE crashes are not rare.
- **Undocumented UI**: Many operations require right-clicking in specific unmarked areas or knowing specific naming conventions.

### Creating Assets: The Basic Flow

1. **Geometry**: Import your `.geo`/`.fgx` into the mod's Geometries folder
2. **Textures**: Import `.dds` files, wrapped in `.tex` files, into the Textures folder
3. **Materials**: Create `.mat` files that reference your textures. Material class `Landmark` for buildings
4. **Asset**: Create `.ast` file. Set class to `TileBase` for districts, or leave as default for individual buildings. Wire geometry and materials via the group states

**Auto material matching**: If your material name matches a geometry triangle group name, the engine auto-assigns it. This saves a lot of manual wiring.

## TileBase Setup for Districts

A TileBase is the master asset for a district hex. It defines the base layout and all the attachment points where buildings, props, and effects get placed.

### Seven Elements of a District

Each district hex is composed of:

1. **Tilebases (TB)** — The base asset holding everything together, paired with a matching decal
2. **Attachments** — Individual props and features referenced by the tilebase. They have terrain following and culling properties
3. **Herobuildings (HB)** — The main gameplay buildings, part of the tilebase. These are what appear/disappear as you construct buildings in-game
4. **Decals** — Ground textures. A second geometry within an asset, parented to a `_decal` helper
5. **Obstruction Blockers (OBs)** — 2D shapes that prevent city buildings from spawning in the area, and curve roads around obstacles. Pivot centered to tilebase, `_OB` suffix
6. **Road Connection Points (RoadCP)** — Point helpers named `Road_CP(XX)`, Y+ aligned. Target one per hex edge for clean road connections
7. **FX Nodes** — Effect attachment points (smoke, fire, etc.). Prefer placing on attachments since they instance. Label `FX_(effecttype)`

### Decal Z-Layering

Decals at different "eras" need different Z offsets from the tilebase pivot to avoid z-fighting:

| Layer | Z Offset |
|-------|----------|
| Ancient decals | 6–10 units |
| Classical–Modern road decals | 11–15 units |
| Decals on top of road | 16–20 units |
| Burn/damage decals | 21–25 units |

### Attachment Naming

This is critical and has bitten many modders: **original attachment names are locked in the asset cloud database.** Copies on tilebases get numbers stripped — `PROP_Barrel023` becomes `PROP_Barrel` when the engine looks it up in the XLP. If you name something wrong initially, you may need to recreate the asset.

### Attachment Properties

| Property | What It Does |
|----------|-------------|
| `TerrainFollowMode` | `Pivot` (default), `Average`, `Maximum`, `None` — how the attachment follows terrain height |
| `CullMode` | `Optional` (default — removed by city buildings/roads/water), `Important` (only water culls), `Permanent` (never removed) |
| `ResourceType` | For assets specific to resource hexes |
| `RandomizeAnims` | Offset animations across repeated instances of the same attachment |

### Herobuilding States

Buildings typically have three visual states:
- **Worked** — normal appearance, full materials
- **PIL** (Pillaged) — damaged version, BurnMaterial applied, often shared geometry with CON
- **CON** (Construction) — under construction, can share PIL geometry to save memory

## XLP Packaging

XLP files (XML Library Packages) are the source-editable form of asset packages. They list named entries that map to your `.ast` files:

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects..XLP>
    <m_ClassName text="TileBase"/>
    <m_PackageName text="Landmarks/My_Tilebases"/>
    <m_Entries>
        <Element>
            <m_EntryID text="_MyDistrict_Ancient_Base_01"/>
            <m_ObjectName text="_MyDistrict_Ancient_Base_01"/>
        </Element>
    </m_Entries>
</AssetObjects..XLP>
```

- `m_ClassName`: The library type. `TileBase` for districts/buildings, `CityBuildings` for city filler, `StrategicView_Sprite` for 2D sprites, `UITexture` for icons
- `m_PackageName`: Path within the BLP structure
- `m_EntryID`: The name ArtDefs use to reference this entry
- `m_ObjectName`: The `.ast` filename on disk (without extension)

## The Cook Pipeline

Once all your files are in place, the build process goes:

1. **Mod.Art.xml** — Register your ArtDefs as art consumers and your XLPs as game libraries
2. **ModBuddy Build** — Compiles `.xlp` → `.blp` (binary packages), resolves dependencies, validates references
3. **Output** — Cooked assets land in the `Cooked/` folder

### Mod.Art.xml Structure

```xml
<AssetObjects::GameArtSpecification>
    <artConsumers>
        <Element>
            <consumerName text="Landmarks"/>
            <relativeArtDefPaths>
                <Element text="MyMod_Landmarks.artdef"/>
            </relativeArtDefPaths>
            <libraryDependencies>
                <Element text="TileBase"/>
                <Element text="CityBuildings"/>
            </libraryDependencies>
            <loadsLibraries>true</loadsLibraries>
        </Element>
    </artConsumers>
    <gameLibraries>
        <Element>
            <libraryName text="TileBase"/>
            <relativePackagePaths>
                <Element text="Landmarks/MyMod_Tilebases"/>
            </relativePackagePaths>
        </Element>
    </gameLibraries>
</AssetObjects::GameArtSpecification>
```

### Common Build Errors

| Error | Likely Cause |
|-------|-------------|
| Missing BLP entry | ArtDef references an XLP `m_EntryID` that doesn't exist |
| Missing library dependency | `Mod.Art.xml` consumer doesn't list a required library in `libraryDependencies` |
| Missing .ast file | XLP entry's `m_ObjectName` doesn't match any `.ast` file on disk |
| Texture format | Game expects `.dds` (DXT1/DXT5 compressed) wrapped in `.tex` files |
| Asset invisible in-game | Xref mismatch — database type name ≠ ArtDef entry name |
| No burn on pillage | Unweighted vertices in the mesh. Every vertex needs a bone assignment |

## Folder Structure

A well-organized mod keeps art files in a standard layout:

```
MyMod/
├── MyMod.Art.xml
├── ArtDefs/
│   ├── MyMod_Buildings.artdef
│   ├── MyMod_Districts.artdef
│   ├── MyMod_Landmarks.artdef
│   ├── MyMod_Icons.artdef
│   └── MyMod_StrategicView.artdef
├── XLPs/
│   ├── MyMod_Tilebases.xlp
│   ├── MyMod_Icons.xlp
│   └── MyMod_StrategicView.xlp
├── Assets/          (.ast files)
├── Geometries/      (.geo + .fgx files)
├── Materials/       (.mat files)
├── Textures/        (.tex + .dds files)
└── Cooked/          (ModBuddy Build output)
```

## Common Gotchas

Here's the collected wisdom of many hours of debugging, arranged as a checklist for when things aren't working:

### Nothing renders at all
- [ ] Does your database type name **exactly** match the ArtDef entry name? Case-sensitive.
- [ ] Did you add the ArtDef to the correct art consumer in `Mod.Art.xml`?
- [ ] Did you add the XLP to a game library in `Mod.Art.xml`?
- [ ] Is the library dependency listed in the art consumer?
- [ ] Did you actually cook/build? Check that `Cooked/` has `.blp` files.

### Model loads but looks wrong
- [ ] Check UV mapping — wrong UV channel assignments cause stretching or missing textures
- [ ] Check material class — should be `Landmark` for buildings
- [ ] Check texture class — `Generic_BaseColor` not `UserInterface`, etc.
- [ ] AO map: can be set at asset level instead of per-material for multi-object assets

### Pillage doesn't show burn effect
- [ ] **Unweighted vertices** — the number one cause. Every vertex must have a bone assignment.
- [ ] Is `DefaultBurnMaterial` actually assigned in the .ast group state?

### Asset invisible in Asset Editor browser
- [ ] Check `%APPDATA%\AssetCloud\mod-<ModName>-asset-deps.json` — assets created outside AE need entries here

### Strategic view missing
- [ ] Each building/district needs three StrategicView entries: Completed, Pillaged, UnderConstruction
- [ ] For districts, set Render=false for Wonder and CityCenter entries

### Hot loading not working
- [ ] Asset Editor must be open alongside the game
- [ ] Modify → Save → Build solution → Hit Hot Load button
- [ ] Some changes (ArtDef structure) require a full game restart
- [ ] `artdef reload Units` works from the debug console, but district ArtDefs may not hot-reload as cleanly

## Dynamic Art: GamePropertyRanges

For more advanced mods, you can have buildings change their appearance based on gameplay state. The pipeline:

1. **Lua** sets a city property: `pCity:SetProperty("key", value)`
2. **GamePropertyRanges.artdef** maps value ranges to named intervals
3. **Landmarks.artdef** uses `[CITYPROP:INTERVAL_NAME]` in its SelectionRule to pick different asset variants
4. Higher Priority values override lower when multiple rules match

This lets you do things like "show boats at the building when adjacent to a harbor" or "upgrade the building appearance based on adjacency bonuses". Sukritact's Oson (Akan) mod is the reference implementation for this pattern.

## What's Next

This guide covers the conceptual pipeline and file relationships. For step-by-step tutorials with screenshots, the Firaxis documentation (available via Steam's "Sid Meier's Civilization VI Development Tools") covers Asset Editor operations in detail. An online mirror is hosted [here](https://htmlpreview.github.io/?https://github.com/wildweegee101/Civ-6-Documentation/blob/main/Civ6Docs.html).

For strategic view sprites, icons, and 2D art, those are significantly simpler — just textures in the right format at the right sizes, referenced by the right ArtDef entries. The 3D pipeline is where all the real complexity lives.

And remember Slothoth's call in the Preamble — if you've figured out the Landmarks system and this guide helped you get started, consider contributing back. The art side is the least documented part of Civ VI modding, and every worked example helps the next person.
