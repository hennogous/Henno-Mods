# Producer live-effect diagnostic — 29 October 2026

Follow-up to the [paused property calibration](csc-ai-producer-property-calibration-20261029.md).
The question is whether the existing Workshop forecast changes in the live city
when its Base-material property changes, independently of cached UI values.

## Evidence recovered before a new session

The previous closed calibration's GameEffects.log contains target runtime50451,
`MOD_CSC_RH_WORKSHOP_FORECAST_BASE`, owned by District1376273/player3/city458758.
Its effect was removed and reapplied at turn100. The log interval was34.659 seconds;
the guarded Base0 and Base1 setter commands began34.6598787 seconds apart.
The commands verified plot2781, its city/Quarter ownership and actual1→0→1 property
readbacks. This is strong target effect-state evidence despite the UI staying80;
it was missed in the first pass. It does not itself expose the live yield value.

The independent correlation preserves raw lines, command timestamps and file
hashes. Runtime50451 is historical provenance, not an ID assumed stable on reload.

## Verified native and supported API routes

The current-build ChangeYieldChange routine at109dc0 is called by native
AdjustBuildingYieldChange::Apply and ::Remove. It accepts a City::Buildings
component plus building/yield indices and a signed delta. Its stored adjustment
table contains12-byte building/yield/value rows. The live GetYieldChange10c0e0
adds the applicable row to other supported contributions; UI potential getters
instead read a published cached vector.

The diagnostic passively observes these two functions. It filters building147/
private yield7 before object reads, checks component/city identity, and bounds
the stored-table walk. Exact-row absence is recorded as absent/null, not silently
converted into a full live getter value of0. Native replacement aliases are not
reconstructed. No native function is invoked and no native memory is written by
the observer.

Supported GameEffects queries independently identify the modifier by definition
and owner, reacquire its runtime handle, and report the owner requirement set,
individual requirement states and active flag. They are reported API evidence,
not a substitute for the live adjustment observation. Empty subject lists do not
prove an absent effect. The source property is verified in Gameplay separately
from UI/cache readbacks.

## Session scope

One existing source100 save under the current installed package; no new world,
installed changes or AI turns. The target remains AI3 Kobdo/city458758, Tailors
plot2781, unbuilt Workshop147. Only the existing Base property is toggled1→0→1.
Queues, Gold, resources and saved assistance history are preserved. Full known
Core/UI restoration is captured regardless of whether the UI forecast responds.
No scoring efficacy or production benefit is inferred from this paused test.

## Observed outcome: live adjustment responds; UI potential does not

All observations were made at inactive turn100, without AI advancement:

| Evidence | Before | Base off | Restored |
|---|---:|---:|---:|
| Gameplay Base property | 1 | 0 | 1 |
| Base owner requirement set | Met | NotMet | Met |
| Base modifier active | true | false | true |
| Exact Workshop/private stored adjustment row | 80 | absent | 80 |
| UI Workshop potential | 80 | 80 | 80 |

The reacquired Base runtime handle was50451 in this session, but selection was
validated from definition and actual district/player/city identity, not assumed
from that number. Base/Spec/role and the separate Both-extra modifier are retained
in all three raw API exports.

The observer captured two complete ChangeYieldChange pairs for player3/city458758,
building147/yield7, with stable component identity:

- Native Remove returned to caller872f32 and passed delta−80. The exact target row
  was80 on entry and absent on leave; table count changed4→3, capacity remained4.
- Native Apply returned to caller871fbc and passed delta+80. The exact target row
  was absent on entry and80 on leave; count changed3→4, capacity remained4.

There were no read errors, dropped events, changed identities or unfinished pairs.
Natural GetYieldChange recorded zero calls. Thus we directly observed the live
stored adjustment being removed and restored, **not a full getter return of0**.
The row/alias distinction remains explicit. The native callers match the statically
identified effect Apply/Remove implementations.

This verifies a useful control: the existing material property can dynamically
gate this saved city's +80 building adjustment without advancing a turn. The
unchanged UI potential is therefore not an accurate representation of that
adjustment during this paused manipulation. It does not establish when the UI
refreshes, and does not retroactively prove what the earlier SQL-zero arm did to
its live modifier instances.

## Consequences for CSC

1. Retain this forecast mechanism provisionally. Its dynamic application is now
   verified in this saved Workshop case; the earlier unchanged UI alone was not
   grounds for removing or increasing it.
2. Use bound requirement/effect state and the live adjustment as the input gate
   for future producer experiments. Treat UI potential as a separate cached
   observation. Neither SQL rows nor UI polling alone establish live delivery.
3. The next producer efficacy experiment can test actual AI valuation/choice with
   a verified off/on input. It still needs a narrowly targeted persistent control:
   the existing role bridge rewrites this property at turn/map events. Do not
   assume today's bare property toggle survives AI play.
4. Static building valuation reads this live adjustment through GetYieldChange,
   but this session ran no AI and captured no natural getter calls. It proves
   delivery, not score magnitude, queue promotion, producer completion or net
   supply-chain benefit. The previously observed positive preference multiplier
   is independent evidence.

No shipping tuning, RH files, installed assets, units, buildings, resources or
production orders changed. No new campaign or automatic follow-on was started.

## Restoration and provenance

The property was restored to its captured original1. Full known initial/off/
restored Core world, ordinary city UI/queues and saved economic history agreed;
Gold, mapped materials, real potential yields, Spec and configured role remained
unchanged. The UI forecast also matched its initial80 after restoration. The
source save was never overwritten.

Artifacts: `Desktop/Codex/csc-native-producer-effect-chain-20261029/run-01`.
The source save retains SHA256
`2982b00a4c4d0c536ac7232e88c2c2b0fc2e56fd2ee7842aa22ad47b2ffb065d`.
The current604-file package is a rebase of the historical source runtime, not
an exact package continuation. DLL SHA256 remains
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.

The reviewed harness passed23 focused session checks and13 observer checks before
launch. The run closed normally at100 with worker/native/observer exit0, fresh
145 mod IDs/148 subscription entries and AutoStart=false restored. All604 installed
files were unchanged. Independent audit verified326 source/RH/evidence/fixture
pins,12 dependencies, exact preferences/package and absence of original worker21484,
native13948 and observer708. Reports are `independent-audit.json`,
`independent-audit.md` and `independent-process-audit.json` in the run. No efficacy
pass follows from successful cleanup.
