# Experimental district score bridge

Research prototype for the pinned Windows XP2 GameCore build. This is not an
installed CSC component or a general mod loader. Importing its Python modules
does not start a game or attach instrumentation.

`kernel.c` supplies native CModule callbacks. Its only gameplay write is a
bounded signed32 addition to the ordinary district NetValue output. The returned
pointer, input arguments, original evaluation and native legality remain intact.
Zero and the invalid sentinel are preserved; overflow and sentinel collision
leave the score unchanged. The first game profile admits one exact original-AI
player/city/district/site and allows at most one +256 Q8 change.

The remaining hooks observe the scoped city's completed district cache, native
winner and present value. They cannot establish actual construction or useful
economic outcomes. PresentValueOf receives a nullable **plot pointer**, whereas
GetBestDistrict writes two int32 coordinates. Entry fingerprints and the PE
identity must match the reviewed build.

## Separate the verification levels

- `run_synthetic.py`: actual Win64 calls in an owned disposable Python process,
  Frida17.24.3 and native CModule callbacks. No Civ operations. Tests argument and
  pointer preservation, arithmetic, filtering, recursion, joined native workers
  and memory guards. The host has a45-second watchdog.
- `test_source.py`: the actual reader in Lua5.1 with mocked game bindings. Tests
  source admission and Gameplay-compatible district enumeration; it does not
  prove those bindings are available in the running game.
- `live_probe.py`: one exact existing save and one250→251 interval through the
  shared controller. `baseline` never writes a score. `treatment` requires a
  qualifying prior baseline and a separate invocation; it is not an automatic
  follow-up or retry. No fresh world or forced order.

Use explicit dependency and new output directories. Existing Frida and Lua51
dependencies are supplied by the operator, not downloaded by these scripts.
Do not infer in-game performance from the synthetic timing.

Pass `--fixtures project/tools/native_ai/district_score_extension/test_cases.json`
to the synthetic runner for the27 explicitly selected independent decision-core
cases. The full91-case pack is retained for its original contract context; the
runner does not execute all of it. Fixture success is not native gameplay proof.
The live driver also requires this workspace's existing `ai_tuning` and shared
controller tools; this directory is not a standalone distribution.

## Scope and lifetime

The prototype uses one immutable, host-qualified single-load window. Session,
epoch and version are labels for that window, **not observed native analysis
generations**. It is not a solution for policy refresh, cross-load persistence,
multiple worlds, arbitrary callbacks, save recovery or shipping compatibility.
Memory-region checks do not pin engine object lifetimes.

The live daemon freezes writes before Menu, drains admitted original calls and
retains all Frida/module references until the held native process exits. It
does not detach or unload while Civ is alive. The active counter tracks admitted
frames, not every rejected hook entry; native exit is the final lifetime barrier.
Disabling is not rollback: caches, requests and autosaves can retain influence.
Always load the exact unchanged original save for an untreated reference.

Game settings/logs live under the local Firaxis user root on this host; native
save files live separately under Documents/My Games. Pass both directories
explicitly. Source and installed-file pins remain frozen throughout a run.

Results and the current interpretation belong in the
[AI handbook](../../../docs/civ6-ai/topics/native/native-placement-extension.md).
