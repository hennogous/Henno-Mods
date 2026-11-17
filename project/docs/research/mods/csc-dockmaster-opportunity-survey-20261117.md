# Dockmaster opportunity survey — requested scope

17 November2026. Henno requests a survey of the current Continents map and
available earlier worlds before changing customer bonuses or material placement.
The current250-turn game continues unchanged. Use recorded coast captures where
available, then shared-controller zero-turn saved-world inspections after the
current worker closes; never open a competing console session.

Count distinct feasible Base–Tailors–Harbor layouts, representing the eventual
Workshop/Lighthouse exchange. Raw material-within-two-of-water counts are only
the broad first filter. Distinguish sea from lakes; legal empty/usable Quarter
and Harbor footprints; resource/improvement viability; ownership/city reach;
already-occupied footprints; unlock/capacity gates and Harbor ordinary Gold
adjacency versus its best alternative. Group alternative plots sharing the same
material cluster/city so overlapping hex combinations do not inflate the number
of independent chain opportunities. Existing built configurations and plausible
future layouts belong in separate counts. Buildings/unlocks can follow normally;
surveying their possibility does not establish a working Service.

Link the layouts to actual Quarter/customer proposals, native comparisons,
district/building execution and missing prerequisites. Include existing Tailors
placed inland despite possible coastal alternatives. Preserve map/source dates
and the distinction between a late-world obstruction and original map geography.

## Existing implementation and earlier evidence

`CSC_MaterialMapCore.lua` version4 already emphasizes Tailors:2× Base-only sites,
4× both-material sites and an abundance-scaled both-site floor. Its density pass
maximizes the gain in supported Quarter centers, with native resource eligibility,
continental palettes, start/center protection and sparse global/continental
budgets. It has no coastal-layout objective. The production pass runs once during
initialization and uses its own deterministic RNG.

The earlier customer-first Continents survey is archived under
`Desktop/Codex/csc-ai-customer-first-continents-20261116/coast250-*`. It found11/21
Tailors Base deposits geometrically near sea and nine AI-owned, but practical
options were fewer: one legal owned layout offered Harbor0 versus best3; another
had unowned water/full capacity; a third was lake-only. These motivate counting
good complete layouts rather than assuming absent Dockmasters imply absent
materials. The maintained query/driver are `tailors_coast_survey.lua/.py`.

If the new survey finds scarcity, a later design experiment should first direct
part of the existing material-assistance budget to a few useful coastal layouts,
prioritizing Base material. Specialty is additional value; it cannot substitute
for the Workshop's Base input. Prefer naturally viable Harbor sites rather than
overbidding for weak ones. No resource-placement or bonus change is authorized
by this survey note itself; the running comparison must retain its frozen rules.
