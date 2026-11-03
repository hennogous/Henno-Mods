"""C6: strategy-owned Yields preference, conditional Lua false versus true.

Native SQL is byte-identical in both arms. Both register the same unowned Yields
list and RH-shaped Call Lua Function strategy BEFORE player creation. Only the
Lua enabled constant differs. ON reuses OFF pristine world. No static trait
preference for this channel; callback/Following and research scores are separate
endpoints. No material or lifecycle claim from this constant-condition control.
"""
from pathlib import Path
import re

import civic_modifier_trial as dormant
import civic_modifier_custom_yield_trial as channel
from paired_standard import read, sha
from run import write

VERSION = 'civic-modifiers-strategy-yield-gate-v1'
TEST = 'C6-strategy-owned-yield-consumer'
YIELD = channel.YIELD
STRATEGY = 'STRATEGY_CSC_TEST_CIVIC_YIELD'
LIST = 'CSC_TEST_CIVIC_YIELD_LIST'
CALLBACK = 'CSC_TestCivicYieldStrategy'
original_comparison = dormant.comparison


def overlay(arm):
    # Deliberately ignore arm: only callback bytes may differ.
    return channel.overlay('on') + """
DELETE FROM AiFavoredItems WHERE Item='YIELD_CSC_TEST_CIVIC_GUIDANCE';
INSERT OR IGNORE INTO Types (Type,Kind) VALUES
 ('STRATEGY_CSC_TEST_CIVIC_YIELD','KIND_VICTORY_STRATEGY');
INSERT OR IGNORE INTO Strategies (StrategyType,VictoryType,NumConditionsNeeded) VALUES
 ('STRATEGY_CSC_TEST_CIVIC_YIELD',NULL,1);
DELETE FROM StrategyConditions WHERE StrategyType='STRATEGY_CSC_TEST_CIVIC_YIELD';
INSERT INTO StrategyConditions (StrategyType,ConditionFunction,StringValue,ThresholdValue) VALUES
 ('STRATEGY_CSC_TEST_CIVIC_YIELD','Call Lua Function','CSC_TestCivicYieldStrategy',1);
INSERT OR IGNORE INTO AiListTypes (ListType) VALUES ('CSC_TEST_CIVIC_YIELD_LIST');
INSERT INTO AiLists (ListType,System)
 SELECT 'CSC_TEST_CIVIC_YIELD_LIST','Yields'
 WHERE NOT EXISTS (SELECT 1 FROM AiLists WHERE ListType='CSC_TEST_CIVIC_YIELD_LIST');
INSERT INTO AiFavoredItems (ListType,Item,Favored,Value) VALUES
 ('CSC_TEST_CIVIC_YIELD_LIST','YIELD_CSC_TEST_CIVIC_GUIDANCE',0,100);
INSERT OR IGNORE INTO Strategy_Priorities (StrategyType,ListType) VALUES
 ('STRATEGY_CSC_TEST_CIVIC_YIELD','CSC_TEST_CIVIC_YIELD_LIST');
"""


def callback_bytes(arm):
    text = dormant.base.CALLBACK_AUDIT.decode() + """
local CSC_C6_ENABLED=__CSC_C6_ACTIVE_LITERAL__;
CSC_RESEARCH_PROBE_NATIVE.experiment_version='strategy-yield-gate-v1';
CSC_RESEARCH_PROBE_NATIVE.gate_active=CSC_C6_ENABLED;
GameEvents.CSC_TestCivicYieldStrategy.Add(function(pid,which)
 local r=CSC_RESEARCH_PROBE_NATIVE;
 local key=tostring(pid)..':'..tostring(which);
 r.calls[key]=(r.calls[key] or 0)+1;
 local active=CSC_C6_ENABLED and pid>=1 and pid<=5 and PlayerManager.IsAlive(pid) and not Players[pid]:IsHuman();
 if active and not r.first_true[key] then r.first_true[key]=Game.GetCurrentGameTurn() end;
 return active;
end);
print('CSC_C6_STRATEGY_CALLBACK_READY',tostring(CSC_C6_ENABLED));
""".replace('__CSC_C6_ACTIVE_LITERAL__', 'true' if arm == 'on' else 'false')
    return text.encode()


