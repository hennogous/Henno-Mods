# Workshop AI guidance without CE

CSC offers one setup option, **Advanced CSC AI planning**. In a single-player game with compatible CE, its default runs the economic planner alongside Civ's normal AI. Turning it off skips the planner. A game without CE uses the stock AI controls below. Ordinary gameplay adjacencies, transaction payouts and Service requirements use their existing definitions in every mode.

| Decision | Input used by the lightweight candidate |
| --- | --- |
| Place a mapped customer next to a Quarter, in either build order | One private adjacency yield per neighboring partner. The SQL derives both directions from building transactions, sales and provider tags, including district replacements. City settlement and generic Wonder tiles are excluded. |
| Place a Quarter near working material infrastructure | One private adjacency yield for selected neighboring improvement families. At least one Base must use the improvement. The family qualifies when a third of its mapped resource types are Base or half are Base and Spec together. An improvement which can occupy ordinary terrain or features requires two neighbors. In the standalone catalogue Bakers sees Farms (two), Pastures and Plantations. Tailors sees Pastures. |
| Recruit a Builder | A +10 preference in the stock unit-request list when a mod has not already supplied that Builder row. The Build City Improvement tree can recruit from other cities. Civ selects the job, unit and route. |

The material cue deliberately uses an observable feature of the map. A Pasture can hold Cattle, Sheep or Horses. Bakers and Tailors each benefit from one of those resources. A Cotton Plantation can feed Tailors but the family also covers thirteen other resources, so a lone Plantation gives Tailors no private adjacency in the standalone catalogue. The outcome measure counts the actual resource and working improvement.

## Research behind the choices

City Lights supplies a local example of stock improvement adjacency. RHAI5 uses the stock unit-request list in `core/Ops/RH_Ops.sql`. AI+ uses the Required City parameter on the Build Unit node of the Build City Improvement tree in `behaviortrees.xml`. Real Strategy's `base/RealStrategy_Anti.sql` illustrates gating a player's preference lists through a Lua strategy condition. That is a candidate for changing broad investment priorities when a shortage is observed.

The Ghidra trace shows that the stock district valuator reads each registered yield, applies the city's weight and also considers eligible competing districts on the same plot. A +1 private adjacency can swing a close location decision. Its final utility depends on both the city and the alternative uses of the land. [Reusable engine trace](https://github.com/hennogous/civ6-ai/blob/8e69bb6/references/engine/modding-controls.md#where-a-registered-adjacency-enters-district-valuation)

## Matched game comparison

The two preselected Continents map seeds are 171124601 and 171124605 on Small/Online. Compare stock CSC, the lightweight guidance and the full planner, always with ordinary AI leaders. The primary outcome is completed Quarters with a working adjacent Base and a completed mapped customer, counted once per Quarter. Track active Service links, Quarter foundations without usable owned Base, loss of the last supplier and popup-free turn times from the same stock automation clock. Retain the final saves for map inspection.

The first no-CE smoke test reached turn 25 and saved successfully. Only the pinned Firaxis XP2 core loaded. Sixteen Quarter-to-customer adjacency links were present while the full planner was absent, and the observer recognized 33 Service attachments. This test preceded the material-family cue. The five AI empires had completed no Quarters by that turn. The full games measure placement quality and Service operation.
