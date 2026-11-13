# Why a weak Quarter can keep the native bid

13 November 2026. Active Problems **1.6 and 1.8**. Henno stopped the outcome
experiment and requested REA investigation. No further game was launched and
no gameplay policy or CE native code changed during this investigation.

**We have a delivery-coverage defect before we have a calibration conclusion.**
The main model publishes a complete value for a weak site, but the native
selector can still compare a much larger stock value for that same identity.
The native writer has a reservation guard stricter than Civ's selector.
Existing logs put a Builder reservation on Sinope's exact tile before the
missed Quarter intervention. This strongly supports that guard as the cause;
the exact rejecting branch and reservation ID were not captured at the write
boundary, so their runtime attribution remains to verify.

## What the AI actually chose in Sinope

The [read-only saved-game replay](csc-ai-placement-time-20261113.md) records
player1/city327684, Tailors district37, plot1062 = **26,14** on the74-wide map.

| Observation | Value |
|---|---:|
|165: native improvement trigger |Farm, priority163 |
|165: improvement tree's reservation of26,14 |SUCCESS |
|166: actual native Quarter cell at selection |444,512 Q8 =1,736.375 utility |
|166: accepted CSC complete bid for that same pair |−15,437 Q8 ≈−60.30 utility |
|166: native Quarter trigger and queue acceptance |priority1,736 |
|166: district tree's reservation of26,14 |SUCCESS |
|169: physical Quarter foundation |+1 adjacency |
|172: physical Quarter completion |+1 adjacency |

The district score comes from CE's existing `best` journal, observed when that
packet is drained at167. The behavior-tree log independently shows Farm163 and
Quarter1736. Thus the engine follows its much larger native Quarter valuation;
it is not comparing the negative complete value we intended for that cell.
The later foundation packet has a different bid and is not substituted for the
earlier decision's bid. These are ordinary native requests and construction,
not forced orders. The attempted Farm's eventual completion is not established.

The same publication contains ten complete writes elsewhere in Sinope; the
other weak Tailors case has twenty elsewhere in its city. This shows a working
capability elsewhere, not complete coverage of the winning row or proof about
the ordering of every other write relative to this comparison.

The replay has two unrelated stale district-event identity faults. Its global
observation completeness fails; individually emitted selector/lifecycle rows
and the native behavior-tree records remain available as explicitly partial
evidence. Do not turn this case into an exhaustive placement success/failure rate.

## REA confirms the native reservation rules

REA opened the **actual installed Firaxis XP2 DLL**, providerGhidra, SHA256
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
The older annotated Ghidra project supplies names only; the following code was
independently decompiled from this updated artifact.

`GetBestDistrict` RVA**3e4a50** reads each eligible row's district scores at+20.
The row must be district-capable (+55), and owned (+5a) or frontier (+57).
Its reservation pointer at+48 leads to:

1. Request ID−1: use the default threshold.
2. Nonempty ID that `Control::Manager::Find` (**4019f0**) cannot resolve:
   also use the default threshold. The selector does not clear that old ID.
3. A live request: use the reservation's stored Q8 priority, at reservation+4.

The candidate must strictly exceed that threshold and match or exceed the
running best. Equal best scores invoke the native tie RNG. There is **no
positive-score requirement** in this selector; its initial floor is
−2,559,744 Q8 (−9,999 utility), read directly atRVA**b66cb0**.

`ReservePlotNode::Update` (**55ef10**) converts its integer reservation
priority toQ8 with a left shift of8 and calls `TryReservePlot` (**3ea040**).
For a live reservation held by a different controller, takeover requires
incoming priority **strictly greater than stored priority +5,120 Q8**.
The constant at**b65580** is bytes`00 14 00 00`: **20 utility**, not20Gold.
A matching controller can refresh its reservation; a missing old controller
does not enforce the margin. The reservation setter stores controller ID,
Q8 priority and a third payload in the12-byte slot.

`ReleasePlot` (**3e97e0**) clears that slot toID−1 and zero payload only when
the releasing controller ID matches. A residual nonempty ID is therefore not
by itself proof of a live claim. Selection and actual reservation are separate
comparisons, with different thresholds. The Farm163/Quarter1736 observations
are consistent with the Quarter readily clearing a weaker improvement claim.
We have not recorded the raw reservation priority/ID at the exact166 write.

## Where our adapter differs

