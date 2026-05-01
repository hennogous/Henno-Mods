# Civ 6 Building Geometry Catalogue — Complete Edition

> Generated 2026-03-30 from SDK pantry analysis of ALL district geometry files.
> Covers base game + Rise & Fall + Gathering Storm.
> Stats from .geo XML metadata + Blender mesh inspection of 34 key assets via CN6.
> For modelling patterns, see [building-geometry-patterns.md](building-geometry-patterns.md).

## How to Read This

- **v** = vertex count, **t** = triangle count, **m** = mesh objects, **b** = bones
- **i** = mesh islands (disconnected pieces) — from Blender analysis where available
- **bbox** = bounding box [X × Y × Z] in game units
- **UV1%** = UV1 space utilisation (percentage of 0-1 UV space occupied)
- PIL/CON = Pillaged/Construction variant exists
- ⭐ = deep mesh inspection performed (CN6 + Blender)

---

## City Center (DIS_CTY)

City Center buildings share a hex with the Palace. They're composited into TileBase variants.
The Granary is the only multi-era City Center building with standalone geometry.

### Core Buildings

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| ⭐ **Granary (Ancient)** | `DIS_CTY_Granary_AN` | 2,868 | 1,624 | 5 | 7 | ✓ | ✓ | 526 islands, bbox [185×145×108], UV1 2.1% |
| ⭐ **Granary (Renaissance)** | `DIS_CTY_Granary_RE` | 3,036 | 1,724 | 6 | 8 | ✓ | ✓ | 578 islands, bbox [212×166×141], UV1 4.6% |
| ⭐ **Granary (Modern)** | `DIS_CTY_Granary_MD` | 4,022 | 2,170 | 7 | 9 | ✓ | ✓ | 862 islands, bbox [212×179×157], UV1 4.2% |
| **Monument (Ancient)** | `DIS_CTY_ANC_Monument` | 1,713 | 1,197 | 10 | 7 | ✓ | ✓ | Obelisk + base |
| **Monument (Asian)** | `DIS_CTY_Monument_Asian` | 1,952 | 1,166 | 6 | 2 | ✓ | ✓ | Culture variant |
| **Monument (Rome)** | `DIS_CTY_ROME_Monument` | — | — | — | — | ✓ | ✓ | Roman unique |
| **Monument (S. America)** | `DIS_CTY_RSA_Monument` | — | — | — | — | ✓ | ✓ | Culture variant |
| **Monument (Mughal)** | `DIS_CTY_RMUG_Monument` | — | — | — | — | — | — | Culture variant |
| **Water Mill (Ancient)** | `DIS_CTY_Watermill_AN` | — | — | — | — | — | — | |
| **Water Mill (Modern)** | `DIS_CTY_Watermill_MD` | — | — | — | — | — | — | |

### Granary Era Progression (Deep Analysis)

| Era | Verts | Tris | Islands | BBox Z | UV1% | Delta from AN |
|-----|------:|-----:|--------:|-------:|-----:|--------------:|
| Ancient | 2,868 | 1,624 | 526 | 108 | 2.1% | — |
| Renaissance | 3,036 | 1,724 | 578 | 141 | 4.6% | +6% verts |
| Modern | 4,022 | 2,170 | 862 | 157 | 4.2% | +40% verts |

**Observation:** Modern era adds ~40% more vertices but ~64% more islands — the complexity increase comes from adding more small detail pieces (pipes, railings, machinery), not making existing pieces denser.

### Palace Variants (by culture)

All palaces are in the City Center. Each civilization set has its own palace mesh.

| Culture Code | Culture Set | Example Civs |
|---|---|---|
| AB | Asian B (East Asian) | China, Japan |
| AE | Asian E (South Asian) | India, Khmer |
| AW | Asian W (Middle Eastern) | Arabia, Persia |
| MG | Medieval Generic | Default European |
| MGG | Medieval Generic Gothic | |
| RC | Renaissance Classical | Greece, Rome |
| RE | Renaissance European | England, France, Spain |
| RBAL | Renaissance Baltic | Poland, Lithuania |
| RBRZ | Renaissance Brazilian | Brazil |
| RENG | Renaissance English | England unique |
| RGER | Renaissance German | Germany unique |
| RIND | Renaissance Indonesian | Indonesia |
| RJ | Renaissance Japanese | Japan |
| RKOR | Renaissance Korean | Korea (DLC) |
| RMAL | Renaissance Malian | Mali (DLC) |
| RMAO | Renaissance Maori | Maori (DLC) |
| RMAP | Renaissance Mapuche | Mapuche (DLC) |
| RMED | Renaissance Mediterranean | |
| RMUG | Renaissance Mughal | India |
| RNA | Renaissance Native American | |
| RNWY | Renaissance Norwegian | Norway |
| RSA | Renaissance South American | Aztec, Inca |
| RSCT | Renaissance Scottish | Scotland (DLC) |
| RSPN | Renaissance Spanish | Spain |
| RSS | Renaissance South/Southeast | |
| RSUM | Renaissance Sumerian | Sumeria |
| RSWD | Renaissance Swedish | Sweden (DLC) |
| INDCL | Industrial Classical | |
| INDRH | Industrial Rhine | |
| IU | Industrial Urban | |
| CREE | Cree | Cree (DLC) |
| FG | Future/Generic | Gathering Storm |

