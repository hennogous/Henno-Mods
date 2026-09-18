import unittest

import numpy as np
from PIL import Image

from sv_blender_frontend import (
    gimp_linear_contrast,
    grade_final_visible,
    grade_generated_for_sam,
    prepare_preshadow_handoff,
)
from sv_postprocess import PostProcessConfig, resize_to_canvas


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

    def test_subject_trim_fits_real_sprite_not_transparent_canvas(self):
        source = Image.new("RGBA", (100, 100), (0, 0, 0, 0))
        source.paste((120, 80, 40, 255), (20, 30, 60, 50))
        config = PostProcessConfig(
            canvas_size=100,
            sprite_size=50,
            trim_to_subject=True,
            enable_base_shadow=False,
        )
        result = resize_to_canvas(source, config)
        self.assertEqual(result.getchannel("A").getbbox()[2] - result.getchannel("A").getbbox()[0], 50)
        self.assertEqual(result.getchannel("A").getbbox()[3] - result.getchannel("A").getbbox()[1], 25)


if __name__ == "__main__":
    unittest.main()
