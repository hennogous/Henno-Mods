# RH-aligned Builder tuning v4 — interrupted native test

The matched seed-1 game did not reach its turn-250 endpoint and is excluded
from completed baseline/v1/v3 comparisons. A [matched turn-200 comparison](csc-ai-rh-builders-20261017-turn200.md) now uses the valid archived progress from all four runs. It shows higher improvement density, while the turn-250 comparison remains unavailable.

## Treatment and controls

CSC changed the improvement pseudo-yield base to 90 and the native major-civ
Builder unit priority to 900, following the inspected RH revision. CSC's own
+50% improvement preference was removed. Bonus-resource12, river4 and reciprocal
sales10 placement signals were unchanged. RH and TAR were disabled.

Online/Prince/vanilla Standard, Small Continents, six majors/nine city states;
map seed830102 and game seed940104. The starting world matched the baseline
exactly. Native DB validation confirmed90/900, 33 sales edges, four resource/river
attachments, no former CSC percentage layer, and unchanged loaded SQL on
reapplication. UI filtering passed.

## Interruption and preserved evidence

The 17 October scheduled check found both Civ and the controller absent.
The controller's last saved status was a second failed debug connection at
14:30 CEST, with last confirmed turn230. The native log also contains turn232,
and the newest autosave is named AutoSave_0234.Civ6Save. No controller traceback
or completed endpoint was recorded. The user subsequently confirmed that Shadow died. This is a reported host failure, not evidence of a Civ-native crash or tuning defect.

Nine primary censuses (1 and every25 through200) have zero observer errors.
The supplemental Builder census at200 also has zero observer errors. Tuning
source hashes still match the launch pins. Censuses225/250 and the completed
final save are absent; transient observer history after200 was not recovered.
The automatic turn-250 comparison was therefore not run. A separate offline analysis compares all four real turn-200 snapshots without fabricating later state. Historical trials
lack Builder production instrumentation in any event.

Evidence root: `Desktop/Codex/csc-ai-rh-builders-20261017/`. Original log tails
and status files were archived under `trial/failure-logs/` before opening Civ
for preference cleanup. Autosaves232/233/234 were copied to
`trial/failure-autosaves/`. The separate turn1 observation-export repair remains
under `preflight-failure/`; it involved no autoplay and no map restart.

No new game or automatic rerun was started after interruption. The scheduled
follow-up was deleted. Preference cleanup opens only the hidden main menu,
restores the original141 mod flags and disabled native auto-start, verifies
them via the game API, and closes Civ; see `trial/preferences-restored.json`
for its confirmation.

Cleanup confirmed at15:45 CEST: native API freshly verified all141 original
mod flags and auto-startfalse, then accepted the close command. No new game.
