# Bakers Reference Contract

The Bakers' Quarter is CSC's implementation reference, but it is not a
blind-copy template. A Quarter applicability manifest decides which Bakers
patterns govern a particular phase.

## Pinned reference

Each Quarter control file pins:

- the source commit used for review;
- every Bakers gameplay companion file used;
- the Bakers localization Markdown source;
- a SHA-256 hash for every pinned file.

The validator fails if a pinned file changes. When Bakers legitimately evolves,
update the lock, review the diff, revisit affected applicability decisions, and
approve the Quarter again.

## Reference dimensions

The Bakers files govern these dimensions when classified as applicable:

- section and registration order;
- stable identifier families;
- core versus Gold versus M&C file boundaries;
- shared action-modifier reuse;
- separate wrappers for distinct gates, sources, strings, or load boundaries;
- one attach wrapper per attached action modifier;
- requirements, requirement sets, and exact arguments;
- same-player adjacency and functioning-building gates;
- direct one-level unique replacement expansion;
- hidden persistent service buildings;
- modifier previews and player-facing discovery;
- Civilopedia registration;
- runtime verification shape.

They do not govern another Quarter's thematic choice, participant, yield,
amount, unlock, service effect, or customer. Those come only from the approved
Quarter design.

## Applicability review questions

For every phase, answer:

1. What is the closest Bakers mechanic family?
2. Which exact source anchor demonstrates it?
3. Is the pattern invariant, parameterized, conditional, shared,
   Quarter-specific, not applicable, or superseded?
4. Which values may change, and where are those values declared?
5. Which nearby Bakers behavior must not be copied?
6. Does the pattern cross core, Gold, M&C, localization, UI, or runtime
   boundaries?
7. What static and runtime evidence would distinguish a correct copy from a
   superficially similar one?

An anchor is a stable identifier or unique source phrase, not a line number.
Line numbers drift too easily.

## Known global invariants

- Register types before their use.
- Keep optional integrations additive and conditionally loaded.
- Keep Quarter Gold companion files Gold-only.
- Keep M&C tier deltas behind the M&C criterion.
- Expand vanilla replacements one level only unless a reviewed exception says
  otherwise.
- Reuse only truly identical action modifiers and requirements.
- Keep wrappers distinct when their attachment, gate, text, or load boundary
  differs.
- Never attach multiple `Name='ModifierId'` arguments to one attach modifier.
- Edit localization Markdown sources, then regenerate SQL.
- Treat SQL parsing as necessary but insufficient evidence.

## Updating the reference

A Bakers reference update is a controlled input change:

1. Record the new commit and hashes.
2. Diff each pinned file against the previous lock.
3. Identify affected applicability entries.
4. Update traceability or assertions if required.
5. Reset `review_status` to `draft` and `implementation_ready` to `false`.
6. Reapprove before further implementation.