CE code`6f53037`, `AIDistrictScores.cpp`, `resolve_late_cell`, requires the
reservation pointer to be readable **and its ID to equal−1**. This applies to
complete final replacements as well as the older guarded adjustment route.
It silently rejects a nonempty ID before a `final` journal record is emitted.

| Row condition | Civ's joint selector | Our complete-value writer |
|---|---|---|
|No reservation |Compares valid cells |Can replace after its other guards |
|Stale nonempty reservation ID |Compares using default threshold |Skips |
|Live Builder/Wonder/other reservation |Can outbid its priority |Skips |

The guard originally protects retained plans in a narrow experimental write.
It is unsuitable as the blanket admission rule for ownership of complete
Quarter values: Civ itself still lets those sites compete. Skipped cells keep
their native direct valuation and any building premium. Other guarded writes
in the city can succeed, so readiness and aggregate write counters remain green.

This is a confirmed code-level coverage mismatch. Sinope's preceding successful
Builder reservation makes it a strong explanation of the observed miss.
It is not yet a captured runtime skip reason; row-pointer aliasing, pre/post
validity and matrix/caller guards must remain in the diagnostic differential.

## A second, separate coverage mismatch

The main UI helper `GetLegalDistrictTargets` returns no owned targets unless
`BuildQueue:CanProduce(districtHash,false,true)` and current BUILD admission
checks pass. The economic adapter quotes owned sites from that list. In
contrast, the native plot evaluator (**3e2aa0**, district branch) loops district
definitions, estimates missing technology/civic time and adds it to construction
time before calling `NetValue` (**52a440**). Its opportunity set includes future
unlock candidates. Frontier quotes use a different radius-three path.

Therefore a complete replacement is not yet guaranteed for every owned future
candidate that the native AI can nominate. This can explain a class of choices
with **no** published complete bid; it does not explain Sinope, which has an
explicit accepted bid. The exact causes of individual missing offers remain
untraced. Do not conflate this with the reservation case.

## What this changes about the next step

Keep the current economics and finite policy bands while closing delivery:

1. Record a bounded, explicit admission/rejection reason for each complete
   candidate at the native write boundary, plus the effective reservation
   state and matrix identity. Preserve packet/row identity and native order.
2. Align complete-value coverage with native competition. Price an eligible
   reserved candidate while leaving Civ's reservation threshold/takeover rules
   intact; never clear a reservation or create construction permission.
   Preserve the distinct safety contract of older guarded adjustments.
3. Cover admitted future-owned candidates coherently, or explicitly report an
   intentional native fallback rather than claiming complete takeover.
4. Before another outcome game, verify that a targeted native comparison sees
   the intended value or an explained fallback. Only then assess score bands.

These are proposed corrections, not implemented or tested changes. No new PR
was made. A fresh run would measure coverage, not resolve the native guard by
itself. Henno's stop instruction remains in force for outcome games.

## Stopped fresh observation and evidence

The subsequent fresh game was stopped by its owning shared controller at160,
native exit0, owners absent, preferences restored and packages retired. The
turn150 checkpoint is preserved, SHA256
`ed599084d04dfbbb84015c1e08bea976710dbff7d7043a4a9436aa578b343c92`.
Its initial map, starting units, seats and starts match the previous game.

Its recorded prefix contains18 original-AI foundations,15 below+3 even with
the prospective local Mill;42 native Quarter selection events,18 with a matching
published complete bid and17 value mismatches. Events are not distinct built
Quarters. There are two deferred lifecycle identities and no observer faults.
The final journal was not drained after the stop: the prefix is incomplete,
not a completed250-turn qualification or a causal policy comparison.

Artifacts: `Desktop/Codex/csc-ai-placement-time-20261113/`:
`replay150-175-01/{Lua.log,AI_Behavior_Trees.csv,placement-watch.json}`,
`fresh250/{source-update-handoff.json,session-closed.json,checkpoint-150.json}`.

REA's complete34-record evidence bundle is
`rea/native-selector-and-reservations-final.json`,4,022,356bytes, SHA256
`02d9529c885d5f4cbbd4ed389e64d7a55ca59c1e40d77811b6ff5b579605189d`.
It preserves artifact identity, pseudocode, assembly, references and direct
constant reads. The large plot evaluator's high-pcode view is truncated;
no completeness claim relies on its omitted value-flow operations. The relevant
district pseudocode is retained. REA's binary session was closed after export.
