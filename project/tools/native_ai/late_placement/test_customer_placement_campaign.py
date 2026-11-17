"""Retirement preserves unique outputs and refuses live-session archives."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from customer_placement_campaign import retire_duplicates
from driver import manifest


class ClosedPackageRetirement(unittest.TestCase):
    def test_archive_cannot_be_its_own_keeper(self):
        with TemporaryDirectory(dir=Path(__file__).parent)as directory:
            out=Path(directory).resolve();archive=out/'CSC Bakers Development Mod';archive.mkdir()
            (archive/'policy.lua').write_text('only copy')
            (out/'packages.json').write_text(json.dumps({str(archive):dict(
                install=str(out/'Mods'/archive.name),files=manifest(archive))}))
            (out/'session-closed.json').write_text(json.dumps(dict(verified=True)))
            with self.assertRaisesRegex(RuntimeError,'own retained source'):retire_duplicates(out)
            self.assertTrue((archive/'policy.lua').exists())

    def test_only_identical_closed_copy_is_removed(self):
        with TemporaryDirectory(dir=Path(__file__).parent)as directory:
            base=Path(directory).resolve();out=base/'run';out.mkdir();keeper=base/'frozen';keeper.mkdir()
            archive=out/'CSC Bakers Development Mod';archive.mkdir()
            (keeper/'policy.lua').write_text('same');(archive/'policy.lua').write_text('same')
            files=manifest(keeper)
            (out/'packages.json').write_text(json.dumps({str(keeper):dict(install=str(base/'Mods'/archive.name),files=files)}))
            (out/'session-closed.json').write_text(json.dumps(dict(verified=False)))
            with self.assertRaises(RuntimeError):retire_duplicates(out)
            self.assertTrue(archive.exists())
            (out/'session-closed.json').write_text(json.dumps(dict(verified=True)))
            (archive/'unique.log').write_text('keep')
            retire_duplicates(out);self.assertTrue(archive.exists())
            (archive/'unique.log').unlink()
            retire_duplicates(out);self.assertFalse(archive.exists());self.assertTrue(keeper.exists())
            self.assertEqual(sum(len(json.loads(p.read_text())['retired'])for p in out.glob('storage-retirement*.json')),1)


if __name__=='__main__':unittest.main()
