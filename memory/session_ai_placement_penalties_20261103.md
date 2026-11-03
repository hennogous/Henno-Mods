# Weak Quarter placement penalties —3 November2026

Henno requested researching how to discourage weak native placements, extending
the existing adjacency policy, and running a new test game. Report:
`project/docs/research/mods/csc-ai-placement-penalties-20261103.md`; AI-C050.

V2 retains+1048576 Q8 for the best eligible>=4 pair/city. Every observed sub-4
pair receives-ceil((4-total)*65536), capped262144. Exact multi-pair keys per city;
signed native comparisons allow negative winners. Future-building uplift only
applies above zero; positive district preference multiplies by1.5. Zero/invalid
results preserved; negative floor-1048576 avoids introducing no-result values
even after that observed multiplier. No old request rollback or forced orders.

19policy checks,40actual native-host checks,9Lua scanner checks,153controller
Python checks passed. Historical100-scan replay:8289weak observations/max133
entries. Native/source identity exact pinned XP2. Research agent read-only Ghidra
confirmed selector; no native session or game changes by that agent.

Fresh driver launched21:58:53 local on3Nov, same Online/Ancient/Prince/Small
Continents/6majors/9citystates/map16131103/game26131103, endpoint100, CSC only.
Evidence:`Desktop/Codex/csc-placement-penalties-20261103/run-01`.
Shared controller/session owns all game control. Original humans excluded.
All driver/HERE/shared/installed sources frozen while worker runs; only offline
parent analyzer, docs and memory may change. Human reporting every15minutes.
**Current status:** initial turn1/source/module checks passed; game active.
Do not start another game or edit pinned files. Finalize results/closure later.
