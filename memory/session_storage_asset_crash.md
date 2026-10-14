# Storage AE crash investigation — 12 October 2026

Henno reports all six Bakers/Tailors Storage S/M/L assets crash immediately on
opening in AE. Extension assets open alone. At his request, removed every
CSC_ALL_Storage_S_Ext / CSC_ALL_Storage_M_Ext attachment from active ASTs (six
attachments across six storage assets); kept the extension assets/XLP entries.

Crash persisted. AssetCloud cache had updated file sizes/timestamps for these
ASTs but still retained all six old extension dependency edges, preventing a
normal startup from rescanning the edited files. With AE closed, backed up the
cache, removed those six edges and invalidated only the six file-info records
to force fresh scanning. Backup: Desktop Codex/CSC_Storage_L/
crash-repair-20261012/mod-Civ Supply Chains-asset-deps.before-refresh.json.

Also repaired confirmed stale AST bindings: Bakers Storage S had ten obsolete
Floor state rows (mesh no longer in either GEO); Bakers Storage L CON+PIL had
five old group-name references, and its PIL decals referenced four old Plane
meshes instead of the current five PilDecal meshes. Copied the matching Tailors
Storage L decal state table and retained Bakers' other material/state settings.
Exact pre-repair AST backups are in the same output folder.

Native readers opened all Small/Medium FGXs and the Large construction/decal
FGXs; mesh names match GEO. Single PIL decal #M removal is exporter behavior,
not a demonstrated cause. Large decals' five native bone bindings per mesh
match GEO; organic-patch and suspect decals share the static three-UV layout.
Do not describe the bounds/culling theory as confirmed. AE reopen/runtime
verification after the cache and binding repairs remains pending with Henno.

Henno subsequently confirmed those repairs did not stop the crashes, and that
many other assets also crash. He suggested clearing AE's cache and explicitly
declined Computer Use; no desktop controls were started. Reset the entire
current CSC dependency cache while AE was closed by moving it to Desktop Codex/
CSC_Storage_L/ae-cache-reset-20261012/ (hash-verified backup). Other projects'
caches, AE settings/browser layout and source assets are untouched. AE must
rebuild this index on next launch; success remains unverified. Treat the earlier
stale-edge and binding repairs as file corrections, not a proven crash fix.

Full cache reset also failed. The regenerated index has no removed storage
extension edges. Henno reports most sophisticated CSC assets crash, including
the Bakers Wind Mill and Tailors buildings; flour closed, Wind Mill tower,
organic patches L/M and building materials open on their own. Wind Mill/expanded
Wind Mill model state pairs and attachment parent bones match their GEOs.
Native reader opens Level 1 S/CON geometry and working flour; all share the same
static three-UV layout. Building atlas DDS payloads/decode checks pass; the TEX
mip count convention also occurs in working prop textures. No confirmed cause.

Latest AE session e7272410-06b1-4e84-a220-621193bce33c.log explicitly repeats
duplicate Shared/Civ6 art dependency errors, 5646 deleted-file classifications,
and Incorrect project attribution for thousands of native geometries. SDK
Expansion1/2 depend on Shared, which depends on Civ6; CSC also lists Shared and
Civ6 directly. No dependency spec change made yet. The session logs successful
tower/patch/material opens but no asset-specific exception for failing buildings.
Do not claim this dependency configuration proves the cause. User forbids UI
automation; continue file diagnostics only.

Henno authorized the dependency/index repair. After he closed AE, backed up the
exact current Art.xml and generated CSC dependency cache to Desktop Codex/
AE_Dependency_Repair_20261012/ (cache SHA256 verified). Removed only direct Civ6
and Shared entries from requiredGameArtIDs, keeping Expansion1 and Expansion2.
SDK specs confirm both expansions bring Shared, and Shared brings Civ6.
Byte comparison against the backup confirms no other Art.xml content changed;
existing unrelated ArtDef changes are preserved. Active CSC cache is absent and
will rebuild on next AE startup. Need Henno's Wind Mill/Storage retry and new log
to assess whether duplicate dependency and attribution errors disappear. This is
a verified configuration repair, not yet a verified crash fix.

Post-repair Wind Mill still crashes. Session ec452616-a743-40d6-8e19-ea853adfe898
(12 Oct 13:33 local) rebuilt CSC dependencies; Incorrect project attribution
and deleted-file classifications are absent. One duplicate Shared error now
remains between Expansion1 and Expansion2's native dependency chains. A BUG at
13:33:45 says Invalid Name parameter passed to IInstanceSetExtensions.
LoadEntityIfUnique, without an entity name. A vanilla Library opens at 13:33:55;
Windows logs AE's same c0000005/address-zero unknown-module crash at 13:33:59.
No Wind Mill runtime-open entry/traceback. Dependency repair improved indexing
but demonstrably did not resolve the crash. Do not alter SDK files to remove the
remaining expansion-shared warning.