Each culture set includes: Palace, 8-22 city Bld variants, and 5 Block shapes (LG_SQ, REC, SQ, TR, WR) × 3 variants.

### Composite TileBases

| TileBase | Contents |
|----------|----------|
| `DIS_CTY_EmptyCity_Base` | Empty City Center |
| `DIS_CTY_Palace_Base` | Palace only |
| `DIS_CTY_Monument_Base` | Monument only |
| `DIS_CTY_Granary_Base` | Granary only |
| `DIS_CTY_PalaceMonumentGranary_Base` | All three |

---

## Campus (DIS_CMP)

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| ⭐ **Library** | `DIS_CMP_Base_Library2` | 999 | 537 | 1 | 3 | ✓ | ✓ | 231 islands (avg 4.3v), bbox [121×161×160], UV1 3.5% |
| ⭐ **University (default)** | `DIS_CMP_Base_University` | 2,742 | 1,478 | 1 | 9 | ✓ | ✓ | 632 islands (avg 4.3v), bbox [279×221×196], UV1 5.4% |
| ⭐ **University (Classical)** | `DIS_CMP_University_Classical` | 2,081 | 1,494 | 2 | 4 | ✓ | ✓ | 365 islands (avg 4.5v), bbox [304×244×209], UV1 6.1% |
| ⭐ **Research Lab** | `DIS_CMP_Research` | 696 | 376 | 1 | 3 | ✓ | ✓ | 160 islands (avg 4.4v), bbox [121×90×160], UV1 3.3% |
| ⭐ **Madrasa** (Arabia UB) | `DIS_CMP_Madrasa` | 2,495 | 1,252 | 1 | 3 | ✓ | ✓ | 622 islands (avg 4.0v), bbox [315×271×185], UV1 5.0% |
| **Seowon** (Korea UB) | `DIS_Seowon_*` | — | — | — | — | ✓ | — | Separate district; see DLC section |

**Campus district props:** Flag, Greenhouse, LightPost, ReflectionPool, Round_Banner, Straight_Banner, Statue, AngledBuilding

### Madrasa variant (MDRSA) district bases

The Madrasa has its own complete set of district base variants:
- Classical: 3 variants (`DIS_CMP_MDRSA_Classical_Base_01/02/03`)
- Industrial: 3 variants
- Modern: 4 variants + Bld_A through Bld_F filler buildings

---

## Commercial Hub (DIS_COM)

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| ⭐ **Market** | `DIS_COM_Market` | 480 | 294 | 1 | 2 | ✓ | ✓ | 94 islands (avg 5.1v), bbox [142×111×105], UV1 3.0% |
| ⭐ **Market (Modern)** | `DIS_COM_Market_Modern` | 694 | 374 | 1 | 2 | ✓ | ✓ | 159 islands (avg 4.4v), bbox [151×123×126], UV1 2.5% |
| ⭐ **Bank (Modern)** | `DIS_COM_Bank_Modern` | 1,547 | 786 | 1 | 2 | ✓ | ✓ | 376 islands (avg 4.1v), bbox [164×164×137], UV1 2.1% |
| ⭐ **Stock Exchange** | `DIS_COM_StockExchange` | 652 | 328 | 1 | 2 | ✓ | ✓ | 162 islands (avg 4.0v), bbox [169×155×168], UV1 1.6% |
| ⭐ **Stock Exchange (Modern)** | `DIS_COM_StockExchange_Modern` | 974 | 508 | 1 | 2 | ✓ | ✓ | 230 islands (avg 4.2v), bbox [169×155×199], UV1 2.4% |
| **Grand Bazaar** (Ottoman UB) | `DIS_COM_OTTO_GrandBazaar` | — | — | 1 | — | — | — | Part of OTTO district system |
| **Suguba** (Mali UB) | `DIS_MALI_COM_Market` | 1,198 | 710 | 1 | — | — | ✓ | Mali-specific Market replacement |
| **Suguba Bank** (Mali) | `DIS_MALI_COM_Bank` | 2,232 | 1,208 | 1 | — | — | ✓ | |
| **Suguba Stock Exchange** | `DIS_MALI_COM_StockExchange` | — | — | — | — | — | ✓ | |

