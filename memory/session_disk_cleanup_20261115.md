# Closed AI archive asset cleanup — 15 November 2026

Henno authorised freeing disk while the calibrated Continents game finishes.
Consolidated identical art assets in74 verified-closed packages under
`Desktop/Codex/csc-ai-problems-1-2-20261110`. The active November15 calibrated
test, frozen inputs, installed mods, source repositories, logs and saves were
untouched. The canonical and target SHA256 matched before each atomic hard-link
replacement. All paths and original bytes remain available.

15,841 links,26,203,844,210 bytes reclaimed by file accounting (**24.405GiB**).
About45.37GiB free at final verification; live game output explains the slightly
smaller net free-space change. Independently checked15,838 initial links and
217 canonical hashes; three long-filename cases were separately completed and
verified using short temporary basenames. Original error receipts retained.

Receipts/script: `Desktop/Codex/disk-cleanup-20261115/`:
`asset-links.jsonl`, `result.json`, `long-path-fixes.json`,
`independent-verification.json`, `deduplicate_closed_assets.py`.
Treat these archives as immutable: copy an archived package out before editing,
because linked assets share storage. This matches the November8 archive policy.

The initial broad inventory was stopped; the faster scoped scan skips reparse
points. Windows DirEntry.stat caches report zero inode/link count, so actual
Path.stat/OS identity is required for physical-storage accounting. Ghidra cleanup
dry-run found zero abandoned sessions and preserved one active session.

Henno clarified that obsolete raw experiments should be purged, with useful
findings in the repo and current tests/baselines retained. Removed32 superseded
October/early-November `csc-ai-*` folders (throughNovember8), preserving baseline,
vanilla, untuned, integrated comparison and tooling roots. Checked resolved paths,
absence of source repositories and absence of a process using each target before
native PowerShell removal. All32 verified absent. Purge reclaimed18.254GiB net;
63.616GiB free afterward. Exact list and receipt: `purge-plan.json` and
`purge-receipt.json` beside the asset-link receipts. Existing Markdown findings
and committed research tools remain; old hardcoded raw-artifact paths in retired
research scripts now point to purged experiments.

Preserved `csc-ai-baseline-20261015`, `csc-ai-baseline-turn400-20261016`,
`csc-no-csc-district-baseline-20261114`, current November10–15 tests, CE source and
build environments, and REA/Ghidra resources. Standing policy now recorded in
`project/docs/civ6-ai/maintenance.md` and `feedback_ai_evidence_retention.md`.
