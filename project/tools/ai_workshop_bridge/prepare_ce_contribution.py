"""Prepare and compile a proposed CE-owned district-score capability, without deployment.

Historical object-only candidate. The current native implementation and its
reporting/lifecycle fixes live in the CE fork, not this generator's old bridge.c.
See ce_policy/ and ce_parity/ for the subsequently qualified development path.

The pinned CE checkout is a read-only input. Outputs include an unapplied Main.cpp
patch and two COFF objects; this does not build or execute a Community Extension DLL.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys

from build import GAMECORE_SHA256, PE, generate_identity_header, sha256, source_pins, write_json, write_text


HERE = Path(__file__).resolve().parent
CE_COMMIT = "e59b5aa910c8a0fcab9b31973ffa477443de0e09"
CE_MAIN_SHA256 = "70d9a9d6d554dcd04b52a107978ee50491948a77f4cec046028e3b324466d194"
CE_LICENSE_SHA256 = "8486a10c4393cee1c25392769ddd3b2d6c242d6ec7928e1414efff7dfb2f07ef"

HEADER = """/* Proposed CE integration points. Not present in released CE1.3. */
#pragma once
#ifndef WIN32_LEAN_AND_MEAN
#define WIN32_LEAN_AND_MEAN
#endif
#include <windows.h>
#ifdef __cplusplus
extern "C" {
#endif
int CE_AIDistrictScoresInitialize(HMODULE core);
void CE_AIDistrictScoresRegisterLua(void *L);
void CE_AIDistrictScoresReset(void);
#ifdef __cplusplus
}
#endif
"""

INTEGRATION = """# Proposed Community Extension district-score capability

This is a review package for a new CE-owned native API. It is **absent from the
installed CE1.3**. No CSC DLL is produced or required by this proposed architecture:
CE would own the compiled hook, while a normal Workshop SQL/Lua mod would publish
numeric incentives through the CE dependency.

## Files and integration

- `native/CSC_AIDistrictScores.c` is the independently authored bridge compiled in
  `CSC_CE_INTEGRATION` mode. It has no separate DLL entry point in that mode.
- `native/hook_entry.S` preserves the native calling convention and caller R12.
- `native/CSC_AIDistrictScores.h` declares the three CE integration points.
- `native/target_identity.h` identifies the exact qualified original GameCore.
- `Main.cpp.patch` is unapplied, against CE commit
  `e59b5aa910c8a0fcab9b31973ffa477443de0e09`. The input checkout was not modified.
- `objects/` contains separately compiled AMD64 COFF objects, **not a linked DLL**.

Add the header and C source to a complete CE checkout and define
`CSC_CE_INTEGRATION` for this C source. Compile the C file as C11 (MSVC `/TC` and
the appropriate C standard setting), not as C++. Link the shim object built from
`hook_entry.S`, CE's MinHook implementation and Windows `Bcrypt.lib`. Preserve
CE's existing dependencies and build settings. The provided Zig object check
does not establish MSVC compatibility or complete CE project integration.

The proposed Main.cpp changes register Lua methods in the gameplay registration
hook only; initialize the capability after HavokScript/MinHook initialization;
reset policy on context creation; and reset before forwarding context destruction.
Only the existing `DllDestroyGameContext` export forwarder is replaced. Verify its
name/ordinal and the entire original export contract in a complete linked build.

## Proposed Lua API and ownership

`CE_AIDistrictScoresBegin(version,width,height,districtCount)` disables current
policy and opens a staged publication. `Allow(playerId)` records original AI
identities. `Entry(player,city,district,plot,delta)` adds bounded numeric rows.
`Commit()` publishes the completed snapshot. `Disable()` retires it, and
`Status()` reports readiness, counters and sampled changes. These are globals
prefixed `CE_AIDistrictScores`, not methods supplied by released CE1.3.

The scoring hook performs native numeric lookup only. Lua runs outside the hook.
Original-human identities must be captured before autoplay changes roles, and
policy must be rebuilt for a new context/load. A changed generation prevents an
in-flight old-policy callback from applying a stale adjustment; this is not a
guarantee that every row in an entire asynchronous analysis pass uses one policy.
Existing cache values and retained requests can preserve earlier influence.

## Qualification still required

The receipt proves only preparation, source pins and C/assembly COFF compilation.
It does not build the complete CE DLL, execute it, verify the installed CE binary
against this source, or establish safe unload, multiplayer or other platforms.
Before release, CE must adopt or otherwise distribute this capability, and its
maintainer must review initialization/failure behavior, existing hook coexistence,
context destruction and recreation, worker completion, publication timing,
ownership exclusions, arithmetic, budgets and loaded-image verification.

The existing own-carrier smoke result does not substitute for running this
CE-integrated build. CSC should fail closed when the new CE capability is absent;
do not substitute unfinished `RegisterCallEvent` callbacks for this typed bridge.