Correction after Henno clarified the latest run was launch AE then Wind Mill
only: newer sessions f0c7914e-718e-479b-bd1e-b41c39cca944 (13:35:57 start) and
8cbb9234-d62b-4757-a03a-a16aa520ff39 were now available. Both have zero Invalid
Name messages and zero Wind_Mill entries. Attribution errors recur on cached
startup (352 native GEO entries; 1184 deleted classifications), so absence on
the initial rebuild did not mean the problem was fully resolved. Newest log ends
13:36:12, Windows records the same native crash 13:36:21. Invalid-name clue belongs
to an earlier session and is not reproduced by this isolated Wind Mill attempt.

## Confirmed texture-cooker cause and repair

Henno cleared all caches again; Chair Upholstered Claret and Wind Mill Tower
opened, assembled Wind Mill crashed. Downloaded Microsoft-signed ProcDump into
Desktop Codex/AE_Crash_Diagnostic_20261012/tools and used hidden one-crash
monitors while Henno manually operated AE (no UI automation). Mini dump
AssetEditor.exe_261012_134524.dmp showed toolhost return RVA 0x4ffc81, a call
through null RDI in ModelCooker_ModelCookTexture.cpp's encoder selection.
Full dump AssetEditor.exe_261012_134942.dmp confirmed texture name CSC_Atlas_AO2,
internal format 1009, dimensions 1024x1024, 11 DDS levels. Monitor exited after
capture; no permanent debugger or Windows crash-dump configuration was installed.

The Storage S/M export script ran raw texconv R8 conversion, bypassing the
existing scene exporter's AO header normalization. Installed AO2 used flags
0x20000 (standard DDPF_LUMINANCE); working Firaxis scalar files use 0x40. This
same compatibility issue had been resolved in September's scene exporter.
Backed up exact DDS/TEX to the diagnostic folder's before-texture-repair/;
normalized live CSC_Atlas_AO2.dds using CSC_Atlas_AO.dds as same-sized template.
Header now matches template byte-for-byte, all payload/mip bytes unchanged
(SHA256 c3319f6b9e275dbe87a817f970761dafb80e19778aa1b67cdfbfe73317f98508).
The old DDS fails the established AO validator; repaired DDS passes.
Patched export_storage_sm_ao.py to normalize and validate before installation.
Added file-only dump reader inspect_ae_texture_crash.py for this exact signature.
Focused existing DDS validation test passes; script syntax checks pass.

Asked Henno to reopen Wind Mill plus a previously crashing Tailors asset; result
pending. Other scalar headers audited (20); only CSC_TEST_Crane_White_AO is also
raw texconv format, belonging to an experimental crane package, not the Wind
Mill dependency chain. It has not been changed as part of the shared AO2 repair.

Henno confirmed "opens fine now!". AE session
fd8a6155-ca82-4641-9286-9ffeecb8e2c7 independently records successful Wind Mill
open at 13:52:53 local and Tailors Storage L at 13:53:16. Main crash is resolved.
Read linked chat "Rebake storage model AO" (01a12f66-9351-7a12-80ed-33f6de2c1f5d):
its export turn created and ran export_storage_sm_ao.py, installing raw texconv
R8 DDS without the established header compatibility step. That is the confirmed
origin. Preserve the rebaked pixels and source models. No message sent to that
chat; the shared script and durable documentation have been corrected locally.

## Attachments restored; reusable capture retained

Restored one extension attachment to each Bakers/Tailors Storage S/M/L asset.
Bakers S comes from its same-day pre-export backup; Tailors L comes from the
NoMainDecals crash-isolation copy (its newer position differs from Git).
The other four attachment blocks come from HEAD. Only the six blocks were
added; every other AST byte, including later binding repairs, was preserved.
Backups and provenance: Desktop Codex/Storage_Extensions_Restored_20261012_140342.
No AE UI automation or cache changes. Reopening restored assemblies remains
a manual verification step; the texture fix itself was already user-confirmed.

Henno asked about PNG source freshness. Confirmed the TEX points to Working
Files/3D Art/Textures/CSC_Atlas_AO2.png, which matches the latest Storage S/M
bake deliverable byte-for-byte (SHA256 a7de994a87464d584f6b8123e943b2fe28847bc68c459234d68c9ac1da04a856).
Fresh texconv conversion reproduces every repaired DDS pixel/mip byte. PNG
samples and DDS bytes differ due to PNG color metadata/conversion, so do not
decode the DDS over the PNG or mistake raw byte differences for a stale bake.
The incompatible header was introduced by texconv, not in the PNG source.

Reusable manual capture: project/tools/asset_editor/capture_ae_crash.ps1.
Guide: project/docs/art/asset-editor-crash-diagnostics.md. Original mini/full
dumps and before-repair files retained in AE_Crash_Diagnostic_20261012.

