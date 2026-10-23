# AI+ review — 20 October 2026

Reviewed Workshop878717347 read-only: SiestaGuru AI+, manifest version13, Workshop last update15March2019. All8XML/SQL content files plus manifest are archived by hash in Desktop/Codex/csc-aiplus-review-20261020/source-and-native-evidence.json. No game launched, installed/source CSC content or preferences changed.

## Named research preferences

core.xml12-29 registers STD_TECHS and STD_CIVICS attached to TRAIT_LEADER_MAJOR_CIV, System Technologies/Civics. Lines626-634 favor Political Philosophy, Suffrage, Exploration and selected technologies. Entries omit Favored/Value; the actual current native AiFavoredItems schema defaults to1/0, so this is not a new flag configuration relative to our controls. individualization.xml registers custom personality traits and lists (ECON_CIVICS etc), with the same rows. The installed package has no Lua files or Lua actions. It adds no dynamic material-aware research preference API. Its success as a whole does not establish individual research entries work on current native code. General technology/civic pseudoyields are each set to1 at core.xml756-760, another broad valuation choice, not a service-specific target.

## New native research-goal lead

AI+ modifies behaviour trees for military and construction. Following its Build City Improvement edits into our verified native database revealed an independent native mechanism: NodeDefinitions defines Add Goal Tech as asking Research AI to work on specified units/buildings/techs. NodeDataDefinitions includes Desired Techs (DefnId4), Desired Civics (6), Contract ID output(7), Tech Value(8), plus improvements and a goal plot. Despite the name, it explicitly accepts civics. Existing native trees bind civic inputs: Build City District node8 uses Needed Civic; Research Trigger Tech node3 uses Needed Civic; Seek Target Wonder node14 uses Prereq Civic. This is actual native schema/wiring evidence, not a claimed tested effect or an AI+ implementation of CSC research goals.

Research Trigger Tech is a four-node Sequence -> Decode Trigger -> Contract Manager Decorator -> Add Goal Tech. It decodes Needed Tech, Needed Civic and Value into a research contract. No TriggeredBehaviorTrees row references this tree in the inspected database; do not invent a Lua-callable trigger or assume a custom trigger can be registered merely by adding rows. The crucial feasibility question is how to create/cancel a valid native goal with the right list/value payload and lifecycle from a legitimate trigger. Test boundedly before proposing deployment. Existing district/building/improvement prerequisite contracts are a possible entry to investigate, not a proven CSC Service adapter. No forced research setter or research boost is required by the node description, but real behaviour remains to be verified.

Recommended next step: inspect native trigger/contract entry points and attempt a disposable fixed civic-goal positive control, verifying logged candidate scores, actual next selection and goal expiry. Only after that test whether a Quarter/material condition can create and retract the goal. This offers a distinct route after the named-item preference nulls. Keep original Real Strategy civic preference reproduction as a separate control if useful; no more long games until a score/goal response is demonstrated.

## Builders

behaviortrees.xml732-733 adds DefnId2=-1 to Build City Improvement Build Unit nodes13/23. Current native schema identifies that parameter as Required City(-1 for any city), confirming the comment Allow building workers in any city. The two nodes contract Builders for clearing plots and improvements respectively; the native tree first tries Find Available Unit before Build Unit. This is a production-location constraint, not proof of improving idle Builder deployment or Quarter-mapped target selection. Its effect and contract traffic require a distinct test before copying.

core.xml668-669 uses improvement default5, plus era/peace/not-under-siege percentage biases (lines908-915). This supports state-sensitive improvement demand rather than assuming a large constant is optimal. Like Real Strategy, Specific Resource settlement rows govern city settling, not exact Quarter placement. No new per-resource/per-Quarter adjacency or ResourceModifiers mechanism found.

## References

- https://steamcommunity.com/sharedfiles/filedetails/?id=878717347
- Installed core.xml, individualization.xml, behaviortrees.xml, AI+.modinfo (read-only)
- Verified CSC-only native snapshot: Desktop/Codex/csc-ai-clean-strategies-20261020/research/custom/native-gameplay.sqlite