**Commercial props:** Apples_Green/Red, Blue/Green/Orange/Red/Yellow_Rug, Box_Closed/Open, Crate, Fruit_Stand, Oranges, Pot_Orange/Purple/Red/Yellow, Pot_Stand, Shop_A/B (+ Modern variants), Tent_A/B/C, Lg/Sm_Tent_Modern, Table

### Market Era Comparison (Deep Analysis)

| Variant | Verts | Tris | Islands | BBox X | UV1% |
|---------|------:|-----:|--------:|-------:|-----:|
| Market (Classical) | 480 | 294 | 94 | 142 | 3.0% |
| Market (Modern) | 694 | 374 | 159 | 151 | 2.5% |
| **Delta** | +45% | +27% | +69% | +6% | -17% |

**Pattern:** Modern variant adds more floating detail pieces (+69% islands) with slightly larger footprint (+6%).

---

## Encampment (DIS_ENC)

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| **Barracks (Ancient)** | `DIS_ENC_Base_DIS_ENC_Barracks_Ancient` | — | — | — | — | — | — | Embedded in base tile |
| ⭐ **Barracks (Classical)** | `DIS_ENC_Base_DIS_ENC_Barracks_Classical` | 1,131 | 549 | 4 | 6 | ✓ | ✓ | 116 islands (avg 3.9v), 4 sub-meshes |
| ⭐ **Barracks (Industrial)** | `DIS_ENC_Base_DIS_ENC_Barracks_Industrial` | 573 | 351 | 1 | — | ✓ | ✓ | 111 islands, bbox [205×192×46] |
| ⭐ **Stable** | `DIS_ENC_Stable` | 1,322 | 663 | 1 | 3 | ✓ | ✓ | 328 islands (avg 4.0v), bbox [214×195×102], UV1 4.0% |
| **Armory** | `DIS_ENC_Base_DIS_ENC_Armory` | — | — | — | — | ✓ | ✓ | Embedded in composite base |
| **Armory (Industrial)** | `DIS_ENC_Base_DIS_ENC_Armory_Industrial` | — | — | — | — | ✓ | ✓ | |
| **Military Academy** | `DIS_ENC_Base_DIS_ENC_MilAcademy_Industrial` | — | — | — | — | ✓ | ✓ | |
| **Ordu** (Mongol UB) | `DIS_ENC_Ordu` | — | — | — | — | ✓ | — | DLC unique |
| **Ikanda** (Zulu UB) | `DIS_ENC_Ikanda_*` | — | — | — | — | ✓ | ✓ | Full separate district system |

**Encampment props (era-variant):**
- Walls: Classical, Industrial (LG/MD/SM), Modern (LG/MD/SM)
- Towers: Classical, Industrial, Modern (all with PIL)
- Tents: Classical, Industrial, Sm_Closed/Open (Ancient/Classical variants)
- Other: Banner, Bullseye, Canon, Blocks, Flag_Classical/LG/Modern, Shed, Standard, Tank_Statue

### Barracks Era Comparison

| Era | Verts | Tris | Islands | Height (Z) |
|-----|------:|-----:|--------:|-----------:|
| Classical | 1,131 | 549 | 116 | 70 |
| Industrial | 573 | 351 | 111 | 46 |

**Anomaly:** Industrial barracks is *simpler* than Classical — it uses fewer, larger geometry pieces (quonset hut style vs. multiple tent buildings).

---

## Industrial Zone (DIS_PRD)

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| ⭐ **Workshop** | `DIS_PRD_Workshop` | 1,002 | 519 | 1 | 3 | ✓ | ✓ | 242 islands (avg 4.1v), bbox [195×160×95], UV1 2.5% |
| ⭐ **Workshop (Industrial)** | `DIS_PRD_IND_Workshop` | 679 | 356 | 1 | 3 | ✓ | ✓ | 162 islands (avg 4.2v), bbox [192×162×82], UV1 2.1% |
| ⭐ **Workshop (Modern)** | `DIS_PRD_Mod_Workshop` | 655 | 340 | 1 | 3 | ✓ | ✓ | 158 islands (avg 4.1v), bbox [191×159×83], UV1 1.9% |
| ⭐ **Factory** | `DIS_PRD_Factory` | 2,989 | 1,744 | 3 | 6 | ✓ | ✓ | 595 islands (avg 4.8v), bbox [325×304×139], UV1 7.1% |
| **Factory (Industrial sub)** | `DIS_PRD_FactoryIND` | — | — | — | — | — | — | Industrial-era sub-building |
| **Electronics Factory** (Japan UB) | `DIS_PRD_Modern_Japan_04ElectronicsFactory` | — | — | — | — | ✓ | ✓ | Japan-specific |
| ⭐ **Power Plant** | `DIS_PRD_PowerPlant` | 1,949 | 1,256 | 1 | 3 | ✓ | ✓ | 368 islands (avg 5.3v), bbox [223×268×166], UV1 5.1% |
| **Fossil Fuel Power Plant** (GS) | `DIS_PRD_PowerPlant_FossilFuel` | 2,141 | 1,360 | 4 | — | ✓ | ✓ | Includes tower sub-mesh |

