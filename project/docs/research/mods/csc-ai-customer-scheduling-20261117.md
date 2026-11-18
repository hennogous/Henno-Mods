# Customer placement: native delivery and matched outcomes

**Two matched Online250 pairs are complete. Connections improve overall;
Pangaea is mixed. Fractal's control is running.** Pair-first scheduling improves fresh coverage at the same forecast
budget; a combined-guidance ablation changes a close Hub choice through physical
foundation. Stronger ordinary sites retain their wins. Three matched Online250
worlds provide the remaining repeated-outcome test. **AI-C214–216**.

| Continents250 | Current control | Pair-first candidate |
|---|---:|---:|
|Physical links outside City Centers|20|34|
|Bakers / Tailors links outside City Centers|11 /9|20 /14|
|Connected foundations with confirmed competing sites|8/16|17/20|
|Quarter-first / customer-first links|12 /8|24 /10|
|Connected Commercial Hubs / all Hubs|3 /16|6 /23|
|Connected Theaters / all Theaters|2 /31|4 /28|
|Quarter foundations, all with Base|23|25|
|At least+3 / at least+4 adjacency|21 /7|23 /9|
|Both material classes at foundation|3|4|
|Guidance average / maximum|1.976s /4.025s|2.362s /5.505s|

Both games close/qualify250 with complete timing and zero observer faults. The
increase in mean guidance cost is0.386s/turn; its cause needs a same-mature-world
comparison if it recurs on the remaining maps. Services remain outside the new
placement pricing. Endpoint properties are Storekeeper8→9, Innkeeper3→1,
Sacristan0→1, and Bakers Stage4 Service0→1. These are downstream outcomes to track
alongside physical connections.

The Quarter-specific gains include customer-after-Quarter links: Bakers10→17,
Tailors2→7. Customer-first links are Bakers1→3 and Tailors7→7. Tailors has seven
Quarter foundations in both arms, so its extra connections are not explained by
more Tailors being placed.

### Offline performance candidate

A diagnostic-only prototype reuses the exact starting world in each producer
coordinate search instead of scheduling and pricing it again. The logical
evaluation count and budget failure remain identical. On201 joint-world calls
(13 existing regressions plus180 generated scenarios), complete canonical
results/errors match exactly while price-function calls fall233,498→206,861.
Another12 route regressions/23 world calls also match completely, including
rounded payouts, queue timing and unavailable values. Wall timings are noisy
during the running game and are not a live performance result.

The source tool is `project/tools/ai_economy/prototype_joint_reuse.py`; its result
JSON and separate Lua model are under the experiment's Desktop `prototypes/`
folder. The tool requires an explicit output directory outside the source tree.
Main source and frozen game
packages are unchanged. If mature-game cost needs work after the remaining
maps, compare old/new scheduling on the same mature save and measure this
candidate there before integrating it.

The prepared `customer_timing_query.py` uses the existing read-only survey
lifecycle after this campaign. Astra's review narrowed its first measurement to
preselected player5 on both mature Continents saves, with B/A/A/B order. Each
replicate resets private F/M/E modules, supplies real common material/early
inputs, and times `QuarterBids` plus its nested customer call. Complete results
must repeat within an arm; a model-only comparison must preserve all bids,
world plans and unavailable outcomes. Proof formatting is outside timers.
This is a cold-history placement pass without Builder/repair assistance or
packet publication. Full-game timing remains the whole-guidance measurement.
The query compiles and preserves active modules offline; native measurement
is pending. Its proof encoder retains sparse plot sets and Havok integer IDs.
The existing survey's optional1..60s acknowledgement timeout never retries a send.

### Pangaea250: mixed outcome

| Pangaea250 | Current control | Pair-first candidate |
|---|---:|---:|
|Physical links outside City Centers|32|28|
|Bakers / Tailors links|20 /12|22 /6|
|Quarter-first / customer-first links|16 /16|18 /10|
|Confirmed comparable connected foundations|10 /14|13 /24|
|Bakers / Tailors foundations, all Base-adjacent|18 /6|21 /3|
|At least+3 / at least+4 foundations|23 /18|23 /16|
|Both material classes at foundation|6|6|
|Storekeeper / Innkeeper endpoint properties|10 /3|10 /4|
|Guidance average / maximum|3.028s /7.044s|2.638s /5.821s|

