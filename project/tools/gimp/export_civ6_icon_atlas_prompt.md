Write a GIMP Python script for the currently open XCF.

Quarter source files use a 4x4 grid. The full 1024x1024 atlas represents IconSize 256.

`CSC_Resources.xcf` uses a 2x2 grid on a 512x512 canvas. Export the visible resource art at 256, 64, 50, 38, 32, and 22 px per slot. Export the separate top-level `FOW` artwork at 256 and 64 px per slot, with `_FOW` after the size in the filename. Keep that layer hidden in the normal atlas. Both resource sheets at IconSize 256 have ten levels, from 512x512 to 1x1. Use the existing sharpening settings for the shared sizes and a radius of 0.8, amount 0.5, and threshold 0 for 64 px slots.

Do not modify the original image. Work only on duplicate images and close/discard them when done.

Derive the export prefix from the current XCF filename by removing the suffix `_Icons.xcf`.
Example: `CSC_BAKERS_Icons.xcf` exports files named `CSC_BAKERS_256.dds`, `CSC_BAKERS_128.dds`, etc.

Create a flattened master duplicate by merging all visible layers. The layer named `Background` should be included as the bottom/background layer. Hidden layers other than `Background` should not be included. The original XCF must remain unmerged.

For Quarter art, export the following DDS files from the flattened master, scaling directly from the 1024x1024 master for each output size:

| IconSize | Atlas size | Output filename | Sharpening |
|---:|---:|---|---|
| 256 | 1024x1024 | `PREFIX_256.dds` | none |
| 128 | 512x512 | `PREFIX_128.dds` | Unsharp Mask radius=1.0, amount=0.5, threshold=0 |
| 80 | 320x320 | `PREFIX_80.dds` | Unsharp Mask radius=1.2, amount=0.5, threshold=0 |
| 70 | 280x280 | `PREFIX_70.dds` | Unsharp Mask radius=1.3, amount=0.5, threshold=0 |
| 50 | 200x200 | `PREFIX_50.dds` | Unsharp Mask radius=1.5, amount=0.5, threshold=0 |
| 38 | 152x152 | `PREFIX_38.dds` | Unsharp Mask radius=1.6, amount=0.5, threshold=0 |
| 32 | 128x128 | `PREFIX_32.dds` | Unsharp Mask radius=1.7, amount=0.5, threshold=0 |
| 22 | 88x88 | `PREFIX_22.dds` | Unsharp Mask radius=1.8, amount=0.5, threshold=0 |

Export DDS files into the same folder as the source XCF.

Use the DDS settings that have been verified to work for these Civ VI icon atlases in GIMP:

- Compression: None
- Format: RGBA8
- Save type: All visible layers
- Flip image vertically on export: unchecked
- Mipmaps: Generate mipmaps with the Box filter for `PREFIX_256.dds` and `PREFIX_256_FOW.dds`. Use No mipmaps for all smaller atlases.
- Perceptual error metric, gamma correction, sRGB, and alpha coverage options: disabled/unchecked
