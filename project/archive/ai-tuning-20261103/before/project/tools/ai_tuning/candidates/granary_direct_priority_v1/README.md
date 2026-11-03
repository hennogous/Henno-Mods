# Experimental direct Granary priority v1

Experimental candidate; native delivery and limited wider-city follow-through were
observed in the completed110→131 pilot. No shipping activation. See the
[qualified result](../../../../docs/research/mods/csc-ai-granary-direct-priority-20261101.md).
Append only
`granary_direct_priority.sql` to the existing CSC `ModSupport_RH_AI.sql` for a
separately approved bounded arm. Do not append the old conditional Lua/SQL.
There is no candidate Lua payload, callback, private flag, new strategy, yield,
grant, forced queue, RH-file edit or manifest change. The compact Lua file here
is an observation-only preflight reader.

## Why a direct trait binding

For pinned GameCore SHA256
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`, reviewed
StartStrategy538fb0 has no Buildings dispatch. CityPlannerInitialize4b4250
loads direct leader/civilization-trait Buildings queries into the vector consumed
by GetBestBuilding; deserialize4afde0 calls that initializer on load. These static
findings support testing the direct path, not claiming native delivery in advance.

The candidate adds exactly one new list, `CSC_AI_GranaryDirectPriority_V1`,
binding AiLists.LeaderType to **TRAIT_LEADER_GENGHIS_KHAN_ABILITY**, System
Buildings, with only BUILDING_GRANARY Favored1/Value0. LeaderType here is a TRAIT
binding, not the raw LEADER_GENGHIS_KHAN name. Value0 is metadata, not an added
yield or proportional score. All existing RH/CSC rows and private forecast40
remain unchanged.

The immutable pretrial native DB is referenced in place:
`Desktop/Codex/csc-native-producer-decision-20261030/run-04/on/runtime-gameplay.sqlite`,
SHA256 `e7267fd206e7c4ea3553c9ad06973de9ea811a6467a27e2391bdc1914d5de2c8`.
Read-only SQLite fixtures copy it to memory only. It contains the exact trait,
one LeaderTraits mapping to Genghis, no civilization mapping for that trait and
no other leader inheriting Genghis. The original closed census did not record
leader/civilization names; actual roster membership is therefore still a native
preflight requirement, not an offline source fact.

## Honest scope and native preflight

This is a PERSISTENT trait/type preference while candidate rows are loaded. It is
NOT conditional on Bakers/Mill/Base/customer state, NOT local to city196610 and
NOT an arbitrary player3-only rule. In the verified scenario it is intended for
original AI3's eleven cities, including off-target cities. A duplicate/shared or
later human-controlled matching leader could also have the preference. This
bounded original-AI trial cannot establish general autoplay/human or release
safety. Record all AI3 Granary proposals, starts, purchases, completions and costs.

Run `granary_direct_preflight.lua` in PlotInfo after the sole driver replaces its
single `__ORIGINAL_HUMANS__` placeholder with the EXACT already-verified Gameplay
CSC_AI_ASSISTANCE_V1_INITIAL_HUMANS mask as a Lua literal. This is observation
metadata injection, not a Game-property mutation. The reader deliberately uses
no UI Game:GetProperty getter. Leader name follows profile_initial_census.lua;
civilization name and trait joins follow CSC_AdjacencyCore.trait.

It prints `CSC_GRANARY_DIRECT_PREFLIGHT=<JSON>` with:

- turn/profile/list_type/binding_trait, original_humans and role_source.
- rows.list_types, lists, favored, leader_trait_bindings,
  civilization_trait_bindings (scalar native row copies).
- roster0..5 in array order, each with player, leader/civilization, alive/major,
  original_role_known/original_human, inherited leader_chain, leader_traits,
  civilization_traits, binding_sources and candidate_membership.
- eligible_player_ids, errors and scope_verified. Only original AI3, with
  Genghis/Mongolia identity, may resolve the candidate trait in this roster;
  observer0 must be known originally human. Missing data, inheritance cycles,
  wrong rows or extra shared members fail closed.

`scope_verified` proves this row/identity check only. Native preference is
explicitly UNOBSERVED_BY_THIS_READER. Require an identity-valid actual positive
Granary preference from the existing fixed-target native observer before efficacy
interpretation. DB rows and static load-path reasoning are insufficient.

## Bounded outcome gate

Any next native arm needs separate root review/GO, exact source110/619 baseline
and maintained source/package/settings restoration. Keep private40, real yields,
economics and native AI orders unchanged. Observe target Granary completion AND
three subsequent consecutive retained benefit observations, with hard endpoint131
and no extension. Distinguish preference input, final ranking, contract/queue,
construction or purchase, actual Food/reciprocal Mill Production and supply
retention. Late completion is censored; no completion or no positive native input
is not a completed mechanism/benefit result. Existing source110 controls remain
qualified descriptive context, not an isolated causal or observer-neutral proof.

`test_granary_direct_priority.py` verifies the exact immutable DB hash, trait/
inheritance uniqueness, three-row-only additive SQL, existing RH/private40
preservation, idempotence, non-RH/missing-binding inactivity, and actual Lua51
roster/preflight failures. No database, executable, save or dependency is cloned.
