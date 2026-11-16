# Fixed building transactions: migration and regression

16 November2026, roadmap1.4/2.1; ordinary-economy goal G1. Nine fixed
relationships now live beside the population transactions in gameplay-owned
headers, payout legs and native gate bindings. Bakers Water/Wind Mill alternatives
exchange with Granary, Bakery and Café; Tailors Workshop exchanges with Lighthouse,
Tailor and Fashion House. Gold companions append legs to the same relationships.

`CSC_FixedBuildingTransactionProcessor.sql` generates the native modifiers,
attachments and narrowly specified requirement templates. Local exchanges remain
city-scoped. External outward wrappers require a functioning customer building;
reverse wrappers retain their original narrower checks. Owner-side unique
building replacements inherit once. Shared native leaves must have consistent
terms. The central model reads declared amounts, keeps actual payout recipient
separate from enabling investment, and selects one alternative Mill.

## Gameplay change list

No intended payout, ownership, availability or gate changes. Existing modifier
and requirement identities remain. Authored native rows move into generated
projections; Stage2 customer metadata is generated from these same relationships.
The shared Café Food leaf remains guarded as a material unit term until the
directional material migration is complete. Population effects retain the already
QAed Q8 baseline from60b51107, not the earlier decimal implementation.

## Verification

-17 transaction tests pass: golden native graphs with Gold on/off and synthetic
  owner-side uniques;288 population worlds; changed fixed amount reaching native
  leaf and model; shared-leaf conflict rejection; one-Mill selection; actual
  recipient attribution; absent catalogue data; enforced native foreign keys.
-102 economic/model/adapter tests pass.
-Bounded zero-turn250 replay `fixed250-02`: all10,954 CSC native effect rows
  exactly equal a fresh original-package replay, including actual engine columns,
  defaults, Services and material effects. Fixed subset137 rows also matches.
  Population refresh equivalence passes across67 cities. Session exit0, owners
  absent, preferences and package restored. No diagnostic save is retained.

The original package is frozen from `csc-ai-customer-first-continents-20261116/
continents250-01`. Qualified loaded XP2 SHA256:
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
Artifacts: `C:/Users/Shadow/Desktop/Codex/csc-ai-ordinary-economy-20261116`,
`original250-01/all-csc-native-graph.json`, and `fixed250-02` equivalence and
session-closed records. Native SQL preference remains1.

The first attempt caught a real generator defect: SQLite REPLACE deleted shared
requirement parents, cascading into dependent modifiers. Stable INSERT/UPDATE
fixes it. New tests enforce the engine's foreign keys and preserve unrelated
siblings/memberships. The corrected full graph comparison is stronger than the
initial fixed-only check.

## Human QA after the complete economy implementation

Check one external customer and one local exchange for each Quarter, both Mill
alternatives, Gold on/off, a unique customer, and independent producer/customer
pillage and repair. The final goal handoff will consolidate these with material,
population and customer-placement cases. Human QA and long games follow the
complete implementation; this report closes only the fixed migration slice.
