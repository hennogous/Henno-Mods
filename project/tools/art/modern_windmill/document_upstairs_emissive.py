from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
for p in [ROOT/'project/docs/art/modern-building-kit.md',ROOT/'memory/project_modern_water_mill.md',Path.home()/'.codex/skills/civ-supply-chains/references/art-modern-kit-and-atlases.md']:
 s=p.read_text(encoding='utf-8')
 s=s.replace('buildings **r006**, props **r004**','buildings **r007**, props **r004**')
 s=s.replace('Buildings r006 retains those corrected normals and adds a **256x256 emissive atlas**\nwith warm, softly edged window panes.','Buildings r007 retains those corrected normals and the **256x256 emissive atlas**.\nAll four panes of every upstairs window emit equal warm light; ground-floor windows\nmap to black. The softness is retained. This corrects r006\'s two dim panes and lit\nground-floor window to match the historical building convention.')
 s=s.replace('uses a faint emission-only preview halo; this is not verification of game bloom.','has emission and glow disabled, as requested. Emissive diagnostics are separate;\nthey do not establish in-game appearance. Future side-by-side comparisons must\nexclude emissive unless explicitly requested.')
 s=s.replace('for r006 publication)','for r006 publication; `emissive-r007` for the upstairs-only correction)')
 s=s.replace('current material releases are buildings r006 and props r004','current material releases are buildings r007 and props r004')
 p.write_text(s,encoding='utf-8')
print('CURRENT_DOCS_R007')
