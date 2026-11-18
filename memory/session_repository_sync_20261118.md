# Repository sync — 18 November 2026

Henno requested sensible commits and pushes for CSC and all skills, explicitly
including civ6-ai. Reviewed the pending source, UI assets, localization, test
tools and notes; kept disposable project/.ai-test-tmp contents and root native
self-test binaries/intermediates on disk and added narrow ignore rules.

Offline checks passed: localization generation, ModBuddy JSON/project parity,
11 ModBuddy tests, two Lua 5.1 Civilopedia tests, adjacency edge and tooltip
regressions, 251 policy gameplay/UI cases, ten local Mill tests, and the complete
Quarter lens suite. Updated one stale lens test to compare Wonder hosts against
the SQL registry now consumed by placement instead of removed Lua literals.
Python syntax and XML structure checks passed for changed/new source files;
git diff --check passed. No live game, desktop interaction or cook was run.

All four Git-backed skill checkouts were clean and matched their fetched remote:
civ-supply-chains ba386aa, civ6-art 6773c69, civ6-gameplay ff98243,
and civ6-ai 66b45bc. The installed reverse-engineer-anything and typesafe-ai
directories are not Git checkouts and have no configured repository to push.