Both arms close/restore/qualify250 with zero native faults and drained captures.
Tailors retains two links per founded Quarter in both arms; fewer Tailors explain
its lower total. Candidate customer-after-Quarter connections increase despite
the lower total. Across the first two maps, non-City-Center links52→62 and
Quarter-first links28→42; mean guidance is2.502→2.500s/turn. Comparable conversion
18/30→30/44 is a legal-alternative metric: linked sites are not automatically
economically superior. Fractal and the native audits below remain open.

Four equal-or-better ordinary-adjacency linked misses have same-generation
cached scores before the matching native BEST, corroborated by independent
actual selector calls:

|Player/city/turn, district|Linked plot / Q8|Chosen plot / Q8|Remaining native margin|
|---|---:|---:|---:|
|3/131073/50, Holy Site|1656 /181415|1654 /210125|112.148utility|
|4/65536/104, Entertainment|755 /313094|603 /332473|75.699utility|
|3/524294/174, Entertainment|2032 /370638|1959 /412516|163.586utility|
|2/393221/237, Commercial Hub|2837 /1069581|3132 /1096130|103.707utility|

The first three receive fresh economic additions7693/7407/3768Q8. In the fourth,
the linked site is the reference: the ordinary site receives-55993Q8 and still
wins. These corrections land; ordinary adjacency alone does not explain the
remaining native values. A fifth Hub case5/196610/164 has a positive28038Q8
offer163, then no offer/same-generation linked cache164 when the ordinary site
wins. Keep that scheduling window separate from the four delivered corrections.
Two Base0-at-customer-foundation flags and the largest terrain concession are
under Astra's read-only audit. No blanket bonus or policy change has been made.
[Compact native comparisons and provenance](csc-ai-customer-scheduling-20261117.json).

The same-seed restart closes/restores/qualifies250. It has24 original-AI Quarter
foundations(18 Bakers/six Tailors), all Base-adjacent,23 at+3+,18 at+4+, and six
with both material classes. Its32 physical non-City-Center links split20 Bakers/
12 Tailors and16 Quarter-first/16 customer-first. Confirmed comparable customer
foundations connect10/14. There are no raw resource losses; eight working-supplier
interruptions are recorded. Endpoint Service properties show10 Storekeepers and
three Innkeepers. Mean/max guidance is3.028/7.044s, with complete250-turn coverage,
zero native faults and all final native records drained. Another0.378GiB of exact
duplicate package archives was retired. Treatment uses the same initial-world
reference and unchanged frozen candidate.

### Pangaea controller recovery,18 November

The first control attempt verified130 and reached135 in the archived Lua log,
then stopped when an optional popup guard exhausted pre-Lua context discovery.
A preceding Wonder close was acknowledged and Core proof had already advanced
to133. Native capture has zero faults, and session exit/restoration verifies0.
The partial is preserved as `pangaea-control250-attempt01-discovery135`.

The shared controller now defers only the typed pre-Lua discovery failure during
polling/presentation checks. It polls the same finite operation, keeping original
interval/progress bounds, at-most-once reservations and strict ambiguous-send
failures. Astra reviewed this boundary;76 focused tests pass, one skipped.
The campaign restarts with identical frozen policy/seed. Duplicate package
archives and native50/100 saves were retired against retained verified copies.
This attempt contributes no completed-game outcome.

The matched150–155 replay starts from the same verified post-restructure save.
Control uses frozen d6a9114a policy; treatment changes only the main CSC economic
adapter (implementation7ea8820a). SQL private adjacency remains1, ordinary
economic coefficients and CE b7194a8 remain fixed. Both source structural gates
pass and both sessions close exit0 with preferences restored.

| Measure | Control | Pair-first |
|---|---:|---:|
|Visited city/type group windows|68 /92|92 /92|
|World forecasts over window|264|264|
|Maximum per-player forecast count|16|16|
|Native district decisions|44|44|
|Actual choices and selected scores matching control|—|44/44|
|Publication average,151–155|2.461s|2.455s|
|Publication maximum,151–155|2.641s|2.579s|
|Lua/policy/observer failures|0|0|

The target is player3 Magdeburg city262144, Bakers2228, Hub2227. Both native
selectors choose the linked Hub at150 with294,684Q8 (1,151.109utility), submit
contract2994 and start construction151. The full native selector matrix is
captured. Other positive owned Hub cells range694.918–1,122.828utility. The
hand-picked earlier reference2080 is already a Diplomatic Quarter at150; use
the captured current matrix for actual alternatives, not that stale reference.

Group counters describe work windows, not separate construction opportunities.
No choice changed in this pilot because the control already chose the good
connection. A genuine switching case and stronger ordinary-site control remain
required before the full-game comparison campaign.

## Next short window

