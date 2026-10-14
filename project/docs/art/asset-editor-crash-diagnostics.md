# Asset Editor crash capture

Asset Editor crash capture now runs automatically on Shadow's machine. The
hidden Windows task **CSC Asset Editor Crash Capture** starts at user sign-in
and is also running in the current session. It waits for AE, captures a full
dump on an unhandled native exception, saves supporting logs, then re-arms after
AE exits. Use AE normally; there is no need to launch a capture or retrace steps.
It does not launch AE, operate its UI, or upload evidence.

The companion task **CSC Asset Editor Assertion Capture** now also runs at
sign-in and in the current session. It checks AE's assertion-window metadata
every two seconds and snapshots the still-running process without dismissing
the dialog. This covers assertions that never become unhandled exceptions.
Its full snapshots, AE logs and assertion metadata are saved in `*_assert_*`
folders. Persistent markers keyed by process start and dialog handle prevent
repeated dumps of the same dialog. No window interaction or screenshot is used.

## Automatic monitoring

- Evidence: `C:\Users\Shadow\Desktop\Codex\AE_Crash_Captures`, one unique
  directory per monitored session. Clean exits retain logs but have no dump.
- Status: `watcher-status.json` in that directory records the supervisor PID,
  phase and completed session count. `Monitoring` means the supervisor is
  running its capture helper; inspect the newest `procdump.log` to distinguish
  waiting for AE from attached to AE. Daily `watcher-YYYYMMDD.log` files retain
  monitor errors and retry messages.
- Assertion status: `assertion-watcher-status.json`; errors:
  `assertion-watcher-errors.log`. The companion watcher has its own mutex and
  runs alongside the native exception debugger. A snapshot only briefly
  suspends AE while collecting memory; it does not terminate the process.
- The task runs only in Shadow's signed-in desktop session, with limited user
  privileges, no visible window, no time limit, and no battery stop condition.
  Duplicate task launches are ignored; a mutex also prevents duplicate watchers.
  Unexpected supervisor failures are retried by Task Scheduler. Re-arming has
  a short gap while the previous session's evidence is finalized.
- Installed scripts: `Desktop\Codex\Tools\AE Crash Capture`. These stable
  copies run independently of the repository's checkout. The versioned sources
  are in `project/tools/asset_editor/`; rerun
  `install_ae_crash_monitor.ps1` to update the installed copies and task.
  An already-running session uses its loaded script until the next restart.
- No automatic dump deletion is configured. Full dumps can be several GB each;
  retained files can be archived or removed manually after diagnosis.

To prevent future automatic starts, disable both **CSC Asset Editor Crash Capture**
and **CSC Asset Editor Assertion Capture** in Windows Task Scheduler.
Disabling their triggers does not stop an existing
capture. The supervisor also honors `pause-monitoring.txt` in the output root
after the current capture helper returns; remove that file before restarting
the task to resume. Avoid forcibly stopping an attached debugger during a dump.

Validation on 2026-10-12: a disposable test program generated two consecutive
native null-call crashes. Both produced readable dumps; separate ProcDump PIDs
proved re-arming, and the bounded test supervisor exited normally. No AE session
or asset was used for the test. Evidence: `Desktop\Codex\AE_Crash_Capture_SelfTest_20261012/result.json`.
The installed production task was verified running with `-ma -e -g -n 1 -w AssetEditor.exe`.

Assertion validation: a disposable hidden process with an assertion-title window
produced a readable snapshot without an exception or termination. Six seconds
of repeated polling produced only one dump, and the pause marker stopped the
watcher cleanly. Test evidence:
`Desktop\Codex\AE_Assertion_Capture_SelfTest_20261012/result.json` and
`dedup-result.json`. Both production tasks were verified running after installation.

Coverage includes persistent assertion dialogs and unhandled native exceptions,
including the diagnosed AE texture
encoder crash. A managed `Environment.FailFast` test exited without a native
dump; logs were retained and monitoring re-armed. Hangs, forced termination,
power loss, assertion dialogs disappearing between polls, and failures outside
these detection paths are not guaranteed
to produce a dump. A dump records process state at failure, not a recording of
every earlier UI action; AE's saved logs provide the available session history.