**Industrial props:** Barrel, BlacksmithA, Bld_A/B/C, CoolingTowerA/B, HandCrane, IND_Fence, IND_Rails, Metal_Tanks_A/B/C, Modern_Crane, Pile/PileA-E, PileBlock/PileWood variants, Pot, RainBarrelA, Red/Yellow/Metal_Barrel, SandCorral, ShackA, Stable, StableShack, Stone_A/B, Tower, Wall_A/B/C, Watermill, WeldingArm, Windmill, Wood_Plank

**Hansa (Germany UB):** Full parallel set — `DIS_PRD_HANSA_*` bases (Classical/Industrial/Modern OBs), HansaFactory*, HansaFiller_Lg/Sm A-C, HansaFillerShop A-E

### Workshop Era Comparison (Deep Analysis)

| Era | Verts | Tris | Islands | BBox Z | UV1% |
|-----|------:|-----:|--------:|-------:|-----:|
| Classical | 1,002 | 519 | 242 | 95 | 2.5% |
| Industrial | 679 | 356 | 162 | 82 | 2.1% |
| Modern | 655 | 340 | 158 | 83 | 1.9% |

**Pattern:** Workshop *decreases* in complexity from Classical → Modern. The Classical variant has more organic detail (thatched roof, wooden beams, multiple outbuildings) while modern is a simpler prefab-style structure relying on textures.

---

## Harbor (DIS_HBR)

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| ⭐ **Lighthouse (Classical)** | `DIS_HBR_Classical_Base_Lighthouse` | 812 | 654 | 1 | 2 | ✓ | ✓ | 114 islands (avg 7.1v), bbox [176×165×280], UV1 6.8% |
| **Lighthouse (Classical, standalone)** | `DIS_HBR_Classical_Lighthouse` | — | — | — | — | — | — | Separate lighthouse mesh |
| ⭐ **Lighthouse (Modern)** | `DIS_HBR_Modern_Base_Lighthouse` | 824 | 633 | 1 | 2 | ✓ | ✓ | 119 islands (avg 6.9v), bbox [176×165×289], UV1 6.4% |
| **Lighthouse (Modern, standalone)** | `DIS_HBR_Modern_Lighthouse` | — | — | — | — | — | — | |
| **Shipyard (Classical)** | `DIS_HBR_Classical_Shipyard` | 1,109 | 761 | 1 | 2 | ✓ | ✓ | 204 islands (avg 5.4v), bbox [190×188×110] |
| **Shipyard (Modern)** | `DIS_HBR_Modern_Shipyard` | — | — | — | — | ✓ | ✓ | |
| **Seaport (Modern)** | `DIS_HBR_Modern_Seaport` | — | — | — | — | ✓ | ✓ | |

**Harbor props (Classical):** Shack, Shack_B, Coal_Pile, Fish_Group, Fish_Table, Lg_Fish_Bin, SM_Bin
**Harbor props (Modern):** Cone, Crane, Lg_Bldg, Orange/Teal/Yellow_Crate, Sign, Warehouse

**Royal Navy Dockyard (England UB):** `DIS_HBR_RNY_*` — parallel set of Classical/Modern bases, Shipyard, Seaport

### Lighthouse Era Comparison

| Era | Verts | Tris | Islands | Height (Z) | UV1% |
|-----|------:|-----:|--------:|-----------:|-----:|
| Classical | 812 | 654 | 114 | 280 | 6.8% |
| Modern | 824 | 633 | 119 | 289 | 6.4% |

**Pattern:** Nearly identical complexity. The lighthouse is one of the few buildings that barely changes between eras — same structural form, just texture differences.

---