## Automatic capture requested and installed

Henno requested continuous capture from machine startup to avoid recreating
crashes. Installed Windows task `CSC Asset Editor Crash Capture`, triggered at
Shadow's sign-in, running hidden with limited user privileges and no execution
time limit or battery restriction. Started immediately and verified Running.
Uses stable copies of capture_ae_crash.ps1 and watch_ae_crashes.ps1 in Desktop
Codex/Tools/AE Crash Capture; versioned installer/source remains in project/tools/asset_editor.
Production waits with -ma -e -g -n 1 -w AssetEditor.exe and re-arms after each
session. Mutex/task policy prevents duplicates; errors retry and log locally.
Outputs: Desktop Codex/AE_Crash_Captures. No automatic deletion or upload.

Two consecutive disposable native null-call fixture crashes both produced
readable mini dumps (~6 MB); monitor PIDs changed and bounded watcher exited.
Self-test result: AE_Crash_Capture_SelfTest_20261012/result.json. Native -g does
not catch the managed Environment.FailFast fixture termination; this limitation
and the distinction between a dump and UI-action history are documented.

## Exit assertion at 14:48 on 2026-10-12

Henno reported a crash while exiting. Automatic ProcDump was still attached to
AE PID 1708, logging exception 0000071A at 14:48:43 and two first-chance CLR
E0434352 exceptions at 14:48:44. No unhandled native dump triggered: AE remained
alive with title `Assert Failed: AssetEditor.exe`. Windows had no matching new
crash event. Preserved a manual full snapshot (1,989,687,419 bytes), complete
memory payload verified, plus live AE log and monitor output under Desktop
Codex/AE_Crash_Captures/20261012_144844_exit_assert. Existing debugger remained
attached; no AE UI operation or process termination.

Recovered the formatted assertion from the snapshot: Platform_TempHeap.cpp,
line 91, expression !m_uiCapacity, message `temp heap not shutdown`, timestamp
10/12/2026 14:48:46. Saved assertion-from-memory.txt. The project's Asserts.log
contained the same message but was stale from October 9; do not use it to date
this failure. This establishes an exit cleanup assertion, not the cause of the
preceding CLR exceptions or an asset attribution. Automatic exception capture
does not yet automatically snapshot a live assertion dialog.

## Assertion gap closed; 15:07 crash diagnosed

Installed second hidden sign-in task `CSC Asset Editor Assertion Capture`,
running watch_ae_assertions.ps1 from stable Desktop Codex tooling. Polls AE
window metadata every two seconds, snapshots each assertion dialog once per
process-start/dialog-handle key, preserves AE logs, never interacts with UI.
Native exception debugger remains attached independently. Hidden fixture test
captured an assertion without crashing; duplicate-poll and pause tests passed.
Evidence: AE_Assertion_Capture_SelfTest_20261012/result.json and dedup-result.json.

Latest crash was captured automatically at 15:07:55: 4,261,778,721-byte full dump
in AE_Crash_Captures/20261012_145337_3d8de4. Native read AV at ToolHost 0x2ac0e7,
instruction mov rsi,[rcx+rbx*8+8], RBX=0, RCX=0xdbe4d7e150; read unmapped
0xdbe4d7e158. Nearby literal assertions identify FGXModelFramework_BehaviorInstanceSet.cpp,
model/asset instance indexing and animation skeleton handling. Distinct from AO2.
Exact log: Cut Attachments in Tailors L, open new CSC_ALL_Storage_L_Ext, cut/move/
rotate attachments, save extension 15:07:53, then crash. Consistent with stale or
corrupt live instance data; exact engine bug/trigger not proven. Current eight
CSC dependencies pass structural parent/child/cycle/name/group checks, but
Henno edited both source assets again after this crash, so the audited files
cannot be asserted to match the crashed session. No asset mutation as diagnosis.

Recovered five complete asset XML strings from the same dump: two Tailors L
copies (six attachments) and three new Storage L extension copies (15
attachments). Preserved with offsets/encodings in xml-recovered-from-memory/.
All candidate parent/bone/group bindings pass against local GEO metadata.
These can be cached/undo-history XML, not final live graph, so they strengthen
but do not prove the runtime-state inference. Consolidated diagnosis.txt retained
beside the dump. Added the generic assertion-dialog capture lesson to civ6-art.

## 15:18 managed crash identified

