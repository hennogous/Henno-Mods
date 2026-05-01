# CSC Building Shape Dictionary

## The Marble Rule
> "If you dropped a marble on it, would it rest or roll? **It should roll!**"
— Official Civ 6 art guidelines

No flat tops. No 90° wall-to-roof transitions without a break.
Everything that faces skyward should shed a marble — pitched, curved, or chamfered.

## Shape Hierarchy (official)
1. **Big shapes** — affect silhouette. Must read clearly at 256px. Roof mass, chimney, tower.
2. **Intermediate shapes** — add secondary read. Dormers, bays, trim bands, steps.
3. **Small shapes** — texture/material detail only. Window mullions, brick courses, tile lines.

Rule: never let small shapes fight big shapes. If it's not readable at thumbnail size, it's small.

## Approved Roof Types (marble-safe)

| type | notes |
|------|-------|
| `pitched` | Default. Ridge must be offset or one slope steeper than the other — never perfectly symmetrical. |
| `hip` | All 4 sides slope. Works well for towers and corner volumes. |
| `shed` | Single slope. Good for annexes, bakehouse wings, market stalls. |
| `gambrel` | Double-pitched per side (barn roof). Adds height without bulk. TODO: implement. |
| `conical` | Turret/tower cap. TODO: implement. |
| `dome` | TODO. Use sparingly — reserved for grand civic buildings. |

❌ `flat` — never use on a primary volume. Flat roofs fail the marble test.
✅ `flat` — only acceptable on a covered walkway or recessed inner courtyard.

## Volume Proportions (Civ style)

- **Tall and narrow beats wide and squat.** Civ buildings punch upward.
- Recommended W:H ratio: 1:0.6 to 1:1.2 (wall height = 60–120% of width)
- Roof height: 40–60% of wall height. Steep roofs read better at game scale.
- Wing volumes: 60–75% of main volume height. Never equal — that reads as two buildings.
- Foundation: hidden in-game. Keep thin (15–20 units).

## Feature Placement Rules

- **Chimneys:** never centred. Off-axis 20–40% from centre. Multiple stacks = different heights.
- **Dormers:** max 1–2 per roof slope. Centred on slope third, not dead centre.
- **Steps:** offset from door centre by 10–20% to imply a life lived asymmetrically.
- **Windows:** groups of odd numbers (1, 3) read better than even. Vary height slightly.
- **Trim bands:** at eave line only — not mid-wall. They separate roof mass from wall mass.

## Exaggeration Guide

These are toy models. Push proportions past realism:
- Chimneys: 30–50% taller than you'd expect
- Roof pitch: 10–15° steeper than real equivalent
- Eave overhang: 1.5–2× real scale
- Step rise: exaggerate height (makes entrance readable)
- Dormer: slightly oversized relative to roof

## TODO: Shape Vocabulary to Implement

- [ ] `gambrel` roof type
- [ ] `conical` roof type (tower caps)
- [ ] `bay_window` feature (projecting bump with own mini roof)
- [ ] `arcade` feature (arched opening series)
- [ ] `buttress` feature (structural diagonal against wall)
- [ ] `bell_tower` volume preset
- [ ] `market_stall` volume preset (open-sided shed)