## Holy Site (DIS_REL)

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| ⭐ **Shrine** | `DIS_REL_Shrine` | 908 | 478 | 1 | 1 | ✓ | ✓ | 215 islands (avg 4.2v), bbox [111×111×104], UV1 2.0% |
| ⭐ **Temple** | `DIS_REL_Temple` | 831 | 480 | 1 | 1 | ✓ | ✓ | 181 islands (avg 4.6v), bbox [178×217×260], UV1 2.1% |
| **Stave Church** (Norway UB) | `DIS_REL_StaveChurch` | — | — | — | — | ✓ | ✓ | Replaces Temple |
| ⭐ **Cathedral** | `DIS_REL_Cathedral` | 2,216 | 1,216 | 12 | 12 | ✓ | ✓ | 410 islands, bbox [240×217×351] — tallest standard building |
| **Gurdwara** | `DIS_REL_Gurdwara` | — | — | — | — | ✓ | ✓ | Worship building |
| **Meeting House** | `DIS_REL_MeetingHouse` | — | — | — | — | ✓ | ✓ | Worship building |
| ⭐ **Mosque** | `DIS_REL_Mosque` | 2,298 | 1,306 | 1 | 1 | ✓ | ✓ | 496 islands (avg 4.6v), bbox [274×237×301], UV1 2.8% |
| **Pagoda** | `DIS_REL_Pagoda` | — | — | — | — | ✓ | ✓ | Worship building |
| **Synagogue** | `DIS_REL_Synagogue` | — | — | — | — | ✓ | ✓ | Worship building |
| **Wat** | `DIS_REL_Wat` | — | — | — | — | ✓ | ✓ | Worship building |
| **Stupa** (GS) | `DIS_REL_Stupa` | 1,889 | 1,217 | 1 | 6 | — | ✓ | GS worship building + rope sub-meshes |
| **Dar-e Mehr** (GS) | `DIS_REL_Dar-E-Mehr` | 2,290 | 1,330 | 1 | 4 | — | ✓ | GS worship building |

**Lavra (Russia UB):** Complete parallel district — `DIS_REL_LAVRA_*` with Lg_Bld, Lg_Wall, Sm_Tower, Sm_Wall, Tower + Ancient/Classical/Industrial/Modern bases

---

## Theater Square (DIS_THR)

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| **Amphitheater** | `DIS_THR_CLA_Base02Ampitheater` | 1,360 | 947 | 1 | 1 | ✓ | ✓ | 202 islands (avg 6.7v), bbox [198×165×83] |
| **Museum (Art)** | `DIS_THR_REN_Base03Museum` | — | — | — | — | ✓ | ✓ | Era-integrated into base tiles |
| **Museum (Artifact)** | (same as Art) | — | — | — | — | ✓ | ✓ | Separate ART/NAT base tile variants |
| **Broadcast Center** | `DIS_THR_MOD_Base04BroadcastCenter_a` | — | — | — | — | ✓ | ✓ | |
| **Film Studio** (America UB) | `DIS_THR_MOD_America04StudioLot` | — | — | — | — | ✓ | ✓ | |
| **Marae** (Maori UB, GS) | `DIS_THR_MAR_Marae` | 2,621 | 1,922 | 2 | — | ✓ | ✓ | DLC unique |

**Theater props:** DinoRemains, DinoSkeleton, MuseumArtColumn, MuseumArtFountain, Parthenon (Acropolis), StatueHorse, StatueLeader, Well

**Acropolis (Greece UB):** `DIS_THR_CLA_Greece*`, `DIS_THR_IND_Greece*`, `DIS_THR_MOD_Greece*` — parallel Greek-themed base tiles across all eras

**Base tile pattern:** `DIS_THR_{ERA}_Base{NN}{TYPE}` where TYPE = ART/NAT for art vs. natural history museums

---

## Entertainment Complex (DIS_ENT)

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| **Arena** | `DIS_ENT_Base_DIS_ENT` | — | — | — | — | — | — | Embedded in district base |
| **Tlachtli** (Aztec UB) | `DIS_ENT_Ballcourt` | — | — | — | — | ✓ | ✓ | |
| ⭐ **Zoo** | `DIS_ENT_Zoo` | 4,188 | 2,563 | 28 | 30 | ✓ | ✓ | 494 islands (main mesh), bbox [200×298×106] — most sub-meshes of any building |
| ⭐ **Stadium** | `DIS_ENT_Stadium` | 2,712 | 1,460 | 1 | 1 | ✓ | ✓ | 626 islands (avg 4.3v), bbox [260×273×154], UV1 4.8% |
| **Thermal Bath** (Hungary UB, GS) | `DIS_ENT_ThermalBath` | 5,465 | 3,420 | 2 | — | ✓ | ✓ | One of highest vertex counts |

**Entertainment props:** BalloonCart, Balloons, BlueTent, Carousel, GameStand, GreenTent, Joust, LampPost, LgOrangeTent, OrangeTent, PurpleTent, Lg/Sm_Trailer (Classical/Industrial/Modern)

**Street Carnival (Brazil UB):** `DIS_ENT_Brazil_Carn_*` — full parallel set: bleachers, LgTent, Tent, flags, + base tiles per era

---

## Water Park (DIS_Water_ENT) — Rise & Fall

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| **Ferris Wheel** | `DIS_Water_ENT_Ferris_Wheel` | 7,655 | 4,388 | 2 | — | ✓ | ✓ | Highest vertex count of any standard building |
| **Aquarium (Industrial)** | `DIS_Water_ENT_IND_Aquarium` | 2,929 | 1,707 | 1 | — | ✓ | ✓ | |
| **Aquarium (Modern)** | `DIS_Water_ENT_MOD_Aquarium` | — | — | — | — | ✓ | ✓ | |
| **Aquatics Center** | `DIS_Water_ENT_Aquatics_Center` | 2,092 | 1,240 | 2 | — | ✓ | ✓ | |

