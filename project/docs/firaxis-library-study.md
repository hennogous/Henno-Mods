# Firaxis Library calibration — 2026-09-10

Follow-up: [campus family study](firaxis-campus-family-study.md) adds direct CON/PIL
and University CN6 measurements and resolves the foundation's B/N/G-only bindings.

Henno supplied intact/construction FGX, campus material/texture files and then an
intact CN6 export. Original files remain untouched. The CN6 header identifies a
CivNexus6 1.3.3 export. Direct CN6 counts and material ranges match adjacent GEO metadata.

The [full study and artifacts](</Users/henno.gous/Library/CloudStorage/GoogleDrive-henno.gous@gmail.com/Other computers/My PC/Working Files/Dropzone/Codex/research/library-study/README.md>)
contain hashes, raw geometry, scripts, map/UV/mipmap sheets, material ablations and a
packed `Library-material-study.blend` preview.

| Intact CN6 | Vertices | Triangles |
|---|---:|---:|
| Whole mesh Library031 | 999 | 537 |
| DIS_CMP_Base group | 843 | 445 |
| Foundation_Modern_01 group | 156 | 92 |

**One mesh, two material groups:** this directly illustrates the distinction missing
from simple mesh-count summaries. It does not measure draw calls. Construction GEO
metadata separately reports 1,567 vertices/833 primitives across two meshes and three
groups; construction FGX geometry was not decoded. AST state visibility is unverified.

The intact mesh has 231 indexed components; diagnostic position grouping at 0.001
source units produces 417 distinct positions and 30 components. About 38.55% of supplied
corner normals differ from their geometric face normals by >1°. Combined with the
[Market study](firaxis-market-study.md), this supports preserving deliberate shading
on economical patches, rather than imposing uniform flat shading or blanket welding.

Campus-group UV1 covers **17.059%** of its atlas with substantial reuse. UV2 covers
**2.077%**, with no overlap detected by 1024² triangle-interior sampling. Foundation
faces are excluded because they sample a different material domain. These are this
group's footprints, not estimates of unused family atlas capacity. The rasterizer
passes full-square and duplicate-square checks; subpixel overlaps remain a limitation.

Clay/base/combined previews show geometry retaining the dome, main masses, columns,
roof profiles and steps while textures supply most windows, courses and ornament.
Painted depth and normal relief align. Quiet masonry and saturated blue accents also
show why “restrained painterly” must not mean desaturating every material.

## Isolated mipmap variants — not promoted to workflow guidance

The supplied B_MIP and B_MIP_Sharpen TEX files explicitly declare MANUAL_MIPS. Their
1024² DDS pixels are identical; their lower mips differ substantially. Actual stored
mip payloads were decoded and checked against Pillow's top-level decode.

However, both variants contain different artwork from the ordinary bound B map, and
their materials also bind opacity and omit emissive. There is no inspected AST proving
their use by the shipped Library. Henno reports that explicitly named MIP files are
very rare across the Pantry, with these possibly among the only examples. This is
user-reported inventory context, not a completed census, but it further weakens any
claim that these files represent a normal Firaxis authoring practice. Retain the file
measurements as an isolated observation; do not promote them into skill guidance or
prioritize further investigation without a concrete need. Ordinary automatic mip
generation and troubleshooting of filtering remain separate technical concerns.

## Limits and next inputs

The foundation material is unresolved and shown in neutral gray, with no terrain
clipping. The preview approximates the shader with AO multiplication and roughness=1−G;
emissive is off, and game tangent/normal convention remains unverified. CN6 tangents
and binormals are retained in JSON; Blender computes its own preview tangent basis.

Useful next inputs are Foundation_Modern_01 MTL plus its bound textures, the matching
Library AST and controlled game/Asset Editor view, and construction CN6 for direct
state comparison. Rendering bottleneck rankings still require game measurements.
