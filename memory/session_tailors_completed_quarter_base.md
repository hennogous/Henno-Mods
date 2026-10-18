# Tailors completed Quarter base — 14 October 2026

Henno created CSC_TAILORS_Classical_Base_06 and its Landmark entry, requesting
selection only while all three Tailors alternate-art/service flags are active.
He also confirmed CSC_TAILORS_Fashion_House_2 is ready and requested selection
while any Stage4 service is active.

Wired the existing completed base with a native `and` of all three CITYPROP
intervals at priority1, preserving its full building set and era/culture tags.
Added the missing Stage4 source modifier to Fashion House under the exact
REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ, the shared Lua binary mirror, and
GamePropertyRanges classifier. Added a priority1 Fashion_House_2 BuildingVariant
using the Stage4 active interval. Both assets were already registered in XLP;
no AST, geometry or AE placement changes were made.

Docs: project/docs/art/expanded-building-art.md and dynamic-art-properties.md.
Updated Stage4 contract/SQL assertions and retired obsolete deferred-flag checks.
The offline validator now skips legacy-column ALTER when the runtime cache lacks
the helper table entirely; CSC_Q_ALL creates it during fixture loading.

Checks: eight flag combinations select full base only for111 and Fashion House
alternate for Stage4=1; Lua reset clears both. XML/AST/package and priority/hero
bindings pass; Stage4 handoff passes; 18 validator regressions pass. Test-created
temp dirs were redirected into the authorized workspace due sandbox TEMP errors.
Cook and in-game appearance remain unverified; rebuild/reload for review.


Naming correction after Henno's review: the shared catalog already required
bonus-semantic flags, but Stage3/4 contract metadata and validator checks were
incomplete. Changed active names to CSC_TAILORS_STAGE_3_EFFECT_FAITH and
CSC_TAILORS_STAGE_4_EFFECT_TOURISM, plus matching ART/ACTIVE identifiers across
SQL/Lua/ArtDefs/docs/assertions. Added effect_content and interval metadata,
bound the shared pattern to all three service requirements and added generic
validator enforcement plus five regression cases. 29 Quarter regressions and
eight-state art checks pass. Stage3/4 approved slice hashes were amended under
Henno's explicit naming correction; their gates remain implementing while the
full phase command check reports unrelated stale CSC_QUARTERS_PEDIA.sql output.
Scoped semantic/SQL/Lua/build-wiring/Tailors-text checks pass. No unrelated
Civilopedia source/output was changed; rebuild/reload needed for renamed flags.
