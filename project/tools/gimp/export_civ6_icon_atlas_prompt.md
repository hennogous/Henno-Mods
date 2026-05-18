Write a GIMP Python script for the currently open XCF.

The source file is a 4x4 Civ VI icon atlas. The original full atlas is 1024x1024, representing IconSize 256.

Do not modify the original image. Work only on duplicate images and close/discard them when done.

Derive the export prefix from the current XCF filename by removing the suffix `_Icons.xcf`.
Example: `CSC_BAKERS_Icons.xcf` exports files named `CSC_BAKERS_256.dds`, `CSC_BAKERS_128.dds`, etc.

Create a flattened master duplicate by merging all visible layers. The layer named `Background` should be included as the bottom/background layer. Hidden layers other than `Background` should not be included. The original XCF must remain unmerged.

Export the following DDS files from the flattened master, scaling directly from the 1024x1024 master for each output size:

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
- Mipmaps: No mipmaps
- Perceptual error metric, gamma correction, sRGB, and alpha coverage options: disabled/unchecked
