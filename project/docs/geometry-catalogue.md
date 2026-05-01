# Geometry Catalogue

> Complete building geometry stats from SDK pantry analysis. Base game + Rise & Fall + Gathering Storm.
> Stats from .geo XML metadata + Blender mesh inspection of 34 key assets via CN6.

## How to Read This

- **v** = vertices, **t** = triangles, **m** = mesh objects, **b** = bones, **i** = mesh islands
- **bbox** = bounding box [X × Y × Z] in game units
- **UV1%** = UV1 space utilisation
- PIL/CON = Pillaged/Construction variant exists
- ⭐ = deep mesh inspection performed (CN6 + Blender)

---

## City Center (DIS_CTY)

### Core Buildings

| Building | Geometry File | v | t | m | b | PIL | CON | Notes |
|----------|---------------|--:|--:|--:|--:|:---:|:---:|-------|
| ⭐ Granary (Ancient) | `DIS_CTY_Granary_AN` | 2,868 | 1,624 | 5 | 7 | ✓ | ✓ | 526i, bbox [185×145×108], UV1 2.1% |
| ⭐ Granary (Renaissance) | `DIS_CTY_Granary_RE` | 3,036 | 1,724 | 6 | 8 | ✓ | ✓ | 578i, bbox [212×166×141], UV1 4.6% |
| ⭐ Granary (Modern) | `DIS_CTY_Granary_MD` | 4,022 | 2,170 | 7 | 9 | ✓ | ✓ | 862i, bbox [212×179×157], UV1 4.2% |
| Monument (Ancient) | `DIS_CTY_ANC_Monument` | 1,713 | 1,197 | 10 | 7 | ✓ | ✓ | Obelisk + base |
| Monument (Asian) | `DIS_CTY_Monument_Asian` | 1,952 | 1,166 | 6 | 2 | ✓ | ✓ | Culture variant |
| Water Mill (Ancient) | `DIS_CTY_Watermill_AN` | — | — | — | — | — | — | |
| Water Mill (Modern) | `DIS_CTY_Watermill_MD` | — | — | — | — | — | — | |

### Granary Era Progression

| Era | Verts | Tris | Islands | BBox Z | UV1% | Delta from AN |
|-----|------:|-----:|--------:|-------:|-----:|--------------:|
| Ancient | 2,868 | 1,624 | 526 | 108 | 2.1% | — |
| Renaissance | 3,036 | 1,724 | 578 | 141 | 4.6% | +6% verts |
| Modern | 4,022 | 2,170 | 862 | 157 | 4.2% | +40% verts |

Modern adds ~40% more vertices but ~64% more islands — complexity comes from more small detail pieces.

### Palace Variants (by culture)

| Code | Culture Set | Example Civs |
|------|------------|--------------|
| AB | East Asian | China, Japan |
| AE | South Asian | India, Khmer |
| AW | Middle Eastern | Arabia, Persia |
| RC | Renaissance Classical | Greece, Rome |
| RE | Renaissance European | England, France, Spain |
| RIND | Renaissance Indonesian | Indonesia |
| RJ | Renaissance Japanese | Japan |
| RMUG | Renaissance Mughal | India |
| RSS | Renaissance S/SE Asian | — |
| RSA | Renaissance South American | Aztec, Inca |
| CREE | Cree (DLC) | Cree |
| RMAO | Maori (DLC) | Maori |

Each culture set includes: Palace, 8–22 city Bld variants, and 5 Block shapes × 3 variants.

### Composite TileBases
`DIS_CTY_EmptyCity_Base`, `DIS_CTY_Palace_Base`, `DIS_CTY_Monument_Base`, `DIS_CTY_Granary_Base`, `DIS_CTY_PalaceMonumentGranary_Base`

---

## Campus (DIS_CMP)

| Building | v | t | m | b | i | bbox | UV1% | PIL | CON |
|----------|--:|--:|--:|--:|--:|------|-----:|:---:|:---:|
| ⭐ Library | 999 | 537 | 1 | 3 | 231 | 121×161×160 | 3.5% | ✓ | ✓ |
| ⭐ University | 2,742 | 1,478 | 1 | 9 | 632 | 279×221×196 | 5.4% | ✓ | ✓ |
| ⭐ University (Classical) | 2,081 | 1,494 | 2 | 4 | 365 | 304×244×209 | 6.1% | ✓ | ✓ |
| ⭐ Research Lab | 696 | 376 | 1 | 3 | 160 | 121×90×160 | 3.3% | ✓ | ✓ |
| ⭐ Madrasa (Arabia UB) | 2,495 | 1,252 | 1 | 3 | 622 | 315×271×185 | 5.0% | ✓ | ✓ |

