# Multiplayer runtime hardening — 20 October 2026

User authorized fixing deterministic writes, trade-route authority and loading
hooks, explicitly **no game launches**. Implemented in source only; no deployment,
build/cook or native tests. Durable details:
`project/docs/integrations/csc-multiplayer-hardening.md`.

- Sorted adjacency sites/stale clears, population registries/cities/keys/properties,
  art city iteration and Wonder stale markers. Actual alive players replace count
  ranges in population, art and trade scans.
- Network host UI alone submits trade snapshots via EXECUTE_SCRIPT, using local
  sender ID and separate city identity. Fixed-field receiver validates turn,
  owner/city/coordinates, counts and saved expected revision; derives bits and
  increments revision last. Host migration rechecks current host; UI coalesces
  events and retries fresh state while operations are outstanding.
- No direct gameplay startup/load callbacks for these four reconcilers. Shared
  GameEvents.PlayerTurnStarted/OnGameTurnStarted plus normal gameplay changes.
- New 12-case executed-Lua suite includes forced iteration differences, loading,
  queue/duplicate/stale/malformed input, host migration, hotseat routing, sparse
  player IDs and two-peer traces. 50 focused/existing tests +14 QA regressions pass.
  QA uses frozen DB via CSC_GAMEPLAY_DATABASE; current cache duplicates M&C setup
  before scripts execute. Policy220 and parity1465 pass; action JSON check passes.
- Existing other workspace changes retained. No SQL/design/gate changes. Dormant
  unit-level adjacency UI read remains outside MP certification. Native two-machine
  validation, including host sending AI/other-human city updates, remains pending.
