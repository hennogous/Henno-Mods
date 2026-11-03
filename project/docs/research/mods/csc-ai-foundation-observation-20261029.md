# Unfinished Quarter observation — closed at turn 110

Observed 29 October; durable closeout 30 October 2026. Follow-up to the
[static foundation decision path](csc-ai-foundation-decision-path-20261029.md).

The original Nuri Bakers foundation was recognised, highly valued, requested,
validated and accepted while another item occupied production. A later request
was selected successfully at native turn109 after that production ended. The
foundation remained incomplete at the hard110 endpoint. This distinguishes
request timing and queue commitment from an unrecognised or necessarily
low-valued foundation. It does not establish a causal tuning benefit or justify
a general finish-first override.

## Scope and identities

One existing source100 save, under the current604-file package and DX11. This is
a current-package rebase of the historical V7 save, not an exact replication of
its historical518-file/DX12 execution. No new world, forced order, preference
change or extra economic intervention was introduced by the probe.

Target: player1, Nuri city524295, plot1862 at12,25, native Bakers district36,
object1507348. Every closed boundary100–110 agrees between Core and UI on this
identity, incompleteness and0/45 production. Original configured human0 is
excluded from the target. City IDs must be joined with player identity.

Save SHA256:
`2982b00a4c4d0c536ac7232e88c2c2b0fc2e56fd2ee7842aa22ad47b2ffb065d`.
Current GameCore DLL SHA256:
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.

Eight bounded passive hooks observed district recommendation, contract
initialization/validation/receipt/update/execution and the city queue decision.
They did not invoke native functions or change arguments, memory data or return
values. Interception patches entry instructions; neutrality in this late-game
scenario remains unproven. The finite controller ran exactly100→110, with
no extension to obtain physical completion.

## Actual sequence

| Native decision / closed boundary | Evidence |
|---|---|
|100 /100|Nuri has an empty queue and pre-existing Walls2011 and Tailors2012 offers. No target Bakers offer is present. Their original creation predates observer arming.|
|100 /101|Tailors2012 wins and Execute succeeds; the queue contains Tailors.|
|102 /103|After Tailors production ends, Builder2061 wins the next observed empty-queue decision. No target Bakers offer is present at that decision.|
|103 /104|GetBestDistrict returns Bakers36 at12,25. Contract2132 is created for the exact target, validated and accepted while Builder remains queued.|
|104|2132 is absent from the first captured city offer vector. The removal/cancellation cause was not observed.|
|105 /106|A separate request2186 for the same foundation is created, validated and accepted. Builder still occupies production.|
|109 /110|An empty-queue decision updates and selects2186. Execute returns success, queue count changes0→1, and the construction log plus boundary110 Core/UI confirm Bakers queued.|
|110 endpoint|Same foundation remains incomplete0/45. Selection is observed; eventual physical completion is censored.|

The native101 rejected Bakers2059 belongs to another city458758 at8,28. A
type-only join would falsely diagnose rejection of the Nuri target. Likewise,
2132's acceptance must not be fused with2186's later execution.

At103, the target site cache is3184048 signedQ8, or12437.6875. Initializer input
is integer12437 and stored present value3183872Q8, or12437. The fractional
difference is consistent with quantization before initialization; its precise
conversion site was not captured. Build priority remains4 and required city
524295. Priority, present value and contract state are distinct fields.

Receipt appends2132 despite its value exceeding the current default build value;
Builder production remains occupied. Founding turn98/current103 lies outside
the statically verified newly founded-city queue-clear exception. Raw state2
on receipt callback return becomes3 at the next snapshot, rather than indicating
rejection. The separate105 request starts with present value12438.

## Values at the three observed queue decisions

Values below are native Q8 converted to ordinary numeric units, **not Gold,
Production yields or a calibrated empire-benefit scale**. The final gate compares
the best contract with unit value minus1 and project value. The ordinary building
fallback is recorded separately and does not enter that contract gate directly.

