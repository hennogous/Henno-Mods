# CE development parity harness

This harness exercises the Lua-only package in `../ce_policy` with a complete
development CE build. Python controls and audits the experiment. Gameplay Lua
computes the policy, and CE owns the native hooks; no Python/Frida process
publishes incentives or installs code in the game.

Build the full CE fork using its `tools/README.md`, preserving its build receipt.
Then run `package_ce.py --ce <unmodified installed CE folder> --dll <fork DLL>
--output <fresh package folder>`. It copies only CE's small metadata/UI files
and the explicit compiled fork DLL, giving the development package a distinct
GUID/prefix. It never copies the original game DLL or changes an installation.
Build the Lua package separately with `../ce_policy/build.py --output <fresh
output folder>`. The two packages depend on each other through the development
GUID ending `2a06`; the policy GUID ends `2a07`.

For a regression using reviewed CSC source without overwriting the human mod,
`package_csc.py --installed-csc <reference> --source <CSC source> --output <fresh
copy>` creates a distinct dependency ending `2a08`. It preserves installed art
and overlays only the four adjacency source files, recording all copied/changed
hashes. This is a test snapshot, not a deployment or native validation. Build
the policy with `--csc-id <copy ID> --adjacency-core <copy Core.lua>`, then pass
the same `--csc-id` to the driver and point `--installed` at the copy. Add
`--reference-csc <human CSC folder>` to verify the human package is unchanged
alongside the active test copy. The controller still restores the exact original
subscription preferences. Default identities and existing callers are unchanged.

Install these into new, dedicated local mod folders while Civ is closed.
Leave the existing stock CE and CSC files unchanged. Do not overlay the fork
into a Workshop subscription or enable two GameCore providers together.

## Run

The driver requires explicit paths:

```text
python -B driver.py
  --output <fresh evidence directory>
  --binary <CivilizationVI.exe>
  --user-root <native Firaxis user directory containing Logs>
  --ce <isolated development CE mod folder>
  --package <isolated Lua policy mod folder>
  --installed <existing CSC mod folder>
  --stock-ce <existing unmodified local CE folder>
  --save-directory <native Saves/Single directory>
  --endpoint 100 --lifecycle
```

This creates one Online test world, advances through6, saves the exact inactive
boundary once, checks a second observation-only world1–2 in the same process,
then reloads the saved6 and compares captured scanner facts. Only then does it
continue toward100. Endpoint2–100 is accepted; the lifecycle exercise requires
at least6. Omit `--lifecycle` for a single fresh-world carrier check.

Every accepted active snapshot is compared with the existing Python shortlist.
This audit does not publish policy into the game. The test checks loaded module
paths/hashes, source/package identities, native capability/fault state and
original-human exclusions. It closes normally and restores exact mod entries
and autostart. A failed operation is not automatically replayed or a saved game
silently rebased. Inspect the archived journal and raw replies before recovery.

For an orderly early stop, write `{"reason":"explanation"}` to
`<evidence directory>/stop-request.json`. The sole driver accepts it at the next
inactive boundary, then performs its normal retirement/restoration. Do not send
competing Tuner commands or edit any pinned Python/Lua/package files while it runs.

## Audit

After closure:

```text
python -B analyze.py <evidence directory>
```

The auditor reconstructs bounded Lua-log chunks and rejects missing/conflicting
parts. It deduplicates frozen journals by native generation/version/record index,
validates complete trace coverage, binds every NetValue change to its published
pair and checks signed arithmetic, floors and protected values. Cache, winner
and PV observations must remain read-only. Native traces and corrected string
transport are documented in the fork's `native/README.md`.

Use `result.json`, `parity-audit.json`, `reload-scanner-parity.json`,
`preferences-restored.json`, `session-closed.json`, module/build receipts and the
source pins together. A successful record audit alone does not establish a
completed run, matched historical outcomes, AI quality or release readiness.

Run `python -B -m unittest discover -s <this directory> -p "test_*.py" -v` offline.
On the restricted Windows host, set TEMP/TMP to an existing writable scratch
directory. The actual-Lua tests are maintained in `../ce_policy` and the shared
scanner tests alongside its original source.
