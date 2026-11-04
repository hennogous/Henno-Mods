"""Build an independent Workshop-format GameCore bridge; never deploy or launch it.

The pristine game's export table supplies ABI metadata only. No game binary is
copied into the package. All generated artifacts, compiler caches and logs live
under the caller-selected output directory.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
GAMECORE_SHA256 = "324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c"
MOD_ID = "d0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a04"
PREFIX = "GameCore_XP2_CSC_Bridge"
DLL_NAME = PREFIX + "_FinalRelease.dll"
WRAPPERS = {"DllCreateGameContext", "DllDestroyGameContext"}
ORIGINAL_MODULE = "GameCore_XP2_FinalRelease"


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def write_json(path: Path, value: object) -> None:
    write_text(path, json.dumps(value, indent=2, ensure_ascii=False) + "\n")


class PE:
    """Small bounded PE32+ table reader, used without executing the artifact."""

    def __init__(self, path: Path):
        self.path = path
        self.data = path.read_bytes()
        if self.data[:2] != b"MZ":
            raise ValueError(f"Not an MZ image: {path}")
        header = self.unpack("<I", 0x3C)[0]
        if self.slice(header, 4) != b"PE\0\0":
            raise ValueError(f"Not a PE image: {path}")
        self.machine, count = self.unpack("<HH", header + 4)
        self.timestamp = self.unpack("<I", header + 8)[0]
        optional_size = self.unpack("<H", header + 20)[0]
        optional = header + 24
        if self.unpack("<H", optional)[0] != 0x20B or self.machine != 0x8664:
            raise ValueError("Expected an AMD64 PE32+ image")
        if optional_size < 112 or count > 96:
            raise ValueError("Invalid optional header or section count")
        self.header_size = self.unpack("<I", optional + 60)[0]
        self.image_size = self.unpack("<I", optional + 56)[0]
        number_directories = self.unpack("<I", optional + 108)[0]
        available_directories = (optional_size - 112) // 8
        if number_directories > available_directories:
            raise ValueError("Data directories exceed optional header")
        self.directories = [self.unpack("<II", optional + 112 + 8 * n)
                            for n in range(number_directories)]
        self.sections = []
        for n in range(count):
            entry = optional + optional_size + 40 * n
            virtual_size, rva, raw_size, raw_offset = self.unpack("<IIII", entry + 8)
            self.slice(raw_offset, raw_size)
            self.sections.append((rva, virtual_size, raw_offset, raw_size))

    def slice(self, offset: int, size: int) -> bytes:
        if offset < 0 or size < 0 or offset + size > len(self.data):
            raise ValueError(f"PE read outside file: offset={offset} size={size}")
        return self.data[offset:offset + size]

    def unpack(self, fmt: str, offset: int) -> tuple:
        return struct.unpack(fmt, self.slice(offset, struct.calcsize(fmt)))

    def offset(self, rva: int, size: int = 1) -> int:
        if rva < self.header_size and rva + size <= self.header_size:
            self.slice(rva, size)
            return rva
        matches = [raw + rva - base for base, _, raw, length in self.sections
                   if base <= rva and rva + size <= base + length]
        if len(matches) != 1:
            raise ValueError(f"PE RVA has no unique file-backed mapping: {rva:#x}")
        return matches[0]

    def string(self, rva: int) -> str:
        start = self.offset(rva)
        end = self.data.find(b"\0", start, min(start + 65536, len(self.data)))
        if end < 0:
            raise ValueError("Unterminated PE table string")
        self.offset(rva, end - start + 1)
        return self.data[start:end].decode("ascii", errors="strict")

    def directory(self, index: int) -> tuple[int, int]:
        return self.directories[index] if index < len(self.directories) else (0, 0)

    def exports(self) -> list[dict]:
        rva, size = self.directory(0)
        if not rva:
            return []
        entry = self.offset(rva, 40)
        _, _, _, _, _, base, count, name_count, functions, names, ordinals = self.unpack(
            "<IIHHIIIIIII", entry)
        if count > 65536 or name_count > 65536:
            raise ValueError("Excessive PE export table")
        names_by_index: dict[int, list[str]] = {}
        for n in range(name_count):
            name_rva = self.unpack("<I", self.offset(names + 4 * n, 4))[0]
            index = self.unpack("<H", self.offset(ordinals + 2 * n, 2))[0]
            if index >= count:
                raise ValueError("Export name ordinal outside function table")
            names_by_index.setdefault(index, []).append(self.string(name_rva))
        rows = []
        for index in range(count):
            address = self.unpack("<I", self.offset(functions + 4 * index, 4))[0]
            if not address:
                continue
            forwarder = self.string(address) if rva <= address < rva + size else None
            for name in names_by_index.get(index, [None]):
                rows.append(dict(name=name, ordinal=base + index, rva=address,
                                 forwarder=forwarder))
        return rows

    def imports(self) -> list[dict]:
        rva, size = self.directory(1)
        if not rva:
            return []
        rows = []
        for index in range(min(size // 20, 512)):
            descriptor = self.unpack("<IIIII", self.offset(rva + 20 * index, 20))
            if not any(descriptor):
                return rows
            lookup, _, _, name_rva, address = descriptor
            thunk = lookup or address
            functions = []
            for n in range(65536):
                value = self.unpack("<Q", self.offset(thunk + 8 * n, 8))[0]
                if not value:
                    break
                if value & (1 << 63):
                    functions.append(dict(ordinal=value & 0xFFFF))
                else:
                    functions.append(dict(name=self.string(value + 2)))
            else:
                raise ValueError("Unterminated import thunk table")
            rows.append(dict(dll=self.string(name_rva), functions=functions))
        raise ValueError("Unterminated or excessive import descriptor table")


def source_pins(paths: list[Path]) -> list[dict]:
    return [dict(path=str(p), bytes=p.stat().st_size, sha256=sha256(p))
            for p in sorted(set(paths))]


def generate_definition(exports: list[dict]) -> str:
    lines = [f"LIBRARY {PREFIX}_FinalRelease", "EXPORTS"]
    for row in exports:
        name, ordinal = row["name"], row["ordinal"]
        if not name or '"' in name or "\n" in name:
            raise ValueError("Expected safely representable named exports")
        if name in WRAPPERS:
            lines.append(f'  "{name}" @{ordinal}')
        else:
            lines.append(f'  "{name}"="{ORIGINAL_MODULE}.{name}" @{ordinal}')
    return "\n".join(lines) + "\n"


def generate_modinfo() -> str:
    mod = ET.Element("Mod", id=MOD_ID, version="1")
    properties = ET.SubElement(mod, "Properties")
    for key, value in {
        "Name": "CSC AI Workshop Bridge (prototype)",
        "Description": "Windows Gathering Storm native delivery prototype. Conflicts with other GameCore replacements. Research package; not qualified for release.",
        "Authors": "Henno",
        "CompatibleVersions": "2.0",
        "AffectsSavedGames": "1",
    }.items():
        ET.SubElement(properties, key).text = value
    dependencies = ET.SubElement(mod, "Dependencies")
    ET.SubElement(dependencies, "Mod", id="4873eb62-8ccc-4574-b784-dda455e74e68",
                  title="Expansion: Gathering Storm")
    frontend = ET.SubElement(mod, "FrontEndActions")
    config = ET.SubElement(frontend, "UpdateDatabase", id="CSC_AI_WorkshopBridge_Config")
    ET.SubElement(ET.SubElement(config, "Properties"), "LoadOrder").text = "20"
    ET.SubElement(config, "File").text = "Data/Config.sql"
    ingame = ET.SubElement(mod, "InGameActions")
    action = ET.SubElement(ingame, "AddGameplayScripts", id="CSC_AI_WorkshopBridge")
    ET.SubElement(ET.SubElement(action, "Properties"), "LoadOrder").text = "999990"
    ET.SubElement(action, "File").text = "Lua/CSC_AI_WorkshopBridge.lua"
    files = ET.SubElement(mod, "Files")
    for name in [f"Binaries/Win64/{DLL_NAME}", "Data/Config.sql",
                 "Lua/CSC_AI_WorkshopBridge.lua", "LICENSE-MinHook.txt"]:
        ET.SubElement(files, "File").text = name
    ET.indent(mod, space="  ")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(mod, encoding="unicode") + "\n"


def generate_identity_header(original: PE) -> str:
    lines = ["/* Generated from the SHA-qualified pristine GameCore; do not edit. */",
             "#pragma once",
             f'#define CSC_GAMECORE_SHA256 "{GAMECORE_SHA256}"',
             f"#define CSC_GAMECORE_TIMESTAMP {original.timestamp}u",
             f"#define CSC_GAMECORE_IMAGE_SIZE {original.image_size}u"]
    for name, rva in [("fingerprint_register", 0x5BDAC0), ("fingerprint_net", 0x52A440)]:
        raw = original.slice(original.offset(rva, 32), 32)
        values = ", ".join(f"0x{byte:02x}" for byte in raw)
        lines.append(f"static const unsigned char {name}[32] = {{ {values} }};")
    return "\n".join(lines) + "\n"


def build(args: argparse.Namespace) -> dict:
    zig, minhook, gamecore, output = [Path(value).resolve(strict=True) for value in
                                     (args.zig, args.minhook, args.gamecore, args.output)]
    if not zig.is_file() or not minhook.is_dir() or not gamecore.is_file() or not output.is_dir():
        raise ValueError("Expected executable/file/directory argument types")
    if output == HERE or output.is_relative_to(HERE):
        raise ValueError("Generated output must be outside the source directory")
    if sha256(gamecore) != GAMECORE_SHA256:
        raise ValueError("GameCore SHA-256 is not the qualified pristine XP2 build")
    original = PE(gamecore)
    exports = original.exports()
    if len(exports) != 157 or {x["name"] for x in exports} & WRAPPERS != WRAPPERS:
        raise ValueError("Unexpected pristine GameCore export contract")
    inputs = [HERE / "bridge.c", HERE / "hook_entry.S", HERE / "gameplay.lua"]
    native_sources = [minhook / "src" / p for p in
                      ("buffer.c", "hook.c", "trampoline.c", "hde/hde64.c")]
    license_path = minhook / "LICENSE.txt"
    for path in inputs + native_sources + [license_path]:
        if not path.is_file():
            raise FileNotFoundError(path)
    work, package = output / "build", output / "package"
    work.mkdir(parents=True, exist_ok=True)
    package.mkdir(parents=True, exist_ok=True)
    dll = package / "Binaries" / "Win64" / DLL_NAME
    dll.parent.mkdir(parents=True, exist_ok=True)
    definition = work / "exports.def"
    write_text(definition, generate_definition(exports))
    identity_header = work / "target_identity.h"
    write_text(identity_header, generate_identity_header(original))
    write_text(package / "Data" / "Config.sql",
               "-- Select this package's GameCore through Civ VI's configuration database.\n"
               f"UPDATE GameCores SET PackageId = '{MOD_ID}', DllPrefix = '{PREFIX}'\n"
               "WHERE GameCore = 'Expansion2';\n")
    write_text(package / "CSC_AI_WorkshopBridge.modinfo", generate_modinfo())
    (package / "Lua").mkdir(exist_ok=True)
    shutil.copyfile(HERE / "gameplay.lua", package / "Lua" / "CSC_AI_WorkshopBridge.lua")
    shutil.copyfile(license_path, package / "LICENSE-MinHook.txt")
    command = [str(zig), "cc", "-target", "x86_64-windows-gnu", "-shared", "-O2",
               "-static-libgcc", "-I" + str(minhook / "include"), "-I" + str(work),
               str(HERE / "bridge.c"), str(HERE / "hook_entry.S"),
               *(str(p) for p in native_sources), str(definition),
               "-lbcrypt", "-lkernel32", "-o", str(dll)]
    environment = os.environ.copy()
    environment["ZIG_LOCAL_CACHE_DIR"] = str(work / "zig-local-cache")
    environment["ZIG_GLOBAL_CACHE_DIR"] = str(work / "zig-global-cache")
    write_json(work / "command.json", command)
    write_json(work / "pristine-exports.json", exports)
    source_files = [Path(__file__).resolve(), *inputs, *native_sources, license_path]
    source_files += list((minhook / "include").rglob("*.h"))
    source_files += list((minhook / "src").rglob("*.h"))
    pins = source_pins(source_files)
    compiler_sha256 = sha256(zig)
    completed = subprocess.run(command, cwd=work, env=environment, capture_output=True,
                               text=True, errors="replace", check=False)
    write_text(work / "compile.stdout.log", completed.stdout)
    write_text(work / "compile.stderr.log", completed.stderr)
    if completed.returncode:
        raise RuntimeError(f"Compiler exited {completed.returncode}; see {work / 'compile.stderr.log'}")
    if source_pins(source_files) != pins or sha256(zig) != compiler_sha256:
        raise ValueError("Build inputs changed while the compiler was running")
    built = PE(dll)
    built_exports = built.exports()
    actual = {(row["name"], row["ordinal"]): row for row in built_exports}
    for expected in exports:
        key = expected["name"], expected["ordinal"]
        if key not in actual:
            raise ValueError(f"Built DLL missing original export name/ordinal {key!r}")
        forwarder = actual[key]["forwarder"]
        wanted = None if key[0] in WRAPPERS else ORIGINAL_MODULE + "." + key[0]
        if forwarder != wanted:
            raise ValueError(f"Incorrect forwarding contract for {key[0]}: {forwarder!r}")
    manifest = dict(
        schema="csc-ai-workshop-bridge-build-v1",
        built_at=dt.datetime.now(dt.timezone.utc).isoformat(),
        mod_id=MOD_ID, dll_prefix=PREFIX, package=str(package),
        original_gamecore=dict(path=str(gamecore), sha256=GAMECORE_SHA256,
                               exports=exports, copied=False),
        compiler=dict(path=str(zig), sha256=compiler_sha256, command=command),
        source_pins=pins,
        generated_definition=dict(path=str(definition), sha256=sha256(definition)),
        generated_identity=dict(path=str(identity_header), sha256=sha256(identity_header),
                                timestamp=original.timestamp, image_size=original.image_size),
        native=dict(path=str(dll), sha256=sha256(dll), exports=built_exports,
                    imports=built.imports()),
        package_files=[dict(path=p.relative_to(package).as_posix(), bytes=p.stat().st_size,
                            sha256=sha256(p)) for p in sorted(package.rglob("*")) if p.is_file()],
        validation=dict(original_exports_preserved=True, native_executed=False,
                        game_launched=False, deployed=False, workshop_published=False),
    )
    write_json(output / "build-manifest.json", manifest)
    return dict(ok=True, package=str(package), dll=str(dll), sha256=sha256(dll),
                export_count=len(built_exports), manifest=str(output / "build-manifest.json"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("zig", "minhook", "gamecore", "output"):
        parser.add_argument("--" + name, required=True, type=Path)
    args = parser.parse_args()
    # Creating the explicitly selected output directory is the only initial write.
    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=True)
    try:
        print(json.dumps(build(args), indent=2))
        return 0
    except (OSError, ValueError, RuntimeError, struct.error) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