| Native turn | Selected contract | Other relevant offered values | Unit gate | Project | Ordinary building fallback |
|---|---|---|---:|---:|---:|
|100|Tailors2012:8944.6640625|Walls2011:698.703125|−1|297|Walls1397.40625|
|102|Builder2061:8287|Walls2011:958.8046875; Chichen Itza2058:36|−1|237|Walls1917.609375|
|109|Bakers2186:20824.55859375|Knight2212:2362; Walls2213:1069.94921875; Chichen Itza2058:36|−1|244.5|Walls2139.8984375|

All three selected contracts pass their observed gate and execute successfully.
These are the observed offers and fallback values, not a census of every
hypothetical site/building. Update changes2186's stored value from12438 to
20824.55859375 before its109 selection; this alone does not expose every score
component or establish the value of retained supply.

Current replay selects Builder after Tailors, whereas the historical archive
selected Walls. Do not attribute this difference to a particular source edit,
graphics backend or instrumentation without a controlled comparison.

## Material conflict and natural assistance

The initial/final full-world records show adjacent plot1863 changing from
resource52/count1/no district to resource−1/count0/Tailors district37. The paired
historical source record identifies the resource as Maize, mapped Bakers Base;
captured runtime TypeTags confirm that named mapping. Database rowid is not
assumed to equal native index. The plot initially had no improvement: no Farm
removal is established. Endpoints and placement evidence do not identify a
Builder harvest or the exact resource-removal event.

Adjacent plot1861 retains its resource28/count1, annotated Sugar/Specialty, and
changes improvement−1→6. This is an observed material-setting change, not proof
of uninterrupted supply, active Service or a causal effect on contract score.

All assistance totals and16 saved economic receipts/9 foundation records remain
identical across100–110:895 Gold cost,358 own Gold,537 subsidy and16 acquired
tiles. Pending and error collections remain empty. Ordinary treasury/world
changes are retained; unchanged assistance receipts do not mean frozen gameplay.

## Consequences for the planner and tuning

1. Record whether a foundation has no request, a rejected request, an accepted
   waiting offer, or a selected queue entry. A single placed-to-complete delay
   cannot distinguish these mechanisms.
2. Account for current production commitments and request timing before adding
   Quarter value. This case already receives a high-valued offer and later wins.
   No blanket queue interruption or global district-priority increase follows.
3. Coordinate Quarter footprints with existing chains' materials. A second
   Quarter can remove the input used to justify the first. High native value and
   eventual selection do not certify a viable chain. Evaluating that trade-off
   is different from an unconditional harvest/district ban.
4. Move the next bounded investigation to producer-building selection. Verify
   live forecast delivery, a fresh consumer and competing alternatives; do not
   infer efficacy from cached UI potential or registration alone.

## Closure, audit and limitations

The closed trace contains129 paired calls and3 decision-gate snapshots,
261 events total, with zero errors/drops/identity changes/reentrancy failures or
pending pairs. Chronology is reconstructed by sequence and entrySequence;
serialized paired records are appended at function return, not entry order.

Independent audit rehashed340 source pins,12 dependencies and604 installed files,
and matched all1709 dispatched command sources to journal hashes. There is one
save load and exactly ten finite activation targets101–110, with no111 command.
Native, observer daemon and original held worker handles exited0. The fresh
closure receipt found all original identities and Civ/Tuner/research owners
absent. All145 mod-ID flags,148 subscription entries and AutoStart=false match
the captured preferences. No installed content was changed.

The separate first attempt remains an initial reader failure at paused100,
with no AI activation/hooks. Its uncaptured target/ledger facts remain
unobserved; they are not retroactively inferred from run02.

Limits: one current-package rebase; observer neutrality unproven; initial offers
predate arming;2132 removal cause unobserved; live scheduling-gate fields not
captured; physical completion censored at110. No tuning efficacy, retained-chain
benefit or native AI purchase claim is made. Successful Execute means insertion
into production here, not completed construction.

Artifacts: `Desktop/Codex/csc-native-foundation-observation-20261029/run-02`.
Independent report/checker in thread workspace H:
`foundation-run02-independent-audit.json`, `.md`,
`audit-foundation-run02-independent.py`; operator summary/material comparison:
`foundation-run02-summary.json`, `foundation-run02-material-comparison.json`.
No automatic follow-on game, campaign or scheduled monitor was created.
