"""C5: does a static native Yields preference tune a dedicated civic signal?

Both arms attach the same dormant custom-yield benefit to Divine Right. The
only difference is one new DefaultYieldBias row, Favored=0/Value=100, for that
dedicated yield. Eight rounds allow preference refresh. ON loads exact OFF
pristine world. A null remains subject to saved Yields-state caching; it is not
proof that a fresh-player consumer ignores these preferences.
"""
from pathlib import Path

import civic_modifier_trial as dormant
import civic_modifier_custom_yield_trial as channel
from paired_standard import read, sha
from run import write

VERSION = 'civic-modifiers-static-yield-preference-v1'
TEST = 'C5-static-dedicated-yield-preference'
YIELD = channel.YIELD
VALUE = 100


def overlay(arm):
    text = channel.overlay('on')
    text += "\nDELETE FROM AiFavoredItems WHERE Item='" + YIELD + "';\n"
    if arm == 'on':
        text += "INSERT INTO AiFavoredItems (ListType,Item,Favored,Value) VALUES ('DefaultYieldBias','" + YIELD + "',0,100);\n"
    return text


def native_check(db, arm, patch, source, with_rst=False):
    # Both arms intentionally have the SAME civic attachments. Original dormant
    # validator checks full definitions/replay; new contrast is preference only.
    result = channel.original_native_check(db, 'on', patch, source, with_rst)
    assert db.execute('SELECT Kind FROM Types WHERE Type=?', (YIELD,)).fetchall() == [('KIND_YIELD',)]
    assert db.execute('SELECT DefaultValue FROM Yields WHERE YieldType=?', (YIELD,)).fetchall() == [(1,)]
    assert db.execute("SELECT LeaderType,AgendaType,System FROM AiLists WHERE ListType='DefaultYieldBias'").fetchall() == [('TRAIT_LEADER_MAJOR_CIV', None, 'Yields')]
    expected = [('DefaultYieldBias', 0, VALUE)] if arm == 'on' else []
    assert db.execute('SELECT ListType,Favored,Value FROM AiFavoredItems WHERE Item=?', (YIELD,)).fetchall() == expected
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='DefaultYieldBias' AND Item='YIELD_CSC_AI_PLACEMENT'").fetchall() == [(25,)]
    result.update(test=TEST, arm=arm, custom_yield=YIELD, default_value=1,
                  static_yield_preferences=expected, civic_attachments_identical=True,
                  no_strategy_or_material_condition=True)
    return result


class PreferenceRunner(channel.CustomYieldRunner):
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
                 civic_attachments_identical=True, no_strategy_or_material_gate=True,
                 no_custom_yield_preferences=self.arm == 'off',
                 static_preference={'list': 'DefaultYieldBias', 'system': 'Yields',
                                    'trait': 'TRAIT_LEADER_MAJOR_CIV', 'item': YIELD,
                                    'favored': 0, 'value': VALUE, 'present': self.arm == 'on'},
                 interpretation='Only a score response proves this saved-player preference consumer; a null may reflect serialized Yields state.')
        write(p, v)

    def observe(self):
        # Eight rounds may complete the target. The impossible Future-Civic
        # guard, rather than target nonownership, guarantees no real bonus.
        self.guard_check('guard-before')
        data = dormant.base.RSTRunner.observe(self)
        self.guard_check('guard-after')
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
                  any_target_preference_response=any(scores['off'][k] != scores['on'][k] for k in target),
                  limits=['Same pristine world, ON under changed Yields preference; no actual economic bonus.',
                          'Static preference response does not prove strategy or material gating.',
                          'A null cannot by itself exclude serialized saved-player Yields state.'])
    return result


original_comparison = dormant.comparison

if __name__ == '__main__':
    dormant.VERSION = VERSION
    dormant.TEST = TEST
    dormant.ROUNDS = 8
    dormant.MODIFIER_YIELDS = (YIELD, YIELD)
    dormant.PAIR_TABLE = 'AiFavoredItems'
    dormant.PAIR_COLUMNS = 'ListType,Item,Favored,Value'
    dormant.pair_additions = lambda: {('DefaultYieldBias', YIELD, 0, VALUE)}
    dormant.overlay = overlay
    dormant.native_check = native_check
    dormant.ModifierRunner = PreferenceRunner
    dormant.comparison = comparison
    dormant.main()
