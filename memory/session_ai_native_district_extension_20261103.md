# Native district-score extension — 3 November 2026

User asked to investigate the native extension after handbook publication.
Offline scope only completed; no game, FireTuner, Frida attach, score mutation,
mod deployment or native prototype compilation was performed. Broader campaign
remains paused. Shared controller is still required for any separately scoped game.

Report: `project/docs/research/mods/civ6-district-score-extension-20261103.md`.
Current model: `project/docs/civ6-ai/topics/native/native-placement-extension.md`.
Added AI-N053..060; N036 remains provisional with concrete new evidence links.

Exact324c DLL/Ghidra identity;13 complete C views,3 complete xrefviews,7completeASM
verified2799instructions/11189bytes againstPE.3e30b9callsdistrictNet52a440;
return3e30be/outputpointerdereference3e30c3/canonicalstore3e30c5 beforepref1.5.
RAX is outputpointer, not scalar score. Net and Value can returnzero early, so
not-sentinel is insufficient admission. Zero also legitimate; initialzero-skip
would be limited. Nativechoice admitsvalidnegatives. Futurebuildinggate>0 makes
pre/postinsertion different. Earlyfeatures/resource/floodtiming guards retained.

Fresh PVxrefs6directsites in4functions. Newly inspected480540 productioneffect
usesbestplotR9=RAX at48060e, PVcall48061b, SAR8 at480622 ->analysisaccumulator;
decompileromitted4tharg, ASMproved. NoSQLregistration traced. Read3e8b30/Write3eaac0
serialize/restore districtcache; alteredvaluescanpersistindependentpolicytable.
Contractsretainmaxold/currentextraPV; priorityseparate. Threatqueuecomparison can
protectalreadybuildingdistrict. Hookdisabledoesnotundocommitment/pastconstruction.

REA reused18IZrecords, inspectedretainedCalcDistrictview ev_2de32e06d5cd4497199b92ad48d09694feebddbf78a7efa96295a587ecb4cfb3,
exported18recordbundle, closedverifiedopenfalse/cleanupfalse. Not18newanalyses.
Ghidra read-only; currentprogram hashunchanged; noannotation/prototype edits.

CE15sourcefiles pinnedcommite59b5aa910c8a0fcab9b31973ffa477443de0e09; installedCE1.3
DLL36ba871516326878984dac0d1903a08a48490ad386516cca4910c83f846f662f separately
identified, no sourcecorrespondence/currentcompatibilityclaim. RegisterCallEvent
nresults0/entryobserver; RegisterProcessorregistryneedsnativecaller;
DistrictTargetChooserCongressnotordinaryplacement. NewC++CEintegration orother
GameCorecarrierneeded. FridaCModule usefulproposedexperimentalhost, notshippingmod.

Recommendeddesign copiedfacts/authorrules ->immutablesession/analysisqualified
numericpolicy ->nativefastlookup/filterBEFOREJS ->sharedordinarycache. NoLua/game
objectcalls onoffturnworker/hothook. Humanoriginalidentityexplicit; Q8utilitynot
yield. Prototypecontract28proposedcases, noneexecuted: pointerno-op, signedguards,
order/generation, persistence, scope, cache/request conversions, concurrency/perf.

Evidence output: `C:/Users/Shadow/Desktop/Codex/csc-native-district-extension-20261103/`;
allowedviz staging samebasename in currentthread outputroot. Independent cache,
host/source and testcontract reviews retained. FullrawCEsource stays external;
public docs cite commit-pinned primary links, no GameCore redistribution.
