---
name: shadow-sync
description: Sync Henno-Mods and the three Civ skill Git repos between Henno's Mac, Shadow and GitHub. Use for /shadow-sync, $shadow-sync, or an explicit request to sync these four repositories.
---

# Shadow sync

Run this routine from the Mac. Invoking it authorizes committing and pushing all
pending, non-ignored changes in these four repositories, including existing staged
changes, new files and deletions. A request to check/preview only does not authorize
commits or pushes. Respect any narrower scope in the current request.

The maintained implementation is beside this file. Resolve this skill's symlink
before finding `scripts/shadow_sync.py`; do not copy the implementation into outputs.

1. Run `python3 <resolved-skill-directory>/scripts/shadow_sync.py --check` first.
   Inspect the changed paths on both hosts. Read applicable repo instructions if
   changes require context. Ordinary source and skill changes are within the sync
   request; if new files clearly contain secrets or unrelated private data, stop
   before including those files. Ask only for a concrete unresolved issue.
2. Run `python3 <resolved-skill-directory>/scripts/shadow_sync.py` to sync. Use
   `--repo <name>` only when the user requests a subset; repeat it for multiple repos.
   `--message "..."` sets the checkpoint commit subject; host suffixes are added.
3. Summarize which repos synced, checkpoint commits, and any failure. Success requires
   matching full commit IDs on Mac, Shadow and freshly fetched GitHub refs, plus
   clean worktrees on both machines. Check mode uses cached refs and is only a preview.

The script validates the known checkout roots, origin URLs, branches and upstreams
on both hosts before committing. `civ6-gameplay` uses `master`; the others use `main`.
Mac skills live under `~/Play/.agents/skills`; Shadow's canonical skills live under
`C:\Users\Shadow\.agents\skills`. Their `.codex/skills` links are discovery aliases.
SSH uses `Shadow@100.122.143.96`, the verified Tailscale address, with existing keys
and host-key checking. `--shadow` can override the target if its binding changes.

The sequence per repo saves work on **both** hosts first, merges current GitHub
history into Mac and pushes, then merges that history into Shadow. If Shadow has
additional commits, stream them back over SSH as a Git bundle, fast-forward Mac,
and push from Mac. Finally fast-forward both hosts and verify their commit IDs.
Mac handles all GitHub writes: Shadow's Windows credential manager is unavailable
in SSH logins, and its existing GitHub CLI credential was invalid when tested.
Shadow's public HTTPS fetches work. No credentials are copied between machines.
Divergent history is preserved with ordinary merge commits.
Ignored output stays ignored; clean repos do not receive checkpoint commits.

Save pending editor changes and avoid editing these repos during the run. Stop on
conflicts, changed branch/upstream, active merge/rebase, SSH/authentication failure
or rejected push. Completed repos and checkpoint commits remain saved; sync is not
atomic across all four repos. Report the exact host/repo and remaining work. A
failed merge may remain open for review. Do not silently choose a conflict side,
stash, reset, clean, rebase published commits, force-push, or retry indefinitely.
Tool-required filesystem/network approval still applies; use escalation when needed.

For implementation changes, run `scripts/test_shadow_sync.py --scratch` with a folder
under `/Users/henno.gous/Play/codex-outputs/shadow-sync/`. Keep generated logs and test
repositories there. Transfer bundles are written under that output folder and
removed after successful import; failed bundles are kept for diagnosis. The routine
otherwise writes only Git's normal checkout metadata and changes needed to merge
the versioned repos.
