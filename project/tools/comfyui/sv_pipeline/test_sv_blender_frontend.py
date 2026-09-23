import unittest
from pathlib import Path
import tempfile

import numpy as np
from PIL import Image

from sv_blender_frontend import (
    gimp_linear_contrast,
    grade_final_visible,
    grade_generated_for_sam,
    prepare_preshadow_handoff,
)
from sv_postprocess import PostProcessConfig, RevealedPostProcessConfig, process_from_preshadow


class BlenderFrontendTests(unittest.TestCase):
    def test_grade_is_deterministic_and_preserves_alpha(self):
        arr = np.zeros((32, 32, 4), dtype=np.uint8)
        arr[8:24, 6:26, :3] = (75, 90, 120)
        arr[8:24, 6:26, 3] = 220
        source = Image.fromarray(arr, "RGBA")
        first = np.asarray(grade_generated_for_sam(source))
        second = np.asarray(grade_generated_for_sam(source))
        self.assertTrue(np.array_equal(first, second))
        self.assertTrue(np.array_equal(first[:, :, 3], arr[:, :, 3]))
        self.assertGreater(first[8:24, 6:26, :3].mean(), arr[8:24, 6:26, :3].mean())

    def test_final_grade_is_deterministic(self):
        source = Image.new("RGBA", (16, 16), (80, 105, 130, 255))
        self.assertEqual(grade_final_visible(source).tobytes(), grade_final_visible(source).tobytes())

    def test_linear_contrast_is_deterministic_and_preserves_alpha(self):
        arr = np.zeros((1, 5, 4), dtype=np.uint8)
        arr[0, :, :3] = np.array([0, 64, 128, 192, 240], dtype=np.uint8)[:, None]
        arr[0, :, 3] = np.array([1, 64, 128, 192, 255], dtype=np.uint8)
        source = Image.fromarray(arr, "RGBA")
        first = np.asarray(gimp_linear_contrast(source, -3))
        second = np.asarray(gimp_linear_contrast(source, -3))
        self.assertTrue(np.array_equal(first, second))
        self.assertTrue(np.array_equal(first[0, :, 3], arr[0, :, 3]))
        self.assertGreater(first[0, 0, 0], 0)
        self.assertLess(first[0, 0, 0], 53)

    def test_handoff_desaturates_and_preserves_alpha(self):
        source = Image.new("RGBA", (16, 16), (220, 40, 120, 177))
        graded_only = np.asarray(grade_final_visible(source), dtype=np.float32)
        result = np.asarray(prepare_preshadow_handoff(source), dtype=np.float32)
        graded_range = graded_only[:, :, :3].max(axis=2) - graded_only[:, :, :3].min(axis=2)
        result_range = result[:, :, :3].max(axis=2) - result[:, :, :3].min(axis=2)
        self.assertLess(result_range.mean(), graded_range.mean())
        self.assertTrue(np.all(result[:, :, 3] == 177))

    def test_preshadow_finalization_writes_six_state_variants(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "Sample_Visible_PreShadow.png"
            Image.new("RGBA", (256, 256), (120, 80, 40, 255)).save(source)
            outputs = process_from_preshadow(
                str(source),
                base_config=PostProcessConfig(enable_base_shadow=False),
                revealed_config=RevealedPostProcessConfig(shadow_path=None),
            )
            expected = {
                "Sample_Visible.png",
                "Sample_Visible_UnderConstruction.png",
                "Sample_Visible_Pillaged.png",
                "Sample_Revealed.png",
                "Sample_Revealed_UnderConstruction.png",
                "Sample_Revealed_Pillaged.png",
            }
            self.assertEqual({Path(output).name for output in outputs}, expected)
            self.assertTrue(all(Path(output).is_file() for output in outputs))


if __name__ == "__main__":
    unittest.main()