The control100–130 replay has completed/restored. The treatment reached130,
but its passive recorder exhausted the32-matrix limit at129. Its held game was
frozen/inactive, then closed through an identity-checked shared-controller
cleanup, exit0 with preferences restored. The test follows a baseline unconnected capital
Hub at2024, where an alternative1949 beside Bakers2022 received positive economic
offers. A second scope records Magdeburg's earlier alternatives. The treatment
uses the identical source and the adapter-only package. Thirty turns include
the turn125 decision; physical follow-through is recorded separately. The guard remains
explicitly bounded. Shared-controller ownership and passive matrix recording
continue, with no extra policy or gameplay orders. In the control, Washington
chooses Hub2024 at125 (346,627Q8) over linked1949 (337,500Q8). Both are owned,
eligible native rows. The former has5Gold adjacency; the latter1Gold and
private-yield1. A35,853Q8 (+140.05utility) economic bid is published for1949
that turn; the native final difference is9,127Q8 (35.65utility). This is a useful
stronger-ordinary-site comparison.

### What the longer window taught us

The treatment changes Boston's district comparison at108, so later empire
development diverges before Washington's125 decision. At125 the treatment still
prefers a CL rural district; these Washington choices no longer isolate a site
switch. All data remains under `pairs100-130`; `failure.json` and
`interruption-reconciled.json` distinguish failed capture from successful
cleanup. The optional matrix payload now has a128-matrix bound for short
targeted windows; normal full-game capture requests no full matrices. A safely
frozen passive fault may explicitly permit cleanup, while the observation still
fails qualification and sequence/transport faults raise.

Astra recommends Buffalo156 next: baseline repeatedly priced linked2017 against
eventual Hub winner2015 through155, then omitted it156. The current control
replays150–160, including baseline foundation158. Native matrices and CE journal
entries distinguish missing residuals from delivered bids that lose. Economic
coefficients remain unchanged.

### Opportunity and score-lineage diagnostics

`customer_placement_watch.lua` observes the actual `CustomerCandidateSets` call:
changed legal/owned/unprotected linked and ordinary footprints, removals,
reference and publication freshness. It includes singleton sets, giving a
denominator beyond the priced shortlist, without another world forecast or map
enumeration. Native CE records retain raw kind, generation and ordinal. Full
games reuse the Quarter observer's journal pass; short customer replays own the
passive read. Neither path writes policy or gameplay state. Physical events and
native selector matrices remain the later outcome records. Eligibility is at
publication; later reservations/legality are checked separately. Diagnostic
faults or truncation fail observation qualification. Astra's second review adds
page offset/total/record-count validation, persistent final-drain failures and
final success only after observer qualification, native exit and restoration.
Missing clocks and disappeared groups remain unobserved; only positive sets
enter the opportunity denominator.47 related checks and three opportunity-
analysis checks pass. The first Buffalo setup closes/restores before play after
a Python-tuple/Lua-list serialization error; the corrected control is
`buffalo-control150-160-02`. Diagnostic source compilation now precedes launch.

`customer_opportunity_results.py` joins the changed sets to actual native choices
and physical foundations, deduplicates capture and reports comparable choices,
linked-only choices and unknown coverage separately by loaded customer type.
It reuses the gameplay-derived native connector registry. A linked proposal
without physical foundation cannot count as a constructed connection.

## Buffalo: the scheduler repairs comparison-time delivery (AI-C215)

Both150–160 arms close/restore exit0 with qualified observations. The original
schedule publishes linked Hub2017 through155 but omits it156; the new schedule
publishes15,978Q8 (+62.414utility) at156. CE generation16/version7 records the
exact early write259,564→275,542 at ordinal862, cached421,150 at982, then
winner2015=470,990 at1007. The independent native selector records actual call156.
Control's linked cell is405,172: treatment's final matrix gains exactly15,978Q8.
This closes publication→early consumer→final comparison for this gap.

The stronger ordinary site still wins by49,840Q8 (194.688utility), and both
physically found Hub2015 at158. The customer set disappears159, with no further
Hub offer. At155 the linked site is a farm with native site adjustment−81,759Q8
(−319.37utility); the riverside woods alternative receives+7,652Q8 (+29.89).
Those are same-clock native site-accounting components, not an attribution of
the entire156 final difference to one input. The ordinary adjacencies are3vs2.
No new coefficient or blanket bonus is justified by this result.

| Measure,150–160 | Control | Pair-first |
|---|---:|---:|
|City/type group windows visited|123/164|164/164|
|World forecasts|474|474|
|Actual native district choices|100|100|
|Same selected types/sites|—|100/100|
|Same selected scores|—|98/100|
|Guidance average,151–160|2.579s|2.480s|
|Guidance maximum|3.368s|3.192s|

