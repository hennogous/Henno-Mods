# Discworld map prototype — 10 November 2026

Separate user request, unrelated to CSC content. Source and reproduction notes:
`project/tests/discworld-map-prototype/README.md`. Output and command journals:
`C:/Users/Shadow/Desktop/Codex/discworld-prototype-20261110/`.
Prior REA/static map findings are in the sibling
`discworld-map-feasibility-20261109/` output directory.

Circular 48×56 nonwrapping map runs in the installed game. Exterior custom
feature blocks a destroyer's native path after Cartography gives ordinary ocean
access. Full mask census passes. Ice art is an obvious placeholder. User's latest
priority is seeing the Rim and best Rimfall v0.1. Stock particle arc is a visual
study; it does not remove the flat ocean or create a floating disc.

Respect Shadow's prohibition on desktop automation. Native `UI.Screenshot()`
writes TGA into the game's Screenshots directory; Pillow converts it for review.
Use `UI.LookAtPlot` first and `UI.SetMapZoom` in a subsequent command: LookAtPlot
without a zoom can overwrite a preceding zoom request. Zoom near 0 is close;
0.8 is wider. `AssetPreview.SetInstancePosition(id,x,y,z)` accepts Z, verified
through GetInstanceInfoByID. Preview instances are not saved with game state.

Restart the game after changing the mod manifest; reloading a save inside the
same process retained the old component list. Original 151 exact installed-mod
preferences were journaled, restored and compared successfully. Final auto-start
was reset false after the last test load. No broad git commit/push requested.

Final package reload and native screenshot passed: 228 VFX instances at valid
positions. Early creation produced huge uninitialized GridToWorld coordinates;
fixed by waiting for LoadGameViewStateDone. Final screenshot is
`screenshots/rimfall-v01.png`; `disc-overview.png` shows the complete circle.
The spray still looks like surf over an ice barrier, not a convincing abyss.
Five-turn autoplay stalled at turn 1 and was stopped; no campaign success claim.
