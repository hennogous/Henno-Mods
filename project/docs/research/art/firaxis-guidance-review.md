# Firaxis guidance reviewed against our asset studies

> **Documentation audit — 2026-09-12: Current.** Dated, pinned guidance review explicitly corrects earlier AO interpretations and informs the current art skill. New original-design advice must be scoped to original assets; existing kit variations follow the user plan.
> Classification: Evidence review. See the [full audit](../../DOCUMENT-AUDIT.md).

2026-09-10. Local reference: `/Users/henno.gous/Play/Civ-6-Documentation`, cloned at
`2c6b1baaf45c658600ac00b92a51c08b0334a3b4` from the user-supplied community mirror.
This is an archive of guidance spanning several development dates, not a current
shader specification. Reviewed BuildingsProcess text/illustrations and relevant
texture-class descriptions. The mirror is not presented as the original publisher.

## Source takeaways

The [building guidance](https://github.com/Wild-W/Civ-6-Documentation/blob/2c6b1baaf45c658600ac00b92a51c08b0334a3b4/Civ6Docs.html)
connects exaggerated, readable masses with modular textures and painted shading.
It asks for genuinely different concept silhouettes, game-scale context and roof
interest. Its normal-support examples remove lighting before defining relief.
Asset AO overrides material AO; city-block setup uses asset-level AO. The workflow
also values reuse between construction and pillaged geometry. These are scoped
source observations, not a mandate for new approval gates or a performance ranking.

## Interpretation of the supplied modder opinion

Henno relayed an unnamed modder's view that fidelity should lead abstraction. Treat
that as community interpretation, not a Firaxis quotation or a verified attribution.

Our Library, Market and city-block comparisons make the useful meaning concrete:
architectural detail should survive simplification. A window needs a convincing
frame and recess; tile courses should explain how the roof is built; a forge should
look usable. Fine geometry is only one way to communicate these things. The inspected
models already demonstrate convincing surface construction on economical meshes.

The unhelpful interpretation would be a required realistic high-poly model before
stylization. That would discard the practical advantage of our primitive-based approach.
Another unhelpful interpretation would be covering every material with equal detail.
The city block's calm plaster is part of why its trim, openings and roof edges read.

My working standard: preserve believable construction and material character while
choosing proportions and detail deliberately for the game view. Our gray blockout
and textured review are complementary checks. Passing one cannot excuse failing the
other. Neither technical polygon economy nor a painterly label is an artistic result.

## Corrections to our previous research

- The foundation MTL proves that its own AO slot is empty. It does **not** prove that
  the foundation receives no AO. The complete asset chain remains uninspected.
- The city-block UV2 area remains 4.75884% of the unit square. Calling that a measured
  allocation within the supplied Base_A texture was too strong. Its preview used an
  assumed map, so that AO treatment must not be accepted as native shading evidence.
- The four campus UV2 layouts remain disjoint, totaling 16.36378% of the unit square.
  Without their asset bindings, disjoint coordinates do not establish a common final
  texture or its memory cost. The coordinate measurements themselves remain useful.
- Separate state AO should not become compulsory. Test whether a reused bake represents
  the necessary occlusion; decide only after resolving actual texture bindings.

Earlier repo summaries and Dropzone reports now carry this correction. Source geometry,
raw UV measurements and map images remain unchanged. The next missing technical input
is the relevant AST—not more speculation from texture names. No existing exported
mod asset was changed, and no new texture architecture is imposed on approved work.

## Changes to our working skill

The skill now requires effective AO binding resolution, preserves valid bake reuse,
and treats the modder's observation as a construction-quality check. It also separates
major silhouette beams from secondary trim and asks for alternative massing before
polishing a new design. These are our implementation choices, calibrated by the native
assets and source review; they are not a verbatim reproduction of Firaxis's process.

For the next original asset, use the already approved brief, compare a few genuinely
different massing studies, then review one at its intended size beside a native asset.
Keep our clean primitive geometry and predictable export counts. Improve construction
specificity and aligned surface detail rather than simply adding noise or polygons.