Props: Flag, Greenhouse, LightPost, ReflectionPool, Banners, Statue, AngledBuilding.

Madrasa has its own complete district base system: Classical/Industrial/Modern variants + Bld_A–F fillers.

---

## Commercial Hub (DIS_COM)

| Building | v | t | i | bbox | UV1% | PIL | CON |
|----------|--:|--:|--:|------|-----:|:---:|:---:|
| ⭐ Market | 480 | 294 | 94 | 142×111×105 | 3.0% | ✓ | ✓ |
| ⭐ Market (Modern) | 694 | 374 | 159 | 151×123×126 | 2.5% | ✓ | ✓ |
| ⭐ Bank (Modern) | 1,547 | 786 | 376 | 164×164×137 | 2.1% | ✓ | ✓ |
| ⭐ Stock Exchange | 652 | 328 | 162 | 169×155×168 | 1.6% | ✓ | ✓ |
| ⭐ Stock Exchange (Modern) | 974 | 508 | 230 | 169×155×199 | 2.4% | ✓ | ✓ |
| Suguba (Mali, Market) | 1,198 | 710 | — | — | — | — | ✓ |
| Suguba Bank (Mali) | 2,232 | 1,208 | — | — | — | — | ✓ |

**Market Era Comparison:**

| Variant | Verts | Tris | Islands | Delta |
|---------|------:|-----:|--------:|------:|
| Classical | 480 | 294 | 94 | — |
| Modern | 694 | 374 | 159 | +45% v, +69% islands |

Props: Fruit stands, rugs, pots, crates, tents (Classical + Modern variants).

---

## Encampment (DIS_ENC)

| Building | v | t | m | b | i | bbox | PIL | CON |
|----------|--:|--:|--:|--:|--:|------|:---:|:---:|
| ⭐ Barracks (Classical) | 1,131 | 549 | 4 | 6 | 116 | 91×108×70 | ✓ | ✓ |
| ⭐ Barracks (Industrial) | 573 | 351 | 1 | — | 111 | 205×192×46 | ✓ | ✓ |
| ⭐ Stable | 1,322 | 663 | 1 | 3 | 328 | 214×195×102 | ✓ | ✓ |

**Barracks anomaly:** Industrial (573v) is *simpler* than Classical (1,131v) — quonset hut vs multiple tents.

Props (era-variant): Walls (Classical/Industrial/Modern, LG/MD/SM), Towers, Tents, Banners, Cannons, Tank Statues.

Ikanda (Zulu UB): Full separate district system with own base tiles across all eras.

---

## Industrial Zone (DIS_PRD)

| Building | v | t | m | b | i | bbox | UV1% | PIL | CON |
|----------|--:|--:|--:|--:|--:|------|-----:|:---:|:---:|
| ⭐ Workshop | 1,002 | 519 | 1 | 3 | 242 | 195×160×95 | 2.5% | ✓ | ✓ |
| ⭐ Workshop (Industrial) | 679 | 356 | 1 | 3 | 162 | 192×162×82 | 2.1% | ✓ | ✓ |
| ⭐ Workshop (Modern) | 655 | 340 | 1 | 3 | 158 | 191×159×83 | 1.9% | ✓ | ✓ |
| ⭐ Factory | 2,989 | 1,744 | 3 | 6 | 595 | 325×304×139 | 7.1% | ✓ | ✓ |
| ⭐ Power Plant | 1,949 | 1,256 | 1 | 3 | 368 | 223×268×166 | 5.1% | ✓ | ✓ |
| Fossil Fuel Plant (GS) | 2,141 | 1,360 | 4 | — | — | — | — | ✓ | ✓ |
| Hydroelectric Dam | 1,224 | 626 | 1 | — | — | — | — | ✓ | ✓ |

**Workshop decreases over eras:** Classical 1,002v → Modern 655v (–35%). Complex timber → simple prefab.

Props: Barrel variants, BlacksmithA, CoolingTowers, Cranes, Metal Tanks, Piles, Rails, Windmill, WeldingArm.

Hansa (Germany UB): Full parallel set with HansaFactory, HansaFiller buildings.

---

## Harbor (DIS_HBR)

