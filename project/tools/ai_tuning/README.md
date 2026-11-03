> Retired as the default AI implementation on 3 November 2026. Current-byte code is preserved in `project/archive/ai-tuning-20261103/`. New native placement work lives in `project/tools/native_ai/quarter_placement_trial/`; these historical planners and policies are not its dependencies.

# CSC AI profiles — source candidate

`CSC_AI_ASSISTANCE` is the single master switch, default On. With no supported
RH release, it selects Basic CSC tuning. With RH active, it selects CSC's RH
extension automatically. Off selects neither, including when RH is active.
`CSC_AI_SUBSIDIES` is a dependent switch, also default On, for both active modes.
The independent resource-map assistance option is not changed by these modes.

The implementation and native-validation boundary are documented in
[`csc-ai-profiles.md`](../../docs/integrations/csc-ai-profiles.md).

## Ownership

- Basic alone owns improvement base30, Builder preference of 50, AI Builder movement
  +1, and any-city production-contract parameters.
- Both active modes add CSC Quarter/customer/bonus-resource/river signals,
  adjacent mapped-material improvement values, conditional Service research
  preferences, and the same bounded Both-site acquisition/foundation host.
- RH owns its global weights, units and movement. Its adapter registers CSC's
  private yield in RH's `RHAITags` UI hook. It supplies a missing any-city Builder
  contract parameter only where RH did not author one; existing values stay.
- Experimental raw-resource/early improvement forecasts, last-material care,
  player-wide harvest bans and extra blanket Builder biases are not promoted.

## RH releases

The reviewed ID and final database load order live in
`project/config/csc-ai-profiles.json`. Currently this describes subscribed beta
5.097, ID `2501be3e-9780-4e9f-9506-4ff71cf076cb`. A public release has no invented ID.
When its ID/schema/load order are known, review them, add the alias and regenerate:

```powershell
python project/tools/ai_tuning/configure_profiles.py
```

This changes the JSON action mirror and regenerates ModBuddy CDATA. It does not
build or deploy. Multiple alias matches cannot install duplicate CSC handlers;
that does not make loading two different RH releases together supported.

## Verification

Use an existing Lua51 `lupa` environment on `PYTHONPATH`, and set
`CSC_TEST_NATIVE_DATABASE` to a preserved native gameplay database:

```powershell
python project/tools/ai_tuning/test_profiles.py -v
python project/tools/modbuddy/civ6proj_actions.py check
```

The SQL suite operates on an in-memory copy. It tests arbitrary preserved RH
weights and contract values, rather than relying on CSC and RH coincidentally
sharing the same number. The Lua suite checks funding, one-shot ledgers, stale
UI reconciliation, human exclusion, normal turn callbacks, zero progress and
queue/cost preservation. These are offline tests, not native combined-mode proof.

The new installed host must be tested in ordinary single-player turns, with
subsidies both On and Off, and with the reviewed RH beta. Its economic backend
is paid Gameplay/WorldBuilder city assignment with native quoted cost and actual
treasury debit, not demonstrated native AI PURCHASE. Multiplayer/hotseat economic
assistance is deliberately inactive until synchronization is tested; static AI
tuning still loads. No current open game is modified during source development.

Do not install the Python planner/funded-acquisition experiment on top of this
host. Its mutation adapters now reject a second installed owner. Future tests
of the player feature need an observation-only autoplay driver, not the old
Python intervention loop. Completed study archives and source versions stay as
executed; do not rebuild or rerun them from the new source.
