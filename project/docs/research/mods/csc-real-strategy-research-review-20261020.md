# Real Strategy review — 20 October 2026

Reviewed read-only Workshop1617282434, Infixo Real Strategy2.3.1. Native source and installed CSC gameplay were not changed; no games launched.

## Research findings

RealStrategy_Naval.sql lines64-76 defines native Strategies/StrategyConditions with Call Lua Function; lines103-115 register Civics list RSTNavalCivics and attach it to STRATEGY_NAVAL; line134 favors CIVIC_NAVAL_TRADITION with Favored1/Value0. RealStrategy.lua ActiveStrategyNaval returns a condition boolean through GameEvents. This is the same mechanism as RH/our clean stock/custom comparison, not a missing alternative research API. No SetResearchingTech/SetProgressingCivic calls or research setters were found in the reviewed Lua.

Many Technologies entries explicitly say BUGGED (e.g. Main.sql432). Author's primary Systems wiki distinguishes Technologies Favored1 reported broken from Civics Favored0 reported inert, while positive civic favoring is described as working. Treat these as historical author findings, not proof for the current build. Some civic entries are retained despite acknowledged inert negative preferences; rows existing in a successful mod do not prove each row works.

Main.sql148-158 and PseudoYields wiki describe residual research valuation plus a civic/technology pseudoyield contribution multiplied by percentage bias. This concerns PseudoYields-system bias, not a documented interpretation of Value on Civics entries. Yields are also described as affecting research scores. Neither global PSEUDOYIELD_CIVIC nor general Culture bias selectively targets Naval Tradition.

## Additional offline audit of completed CSC study

Evidence: C:/Users/Shadow/Desktop/Codex/csc-ai-clean-strategies-20261020/research-candidate-score-audit.json.

AI_GovtPolicies.csv contains Civic candidate score rows; AI_Research.csv contains Tech rows. Analyzed turns71-150, players1-5. Sham/stock/custom each have5002unique civic candidate keys. Stock and custom each match sham on every key and ordered score/tail values, with zero missing or extra keys. All327Naval candidate keys match. Tech records likewise match on16682keys, but this is expected in a civic-only treatment. These are logged scores at CSV precision, not all hidden internal fields. Thus the civic treatment produced no logged candidate valuation effect, strengthening the previous identical-choice result without establishing universal engine nonconsumption.

## Recommended next work (not launched)

First reproduce an author-reported positive civic preference in its original context, using disposable Real Strategy-controlled paired cases differing only by one favored item in an active existing list (government-unlock civic and/or Naval Tradition). Check actual candidate scores and a natural decision; do not change current civic or grant progress. Keep all other Real Strategy data identical. If this responds, reduce that working context to find the minimum CSC integration. If it does not, historical claims do not validate the current build.

Separately calibrate a strong PSEUDOYIELD_CIVIC or general yield bias against the research scores themselves. This distinguishes native valuation responsiveness from named-item preference responsiveness; it is a diagnostic, not a targeted gameplay fix. Before longer games require a measured score response. If only native unlock valuation responds, investigate whether CSC Service value can be exposed through engine-visible unlock effects; that remains a hypothesis, not a proven method. Direct Lua research selection is a separate explicitly controlled fallback, not preference guidance.

## Builders and materials

Main.sql105 uses improvement default4 (comment13.5too much) versus our90. PseudoYields wiki distinguishes improvement demand/contracts from Builder construction speed after contracting. Main.sql927/953/973/990 adjusts improvement bias by danger/war/peace. These motivate future backlog-aware tuning, not an immediate baseline change. Settlement Specific Resource entries are city-location scoring, not Quarter placement; no new per-Quarter ResourceModifiers mechanism was found.

## Primary references

- https://steamcommunity.com/sharedfiles/filedetails/?id=1617282434
- https://github.com/Infixo/Civ6-Real-Strategy/blob/master/base/RealStrategy_Naval.sql
- https://github.com/Infixo/Civ6-Real-Strategy/blob/master/base/RealStrategy_Main.sql
- https://github.com/Infixo/Civ6-Real-Strategy/wiki/Systems
- https://github.com/Infixo/Civ6-Real-Strategy/wiki/PseudoYields
