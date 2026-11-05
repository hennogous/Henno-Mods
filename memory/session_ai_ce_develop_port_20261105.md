# CE develop source port and deferred build —5 November2026

Userapprovedplan: closeprematurePR9, preserveoldtestedfork, API-onlydevelopport,
supportedMSVCbuild/nativecheck, continuedAPIscopereview, laterPRsafterapproval.
Explicitnewmaintainabilityrequirement: veryclearcommentsandreadablecode forWildW.
Read feedback_upstream_pr_review.md andfeedback_ce_api_maintainability.md.

PR9 CLOSED06:39:18UTC withapprovedexplanation. Oldremote/localCE-fork cleanat
a928eb8b4298ed24dc2d74be0123ca2da434ed63. Isolatednewrepo:
Desktop/Codex/csc-ce-develop-port-20261105/source. Developbase2986a746b396eb93aad14f9afffb043a09c2c489.
Branchfeature/ai-district-scores-develop pushedcommitsf9eda1c+87f48fc, clean.
No newPR; noCSCspecificpolicy or alternateCEbuilderinthatbranch.

Sourceindependentcorrectness+maintainabilityreviewsPASS. C985lines afterformat;
7774Ctokens/53headertokens+allPPdirectivessame. FinalC7a6cdf2abe5770268af51d23b2d45e7db0edcd6ee5605bc557785e766a4a6343.
OnlyMain11lines, existingMSVCproject/filterwiring, fivegenericnativefiles plus
isolatedtestdriver. Preservecurrentdeveloplogger/call_once/exports/lifecycle.
36isolatedCchecksPASS viaalreadyavailableZig0.15.2 (NOTwholeCE/MSVC/MASM/game).
24Lua,17harness/package,164sharedcontrollerPASS. Offlineharnessnowselects
distinctCSCtestID/pinsactualdependencyCore; defaultIDsunchanged. Portablefixture
suppliesfakeuserdirinstead ofassumingrealLOCALAPPDATA insideWindowsApps sandbox.

Supportedtoolchainabsent (onlyModBuddyVS2013shell/MSBuild12,SDK8). Userapproved
minimalVS2022BuildTools/v143/SDK26100install, BUT latercan'tseeUAC and says
WILL BE AT KEYBOARD LATER; DO WHAT POSSIBLE WITHOUT FOR NOW. DO NOTRETRYINSTALL
orstartCivuntiluserreturns. Launchwrapper80782cancelledCtrlC/exit1; elevatedinventorySTILLlistsconsent11484.
Do notautomateitssecurityUI; dismissoldpromptwhenuserbackbeforefreshinstall.
NoVSpathinstalled. Signedinstaller+planretainedtoolchain/.
CUApartcompletedsummaryLocatedelevationprompt; nosecurityUIinputperformed.

environment/ pinsvcpkg5d68747a,MinHook1.3.4/Capstone5.0.9[x86],staticx64,external
normalMSBuildprops/targets/compatMinHooknamealias; baseline98filespinned.
No globalvcpkgintegration/AsmJit/CEbuildsystemchange. Baseline+portbuildscriptsready.
packages/csc-regression618files (ID…2a08): installedhumanCSCsnapshot+only4adjfiles
overlaidfromreviewedsource, allhashes; sourceCore5f19314 vsinstalledCore0e150ff9.
packages/policy-regression depends…2a08 andpinsactualcopyCore. NOTinstalled.
No newCE DLL/package. FutureCE/policy testGUIDduplicatesneeddedicatedfolderbackup
orcarefulreplacementofpreviousdevpackages, neverhumanstockCSC/CEoverwrites.

Durablehumanhandoff project/docs/research/mods/csc-ce-develop-port-20261105.md,
maintainedguidesreflectclosedPR/newportpending. Nextactualsupportedbuild then
inspectexports/imports/MASMunwind,36MSVCchecks, sharedcontrollerboundedOnline<=100
lifecycle/diagnostics/savereload/provenance/normalrestoration.15minagentcheck-ins
onlyoncehealthyautonomousgameisrunning; source/installedpinsfrozenwhileworkerowns.

## Installation resumed at the keyboard

Henno returned and authorized continuing the supported build/runtime plan. The
earlier away-from-keyboard hold above is superseded. Automatic elevation launches
did not produce a usable prompt for him; do not keep relaunching them. Attempt02
also exposed an installer argument mistake (`--lang` is invalid for this install
command); it exited87 and installed only the Installer client. Attempts03/04
reported cancelled elevation. Attempt05's normal bootstrapper showed a consent
process but subsequently closed without installing the compiler.

