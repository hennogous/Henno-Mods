# Current CSC AI status

**Current instruction: outcome tests stopped; REA investigation, 13 November.**
The fresh lifecycle run stopped at160 through the shared controller, exited0
and restored preferences. Turn150 is saved. No further game or tuning change.
REA on the actual updated DLL confirms a native reservation is a threshold,
while our complete-value writer skips every nonempty reservation ID. Sinope's
logs show Farm163 reserving its tile on165, then Quarter1736 winning on166
while our accepted bid was about−60 utility. This is a concrete coverage
mismatch and a strong explanation of that miss; the exact native rejecting
guard was not logged. Owned future candidates also have a separate current-
BUILD-target coverage gap. Fix/verify delivery before calibrating scores.
[Native mechanism, evidence and limits](../research/mods/csc-ai-reservation-write-gap-20261113.md).

**13 November outcome and active investigation, Problems 1.6/1.8:** the new
normal Online250 run completed and restored the session cleanly. It has 26
completed Quarters: 23 with Base materials, but only 8 at +3 or better and 4
at +4 or better at the endpoint. One Bakers chain delivers 112 measured active
Service turns; Tailors has none. All 250 publications succeed without reported
fallback or faults. This does not solve poor placement. Five sampled winning
receipt rows have no write in that same packet window; retained plans and
sampling prevent attributing the cause yet. We are adding read-only foundation,
completion and native winning-operand records. The short turn150–175 replay
records Sinope at +1 at foundation/completion and a native choice444,512 Q8
versus our published−15,437 Q8. Another +3 choice consumes our exact write.
Its global observer completeness fails on stale event identities; that gap is
preserved and the reader fixed. The subsequent fresh250 recorded the same
diagnostics with unchanged policy until Henno stopped it at160.
[Placement-time evidence](../research/mods/csc-ai-placement-time-20261113.md).
No tuning weights changed. [Completed prior result and
limits](../research/mods/csc-ai-economy-250-20261113.md). The old goal stays paused.

**13 November central-model integration:** [architecture and diagram](architecture.md)
map the agreed economy, decision adapters and native systems to all of
Problems **1.1–1.8 and 2.1–2.2**. Main CSC now publishes complete late Quarter
values. Astra reviews the implementation and reproduces 22 economic tests; the
final source passes a fresh native smoke with exact writes/cache reads/eligible
comparisons. A preceding 30-turn window verifies repeated delivery, not improved
placement or Services. [Evidence, revisions and limits](../research/mods/csc-ai-central-economy-20261113.md).
The original 6 November decision is preserved in commit `057d4c55`.

