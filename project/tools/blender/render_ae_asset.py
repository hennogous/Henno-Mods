"""Read a saved Asset Editor AST and render reproducible icon/SV Blender inputs.

Usage: py -3 project/tools/blender/render_ae_asset.py "Civ Supply Chains/Assets/NAME.ast" --L1
Only generated output is written. AE files and authoring blends are never modified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import struct
import tempfile
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
TOOLS = ROOT / "project/tools"
DEFAULT_SDK = Path("C:/Program Files (x86)/Steam/steamapps/common/Sid Meier's Civilization VI SDK Assets")
DEFAULT_BLENDER = Path("C:/Program Files/Blender Foundation/Blender 5.1/blender.exe")
CAMERA_PRESETS = Path(__file__).with_name("ae_render_camera_presets.json")
PRESETS = {
    "icon": {"projection": "PERSP", "elevation": 23.0, "lens": 37.0,
             "distance_span": 1.5, "turn": 0.0, "sun_direction": [-240, -280, 360],
             "sun_energy": 3.0, "sun_angle": 8.0, "world_color": [1, 1, 0.9],
             "world_strength": 0.8, "view_transform": "Standard", "exposure": 0.0},
    "sv": {"projection": "ORTHO", "elevation": 39.351752626264734,
           "ortho_span": 1.70, "turn": 0.0, "sun_direction": [-300, -280, 500],
           "sun_energy": 3.0, "sun_angle": 8.0, "world_color": [0.7, 0.8, 1.0],
           "world_strength": 0.65, "view_transform": "AgX", "exposure": 0.35},
}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stable_png(data):
    """Remove Blender timestamp/path stamps without decoding or changing pixels."""
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("Not a PNG")
    chunks, offset = [data[:8]], 8
    while offset < len(data):
        if offset + 12 > len(data):
            raise ValueError("Truncated PNG chunk")
        length = struct.unpack_from(">I", data, offset)[0]
        end = offset + length + 12
        if end > len(data):
            raise ValueError("Truncated PNG payload")
        if data[offset + 4:offset + 8] not in (b"tEXt", b"zTXt", b"iTXt", b"tIME", b"eXIf"):
            chunks.append(data[offset:end])
        offset = end
    return b"".join(chunks)


def txt(element, path, default=""):
    if element is None:
        return default
    node = element.find(path)
    return node.get("text", node.text or default) if node is not None else default


def read_xml(path):
    # Some Firaxis GEOs use unbound dotted-prefix tags (not XML namespaces).
    # Some native SDK descriptors include a C-string terminator after the XML.
    # Strip terminal padding only; invalid bytes inside the document still fail.
    content = Path(path).read_text(encoding="utf-8-sig").rstrip("\x00\r\n\t ")
    return ET.fromstring(re.sub(r"(<\/?)([\w.]+):", r"\1\2.", content))


def values(element):
    result = {}
    if element is not None:
        for row in element.findall(".//Element"):
            key = txt(row, "m_ParamName")
            if key:
                for field in ("m_ObjectName", "m_EntryName", "m_bValue", "m_fValue", "m_Value"):
                    if row.find(field) is not None:
                        result[key] = txt(row, field)
                        break
    return result


def texture_bindings(element):
    return {txt(row, "m_ParamName"): txt(row, "m_ObjectName")
            for row in element.findall(".//Element")
            if txt(row, "m_eObjectType") == "TEXTURE" and txt(row, "m_ObjectName")}


class Resolver:
    """Local mod overrides first; native resources from SDK dependency inventories."""
    def __init__(self, mod, sdk):
        self.mod, self.sdk = Path(mod).resolve(), Path(sdk).resolve()
        self.index = {}
        self.inputs = {}
        for dep in sorted(self.sdk.glob("*-asset-deps.json")):
            for row in json.loads(dep.read_text(encoding="utf-8-sig")).get("Files", []):
                path = self.sdk / row["Filename"]
                if path.suffix.lower() in (".ast", ".geo", ".fgx", ".mtl", ".tex", ".dds", ".xlp"):
                    self.index.setdefault(path.name.casefold(), set()).add(path)
        for folder in ("Assets", "Geometries", "Materials", "Textures", "XLPs"):
            for path in (self.mod / folder).rglob("*"):
                if path.is_file():
                    self.index.setdefault(path.name.casefold(), set()).add(path)

    def track(self, path):
        path = Path(path).resolve()
        self.inputs[str(path)] = digest(path)
        return path

    def resolve(self, name, extension, near=None):
        basename = Path(name.replace("\\", "/")).name
        if not basename.casefold().endswith(extension):
            basename += extension
        candidates = [p for p in self.index.get(basename.casefold(), ()) if p.is_file()]
        if not candidates:
            raise FileNotFoundError(f"Cannot resolve {name}{extension} in mod/SDK")
        def rank(path):
            shared = len(os.path.commonpath([str(path), str(near)])) if near else 0
            return (0 if path.is_relative_to(self.mod) else 1, -shared)
        candidates.sort(key=lambda p: (rank(p), str(p).casefold()))
        peers = [p for p in candidates if rank(p) == rank(candidates[0])]
        if len(peers) > 1 and len({digest(p) for p in peers}) > 1:
            raise ValueError(f"Ambiguous resource {name}: {peers}")
        return self.track(candidates[0])

    def attached_asset(self, binding, near):
        ident = txt(binding, "m_EntryName")
        hint = txt(binding, "m_XLPPath")
        if hint:
            matches = []
            for xlp in self.index.get(Path(hint.replace("\\", "/")).name.casefold(), ()):
                if not xlp.is_file():
                    continue
                xroot = read_xml(xlp)
                if txt(xroot, "m_PackageName").casefold() != txt(binding, "m_BLPPackage").casefold():
                    continue
                entries = [e for e in xroot.findall("m_Entries/Element")
                           if txt(e, "m_EntryID").casefold() == ident.casefold()]
                if len(entries) > 1:
                    raise ValueError(f"Duplicate {ident} entry in {xlp}")
                if entries:
                    matches.append((xlp, txt(entries[0], "m_ObjectName")))
            if matches:
                # Base/DLC XLPs share filenames; identify the entry before choosing a package.
                matches.sort(key=lambda row: (not row[0].is_relative_to(self.mod), len(row[0].parts), str(row[0])))
                local = [row for row in matches if row[0].is_relative_to(self.mod)]
                chosen = local or matches
                if len({name for _, name in chosen}) != 1:
                    raise ValueError(f"Ambiguous XLP entry {ident}: {chosen}")
                xlp, name = chosen[0]
                self.track(xlp)
                return self.resolve(name, ".ast", xlp)
        return self.resolve(ident, ".ast", near)


class Assembly:
    def __init__(self, resolver, state="Worked"):
        self.r, self.state = resolver, state
        self.assets, self.geometries, self.materials = {}, {}, {}
        self.excluded, self.warnings = [], []

    def material(self, ident, overrides, near, enabled):
        path = self.r.resolve(ident, ".mtl", near)
        root = read_xml(path)
        bindings = texture_bindings(root)
        bindings.update(overrides)
        textures = {}
        for channel, texture in sorted(bindings.items()):
            tex = self.r.resolve(texture, ".tex", path)
            descriptor = read_xml(tex)
            filename = next((txt(e, "m_RelativePath") for e in descriptor.findall("m_DataFiles/Element")
                             if txt(e, "m_ID").casefold() == "dds"), texture + ".dds")
            adjacent = tex.parent / filename
            source = self.r.track(adjacent) if adjacent.is_file() else self.r.resolve(filename, ".dds", tex)
            textures[channel] = {"id": texture, "source": str(source)}
        key = hashlib.sha256(json.dumps([str(path), bindings, enabled], sort_keys=True).encode()).hexdigest()[:16]
        self.materials[key] = {"id": ident, "shader": txt(root, "m_ClassName"),
                               "textures": textures, "emission_enabled": enabled}
        return key

    def asset(self, path, stack=()):
        path = self.r.track(path)
        key = str(path)
        if key in stack:
            raise ValueError("Attachment cycle: " + " -> ".join((*stack, key)))
        if key in self.assets:
            return key
        root = read_xml(path)
        record = {"id": txt(root, "m_Name", path.stem), "source": key, "models": [], "attachments": []}
        overrides = texture_bindings(root.find("m_CookParams")) if root.find("m_CookParams") is not None else {}
        model_names = set()
        for model in root.findall("m_GeometrySet/m_ModelInstances/Element"):
            ident, geo_id = txt(model, "m_Name"), txt(model, "m_GeoName")
            model_names.add(ident)
            state_rows = {}
            for row in model.findall("m_GroupStates/Element"):
                if txt(row, "m_StateName") == self.state:
                    pair = (txt(row, "m_MeshName"), txt(row, "m_GroupName"))
                    if pair in state_rows:
                        raise ValueError(f"Duplicate {self.state} state row: {path}, {pair}")
                    state_rows[pair] = values(row)
            active = {k: v for k, v in state_rows.items() if v.get("Visible", "false").lower() == "true"}
            # Decals are context, not icon/SV subjects. Exclusion uses the actual shader.
            active = {k: v for k, v in active.items() if not self.is_decal(v.get("Material", ""), path)}
            if not active:
                self.excluded.append({"asset": record["id"], "model": ident, "reason": "hidden state or decal"})
                # Retain the geometry for attachment anchor lookup when needed.
                record["models"].append({"id": ident, "geometry": None, "groups": []})
                continue
            geo_path = self.r.resolve(geo_id, ".geo", path)
            geo = read_xml(geo_path)
            filename = next((txt(e, "m_RelativePath") for e in geo.findall("m_DataFiles/Element")
                             if txt(e, "m_ID").casefold() in ("gr2", "fgx")), geo_id + ".fgx")
            adjacent = geo_path.parent / filename
            fgx = self.r.track(adjacent) if adjacent.is_file() else self.r.resolve(filename, ".fgx", geo_path)
            gkey = str(fgx)
            self.geometries[gkey] = {"id": geo_id, "source": gkey}
            groups = []
            for mesh in geo.findall("m_Meshes/Element"):
                for group in mesh.findall("m_Groups/Element"):
                    pair = (txt(mesh, "m_Name"), txt(group, "m_Name"))
                    if pair not in active:
                        continue
                    row = active.pop(pair)
                    material = self.material(row["Material"], overrides, path,
                                             row.get("EmissiveEnabled", "true").lower() == "true")
                    groups.append({"mesh": pair[0], "group": pair[1], "first": int(txt(group, "m_nFirstPrim")),
                                   "count": int(txt(group, "m_nPrims")), "material": material})
            if active:
                raise ValueError(f"AST groups absent from GEO {geo_path}: {sorted(active)}")
            record["models"].append({"id": ident, "geometry": gkey, "groups": groups})
        for point in root.findall("m_BehaviorData/m_behaviorDataSets/m_attachmentPoints/m_Points/Element"):
            binding = next((e for e in point.findall("m_CookParams/m_Values/Element")
                            if txt(e, "m_ParamName") == "Asset"), None)
            if binding is None or not txt(binding, "m_EntryName"):
                continue
            owner = txt(point, "m_ModelInstanceName")
            if owner not in model_names:
                raise ValueError(f"Missing attachment owner {owner}: {path}")
            child = self.asset(self.r.attached_asset(binding, path), (*stack, key))
            position = [float(txt(point, "m_position/" + axis, "0")) for axis in "xyz"]
            rotation = [float(txt(point, "m_orientation/" + axis, "0")) for axis in "xyz"]
            scale = float(txt(point, "m_scale", "1"))
            if scale <= 0:
                raise ValueError(f"Invalid attachment scale: {path}")
            if any(abs(v) > 1e-6 for v in rotation[:2]):
                self.warnings.append(f"{record['id']}/{txt(point, 'm_Name')}: compound X/Y rotation uses inverse CSC export convention; AE visual calibration pending")
            record["attachments"].append({"id": txt(point, "m_Name"), "asset": child, "owner": owner,
                                          "bone": txt(point, "m_BoneName"), "position": position,
                                          "rotation": rotation, "scale": scale, "settings": values(point.find("m_CookParams"))})
        if root.findall("m_BehaviorData/m_behaviorDataSets/m_animationBindings/m_Bindings/Element"):
            self.warnings.append(f"{record['id']}: deterministic bind pose; animation clips are not evaluated")
        self.assets[key] = record
        return key

    def is_decal(self, ident, near):
        if not ident:
            raise ValueError(f"Visible state without material: {near}")
        path = self.r.resolve(ident, ".mtl", near)
        return "decal" in txt(read_xml(path), "m_ClassName").casefold()


def helper(cache):
    libs = TOOLS / "cn6libs"
    source = TOOLS / "blender/ExtractPropFgx.cs"
    files = [source, libs / "CivNexus6.exe", *sorted(libs.glob("*.dll"))]
    fingerprint = hashlib.sha256("".join(digest(p) for p in files).encode()).hexdigest()[:16]
    runtime = cache / "extractor" / fingerprint
    exe = runtime / "ExtractPropFgx.exe"
    if not exe.is_file():
        runtime.mkdir(parents=True, exist_ok=True)
        for path in files[1:]:
            shutil.copy2(path, runtime / path.name)
        csc = Path(os.environ.get("WINDIR", "C:/Windows")) / "Microsoft.NET/Framework64/v4.0.30319/csc.exe"
        refs = ["System.Web.Extensions.dll", *[str(p) for p in libs.glob("Firaxis.*.dll")]]
        result = subprocess.run([str(csc), "/nologo", "/unsafe", "/target:exe", "/platform:x64", "/out:" + str(exe),
                                 *["/reference:" + r for r in refs], str(source)], capture_output=True, text=True)
        if result.returncode:
            raise RuntimeError(result.stdout + result.stderr)
    return exe, fingerprint


def prepare_geometry(assembly, cache, run):
    exe, fingerprint = helper(cache)
    for key, geometry in assembly.geometries.items():
        checksum = digest(key)
        cached = cache / "geometry" / f"{checksum}_{fingerprint}.json"
        cached.parent.mkdir(parents=True, exist_ok=True)
        if not cached.is_file():
            temporary = cached.with_suffix(".tmp")
            result = subprocess.run([str(exe), str(exe.parent), key, str(temporary)],
                                    cwd=exe.parent, capture_output=True, text=True)
            if result.returncode:
                raise RuntimeError(f"FGX extraction failed for {key}:\n{result.stdout}\n{result.stderr}")
            json.loads(temporary.read_text())
            temporary.replace(cached)
        target = run / "geometry" / (checksum + ".json")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(cached, target)
        geometry["extracted"] = str(target)


def publish_images(report, asset, directory):
    """Place stable, distinct 2D input PNGs beside the AST, including cached runs."""
    directory.mkdir(parents=True, exist_ok=True)
    published = {}
    for mode, rendering in report.items():
        outside = rendering.get("outside_frame_objects", [])
        if outside:
            print(f"{mode.upper()} fixed {rendering['camera_class']}: {len(outside)} mesh groups outside frame; camera retained", flush=True)
        source = Path(rendering["image"])
        destination = directory / f"{asset.stem}_{mode.upper() if mode == 'sv' else 'Icon'}_Input.png"
        data = source.read_bytes()
        if not destination.is_file() or destination.read_bytes() != data:
            handle, temporary = tempfile.mkstemp(prefix="." + destination.stem + "_", suffix=".tmp", dir=directory)
            try:
                with os.fdopen(handle, "wb") as stream:
                    stream.write(data)
                os.replace(temporary, destination)
            finally:
                if Path(temporary).exists():
                    Path(temporary).unlink()
        published[mode] = str(destination)
        print(mode.upper() + " PNG", destination, flush=True)
    return published


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("asset", type=Path)
    p.add_argument("--mode", choices=("both", "icon", "sv"), default="both")
    framing = p.add_mutually_exclusive_group(required=True)
    for level in ("L1", "L2", "L3"):
        framing.add_argument("--" + level, dest="camera_class", action="store_const", const=level,
                             help=f"Locked {level} camera and framing, independent of prop layout")
    framing.add_argument("--auto-frame", dest="camera_class", action="store_const", const="auto",
                         help="Explicit legacy bounds-based framing; unsuitable for reusable XCF paths")
    p.add_argument("--output", type=Path, help="Render package/cache root; default Desktop/Codex/asset-renders")
    p.add_argument("--image-output-dir", type=Path, help="Final PNG folder; default is the input AST's folder")
    p.add_argument("--mod-root", type=Path, default=ROOT / "Civ Supply Chains")
    p.add_argument("--sdk", type=Path, default=DEFAULT_SDK)
    p.add_argument("--blender", type=Path, default=DEFAULT_BLENDER)
    p.add_argument("--resolution", type=int, default=1024)
    p.add_argument("--samples", type=int, default=32)
    p.add_argument("--icon-texture", choices=("light", "runtime"), default="light")
    p.add_argument("--force", action="store_true", help="Render again even if the exact outputs are cached")
    p.add_argument("--prepare-only", action="store_true", help="Resolve/extract/validate inputs without rendering")
    args = p.parse_args()
    if args.resolution < 64 or args.samples < 1:
        p.error("Resolution must be >=64 and samples >=1")
    asset = args.asset.resolve()
    image_directory = (args.image_output_dir or asset.parent).resolve()
    output = (args.output or Path.home() / "Desktop/Codex/asset-renders").resolve()
    # Output must never live in a source mod or SDK directory.
    if output.is_relative_to(args.mod_root.resolve()) or output.is_relative_to(args.sdk.resolve()):
        p.error("Output must be outside the source mod and SDK")
    output.mkdir(parents=True, exist_ok=True)
    resolver = Resolver(args.mod_root, args.sdk)
    assembly = Assembly(resolver)
    root = assembly.asset(asset)
    modes = ["icon", "sv"] if args.mode == "both" else [args.mode]
    if "icon" in modes and args.icon_texture == "light":
        switched = False
        for material in assembly.materials.values():
            base = material["textures"].get("BaseColor")
            if base and re.fullmatch(r"CSC_Atlas_B_[A-Z]+(?:_2)?", base["id"]):
                alternate = base["id"] if base["id"].endswith("_2") else base["id"] + "_2"
                tex = resolver.resolve(alternate, ".tex", asset)
                filename = txt(read_xml(tex), "m_DataFiles/Element/m_RelativePath", alternate + ".dds")
                source = tex.parent / filename
                base["icon_override"] = str(resolver.track(source) if source.is_file() else resolver.resolve(filename, ".dds", tex))
                base["icon_override_id"] = alternate
                switched = True
        if not switched:
            raise ValueError("No CSC Quarter building atlas to switch; use --icon-texture runtime explicitly")
    blender_version = subprocess.run([str(args.blender), "--version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    # Code, dependencies, render settings and all consumed sources invalidate reuse.
    scripts = [Path(__file__), TOOLS / "blender/ae_asset_render_blender.py", TOOLS / "blender/ExtractPropFgx.cs", CAMERA_PRESETS]
    settings = {"modes": modes, "presets": PRESETS, "resolution": args.resolution, "samples": args.samples,
                "icon_texture": args.icon_texture, "blender": blender_version, "state": "Worked", "seed": 0,
                "render_emission_enabled": False}
    settings["camera_class"] = args.camera_class
    if args.camera_class != "auto":
        settings["fixed_camera"] = json.loads(CAMERA_PRESETS.read_text())["classes"][args.camera_class]
    settings["extractor_runtime"] = helper(output / "_cache")[1]
    signature = {"inputs": resolver.inputs, "settings": settings, "tools": {str(x): digest(x) for x in scripts}}
    fingerprint = hashlib.sha256(json.dumps(signature, sort_keys=True).encode()).hexdigest()
    run = output / asset.stem / fingerprint[:16]
    run.mkdir(parents=True, exist_ok=True)
    manifest = run / "manifest.json"
    if manifest.is_file() and not args.force and not args.prepare_only:
        previous = json.loads(manifest.read_text())
        if previous.get("status") == "complete" and all(Path(path).is_file() and digest(path) == sha
                                                       for path, sha in previous.get("outputs", {}).items()):
            previous["published_images"] = publish_images(previous["report"], asset, image_directory)
            manifest.write_text(json.dumps(previous, indent=2))
            print("CACHED", manifest, flush=True)
            return
    prepare_geometry(assembly, output / "_cache", run)
    job = {"root": root, "assets": assembly.assets, "geometries": assembly.geometries,
           "materials": assembly.materials, "excluded": assembly.excluded, "warnings": assembly.warnings,
           "settings": settings, "output": str(run), "fingerprint": fingerprint, "signature": signature}
    jobfile = run / "job.json"
    jobfile.write_text(json.dumps(job, indent=2))
    print("PREPARED", len(assembly.assets), "assets,", len(assembly.geometries), "geometries,", manifest, flush=True)
    if args.prepare_only:
        return
    logfile = run / "blender.log"
    with logfile.open("w", encoding="utf-8") as log:
        result = subprocess.run([str(args.blender), "--background", "--factory-startup", "--threads", "4",
                                 "--python-exit-code", "1", "--python", str(scripts[1]), "--", str(jobfile)],
                                stdout=log, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f"Blender failed ({result.returncode}); see {logfile}\n" + logfile.read_text(errors="replace")[-3500:])
    report = json.loads((run / "render-report.json").read_text())
    # Detect mid-run editing; a render must describe one coherent saved revision.
    changed = [path for path, sha in resolver.inputs.items() if digest(path) != sha]
    if changed:
        raise RuntimeError("Sources changed while rendering: " + ", ".join(changed))
    products = [f for f in run.rglob("*") if f.is_file() and f.suffix in (".png", ".exr", ".blend")]
    for product in products:
        if product.suffix == ".png":
            product.write_bytes(stable_png(product.read_bytes()))
    published = publish_images(report, asset, image_directory)
    manifest.write_text(json.dumps({"status": "complete", "fingerprint": fingerprint, **signature,
                                    "report": report, "published_images": published,
                                    "outputs": {str(f): digest(f) for f in products}}, indent=2))
    print("COMPLETE", manifest, flush=True)


if __name__ == "__main__":
    main()
