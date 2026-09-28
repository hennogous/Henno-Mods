#!/usr/bin/env python3
"""Commit and converge the four known Civ repos without rewriting history."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys

sys.dont_write_bytecode = True

from git_worker import SyncError, operate


def bindings():
    play = Path.home() / "Play"
    shadow_skills = "C:/Users/Shadow/.agents/skills/"
    specs = [{"name": "Henno-Mods", "github": "hennogous/Henno-Mods",
              "branch": "main", "mac": str(play / "Henno-Mods"),
              "shadow": "C:/Users/Shadow/Documents/Firaxis ModBuddy/Civilization VI/Henno Mods"}]
    for name in ("civ-supply-chains", "civ6-art", "civ6-gameplay"):
        specs.append({"name": name, "github": f"hennogous/{name}",
                      "branch": "master" if name == "civ6-gameplay" else "main",
                      "mac": str(play / ".agents/skills" / name),
                      "shadow": shadow_skills + name})
    return specs


def remote(request, target):
    source = Path(__file__).with_name("git_worker.py").read_text(encoding="utf-8")
    payload = "import json\n" + source + "\nprint(json.dumps(handle(json.loads(" + repr(json.dumps(request)) + "))))\n"
    result = subprocess.run(
        ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=10", "-o",
         "ServerAliveInterval=15", "-o", "ServerAliveCountMax=3", target,
         'py -3 -c "import sys;exec(sys.stdin.read())"'],
        input=payload, capture_output=True, encoding="utf-8", errors="replace", timeout=700,
    )
    if result.returncode:
        raise SyncError(f"Shadow SSH failed: {result.stderr or result.stdout}")
    try:
        response = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise SyncError(f"Unexpected Shadow response: {result.stdout}\n{result.stderr}") from error
    if not response["ok"]:
        raise SyncError(response["error"])
    return response["result"]


def synchronize(specs, call, message, preview=False):
    # Preflight every selected checkout on both hosts before any checkpoint.
    states = {}
    for spec in specs:
        for host in ("mac", "shadow"):
            state = call(spec=spec, host=host, action="inspect")
            states[spec["name"], host] = state
            print(f"{spec['name']} / {host}: {state['branch']} {state['head'][:12]}", flush=True)
            print(state["status"] or "  clean", flush=True)
    if preview:
        print("Preview only; origin refs are cached. No commits, fetches or pushes.", flush=True)
        return []
    completed = []
    for spec in specs:
        name = spec["name"]
        for host in ("mac", "shadow"):
            print(f"{name}: saving {host} work", flush=True)
            saved = call(spec=spec, host=host, action="checkpoint", message=message,
                         expected=states[name, host])
            if saved["checkpoint"]:
                print(f"  checkpoint {host}: {saved['checkpoint']}", flush=True)
        print(f"{name}: merging GitHub into Mac and pushing", flush=True)
        call(spec=spec, host="mac", action="publish")
        print(f"{name}: merging Mac/GitHub into Shadow and pushing", flush=True)
        call(spec=spec, host="shadow", action="publish")
        print(f"{name}: fast-forwarding Mac and verifying", flush=True)
        mac = call(spec=spec, host="mac", action="finish")
        shadow = call(spec=spec, host="shadow", action="finish")
        mac = call(spec=spec, host="mac", action="inspect")
        if len({mac["head"], shadow["head"], mac["origin_head"], shadow["origin_head"]}) != 1:
            raise SyncError(f"{name}: heads differ after sync; another writer may be active")
        if mac["status"] or shadow["status"]:
            raise SyncError(f"{name}: worktree changed during verification")
        completed.append(name)
        print(f"SYNCED {name}: {mac['head']} (Mac = Shadow = GitHub)", flush=True)
    return completed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="read-only preview on both hosts")
    parser.add_argument("--repo", action="append", choices=[s["name"] for s in bindings()])
    parser.add_argument("--message", default="Shadow sync checkpoint " + datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"))
    parser.add_argument("--shadow", default="Shadow@100.122.143.96")
    args = parser.parse_args()
    specs = [s for s in bindings() if not args.repo or s["name"] in args.repo]

    def call(**request):
        if request["host"] == "mac":
            return operate(**request)
        return remote(request, args.shadow)

    try:
        synchronize(specs, call, args.message, preview=args.check)
    except (SyncError, OSError, subprocess.TimeoutExpired) as error:
        print(f"STOPPED: {error}\nCompleted repos and checkpoint commits remain saved."
              " Inspect this failure before rerunning.", file=sys.stderr, flush=True)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
