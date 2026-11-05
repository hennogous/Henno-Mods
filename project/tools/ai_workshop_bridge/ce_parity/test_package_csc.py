"""Exercise isolated CSC snapshots without touching any installed mod."""
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from package_csc import ORIGINAL_ID, OVERLAYS, TEST_ID, build, digest, inventory


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
