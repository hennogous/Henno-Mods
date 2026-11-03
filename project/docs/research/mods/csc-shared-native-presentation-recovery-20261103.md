# Shared-controller recovery for discovery and project popups

3 November 2026. This fixes a shared automation gap exposed by the
[native Quarter choice trial](civ6-district-placement-choice-20261103.md).
It is infrastructure work, not an AI placement policy.

## What was missing

The maintained shared controller already acknowledged disaster, diplomacy and
wonder-built presentations. It did not acknowledge the separate shipped
`NaturalWonderPopup` or `ProjectBuiltPopup` contexts. Both can hold event
processing during a finite observer interval.

The first treatment stalled at Core turn 253 while attempting 254. Its retained
log had an unmatched Natural Wonder event lock. A no-adjustment control then
observed the actual visible popup and acknowledged three Natural Wonder
presentations through their shipped `Close()` routine. Each close hid the popup,
emptied its stack entry and logged an unlock. These are three acknowledgements,
not evidence identifying three distinct natural wonders.

The turn still did not advance. The subsequent retained log and visibility
receipts showed **ProjectBuiltPopup lock 61969**, priority 1000, with no matching
unlock. Closing the discovery presentations had exposed another held cinematic.
The control timed out at its declared 600-second limit. It completed 251–253,
made zero score writes and closed normally with native exit 0 and restored
preferences. Its successful cleanup is separate from its failed recovery.

## Permanent shared behavior

`FullGameController.__init__` now installs `presentation_playback` automatically.
Both full-game and probe callers receive the two handlers; a trial-specific
adapter is unnecessary. Existing presentation handling runs first. Natural
Wonder and project-built handlers then each obtain their own fresh proof.

Before a close, the handler checks:

- Core is in an active observer operation with one to five turns remaining,
  with the target clock matching that remainder and the original human alive;
- the UI reports the same turn and the exact shipped popup context is visible;
- for project-built, its stack entry is present exactly once at priority 1000
  and strictly exceeds every other entry's priority.

The exact shipped `Close()` routine manages its own queue, sound, lens/camera,
visibility and event lock. Neither handler submits a gameplay choice, production
order or autoplay activation. An intent receipt is retained before transmission.
An ambiguous response blocks replay. Each handler permits at most eight
acknowledged closes per interval. A confirmed no-op can be checked again with
fresh facts. The Natural Wonder guard records its stack read; it does not claim
to enforce the project-built guard's stricter stack admission.

The fix is committed in `4264f8a`. It does not weaken native experiment budgets,
source parity, unchanged-input gates or normal shutdown/restoration requirements.

## Verification and current limit

Seven portable regression tests passed. The optional Lua5.1 regression also
passed its five priority/visibility cases. More focused retained checks exercised
the actual Natural Wonder guard in 16 cases and the project-built guard in 25
cases, plus controller mocks. These overlap; they are not independent engine
findings. The committed controller candidate separately verified automatic
installation without game I/O and the added alive-state reply field.

A bounded replay of the unchanged original saved game verified the default
handlers in the actual game: three Natural Wonder acknowledgements and one
project-built acknowledgement released their event locks. Three settled Core
readbacks then confirmed **turn254, inactive autoplay, zero remaining turns and
the original human handoff**. The controller proceeded to its next normal
interval. At254, Sydney also had the requested Tailors foundation at the
preferred plot2272, following natural completion of its Bomber.

The incentive, selected tile and score delta are unchanged. The old baseline's archived controller is compared
against the new one with an exact two-line presentation-install exception;
other native and control inputs remain checked. The replay's initial and
pre-decision world facts matched. The Quarter completed at255 and the driver
stopped at its declared completed-preferred condition. Final normal shutdown
also passed: exit0, settings restored, owners absent and all frozen inputs,
source save and installed package unchanged. The independent replay audit
passed54 checks. This verifies the repaired path in this saved-game case;
unknown future presentation contexts still require evidence and scoped handling.

Evidence: `Desktop/Codex/csc-native-placement-choice-20261103/`, staged under
the current chat's visualization root. Relevant subdirectories are
`control-01-natural-wonder`, `project-built-guard-proposal`, and
`treatment-02-shared-presentation`.
