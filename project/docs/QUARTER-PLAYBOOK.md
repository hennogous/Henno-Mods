# CSC — New Quarter Playbook

Standard checklist for implementing each new Quarter after Bakers'. Use Bakers' as the reference implementation throughout.

---

## Phase 1: Design

- [ ] **Review Quarter design doc** (`docs/content/quarters/<quarter>.md`)
  - Identify main yield focus
  - List BASE and SPEC resources
  - Map customer districts (who gets adjacency bonuses)
  - Map stage 2/3/4 building names, unlock techs/civics, costs
  - Identify thematic variances from Bakers' framework:
    - Stage 2 mechanic variant (Bakers' has Water Mill/Wind Mill split — is there an equivalent?)
    - Stage 3 customer district + building (Bakers' → Commercial Hub / Market)
    - Stage 4 customer district + building (Bakers' → Entertainment Complex / Zoo)
    - Stage effect details per civic unlock
    - Specialist building placement (which external district?)
    - Trade route yield type
  - Note any unique mechanics not in the framework (e.g. Tailors' naval production bonus)
- [ ] **Update design doc** if needed — resolve any TBDs before coding
- [ ] **Cross-check materials table** (`docs/content/reference/materials.md`) for resource mappings

## Phase 2: Gameplay SQL

All files in `Civ Supply Chains\Data\`.

- [ ] **Create `CSC_Q_<QUARTER>.sql`** from Bakers' template
  - Substitutions needed:
    - `BAKERS` → `<QUARTER>` in all identifiers
    - Main yield type (`YIELD_FOOD` → `YIELD_<X>`)
    - BASE resource list (TypeTags)
    - SPEC resource list (TypeTags)
    - Improvement types for stage 1 (which improvements feed this Quarter?)
    - Stage 2 building name, prereq tech/civic, thematic variant
    - Stage 3 building name, prereq tech/civic
    - Stage 4 building name, prereq tech/civic
    - Customer district adjacencies (both directions)
    - Customer district unique replacers (e.g. Suguba for Commercial Hub)
    - Stage effect modifier details (growth/housing/tourism → whatever this Quarter does)
    - Stage effect prereq civics
    - Specialist building types + target districts
    - Trade route yield types
    - Population scaling customer buildings (Zoo/Ferris → this Quarter's equivalent)
    - Building costs, maintenance, citizen slots, entertainment values
    - Great Person class for stage 3/4
    - Regional range on stage 4 if applicable
  - Handle unique mechanics not in the template
- [ ] **Create `CSC_Q_<QUARTER>_MC_MODE.sql`** if M&C integration differs from Bakers'
- [ ] **Review shared requirements** — some `REQSET_CSC_*` and `REQ_CSC_*` are reusable across Quarters (e.g. `REQ_CSC_PLOT_ADJ_TO_OWNER`, `REQ_CSC_PLOT_ADJ_TO_RIVER`). Don't duplicate, only create Quarter-specific ones.
- [ ] **Civic description UPDATEs** — add the new Quarter's unlock text to relevant civics

## Phase 3: Localization

Files in `Civ Supply Chains\Text\`.

- [ ] **Add entries to `CSC_QUARTERS_TEXT.sql`**
  - District name + description
  - Building names + descriptions (all stages + specialists)
  - Adjacency descriptions
  - Stage effect descriptions
  - Specialist building names
  - Civic unlock text
- [ ] **Add entries to `CSC_QUARTERS_PEDIA.sql`** — civilopedia pages
- [ ] **Update `CSC_RESOURCES_TEXT.sql`** if new custom resources are introduced

## Phase 4: .modinfo

- [ ] **Add SQL file actions** to `Civ Supply Chains.civ6proj` / `.modinfo`
  - Gameplay SQL → UpdateDatabase action
  - Text SQL → UpdateText action (or appropriate load order)
  - MC MODE SQL → conditional on game mode if applicable

## Phase 5: Art

### 3D Assets
- [ ] **Assign kit geometries** — which of the 6 reusable building models for each stage?
- [ ] **Create Quarter-specific materials** (.mat) — roof color, thematic textures
- [ ] **Create Quarter-specific textures** (.tex/.dds) — atlas with Quarter's color scheme
- [ ] **Add props** per building for uniqueness (manual Blender work)
- [ ] **Export** — Blender → .cn6 → CivNexus6 → .fgx/.geo
- [ ] **Create .ast files** — wire geometry + material + texture per building
- [ ] **Create ArtDef entries** — point game concepts to assets
- [ ] **Create/update .xlp** — package entries for new assets
- [ ] **Cook** — ModBuddy build → .blp

### 2D Assets
- [ ] **District icon** — all required sizes (from GIMP template)
- [ ] **Building icons** — all stages, all required sizes
- [ ] **Strategic view sprites** — if applicable
- [ ] **Icon SQL** — wire icon references in gameplay SQL

## Phase 6: Integration

- [ ] **Cross-Quarter adjacencies** — if this Quarter interacts with other Quarters (e.g. Brewers' ↔ Bakers'), wire both sides
- [ ] **Verify shared modifier types** — `MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER` etc. already registered
- [ ] **City Lights compatibility** — add Rural Community / Urban Borough adjacencies if supported
- [ ] **M&C compatibility** — verify Industry/Corporation bonus scaling

## Phase 7: Test

- [ ] **Build mod** — ModBuddy, resolve any build errors
- [ ] **Start game** — verify no database errors in logs
- [ ] **Check db dump** — verify all entries inserted correctly
- [ ] **Place Quarter** — verify adjacency bonuses display correctly
- [ ] **Build stage 2** — verify transactions with adjacent improvements
- [ ] **Build stage 3** — verify citizen scaling, Market interaction
- [ ] **Build stage 4** — verify specialty materials interaction, regional amenity
- [ ] **Civic unlocks** — verify stage effects appear at correct civic
- [ ] **Specialist buildings** — verify they spawn in correct external districts
- [ ] **Trade routes** — verify yield bonuses
- [ ] **Icons** — verify all sizes display correctly in all UI contexts
- [ ] **Civilopedia** — verify entries are correct and formatted
- [ ] **M&C mode** — verify Industry/Corporation bonuses if applicable

## Phase 8: Polish

- [ ] **Balance pass** — yields feel right relative to other Quarters and vanilla districts?
- [ ] **Description pass** — all tooltip text clear and accurate?
- [ ] **Update design doc** — capture any changes made during implementation
- [ ] **Commit** — meaningful commit message, push to GitHub
- [ ] **Update docs site** — if design doc changed, Quartz rebuilds automatically via GitHub Actions

---

## Notes

- Many shared requirements and modifiers exist from Bakers'. Check before creating duplicates.
- The population scaling pattern (temp `CSC_PopulationLevels` table) is reusable as-is — just swap the modifier/building names.
- River access flag pattern (Water Mill / Wind Mill) is Bakers'-specific — not all Quarters have this. Check the design doc.
- Stage effect prereq requirement sets may need Quarter-specific versions if the prereq civic differs.