**Water Park props:** Entrance, Sea_Lions, Seat, Tank, Tank_A/B (IND/MOD), Tent variants (Blue, Green, Orange, Purple + striped)

---

## Aerodrome (DIS_AERO)

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| ⭐ **Airport** | `DIS_AERO_Airport` | 1,627 | 1,015 | 1 | 1 | ✓ | ✓ | 303 islands (avg 5.4v), bbox [306×381×148], UV1 7.8% |
| **Hangar** | `DIS_AERO_Hangar` | — | — | — | — | ✓ | ✓ | |
| **Bld_A** | `DIS_AERO_Bld_A` | — | — | — | — | ✓ | ✓ | Terminal building |
| **Bld_B** | `DIS_AERO_Bld_B` | — | — | — | — | ✓ | ✓ | Control building |

**Aerodrome props:** Lightpost, Lugage_CarrierA/B, Lugage_carts, Radio_Tower, Tower, Windsock

---

## Spaceport (DIS_SPACE)

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| **Bld_A** | `DIS_SPACE_Bld_A` | — | — | — | — | ✓ | ✓ | |
| **Bld_B** | `DIS_SPACE_Bld_B` | — | — | — | — | ✓ | ✓ | |
| **Bld_C** | `DIS_SPACE_Bld_C` | — | — | — | — | ✓ | ✓ | |
| **Bld_D** | `DIS_SPACE_Bld_D` | — | — | — | — | ✓ | ✓ | |
| **Mission Control** | `DIS_SPACE_Mission_Control` | — | — | — | — | ✓ | ✓ | |
| **Large Rocket** | `DIS_SPACE_Large_Rocket` | — | — | — | — | — | ✓ | Mars mission |
| **Medium Rocket** | `DIS_SPACE_Medium_Rocket` | — | — | — | — | — | ✓ | Moon mission |
| **Small Rocket** | `DIS_SPACE_Small_Rocket` | — | — | — | — | — | ✓ | Satellite |
| **Saturn** | `DIS_SPACE_Saturn` | — | — | — | — | — | — | Saturn V reference rocket |

**Spaceport props:** Launch_Cam (01/Lg/Med), Oil_Tank/B, PipesA/B/C, Sphere

---

## Neighborhood (DIS_NBH)

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| **HouseA-G** | `DIS_NBH_HouseA` etc. | ~300-600v each | — | 1 | — | ✓ | — | 7 residential house variants |
| **Townhouse_A** (Lg/Sm) | `DIS_NBH_Townhouse_A_Lg/Sm` | — | — | 1 | — | ✓ | — | Row houses |
| **Hotel_A** (Lg/Sm/XSm) | `DIS_NBH_Hotel_A_Lg/Sm/XSm` | — | — | 1 | — | ✓ | — | |
| **Apartment_A** (Lg/Sm) | `DIS_NBH_Apartment_A_Lg/Sm` | — | — | 1 | — | — | — | |
| **Shopping Mall** (R&F) | `DIS_NBH_Mall_A/B/C` | — | — | — | — | ✓ | — | DLC addition |
| **Food Market** (R&F) | `DIS_NBH_Market_A` | — | — | — | — | ✓ | — | DLC addition |

**Neighborhood props:** DogHouse, FenceA-D, LawnGnomeA/B, PinkFlamingoA/B, WaterTower

**Mbanza (Kongo UB):** `DIS_Mbanza_*` — Bld_A-E, Pot_Blue/Orange, Rugs, Tent + base tiles

---

## Aqueduct (DIS_AQD)

| Building/Element | Geometry File | Notes |
|----------|---------------|-------|
| **Bath** | `DIS_AQD_Base_Bath` | PIL, CON variants |
| **Gate** | `DIS_AQD_Base_Gate` | PIL, CON variants |
| **Tower** | `DIS_AQD_Base_Tower` | PIL, CON variants |
| **Wall** | `DIS_AQD_Base_Wall` | PIL, CON variants |
| **Waterwheel** | `DIS_AQD_Base_Waterwheel` | + Reversed variant |

Era-specific base tiles: Classical, Industrial, Modern + era-specific filler buildings (IND_Bld_Lg/Sm A-D, MOD_Bld_Lg/Sm A-B)

---

## Canal (DIS_CNL) — Gathering Storm

Complex district with orientation-dependent geometry:

| Pattern | Variants |
|---------|----------|
| Straight | Base01/02, StrtExit_N/S, YExit_N/S |
| Bent | Base01, StrtExit_N/S, YExit_N/S |
| Port | Base |

Each variant has: Classical, Industrial (IND), and Ancient (ANC) eras. All have CON and PIL variants.

