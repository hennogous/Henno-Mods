# Repository preservation and publishing cleanup — 3 November 2026

Henno explicitly requested sensible commits/pushes for CSC and installed skill
repos until clean, plus a new civ6-ai repository, while the test game runs.
Preserve existing changes; no reset/clean/discard operation was used.

CSC reviewed1258initial changed/untracked paths, about361MB existing content.
Separate commits:1a62664 gameplay/trade/lenses; e96c13c modern art and cooked asset
preservation checkpoint; bab93f9 historical AI tooling/shared controller;
54c6091 project/session documentation. The final separate adjacency-policy commit
includes the Online100 evidence and current handbook reconciliation.

QA found two stale reference locks. Reviewed current lens/trade source against
existing intended contracts; normalized Bakers SQL LF, removed an obsolete
contradictory duplicate Cafe +2Gold bullet, regenerated localization and refreshed
reference hashes without changing phase approval/acceptance states.177contract
tests pass. ModBuddy actions check and localization --check pass. Lens lifecycle,
flows, readiness and Service-marker checks pass.526XML/973Python/53JSON sources
parsed at the preservation checkpoint. This is structural validation, not a new
visual/cook/runtime acceptance of every art asset.

Shared controller153tests pass using package discovery (-t project/tools/ai_baseline),
isolated temp root, existing Lua test deps and explicit actual LOCALAPPDATA.
Updated war and checkpoint test fixtures for existing guard/UI-phase contracts;
no running controller source was edited. Other historical AI tools were preserved,
not reactivated or claimed newly game-validated.

Skill repositories allprivate, validated frontmatter/relative links, clean/pushed:
civ-supply-chains99feb70 (also repaired23mojibake sequences/canonical site links),
civ6-art6773c69, civ6-gameplay4b9e618 (master), newciv6-ai080116a(main).
GitHub connector lacks repository creation; existingauthenticatedgh created
hennogous/civ6-ai with SKILL.md and a concise packaging README. Existing PyYAML
from Desktop/Codex/csc-adjacencies/test-deps enabled the actual skill validator;
no new dependency installation was needed.

Publishing must refresh catalogue/build hosted profile/verify and confirm Pages;
final receipts outside the repository hold commit/deployment hashes and clean
upstream parity. Generated handbook outputs remain ignored. Runtime evidence
stays in Desktop/Codex; no game binary/database/save was added to Git.
