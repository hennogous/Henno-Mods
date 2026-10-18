# Terrain-aware native QA and manual testing handover

15 October 2026: Henno saw ocean placements in QA and challenged the fixture's
validity. Do not hard-code coordinates and terraform water into land. Understand
terrain/resource/improvement/district requirements, then algorithmically find
viable map candidates. Preserve terrain, features, ownership and normal legal
placement; report unsupported scenarios as blocked/inconclusive. Native purchase
success does not make the rest of an invalid fixture legitimate.

Draft read-only planner: project/tests/qa/placement.lua and
project/tools/qa/plan_materials.py. Existing helpers now reject unsafe legacy
setup. Draft changes have NOT been tested; old smoke/full-run integration still
needs completion. Do not count previous 127 offline tests as validation of this
new draft. Placement-dependent prior native results are qualified in the fix
report. Static arithmetic and saved notification cache evidence remain separate.

Latest explicit instruction: Henno will run his own tests now; automated tests
can run later. Leave Civ entirely under his control. Do not start games, change
preferences, move units, modify saves or run automated game checks until he
resumes them. No scheduled wake-up was requested.