---

## Dam (DIS_DAM) — Gathering Storm

| Building | Geometry File | v | t | m | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|:---:|:---:|-------|
| **Dam (Classical)** | `DIS_DAM_Dam_CLA` | 1,667 | 1,213 | 1 | ✓ | ✓ | |
| **Dam (Modern)** | `DIS_DAM_Dam_MOD` | 1,708 | 1,114 | 1 | ✓ | ✓ | |
| **Hydroelectric Dam** | `DIS_DAM_HydroPlant` | 1,224 | 626 | 1 | ✓ | ✓ | + TB (TileBase) variant |
| **Flood Barrier** | (no standalone geo) | — | — | — | — | — | Integrated into Dam base |

**Dam props:** Boathouse (CLA/MOD), Coil, Gazebo (CLA/MOD), Generator_Platform, Monument_Lg/Sm, Outhouse_CLA, Tower_Platform

---

## Government Plaza (DIS_GOV) — Rise & Fall

| Building | Geometry File | v | t | m | b | PIL | CON |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|
| **Ancestral Hall** (Tall) | `DIS_GOV_Tall_Bld` | 1,456 | 776 | 1 | 2 | ✓ | ✓ |
| **Audience Chamber** (Wide) | `DIS_GOV_Wide_Bld` | 533 | 288 | 1 | 2 | ✓ | ✓ |
| **Warlord's Throne** (Conquest) | `DIS_GOV_Conquest_Bld` | 598 | 324 | 1 | 2 | ✓ | ✓ |
| **Foreign Ministry** (CityStates) | `DIS_GOV_City_States_Bld` | 945 | 471 | 1 | 2 | ✓ | ✓ |
| **Grand Master's Chapel** (Faith) | `DIS_GOV_Faith_Bld` | 2,008 | 1,103 | 1 | 8 | ✓ | ✓ |
| **Intelligence Agency** (Spies) | `DIS_GOV_Spies_Bld` | 1,374 | 664 | 1 | 2 | ✓ | ✓ |
| **National History Museum** (Culture) | `DIS_GOV_Culture_Bld` | 3,197 | 1,568 | 1 | 6 | ✓ | ✓ |
| **Royal Society** (Science) | `DIS_GOV_Science_Bld` | 1,536 | 779 | 1 | 8 | ✓ | ✓ |
| **War Department** (Military) | `DIS_GOV_Military_Bld` | 1,738 | 898 | 1 | 18 | ✓ | ✓ |

**Gov Plaza props:** Ancient_Bld_A-D, FlagPole, Hotel_A_Lg/Sm, Hotel_B, Monument_Bld, Pillars_A, Reflection_Pool, Statue

**District bases:** Ancient (1), Classical (3), Industrial (3), Modern (4), Construction (1)

**Pattern:** Gov Plaza buildings use `DIS_GOV_{PURPOSE}_Bld` naming. Bone counts vary widely (2-18) — the Military building has the most attachment points. The Culture building (National History Museum) has the highest vertex count at 3,197v.

---

## Unique District Replacements (DLC)

### Seowon (Korea, R&F) — replaces Campus
Full parallel district: `DIS_Seowon_*` with Ancient/Classical/Industrial/Modern bases, Bld_A-J, SmA, Sm_Temple, Lg, Wall_A-E, Lanterns, Barrel

### Ikanda (Zulu, R&F) — replaces Encampment
Full parallel district: `DIS_ENC_Ikanda_*` with ANC/CLA/IND/MOD bases, Thatch buildings, Fences, Firepit, Gate, Outbldg, Pot, Spikes, Tower, Wall + corner

### Cothon (Phoenicia, GS) — replaces Harbor
`DIS_COTHON_*` — Lighthouse, Shipyard, Seaport + Classical/Modern bases, Shack_A/B, Bld_A/B

### Ottoman Commercial (GS) — Grand Bazaar district variant
`DIS_COM_OTTO_*` — GrandBazaar, Main_Bld, Bld_A-C, Booth_A-E, Blanket_A-E, Lights, Pot/Sac variants

### Mali Commercial (GS) — Suguba
`DIS_MALI_COM_*` — Market, Modern_Market, Bank, StockExchange, Filler_Bld (Lg/Med/SM)

---

## Building Count Summary

