# Bakers reference pattern catalog

> **Documentation audit — 2026-09-12: Current.** All three Bakers pattern catalogs exist under project/specs/reference. The reusable/parameterized/optional/Bakers-only distinction remains applicable; current control.yaml owns phase approval state.
> Classification: Quarter workflow. See the [full audit](../DOCUMENT-AUDIT.md).

The gameplay catalog is
`project/specs/reference/bakers-gameplay-patterns.yaml`. It describes reusable
implementation shapes from Bakers without making Bakers itself a universal
template.

The companion visual/architectural catalog is
`project/specs/reference/bakers-sql-style.yaml`. It records the SQL presentation
style demonstrated by Bakers and the CSC/Civ VI skill rules that should be
machine-enforced rather than left to prose review.

## Classifications

| Classification | Meaning |
|---|---|
| `reusable_invariant` | Structural rule that applies unless the design explicitly says otherwise. |
| `reusable_parameterized` | Reusable pattern whose identifiers, yields, amounts, gates, and targets must all be supplied by the Quarter contract. |
| `specialized_optional` | Proven implementation for a mechanic that is used only when the Quarter design calls for it. |
| `bakers_only` | A Bakers peculiarity that other Quarters must not inherit automatically. |

The validator rejects any `bakers_only` pattern referenced by a Tailors
requirement.

The SQL style validator separately checks section hierarchy and order, subsection
presentation, top-level keyword placement, wide-table value comments, new-file
whitespace, Gold companion isolation, M&C Gold isolation, shared-table ownership,
and accidental Bakers identifiers.

## What is parameterized

The catalog covers:

- Quarter types, material classes, and core resource mappings;
- both directions of resource-improvement transactions;
- M&C Industry and Corporation totals;
- district definition, material adjacency, bilateral district transactions, and
  river-edge scaling;
- stage building definitions, local exchanges, customer exchanges, specialist
  yields, and amenities;
- decimal per-population and integer per-N-population transactions;
- direct one-level replacement handling;
- persistent hidden services, their destination effects, and Wonder variants;
- domestic supplied trade routes and their UI/gameplay property contract;
- Gold companion splitting;
- preserved optional-mod resource mappings;
- deferred dynamic-art property bridges.

Each entry lists its required parameters and invariants. A Quarter requirement
must provide all design values; the catalog never supplies a missing yield or
amount.

## Bakers behavior explicitly excluded from Tailors

The catalog marks Bakers stage-two Water/Wind variants, river/no-river flag
buildings, and vanilla Water Mill/Palgum replacement handling as `bakers_only`.
These cannot leak into Tailors through broad copying.

## Updating the catalog

Change a classification only with a reviewed example and a reason. When the
reference SQL changes, update its hash in the Quarter control file and re-review
the affected catalog entries. Once Tailors is complete, prefer Tailors anchors
for normal Quarter structure and keep Bakers anchors only for specialized
mechanics not exercised by Tailors.
