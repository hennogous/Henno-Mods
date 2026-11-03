# Native Quarter placement and weight calibration — 1 November 2026

Status: both observer diagnostics CLOSED/AUDITED at2, each after one AI
interval. No target Quarter score/choice was captured; no weights changed.
The original installation/preferences are restored and all test owners absent.
This branch is stopped, with no further native attempt authorized. The broad
tool goal remains paused. [Compact controls/evidence table](csc-native-quarter-placement-control-evidence-20261101.md).
Earlier startup/live sections below are historical phase records.

## What reaches placement scoring

Verified against GameCore_XP2_FinalRelease.dll SHA256
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`:
CityEvaluation `3e2aa0` → NetValue `52a440` → DistrictValue `52d500`
reaches ordinary District_Adjacencies, including dynamic custom Yields.
The misleading recovered Improvement namespace on `25f570` does not describe
its actual district-definition inputs. Bodies, callers and loaders govern this
finding. This proves a scoring route, not an observed placement improvement.

The owned-plot wrapper and direct selected-district adjacency are separate
contributions. The alternative-district vector can cause the **full maximum
alternative static value** to be subtracted, subject to native conditions.
Ownership, discounting, maintenance, clearing, existing land value and district
preference also matter. A normalized yield slice is not the final plot score.

## Weight units

The native NormalizeYields loop uses the dynamic YieldDefinitions count. It
multiplies signed Q8 amounts by the yield's DefaultValue, then applies the actual
aggregate player YieldBonus. The observed static implementation caps the upper
bonus at +900%; no lower clamp appears in this function. The Yields list handler
reads AiFavoredItems.Value as a percentage-style contribution: **25 means +25%,
not 25 times**. Other player/strategy inputs can change the aggregate.

Actual loaded prior RH-profile DB inputs and default-bias-only arithmetic:

| Channel | DefaultValue | DefaultYieldBias.Value | Normalized single raw unit |
|---|---:|---:|---:|
| CSC private placement |1|25|1.25|
| Production |1|28|1.27734375|
| Gold |0.66|16|0.7578125|
| Science |1|17|1.16796875|

These examples include native Q8 truncation, but exclude other active biases and
all later score stages. Nine arithmetic controls pass; they are not live values.
Current source cues are river4, Quarter→customer10 and customer→Quarter30.
Their private normalized slices would be5,12.5 and37.5 under only the default
bias. Do not infer actual placement ranking or a safe tuning amount from that.
The old all-BONUS12 cue is removed.

Districts preference is a separate channel: its identified evaluator uses the
aggregate sign, with a positive preference scaling net value by1.5. Increasing
its SQL Value is not a proportional weight increase. This does not describe the
Yields or PseudoYields handlers.

## Material specificity remains a boundary

The standard adjacency loader supports any-resource Boolean and one native
ResourceClass string, not named-resource or CSC TypeTag matching. Prior native
class probes show that concatenated class lists are not a set selector. Resource
reclassification would change gameplay and is not proposed.

The traced AI requirement registry supplies adjacent resource **class** matching;
resource type/tag requirements operate on the current subject plot. It exposes
no verified exact-neighbor resource/type-tag route. This is a bounded finding,
not proof that every unused gameplay requirement is absent.

Current Quarter-owned material40 modifiers are not verified as localized
pre-placement cues. **3 November correction:** the earlier city-iterator mapping
to PLAYER_PLOT_YIELDS was wrong. Actual PLAYER_PLOT_YIELDS and SINGLE_PLOT_YIELDS
share a once-only supplied-plot handler; neither supplies city or plot context.
The direct DistrictValue context leaves its required plot pointer unset, and
the empty-collection effect fallback changes no accumulator. See the
[verified pointer chains and scope](csc-future-economy-forecast-20261103.md#4-plot-context-correction-to-an-earlier-native-note).
The identified AI owner-adjacency handler does not perform a distance calculation.
Do not extrapolate this to universal zero effect or gameplay requirement
semantics. Generic Farms, bonus resources and synthetic markers are not accepted
substitutes for exact industry materials.

## Next bounded observation

Astra recommends an unchanged-weight baseline: one declared AI3/Bakers/city131073
calibration fixture, selected plot unspecified, hard turn40 or earlier first useful
natural decision. This fixture is selected from known history, not an independent
performance sample. The observer must correlate raw/normalized components,
actual effective bonus, opportunity deduction, final scores, candidate cache,
natural winning district/plot and reservation. Partial candidate coverage cannot
establish a complete ranking.

Nine read-only observation points have verified static ABI and24-byte instruction
fingerprints. Root independently checked all nine against the pristine PE file.
That verifies addresses, not a running collector. The implementation must bound
global callback overhead separately from retained records. It uses the shared
NativeSession/finite controller, with no forced orders, direct native calls,
return-value patches, DLL edits or RH changes. Fresh UI bootstrap and source
parity must pass before AI advancement.

No automatic treatment follows this baseline. Only an interpretable observation
that forward10 dominates an inferior site could justify a separate controlled
10→5 forward-cue test. Reverse30, river4 and all other policy remain fixed. No
long-game extension or broad campaign revival is authorized by this protocol.

## Evidence

Small raw decompiles, ABI specification, evidence hashes, weight-definitions.json,
weight-units.json and root-static-handoff-verification.json are in
`H/native-quarter-placement-consumer-20261101` (H is this chat's visualization
workspace). No extra Ghidra session/database copy was made. Native choice and
efficacy remain unobserved.

## Native baseline initial1 gate

Authority: Desktop/Codex/csc-native-quarter-placement-20261101/baseline/run-01.
Worker22492 creation134379911987142790; DX11Civ2588 creation134379912028661123;
observer daemon5884 creation134379913527175102. These identify this run only; read
later state rather than treating the source clock as its current progress.

Root source1 audit verifies342 frozen inputs, all3404 source plots,12 setup units,
six5-Gold wallets, original human0/AI1..5 roles, all477 native DB tables/rows exactly
matching the prior no-BONUS runtime, and zero host effects. The fresh UI bootstrap
now actually supplies both captured modules/version2/all required methods without
manual imports or initialization. This closes the pending cold-start check for
the source repair; it does not prove scoring or AI-choice benefit.

The nine-point Frida17.24.3 observer attached disabled with exact build/byte/config
checks and zero errors/pending. Root digest6bd70d90 released only the first1→2;
a separate first2 review is required before the remaining hard40 budget. The
reusable observer/profile/driver have50 focused offline checks (21Python,
18JavaScript,11driver+actualLua), all passing. Current runtime/source inputs stay
frozen until normal closure; no overlapping console client or midrun tuning.
Root evidence is H/.../probe/root-source1-audit.json and root-baseline-go.json.

## Global-hook diagnostic and corrected observation

The first observer was closed at actual2 after one AI interval:882,774 callbacks
at the first2 handback,1,029,621 by the inert freeze. Global Normalize/bonus hooks
dominated; target city131073 was not yet present, and no candidate pair or weight
response was observed. Zero host effects and zero observer errors. This is an
instrument-cost result, not a gameplay failure or an AI non-response.

Root independently verified all342 then-current pins, normal native exit0,
retained daemon exit, all owners absent, exact619-file installation restoration,
and raw145-ID/148-entry preferences/AutoStartfalse. H/probe/root-closed2-independent-audit.json
is the closure authority. After that audit, source was intentionally updated to
add the corrected observer: audit archived old inputs, not current tool hashes.

Astra endorsed ONE corrected baseline with ten exact points: replace the two hot
global Normalize/bonus hooks with three local post-call sites inside DistrictValue.
The seven surrounding score/cache/choice/reservation points remain. The same
source1/current SQL/RH/economics and hard40/known-city bounds apply. This new
observation intentionally restarts the original save; it is not continuation of
the discarded diagnostic interval or an independent performance sample.

Wrapper raw integer and normalized output are directly observed. Own/competing
normalized outputs are direct, but their raw inputs are **unobserved**: Normalize
overwrote the only proved original slots. Private capped bias may be inferred
conditionally from a nonzero private wrapper and verified DefaultValue1, with
integer/rounding/overflow qualifications; it is not a direct strategy-bonus read.
No inverse-generated raw vector is presented as measurement.

Useful exposure requires a selected plot and observed alternative both owned at
the native score cache and later facts; nonzero private wrapper inference in one,
own/competing normalized observations, deduction/DistrictValue/Net/cache and a
unique natural choice/reservation link. No missing exposure is scored as success.
No third attempt, higher cap or automatic weight treatment if this remains costly
or unlinked. The first2 continuation gate additionally requires<=100,000 callbacks.

Canonical source includes named profile quarter-placement-post-v2, its collector,
portable tests and exact build/fingerprint guards.28 Python-profile,39 post-JS,
15 driver/Lua fixtures pass. Current startup worker23564 birth134379927549826896,
DX11Civ8720 birth134379927592646428;345 executed inputs frozen. Authority is
Desktop/Codex/csc-native-quarter-placement-20261101/baseline-post-v2/run-01;
the exact first2/observer identities must be read from its actual artifacts.

## Final corrected diagnostic result

The corrected local-post observer generated294,437 callbacks in its first AI
interval, failing the preregistered100,000 gate.257,080 were competing-normalize
callbacks. Target city absent;0 candidate pairs/0 errors/0 host effects. Root
ordered normal closure at2, without a third retry or weight change. Final inert
freeze343,344 callbacks/0 pending. Root verified345 current pins and53 archived
text entries, native/worker exit0, retained daemon exit, exact619 installation,
raw145-ID/148-entry preferences/AutoStartfalse and exact owner absence.
Authority: H/probe-v2/root-closed2-independent-audit.json. All runtime owners are
gone; current source is the reviewed tool version, not a claimed gameplay release.

The result is an observation-cost limitation, not evidence that the guidance
works or fails. Astra's follow-up recommends native-side filtering before JS as
a prerequisite for later instrumentation, and offline use of existing planner
choices/dependency-loss records now. Current weight units/routes are verified
statically; live calibration and exact native material placement remain open.
