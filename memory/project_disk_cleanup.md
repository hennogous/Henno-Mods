# Disk cleanup on Shadow

## 8 November 2026

Henno approved the remaining cleanup candidates and explicitly authorized deleting
the full `Desktop/Codex/csc-ai-paired-standard-20261016` archive. Verified absent
after removing its remaining 4,156 files, 7,971,507,580 bytes. The previous cleanup
in `AI tuning 2` had already removed its 27 cumulative log snapshots and hardlinked
the separate `csc-ai-integrated-20261108` package copies. Those earlier savings
are excluded from this pass.

The November 6 natural and November 7 qualification archives now share disk
storage for 9,193 independently stored, SHA-256-identical cooked assets. All
9,193 paths were verified against their canonical files after replacement.
Treat these archive copies as immutable and copy a package out before editing
it. Removed 588 `.obj` intermediates from successful closed CE builds while
retaining binaries and build records. Frida temp cleanup was deferred because
the live process check found Civilization VI running.

This pass reclaimed 36.709 GiB by file accounting, with 84.553 GiB free on C:
at final verification. Receipts are in `Desktop/Codex/disk-cleanup-20261108/`
(`bakers-asset-hardlinks-5e247e87.jsonl`, `intermediates-04541289.json`,
`frida-temp.json`).

## 10 November 2026

Removed the retired CE AI Development Fork and CSC CE Policy Parity local
installs with Civ VI closed. Verified byte-identical copies in
`Desktop/Codex/csc-ce-parity-20261104` before removal.

Removed 225 older named AI test saves from the live Single save directory
after verifying SHA-256-identical copies in the test archives. This reclaimed
351,011,662 bytes. The restore index is
`Desktop/Codex/csc-retired-test-save-cleanup-20261110.json`. Personal saves,
autosaves, saves from November 8 onward and unique test saves were retained.
