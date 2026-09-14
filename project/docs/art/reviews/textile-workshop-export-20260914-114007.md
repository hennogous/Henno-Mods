# Textile Workshop export review — 14 September 2026

Reviewed run: `20260914-114007-861249`, the newest run at review time, under
`C:\Users\Shadow\Desktop\Working Files\3D Art\TAILORS\Textile Workshop\revision-08-export-ready\export-runs`.

**Result: no blocking issues found in the exported package. Ready for installation
and Asset Editor review.** This review did not install or edit staged/live assets.

## Verified

- The run completed discovery, decode, build and Windows conversion with zero
  reported blockers: 11 custom assets, 12 geometries, 32 attachment placements,
  5 used material identities (3 generated MTLs), and 13 generated DDS textures.
- Reopened all 12 FGX files with Firaxis/Granny through `FGXToCN6.exe`. Mesh names,
  vertex counts, triangle indices and material-index columns matched decoded
  inputs. All three UV sets and normal/tangent/bitangent data survived. Maximum
  observed position difference was below 0.00005 Blender units; UV difference
  below 0.00000008. Readback text rounds floats, so these are comparison bounds,
  not a claim of exact binary equivalence.
- Both primary building geometries contain 6 meshes, 1,603 exported vertices and
  952 triangles each, including the fixed loom and dye vats. These counts exclude
  their attached props and shared construction/pillage models.
- Both variants contain 16 attachment points. Identities, translation, Z rotation
  and uniform scale match the decoded placements. Custom attachments have staged
  XLP registrations; generated asset IDs are registered once. Reused pantry
  attachments retain native state behavior under the configured policy.
- All referenced AST model geometry files, FGX files, mesh/group pairs and material
  identities resolve against the stage, live mod or SDK pantry. Generated material
  texture references resolve to TEX and DDS files. No asset-level AO, LightMap or
  EmissionMap override masks the generated material bindings.
- All main mesh groups have the five expected states. Intact buildings are visible
  in Worked/Unworked/Unbuilt; authored standalone props in Worked/Unworked. Shared
  construction/pillage and base-decal model state tables match the bundled profile.
  The 11 supplied debris meshes are visible only in Pillaged.
- All 13 DDS files passed header, dimensions, format, payload and mip-count checks.
  All 90 converted-file manifest hashes match. Recorded source blends, library
  inputs and source image hashes still match. Destination baselines also match,
  so the run has no detected conflict with current mod files at review time.

## Non-blocking observation and remaining review

The converter logs warn about obsolete virtual-space paths under
`C:\Users\Shadow\Desktop\Civ Supply Chains\Assets` and `Resource`. All FGX files
were nevertheless produced and successfully reopened; the warning did not prevent
the tested geometry conversion. It is not evidence that Asset Editor's dependency
browser is correctly configured.

Actual shader appearance, animated/runtime state transitions, terrain-following
of independent attachment pivots, Asset Editor dependency registration and cooking
remain unverified. No visual or in-game approval is implied by this structural
review. In particular, pantry attachments retain their native state behavior;
their final appearance alongside generated debris needs the shared game review.

Local review intermediates and numerical results are in
`project/snapshots/export-review-20260914-114007/` (ignored scratch output).
