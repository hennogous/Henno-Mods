# Guidance for mapped Wonder sites

The current calibration offers **8 utility** with a Base deposit, **16** with a
working Base improvement, and **24** with working Base and Specialty. CE caps
the increase at one twelfth of the positive native score (about 8.33%).
A site with a native score of 200 utility and both materials working can thus
gain about 16.7 utility, up from 6.25 in the first version. The publisher reads
CE's maximum offer amount so an older build can still accept the packet.
All 158 economy and 259 native score checks pass. The calibrated CE Release
DLL SHA256 is
`9f774e61cf8387b49f45cc46d5a9380884c444b4234b4728489047ca6c4af7aa`.
The original implementation and evidence are described below.

The CSC publisher offers a small siting preference for mapped Wonders beside
completed, functioning and materially viable Quarters. Bolshoi Theatre,
Broadway and Sydney Opera House currently use it through the Tailors' Wonder
sales records. The relationship comes from `CSC_QuarterWonderSales`, the same
generated table that the Quarter forecast uses for completed Wonder customers.

For each eligible Quarter, Lua looks at its six neighbors and publishes only
owned empty candidate plots. The Wonder can be in another city of the same
player. Critical or threatened material plots are excluded. The request is
4 utility with a Base deposit, 6 with a working Base improvement, and 8 with
working Base and Specialty. Overlapping chains keep the strongest request for
an identical player/city/building/plot key. The publisher limits work to
128 offers per player and a 512-offer packet. CE gives supplier protection
priority and further caps the actual increase at one thirty-second of the
positive native score, or 8 utility overall. These initial bounds let a
close candidate compete while keeping substantial native site differences.

REA decompiled the installed Windows XP2 GameCore
SHA256 `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
The plot evaluator at RVA `3e2aa0` checks `CanHaveWonder` at `25bad0` and
supplies the building index, city, coordinates, research/construction delay,
discount and Wonder horizon to Building NetValue at `52a050`. The call at
`3e419a` begins with `e8 b1 5e 14 00`. At return `3e419f` the caller reads
and stores the signed Q8 score at that plot's entry for the building. The
ordinary building forecast calls the same function separately with sentinel
coordinates. CE already qualified and filters both call sites.
REA evidence is `ev_95259b178a033f79e321ad2391777f10bc005d27b188544ce4f3525e3e59acff`
and byte evidence is `ev_d7622c370c53e6982dd2dde7f416eda4c16e576e53409e42a5c1bdf4b13f710a`.
The original supplier protection replay documented a changed Wonder
reservation through this score path.
[Matched replay](csc-ai-bakers-natural-research-20261106.md#matched-wonder-protection-changed-the-reservation).

The placement offer reuses the existing hook and atomic policy. It depends on
the updated CE development build. The status reports the published version,
offer count, matching native evaluations, score writes and the first write's
key and before/after score. An old CE build has zero offer capacity. Native
eligibility and later production and reservation decisions still apply.

Verified through REA, 158 economy Lua tests, and a Release x64 CE build
with 259 district-score checks, four hook-group checks and the synthetic
instruction-call lifecycle check. Release DLL SHA256
`929a3c3242ec6c9df939b47d166a8ce4a9133b132847f42fa79ad3b1f5f4e17e`.
The next live evidence is a matching positive score receipt, followed by a
comparison, reservation and construction at a mapped site.

## Live Pangaea result

The shared controller completed Online turn 250 on the known Pangaea
27061117/37061117 seed with the integrated CSC policy from `49b2d5b2` and CE
`ddad388`. It reused the five optional content/UI packages from the earlier
Pangaea run. Passive observers recorded outcomes. All 250 publications
succeeded and all ten milestone censuses were recovered.

| Measurement | Result |
| --- | ---: |
| Turns with Wonder offers | 173 |
| Staged offer entries across those packets, including refreshes | 2,724 |
| Maximum entries in one packet | 21 |
| Exact Wonder score matches in the logged native windows | 0 |
| Positive Wonder score writes | 0 |
| Wonder hook faults | 0 |
| Distinct original-AI reservation keys for the three mapped Wonders | 15 |
| Those reserved plots next to an owned Tailors Quarter at reservation | 0 |

The native status acknowledged the prior packet through version 249. The run
stopped at the turn-250 boundary. The same hook still registered supplier
protection writes. The geometry comparison joins successful native reservations
to the Tailors footprints observed at their turn. Eleven reservation keys
belonged to players with no functioning Tailors Quarter at that time.
Mapuche finished Broadway at Ngulu Mapu on plot 2704, first reserved there on
turn 143. Nubia's later Broadway contract at Napata did not finish the Wonder.
The earlier run on this seed completed Broadway at Angkor Thom, with no
mapped Wonder adjacency there either. The earlier run differs in other CSC
policy, so the city difference has no attribution to Wonder guidance.

This run verifies packet publication and regular native scoring activity, with
no eligible offered row observed. It leaves the positive score path's live
effect open. A targeted comparison should start with a verified legal Wonder
tile beside a functioning Tailors Quarter. Capturing the rejected offered
footprints would also tell us how much of the gap is map geometry versus
native eligibility, timing or score routing.

CSC guidance took 2.604 seconds mean and 6.198 seconds max per turn across
250 turns. The controller closed Civ normally and restored the preferences.
The inactive player save gate declined the turn-250 save before any request
was sent. The endpoint census and logs were retained along with verified
saves at turns 50, 100 and 200. Removed 405,642,180 bytes of verified closed
package duplicates. Evidence is under
`Desktop/Codex/csc-ai-wonder-placement-20261118/pangaea250`, including
`Lua.log`, `AI_Behavior_Trees.csv`, `City_BuildQueue.csv`,
`ai-processing-time.json` and `full-game-observation-complete.json`.
