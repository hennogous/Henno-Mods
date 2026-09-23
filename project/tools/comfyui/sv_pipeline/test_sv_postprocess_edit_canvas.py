"""Regression checks for an exported, already-composed SV editing canvas."""

from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image

from sv_postprocess import (
    PostProcessConfig,
    RevealedPostProcessConfig,
    is_canonical_sv_edit_source,
    process_from_preshadow,
)


class ExportedCanvasTests(unittest.TestCase):
    def test_canonical_export_does_not_need_preshadow_suffix(self):
        self.assertTrue(is_canonical_sv_edit_source("CSC_TAILORS_SV_Tailor"))
        self.assertFalse(is_canonical_sv_edit_source("CSC_TAILORS_SV_Tailor_Input"))
        self.assertFalse(is_canonical_sv_edit_source("CSC_TAILORS_SV_Tailor_Visible"))
        self.assertFalse(is_canonical_sv_edit_source("CSC_TAILORS_SV_Tailor_Visible_PreShadow"))

    def test_full_800_pixel_canvas_keeps_proportional_composition(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "CSC_TAILORS_SV_Tailor.png"
            canvas = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
            canvas.paste((180, 90, 120, 255), (150, 150, 650, 650))
            canvas.save(source)
            outputs = process_from_preshadow(
                str(source),
                base_config=PostProcessConfig(enable_base_shadow=False),
                revealed_config=RevealedPostProcessConfig(shadow_path=None),
                state_overlays=[],
                preplaced_canvas=True,
            )
            visible = Image.open(Path(directory) / "CSC_TAILORS_SV_Tailor_Visible.png")
            self.assertEqual(visible.size, (256, 256))
            # Ignore the faint Lanczos alpha fringe beyond the painted square.
            solid_alpha = visible.getchannel("A").point(lambda value: 255 if value > 16 else 0)
            left, top, right, bottom = solid_alpha.getbbox()
            self.assertLessEqual(abs(left - 48), 2)
            self.assertLessEqual(abs(top - 48), 2)
            self.assertLessEqual(abs((right - left) - 160), 4)
            self.assertLessEqual(abs((bottom - top) - 160), 4)
            self.assertIn(str(Path(directory) / "CSC_TAILORS_SV_Tailor_Revealed.png"), outputs)

    def test_cli_auto_routes_unsuffixed_export(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "CSC_TAILORS_SV_Tailor.png"
            canvas = Image.new("RGBA", (800, 800), (0, 0, 0, 0))
            canvas.paste((180, 90, 120, 255), (150, 150, 650, 650))
            canvas.save(source)
            result = subprocess.run(
                [sys.executable, str(Path(__file__).with_name("sv_postprocess.py")),
                 str(source), "--no-base-shadow", "--revealed-shadow-path", ""],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            visible = Image.open(Path(directory) / "CSC_TAILORS_SV_Tailor_Visible.png")
            solid_alpha = visible.getchannel("A").point(lambda value: 255 if value > 16 else 0)
            left, top, right, bottom = solid_alpha.getbbox()
            self.assertLessEqual(abs(left - 48), 2)
            self.assertLessEqual(abs((right - left) - 160), 4)


if __name__ == "__main__":
    unittest.main()
