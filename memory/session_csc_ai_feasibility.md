# CSC AI feasibility — 11 October 2026

Henno wants AI guidance for Quarter placement beside BASE + SPEC materials and
sales districts, later customer district placement, material improvements, and
Service-oriented Quarter selection. This turn is feasibility research; no
gameplay implementation or live AI trial was performed.

Evidence inspected:
- Installed civ6-gameplay `references/ai-system.md` (RH v4.21-derived notes).
- Live CSC bundled adjacency scripts/processor/modifiers and
  `project/docs/integrations/csc-adjacencies.md`; current Bakers/Tailors SQL and
  public Quarter design files. Installed CSC skill has stale MAB dependency/
  processor pointers; live repo and supplied AGENTS instructions supersede them.
- Firaxis base gameplay schema and expansion data. Native
  `Adjacency_YieldChanges` has district/improvement/terrain/feature selectors,
  generic resources and resource classes, but no specific ResourceType or CSC
  TypeTag selector. No expansion addition of AdjacentResourceType found.
- Public Roman-Holiday/RHAI source, commit
  `91584816e88f458461ae132e30d6860adba97eed` (28 October 2024; repository explicitly
  marked old version). Read-only checkout:
  `C:\Users\Shadow\Desktop\Codex\csc-ai-feasibility\RHAI-reference`.
  `core/Strategies/Internal_Strat2.sql` uses native District_Adjacencies with
  YIELD_RH_PLACEMENT and hidden-tech gates to encourage placements in both
  directions (e.g. IZ beside Aqueduct and Aqueduct beside IZ).
  `Relic_Strat.sql` registers the yield and its AI weight. This proves an authored
  technique exists, not measured CSC behavior or current RHAI compatibility.
- Infixo's Systems wiki warns blanket favored districts/buildings can become
  ubiquitous; PlotEvaluations is settlement, not a generic district tile hook.

Findings / uncertainty:
- CSC UI appends custom preview strings; gameplay writes bit properties only on
  existing, completed districts. UI preview is not a native prospective AI score
  callback. Actual yield tests do not establish AI placement valuation. Treat
  native AI awareness of custom prospective bonuses as unproven, likely absent.
- Native virtual-yield district-to-district guidance is a strong initial
  prototype for both Quarter -> existing customer and customer -> Quarter.
  Own CSC identifiers; preserve actual economic yields; calibrate strength and
  native UI visibility. No need for an RHAI dependency.
- Exact BASE/SPEC pairing is the hard part. Farm/plantation/pasture proximity is
  an approximate signal and misses unimproved resources and class combinations.
  Counting exact candidates in Lua is easy; feeding that count to prospective
  native AI evaluation is unproven. Properties alone are not an AI scoring hook.
- Builder availability and visible tile gains can help; remote Quarter/Service
  gains from improvements are not confirmed to be valued prospectively. Broad
  builder/improvement boosts do not encode adjacency-specific task priorities.
- Strategy/era/leader preferences and virtual benefit yields can approximate
  Quarter/Service value, but do not create a full multi-step planner. Services
  are automatically granted; guidance should favor their enabling buildings and
  useful sites, not instruct AI to construct hidden Service buildings.
- Shared tags/material config should supply guidance generation; respect optional
  resources/settings and unique replacements. Test standalone CSC before optional
  RHAI compatibility tuning; avoid replacing global AI weights wholesale.

Suggested next work: controlled AI A/B fixture for prospective custom adjacency
visibility, then native virtual-yield sales adjacency in both build orders;
separately probe exact material score transport and builder remote-gain awareness.
Use AI_CityBuild.csv/AI_Planning.csv plus legal-site choices, improvement decisions,
and actual Service activation. Compare current-yield ties where one site has both
BASE and SPEC and another only repeated BASE. No tests executed this session.
