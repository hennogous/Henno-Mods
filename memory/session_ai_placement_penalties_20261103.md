# Weak Quarter placement penalties — completed4 November2026

Henno requested researching weak-site discouragement, extending the current
adjacency policy and a fresh test game. Report:
`project/docs/research/mods/csc-ai-placement-penalties-20261103.md`; AI-C050.

V2 keeps+1048576 Q8 for the best eligible>=4 pair/city and deducts
-ceil((4-total)*65536), capped262144, from observed sub-4 pairs. Native signed
negative values remain selectable. Conservative-1048576 floor, raw0/invalid
protection, exact multi-pair keys and original-human exclusion. Native building
forecasts only boost positive values; district preference can multiply by1.5.
No old tuning, grants, forced foundations/orders, queue or reservation changes.

The Online/Ancient/Prince/SmallContinents world reached100 after source80 recovery.
Evidence:`Desktop/Codex/csc-placement-penalties-20261103/`.
Completed windows:13881 deductions/75 additions/0native errors. Ten promoted
foundations (8Bakers/2Tailors),9completed;4below-4 foundations,3completed;
14total/12complete. Prior positive-only game had23below4, a descriptive comparison
without matched causal or economic-benefit proof. All10qualified/promoted pairs
founded; fresh native Best observed all10. No negative Best return observed.

Four exceptions fully traced in`weak-sites.json`:
- The Hague1170/+1: unlisted at74nativeBest/contract933, first penalty75 gives
  62312->-134296/PVnegative; old4014request selected75, foundation76/complete80.
- Pokrovka2212/+0: unlisted nativeBest/contract1270at92; first listed93; later
  negativePV stilloldrequestselected97, foundation98/unfinished100.
- Delhi1429/+3:66743-65536=1207, finalcache1358358/Best; contract1042, foundation87/complete88.
- Majapahit1829/+1:228808-196608=32200, finalcache1623830/Best; contract1139, foundation90/complete91.
Thus next placement work is earlier native-candidate coverage and final aggregate
penalties; larger early weights alone do not solve coverage/retained requests.
Exact earlier scanner exclusion (ownership/visibility/assignment/legality or
intra-turn changes) unknown. Existing request refresh is a separate contract.

At75 UI human cache caused one warning skip; scheduled retry succeeded. Root's
repair request arrived after play resumed80 and exposed missing probe capture,
causing ordinary driver cleanup, native0/daemon0/prefs restored/owners absent.
Initial statusclaim9allgood corrected:8promoted+TheHagueweak at80. Read progress
again immediately before any future intervention; one explicit skip is not a
persistent stall. Sharedprobe now captures limited read-only phases for active
and inactive handoffs; three exit guards use freshCoreproof with UIclock/local
checks, log staleUIhuman and retain Corehuman/session/participant/choice guards.
161controller checks+35Lua fixtures+20policy/recovery checks passed;40native host
and9scanner checks unchanged. New eligible warning/handoff did not recur in
recovered segment, so repair native validation remains bounded/offline.

Save80SHA6569b8b97489c558212e361772f126ae8c04c054983e83ce88409d8716a65a7c.
Recovery04Nov exactly matched captured cities/districts/queues/candidates/rules/
players, plus installed/dependencies/original preferences. Not full-world/RNG/
cache/fractional-turn parity. Explicit`analysis-boundaries.json` uses recovery80
once; original80 retained reference, partial original80->81(245changes) separate.
No automatic extra games. Both runs fullyclosed, native/daemon0, final100,
installedunchanged/prefs145IDs148entriesAutoStartfalse restored. No owners alive.
Broad older campaign remains paused; no additional game or first-Mill incentive
was started. Maintain15min game check-ins and rich autonomous evidence.

Source commits:b3c85f5 policy;e0b2c95 catalog;0726b96 sharedrepair/recovery.
Final result documentation and publication receipts accompany the evidence bundle.