## Manual capture when automatic monitoring is disabled

1. Double-click `C:\Users\Shadow\Desktop\Codex\Capture AE Crash.cmd`.
2. Launch AE and reproduce the failure. Wait for ProcDump to finish writing.
3. The launcher prints the new folder under `Desktop\Codex\AE_Crash_Captures`.
   Add the asset name and exact steps to its `reproduction.txt`.

Each dated folder retains the dump, ProcDump output, tool version/hash and
arguments, AE/ToolHost versions and hashes, before/after AE logs, and matching
Windows Application events.
Full dumps are the default: the 2026-10-12 crash needed heap memory to recover
the exact texture name. That capture was about 2.5 GB. A normal AE exit creates
no dump; the automatic supervisor re-arms, or start another manual capture.
Ctrl+C in the manual launcher cancels and lets
ProcDump detach. Do not force-kill the debugged AE process to stop monitoring.
Existing evidence is never overwritten or automatically deleted.

The launcher uses the versioned script
[`capture_ae_crash.ps1`](../../tools/asset_editor/capture_ae_crash.ps1).
The automatic task uses [`watch_ae_crashes.ps1`](../../tools/asset_editor/watch_ae_crashes.ps1)
and is installed by [`install_ae_crash_monitor.ps1`](../../tools/asset_editor/install_ae_crash_monitor.ps1).
Assertions are watched by [`watch_ae_assertions.ps1`](../../tools/asset_editor/watch_ae_assertions.ps1).
CLI examples, from the workspace root:

```powershell
& './project/tools/asset_editor/capture_ae_crash.ps1' -Note 'Fresh AE launch; open CSC_BAKERS_Wind_Mill'
& './project/tools/asset_editor/capture_ae_crash.ps1' -CheckOnly
```