## Source and distribution boundary

The patch changes CE source, whose existing `LICENSE.txt` is included unchanged
as `CE-LICENSE-reference.txt`; see that license and the upstream README when
reviewing a contribution or distributing a derivative CE build. This document
does not resolve licensing for a future combined distribution. The native source
here was independently authored; MinHook remains a separately licensed dependency
with its own notice. No external maintainer message, publication, installation or
game execution was performed by this preparation tool.
"""


def replace_once(text: str, before: str, after: str, label: str) -> str:
    if text.count(before) != 1:
        raise ValueError(f"Expected exactly one pinned CE {label} anchor")
    return text.replace(before, after, 1)


def main_patch(original: str) -> tuple[str, str]:
    updated = replace_once(original, '#include "NationalParks.h"\n',
                           '#include "NationalParks.h"\n#include "native/CSC_AIDistrictScores.h"\n',
                           "header")
    updated = replace_once(updated,
        'void __cdecl Hook_RegisterScriptData(hks::lua_State* L) {\n'
        '    std::cout << "Registering lua globals!\\n";\n\n    PushSharedGlobals(L);\n',
        'void __cdecl Hook_RegisterScriptData(hks::lua_State* L) {\n'
        '    std::cout << "Registering lua globals!\\n";\n\n    PushSharedGlobals(L);\n'
        '    CE_AIDistrictScoresRegisterLua(L);\n', "gameplay Lua registration")
    updated = replace_once(updated,
        '        hks::InitHavokScript();\n        InitHooks();\n',
        '        hks::InitHavokScript();\n'
        '        if (!CE_AIDistrictScoresInitialize(Runtime::GameCore)) {\n'
        '            std::cout << "CE district-score capability unavailable; policy disabled.\\n";\n'
        '        }\n'
        '        CE_AIDistrictScoresReset();\n        InitHooks();\n', "initialization")
    updated = replace_once(updated,
        '        return base_DllCreateGameContext();\n    }\n}\n',
        '        return base_DllCreateGameContext();\n    }\n\n'
        '    __declspec(dllexport) void __cdecl DllDestroyGameContext(void* context) {\n'
        '        CE_AIDistrictScoresReset();\n'
        '        using DestroyContext = void (__cdecl *)(void*);\n'
        '        auto destroy = reinterpret_cast<DestroyContext>(\n'
        '            GetProcAddress(Runtime::GameCore, "DllDestroyGameContext"));\n'
        '        if (destroy) destroy(context);\n    }\n}\n', "destroy wrapper")
    forwarder = '#pragma comment(linker,"/export:DllDestroyGameContext=GameCore_XP2_FinalRelease.DllDestroyGameContext,@156")\n'
    updated = replace_once(updated, forwarder,
        '#pragma comment(linker,"/export:DllDestroyGameContext,@156")\n', "destroy export")
    before_forwarders = [line for line in original.splitlines()
                         if '#pragma comment(linker,"/export:' in line and "DllDestroyGameContext" not in line]
    after_forwarders = [line for line in updated.splitlines()
                        if '#pragma comment(linker,"/export:' in line and "DllDestroyGameContext" not in line]
    if before_forwarders != after_forwarders:
        raise ValueError("An unrelated CE export directive changed")
    if updated.count("CE_AIDistrictScoresRegisterLua(L);") != 1:
        raise ValueError("Unexpected Lua registration count")
    patch = "".join(difflib.unified_diff(original.splitlines(keepends=True),
                                       updated.splitlines(keepends=True),
                                       fromfile="a/Main.cpp", tofile="b/Main.cpp"))
    return patch, updated


def check_coff(path: Path) -> dict:
    data = path.read_bytes()
    if len(data) < 20:
        raise ValueError(f"Truncated COFF object: {path}")
    machine, sections = struct.unpack_from("<HH", data)
    optional_size = struct.unpack_from("<H", data, 16)[0]
    if machine != 0x8664 or sections < 1 or optional_size != 0 or data[:2] == b"MZ":
        raise ValueError(f"Not an ordinary AMD64 COFF object: {path}")
    return dict(path=str(path), bytes=len(data), sha256=sha256(path),
                machine="amd64", section_count=sections, linked_dll=False)


def prepare(args: argparse.Namespace) -> dict:
    zig, minhook, gamecore, ce_source = [Path(p).resolve(strict=True) for p in
                                       (args.zig, args.minhook, args.gamecore, args.ce_source)]
    output = args.output.resolve()
    if not zig.is_file() or not minhook.is_dir() or not gamecore.is_file() or not ce_source.is_dir():
        raise ValueError("Expected a compiler, dependency directory, GameCore file and CE source directory")
    if any(output == p or output.is_relative_to(p) for p in (HERE, ce_source, gamecore.parent)):
        raise ValueError("Output must be separate from source and installed game directories")
    ce_main, ce_license = ce_source / "Main.cpp", ce_source / "LICENSE.txt"
    if sha256(ce_main) != CE_MAIN_SHA256 or sha256(ce_license) != CE_LICENSE_SHA256:
        raise ValueError("CE Main.cpp/LICENSE.txt do not match the pinned reviewed commit")
    if sha256(gamecore) != GAMECORE_SHA256:
        raise ValueError("Original GameCore is not the qualified pristine build")
    bridge, assembly = HERE / "bridge.c", HERE / "hook_entry.S"
    if "#ifdef CSC_CE_INTEGRATION" not in bridge.read_text(encoding="utf-8-sig"):
        raise ValueError("The bridge lacks the CE integration branch")
    dependency_inputs = list((minhook / "include").rglob("*.h"))
    if not (minhook / "include" / "MinHook.h").is_file():
        raise ValueError("MinHook headers are missing")
    inputs = [Path(__file__).resolve(), HERE / "build.py", bridge, assembly,
              ce_main, ce_license, *dependency_inputs]
    before_pins = source_pins(inputs)
    compiler_hash = sha256(zig)
    native = output / "contribution" / "native"
    objects = output / "objects"
    logs = output / "compile-logs"
    for directory in (native, objects, logs):
        directory.mkdir(parents=True, exist_ok=True)
    contribution = native.parent
    shutil.copyfile(bridge, native / "CSC_AIDistrictScores.c")
    shutil.copyfile(assembly, native / "hook_entry.S")
    write_text(native / "CSC_AIDistrictScores.h", HEADER)
    write_text(native / "target_identity.h", generate_identity_header(PE(gamecore)))
    original_text = ce_main.read_text(encoding="utf-8-sig")
    patch, updated = main_patch(original_text)
    write_text(contribution / "Main.cpp.patch", patch)
    write_text(contribution / "Main.cpp.proposed", updated)
    write_text(contribution / "integration.md", INTEGRATION)
    shutil.copyfile(ce_license, contribution / "CE-LICENSE-reference.txt")
    environment = os.environ.copy()
    environment["ZIG_LOCAL_CACHE_DIR"] = str(output / "zig-local-cache")
    environment["ZIG_GLOBAL_CACHE_DIR"] = str(output / "zig-global-cache")
    commands = [
        [str(zig), "cc", "-target", "x86_64-windows-gnu", "-std=c11", "-O2",
         "-DCSC_CE_INTEGRATION", "-I" + str(minhook / "include"), "-I" + str(native),
         "-c", str(bridge), "-o", str(objects / "CSC_AIDistrictScores.obj")],
        [str(zig), "cc", "-target", "x86_64-windows-gnu", "-c", str(assembly),
         "-o", str(objects / "hook_entry.obj")],
    ]
    compilations = []
    for index, command in enumerate(commands, 1):
        write_json(logs / f"command-{index}.json", command)
        result = subprocess.run(command, cwd=output, env=environment,
                                capture_output=True, text=True, errors="replace", check=False)
        write_text(logs / f"stdout-{index}.log", result.stdout)
        write_text(logs / f"stderr-{index}.log", result.stderr)
        compilations.append(dict(command=command, returncode=result.returncode))
        if result.returncode:
            raise RuntimeError(f"COFF compilation {index} failed; see {logs}")
    if before_pins != source_pins(inputs) or sha256(zig) != compiler_hash:
        raise ValueError("A read-only input changed during preparation")
    manifest = dict(
        schema="csc-ce-district-score-contribution-v1",
        prepared_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        upstream=dict(repository="https://github.com/Wild-W/CivilizationVI_CommunityExtension",
                      commit=CE_COMMIT, source=str(ce_source), source_modified=False,
                      installed_ce_1_3_has_proposed_api=False),
        original_gamecore=dict(path=str(gamecore), sha256=GAMECORE_SHA256, copied=False),
        compiler=dict(path=str(zig), sha256=compiler_hash), source_pins=before_pins,
        compilations=compilations, objects=[check_coff(objects / name) for name in
                                           ("CSC_AIDistrictScores.obj", "hook_entry.obj")],
        contribution_files=[dict(path=p.relative_to(output).as_posix(), bytes=p.stat().st_size,
                                 sha256=sha256(p)) for p in sorted(contribution.rglob("*")) if p.is_file()],
        validation=dict(coff_compilation=True, full_ce_link=False, msvc_build=False,
                        native_executed=False, game_launched=False, deployed=False,
                        workshop_published=False, external_message_sent=False,
                        csc_dll_produced=False),
    )
    write_json(output / "contribution-manifest.json", manifest)
    return dict(ok=True, contribution=str(contribution),
                manifest=str(output / "contribution-manifest.json"),
                objects=manifest["objects"], full_ce_build=False, native_executed=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("zig", "minhook", "gamecore", "ce-source", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args), indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, struct.error) as error:
        print(f"CE contribution preparation failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
