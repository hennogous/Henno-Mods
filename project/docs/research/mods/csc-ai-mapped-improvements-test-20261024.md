# Complete mapped-resource improvement incentives —24 October

Henno requested early incentives for Mines on Bakers/Tailors materials and all
other mapped resource improvements, including modded resources. He explicitly
requested in-game testing. This is one bounded initial1-to150 comparison with
15-minute updates; it does not resume the paused broader overnight investigation.

## Coverage and implementation

`material_mapped_improvement_forecast.sql` joins active Bakers/Tailors BASE/SPEC
TypeTags to Resources and Improvement_ValidResources. No hard-coded resource
catalogue or five-type allowlist defines coverage. Enabled compatibility mappings
and native valid custom improvements can qualify. A tag without a native valid
improvement does not invent legality. Duplicate Base/Spec/industry mappings do
not duplicate the early reward on one improvement.

Preserve the tested direct early80 Pasture/Camp/Plantation rows and conditional
resource-only Farm80. Add one resource-conditional80 modifier per previously
uncovered improvement type, with an OR set of its mapped valid resources. The
current snapshot covers20 unique pairs across Farm/Pasture/Camp/Plantation/Mine;
only Salt and Silver Mines were missing early coverage. Terrain-only Mines and
unrelated Iron Mines get no new80. Future mapped resources/improvement types are
generated automatically from active mappings when preparing a candidate.

The direct three-row paths are deliberately retained rather than replacing the
stronger-tested native forecasting route with a conditional route everywhere.
Their prior broad resource-bound scope is unchanged. The new additions are
restricted to mapped materials. Existing exact matching adjacent-Quarter80,
Quarter presence40, raw resource40/20 and care160/80/20 all remain unchanged and
can stack subject to their own native conditions. Unfinished Quarter support
uses the same current native collection behavior; this extension adds no new
completion prerequisite. No new flat Farm or Mine row is introduced.

Amounts are private planning units. New conditional rules retain the all-owner
diagnostic scope of the preceding forecast work. They can affect citizen
allocation; this is not an AI-only release deployment. SQL coverage is not proof
of conditional future-job projection, value application or an AI decision.

The SQL is unregistered in the normal source modinfo and installed only by this
declared test candidate. Candidate517 has NINE deltas over original510, two over
the preceding516 package (new SQL plus modinfo). No real yields, native legality,
resource mappings, AI work weights, research, grants or Builder orders changed.

## Worker availability decision

Keep worker policy unchanged for this comparison: improvementbase30, sustained
material-work demand up to60, general Builder preference50 and any-city Builder
contracts. Prior log intelligence already found many Find Available Unit and Move
Unit failures despite substantial Builder production. Empire-wide Builder counts
and charges are not proof that a particular job has a usable unreserved unit.

We do not need several more full games before investigating availability. Use
the same test's existing native tree/unit/contract logs and Builder observations
to trace job reservations, Find Available Unit/Move Unit outcomes, production
requests and actual unit operations. Distinguish a capacity shortage from unit
reservation, range/path/danger, job scope or request-legality failures. Do not
invent a hidden eligibility reason from a nearby Builder or failed node alone.
Add a targeted correction after identifying the failing decision path; do not
add another blanket production bonus simultaneously with this coverage change.

## Verification and native test

Ten focused SQL tests cover mapped Salt/Silver, terrain/unrelated exclusion,
modded resources/custom improvements, deduplication, idempotence, unchanged real
yields/legality/adjacent support and invalid/tampered definitions. Six actual
Lua5.1 controls cover new native-value observation parsing, missing incentives,
terrain/unrelated false rewards, modded names, care and pillage exclusions.
Three finite-driver checks retain canonical play, one initial save load,150 bound,
no direct world grants and save-before-failure. Total19 checks pass offline.
Full native-schema replay preserves all tables except seven requirement/modifier
tables; original direct early rows and worker policy remain byte/row-identical.

The native comparison uses preserved initial1 SHA
9a9e94c37183710663dae7b2a47db95c197f1e0ed571033e688c43927a9cefb2,
map830405/game940411, Ancient/Online/Prince/Continents Small, Tomyris0 and
Amanitore/Tamar/Genghis/Joao/Hojo. No new map/resource pass is generated. This
matches the preceding516 initial1 treatment timing. Optional external mods are
not newly enabled; dynamic fixture coverage is not a claim that every optional
resource pack was tested natively. CSC custom material mappings are present.

