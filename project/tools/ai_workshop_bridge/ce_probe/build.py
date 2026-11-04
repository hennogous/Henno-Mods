"""Create a CE-dependent, Lua-only capability probe; does not install or run it."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import xml.etree.ElementTree as ET

HERE = Path(__file__).resolve().parent
MOD_ID = "d0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a05"
CE_ID = "3351473b-0746-417a-a618-2b66a04d8f3d"
PARSER_SOURCE = HERE.parent / "build.py"


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(text.encode("utf-8"))


def build(gamecore: Path, output: Path) -> dict:
    spec = importlib.util.spec_from_file_location("csc_bridge_pe_parser", PARSER_SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    actual_sha = sha(gamecore)
    if actual_sha != module.GAMECORE_SHA256:
        raise ValueError("GameCore does not match the qualified pristine SHA-256")
    pe = module.PE(gamecore)
    pins = [dict(path=str(path), sha256=sha(path)) for path in
            [Path(__file__).resolve(), HERE / "gameplay.lua", PARSER_SOURCE]]
    package = output / "package"
    target = ["-- Generated from the SHA-qualified pristine GameCore.",
              "CSC_CE_PROBE_TARGET = {", f'  sha256 = "{actual_sha}",',
              f"  timestamp = {pe.timestamp},", f"  image_size = {pe.image_size},",
              "  fingerprints = {"]
    for name, rva in [("GetPlayer", 0x63d080), ("InitializeAiSystems", 0x2f9350),
                      ("CityManagerDoTurnActivate", 0x3d9130)]:
        raw = pe.slice(pe.offset(rva, 32), 32)
        target.append(f'    {{ name = "{name}", rva = {rva}, bytes = {{ ' +
                      ", ".join(str(x) for x in raw) + " } },")
    target += ["  }", "}", ""]
    write(package / "Lua" / "CSC_CE_Probe_Target.lua", "\n".join(target))
    write(package / "Lua" / "CSC_CE_Probe.lua", (HERE / "gameplay.lua").read_text(encoding="utf-8"))
    mod = ET.Element("Mod", id=MOD_ID, version="1")
    props = ET.SubElement(mod, "Properties")
    for key, value in {
        "Name": "CSC CE memory capability probe (read only)",
        "Description": "Developer diagnostic. Requires the existing Community Extension; contains no DLL or native hook. Records bounded cache observations in Lua.log. Not a tuning feature.",
        "Authors": "Henno", "CompatibleVersions": "2.0", "AffectsSavedGames": "0",
    }.items():
        ET.SubElement(props, key).text = value
    dependencies = ET.SubElement(mod, "Dependencies")
    ET.SubElement(dependencies, "Mod", id=CE_ID, title="Community Extension")
    ET.SubElement(dependencies, "Mod", id="4873eb62-8ccc-4574-b784-dda455e74e68",
                  title="Expansion: Gathering Storm")
    actions = ET.SubElement(mod, "InGameActions")
    imports = ET.SubElement(actions, "ImportFiles", id="CSC_CE_Probe_Target")
    ET.SubElement(imports, "File").text = "Lua/CSC_CE_Probe_Target.lua"
    script = ET.SubElement(actions, "AddGameplayScripts", id="CSC_CE_Probe")
    ET.SubElement(ET.SubElement(script, "Properties"), "LoadOrder").text = "999990"
    ET.SubElement(script, "File").text = "Lua/CSC_CE_Probe.lua"
    files = ET.SubElement(mod, "Files")
    for path in ["Lua/CSC_CE_Probe.lua", "Lua/CSC_CE_Probe_Target.lua"]:
        ET.SubElement(files, "File").text = path
    ET.indent(mod, space="  ")
    write(package / "CSC_CE_Probe.modinfo", '<?xml version="1.0" encoding="utf-8"?>\n' +
          ET.tostring(mod, encoding="unicode") + "\n")
    manifest = dict(schema="csc-ce-probe-package-v1", mod_id=MOD_ID,
                    ce_dependency=CE_ID, built_at=dt.datetime.now(dt.timezone.utc).isoformat(),
                    source_pins=pins, gamecore_sha256=actual_sha,
                    expected_timestamp=pe.timestamp, expected_image_size=pe.image_size,
                    files=[dict(path=p.relative_to(package).as_posix(), sha256=sha(p))
                           for p in sorted(package.rglob("*")) if p.is_file()],
                    guarantees=dict(no_native_binary=True, no_memory_writes=True,
                                    no_native_callbacks=True),
                    status=dict(deployed=False, game_run=False, timing_qualified=False,
                                exclusive_cache_window_proved=False))
    write(output / "manifest.json", json.dumps(manifest, indent=2) + "\n")
    return dict(ok=True, package=str(package), manifest=str(output / "manifest.json"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gamecore", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output == HERE or output.is_relative_to(HERE):
        parser.error("Output must be outside the source directory")
    print(json.dumps(build(args.gamecore.resolve(strict=True), output), indent=2))