| District | Base Geos | PIL | CON | DLC Geos | Total |
|----------|--:|--:|--:|--:|--:|
| City Center (CTY) | 700+ | ~200 | ~30 | ~200 | ~1,200+ |
| Campus (CMP) | 18 | 6 | 4 | ~60 (Seowon) | ~90 |
| Commercial Hub (COM) | 32 | 15 | 12 | ~50 (OTTO/MALI) | ~110 |
| Encampment (ENC) | 33 | 20 | 8 | ~50 (Ikanda) | ~110 |
| Industrial Zone (PRD) | 90 | 30 | 20 | ~10 | ~150 |
| Harbor (HBR) | 21 | 10 | 8 | ~30 (RNY/Cothon) | ~70 |
| Holy Site (REL) | 20 | 12 | 10 | ~40 (Lavra) | ~80 |
| Theater Square (THR) | 72 | 10 | 5 | ~20 (Marae) | ~110 |
| Entertainment (ENT) | 26 | 10 | 8 | ~5 (ThermalBath) | ~50 |
| Water Park | — | — | — | ~60 | ~60 |
| Aerodrome (AERO) | 15 | 8 | 4 | — | ~30 |
| Spaceport (SPACE) | 17 | 8 | 6 | — | ~30 |
| Neighborhood (NBH) | 24 | 12 | 2 | ~25 (Mall/Market) | ~65 |
| Aqueduct (AQD) | ~30 | 8 | 6 | — | ~45 |
| Canal (CNL) | 24 | 8 | 6 | — | ~40 |
| Dam (DAM) | — | — | — | ~30 | ~30 |
| Gov Plaza (GOV) | — | — | — | ~40 | ~40 |
| **TOTAL** | **~1,150** | **~350** | **~130** | **~620** | **~2,300+** |

---

## Major Building Deep Analysis Summary

All 11 major buildings inspected via CN6 + Blender:

| Building | Verts | Tris | Islands | Avg Island | BBox [X×Y×Z] | UV1% | UV2% |
|----------|------:|-----:|--------:|-----------:|-------------|-----:|-----:|
| Market | 480 | 294 | 94 | 5.1 | 142×111×105 | 3.0 | 5.0 |
| Market (Modern) | 694 | 374 | 159 | 4.4 | 151×123×126 | 2.5 | — |
| Library | 999 | 537 | 231 | 4.3 | 121×161×160 | 3.5 | 5.0 |
| Lighthouse (Classical) | 812 | 654 | 114 | 7.1 | 176×165×280 | 6.8 | — |
| Lighthouse (Modern) | 824 | 633 | 119 | 6.9 | 176×165×289 | 6.4 | — |
| Granary (Ancient) | 2,868 | 1,624 | 526 | 4.4 | 185×145×108 | 2.1 | — |
| Granary (Modern) | 4,022 | 2,170 | 862 | 4.2 | 212×179×157 | 4.2 | — |
| Barracks (Classical) | 1,131 | 549 | 116 | 3.9 | 91×108×70 | 1.6 | — |
| Workshop | 1,002 | 519 | 242 | 4.1 | 195×160×95 | 2.5 | — |
| Stable | 1,322 | 663 | 328 | 4.0 | 214×195×102 | 4.0 | — |
| Shrine | 908 | 478 | 215 | 4.2 | 111×111×104 | 2.0 | — |
| Temple | 831 | 480 | 181 | 4.6 | 178×217×260 | 2.1 | — |
| Bank (Modern) | 1,547 | 786 | 376 | 4.1 | 164×164×137 | 2.1 | — |
| University (default) | 2,742 | 1,478 | 632 | 4.3 | 279×221×196 | 5.4 | — |
| University (Classical) | 2,081 | 1,494 | 365 | 4.5 | 304×244×209 | 6.1 | — |

**Key insight: Average island size is 4.0-5.1 vertices across ALL buildings.** This is the fundamental building block of Civ 6 geometry — individual floating quads (2 triangles = 4 unique vertices). The lighthouse is the notable exception at 7.1 avg — its cylindrical tower uses slightly larger connected patches.

---

## Appendix: Geometry Files Not Mapped to Buildings

Some geometry in the pantry serves district decoration rather than specific gameplay buildings:

| Prefix | Purpose |
|--------|---------|
| `DIS_Ancient_*` | Generic ancient-era props (Cross, flag, Banners, Fillers) |
| `DIS_GEN_*` | Generic fillers across eras (Cars, IND_Filler buildings, LampPosts, Torches) |
| `DIS_Hanging_flags` | Decoration props |
| `DIS_Lg_Banner` | Large banner prop |
| `DIS_Roped_Flags` | Rope flag decoration |
| `DIS_Pot*` | Pot props |
| `DIS_SimpleHexOB` | Empty hex obstruction box |
| `DIS_CTY_*_Block_*` | City block composites (procedural city generation) |
| `DIS_CTY_*_Bld_*` | City filler buildings (culture-specific housing) |
| `DIS_CTY_Foundation_*` | Ground plane foundation meshes |

---

*Full mesh analysis data: [`building-mesh-analysis.json`](building-mesh-analysis.json)*
*Bulk geometry stats: [`geo-stats-all.tsv`](geo-stats-all.tsv)*
*Blender inspection script: [`../scripts/inspect_building_mesh.py`](../scripts/inspect_building_mesh.py)*
