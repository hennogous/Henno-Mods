# Quarter localization patterns

The localization catalog is
`project/specs/reference/bakers-localization-patterns.yaml`. It captures the
Bakers sentence structures and document coverage separately from Tailors values.

## Source and generation

The editable source is Markdown under `project/localization/`. Generated SQL
under `Civ Supply Chains/Text/` is an output and is never edited directly.

Localization is produced from the approved implementation contract, not merely
from the public design. This prevents text from promising a mechanic that the
game does not implement.

## Required wording structures

- District and material effects are ordered exactly as the design.
- District bilateral effects use one sentence ending with the effect “in
  return.”
- Building transactions use “from …, in exchange for …”, including local and
  adjacent-customer exchanges.
- Service introductions state the Civic, supplied source building, service, and
  destination condition.
- “Supplied” is used only when the gameplay requirement actually checks the
  stated materials.
- Trade text states destination yield, Quarter return, the missing-Quarter gate,
  and the origin amenity.
- Industry and Corporation sub-bullets state final totals, not opaque deltas.

The exact slot structures live in the YAML catalog so validators and future
generators can consume them.

## Coverage beyond object descriptions

A complete Quarter localization implementation includes:

- all district, building, service, and UI names;
- district and building descriptions;
- supply-chain and history Civilopedia chapters;
- append text for every affected vanilla customer building and Wonder;
- append text for every service-unlock Civic;
- notification state variants only if the shared notification subsystem exposes
  that service.

Every one of these obligations is attached to the same implementation
requirement as its gameplay behavior.

## Tailors as the future text reference

After Tailors is accepted, its localization source should become the normal
Quarter reference because it will be generated under this contract. Bakers
remains authoritative only for text surfaces or specialized mechanics that
Tailors does not contain.
