# CSC AI profile source audit — 28 October 2026

Native follow-up: the [Units parser review](csc-ai-native-builder-consumers-20261028.md) establishes integer Value accumulation; the [subsequent Builder priority trace](csc-ai-native-builder-priority-20261028.md) connects it to an additive initial contract priority. This is separate from the contract present-value field and does not yet establish final allocation or runtime benefit. The source-only cautions below still apply.


Offline source inspection while Henno uses Civ for manual QA. No game/process/client access, FireTuner, Frida, deployment, settings changes, installed writes, or gameplay source edits. This is a source/action inventory, not an assertion about the currently loaded game database or beneficial outcomes. Read with [native production analysis](csc-ai-native-production-analysis-20261028.md), [AI objectives](../../integrations/csc-ai-objectives.md) and [roadmap](../../integrations/csc-ai-roadmap.md).

Evidence classes: **S** = checked source declaration/gate; **N** = separately documented static native analysis; **R** = historical observation cited by source, not reproduced here; **I** = implication requiring validation. Paths beginning Data/, Lua_UI/, ModSupport/ or Settings/ are relative to `Civ Supply Chains/`.

## Action gates

| Layer | Exact source reference | Checked declaration (S) |
|---|---|---|
| Master setting | Settings/Settings.xml:18,25 | CSC_AI_ASSISTANCE defaults on; subsidy option depends on it. Subsidy defaults on at :19 and excludes multiplayer modes in setting metadata. |
| Marker | Data/CSC_AI_Profile.sql:4–10; project/modbuddy/CivSupplyChains.actions.json:1593–1602 | Unconditional marker action at load3499 creates ACTIVE/OFF. This marker alone does not load guidance. |
| Basic | actions.json:1603–1675 | DB load3500 includes CSC_AI.sql then CSC_AI_Basic.sql; research/import/assistance/UI actions use assistance-enabled AND supported-RH-absent criteria. Basic SQL :4 changes marker to BASIC. |
| RH | actions.json:1676–1762 | DB load300000100 includes CSC_AI.sql then ModSupport_RH_AI.sql; research/import/assistance/UI plus CustomerRoles use assistance-enabled AND supported-RH-present. RH SQL :7 changes marker to RH. |
| Recognition | actions.json:354–403; project/config/csc-ai-profiles.json:4–10 | Only reviewed beta ID2501be3e-9780-4e9f-9506-4ff71cf076cb selects RH. Config says reviewed5.097, after300000000, nativeCombinedProfileTested=false. Recognition is by ID, not a checked release-version comparison. An unrecognized AI mod takes the no-supported-RH path. |
| Presentation | actions.json:423–453 | Private-yield filter/import and text are separate; ReportScreen replacement is enabled+no-RH. RH SQL :9–14 registers Yields.Name in RHAITags instead. |

“Automatic RH” means automatic selection **when master assistance is enabled**, not that RH bypasses the master switch. Source CSC_AI_Profile.sql:1–3 wording (“Basic setting”) predates the current shared assistance setting and can mislead.

## Shared CSC inputs versus baseline-wide tuning

| Scope | References | What source adds; evidence limits |
|---|---|---|
| Shared native signals | Data/CSC_AI.sql:19–36,44–117 | Private YIELD_CSC_AI_PLACEMENT and DefaultYieldBias; Quarter/customer directed adjacency graph, reverse customer30 vs Quarter10, broad bonus-resource proxy, river signal. These are CSC needs loaded in both modes, but the bonus-class proxy can value the wrong industry (:89–95). Values here are adjacency/yield amounts, **not** Buildings/Districts list Value fields. S; native responsiveness/benefit remain separate. |
| Shared material care signal | CSC_AI.sql:133–291 | Exact BASE/SPEC/resource-visible material presence40, marginal matching improvement80; deduplicates same-industry improvement signal. This is yield/modifier guidance, not a direct Builder assignment. The source itself warns private yields can affect citizen allocation/output (:38–41). S; retention/repair benefit not established by declaration. |
| Shared Service research | CSC_AI.sql:294 onward; Lua_UI/AI/CSC_AI_Research.lua:39 | CSC strategy namespace and callback, eligible alive major nonhuman players. Source comments explicitly separate declarations from proven research choices. S. |
| Basic baseline-wide knobs | Data/CSC_AI_Basic.sql:5–17 | Removes legacy CSC improvement list, sets global PSEUDOYIELD_IMPROVEMENT default30, sets Units-system UnitPriorityBoosts Builder Favored1/Value50. These apply beyond CSC sites; intended as standalone baseline. S for source applicability; N for the separately traced Units integer-to-initial-request-priority consumer. Value50 is an additive priority contribution when applicable, not a percentage or direct present-value boost. Runtime aggregation and benefit remain unverified. |
| Basic Builder movement | CSC_AI_Basic.sql:19–45 | +1 movement; major trait attachment, AI-owner requirement, Builder subject requirement. RH action excludes this file. S, not proof of movement benefit. |
| Basic contract flexibility | CSC_AI_Basic.sql:47–61 | Required City=-1 for Build Unit nodes in Build City Improvement; inserts missing and overwrites existing parameter rows. Permits any-city contract scope; does not guarantee recruitment/reachability. S. |
| Native globals | Scoped CSC_AI*.sql and RH compatibility SQL search | No AI_CURRENT_TASK_BIAS or AI_DISCOUNT_RATE override found. Native threshold/discount findings do not mean CSC currently tunes them. S absence in scoped files. |

Both modes should add only what CSC needs. That objective does not automatically justify Basic's broader default30, Builder50 or movement magnitude as optimal. Conversely, it does not prohibit a narrowly evidenced RH Builder addition.

