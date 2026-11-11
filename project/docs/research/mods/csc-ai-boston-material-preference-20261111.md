# Boston: matched material preference and native choice

Problem **1.1**, evidence levels 1–3. Acceptance is a changed native Quarter
choice toward a legal site with viable mapped Base, produced by reusable main
CSC code. The first pair is a valid negative result. The later strong-material
pair changes Government to Bakers and closes that scope, validated by Astra.
Neither pair establishes Quarter construction or native tile acquisition.

## Matched ordinary-policy test

Artifacts under `Desktop/Codex/csc-ai-problems-1-2-20261110/`:

- `boston-material-control-01`
- `boston-material-treatment-01`

Both load the same Boston turn-22 checkpoint (SHA-256
`9675be27c614a2429a9cdca485a09a8d7421e627cc7833cb472bb9b1c390f55a`),
use the same frozen gameplay carrier and current four main CSC AI modules plus
UI quote bridge, and run to inactive turn 33. The CE DLL is
`f8121151c787e4dcd4fea876eaaef5d6d1bb2b54561bc94d9d7da6385f21aa07`;
stock XP2 is `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
No Frida writer or external score pulse runs in these arms.

The old save lacks the policy's original-seat metadata. The diagnostic helper
supplies only player 3's missing AI-role property after checking pinned source
provenance, turn, human observer, leader, city and conflicting saved properties.
This migrates the fixture; ordinary CSC role capture remains unchanged.

The two staged publishers differ only in the diagnostic control Boolean.
Control removes the positive `(3, 131073, 36, 721)` entry **after capacity
trimming**, so no previously omitted entry takes its place. The initial retained
packets differ exactly by that entry, **+6,144 Q8 = +24 utility**. The other
60 entries, including another positive Bakers candidate, remain; other policy
arrays have matching counts. This is a one-pair ablation, not removal of every
Quarter incentive.

The live model reports one viable, currently improvable Cattle Base at 796,
no Specialty, an existing adjacent City Center and one additional future
customer footprint. Projected combined adjacency is **3**, so the ordinary
viable-site band applies; the strong-site +48 band is not justified here.

| Observation | Control | Treatment |
| --- | --- | --- |
| Target staged initially | 0 | 1 |
| Native target score | 28,795 Q8, read as treatment's pre-write value | 34,939 Q8 after the +6,144 write |
| Completed target write / eligible read / city selection / win | None staged | 1 / 1 / 1 / 0 |
| Native Boston choice on 22 | Campus 944, value 153 | Campus 944, value 153 |
| Accepted plot-purchase request | 225 | 225 |
| Quarter 721 through 33 | Owned, empty | Owned, empty |
| Cattle 796 | Retained; Pasture present by 28 | Same |

All 13 physical/queue snapshots match. Both sessions completed 11 turns, reported
healthy CE policy with zero faults, and closed normally with preferences and
temporary packages verified. Later target staging disappears while the Campus
plan remains: thirteen snapshots are not thirteen fresh failed selections.

## What this establishes

The current dynamic main policy publishes and delivers its ordinary material
preference to a native comparison. It does **not** establish a changed placement
or construction decision. Preserve this as an accepted negative result rather
than escalating the offer to the measured score gap.

## Next controlled case and limits

The read-only survey identifies **720** as the only projected Commercial Hub or
Entertainment footprint next to 721. Sugar on 720 would add one material point
but remove one projected customer point. Material adjacency also requires owned
land. Neither a resource on an unowned neighbor nor consumption of the sole
customer footprint automatically creates a +4 site.

Astra recommends inspecting the six neighbors once, then preparing a single
controlled derivative with a natively suitable Specialty on another revealed,
empty neighbor, assigning ownership explicitly if needed. Record both edits;
this is fixture preparation and proves no acquisition capability. Preserve 720,
City Center 795 and Base 796. Use the same derivative in both arms and require
the unchanged model to independently produce +4/+12,288 before testing the
ordinary strong-site preference. If either qualification fails or both arms
make the same decision, retain that result without gap-derived bid escalation.

The subsequent `boston-material-geometry-01` survey completed at turn 22 with
zero turns advanced and verified normal cleanup. Native `CanHaveResource`
accepts Sugar on revealed, empty, unowned **722** (Grass/Marsh). It rejects Sugar
on **720** (Grass Hills); Tea is suitable there, but would still consume that
customer footprint. Thus the earlier Sugar-on-720 idea was unsuitable for two
independent reasons. The controlled preparation uses 722, preserving 720.

`boston-material-strong-prepare-01` then completed at turn 22 with zero turns
advanced, native SaveComplete, matching native/archive hashes and normal cleanup.
The common derivative SHA-256 is
`bdcd0d5e9f77e494ef2e7467fa8ad3c29c0167260561bfca07401ebd241aedd1`.
It contains exactly the declared ownership and Sugar edits at 722; treasury
remained 45 Gold. The actual main-policy survey reports Base 1, Specialty 1,
pending 0, adjacency 4 and +12,288 Q8 for 721. The independent geometry survey
retains future-host 720 and viable Specialty 722. These qualify a controlled
test input, not a native decision effect. Both arms must reopen this exact save.

The maintained runner checks original provenance, the derivative's verified
preparation/closure, both saved hashes and persisted Sugar ownership. The
diagnostic initial-offer guard accepts only the existing +24/+48 bands. Five
Lua helper checks and nine discovery checks pass, including rejection of changed
source facts, a missing mutation API before either edit, duplicate offers and
gap-derived bid 10,730. Astra reviewed the fixture and these scientific guards.

## Strong-material pair: changed native choice, no construction yet

**AI-C151 closes Problem 1.1 levels 1–3** at the representative scope of a
material-aware, owned Quarter choice/request. Astra independently verified the
source, isolated initial packet, native result and both terminal sessions.
This later result does not overwrite the first pair's valid negative result.

Artifacts: `boston-material-strong-control-01` and
`boston-material-strong-treatment-01`, under the same artifact root above.
Both reopen the exact prepared derivative and run 22→33. Package manifests
differ only in the staged publisher; its text differs only in the control
Boolean. The initial retained packet differs exactly by
`(3,131073,36,721,+12288)`; all other initial entries match and the other four
policy-array counts are zero in both arms. The extra resource can affect native
valuation too, so **compare these two arms to each other**, not to the original
Campus result.

| Observed native path | Control: target offer removed | Treatment: ordinary main offer |
| --- | --- | --- |
| First Boston district choice, 22 | Government Plaza, logged value 96 | Bakers, logged value 124 |
| Reserved plot | 796, Cattle | 721, supplied Quarter site |
| Target cache | No staged target | 19,623→31,911 Q8, exact +12,288 |
| First completed target receipt, observed 23 | Staged 0 | Write 1, eligible read 1, city selection 1, site win 1 |
| Quarter request | Absent | Contract 225 submitted on 22 |
| Later outcome | Government replaces Cattle by 29 | Bakers plan retained through 28, then Preserve selected on 29 |
| Quarter foundation/completion through 33 | Absent | Absent |

Both `complete.json` records verify 11 turns. Both `session-closed.json` records
verify normal exit, owner absence, preferences and packages. Treatment retained
Cattle 796 through 33, but it remained unimproved. That is an incidental
consequence of choosing the Quarter instead of Government, not an independent
material-protection ablation or evidence of a working Service.

The treatment is the reusable main CSC scanner, supplier reader, site model,
publisher and CE adapter operating on live facts. Only old-save role metadata,
receipts and the control's one-pair removal are diagnostic. The fixture's map
coordinates do not enter shipping policy. This demonstrates joint district-type
and site choice, **not relocation between two Bakers sites**.

**Limits:** 1.5 acquisition and 1.6 construction remain open. Do not also close
1.4: the pair isolates the whole positive offer, not the strong-over-viable
increment. In this source, the +24 band would yield 25,767 Q8 (100.65 utility),
already above Government's logged 96. A future-customer-point ablation that
only changes +48→+24 is therefore unlikely to change this initial choice.
The active next acceptance is 1.2: trace a mapped existing or specific feasible
future customer's contribution through policy and a controlled native choice.
