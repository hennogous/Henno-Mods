"""Git operations shared by the Mac controller and its in-memory SSH worker."""

import os
from pathlib import Path
import subprocess
import sys


class SyncError(RuntimeError):
    pass


def git(path, *args, allowed=(0,)):
    env = dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="never")
    result = subprocess.run(
        ["git", "-c", "core.quotePath=false", "-C", str(path), *args],
        capture_output=True, encoding="utf-8", errors="replace", env=env,
        timeout=300,
    )
    if result.returncode not in allowed:
        raise SyncError(f"{path}: git {' '.join(args)} failed:\n"
                        f"{result.stdout}{result.stderr}".rstrip())
    return result.stdout.strip()


def github_repo(url):
    for prefix in ("https://github.com/", "git@github.com:", "ssh://git@github.com/"):
        if url.startswith(prefix):
            return url[len(prefix):].removesuffix(".git").rstrip("/")
    return None


def inspect_repo(spec, host):
    path = Path(spec[host]).resolve()
    root = Path(git(path, "rev-parse", "--show-toplevel")).resolve()
    if root != path:
        raise SyncError(f"{path}: expected a repository root, found {root}")
    branch = git(path, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch != spec["branch"]:
        raise SyncError(f"{path}: branch {branch!r}; expected {spec['branch']!r}")
    upstream = git(path, "rev-parse", "--abbrev-ref", "@{upstream}")
    if upstream != f"origin/{branch}":
        raise SyncError(f"{path}: unexpected upstream {upstream}")
    for option in ((), ("--push",)):
        urls = git(path, "remote", "get-url", *option, "--all", "origin").splitlines()
        if len(urls) != 1 or github_repo(urls[0]) != spec["github"]:
            raise SyncError(f"{path}: origin does not match {spec['github']}")
    for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD",
                   "rebase-merge", "rebase-apply", "BISECT_LOG", "index.lock"):
        marker_path = Path(git(path, "rev-parse", "--git-path", marker))
        if not marker_path.is_absolute():
            marker_path = path / marker_path
        if marker_path.exists():
            raise SyncError(f"{path}: active Git operation ({marker})")
    status = git(path, "status", "--porcelain=v1", "--untracked-files=all")
    if git(path, "ls-files", "--unmerged"):
        raise SyncError(f"{path}: unresolved conflicts")
    return {"name": spec["name"], "host": host, "path": str(path),
            "branch": branch, "head": git(path, "rev-parse", "HEAD"),
            "origin_head": git(path, "rev-parse", f"origin/{branch}"),
            "status": status}


def operate(spec, host, action, message="", expected=None):
    state = inspect_repo(spec, host)
    path = state["path"]
    if action == "inspect":
        return dict(state, checkpoint=None)
    if expected and any(state[k] != expected[k] for k in ("head", "status")):
        raise SyncError(f"{path}: changed since preview; inspect and run again")
    commit = None
    if action == "checkpoint":
        if state["status"]:
            git(path, "add", "--all", "--", ".")
            # An edited submodule cannot be saved by committing its parent.
            result = subprocess.run(["git", "-C", path, "diff", "--cached", "--quiet"],
                                    capture_output=True)
            if result.returncode == 1:
                git(path, "commit", "-m", f"{message} ({host})")
                commit = git(path, "rev-parse", "HEAD")
            elif result.returncode != 0:
                raise SyncError(f"{path}: cannot inspect staged changes")
    elif action in ("publish", "merge", "finish"):
        if state["status"]:
            raise SyncError(f"{path}: worktree became dirty; stop editing and retry")
        branch = spec["branch"]
        git(path, "fetch", "--no-tags", "origin", f"refs/heads/{branch}:refs/remotes/origin/{branch}")
        if action == "finish":
            git(path, "merge", "--ff-only", f"origin/{branch}")
        else:
            git(path, "-c", "merge.autoStash=false", "merge", "--no-edit", f"origin/{branch}")
            if action == "publish":
                git(path, "push", "origin", f"HEAD:refs/heads/{branch}")
    else:
        raise SyncError(f"Unknown action: {action}")
    final = inspect_repo(spec, host)
    if final["status"]:
        raise SyncError(f"{path}: worktree is still dirty after {action}")
    final["checkpoint"] = commit
    return final


def stream_bundle(spec, host, base, expected_head):
    """Stream only objects after the shared Mac commit; never copy credentials."""
    state = inspect_repo(spec, host)
    if state["status"] or state["head"] != expected_head:
        raise SyncError(f"{state['path']}: changed before bundle transfer")
    git(state["path"], "merge-base", "--is-ancestor", base, "HEAD")
    result = subprocess.run(
        ["git", "-C", state["path"], "bundle", "create", "-", f"{base}..HEAD"],
        stdout=sys.stdout.buffer, stderr=subprocess.PIPE, timeout=300,
    )
    if result.returncode:
        raise SyncError(result.stderr.decode("utf-8", errors="replace"))


def handle(request):
    try:
        return {"ok": True, "result": operate(**request)}
    except (SyncError, OSError, subprocess.TimeoutExpired) as error:
        return {"ok": False, "error": str(error)}
