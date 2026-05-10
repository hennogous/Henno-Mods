## New-session startup reading order

When starting a new Codex session for CSC, the fastest useful reading order is:

1. `memory/MEMORY.md`
2. The most relevant recent `memory/project_*.md` files
3. `project/README.md`
4. `AGENTS.md`
5. The exact implementation file(s) for the current task

Use task-specific follow-up reads after that:

- Quarter gameplay work: `Civ Supply Chains/Data/CSC_Q_BAKERS.sql` and `project/docs/QUARTER-PLAYBOOK.md`
- MAB / adjacency work: `project/docs/MAB_MANUAL.md`
- Art kit / building work: `project/docs/ART-KIT-3D-PASS.md`, `project/docs/BUILDING-SHAPES.md`, and export pipeline docs
- FireTuner / live test work: `project/firetuner/FIRETUNER-PROTOCOL.md` and `project/tools/firetuner/`
- ComfyUI / icons / SV work: `project/docs/COMFYUI-SETUP.md` and `project/docs/strategic-view-sprites.md`

Short version:

- Read memory first for current state
- Read `project/README.md` for the doc/tool map
- Read `AGENTS.md` for operating context
- Read the specific file being changed before acting
