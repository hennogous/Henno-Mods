# Native SQL customer adjacency: coverage and strength

Henno directs **2.1** to verify the native SQL incentive and its strength before
adding other customer-placement approaches. Customer/building relationships must
come from existing gameplay definitions, without a second AI-maintained map.

## Found: Stage3 routing migration left native edges missing

The completed calibrated250 game's loaded database contains24 private-yield
district/Quarter edges. Its transaction registries imply30. Six transaction edges are missing:

- Commercial Hub beside Bakers and beside Tailors.
- Holy Site beside Tailors.
- Suguba beside Bakers and beside Tailors.
- Lavra beside Tailors.

The SQL generator reads `CSC_QuarterCustomerBuildings`. Population-scaled Stage3
sales moved into `CSC_Stage3CustomerTransactions`, so their customer districts
no longer appear in that first table. The central economic facts reader already
reads both registries; the native SQL generator did not. Its unit fixture still
put Stage3 rows in the old table, hiding the migration gap.

This corrects the preceding inference that the Commercial Hub incentive was
merely too weak. The original game's archived native database and a cold150
reload both lack that rule. The first diagnostic updates a missing row, rejects
its database preflight and advances no turn; its175-row structural census matches
and its cleanup is retained.

## Data-driven repair

`CSC_AI_Connectors.sql` derives its temporary edge set from both gameplay
transaction registries and the gameplay `_SALES`/`_GOODS_PROVIDER` district tags,
then expands direct district replacements. The edge primary key deduplicates repeated stages/buildings and
provider overlap. The list is generated output; no new authored interaction map
or fixed Bakers/Tailors customer list is introduced.

An audit independently derives the expected graph from the loaded definitions.
The first transaction repair changes24/30 to30/30 coverage. A broader audit of
existing gameplay sales tags then finds **18 further missing links**: nine loaded
City Lights urban district types for each Quarter. These are tag-defined sales
partners without a specific customer-building transaction row. The final generator
consumes those tags too, reaching **48/48** on the native-schema database copy.
No City Lights district names are authored in the AI generator or its audit.

The Quarter key is derived from its gameplay district's standard CSC name; the
same sales/provider tags already drive the Lua siting reader. Adding a gameplay
tag-only partner, even to a new Quarter with no transaction rows, now creates its
native signal. Tests cover this, overlap and absent optional-mod district types.
Generation and auditing happen once at database setup/preflight, adding no
recurring Lua scan. Core/Stage3 and City Lights definitions load100/101; the
connector action loads480.
It explicitly routes City Center settlement and exact Wonder hosts outside this
ordinary district-placement signal. The updated fixture uses the real split
registries and proves that adding a gameplay-defined test Quarter/customer
requires no AI mapping update. Future full-game preflight checks the complete
customer graph rather than only Harbor/provider examples.

## Controlled native replay

Source: the latest ordinary calibrated Continents save150, map21951115/game32151115,
CSC de174092 plus the SQL repair. Same frozen CE1be0545b; native XP2092abfbb.
WildW develop remains2986a746/mastere59b5aa9 when checked before testing.
Ghidra's324c51e9 reference and the live binary have identical full.text bytes,
SHA d5bc8feddb8c030dbf2afc3fa9d9110eadbdb349cdb8aa56d5928625290c3d79.

The production SQL generator runs in every arm as an identical final diagnostic
action. Only the Commercial Hub/Bakers rule's amount varies0/1/4/8; rule/yield
identities, bias and other edges remain fixed between arms. Main CSC Lua remains
unchanged. No district, queue, population, ownership, gold or unlock is forced.

The shared controller cold-loads150 and verifies structure. A read-only survey
records owned/legal footprints and fresh native site quotes. Short150→155 play
captures complete cached district/site matrices at the existing qualified
post-GetBestDistrict selection boundary in four specified cities. These signed
Q8 values are the actual consumer's comparison, separate from diagnostic
instant-ready intrinsic/site-cost quotes. Matrix capture is opt-in and absent
from normal full-game instrumentation.

The four dose arms use the **first,30-edge Stage3 repair**, before the broader
City Lights sales-tag correction. All four load the same175-row saved-world
structure, record18 full native matrices each and close with native exit0 and
preferences restored. The matrices have37 plot rows and54 loaded district columns;
there are zero hook faults or buffered records.

In Qaraqorum (player5/city65536), Bakers1452 has a legal empty riverside neighbor,
plot1379. At the first native150 comparison:

| Commercial Hub site | Signal0 | Signal1 | Signal4 | Signal8 |
| --- | ---: | ---: | ---: | ---: |
| Beside Bakers,1379 |2818.348|2864.047|3001.293|3184.242|
| Away from Bakers,1601 |2838.164|2838.164|2838.164|2838.164|

Values are native utility (signed Q8 divided by256). +1 contributes45.699 utility
to1379 in this comparison; across the four scoped cities the measured effect is
35.2–48.2. First-comparison ownership, frontier, reservation and eligibility flags
match across arms. Other district columns can change through native alternative-
land valuation, so this is an input processed by ordinary valuation.

At native154, the actual Commercial Hub selector chooses1601 with signal0
(value3376.324), and1379 with1/4/8 (3405.129/3549.848/3742.793). Earlier150–153
choices match across arms. This establishes native consumption and a desirable
selected-site change. Construction follows a later phase: neither candidate is
founded by the inactive155 endpoint. **Keep the default+1**: increasing strength
adds no site-choice benefit in this controlled example. An ordinary follow-up
run can measure customer foundations and Services with the complete graph.

A separate zero-turn150 cold-load qualifies the final48-edge graph; it is kept
separate from the isolated30-edge dose comparison. It verifies **48/48 loaded
links**, no missing/unexpected/invalid/duplicate rules, and175/175 unchanged
structural rows. Native exit0, preferences restored and package checks pass.
Receipts are under `all-partners1-survey150`.

[Compact matched-dose measurements](csc-ai-native-customer-signal-20261116.json).
Artifact root:
`C:/Users/Shadow/Desktop/Codex/csc-ai-sql-customer-signal-20261116`.


## Corrections and retained evidence

The initial cold-load fails the missing-rule preflight without advancing play.
The first repaired attempt then exposes a Python tuple/Lua encoding error before
play; its owned process needs recorded forced exit after graceful exit stalls.
The encoder is fixed and regression-tested. The four completed dose arms all
close normally. Read-only150 checkpoint provenance and opt-in full matrices are
reusable diagnostic tooling; ordinary games do not capture full matrices.

City Center settlement and specific Wonder-building buyers remain separate
consumers. The audit lists their gameplay definitions as explicit exclusions;
boosting generic DISTRICT_WONDER would favor unrelated Wonders too.

79 economic/Lua checks and31 targeted replay/observer/continuation checks pass;
SQL layout passes. The trace/result helpers and small native journals preserve
exact values, identities and cleanup receipts. No CE API or DLL change, no new
customer planner and no upstream PR are part of this repair.


After all sessions closed, ten redundant generated CSC/CE package copies from
these five successful arms were checked against their complete manifests and
removed (2,066,368,689 bytes). The original frozen source packages, per-arm final
SQL/modinfo, manifests, implementation snapshots, native journals and lifecycle
receipts remain. Reconstruct each tested package from its unchanged frozen source
plus its archived diagnostic SQL/modinfo. `package-prune-receipt.json` records the
exact generated paths. Baselines and replay-source saves are preserved.
