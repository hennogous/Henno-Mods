# Material care v1: first native-incentive pilot

Authorized23October after the own-first pilot and the tuning-only comparison.
Earlier work is committed/pushed; old games and monitors remain closed.

The candidate combines independently authored ideas from the read-only AI-mod
review: RH-style state-sensitive demand, AI+ Builder production-contract freedom,
and Real Strategy's distinction between job demand and Builder production.
It does not copy their code or import their general Farm/Mine preference skews.

- Existing exact-material presence40 and matching improvement-owned80 remain.
- A player-owned raw-supply signal adds160 for a Quarter's last Base,80 for its
  last Specialty, or20 for redundant supply. Only the strongest category applies
  to a physical tile, even if several Quarters share it. This private planning
  value persists through pillage and includes unfinished Quarters. It is a soft
  valuation hypothesis, not a resource reservation or replacement veto.
- A plot backlog distinguishes working, repair, legally developable, unsafe,
  inaccessible, unknown legality, and locked/illegal supplies. Missing improvements
  count only when native CanHaveImprovement and research gates pass. Repairs do
  not consume a charge. Existing total Builder charges are a conservative upper
  bound on capacity, not evidence of nearby idle units or safe paths.
- A native strategy raises Builder preference100 and improvement valuation100%
  only while missing-work count exceeds total charges, or repairs exist without
  any Builder. Existing global Builder50/improvement90 remain unchanged.
- Build City Improvement production nodes13/23 may contract a Builder in any city
  (Required City=-1). No unit is assigned, purchased, granted or moved by this code.
- Native events invalidate cached player scopes. Activations/callbacks rescan
  only Quarter neighbors and Builder units; one initial property cleanup scans
  the map. Work-state changes and material loss are retained in a compact ledger.

The first test targets225, the common comparison checkpoint. Same seeds830405/
940411, roster, Ancient/Online/Prince/Small Continents and resource pass as the
previous own-first game. Its player0 was defeated232, so225 is the declared endpoint,
not a relabeled250 pass. Keep actual AI-funds-first/shortfall-only donations,
quoted assisted assignment, legal0% foundations and light25-turn outcome captures.
No strategy-to-Service matching, forced research or direct Builder orders.

Validate Lua5.1 guards, native-schema/replay, loaded modifier attachments, tree
rows and actual runtime callbacks before calling the mechanism native-validated.
Offline success does not show that replacement/repair evaluators consume the
signals. The test must measure last-Base losses, improvement/pillage/repair state,
Builder capacity/demand, Both retention, customer buildings and eligible sales
links; payments remain unobserved. Report unsafe/locked work separately and do
not infer exact paths or repair actors from a changed endpoint.

Run evidence: Desktop/Codex/csc-material-care-v1-20261023/run-01. Installation is
an isolated512-file candidate over the preserved current510-file package. After
audit, normal exit and all Civ processes absent, restore the pretest510 package
and original144 preferences. Preserve source fixes and unrelated work.
