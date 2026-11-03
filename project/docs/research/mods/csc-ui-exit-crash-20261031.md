# Lens radio-button exit crash — 31 October 2026

## Scope and current acceptance

User stopped the material-follow-through work to investigate apparent hangs,
including UI thread `01a12526-64af-74d3-af07-ac0514fff784` (UI / More Lenses).
That thread was read directly. No additional AI test is authorized by this
report. The narrow source/runtime patch is implemented and offline tests pass;
native zero-AI exit validation is now complete. All three declared cases exited
normally, and the independent artifact audit passed. This fixes the reproduced
shutdown regression; it is not a claim that all UI/input lifetime issues are fixed.

## Actual failure, not a guessed deadlock

The material observation loaded the preserved turn110 save and passed the entire
declared Core reference. Its UI read captured Flax/Honey metadata and Builder
charges. A separate reporter error then called UI-only
`PlayerConfigurations[3]:IsHuman()` in GameCore. It stopped before assistance
pause or autoplay. No AI turn, order, funding or property treatment occurred.
That binding error is not evidence of AI behavior and is separate from the exit
failure. A previous source110 session without that error also failed to exit.

Exact DX11 owner3452, creation filetime134379034009686784, acknowledged one
ExitToMainMenu request, but MainMenu never became ready within180 seconds.
One normal CloseMainWindow request also did not exit. A read-only context
discovery timed out, so the proposed stock UI pre-exit teardown was NOT sent.

External MiniDumpWriteDump captured1,848,855 bytes,56 threads and146 modules,
SHA256 `2bc2b31f76bb65b8dfa8a7ef4f6e73009ac505c59c0cd5d01fa5075f7ab694bc`.
No full RAM dump, debugger injection, Frida hook, process patch or forced kill.
The main thread was waiting on its owned native exception dialog, not shown to
be spinning or blocked on a graphics lock. The dialog reported
`EXCEPTION_ACCESS_VIOLATION`, write address `0x188`.

A recovered exception record and AMD64 context matched that exact write:
HavokScript_FinalRelease.dll+0x1e69a, instruction
`sub dword ptr [rcx+0x130],r8d`, RCX0x58, R8=1. The dump was captured after the
fault; this is a recovered saved exception context, not an OS exception stream.
The address arithmetic independently reproduces0x188.

An isolated helper mapped exact local PE images and captured stack bytes as
non-executable data, then used Windows RtlVirtualUnwind. It did not run target
code or modify the game. The verified original path was:

```text
Havok+1e69a → Havok+119ec → Havok+2b2c6 → Civ+db2854 → Civ+db27b6
→ Civ+87b735 → Civ+92b294 → Havok+6b8f2 → Havok+5f629 → Havok+55d8b
```

At Civ+92b294, restored registers and exact wrapper bytes resolve to
`RadioButtonControl::SetCheck` at Civ+92c290. The preceding branch zeroes DL,
establishing the false argument. This binding attribution is verified; the
original exact Lua source line was not recovered from the VM. Raw stack pointer
scans alone contained misleading candidates and were not treated as call frames.
There is no direct stack evidence for ClearGlobalInputHandler, DestroyChild or
ResetAllWaves as the faulting call.

## Relevant UI code and narrow fix

The actual installed611 package matched its archived manifest. Its lens panel
also matched current project source at SHA256
`5bcf47686f62cbf6db5fda4e3e59647e52775b520ea3fa243aeab8d6c8e483d6`.
Other current project lens support/placement/ArtDef files differ from installed
bytes; their newer source was not silently deployed or blamed for the crash.

The panel calls Close on inactive mode/local-player transitions and on shutdown.
Close previously always requested `SupplyChainsLensEntry:SetCheck(false)`, even
for an already unchecked, unopened lens. That also crosses the binding during
UI teardown. The candidate mirrors the entry's checked state in Lua, updates the
mirror from the registered check handler, suppresses redundant native writes,
publishes the mirror before synchronous callback reentry, and refuses checkbox
updates once shutdown begins. Teardown decisions no longer query that entry's
native checked state. Normal open/close, radio-group and click behavior remain.

Small entry/Quarter-choice and shutdown markers distinguish future call sites.
Only `Lua_UI/Lenses/CSC_SupplyChainsLensPanel.lua` changes in the installed
package; candidate/source SHA256 is
`31b3f49c58a2910ca97d12b547bcc443519f5b10d1e434fda375f20b6470c539`.
Arrows, styles, ArtDefs, rendering, global input cleanup and AI policy are
unchanged in this causal candidate. The review did find other lifecycle concerns,
including a mask buried under a newer popup; they are not claimed fixed by this
patch and are not established causes of this native exception.

