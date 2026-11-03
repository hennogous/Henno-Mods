# Experimental Granary priority v1

These are reviewed-candidate source payloads, not shipping content. Nothing here
installs itself or changes the mod manifest. A later approved test appends
`granary_priority.sql` to existing `ModSupport/ModSupport_RH_AI.sql` and
`granary_priority.lua` to existing `ModSupport/ModSupport_RH_AI_Roles.lua`.
Together with the two separately reviewed host files this is four existing-file
deltas. Preserve every original byte before each append and restore those exact
pretest files through the maintained narrow staging/session protocol.

The payload adds one independent conditional Buildings list containing only
BUILDING_GRANARY, Favored=1, Value=0. It does not replace RH/CSC rows, attach to an
old Quarter strategy, change private forecast40 or add real/private yields.
Its preference is PLAYER-WIDE for the Granary type even though one local gap
gates it; observe all AI3 cities as well as the reviewed target.

Private Game property `CSC_AI_GRANARY_PRIORITY_V1` is nil/inactive by default.
Only this exact reviewed schema is supported, inclusive through131:

```lua
{version=1,player=3,city=196610,source=2711,start_turn=110,deadline_turn=131}
```

The original configured-human mask must contain human observer0 and exclude3,
accepting string/numeric keys. Current autoplay IsHuman is never queried.
The predicate also requires RH mode, alive major3, exact owned city/source,
completed unpillaged Bakers Quarter, functioning Wind/Water Mill, the target
city's owned completed adjacent City Center without Granary, Pottery and at
least one owned/revealed/visible mapped adjacent Base with its exact native
valid-resource improvement and explicitly unpillaged state. City Center defense
pillage is not a functioning-building gate. Resource visibility reads its own
tech/civic prerequisites. No UI bridge or Gameplay CanProduce/queue getter is used;
the driver must check native CanProduce independently at scheduled boundaries.
The Mill check uses city inventory plus its Bakers prerequisite, under this
reviewed city's one-Bakers-Quarter condition. Preflight must retain the independently
verified unique Bakers source2711 and physical Mill location at that source.
No new Gameplay GetBuildingLocation binding is assumed or called. Neighbours
use only the proven Map.GetAdjacentPlot(x,y,direction) binding for directions0..5,
with nil guards for map edges.

SQL identities for row preflight:

| Kind | Identifier |
|---|---|
| Strategy type | `STRATEGY_CSC_AI_GRANARY_PRIORITY_V1` |
| List and GameEvents callback | `CSC_AI_GranaryPriority_V1` |
| System and preference row | `Buildings`; `BUILDING_GRANARY`, Favored1, Value0 |
| Conditions | `Is Not Major`, Disqualifier1; `Call Lua Function`, StringValue callback, Threshold0 |

Read `ExposedMembers.CSC_AI_GranaryPriority.Inspect(3)` for a detached table:

- `flag`: current private flag, when present.
- `predicate`: active/reason/turn/player/city/source, original_configured_AI,
  source_complete/source_unpillaged, functioning_mills, customer_plot,
  granary_missing, pottery and working_base_plots as each gate is reached.
  A binding failure returns reason=predicate_error plus error text.
- `status`: version/flag_property/callback_name/strategy_type/list_type,
  registered, calls/true_calls/false_calls, states, bounded transitions,
  error_count/errors, callback_forms and last_callback raw argument scalars/types.

Inspect is pure with respect to callback diagnostics, Game/plot properties and
orders. Only the actual registered GameEvents handler updates calls, positive/
negative counts, transitions or callback errors. Registration must equal1;
predicate errors or registration errors fail preflight. Missing callback exposure
is unobserved adoption, not successful native strategy use.

`stopped_notifications` explicitly says UNOBSERVED because no native stop-event
interface has been validated. False predicate/callback and native strategy
Stopped, actual preference removal, queue choice and physical completion are
separate evidence. Native removal may lag the predicate. A future native test
must record that lag/coverage gaps and never force callback calls for proof.

Run `test_granary_priority.py` with the existing Lua51 Lupa environment. SQL
fixtures use a read-only preserved native gameplay database, copied to memory
only; set `CSC_TEST_GRANARY_DATABASE` for another host. They check additive rows,
idempotence, non-RH inactivity and preservation of existing RH/Quarter/effect
tables/private40. Lua fixtures cover pure inspection, exact flag/identity,
physical loss/visibility/native mapping, true/false transitions/errors and append
compilation. Offline tests are not native preference or completion proof.
