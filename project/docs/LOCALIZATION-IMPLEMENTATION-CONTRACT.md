# Localization Implementation Contract

Quarter localization is a mechanical UI contract. The approved design supplies
the facts; live implementation proves those facts exist; Bakers supplies the
applicable expression pattern.

## Source rule

Edit `project/localization/CSC_<QUARTER>_TEXT.md`. Generated SQL under
`Civ Supply Chains/Text/` is output and must pass `loc_md_to_sql.py --check`.

Text must never promise a design-only or partially implemented effect.

## Building-description grammar

Use the applicable Bakers ordering:

1. material/input transactions;
2. citizen slots and citizen yields;
3. local Quarter transactions;
4. adjacent customer/sales transactions;
5. trade-route transactions;
6. service unlocks and downstream effects.

Each complete bilateral transaction is stated from the described object's
perspective in one bullet:

> `received effect`, in exchange for `counterparty effect`.

Do not split the two halves into separate bullets when Bakers expresses the
same mechanic as one exchange. Use exact yield icons, numeric formatting, and
participant scope from the implementation contract.

Use a blank line between transaction bullets and a following service paragraph,
matching Bakers. Use `{LOC_...}` substitution for named services where the
Bakers pattern does so.

## Service grammar

- Name the destination/customer first where it improves comprehension.
- State the eligibility relationship and unlock exactly.
- State every implemented effect, including the exact Great Person class.
- State stacking or cardinality explicitly where player interpretation depends
  on it.
- Do not use broad era wording unless it matches the implemented promotion
  classes and era gates.

Service UI append text and civic append text are separate surfaces and require
separate traceability assertions.

## District descriptions

District descriptions are concise placement/economic overviews. They must use
the Bakers bullet structure and icon conventions, but only values proven by the
district implementation and active compatibility patches.

Optional-mod text changes live in the appropriate ModSupport localization
source and must compose with the base text without duplicate appends.

## Civilopedia

For every phase participant declared in the gameplay contract:

- supply-chain title and paragraph;
- historical-context title and paragraph;
- correct registration through the Quarter Pedia pipeline;
- text that distinguishes actual gameplay from historical explanation.

Historical prose may be Quarter-specific. Mechanical Pedia prose remains bound
to the same design and implementation evidence as descriptions.

## Review checklist

- Every mechanical sentence maps to a traceability requirement.
- Each amount, icon, unlock, participant, scope, and direction matches code.
- Building-description sections follow the declared ordering.
- Bilateral transactions use the applicable Bakers exchange construction.
- Replacement coverage described in text matches replacement coverage in SQL.
- Gold and M&C claims are supported by their companion files.
- Service descriptions include all and only implemented effects.
- Generated SQL is current.
- Runtime-sensitive claims remain unmarked as tested until verified in game.
