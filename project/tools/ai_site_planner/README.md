# Offline CSC site planner

Fresh implementation after retirement of the earlier tuning. Imports no old
planner, heuristic, subsidy, foundation, game-control or native-hook module.
It reads copied facts and produces review artifacts only.

The first mechanics profile supports **Tailors**. Bakers and other Quarters
require independently checked profiles; unsupported types fail explicitly.

```text
python -B -m unittest discover -s project/tools/ai_site_planner -p test_evaluator.py -v
python -B project/tools/ai_site_planner/report.py --output OUTPUT_DIRECTORY
```

Outputs: `review.json`, `review.md`, and standalone `review.html`. The HTML offers
27 precomputed combinations of horizon, yield emphasis and unquoted-building
cost assumptions, using the same Python evaluator. It needs no server/network.
The handbook build also publishes it at `/ai/static/site-planner-review.html`.
`--markdown PATH` also writes the generated human-readable report to a chosen
repository destination. Canonical report:
`project/docs/research/mods/csc-ai-site-evaluator-20261103.md`.

## Input and provenance

`fixtures/captured_sites.json` contains copied facts from four closed captures,
their external locators/SHA-256, and an explicit current-mechanics profile with
LF-normalized source hashes. It contains six new Tailors alternatives at110
and38 existing Tailors observations from two historical150 worlds. Historical
treatments remain declared; neither those worlds nor their production figures
are called clean current-game references.

`build_fixture.py --shadow PATH --census PATH --candidate PATH --reference PATH
--output PATH` rebuilds the copied fixture from the original files. It reuses
observed objects, mapping/ownership/visibility, material/producer/customer states,
and the native river getter count. Old computed yields, private guidance values,
rankings and policy decisions are not imported. Exact source pointers and hashes
remain with each case. No external captures are needed to run the committed tests
or replay the committed fixture.

## Model

Compare valid building bundles, including Workshop+Fashion without Tailor.
New districts use the captured district cost when available; other unquoted
costs use a declared nominal-cost multiplier. Construction is serial at fixed
captured production. A component contributes only after the required completion.
For each yield, keep a separate component ledger:

```text
component total = per-turn amount × max(0, horizon − ready turn)
review utility = weighted modelled yields − weighted new construction cost
upgrade value = plan utility − utility of retaining the observed state
```

Default review weights P1/G0.5/C1 are assumptions, not calibrated native values.
Missing positive and negative terms make the result neither an upper nor lower
bound. Retain/defer is0. No `deltaQ8` or deployable native policy is produced.

Important distinctions:

- Material deposits can give district adjacency before improvement. Only owned,
  revealed, district-free working supply feeds modeled material transactions.
  Worked-tile income needs a working citizen; missing citizen evidence gets no
  realised tile-yield credit. Supply itself can work on an unworked tile.
- Ordinary customer sales are not material-gated. Services have their own supply,
  customer and unlock gates and remain unpriced unless a review value is explicit.
- Current Stage3 engine coefficient is0.105; Stage4 uses each customer's own
  floor(population/5), not pooled populations. Direct Market/Temple branches in
  one city remain distinct. This is not an exact displayed-yield simulator.
- Future customer branches need a specific captured plot-potential observation,
  explicit cost/timing, declared ordinary yields and conflict assessment. Future
  material work needs its own mapped owned footprint, cost, timing and conflict
  assessment. Neither is reported as observed completion or executable permission.
- The agreed Base-supply ambition is reported separately from partial cashflow.
  A positive conditional result without a Base path is not a proposed commitment.
- Pillaged or unfinished investments need actual repair/remaining-work inputs;
  the evaluator does not make those free. Full repair policy remains later work.

Known omissions: policies/optional integrations/replacement coverage, specialists,
trade demand, amenity/growth feedback, actual queue delays, future unlock evidence,
alternative land/district/military value, Builder travel/safety and a mapping to
native utility. Read the report before interpreting a number as a recommendation.

The evaluator supports the next **review** of good-site logic. Native multi-entry
policy publication, refresh, persistence, actual AI choice and economic benefit
are separate roadmap phases.

## Simple full-adjacency native policy

The separately authorized first native placement policy is in
`adjacency_policy/`. It reads the scanner from main CSC
`Lua_UI/AI/CSC_AI_AdjacencyScan.lua` and evaluates Bakers and Tailors with the loaded shared
adjacency rules, including planned first-Mill terrain/river bonuses. It promotes
one highest-scoring >=4 Production+Gold pair per city, without banning other
sites. That v1 result is preserved. The current v2 adds a soft penalty for every
observed sub-4 pair, while retaining the same good-site promotion. Each missing
point subtracts65,536 Q8, capped262,144; these are experimental priorities rather
than yield prices. Negative values remain selectable. Native zero/invalid values
are preserved, and negative adjustments stop at-1,048,576 Q8 to leave room for
the later1.5 district-preference factor without creating a no-result sentinel.
Tables now hold up to4096 exact pairs; windows allow4096 writes/16384 records.
See [the penalty investigation](../../docs/research/mods/csc-ai-placement-penalties-20261103.md).
This remains a priority experiment, separate from the investment utility above.

Read [the policy and Online100 evidence](../../docs/research/mods/csc-ai-adjacency-policy-20261103.md)
before running it. Its driver uses `full_game_controller` and `NativeSession`,
with exact native identity/fingerprints, original-AI scope and normal cleanup.
A machine-interruption recovery uses an explicitly pinned supported native save
and retains the original run's player identities and preferences. Turn100 is a
hard upper bound; importing a module never launches or attaches to a game.

Offline checks:

```text
python -B -m unittest discover -s project/tools/ai_site_planner/adjacency_policy -p test_policy.py -v
python -B project/tools/ai_site_planner/adjacency_policy/test_scanner.py --dependencies LUA_TEST_DEPS --output NEW_RECEIPT.json
python -B project/tools/ai_site_planner/adjacency_policy/run_synthetic.py --dependencies FRIDA_17_24_3_DEPS --output NEW_RECEIPT.json
```

`analyze_adjacency_trial.py --base EVIDENCE_BUNDLE --output REVIEW.json` is
read-only. It joins accepted scans, preceding-site scores, promotion history,
physical observations, native windows and timestamped operation journals.
Original interrupted intervals remain partial; no unseen events are fabricated.
The normalized fixture/evaluator remains runnable independently of these tools.