The two score differences are the same linked CL rural site1532 on156/157;
neither selected footprint changes. All policy/observer faults are zero.

### Bounded positive construction gate

Astra confirms that earlier Qaraqorum SQL0/1 changed a choice but reached no
foundation by155. Magdeburg's already-winning Hub did reach foundation, so those
different cases cannot be combined into changed-choice→construction evidence.
The next bounded test uses the **current** qualified150 save and pair-first main
CSC adapter, Magdeburg city262144. Only the Bakers→Hub private SQL amount varies
0/1; all ordinary economic coefficients remain fixed. The zero arm is active
under `magdeburg-sql0-150-155`. This qualifies the combined customer-placement
mechanism, with scheduler-only delivery measured separately above.

**Both arms now pass through physical construction (AI-C216):** zero selects
unlinked2377 at150 (288,287Q8), then founds it151. Normal1 selects linked2227
at150 (294,684Q8), then founds it151. The corresponding competing cells are
278,814Q8 for2227 in the zero arm and271,631Q8 for2377 in the normal arm.
Both close/restore exit0 with qualified captures and matching save identity.
No bid, production order or foundation was forced.

**Attribution correction:** the Lua reverse partner graph currently accepts
only positive private-yield rule rows. Setting this edge to0 therefore also
removes Bakers→Hub from customer-first and post-Quarter candidate routing.
This is an ablation of combined guidance for that relationship, not an isolated
measurement of SQL versus Lua. Ordinary gameplay transactions and production
coefficients remain unchanged. Future isolated-channel experiments must retain
the structural partner graph independently of incentive amplitude. Normal
production1 retains every generated relationship; this test changes no shipped
policy. It closes the combined close-choice→foundation gate without claiming
the scheduler alone caused that switch.

## Final comparison campaign

`customer_placement_campaign.py` runs fresh control/treatment pairs on the three
preselected worlds, Online250. It checks initial-world parity, fixed package and
optional-mod manifests before each child, all timing coverage and clean native
closure. The current-policy Continents reference is rerun to give the new
opportunity denominator the same coverage in both arms. Native decisions remain
under the existing shared controller; no probe policy is enabled.

Astra's runner review adds resumable offline postprocessing for already-closed
qualified children, explicit stops for partial/live outcomes, immutable startup
manifest checks between games and a separate-keeper deletion guard. Two archive
retirement checks pass. Exact duplicate closed package copies are retired after
analysis; unique inputs, all outcome records and saves remain. The campaign has
six fresh games, not six simultaneously active games. Final three-map outcomes
still must demonstrate improvement before the goal is complete.

WildW's develop2986a746/mastere59b5aa9 remain unchanged on the pre-campaign
GitHub branch check. Qualified CE b7194a8 remains the frozen runtime. No PR.

### Continents control completed

The fresh current-policy control closes/qualifies250. All1,844 ordered native
district choices **and their Q8 scores** equal the previous frozen-control run.
Its23 Quarter foundations remain16 Bakers/seven Tailors, all Base-adjacent;
21 are+3+, seven+4+, three have both material classes. This corroborates that the
added passive candidate/journal diagnostics preserve these decisions on this map.

At250,20 physical non-City-Center customer/Quarter pairs remain:12 Quarter-first,
eight customer-first. There are three connected Hubs/16 total, two Theaters/31,
one Holy Site/seven, one Entertainment/Hippodrome/ten, zero Harbors/13, seven CL
urban sales sites/28 and four rural goods-provider sites/37. Eight Storekeeper
properties and three Innkeeper properties are active; no Dockmaster/Sacristan.

The new opportunity denominator finds16 customer foundations with positively
observed linked **and** ordinary owned legal alternatives beside an existing
Quarter at the actual choice; eight select linked sites and physically connect.
Hubs contribute3/5. Two further Hub choices fall outside the current observed
candidate set and remain separate; sites without a positive group are not
counted as proven absence. Customer-first foundations are reported by their
physical order, outside this existing-Quarter comparison denominator.

Guidance has complete250-turn timing:1.976s average,4.025s maximum; zero policy
or observer failures. Exact duplicate package retirement recovers0.379GiB after
clean native exit. The matched candidate starts next with the same initial-world
reference and frozen gameplay/mod stack. Compare both arms before deciding
whether this first scheduler slice improves the full-game outcomes.

### Candidate checkpoint recovery

