# CSC Building Config Schema

A building is a **spec dict** with three sections: `volumes`, `features`, and `meta`.

---

## `volumes` — the massing

A list of rectangular volumes that make up the building's silhouette.
Each volume can have its own roof. Volumes are merged into one mesh.

```json
"volumes": [
  {
    "id": "main",
    "x": -60, "y": -45,       // bottom-left corner (world space)
    "w": 120, "d": 90,         // width (X), depth (Y)
    "h": 65,                   // wall height
    "roof": {
      "type": "pitched",       // pitched | shed | flat | hip
      "height": 38,            // ridge height above wall top
      "ridge_offset_y": -8,    // shift ridge toward back (asymmetry)
      "overhang": 8            // eave overhang beyond walls
    }
  },
  {
    "id": "wing",
    "x": 5, "y": -135,
    "w": 70, "d": 50,
    "h": 48,
    "roof": {
      "type": "pitched",
      "height": 22,
      "ridge_offset_y": 0,
      "overhang": 5
    }
  }
]
```

## `features` — details attached to volumes

Each feature targets a volume by `volume_id` and a wall face by `face`
(`front`=+Y, `back`=-Y, `right`=+X, `left`=-X, `top`).

Position `cx`, `cy` is relative to the volume's centre on that face.
`z` is absolute world Z.

```json
"features": [
  {
    "type": "window",
    "volume_id": "main",
    "face": "front",
    "cx": -38, "z": 34,        // offset from volume centre, absolute Z
    "w": 20, "h": 24, "depth": 5
  },
  {
    "type": "chimney",
    "volume_id": "main",
    "cx": 22, "cy": -15,       // offset from volume centre in XY
    "w": 16, "d": 14,
    "base_z_frac": 0.55,       // start at 55% of wall height
    "top_above_ridge": 25,     // how far above roof ridge
    "cap_overhang": 3.5, "cap_h": 5
  },
  {
    "type": "dormer",
    "volume_id": "main",
    "face": "front",
    "cx": 0,                   // centred
    "z_frac": 0.3,             // 30% up the roof height
    "w": 26, "d": 9, "h": 20,
    "roof_h_frac": 0.45        // shed roof drops to 45% of dormer height
  },
  {
    "type": "step",
    "volume_id": "main",
    "face": "front",
    "cx": 0,
    "w": 56, "d": 10, "h": 6
  },
  {
    "type": "trim_band",
    "volume_id": "main",
    "z_frac": 1.0,             // at wall top
    "overhang": 9.5, "h": 5, "rise": 2
  }
]
```

## `meta`

```json
"meta": {
  "name": "CSC_BKR_Bakery_01",
  "found_depth": 20,
  "found_overhang": 5
}
```

---

## Roof types

| type | params |
|------|--------|
| `pitched` | `height`, `ridge_offset_y`, `overhang` |
| `shed` | `height`, `slope_dir` (+Y/-Y/+X/-X), `overhang` |
| `flat` | `overhang` |
| `hip` | `height`, `overhang` (all 4 sides slope to central point) |

---

## Vertex group conventions

| group | contents |
|-------|----------|
| `Foundation` | all verts below Z=0 |
| `Walls` | verts 0 ≤ Z ≤ max wall height |
| `Roof` | verts above max wall height |
| `VERTEX_KEYS` | all verts (Civ animation support) |
| `{BUILDING_NAME}` | all verts (Civ export convention) |
