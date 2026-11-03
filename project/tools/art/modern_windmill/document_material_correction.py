"""Promote completed material correction evidence into current project references."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
status='''**Current material delivery, 27 October:** buildings **r006**, props **r004**.
The corrective normal pass (buildings r005 / props r004) replaces the rejected
threshold/noise treatment with registered masonry joints, folded roof seams,
recessed glazing and traced timber grain. Twelve saved-assembly diagnostics cover
both mills: B-only, neutral normals off/on under two light directions, and combined
materials. Agent visual review, native DDS readback and isolated SDK cooking passed.
Human visual acceptance and in-game appearance remain unverified.

Buildings r006 retains those corrected normals and adds a **256x256 emissive atlas**
with warm, softly edged window panes. The reusable base and Water Mill masters
have UV3-only updates; native geometry, UV1/UV2, B, AO and saved AST placements are
unchanged. Wind Mill inherits the shared base. The dark historical/modern comparison
uses a faint emission-only preview halo; this is not verification of game bloom.
The portable rebuild retains `sources/registered_E.png`. Current master paths
below remain unchanged. Backups, validation, cook results and review images are at
`C:\\Users\\Shadow\\Desktop\\Codex\\modern-normal-correction-20261027` (emissive subfolder
for r006 publication). No new B artwork or geometry was introduced in this pass.
'''
p=ROOT/'project/docs/art/modern-building-kit.md';s=p.read_text(encoding='utf-8');a=s.index('**Subsequent material feedback');b=s.index('Latest refinement',a);s=s[:a]+status+'\n'+s[b:];s=s.replace('Latest refinement, 27 October: buildings release **r004**, props **r003**.','Earlier paint/layout refinement, 27 October: buildings release **r004**, props **r003**.');s=s.replace('Current atlas releases: buildings `2026-10-27_Modern_r003`, props','Earlier AO allocation release: buildings `2026-10-27_Modern_r003`, props');s=s.replace('1024² surface pages, 2048² AO from r003.','1024² B/N/G/M pages, 256² E from r006, 2048² AO from r003.');p.write_text(s,encoding='utf-8')
p=Path.home()/'.codex/skills/civ-supply-chains/references/art-modern-kit-and-atlases.md';s=p.read_text(encoding='utf-8');a=s.index('Henno subsequently described');b=s.index('## Current painted kit',a);s=s[:a]+status+'\n'+s[b:];s=s.replace('Supersedes the scattered historical UV1 slot layout. Buildings r004 and props\nr003 are current.','Supersedes the scattered historical UV1 slot layout. The layout began with buildings\nr004 and props r003; current material releases are buildings r006 and props r004.');p.write_text(s,encoding='utf-8')
p=ROOT/'memory/project_modern_water_mill.md';s=p.read_text(encoding='utf-8');s=s.replace('This follow-up edits guidance/documentation only; actual normal repair pending.','That guidance-only follow-up was superseded by the completed correction documented above.');p.write_text('# Current: corrected normals and compact emissive installed\n\n'+status+'\n'+s,encoding='utf-8')
print('UPDATED_CURRENT_MATERIAL_REFERENCES')
