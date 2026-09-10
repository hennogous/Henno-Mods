# Art direction for economical Civ VI buildings

## Shape decisions

The user-supplied Firaxis guidance separates big shapes, intermediate shapes and
fine detail in a 3:2:1 hierarchy. Use it to organize visual emphasis, not as a literal
polygon allocation or mandatory numerical area measurement.

| Layer | Typical elements | Modeling decision |
|---|---|---|
| Big | Entire roof, house body, major attached volume | Establish footprint, silhouette, broad proportion and curvature |
| Intermediate | Chimney, large beams, porch, awning, balcony | Break silhouette selectively and communicate the building's role |
| Fine | Mortar, tile lips, grain, plaster wear | Usually material detail; geometry only when it reads at game scale |

Give surfaces a directional flow: swept eaves, changing beam width, flared supports,
slightly leaning or tapered masses. The marble metaphor encourages slopes and lively
curves, not arbitrary deformation of every functional horizontal surface. Intentional
asymmetry should still suggest a building somebody constructed.

Measure a sloping board perpendicular to its centerline. A vertical offset produces
a deceptively narrow board on a steep roof. On curved boards, use a controlled
profile/sweep and miter joins, and align grain to the path. Exaggerate forms that must
read from above; avoid multiplying equally prominent competing accents.

Simple geometry can be visually detailed. Do not confuse silhouette economy with
uniformly bland surfaces. Conversely, a dense texture cannot rescue a weak roofline.

## Concepts that can become assets

Choose an era/culture and a small number of identifying features. Request a readable
three-quarter building study with clear material blocks and an uncluttered background.
Translate atmosphere and illustrated lighting into material/geometry decisions; do
not model painted shadows. For ambiguous roofs or rear walls, resolve the construction
in a gray model or supplementary view before detailed UV work.

Preserve the user's approved features across iterations. Track why a silhouette was
changed rather than allowing each generation to redesign the asset accidentally.

## Painterly materials

Observations from the supplied Firaxis watermill and commercial atlases:

- Broad material faces have calm value/color fields with purposeful abbreviated marks.
- Construction remains detailed: framing, mortar, recesses, tile lips and grain are
  designed to be legible, not merely covered in random noise.
- Selective painted highlights/crevice shading coexist with normal-map relief.
  Removing all painted shading is not automatically more faithful to the style.
- Gloss contrast contributes to material identity; intense specular flecks or coarse
  bump on plaster can undo a convincing painted base.

For atlas image generation, describe regions, boundaries, material identities and
grain orientation explicitly. Specify restrained wear, quiet broad faces and selective
edge definition. Avoid oil-paint impasto, dense scratch/grunge overlays and photographic
wood grain unless the reference really calls for them. Judge the returned image;
these words do not guarantee compliant output.

Authored height should represent construction: flat raised stone faces with broad
bevels, lower mortar, controlled tile lips and selected grooves. Using inspected dark
seams as a mask can help, but dark color is not height ground truth. Asset-specific
thresholds need visual review after a repaint. Use neutral material to expose false
embossing of brushstrokes or color patches.

## Game-view review

Compare to neighboring reference buildings at the same displayed scale and light.
Look at silhouette first, broad color separation second, useful relief third.
Check all relevant rotations and states; a still from one view does not prove hidden
surfaces are safe to remove or that normal orientation is correct.

In the blacksmith screenshot, the heavy timber and roof remained readable. Potential
follow-ups were softer repeated tile-edge contrast, a warmer/less pristine chimney,
and clearer forge-bay emphasis. These were assistant visual judgments awaiting a
tested revision, not measured rules for all Civ VI buildings.

## Source and evidence

The Firaxis reference supplied by the user is mirrored at
[Civ6Docs.html](https://github.com/wildweegee101/Civ-6-Documentation/blob/main/Civ6Docs.html).
Keep source excerpts, user preferences, interpretation and experiment results distinct.
Preserve visual crops with their source/asset identifiers in the owning project's
reference collection when permitted; do not silently turn third-party opinions into
official Firaxis requirements.