**13 November correction:** canonical design requires Quarters to consume
population-limited district slots. Both active SQL definitions incorrectly used
`RequiresPopulation=0`; source now uses 1, with a passing SQLite regression. Prior
full games used the wrong setting. Fresh loaded-definition reads now verify 1
for both Quarters. Recurring transaction valuation is integrated through the
central model and late adapter above; slot-constrained normal-play quality
remains to measure. [Correction and scope](../research/mods/csc-ai-quarter-adjacency-20261112.md#correction-district-slots-and-the-intended-transaction-forecast).

**12 November follow-up, Problems 1.2/1.4/1.8:** conservative forecasts now
exclude future/foundation customer yield and penalise viable sites below +3.
The fresh same-seed Online-speed turn-200 trial is complete and independently audited:
32 complete Quarters, 13 at +3 or better, 5 at +4 or better; 19 remain below +3.
Bakers has 4 active Stage 2 chains/287 native chain-turns (previous 6/312), Tailors 0.
All 200 publications succeed with no omissions or policy faults. This revision
lands but does not solve weak Quarter proliferation. Both early observation
failures, exact package parity, final cleanup and comparison limits are retained.
Earlier scoped capability closures keep their original meaning. The old goal
remains paused. [Full measurements and completed trial](../research/mods/csc-ai-quarter-adjacency-20261112.md).

Updated 12 November 2026. Goal: Problems **1.1–1.8 and 2.1–2.2**, through
[completion contract](acceptance.md), including Henno's 12 November clarification
for native-system guidance. All ten scoped solutions are integrated; the preceding
trial completed one normal 250-turn game and historical baseline comparison.
Prior controlled evidence and its limits remain recorded below.

**Previous 250-turn result, independently audited by Astra:** all ten paths are harmonised
in main CSC; the full game reaches 250 and closes normally. At the comparable
200 clock, completed Quarters are 30 → 29, those with Base 6 → 24, improved
Base 3 → 16 and Bakers Stage 2 active properties 1 → 6. Confirmed Storekeeper
activity is 39 → 312 chain-turns through 199. Tailors Stage 2 remains zero:
material supply improves, but Harbor/customer access does not form a chain.
Production is down 7.8%, net Gold up 11.9% and Food surplus up 9.3%, with
37 → 35 cities. This is a same-initial-world historical comparison with changed
gameplay/CE content, not a causal tuning-only balance test. At 250, Bakers
reaches eight physical/active-property chains; Tailors remains zero.
[Full results and limits](../research/mods/csc-ai-harmonised-250-20261112.md),
[AI-C169](findings.md#ai-c169).

## Completed representative scopes

- **1.1 Material-aware Quarter choice/request — levels 1–3.** A matched
  ordinary +48 offer on the shared Base+Specialty-qualified source changed
  Government to Bakers, with exact native write, site win, request and
  reservation. No Quarter construction completed. [AI-C151](findings.md#ai-c151).
- **1.2 Future customer access — levels 1–3.** Crediting prospective Commercial
  Hub 869 changes Washington's native choice at 870 from Holy Site to Bakers,
  with a matching construction request. Complete packet comparison isolates
  that host path. The location itself does not change. [AI-C153](findings.md#ai-c153).
- **1.3 Rivers — levels 1–3.** Withholding one prospective river-Mill input
  reranks the main owned-site offer and changes the native Bakers location and
  request 2497→2571. Complete packet audit isolates that path; no realised yield
  or Quarter completion is implied. [AI-C156](findings.md#ai-c156).
- **1.4 Combined adjacency — levels 1–3.** Ordinary main guidance changes the
  native Quarter site/request from viable 3-adjacency site 2571 to strong
  4-adjacency site 2497, with complete packet/cache audit. This does not prove premium
  necessity or construction. [AI-C158](findings.md#ai-c158).
- **1.5 Tile acquisition — levels 1–3.** Paid Quarter-footprint follow-through
  combines with native paid supplier acquisition and actual Farm completion.
  No supplier-bid purchase necessity or Service is implied.
  [AI-C162](findings.md#ai-c162), [AI-C163](findings.md#ai-c163).
- **1.6 Construction follow-through — levels 1–3.** Causal Quarter preference
  and an integrated ownership-prerequisite repair proceed through request,
  production, foundation and physical completion. Fresh and retained-plan
  reload pass; no realised Service is implied. [AI-C162](findings.md#ai-c162).
- **1.7 Defer/reconsider — levels 1–3, composite representative scope.**
  Nicopolis's typed declines causally change Bakers to Hippodrome. Washington's
  genuine no-Base scope withdraws after restored Cattle through ordinary23
  publication; native Bakers870 wins and receives request241. Astra audits
  both legs. Separate cases establish these capabilities; no uninterrupted
  single-city cycle or Quarter construction is claimed.
  [AI-C165](findings.md#ai-c165), [AI-C167](findings.md#ai-c167).
- **1.8 Weak-site suppression — levels 1–3.** Matched main-policy deductions
  changed Nicopolis's native site and request, including dynamic frontier
  coverage. This proves suppression of known weak sites, not that every
  replacement is well supplied or that the purchase succeeds. [AI-C138](findings.md#ai-c138), [AI-C139](findings.md#ai-c139).
- **2.2 Finite material protection — levels 1–3.** The automatic main CSC
  policy changed Boston's Campus from Cattle 796 to 720. The retained Cattle
  Pasture was worked. Absolute exclusions, other destructive consumers and
  broader reliability are separate claims. [AI-C065](findings.md#ai-c065).

Astra independently validated these closure scopes on the resumed goal. Later
qualification does not erase them unless it contradicts the original evidence.

## Integrated placement scope; native 2.1 route accepted

The complete normal run is now recorded in AI-C169; conditional mechanisms
without an opportunity in that world retain their separate earlier evidence.

**Native route accepted under Henno's clarified criterion:** loaded mapped
private-yield adjacency, verified native consumption and dynamic main CSC
integration suffice. An isolated changed-choice result is optional; evaluate
actual placements in the normal game. Preserve standalone valuation and
material protection. The production scanner now leaves existing-Quarter
co-location to native SQL and retains +16 only for credible future footprints.

Current2.1 scope is Tailors→Harbor/replacements: the Stage2 registry excludes
City Center nominations, so Bakers' zero customer offers are expected. The
old Fractal run has five native customer comparisons and three exact wins,
but no isolated customer-signal ablation yet. Its later200 source has no
current customer offers. The common Hamburg208 checkpoint now qualifies a
completed Tailors, preserved Sheep and two legal adjacent Harbor sites.
Henno requests native private-yield adjacency first: both diagnostic arms
withhold the optional CE customer bonus and vary only the native link.
The loaded gameplay DB confirms the OFF link is absent after loading that
save, with definitions/bias preserved. A fresh game is not required to load
this SQL change. The completed pair proves native consumption: adjacent
Harbors gain11113/11117 Q8, while competing Water Entertainment values on
those plots decrease5568/5569 Q8. The other1364 matrix cells match.
Both arms select/request Theater; no changed-choice win is claimed.
This is not a purely additive Harbor bonus. Astra independently validates
the partial result, package hashes, trace journals and cleanup.
[AI-C168](findings.md#ai-c168).
[Scoping and existing leads](../research/mods/csc-ai-customer-placement-20261112.md).

**Latest completed capability:** 1.7 is complete at the stated composite scope.
Washington22/version1 stages the actual no-Base decline. Exact restoration of
existing Cattle796 leaves that publication intact; ordinary23/version 2
withdraws it. Native Net/cache/Best reads40267+6144=46411, selects Bakers870,
reserves it and submits request241. All644 package hashes, source, diagnostic
staging and cleanup pass independent Astra review.
[Evidence](../research/mods/csc-ai-quarter-reconsideration-washington-20261112.md).

The preserved Nicopolis200→254 continuation proves ordinary-publication withdrawal
after a controlled transfer of existing farmed Base471. It produces fresh
Holy Site, Commercial Hub and Water Entertainment Complex requests, rather
than Bakers. The main Quarter bid improves; native input valuation falls.
All packages and cleanup pass audit. It remains a negative for later Quarter
selection; the composite closure does not turn it into a successful city cycle.
[AI-C166](findings.md#ai-c166), [continuation](../research/mods/csc-ai-quarter-reconsideration-20261112.md).

**1.5 is now closed at levels 1–3, independently approved by Astra.** Its
integrated footprint workflow (AI-C162) reaches paid ownership and completed
construction. The separate supplier route (AI-C163) delivers +6,656 Q8 to the
mapped Farm forecast, pays45 Gold at220, obtains intended-city ownership, and
executes Farm construction at226. Physical Flax plus an unpillaged Farm remain
at227–230. The unowned offer retires after ownership. Exact journals, checkpoint
hashes, every archived package file and normal cleanup pass.

The supplier was already the control's sole resource candidate; no supplier-bid
purchase necessity is claimed. The controlled action effect is established in
the accepted footprint workflow; the written separate supplier gate requires
paid acquisition through improvement, not another BUY-versus-NOT-BUY result.
No Service or overlapping-buyer reliability is claimed.
[Supplier evidence and sealed audit](../research/mods/csc-ai-supplier-acquisition-20261112.md).

**All ten scoped solution paths are integrated.** Native 2.1 qualifies under
the revised criterion; practical outcomes are recorded in the completed full run.
See the [harmonisation review and run protocol](../research/mods/csc-ai-harmonised-250-20261112.md).

## Evidence levels by sub-problem

| Item | 1: Mechanism | 2: Changed decision/action | 3: Integrated reproduction |
| --- | --- | --- | --- |
| 1.1 Materials | Verified | Quarter choice/request changed | **Complete at stated scope** |
| 1.2 Neighbors | Verified | Future-host path changes type/request | **Complete at stated scope** |
| 1.3 Rivers | Verified | Quarter site/request changed | **Complete at stated scope** |
| 1.4 Combined adjacency | Verified | Stronger Quarter site/request wins | **Complete at stated scope** |
| 1.5 Buying | Footprint and supplier delivery verified | Causal footprint follow-through; supplier paid and improved | **Complete at stated scope** |
| 1.6 Follow-through | Verified | Causal preference and acknowledgement lead to physical completion | **Complete at stated scope** |
| 1.7 Defer/reconsider | Typed decline and ordinary withdrawal verified | Causal deferral plus later supported Quarter choice/request | **Complete composite representative scope** |
| 1.8 Poor sites | Verified | Verified, scoped suppression | **Complete at stated scope** |
| 2.1 Customer sites | Native SQL valuation isolated | ON/OFF retains Theater; isolated choice change optional by user clarification | **Integrated; 250-turn outcomes in AI-C169** |
| 2.2 Protect materials | Verified | Verified, supplier retained | **Complete finite-penalty scope** |

## Retained acquisition negatives and limits

The Szeged fixture received eight native writes and eligible cache reads.
Its +24 offer did not beat Neighborhood, and no purchase contract appeared.
[AI-C149](findings.md#ai-c149). Fresh city→tree→purchase-contract→attempt
lineage is verified, but payment and intended-city annexation are not.
[AI-C146](findings.md#ai-c146).

The two-turn Nuremberg/Hamburg comparison qualified complete seven-city quote
sets and ample Treasury. Nuremberg's owned 788 is stronger than frontier 862;
Hamburg's free 1085 matches frontier 1011. Those comparisons establish no
economic reason to buy. The preserved 202 source now supports the explicitly
controlled release fixture above; this does not prove buying was useful in
the original world, where the tile was already owned.

No upstream CE PR is authorized. Stock AI remains the target; RHAI5 and the
older multi-seed Stage 2 milestone are follow-up qualification. Keep engine
facts in the civ6-ai skill and CSC applications/evidence in repo Markdown.
