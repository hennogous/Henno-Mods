# Industrial Zone architecture investigation — 1 November 2026

Henno questioned whether the old AI research direction was sound. Current request:
investigate vanilla IZ → Workshop → Factory architecture using REA and existing
resources, maximize offline work, shared controller for any fresh game. This does
not resume the old paused broad campaign. The initial phase was entirely offline;
the user's subsequent "go ahead" authorized the bounded runtime follow-up below.

Durable findings: `project/docs/research/mods/civ6-industrial-zone-planning-architecture-20261101.md`.
Raw package: Desktop/Codex/csc-iz-architecture-20261101. Current installed/reference
DLL SHA324c51e9...46c2e98c matches. Ghidra12.2 + fresh REA6.8.0/12.1.4 dossiers.

Main architectural result: prerequisite-aware future forecasts + backward value
propagation + item-level requests, not proven persistent Factory-rooted sequence
in ordinary city path. Windows loaders prove +198 direct dependent collection,
+1f8 prereqs, +1e0 mutually exclusive (do NOT call prerequisites). 3dfee0 adds
positive Factory value into Workshop; missing IZ district candidates get qualifying
building sum. Cache alias +4e0 wrapper/+4f0 data == first entry+28 verified.
3e2aa0 forecast includes missing district/building production/research delay.
GetBestBuilding/CheckForUnitOrBuilding rejects normal missing Workshop at result+4
or legal missing IZ+18. Inspectors have OR prerequisite semantics (Factory has one).
BuildFromCity55ba40/Init3f9100/Execute3f8310/BuildBuilding3df040 request one item;
no recursive construction dispatch found in those bodies. Native district tree
already coordinates research/acquisition/clearance/construction, so avoid 'no plans'.

Contract decorators TurnLimit5 limit waiting; native counter>limit cancels states
1/3, exempts executing5; not physical completion in five turns. Max(old,current)
score through Update is bounded path, not lifetime invariant. Ordinary queue
competition still applies. No runtime numeric ranking/sequence/benefit proof here.

REA bundle18records3,560,274bytes exported, active session normally closed, no new
project/snapshot retained. Initial dossier5526c0 is optional district acceleration,
NOT XML Build Unit (actual BuildFromCity). Tiny trace3f9100 partial120nodes144edges,
2decompilations; unresolved bindings/call caps explicitly retained. Never use it
as global absence proof. 29 small native C exports;420 ASM instruction bytes checked
against PE. Raw index/receipts in package. Independent raw/report audit corrected
first cache district-row reset exception and mutually-exclusive wording.

Next if runtime needed: one existing-snapshot city with IZ/noWorkshop, relevant
tech available and boost motives controlled; observe raw/adjusted Workshop and
Factory cache, selected item, request and queue. No global normalization hooks or
new long performance campaign. Always shared controller/native-profile hosting.

## Authorized runtime follow-up — complete, normally closed

Durable result: `project/docs/research/mods/civ6-industrial-zone-decision-boundary-20261101.md`.
Raw package: Desktop/Codex/csc-iz-boundary-20261101. No fresh world/tuning/deployment.
Two existing-save loads: run01 reader failed CityDistricts Members before AI/hooks,
closed0; corrected documented index API validated11actualLua51mockcases. Run02
sharedcontroller loaded exact historical04turn250 SHAea818368...e48 CURRENT632fileCSC
(declared diagnostic rebase, not historical arm reproduction), advanced251/252/253.
Loaded CSC_AI_Profile OFF; all7 captures assistance OFF/empty pending/cycles,
no callback removed, no CSC economic effects. Both cities exactIZ/tech/prereq gates.

Frozen4hooks/904entry+returncallbacks/13pairs(6Calc6Best1Queue)/0errors/0pending/unsaturated.
ALL6 Calc Wdelta=max(0,FactoryENTRY), not FactoryRETURN: Toulouse29833->249803
Fentry219970 at251/252, then29833->260708 Fentry230875 at253. MissingWorkshop
receives futureFactoryvalue. Nicomedia Workshop alreadybuilt sentinel-2559744
receivesF997520/1039845 at251/252; Factorycomplete at253 entryFsentinel gives0.
Factory ownincrease not individuallyattributed; pass is definitionorder17W/24F,
not provedfullrecursiveclosure/freshinputs. No native intervention/causalbenefit.

5 Bestcalls caller3ea73b UpdateBuildQueueForThreat flags1/0 (NOT ordinary0/0);
Toulouse selected139WIND_MILL6569594 butproduction112FLOOD_BARRIER remains.
Nicomedia selects8LIGHTHOUSE whileexistingFactorycontinues. Native252 factory
178.7/165, contract6200COMPLETED; actual253Factorypresent/unpillaged.
Queuecall10 enclosesBest11return3e849c1/0Lighthouse610313; nativecitylog
Neighborhood BuildCityDistrict CONTRACT6381 and253productionNeighborhood.
No targetBuildBuilding, no ordinary0/0 or newWorkshoprequest. Buildingcategory
winner !=actualproduction. Contract6381score/comparisons unobserved. Toulouse
ClassStruggleunowned/boostfalse, queueoccupied, no clean nextitemdecision.

NormalNativeSession close0, original145IDs148prefsAutoStartfalse, exact632installed,
saveSHA/source29pins/deps12unchanged; noexplicitdetach/unload, retaineddaemon
exitafterexactnativeexit. Independent21checkaudit actualrawprefs+OS native2392,
daemon5148,worker23960absent; finalinventory[]. Allsourcesnowunfrozen. No savewritten.
ClosedDB noWAL/SHM copied12,419,072bytes SHAe1a73e2d...40d60/integrityok/profileOFF.
Native/raw/reportindependentreviewreceipts retained. No new long campaign authorized.
Next distinct offlinequestion: do future material/customer relationships enter
Quarter/producer forecasts before they exist? DeclaredBuildingPrereqs evidence
does not prove that cross-district/economic channel; tracebeforemoregames/planner.
