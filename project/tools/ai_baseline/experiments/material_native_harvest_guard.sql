-- COARSE MECHANISM DIAGNOSTIC ONLY. Not production registration or AI tuning.
-- Test the shipped native no-resource-harvest legality effect when preferences
-- fail. It forbids ALL resource harvesting for these five saved-world AI owners,
-- not just CSC materials; district replacement/AI job behavior needs measurement.
-- It may impair helpful harvesting and leave incompatible jobs stuck. No direct
-- unit orders, resource restoration, real yields, boosts or treasury edits.
-- Exact unique leader traits exclude observer0 even during autoplay role changes.
INSERT OR IGNORE INTO Modifiers
 (ModifierId,ModifierType,OwnerRequirementSetId)
VALUES ('MOD_CSC_AI_NATIVE_HARVEST_GUARD_DIAGNOSTIC',
        'MODIFIER_PLAYER_ADJUST_PREVENT_HARVEST_RESOURCE','REQSET_CSC_AI_SUPPLY_AI');
INSERT OR REPLACE INTO ModifierArguments (ModifierId,Name,Value)
VALUES ('MOD_CSC_AI_NATIVE_HARVEST_GUARD_DIAGNOSTIC','Enable','1');
INSERT OR IGNORE INTO TraitModifiers (TraitType,ModifierId)
VALUES
('TRAIT_LEADER_KANDAKE_OF_MEROE','MOD_CSC_AI_NATIVE_HARVEST_GUARD_DIAGNOSTIC'),
('TRAIT_LEADER_RELIGION_CITY_STATES','MOD_CSC_AI_NATIVE_HARVEST_GUARD_DIAGNOSTIC'),
('TRAIT_LEADER_GENGHIS_KHAN_ABILITY','MOD_CSC_AI_NATIVE_HARVEST_GUARD_DIAGNOSTIC'),
('TRAIT_LEADER_JOAO_III','MOD_CSC_AI_NATIVE_HARVEST_GUARD_DIAGNOSTIC'),
('TRAIT_LEADER_DIVINE_WIND','MOD_CSC_AI_NATIVE_HARVEST_GUARD_DIAGNOSTIC');