Four new executed-Lua fixture scenarios exercise unopened repeated close,
unopened shutdown, active shutdown with an invalid native radio binding, and
normal toggling. The original panel fails the first three and passes normal
toggling; the candidate passes all four. The full256-classification/panel/flow/
stock-PlotInfo suite passes, including immediate/deferred real More Lenses
listeners in the mock runtime. These fixtures establish Lua behavior, not native
teardown safety or rendered appearance.

## Preservation and cleanup of the crashed session

The exact crash dialog button was identified and its native ExceptionDlgProc
branch checked: control1001 performs EndDialog. One ordinary crash-report OK
acknowledgement closed3452 through its own fault handler, exit `0xC0000005`.
No forced termination was used. A separate Menu-only session restored the exact
original145 mod IDs/148 subscription entries and AutoStartfalse, then ExitOK
closed normally. Its session did not load a world or advance AI. All original
296 pinned inputs,611 installed files and source save were unchanged at that
closed boundary. The later single-file candidate deployment is explicitly separate.

## Reproduction and evidence

- Original run: `Desktop/Codex/csc-native-material-followthrough-20261031/run-01`;
  `native-hang-findings.json`, partial UI capture and separate reporter/cleanup
  failure records, `hang-diagnostic/` dump, saved context, genuine unwind,
  binding proof and normal crash-OK receipt.
- Candidate deployment/exit cases:
  `Desktop/Codex/csc-ui-exit-regression-20261031`.
- Staged baseline/candidate and regression output:
  `H/material-followthrough-20261031/ui-exit-fix` and sibling fixture receipts.
- Independent Terra review and Astra review:
  `H/material-followthrough-20261031/ui-hang-review-terra.md` and
  `astra-ui-hang-review.md`. Their initial hypotheses remain distinguished from
  the later genuine unwind. H is this thread's visualization workspace.
- Maintained regression driver: `project/tools/ai_tuning/native_ui_exit_probe.py`.
  It reuses NativeSession/finite controller and performs no AI play. Log-verdict
  fixtures are `test_native_ui_exit.py`; radio lifetime fixtures use the actual
  panel in `project/tools/lenses/test_standalone_panel.py`.

## Native acceptance — complete

Required: two fresh unopened zero-AI source110 Menu/normal-exit round trips, then
an active-lens case that opens Bakers, switches Tailors, closes, reopens and
returns to Menu while active. Require completed shutdown markers, no post-shutdown
radio call, full Core initial/final equality, exact preferences, normal native
exit0, owner absence and only the declared panel delta. Stop on failure and
preserve actual fault evidence. No AI/material test resumes before this gate.


### Actual closed results

| Case | Native owner | UI exercise | Result |
|---|---|---|---|
| run-01-unopened |9444| Leave lens unopened; Menu exit | MainMenu ready, ExitOK0 |
| run-02-unopened |18740| Independent fresh-process repeat | MainMenu ready, ExitOK0 |
| run-03-active |1740| Open Bakers, switch Tailors, close, reopen Bakers, Menu while active | MainMenu ready, ExitOK0 |

All cases loaded source110 once and advanced zero AI turns. The complete Core
census matched its declared reference and remained identical across the UI
exercise. Each closed generation recorded exactly one shutdown, the checkbox
skip, and shutdown completion, with no radio call starting during/after shutdown
and no Lua errors. Native phase readbacks and actual panel markers confirm the
active interactions; they are not inferred merely from sent event names.

Each restored145 mod IDs/148 subscription entries and AutoStartfalse, exited0,
left no owner and preserved298 input pins and the611-file candidate installation.
Root independently verified all three raw result/pin/Core/command/closure sets,
including the absence of autoplay, host, economic, unit-order and research-order
commands. `H/material-followthrough-20261031/independent-ui-exit-audit.json` is the
independent receipt. The patched panel remains installed and matches project
source at31b3f49c; every other installed file matches the pre-test611 manifest.

This is a tested narrow lifecycle fix on current DX11/RH source110 sessions.
The exact original Lua line is inferred from source and the one-file behavioral
change; the native SetCheck(false) binding/fault is independently resolved.
Rendered arrow appearance and every optional mod combination were not visually
retested. Existing lens visuals, renderer/ArtDefs and input logic were preserved.
After this gate passed, the previously authorized material observation resumed
with its separate Core-context reader correction. It completed110 through115
and exited normally with exact preferences restored,296 pins and all611 files
unchanged. Both target resources remained unimproved at the accepted checkpoints;
this is a bounded observation, not an incentive-effectiveness verdict. See
`csc-ai-material-followthrough-20261031.md` for the separate result.