Prepared `Desktop/Codex/csc-ce-develop-port-20261105/Install-CE-BuildTools.cmd`
with the corrected official bootstrapper command, exact minimal components and
an exit-code receipt. Henno launched it directly and said it now looks good.
At07:40UTC setup is actively installing C++ components under
`C:/BuildTools/CE-v143`; no consent process remains. Installation completion,
vswhere registration and usable compiler/SDK still need verification before the
dependency/baseline/API builds. No new upstream PR is authorized.

## Supported build and native regression in progress

Manual installer completed exit0 at08:43:49 local. vswhere verifies complete,
launchable VS2022 17.14.37827.9, MSVC14.44.35207, SDK10.0.26100.0 under
`C:/BuildTools/CE-v143`, no reboot required. All36 isolated native checks PASS
with actual x64 MSVC C11; self-test EXE dffa1f07ac473e7ecb3c1ad876f28281df9901dacf239862fdd37d06e348794c.

Pinned vcpkg dependencies and both existing-project Release/x64 builds PASS.
Unchanged upstream DLL18af3c5a0e92d98756a0fdfcd28351bdcbaf1efdcd646ce6a27adfcb995991ad;
feature DLLb1090682fc6c964d077c36efe4dcbac6693d6bf83f9da08b5ad4c0f6e77d139b.
Both144 upstream warnings/0errors, no source fixes/new API warnings. All157
exports/155forwarders preserved, no non-Windows runtime DLL dependencies. Source
HEAD87f48fc remains clean. `supported-msvc-builds.json` pins tools/deps/artifacts.
Independent built PE/compiled guards/lifecycle/shim/unwind audit PASS in
`independent-artifact-audit/`; static success does not qualify game behavior.

Runtime staging is journaled at `runtime-staging.json`: old dedicated
`CE AI Development Fork` and `CSC CE Policy Parity` moved to artifact
`runtime-backup/`, replaced with exact test packages. New
`CSC CE Develop Regression` ID...2a08 installed. Original human CSC and stock CE
remain unchanged. After the driver closes, move test copies out of Mods into
artifact runtime-retired and restore the two old dedicated folders; verify hashes.
No recursive deletion needed. All resolved move paths must stay in named roots.

Native regression launched through shared `ce_parity/driver.py`, exec session40565,
artifact `native-regression-msvc-01`, Online100 + lifecycle. Correct game EXE is
`Base/Binaries/Win64Steam/CivilizationVI.exe` (not Win64). OriginalCSC reference,
stockCE, isolatedCSC selected by ID, three packages and executed sources pinned.
One driver exclusively owns Tuner; DO NOT edit pinned Python/Lua/installed files
or send another Tuner command. Setup still needs initial health verification.
Once healthy, only check game every15min; use archived progress/observations and
later result/audit, never dispatch as evidence. No new PR is authorized.

## Final native closeout

Driver finished normally at100, lifecycle_exercised=true, closed=true, error=null,
installed_unchanged=true, native exit0 and no remaining owners. At the scheduled
15-minute check it was reloaded68/ready1/faults0 with exact save scanner parity.
Final audit verifies101 matching policy plans/100 published windows/27,775
complete records: Net13,808, cache13,812, best135, PV20;62 increases and13,746
deductions, no original-human trace, no native faults. All153 installed entries
(150 mod IDs) and autostartfalse restored. Source/archive/module identities pinned.

Guarded restore-runtime.ps1 executed after closure/preferences verification:
three test copies moved into runtime-retired, two prior dedicated development
packages restored by recorded hashes. Original human CSC and stock CE unchanged.
runtime-restoration.json status=restored, no deletion or active game remains.

Fork README updated with supported/runtime receipts and limits; no compiled
input changed. Clean/pushed HEADc2355d66460dd0c0283a8d73e96100433e8a2336, tested
implementation remains87f48fc and exactDLLb1090682…139b. Old fork a928 preserved,
PR9 remains closed, no new PR. Docs/guide/findings updated for the completed
qualification. Native method parity restored; focused Mill yield and
forecast attribution, economic benefit, broad CE compatibility and final API scope
remain separate future work. Do not start another world without a new need.

Independent closed-run review PASS from raw facts/traces, all65archivedpins,
three off-context zero states, ten reload fields, savedfileidentity and153exact
preferences. Receipt independent-runtime-review/reviewer-receipt.json. Actual
Database.log delta contains80 new CurrentClickouts Localization duplicate errors
(46 suchlines already in prefix), no Gameplay ERROR lines/Lua runtimeerrors.
Documented caveat; zero-fault claims refer specifically to native API/policy.
