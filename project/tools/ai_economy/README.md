# Economic model checks

These tests execute the real Lua 5.1 model/fact/adaptor code through `lupa`.
They verify economic and publication invariants; they do not simulate a native
winner, construction or Service. Install `lupa==2.8` in the chosen test Python.

From the repository root:

```powershell
python -m unittest discover -s project/tools/ai_economy -v
python -m unittest discover -s project/tools/ai_workshop_bridge/ce_frontend -v
python -m unittest discover -s project/tools/ai_site_planner/adjacency_policy -v
python -m unittest discover -s project/tools/quarter_contracts/tests -p test_quarter_district_capacity.py -v
```

The shared-controller fresh-game driver optionally accepts `--economy-preflight`.
Its endpoint reads validate native price calls, numeric fact bindings and loaded
district-slot definitions. It grants no unlock, bid or world edit. Main CSC is
the only policy in those runs. Exact runtime versions and receipts are in the
[13 November evidence record](../../docs/research/mods/csc-ai-central-economy-20261113.md).

On Shadow these checks used Python312 with an isolated `lupa` installation at
`C:/Windows/Temp/csc-ai-economy-python` on `PYTHONPATH`; this temporary dependency
is not mod content or part of the CE build.
