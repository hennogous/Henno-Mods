"""Resolver/assembly regressions: exercise source boundaries without Blender."""
import json
from pathlib import Path
import tempfile
import struct
import zlib
import unittest
import xml.etree.ElementTree as ET

from render_ae_asset import Assembly, Resolver, stable_png


class PngTests(unittest.TestCase):
    def test_strip_volatile_metadata_preserves_image_and_color_chunks(self):
        def chunk(kind, data):
            return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
        header = b"\x89PNG\r\n\x1a\n"
        fixed = [chunk(b"IHDR", b"header"), chunk(b"sRGB", b"\x00"),
                 chunk(b"IDAT", b"identical-pixel-stream"), chunk(b"IEND", b"")]
        first = header + fixed[0] + chunk(b"tEXt", b"Date\x00first") + b"".join(fixed[1:])
        second = header + fixed[0] + chunk(b"tEXt", b"Date\x00second") + b"".join(fixed[1:])
        self.assertEqual(stable_png(first), stable_png(second))
        self.assertEqual(stable_png(first), header + b"".join(fixed))

    def test_truncated_png_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "Truncated"):
            stable_png(b"\x89PNG\r\n\x1a\n" + b"\x00\x00\x00\x10IDAT")


class AssemblyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.mod, self.sdk = self.root / "Mod", self.root / "SDK"
        self.sdk.mkdir()
        for folder in ("Assets", "Geometries", "Materials", "Textures", "XLPs"):
            (self.mod / folder).mkdir(parents=True)
        (self.mod / "Materials/Mat.mtl").write_text('<Material><m_ClassName text="Landmark"/></Material>')
        (self.mod / "Materials/Decal.mtl").write_text('<Material><m_ClassName text="DecalMaterial"/></Material>')

    def asset(self, name, material="Mat", visible=True, attachment=None, overrides=None):
        root = ET.Element("Asset")
        ET.SubElement(root, "m_Name", text=name)
        models = ET.SubElement(ET.SubElement(root, "m_GeometrySet"), "m_ModelInstances")
        model = ET.SubElement(models, "Element")
        ET.SubElement(model, "m_Name", text=name)
        ET.SubElement(model, "m_GeoName", text=name)
        states = ET.SubElement(model, "m_GroupStates")
        for state, flag in (("Worked", visible), ("Pillaged", False)):
            row = ET.SubElement(states, "Element")
            for key, value in (("m_StateName", state), ("m_MeshName", "Mesh"), ("m_GroupName", "Group")):
                ET.SubElement(row, key, text=value)
            vals = ET.SubElement(ET.SubElement(row, "m_Values"), "m_Values")
            for key, field, value in (("Material", "m_ObjectName", material), ("Visible", "m_bValue", str(flag).lower())):
                item = ET.SubElement(vals, "Element")
                ET.SubElement(item, "m_ParamName", text=key)
                ET.SubElement(item, field, text=value)
        if overrides:
            vals = ET.SubElement(ET.SubElement(root, "m_CookParams"), "m_Values")
            for key, value in overrides.items():
                item = ET.SubElement(vals, "Element")
                ET.SubElement(item, "m_ParamName", text=key)
                ET.SubElement(item, "m_eObjectType", text="TEXTURE")
                ET.SubElement(item, "m_ObjectName", text=value)
        if attachment:
            points = ET.SubElement(ET.SubElement(ET.SubElement(ET.SubElement(root, "m_BehaviorData"),
                                   "m_behaviorDataSets"), "m_attachmentPoints"), "m_Points")
            point = ET.SubElement(points, "Element")
            for field, value in (("m_Name", "PlacedProp"), ("m_ModelInstanceName", name), ("m_BoneName", name)):
                ET.SubElement(point, field, text=value)
            ET.SubElement(point, "m_scale").text = "0.75"
            for field, data in (("m_position", [1, 2, 3]), ("m_orientation", [0, 0, -0.4])):
                node = ET.SubElement(point, field)
                for axis, value in zip("xyz", data):
                    ET.SubElement(node, axis).text = str(value)
            vals = ET.SubElement(ET.SubElement(point, "m_CookParams"), "m_Values")
            bind = ET.SubElement(vals, "Element")
            ET.SubElement(bind, "m_ParamName", text="Asset")
            ET.SubElement(bind, "m_EntryName", text=attachment)
        path = self.mod / "Assets" / (name + ".ast")
        ET.ElementTree(root).write(path)
        (self.mod / "Geometries" / (name + ".fgx")).write_bytes(b"fixture")
        (self.mod / "Geometries" / (name + ".geo")).write_text(
            '<Geo><m_Meshes><Element><m_Name text="Mesh"/><m_Groups><Element><m_Name text="Group"/>'
            '<m_nFirstPrim>0</m_nFirstPrim><m_nPrims>1</m_nPrims></Element></m_Groups></Element></m_Meshes></Geo>')
        return path

    def resolver(self):
        return Resolver(self.mod, self.sdk)

    def test_saved_placements_are_read_without_modifying_sources(self):
        self.asset("Prop")
        path = self.asset("Building", attachment="Prop")
        original = path.read_bytes()
        assembly = Assembly(self.resolver())
        key = assembly.asset(path)
        attach = assembly.assets[key]["attachments"][0]
        self.assertEqual(attach["position"], [1, 2, 3])
        self.assertEqual(attach["rotation"], [0, 0, -0.4])
        self.assertEqual(attach["scale"], 0.75)
        self.assertEqual(path.read_bytes(), original)

    def test_hidden_state_and_decals_do_not_consume_geometry(self):
        assembly = Assembly(self.resolver())
        # Build sources before creating the resolver's file inventory.
        hidden = self.asset("Hidden", visible=False)
        decal = self.asset("Paving", material="Decal")
        assembly = Assembly(self.resolver())
        assembly.asset(hidden)
        assembly.asset(decal)
        self.assertEqual(assembly.geometries, {})
        self.assertEqual(len(assembly.excluded), 2)

    def test_cycle_fails_explicitly(self):
        self.asset("A", attachment="B")
        self.asset("B", attachment="A")
        with self.assertRaisesRegex(ValueError, "Attachment cycle"):
            Assembly(self.resolver()).asset(self.mod / "Assets/A.ast")

    def test_missing_attachment_owner_fails(self):
        self.asset("Prop")
        path = self.asset("Building", attachment="Prop")
        root = ET.parse(path)
        root.find(".//m_ModelInstanceName").set("text", "MissingOwner")
        root.write(path)
        with self.assertRaisesRegex(ValueError, "Missing attachment owner"):
            Assembly(self.resolver()).asset(path)

    def test_missing_visible_geo_group_fails(self):
        path = self.asset("Building")
        geo = self.mod / "Geometries/Building.geo"
        geo.write_text(geo.read_text().replace('text="Group"', 'text="Other"'))
        with self.assertRaisesRegex(ValueError, "AST groups absent"):
            Assembly(self.resolver()).asset(path)

    def test_duplicate_state_row_fails(self):
        path = self.asset("Building")
        root = ET.parse(path)
        states = root.find(".//m_GroupStates")
        states.append(ET.fromstring(ET.tostring(states[0])))
        root.write(path)
        with self.assertRaisesRegex(ValueError, "Duplicate Worked"):
            Assembly(self.resolver()).asset(path)

    def test_xlp_alias_and_shared_native_filename(self):
        prop = self.asset("ActualProp")
        native = self.sdk / "Civ6/pantry/XLPs/tilebases.xlp"
        dlc = self.sdk / "Civ6/DLC/Expansion1/pantry/XLPs/Tilebases.xlp"
        for path, entry in ((native, "WantedEntry"), (dlc, "OtherEntry")):
            path.parent.mkdir(parents=True)
            path.write_text('<XLP><m_PackageName text="Landmarks/Tilebases"/><m_Entries><Element>'
                            f'<m_EntryID text="{entry}"/><m_ObjectName text="ActualProp"/></Element></m_Entries></XLP>')
        (self.sdk / "civ6-asset-deps.json").write_text(json.dumps({"Files": [
            {"Filename": str(p.relative_to(self.sdk))} for p in (native, dlc)]}))
        binding = ET.fromstring('<Element><m_EntryName text="WantedEntry"/><m_XLPPath text="tilebases.xlp"/>'
                                '<m_BLPPackage text="landmarks/tilebases"/></Element>')
        resolver = self.resolver()
        self.assertEqual(resolver.attached_asset(binding, self.mod), prop)
        self.assertIn(str(native.resolve()), resolver.inputs)

    def test_asset_texture_override_wins_material_binding(self):
        for name in ("MatBase", "AssetBase"):
            (self.mod / "Textures" / (name + ".dds")).write_bytes(name.encode())
            (self.mod / "Textures" / (name + ".tex")).write_text(
                f'<Tex><m_DataFiles><Element><m_ID text="DDS"/><m_RelativePath text="{name}.dds"/></Element></m_DataFiles></Tex>')
        (self.mod / "Materials/Mat.mtl").write_text('<Material><m_ClassName text="Landmark"/><m_CookParams><m_Values>'
            '<Element><m_ParamName text="BaseColor"/><m_ObjectName text="MatBase"/><m_eObjectType text="TEXTURE"/>'
            '</Element></m_Values></m_CookParams></Material>')
        path = self.asset("Building", overrides={"BaseColor": "AssetBase"})
        assembly = Assembly(self.resolver())
        assembly.asset(path)
        self.assertEqual(next(iter(assembly.materials.values()))["textures"]["BaseColor"]["id"], "AssetBase")


if __name__ == "__main__":
    unittest.main()
