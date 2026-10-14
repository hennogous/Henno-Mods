# Asset Editor orphan preview cleanup

Status, 2026-10-12: cause identified in two full crash dumps; one-byte repair
installed and hash-verified at 16:41:39 local time; offline checks passed.
Manual AE validation remains pending. This addresses **Duplicate knob created**; earlier native
model-instance and exit-assertion failures have different signatures.

## Cause and evidence

AE can retain an asset's preview after its document closes when another open
asset depends on it. Reopening the child creates another preview with the same
control group. The native preview sends another creation notification for
**Show Obstructions**, and the managed control database throws.

Both dumps contain an orphaned Tailors Storage L preview while Tailors Classical
Base 03 is open. That parent directly attaches Storage L; Storage L attaches the
Storage L extension. Attachment editing was the setting in which the fault
appeared, but dragging or bulk bone changes are not established as the failing
operation. The later dump's main UI thread is inside
`AssetBrowserFileCommands.DoOpen` / `BaseEntityEditor.Open`, creating a new
document preview when the notification worker throws.

Evidence under `Desktop\Codex\AE_Crash_Captures`:

| Capture | Preview registrations | Main document registry |
|---|---|---|
| `20261012_150922_9d5fba/AssetEditor.exe_261012_151837.dmp` | L windows 1 and 9 | Only new L document/window 9 is open; window 1 is orphaned |
| `20261012_152048_986c8a/AssetEditor.exe_261012_153252.dmp` | L windows 4 and 5; extension window 1 | Only new L document/window 5 is open; old L window 4 and extension window 1 are orphaned |

In the later dump, fault-thread stack arguments preserve the native creation
callback's name `LPWS_OBVisibility`, group
`CSC_TAILORS_Storage_L_CSC_TAILORS_Storage_L_0`, label `Show Obstructions`,
and type 3 (boolean). Existing managed `BoolKnob` at `0x28e0cc705f0` has exactly
the same name/group/label. The old and new L documents have the same URI and
distinct preview wrappers. These are entries in the live `PreviewWindows`
dictionary, not merely objects awaiting garbage collection. The database throws
on an existing name hash within the same group. No attachment-name change is
indicated by this evidence.

The offline reader
[`inspect_ae_knob_dump.cs`](../../tools/asset_editor/inspect_ae_knob_dump.cs)
accepts `--registry` to compare live documents with preview registrations using
CLR field metadata. Other modes: `--documents`, `--threads`,
`--name=LPWS_OBVisibility`, and `--type=Fully.Qualified.Type`.
[`inspect_ae_il.cs`](../../tools/asset_editor/inspect_ae_il.cs) reads SDK IL
without executing editor code. Native captured memory is queryable with
[`query_ae_dump.py`](../../tools/asset_editor/query_ae_dump.py).

## Cleanup defect and repair

`Firaxis.AssetPreviewing.dll`, assembly version 1.0.0.0:
`PreviewerDocumentService.DocumentRegistry_DocumentRemoved` calls
`UnbindSurrogatePreviewer(removedDocument)`. When an open previewable dependent
exists, that helper unbinds the display and returns true. The removal handler
then returns immediately at IL `0011`, skipping
`ShutdownDocumentPreviewing`, `AssetPreviewer.CloseWindow`, and removal from
`PreviewWindows`.

The helper applies to asset dependencies as well as non-previewable documents
such as materials. The repair preserves that call and display unbinding but
sends its true branch to the existing previewable-document check at IL `0013`.
Previewable assets use the normal shutdown/close/remove path. Non-previewable
documents return at the existing null-adaptation check. The duplicate exception
is not suppressed; no mod asset is modified.

The assembly has no strong-name public key or Authenticode signature. The patch
preserves size, metadata, method layout, identity and all code except one
short-branch displacement byte:

| Property | Value |
|---|---|
| Method token / RVA | `0x060002b8` / `0xd7a0` |
| File offset / byte | `0xb9be`: `7a` → `00` |
| Original SHA256 | `b1855d6319f0ce804162342252892247fd3540da25f0f6872d64713f4a38f990` |
| Patched SHA256 | `6a897703193d74e86f01aa657f1ca5ea71e8879d5777a2410ceb70da3868c9bf` |

Do not apply these offsets to another SDK build. The preparer refuses a different
original hash. Steam verification or an SDK update can restore the original DLL;
check hashes before any reinstallation.

## Validation and remaining limits

The offline validator compares all **1,176 method bodies**: only the intended
branch target differs. It interprets the actual removal method IL for all eight
combinations of surrogate present/absent, previewable/non-previewable document,
and tracked/untracked window. The original surrogate-plus-previewable path
reproduces skipped cleanup; the patched path performs cleanup. Material handling
and ordinary removal retain their prior call traces. An untracked preview still
follows AE's existing assertion path. Engine calls are substituted, so these
tests do not prove native window/control destruction in a live session.

Manual test: launch fresh AE, open Classical Base 03 and Storage L, edit/save a
barrel attachment, close L with Base 03 still open, reopen L, and repeat the
edit/close/reopen cycle. Also check the extension and a material. Record any
crash with its exact capture and action. Automatic crash/assertion monitoring
remains enabled. Do not declare all attachment-editing crashes fixed by this
narrower repair.

## Installation and rollback

Package: `C:\Users\Shadow\Desktop\Codex\AE_Preview_Cleanup_Fix_20261012`.
Exact original/patched DLLs, `patch-manifest.json`, `offline-validation.txt` and
the version/hash-checked installer are retained there. Installation requires AE
closed and SDK write access, records `install-result.json`, and refuses unknown
installed hashes. A failed overwrite restores the previous verified copy.

Installation succeeded with no AE process running. The first two attempts
refused safely while AE was open. Sandboxed process enumeration had hidden
that process; use full process visibility for the installation guard rather
than inferring closure from a sandboxed `Get-Process` result. The installed DLL
hash matches the patched copy. Original backup hash matches the stock DLL.

Affected installed file:
`C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK\AssetModTools\AssetEditor\Firaxis.AssetPreviewing.dll`.

Run the package's `install_preview_cleanup_patch.ps1` with `-Mode Check`,
`-Mode Install`, or `-Mode Restore`, and
`-PackageDirectory 'C:\Users\Shadow\Desktop\Codex\AE_Preview_Cleanup_Fix_20261012'`.
Restore puts back the exact original DLL after checking the current hash.
Versioned sources:
[`prepare_preview_cleanup_patch.py`](../../tools/asset_editor/prepare_preview_cleanup_patch.py),
[`validate_preview_cleanup_patch.cs`](../../tools/asset_editor/validate_preview_cleanup_patch.cs),
[`install_preview_cleanup_patch.ps1`](../../tools/asset_editor/install_preview_cleanup_patch.ps1).

Without the patch, start fresh and edit the child alone. If both parent and child
must be open, close the parent before closing and reopening the child. Restart
after a session may have orphaned a preview; closing visible tabs alone does
not remove those stale registrations. This workaround follows the observed
branch condition but also needs runtime review.