def native_check(db, arm, patch, source, with_rst=False):
    result = channel.original_native_check(db, 'on', patch, source, with_rst)
    assert db.execute('SELECT Kind FROM Types WHERE Type=?', (YIELD,)).fetchall() == [('KIND_YIELD',)]
    assert db.execute('SELECT DefaultValue FROM Yields WHERE YieldType=?', (YIELD,)).fetchall() == [(1,)]
    assert db.execute('SELECT LeaderType,AgendaType,System FROM AiLists WHERE ListType=?', (LIST,)).fetchall() == [(None, None, 'Yields')]
    assert db.execute('SELECT ListType,Favored,Value FROM AiFavoredItems WHERE Item=?', (YIELD,)).fetchall() == [(LIST, 0, 100)]
    assert db.execute('SELECT StrategyType FROM Strategy_Priorities WHERE ListType=?', (LIST,)).fetchall() == [(STRATEGY,)]
    assert db.execute('SELECT ConditionFunction,StringValue,ThresholdValue FROM StrategyConditions WHERE StrategyType=?', (STRATEGY,)).fetchall() == [('Call Lua Function', CALLBACK, 1)]
    assert db.execute('SELECT NumConditionsNeeded FROM Strategies WHERE StrategyType=?', (STRATEGY,)).fetchall() == [(1,)]
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='DefaultYieldBias' AND Item='YIELD_CSC_AI_PLACEMENT'").fetchall() == [(25,)]
    result.update(test=TEST, arm=arm, identical_native_definitions=True,
                  preference_owner='Strategy ONLY; no trait or agenda binding',
                  expected_callback_active=arm == 'on')
    return result


class StrategyYieldRunner(channel.CustomYieldRunner):
    def pin_sources(self):
        super().pin_sources()
        p = self.out / 'tuning-source-hashes.json'
        pins = read(p)
        pins[str(Path(__file__))] = sha(Path(__file__))
        write(p, pins)

    def archive_version(self):
        super().archive_version()
        p = self.out / 'source-version/version.json'
        v = read(p)
        v.update(code_version=VERSION, test=TEST, analyzed_rounds=8,
                 civic_attachments_identical=True, native_SQL_identical=True,
                 no_custom_yield_preferences=False, no_material_condition=True,
                 strategy=STRATEGY, yield_list=LIST, system='Yields',
                 preference={'favored': 0, 'value': 100},
                 callback_active=self.arm == 'on')
        write(p, v)
        (p.parent / 'applied-callback.lua').write_bytes(callback_bytes(self.arm))

    def observe(self):
        self.guard_check('guard-before')
        data = dormant.base.RSTRunner.observe(self)
        self.guard_check('guard-after')
        log = (self.out / 'native-logs/AI_Victories.csv').read_text(errors='replace')
        active = self.arm == 'on'
        first = data['native']['first_true'] or {}
        calls = data['native']['calls'] or {}
        following = {}
        for pid in range(1, 6):
            key = str(pid) + ':1'
            assert calls.get(key, 0) > 0, 'Callback never reached for ' + key
            assert (key in first) is active
            turns = [int(t) for t in re.findall(r'^\s*(\d+),\s*' + str(pid) + r',\s*' + STRATEGY + r',\s*Following\s*$', log, re.M)]
            assert bool(turns) is active, 'Following differs from intended condition for ' + key
            following[pid] = {'callback_calls': calls[key], 'first_true': first.get(key),
                              'following_turns': turns}
        write(self.out / 'strategy-activation-validation.json', {
            'passed': True, 'expected_active': active, 'per_player': following,
            'does_not_establish_yield_or_civic_consumption': True})
        return data


def comparison(root):
    result = original_comparison(root)
    scores = {a: dormant.base.score_rows(root / a / 'native-logs/AI_GovtPolicies.csv', 71, 78) for a in ('off', 'on')}
    common = scores['off'].keys() & scores['on'].keys()
    target = [k for k in common if k[2] == dormant.base.TARGET]
    result.update(code_version=VERSION, test=TEST,
                  matched_records_all_eight_rounds=len(common),
                  different_records_all_eight_rounds=sum(scores['off'][k] != scores['on'][k] for k in common),
                  target_score_changes_by_turn={t: sum(scores['off'][k] != scores['on'][k] for k in target if k[0] == t) for t in range(71,79)},
                  any_target_strategy_response=any(scores['off'][k] != scores['on'][k] for k in target),
                  activation={a: read(root / a / 'strategy-activation-validation.json') for a in ('off', 'on')},
                  limits=['Constant-condition callback control, not material gating or natural performance.',
                          'Callback and Following alone do not establish Yields consumer response.'])
    return result


if __name__ == '__main__':
    dormant.VERSION = VERSION
    dormant.TEST = TEST
    dormant.ROUNDS = 8
    dormant.MODIFIER_YIELDS = (YIELD, YIELD)
    dormant.PAIR_TABLE = None
    dormant.pair_additions = lambda: set()
    dormant.overlay = overlay
    dormant.callback_bytes = callback_bytes
    dormant.native_check = native_check
    dormant.ModifierRunner = StrategyYieldRunner
    dormant.comparison = comparison
    dormant.main()