The first candidate attempt stops at100 before issuing its optional checkpoint
save: shipped single-player UI permission requires a locally active turn, which
the inactive observer seat did not have. Core was idle/alive, and the native
recorder had zero faults. The session closes normally, exit0/preferences
restored. Its records remain in
`final-comparisons/continents-treatment250-attempt01-save-gate100`; the relocation
receipt preserves its original path/provenance.

Full-game observation now follows the existing vanilla control runner: catch
only `SavePermissionUnavailable` for ancillary50/100/150/200 saves, record zero
requests and continue to the next bounded play window. Ambiguous/post-request
failures and the required endpoint save remain strict. The regression test
confirms observation continues100→105 after a refusal and stops after a sent-save
timeout.23 focused observation/campaign/continuation checks pass. Fix6b31aca7
changes no game policy, coefficient or package. Astra verified shipped UI source
and the closed failed session; the validated control remains usable.

The candidate restarts freshly from1 on the same preselected seed and frozen
inputs. This avoids combining different transient-cache segments in its final
outcome. Exact duplicate failed-attempt packages and its redundant native50
checkpoint are retired after hash checks; the archived save and all records
remain. The parent runner resumes qualified controls and preserves this failed
attempt explicitly in its progress history.

The fresh retry reaches250 and closes/qualifies. Its turn100 refusal is recorded
with zero requests and ordinary autoplay continues;150/200 and the required
endpoint save succeed. The runner finishes candidate analysis/retirement and
starts the preselected Pangaea control.

### Astra's first full-pair review

The gain is mainly Quarter-first:12→24 links. Among linked comparable choices,
selected ordinary adjacency equals/exceeds the best ordinary alternative in
13/17 candidate cases versus6/8 control. Largest concession is two adjacency
points in either arm. This is terrain geometry; native site costs and economic
streams remain part of the actual comparison. The21 candidate Harbors have no
positive existing-Quarter opportunity observation, so their zero connections do
not justify a larger Harbor bonus.

One reported link without Base was a capture-history analysis error. Live totals
show one owned, unimproved Wheat at both choice141 and foundation144 beside
captured Bakers2080; it becomes a working Farm194. Changed-only per-owner
material rows had omitted that unchanged resource after ownership transfer.
Coordination analyser v3 uses complete `MATERIAL_TOTAL` snapshots, exposes their
round/sequence, and leaves missing inventories unknown. Both corrected arms
have zero links flagged without Base. Six focused analysis checks pass; this
changes reporting only. The long-running parent has cached v2, so rerun the
closed-arm coordination analysis with v3 before the final comparison.

Customer forecasts remain10,464→10,483 (+0.18%), while group visits rise
2,787→4,066. Additional unique work matters: route misses increase28% and recorded
quote counters38%. Turns201–250 contribute about65 of the additional96 publisher
seconds; late joint evaluations rise46%, quote counters84%. Keep the policy
frozen for the remaining two map pairs, then compare adapters on the same mature
state to distinguish scheduling cost from the larger/different economy it creates.

## Storage

On Henno's instruction, ten exact duplicate CE/CSC installed-package archives
from five closed surveys/replays were rehashed against retained immutable
sources and removed. Actual recovered space is1.896GiB, leaving38.62GiB at the
check. All saves, compact/raw records, baseline inputs and the current treatment
freeze remain. The deletion ledger with manifests/keepers is
`Desktop/Codex/csc-ai-customer-scheduling-20261117/storage-retirement-20261117.json`.
Retire further closed duplicate copies as work proceeds; preserve live inputs
and required comparison baselines. This removes redundant packages, not evidence
needed to rerun the current experiments.

A second retirement removed four exact duplicate package copies from the
closed/reconciled100–130 windows: another0.758GiB recovered,38.25GiB free while
the Buffalo control runs. Its separate ledger is
`storage-retirement-windows-20261117.json`. Total recovery so far:2.654GiB.

Six further exact Buffalo copies were retired after both sessions closed:
another1.136GiB, cumulative3.790GiB. The check left37.77GiB free during the next
diagnostic; see `storage-retirement-buffalo-20261117.json`. The campaign records
free space and retirement after each closed game and requires10GiB before a new
launch.

## Remaining goal gates

Native changed near-tie site/foundation; stronger ordinary-site win; invalidation;
opportunity-based outcome instrumentation; three preselected fresh Online250
treatment games and matched current-policy comparisons. Continue beyond this
first scheduler slice wherever evidence identifies a discovery, eligibility,
continuity, acquisition or valuation blocker. After Problem2.1 is proven, use
remaining usage for Problem3 research as requested in the updated goal.