The first output run01 failed BEFORE Civilization launch while staging a missing
older companion SQL. No commands, loads, AI turns, foundations or purchases were
issued. Independent review preserves raw failure artifacts and proves original510
restoration. All nine source files were then staged/hash-verified. The sole native
test is run02; see active-run.json rather than treating directory ordinal as a
world count. Startup dispatch does not prove native advancement.

Initial source/fullworld/Gold/fresh setup units/native446/517 gates precede AI.
LIGHT full outcomes1/25/50/75/100/125/150 plus Builder5; economic and0% receipts
unchanged. New mapped-values snapshots read eligible isolated mapped Mines as
raw+80, excluded/unrelated/terrain Mines as raw only. Quarter/care/pillaged rows
are recorded separately. A missing positive control is UNOBSERVED. A failed
control preserves an exact save before stopping. Review actual Mine job scores,
reservations, native operations, working supply, harvest/district competition and
repair separately. No extra per-turn deep profiling or native competitor client.

Independent final auditor: `material_mapped_start1_audit.py`; log reader:
H/mapped-improvements150-review.py. Both are offline; repair schema assumptions
without replaying native games. Expected fresh745 research observations minus
explicit defeats. Recovery is allowed by default but lost observations must stay
missing, with accepted timeline and financial one-shot provenance reconciled.

After actual150/job+supervisor complete0, normal Menu exit/allCiv absent and
original510/144preferences/autostartfalse verification, publish actual outcomes
and a descriptive comparison. Service/customer links are not observed monetary
payments. Then delete only the new monitor and record the actual receipt. All
old studies/deleted monitors remain closed, broader goal paused, no extension.


Native startup addendum: run02 SQL/native20 coverage and exact initial1 gates passed, then the readonly observer failed on ImprovementModifiers.ModifierId. The native Lua field is ModifierID (SQLite column identifiers are case-insensitive; Lua row fields are not). The reader and actualLua51 fixtures were corrected only after owners exited. Independent review verifies0AI advance/economic effects, unchanged initial world and original510/prefs restoration. Current sole outcome-test branch is run03/supervisor9652; read active-run for current worker/native clocks. Old two startup branches remain archived and contribute no experimental outcomes. Gameplay/worker policy unchanged.

AUTHORITATIVE startup independently VERIFIED: actual native7, supervisor9652/worker9868/DX12Civ7860, 231 unchanged pins,517 runtime hashes/native446/full source1 startup parity and all20 mapped SQL pairs. Corrected native ModifierID reader ran at1; no naturally built positive Mine control yet, so application and AI decision benefit remain PENDING. Keep worker policy unchanged, all sources frozen and worker exclusive.


## Audited150 and human inspection override

The sole outcome branch run-03 reached native150 and both original controllers exited0. Independent offline audit passed: 231 source pins, 446 native tables, all 745 unique AI research observations (1..149), exact checkpoint coverage, economic receipts and zero-progress foundations. No additional map was generated. The two earlier staging/reader attempts contributed no AI outcomes.

At150 the five AI players had31cities/324population,45Quarters/44complete,40producer buildings,15functioning producers including4Both,15structural sales links and14Service-property instances. These links and flags do not measure actual monetary transactions, which remain UNOBSERVED. Seven assisted foundations were placed, six complete by150 and the turn127 Tailors site still unfinished. Seventeen acquired tiles cost830Gold:448AIown funds plus382fallback donations. Backend remains assisted quoted city assignment, not native AI PURCHASE.

New mapped Salt/Silver Mine application remains UNOBSERVED: zero eligible isolated positive controls across closed checkpoints. Forty-seven excluded Mine control observations correctly received no extra value. Existing resource-Farm value application has28positive control observations and213terrain-zero controls. Equal nominal80 incentives do not demonstrate equal forecasting or behavioral effectiveness.

Native Builder logs contain292build/28repair/8harvest/6remove-improvement START records, not unique completed jobs. Preservation remains mixed: confirmed adjacent material harvests occurred despite care signals; incentive application is not proof that the harvest scorer prices lost supply-chain value. Worker policy stayed unchanged. Comparison to prior516 is descriptive, same-map and not independent replication.

## Human inspection override

After completion the worker normally exited Civ and verified original510/144preferences/autostartfalse. The human then requested leaving150open; that request arrived after automatic closure. A separate inspection loader is reopening the exact final save SHA9780226b33ec616a6588e6da097c71aaab33fa1ca425a4bee7964dbc0c096f7b under archived candidate517, without autoplay, planner actions, purchases or reconstruction. Read human-inspection-150/status.json for actual readiness. Original completed run/audit/restoration receipts are preserved; they describe the state BEFORE reopening. Current candidate517 installation and inspection preferences require cleanup only after the human finishes and Civ is absent. No extension beyond150 is authorized.
