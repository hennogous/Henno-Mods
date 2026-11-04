# Workshop delivery investigation,4 November2026

Henno put further AI tuning on hold to derisk shipment, then clarified he prefers
no own CSC DLL but accepts a Community Extension dependency. Keep this preference
ahead of the older score-component/tuning next steps. Do not deploy the independent
prototype as the selected release architecture or silently revive Frida as one.

Canonical explanation: project/docs/civ6-ai/topics/native/workshop-delivery.md.
Report: project/docs/research/mods/csc-native-workshop-delivery-20261104.md.
Source tools: project/tools/ai_workshop_bridge/.
Evidence: Desktop/Codex/csc-workshop-native-delivery-20261104/.

Correction: frontend GameCores PackageId/DllPrefix selects DLLs inside a mod
package's Binaries/Win64. Installed Workshop CE demonstrates that mechanism.
No external injector/manual executable-folder copy is inherently required.
The old CE INI location was optional console configuration. Generic gameplay
skill guidance corrected and pushed86d61bc; repo correctionCOR-008/AI-N070.

Independent carrier (own GUIDa04) proved package-native loading, Lua API and
zero-write Online1–2, then42 observed+256Q8 adjustments in Online1–6 and a second
observation world1–2 in SAME process. Policy cleared/new generation20/version0.
All native exits0, exact149entries146IDs/autostartfalse restored, CSC/proxy content
unchanged and owners absent. Driversecondpostassert EXIT1 because endturncounter
reset hid receipts; originalresult kept,42writes reconciled offline from
logs-closed/Lua.log in fourgenerations, no replay. Currentanalyzer fixed+4tests.

Preferred CE-owned capability: common bridge.c compiled with CSC_CE_INTEGRATION,
own shim and proposedCE_AIDistrictScoresBegin/Allow/Entry/Commit/Disable/Status.
prepare_ce_contribution.py generates unappliedMain.cpppatch and twoAMD64COFF
objects; compile andgitapplycheckpass pinnedCEe59b5aa. No fullCElink/MSVCbuild,
nativeexecution/adoption, externalmaintainermessage or publication. StockCE1.3
lacksnewAPI; a privatefork is stillmaintaininga nativedistribution. CEfrontend
adapter Lua has7fixtures andfailsunavailable onstockCE.

ExistingCE RegisterCallEvent wikistillunfinished; inspected ABI/trampoline/state
issues preventassumingturnkeysafehook. No observedCEcrashorwrongthreadclaim.
DirectmatrixeditingwouldbeFINALaggregate vsourprestore andneedsverifiedtiming,
freshanalysis/idempotence; jobcompleteflagsnotlocks.

CE-onlyreadprobeGUIDa05 containsLuaonly, noMemwrites/hook. Tenfixturespassed.
FollowglobalGameb8aa68 ->+240manager ->+20playerarray ->slot8*pid ->Player+650
CityManager ->+98linkedhead ->node0CityBuild,next10. CheckcityidentitynormalLua.
Players[pid].__instance isREFERENCEWRAPPER, notnativePlayer; never+650fromit.
ThreeCEprobeMENUONLYattempts01/02/03 createdNOWORLDS, normalexit/restoredall.
03CanEnableMod(handle,true) gaveContainsDuplicates: localCE1431 andWorkshopCE1434
sameGUID/version.04usesCanEnableMod/EnableMod NONrecursiveafterexactWorkshopCE
enabled, avoidingalternatecopydependencyclosure. FinalCEreadresult inreport.

No actual Workshop upload/subscription roundtrip tested. No policy improvement,
choice/benefit or fullshippingreadinessclaim. Save/load/fullCEintegration and
supportedcombination tests remain release gates. All games sharedcontroller,
Online speed and at most6 turns perworld; preference/content restoration tracked.

FINAL CE-read-probe08: normalOnline1–3,307receipts/55city/174scores/no disabled/no Memwrites. ActualnewCEscoreAPI nil. CE-onlymodule+original verifiedSHA; selectedLOCALCE byteidenticalWorkshop to satisfyresolver. 01–04MENUONLY no worlds; 05–07worlds3 stoppedprobe (nativegamesclosed0) on `_G`/strictfieldtypeassumptions. FIELD_* were NUMERIC STRINGS, notmissingAPIs; use tonumber. Probe08 passed afterguardsfixed.150entries147IDs/autostartfalse restored; noowners/contentchanges. Player1 turn2 OnGameTurnStarted/PlayerTurnStarted flags0; laterActivated flags1 withscores, NOexclusivewrite/preselectionclaim. No moregamesauthorizedbythisnote.
