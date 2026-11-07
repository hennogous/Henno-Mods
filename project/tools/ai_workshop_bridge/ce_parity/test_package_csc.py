"""Exercise isolated CSC snapshots without touching any installed mod."""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from package_csc import BAKERS_ACTIONS, ORIGINAL_ID, OVERLAYS, TEST_ID, build, digest, inventory


class IsolatedCSC(unittest.TestCase):
    def inputs(self, directory):
        installed, source = directory / 'reference', directory / 'reviewed-source'
        installed.mkdir()
        (installed / 'CSC.modinfo').write_text(
            '<Mod id="' + ORIGINAL_ID + '"><Properties><Name>Human CSC</Name>'
            '</Properties></Mod>', encoding='utf-8')
        for name in OVERLAYS:
            for root, text in ((installed, 'installed'), (source, 'reviewed')):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text + ':' + name, encoding='utf-8')
        (installed / 'retained-art.bin').write_bytes(b'asset fixture')
        return installed, source

    def test_snapshot_reidentifies_only_copy_and_pins_reviewed_overlays(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            installed, source = self.inputs(directory)
            before = inventory(installed)
            output = directory / 'package'
            receipt = build(installed, source, output)
            self.assertEqual(inventory(installed), before)
            self.assertEqual(ET.parse(installed / 'CSC.modinfo').getroot().get('id'), ORIGINAL_ID)
            self.assertEqual(ET.parse(output / 'CSC.modinfo').getroot().get('id'), TEST_ID)
            self.assertEqual((output / 'retained-art.bin').read_bytes(), b'asset fixture')
            for name in OVERLAYS:
                self.assertEqual(digest(output / name), digest(source / name))
                self.assertEqual(receipt['overlays'][name], digest(source / name))
            saved = json.loads((directory / 'package-receipt.json').read_text())
            self.assertEqual(saved, receipt)
            self.assertFalse(saved['installed'])
            self.assertFalse(saved['native_validated'])

    def test_original_id_and_input_nested_output_are_rejected_before_copy(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            installed, source = self.inputs(directory)
            for output, identity in ((directory / 'bad', ORIGINAL_ID),
                                     (installed / 'nested', TEST_ID),
                                     (source / 'nested', TEST_ID)):
                with self.assertRaises(ValueError):
                    build(installed, source, output, mod_id=identity)
                self.assertFalse(output.exists())

    def test_bakers_package_has_canonical_actions_and_a_separate_dependency(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            installed, source = self.inputs(directory)
            manifest = installed / 'CSC.modinfo'
            manifest.write_text(
                f'<Mod id="{ORIGINAL_ID}"><Properties><Name>Human CSC</Name></Properties>'
                '<Dependencies/><InGameActions><DoNothing id="CSC_AI_BakersGameplay"/>'
                '</InGameActions><Files/></Mod>', encoding='utf-8')
            actions = directory / 'actions.json'
            definitions = []
            for action in sorted(BAKERS_ACTIONS):
                script = f'Lua_UI/{action}.lua'
                (source / script).write_text(action, encoding='utf-8')
                definitions.append(dict(id=action, type='AddGameplayScripts' if action == 'CSC_AI_BakersGameplay'
                                        else 'ImportFiles', properties={'LoadOrder': '490'}, files=[script]))
            actions.write_text(json.dumps({'blocks': {'inGameActions': definitions}}), encoding='utf-8')
            ce = 'd0f3a2ab-4fa6-4a7a-bf9b-b82a66fe2a16'
            out = directory / 'package'
            receipt = build(installed, source, out, ce_dependency=ce, bakers_actions=actions)
            root = ET.parse(out / manifest.name).getroot()
            self.assertEqual([item.get('id') for item in root.findall('Dependencies/Mod')], [ce])
            self.assertEqual(len(root.findall('InGameActions/AddGameplayScripts')), 1)
            self.assertEqual({item.get('id') for item in root.find('InGameActions')}, BAKERS_ACTIONS)
            self.assertEqual({item.text for item in root.findall('Files/File')},
                             {item['files'][0] for item in definitions})
            self.assertTrue(receipt['main_publisher'])
            self.assertEqual(receipt['action_sha256'], digest(actions))