## RH-specific CSC additions and comment audit

- **Any-city fallback** — ModSupport/ModSupport_RH_AI.sql:16–24 inserts Required City=-1 only if the target node/parameter has no row. It preserves existing RH values, unlike Basic's overwrite. S. This is already a CSC Builder-related change in RH mode; the header's “do not replace behavior trees” means no wholesale replacement, not zero parameter additions.
- **Producer Buildings list V1** — :26–56 adds seven CSC producers with Favored1 and Value90/60. N: the traced Buildings handler consumes Favored sign, not this Value magnitude. Therefore :32–33 “Stage4 is lower at60” is misleading as a claim of weaker building preference. Equal Favored does not establish equal final production value, since underlying building economics differ.
- **Granary forecast V2/V3** — :60–202 attaches private building-yield effects to customer targets and adds configured-AI role properties. Amount40 at :170 is an effect argument, not an AiFavoredItems.Value; the new list finding does not invalidate its magnitude. Role correction refers to prior human/autoplay spillover (R); no reproduction here.
- **Tailors Workshop forecast V6** — :206–263 uses mirrored visible/improvable material facts with private yield amounts and separate BOTH_EXTRA40. Lua role bridge is `ModSupport_RH_AI_Roles.lua:1–5,29–33,111–132`; it writes properties, not production/treasury/improvement orders. S; these forecast signals overlap shared exact-material opportunity and assistance siting inputs at different consumers, so combined effect requires calibration rather than summed “strength.”
- **Strategy counterparts V7** — :265–344 clones RH template-building entries into CSC building stages, preserving Favored, Value, string/difficulty metadata with existence/duplicate guards. :272 language preserving “weights” should distinguish stored Value from effective Buildings preference. N says the preserved Favored matters in the traced handler; Value600/1080 etc are not proven numerical multipliers. Overlap with V1 can expose the same CSC producer to major-trait plus adopted-strategy preferences; additive/repeated sign application and lifecycle need consumer/runtime checks.
- **Foundation priority V8** — :347–383 creates per-Quarter Lua-conditional Districts preferences, Favored1/Value300. Roles.lua:135–140,190–191 connects this to a confirmed surviving incomplete assisted foundation. N: district positive preference is the traced sign route (1.5 factor); Value300 does not encode priority strength or guarantee queue promotion. Reconsidering contracts invalidates them; QueueNextBuild requires its queue gate and contract route. Comments around “foundation priority” should describe this narrower mechanism.

Do not blanket replace every “Value” or “reward” comment: private-yield amounts, PseudoYields, Units, research and Buildings/Districts lists are different consumers.

## Assisted policies are a separate intervention

Both modes load the same OpportunityPolicy + Assistance gameplay/UI host (actions above). `CSC_AI_Assistance.lua:22–41` checks mode, alive major, UI-established AI identity and initial-human exclusion. UI `CSC_AI_AssistanceUI.lua:15–17` allows economics only when multiplayer/hotseat queries exist and both are false. Subsidies are an additional Funding argument at Assistance.lua:213, not the master mode selector.

- `CSC_AI_OpportunityPolicy.lua:10` computes funding and :50 routes tile acquisition; :81 ranks opportunities.
- Assistance.lua:169–182 closes a quoted purchase with exact debit/readback; :215–234 uses WorldBuilder city manager SetPlotOwner with ledger and optional grant; :247–255 creates an incomplete district foundation and checks readback.
- This is direct economic/map intervention, distinct from native valuation. Do not describe foundations as native district selection or tile ownership as an ordinary native purchase. Source limits and ledger assertions are declarations, not successful current-game execution evidence.

## Builder duplication and dormant-source risk

Read-only subscribed RH root: `C:/Program Files (x86)/Steam/steamapps/workshop/content/289070/3792072489/` (name5.097 verified in RHAI_V5_Beta.modinfo:4).

- RH `core/Main/RH_LAI_Main.sql:9` already declares improvement default30. Copying Basic's same default into RH would be redundant and potentially erase later context-specific adjustments.
- RH `core/Main/RH_LAI_Main3.sql:234–254` attaches AI_BUILDER_MOVEMENT with **friendly-territory-start** movement+1 and AI/Builder requirements. Basic's general ADJUST_MOVEMENT is a different effect: adding it would risk stacking rather than simply filling the same gap.
- RH has context-specific improvement/Builder preferences: `core/Leaders/RH_Trait_Leader.sql:768,793` growth improvement200/Builder50; :265 aggressive improvement23; `core/Ops/RH_EmergencyDefense.sql:133` danger improvement-40. These source rows do not establish effective runtime aggregation, but rule out treating RH as a missing generic Builder baseline.
- **Dormant candidate:** `Data/CSC_AI_MaterialCare.sql` and `Lua_UI/AI/CSC_AI_MaterialCare.lua` exist, but neither is referenced by current actions JSON (checked source search). SQL :134–136 defines backlog Builder and improvement preferences; :141–153 changes improvement-tree parameters. Lua :125 counts Builders; :171–187 warns busy/shared counts and distinguishes urgent work/repair. Do not report these as active shipping behavior solely because files exist. Registering them later requires mode gates and overlap review, particularly RH's context policies and CSC's existing any-city fallback.

A useful RH Builder change needs a CSC-specific demonstrated gap: distinguish insufficient available charges, wrong location/reachability, reserved/busy units, missing improvement forecast, repair urgency, and production-contract lifecycle. No new change is proposed as proven necessary here, and no gameplay code was changed.