# Guidance for mapped Wonder sites

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