| Building | v | t | i | bbox | UV1% | PIL | CON |
|----------|--:|--:|--:|------|-----:|:---:|:---:|
| ⭐ Lighthouse (Classical) | 812 | 654 | 114 | 176×165×280 | 6.8% | ✓ | ✓ |
| ⭐ Lighthouse (Modern) | 824 | 633 | 119 | 176×165×289 | 6.4% | ✓ | ✓ |
| Shipyard (Classical) | 1,109 | 761 | 204 | 190×188×110 | — | ✓ | ✓ |

**Lighthouse barely changes:** +1.5% verts Classical→Modern. Same structural form.

Royal Navy Dockyard (England UB): Parallel set of Classical/Modern bases.

---

## Holy Site (DIS_REL)

| Building | v | t | m | b | i | bbox | UV1% | PIL | CON |
|----------|--:|--:|--:|--:|--:|------|-----:|:---:|:---:|
| ⭐ Shrine | 908 | 478 | 1 | 1 | 215 | 111×111×104 | 2.0% | ✓ | ✓ |
| ⭐ Temple | 831 | 480 | 1 | 1 | 181 | 178×217×260 | 2.1% | ✓ | ✓ |
| ⭐ Cathedral | 2,216 | 1,216 | 12 | 12 | 410 | 240×217×351 | — | ✓ | ✓ |
| ⭐ Mosque | 2,298 | 1,306 | 1 | 1 | 496 | 274×237×301 | 2.8% | ✓ | ✓ |
| Stupa (GS) | 1,889 | 1,217 | 1 | 6 | — | — | — | — | ✓ |
| Dar-e Mehr (GS) | 2,290 | 1,330 | 1 | 4 | — | — | — | — | ✓ |

Cathedral (351 Z) and Mosque (301 Z) are the **tallest standard buildings** in the game.

Lavra (Russia UB): Complete parallel district system.

---

## Theater Square (DIS_THR)

| Building | v | t | i | bbox | PIL | CON |
|----------|--:|--:|--:|------|:---:|:---:|
| Amphitheater | 1,360 | 947 | 202 | 198×165×83 | ✓ | ✓ |
| Marae (Maori, GS) | 2,621 | 1,922 | — | — | ✓ | ✓ |

Base tiles follow `DIS_THR_{ERA}_Base{NN}{TYPE}` where TYPE = ART/NAT for museum variants.

Acropolis (Greece UB): Parallel Greek-themed bases across all eras.

---

## Entertainment Complex (DIS_ENT)

| Building | v | t | m | b | i | bbox | UV1% | PIL | CON |
|----------|--:|--:|--:|--:|--:|------|-----:|:---:|:---:|
| ⭐ Zoo | 4,188 | 2,563 | 28 | 30 | 494 | 200×298×106 | — | ✓ | ✓ |
| ⭐ Stadium | 2,712 | 1,460 | 1 | 1 | 626 | 260×273×154 | 4.8% | ✓ | ✓ |
| Thermal Bath (Hungary, GS) | 5,465 | 3,420 | 2 | — | — | — | — | ✓ | ✓ |

Zoo: Most sub-meshes of any building (28 objects — structures, paths, decals, fences, water).

### Water Park (DIS_Water_ENT, R&F)

| Building | v | t |
|----------|--:|--:|
| Ferris Wheel | 7,655 | 4,388 |
| Aquarium (Industrial) | 2,929 | 1,707 |
| Aquatics Center | 2,092 | 1,240 |

Ferris Wheel: **Highest vertex count** of any standard building.

---

## Aerodrome (DIS_AERO)

| Building | v | t | i | bbox | UV1% | PIL | CON |
|----------|--:|--:|--:|------|-----:|:---:|:---:|
| ⭐ Airport | 1,627 | 1,015 | 303 | 306×381×148 | 7.8% | ✓ | ✓ |

Props: Lightpost, Luggage carriers/carts, Radio Tower, Tower, Windsock.

---

## Government Plaza (DIS_GOV, R&F)

| Building | Geo Name | v | t | b | PIL | CON |
|----------|----------|--:|--:|--:|:---:|:---:|
| Ancestral Hall | `DIS_GOV_Tall_Bld` | 1,456 | 776 | 2 | ✓ | ✓ |
| Audience Chamber | `DIS_GOV_Wide_Bld` | 533 | 288 | 2 | ✓ | ✓ |
| Warlord's Throne | `DIS_GOV_Conquest_Bld` | 598 | 324 | 2 | ✓ | ✓ |
| Foreign Ministry | `DIS_GOV_City_States_Bld` | 945 | 471 | 2 | ✓ | ✓ |
| Grand Master's Chapel | `DIS_GOV_Faith_Bld` | 2,008 | 1,103 | 8 | ✓ | ✓ |
| Intelligence Agency | `DIS_GOV_Spies_Bld` | 1,374 | 664 | 2 | ✓ | ✓ |
| Nat'l History Museum | `DIS_GOV_Culture_Bld` | 3,197 | 1,568 | 6 | ✓ | ✓ |
| Royal Society | `DIS_GOV_Science_Bld` | 1,536 | 779 | 8 | ✓ | ✓ |
| War Department | `DIS_GOV_Military_Bld` | 1,738 | 898 | 18 | ✓ | ✓ |

