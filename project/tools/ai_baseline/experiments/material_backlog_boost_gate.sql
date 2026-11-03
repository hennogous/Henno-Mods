-- Mechanism diagnostic only; NOT registered in the normal CSC project/package.
-- The observed native Mine/clear jobs originated from the improvement-count
-- boost handler while the material-backlog strategy was active. Test deferring
-- that handler during the EXISTING strategy, without changing work urgency,
-- Builder/production preferences, yields, boost rules or direct unit orders.
-- This is player-wide while active, not a plot-specific veto. It also defers
-- useful Farm/Pasture/Quarry/etc. boost jobs; actual benefit is UNPROVEN.
-- It need not cancel an already reserved job. Native logs must establish effect.
INSERT OR IGNORE INTO AiListTypes (ListType)
VALUES ('CSC_AI_MATERIAL_BACKLOG_BOOST_GATE_DIAGNOSTIC');
DELETE FROM AiFavoredItems
WHERE ListType='CSC_AI_MATERIAL_BACKLOG_BOOST_GATE_DIAGNOSTIC';
DELETE FROM AiLists
WHERE ListType='CSC_AI_MATERIAL_BACKLOG_BOOST_GATE_DIAGNOSTIC';
DELETE FROM Strategy_Priorities
WHERE ListType='CSC_AI_MATERIAL_BACKLOG_BOOST_GATE_DIAGNOSTIC';
INSERT INTO AiLists (ListType,System)
VALUES ('CSC_AI_MATERIAL_BACKLOG_BOOST_GATE_DIAGNOSTIC','TechBoosts');
INSERT INTO AiFavoredItems (ListType,Item,Favored,Value)
VALUES ('CSC_AI_MATERIAL_BACKLOG_BOOST_GATE_DIAGNOSTIC',
        'DEFAULT_HANDLER_HAVE_X_IMPROVEMENTS',0,0);
INSERT INTO Strategy_Priorities (StrategyType,ListType)
VALUES ('STRATEGY_CSC_AI_MATERIAL_BACKLOG',
        'CSC_AI_MATERIAL_BACKLOG_BOOST_GATE_DIAGNOSTIC');