`-CheckOnly` validates the signed tool and shows the planned command without
starting a monitor or writing output. `-Mini` explicitly requests a smaller
dump, which can omit essential texture/object memory. `-OutputRoot` and
`-ProcDump` override local defaults; `-AssetEditorDirectory` selects the SDK
installation whose binary versions/hashes are recorded. To set up another machine, obtain ProcDump
from [Microsoft Sysinternals](https://learn.microsoft.com/en-us/sysinternals/downloads/procdump)
and preserve its valid Microsoft signature. The local executable is kept at
`Desktop\Codex\Tools\ProcDump\procdump64.exe`.

## Inspect the evidence

The file-only Python readers require the standard library:

```powershell
python './project/tools/art/inspect_ae_minidump.py' 'C:\path\AssetEditor.exe_timestamp.dmp'
python './project/tools/art/inspect_ae_texture_crash.py' 'C:\path\AssetEditor.exe_timestamp.dmp'
```

The general reader reports the exception and module-relative candidate stack
addresses. These are raw stack candidates, not a symbolically unwound backtrace.
Use WinDbg with matching modules/symbols for other failures or deeper analysis.
The texture reader applies **only** to the verified ToolHost null-call signature
(return RVA `0x4ffc81`, fault RIP zero); it refuses other crashes. An RVA alone
is not portable across tool versions. Save the affected module/version and
source-file hashes before making repairs, and retain an untouched source copy.
Compare evidence from the exact reproduction with the normal logs; their last
message may precede the real fault.

For managed exception `0xe0434352`, use the offline
[`inspect_ae_managed_dump.cs`](../../tools/asset_editor/inspect_ae_managed_dump.cs)
reader to recover the exception message and managed stack. The tested x64 .NET
Framework build and Microsoft ClrMD 1.1.142101 dependency are retained in
`Desktop\Codex\Tools\ClrMD`. Run the executable with the dump path and a matching
`mscordacwks.dll` path; this machine's matching DAC is
`C:\Windows\Microsoft.NET\Framework64\v4.0.30319\mscordacwks.dll`.
CLR/DAC versions must match the captured process; do not assume a future
Windows update leaves the current DAC suitable for an older dump.
The reader prints each thread's last thrown exception, which can be stale.
Match its OS thread ID to the dump's ExceptionStream fault thread before
attributing it to the crash. Microsoft documents the underlying library in
the [ClrMD repository](https://github.com/microsoft/clrmd).

## Confirmed 2026-10-12 AO2 failure

Evidence remains in `Desktop\Codex\AE_Crash_Diagnostic_20261012`:

- `AssetEditor.exe_261012_134524.dmp`: initial mini dump.
- `AssetEditor.exe_261012_134942.dmp`: full dump identifying `CSC_Atlas_AO2`.
- `before-texture-repair/`: the original incompatible DDS and TEX.
- `monitor*.log`: capture output; signed ProcDump is also retained in `tools/`.

Assembled buildings crashed while individual props and material previews
opened. Removing storage extensions and clearing caches did not solve it.
The texture encoder called a null function pointer while handling AO2 as
internal format 1009. Raw texconv R8 output had legacy `DDPF_LUMINANCE`
(`0x20000`); the working Firaxis scalar layout used `DDPF_RGB` (`0x40`),
8 bits, red mask `0xff`. Normalizing the header fixed the crash without changing
the baked image or mip payload. Henno confirmed Wind Mill and Tailors opened.

AE's source remains
`Working Files\3D Art\Textures\CSC_Atlas_AO2.png`. It matches the latest Storage
S/M bake deliverable byte-for-byte. Regenerating it through the same texconv
command reproduces all repaired DDS pixel/mip bytes (payload SHA256
`c3319f6b9e275dbe87a817f970761dafb80e19778aa1b67cdfbfe73317f98508`).
PNG SHA256: `a7de994a87464d584f6b8123e943b2fe28847bc68c459234d68c9ac1da04a856`.
Do not replace this PNG with an older atlas or decode the DDS over it: the PNG
is the authoring source, with its existing color metadata. The source PNG did
not contain the incompatible DDS header. Direct texconv conversion must run
the existing AO normalization and validation before installing the DDS;
`export_storage_sm_ao.py` now does so. AE reimport itself was not exercised by
automation during this repair.

The six Bakers/Tailors Storage S/M/L extension attachments were restored after
the diagnosis. Their backups and source provenance are in
`Desktop\Codex\Storage_Extensions_Restored_20261012_140342/restoration.json`.
Tailors L uses its newer crash-isolation snapshot placement, not the older
placement in Git. Restoration preserves all other AST bytes and later binding fixes.

## 15:07:55 model-instance crash

The automatic capture saved a complete 4,261,778,721-byte dump at
`Desktop\Codex\AE_Crash_Captures\20261012_145337_3d8de4\AssetEditor.exe_261012_150755.dmp`.
It took about 80 seconds to finish; Windows reported the crash afterward.

Confirmed facts:

- Unhandled read access violation `0xc0000005`, ToolHost RVA `0x2ac0e7`.
- Faulting instruction: `mov rsi, qword ptr [rcx + rbx*8 + 8]`.
  RBX was zero and RCX was `0xdbe4d7e150`, making the unmapped read address
  `0xdbe4d7e158`.
- Nearby compiled assertions name
  `FGXModelFramework_BehaviorInstanceSet.cpp` and check asset/model instance
  indices and `kAnimSet.Skeleton`. This is the model/animation instance update
  path, distinct from the repaired AO2 texture encoder.
- The exact session log records cutting attachments in Tailors Storage L,
  opening the new `CSC_ALL_Storage_L_Ext`, cutting and moving/rotating its
  attachments, then saving the extension at 15:07:53. The crash follows two
  seconds later. This associates the failure with that live editing sequence;
  it does not establish a defective extension file.

The invalid runtime pointer is consistent with stale or corrupt instance data
after live attachment edits. The exact lifetime/indexing bug cannot be proven
without matching native symbols or a repeatable isolated trigger. The user
continued editing both assets after restarting AE. A structural audit of the
then-current eight CSC dependencies found no missing parent model, missing CSC
child, cycle, duplicate point name, or mesh/material-group mismatch; those files
are not guaranteed to be the exact versions loaded at the crash. No speculative
asset edits were made. Keep the dump and original session log for comparison
against subsequent failures at this same native offset.

Five complete XML strings were subsequently recovered from the dump: two
Tailors Storage L copies (six attachments) and three Storage L extension copies
(15 attachments). They are retained in the dump folder's
`xml-recovered-from-memory/` with file offsets/encodings. No missing parent model,
missing bone, or mesh/material-group mismatch was found in these candidates
against the local GEO metadata. They may be cached or undo-history copies,
so they support the runtime-state diagnosis without proving the final live
instance state. The consolidated findings are in `diagnosis.txt` beside the dump.

## 15:18:37 duplicate preview-control crash

Automatic capture retained a complete 4,541,284,417-byte full dump in
`Desktop\Codex\AE_Crash_Captures\20261012_150922_9d5fba`:
`AssetEditor.exe_261012_151837.dmp`. Writing finished at 15:20:46.
`managed-exceptions.txt` contains the recovered managed stack.

The dump's ExceptionStream fault thread is `0x3b64`. ClrMD identifies that same
thread's exception as `System.Exception`, HRESULT `0x80131500`, message
**Duplicate knob created**. The exception stack is:

1. `Firaxis.CivTech.AssetPreviewer.KnobDatabase.ProcessPacket`
2. `Firaxis.CivTech.AssetPreviewer.KnobManager.SendNotificationPacketToUIThread`
3. `Firaxis.CivTech.AssetPreviewer._INTERNAL.ToolContextImpl.Notify`

This is a confirmed duplicate registration in AE's runtime preview-control
database. A "knob" here is an internal preview control/property; this message
does not establish duplicate attachment-point names in the asset XML.

Henno reports copying attachments into `CSC_ALL_Storage_L_Ext` from an asset
with different model instances/bones, then bulk changing both bindings. The
exact session log records Paste Attachments at 15:18:16, including 17 points
referencing unavailable `CSC_Storage_M` or `CSC_Storage_M_CON+PIL` instances,
followed by 17 EditModelInstance operations at 15:18:25 and 17 EditBoneName
operations at 15:18:28. It records saving `CSC_TAILORS_Storage_L.ast` at
15:18:29, then loading the default game environment at 15:18:37 before the
exception. Multiple documents were involved; do not claim the log saved the
extension at that moment.

Initial analysis associated the registration failure with the editing sequence.
Deeper analysis subsequently identified orphaned previews in both dumps and
AE's skipped document cleanup; see the
[preview cleanup diagnosis and repair](asset-editor-preview-cleanup-fix.md).
This is a different signature from
both the 15:07 native instance-data access violation and the repaired AO2
encoder crash. No asset files were changed speculatively. Reopening AE after
cross-asset pasting, or applying binding changes in smaller batches, are
workarounds to try rather than verified fixes. Keep the original dump/log and
compare future failures by exception message and stack, not only the last log
line or asset name.

The failure repeated at **15:32:52** while Henno was moving a barrel attachment
in `CSC_TAILORS_Storage_L.ast`. The full dump in
`Desktop\Codex\AE_Crash_Captures\20261012_152048_986c8a` is 4,724,543,951 bytes
with a complete memory payload. Fault thread `0x13a4` has the same
`System.Exception: Duplicate knob created` and identical exception stack.
The exact log records an unfinished Move Attachment transaction at 15:32:33,
save at 15:32:44, and environment reload at 15:32:52. The user-reported barrel
move is the editing context, not proof of the precise failing operation.
This second occurrence shows bulk model/bone editing is not required to
encounter the signature. Dump writing completed at 15:35:08 after 136 seconds;
AE can appear hung during this capture. The original dump, managed stack and
`diagnosis.txt` are retained together. No asset changes were made.