Naming: `DIS_GOV_{PURPOSE}_Bld`. Widest complexity range of any district (533–3,197v). War Department has 18 bones — most attachment points.

---

## Summary Statistics

### All 34 Deep-Inspected Buildings

| Building | Verts | Tris | Islands | Avg Island | BBox [X×Y×Z] | UV1% |
|----------|------:|-----:|--------:|-----------:|-------------|-----:|
| Market | 480 | 294 | 94 | 5.1 | 142×111×105 | 3.0 |
| Market (Modern) | 694 | 374 | 159 | 4.4 | 151×123×126 | 2.5 |
| Research Lab | 696 | 376 | 160 | 4.4 | 121×90×160 | 3.3 |
| Lighthouse (CL) | 812 | 654 | 114 | 7.1 | 176×165×280 | 6.8 |
| Lighthouse (MD) | 824 | 633 | 119 | 6.9 | 176×165×289 | 6.4 |
| Temple | 831 | 480 | 181 | 4.6 | 178×217×260 | 2.1 |
| Shrine | 908 | 478 | 215 | 4.2 | 111×111×104 | 2.0 |
| Library | 999 | 537 | 231 | 4.3 | 121×161×160 | 3.5 |
| Workshop | 1,002 | 519 | 242 | 4.1 | 195×160×95 | 2.5 |
| Barracks (CL) | 1,131 | 549 | 116 | 3.9 | 91×108×70 | 1.6 |
| Stable | 1,322 | 663 | 328 | 4.0 | 214×195×102 | 4.0 |
| Amphitheater | 1,360 | 947 | 202 | 6.7 | 198×165×83 | — |
| Bank (Modern) | 1,547 | 786 | 376 | 4.1 | 164×164×137 | 2.1 |
| Airport | 1,627 | 1,015 | 303 | 5.4 | 306×381×148 | 7.8 |
| Power Plant | 1,949 | 1,256 | 368 | 5.3 | 223×268×166 | 5.1 |
| University (CL) | 2,081 | 1,494 | 365 | 4.5 | 304×244×209 | 6.1 |
| Cathedral | 2,216 | 1,216 | 410 | 4.4 | 240×217×351 | — |
| Mosque | 2,298 | 1,306 | 496 | 4.6 | 274×237×301 | 2.8 |
| Madrasa | 2,495 | 1,252 | 622 | 4.0 | 315×271×185 | 5.0 |
| University | 2,742 | 1,478 | 632 | 4.3 | 279×221×196 | 5.4 |
| Stadium | 2,712 | 1,460 | 626 | 4.3 | 260×273×154 | 4.8 |
| Granary (AN) | 2,868 | 1,624 | 526 | 4.4 | 185×145×108 | 2.1 |
| Factory | 2,989 | 1,744 | 595 | 4.8 | 325×304×139 | 7.1 |
| Granary (MD) | 4,022 | 2,170 | 862 | 4.2 | 212×179×157 | 4.2 |
| Zoo | 4,188 | 2,563 | 494 | — | 200×298×106 | — |

**Universal constant: average island size is 4.0–5.1 vertices across ALL buildings.** This is the fundamental unit of Civ 6 geometry — individual floating quads.

### Budget Tiers (Summary)

| Tier | Verts | Tris | Use For |
|------|------:|-----:|---------|
| T1 | 400–1,000 | 250–600 | Simple ancient/basic buildings |
| T2 | 1,000–2,000 | 500–1,300 | Standard buildings (target ~1,500v) |
| T3 | 2,000–3,000 | 1,200–1,800 | Complex/modern/religious buildings |
| T4 | 3,000–4,500 | 1,600–2,600 | District centerpieces |
| Wonders | 5,000–10,000+ | — | Not analysed but estimated |

### Total Game Geometry Count

| Category | Count |
|----------|------:|
| Base game geos | ~1,150 |
| PIL variants | ~350 |
| CON variants | ~130 |
| DLC geos | ~620 |
| **Total** | **~2,300+** |