Another automatic full capture: AE_Crash_Captures/20261012_150922_9d5fba/
AssetEditor.exe_261012_151837.dmp, 4,541,284,417 bytes, complete memory payload,
finished 15:20:46. Microsoft ClrMD 1.1.142101 offline reader recovered actual
fault-thread 0x3b64 exception System.Exception / HRESULT 0x80131500 / message
`Duplicate knob created`. Stack: AssetPreviewer.KnobDatabase.ProcessPacket ->
KnobManager.SendNotificationPacketToUIThread -> ToolContextImpl.Notify.
Retained managed-exceptions.txt beside dump. Tested reusable reader source is
project/tools/asset_editor/inspect_ae_managed_dump.cs; compiled x64 Framework
reader/dependency/package retained Desktop Codex/Tools/ClrMD. Match CLR/DAC
versions and exception thread ID; last thrown exceptions on other threads can
be stale.

Henno reports copying attachments into L_Ext from a different model/bone asset,
then bulk retargeting. Exact log: Paste Attachments 15:18:16 with 17 references
to missing CSC_Storage_M or CSC_Storage_M_CON+PIL; EditModelInstance 17 ops at
15:18:25; EditBoneName 17 ops at 15:18:28; save Tailors L 15:18:29; load default
environment then crash 15:18:37. Several docs involved; user's recollection
names L_Ext whereas log's saved document is Tailors L. Confirmed duplicate
runtime preview-control registration, not proven duplicate AST attachment
names. Fits live refresh after retargeting; exact duplicate/control trigger
unknown. Distinct from native 15:07 failure and AO2. No speculative asset edits.
Reopen after paste / smaller binding batches are unverified workarounds only.

Repeated managed signature at 15:32:52: Henno reports moving a barrel attachment
in Tailors Storage L and apparent hang. Automatic dump completed 15:35:08 in
136.2 seconds; 4,724,543,951 bytes, complete memory payload. Exact fault thread
0x13a4 has the same Duplicate knob created exception and same preview-control
stack. Folder AE_Crash_Captures/20261012_152048_986c8a, managed-exceptions.txt
and diagnosis.txt retained. Log has Move Attachment started 15:32:33 without
end, save Tailors L 15:32:44, environment reload 15:32:52. This establishes
recurrence after ordinary attachment movement, so bulk retargeting is not a
necessary trigger. Do not attribute it specifically to save or drag without
more evidence. The apparent hang can be dump collection holding process state.
Both background tasks verified running after capture; no asset modifications.

## Deeper duplicate-control diagnosis, 2026-10-12

Both 15:18 and 15:32 dumps have an orphan Tailors Storage L preview retained in
PreviewerDocumentService.PreviewWindows while the main DocumentRegistry has
only a new L document. Classical Base 03 remains open and attaches L. Later dump
also has orphan L_Ext. New --registry mode in inspect_ae_knob_dump.cs uses CLR
field metadata (Dictionary entry reference fields are reordered; do not guess
their raw layout). Exact later duplicate callback is LPWS_OBVisibility / group
CSC_TAILORS_Storage_L_CSC_TAILORS_Storage_L_0 / Show Obstructions / boolean.
Existing BoolKnob 0x28e0cc705f0 matches. Main UI stack is DoOpen / BaseEntityEditor.Open,
not proof of a drag failure. User cannot recall reopen/Save As sequence; dumps
are sufficient and do not require another memory question.

Static DLL inspection identifies DocumentRegistry_DocumentRemoved returning
early when UnbindSurrogatePreviewer finds an open dependent. This wrongly skips
ShutdownDocumentPreviewing, CloseWindow and dictionary removal for assets as
well as materials. One-byte patch redirects IL0011 br.s from return008d to
previewable check0013, preserving non-previewable handling. Original DLL unsigned,
SHA b1855d6319f0ce804162342252892247fd3540da25f0f6872d64713f4a38f990;
patched SHA 6a897703193d74e86f01aa657f1ca5ea71e8879d5777a2410ceb70da3868c9bf.
Offline all1176 method bodies / eight state paths pass. Native runtime unverified.
Package Desktop Codex/AE_Preview_Cleanup_Fix_20261012 prepared with original and
rollback installer. First install attempt refused because AE had reopened;
asked user to save/close. No DLL changed yet. See durable preview-cleanup report.
Correction: sandboxed Get-Process could not see the already-running AE process;
it had not reopened. An unsandboxed check showed PID13036 started15:35:12, still
responding. Installer's unsandboxed guard refused both attempts. Use unsandboxed
process checks before SDK installation; await required user save/close state.
Generic civ6-art troubleshooting section updated with diagnosis, scoped workaround
and offline/runtime validation distinction, with a pre-edit backup in the repair
package. Source docs/tooling complete; installation awaits AE closure.
No speculative AST edit or Automatic Export setting change; worker was idle.

Final state16:41:39: unsandboxed check now showed no AE process; installer
successfully installed/hash-verified patched Firaxis.AssetPreviewing.dll in SDK.
install-result.json and original DLL retained in repair package. User asked to
manually test parent Base03 plus child L edit/save/close/reopen cycle. Runtime
validation pending; do not call all AE crashes fixed. Automatic monitors active.
