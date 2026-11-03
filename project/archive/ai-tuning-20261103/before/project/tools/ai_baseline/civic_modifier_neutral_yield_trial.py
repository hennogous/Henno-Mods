"""C8: zero idle signal and restore it through material-ready strategy.

Both arms define static DefaultYieldBias=-100 and strategy Yields=+100 on the
dedicated channel, whose DefaultValue stays1. OFF has no civic attachment and
disabled callback. ON attaches the dormant benefit and enables real readiness.
This is a candidate-versus-no-signal contrast: two combined changes, explicitly
not a one-factor preference experiment. No assumption about percentage stacking.
"""
from pathlib import Path

import civic_modifier_trial as dormant
import civic_modifier_custom_yield_trial as channel
import civic_modifier_strategy_yield_trial as strategy
import civic_modifier_material_yield_trial as material
from paired_standard import read, sha
from run import write

VERSION = 'civic-modifiers-idle-neutral-material-signal-v1'
TEST = 'C8-neutral-idle-material-restoration'
YIELD = strategy.YIELD
STRATEGY_CONDITION_ROWS = [('Call Lua Function',strategy.CALLBACK,1)]


def overlay(arm):
    text = material.overlay(arm) + """
DELETE FROM AiFavoredItems WHERE ListType='DefaultYieldBias' AND Item='YIELD_CSC_TEST_CIVIC_GUIDANCE';
INSERT INTO AiFavoredItems (ListType,Item,Favored,Value) VALUES
 ('DefaultYieldBias','YIELD_CSC_TEST_CIVIC_GUIDANCE',0,-100);
DELETE FROM CivicModifiers WHERE ModifierId IN ('CSC_TEST_CIVIC_MODIFIER_PRODUCTION','CSC_TEST_CIVIC_MODIFIER_FOOD');
"""
    if arm == 'on':
        text += '\nINSERT INTO CivicModifiers (CivicType,ModifierId) VALUES\n'
        text += ',\n'.join("('"+dormant.base.TARGET+"','"+m+"')" for m in dormant.MODS)+';\n'
    return text


def callback_bytes(arm):
    return material.callback_bytes(arm)


def native_check(db, arm, patch, source, with_rst=False):
    result = channel.original_native_check(db, arm, patch, source, with_rst)
    assert db.execute('SELECT Kind FROM Types WHERE Type=?',(YIELD,)).fetchall()==[('KIND_YIELD',)]
    assert db.execute('SELECT DefaultValue FROM Yields WHERE YieldType=?',(YIELD,)).fetchall()==[(1,)]
    assert db.execute('SELECT ListType,Favored,Value FROM AiFavoredItems WHERE Item=? ORDER BY ListType',(YIELD,)).fetchall()==sorted([(strategy.LIST,0,100),('DefaultYieldBias',0,-100)])
    assert db.execute('SELECT LeaderType,AgendaType,System FROM AiLists WHERE ListType=?',(strategy.LIST,)).fetchall()==[(None,None,'Yields')]
    assert db.execute("SELECT LeaderType,AgendaType,System FROM AiLists WHERE ListType='DefaultYieldBias'").fetchall()==[('TRAIT_LEADER_MAJOR_CIV',None,'Yields')]
    assert db.execute('SELECT StrategyType FROM Strategy_Priorities WHERE ListType=?',(strategy.LIST,)).fetchall()==[(strategy.STRATEGY,)]
    assert db.execute('SELECT ConditionFunction,StringValue,ThresholdValue FROM StrategyConditions WHERE StrategyType=? ORDER BY Exclusive',(strategy.STRATEGY,)).fetchall()==STRATEGY_CONDITION_ROWS
    assert db.execute("SELECT Value FROM AiFavoredItems WHERE ListType='DefaultYieldBias' AND Item='YIELD_CSC_AI_PLACEMENT'").fetchall()==[(25,)]
    result.update(test=TEST,static_bias=-100,active_strategy_bias=100,
                  comparison='No attachments/callback disabled versus attached benefit/material callback enabled',
                  stacking_semantics='Measured by scoring; not assumed')
    return result


class NeutralYieldRunner(material.MaterialYieldRunner):
    def pin_sources(self):
        super().pin_sources()
        p=self.out/'tuning-source-hashes.json';pins=read(p)
        pins[str(Path(__file__))]=sha(Path(__file__));write(p,pins)

    def archive_version(self):
        super().archive_version()
        p=self.out/'source-version/version.json';v=read(p)
        v.update(code_version=VERSION,test=TEST,civic_attachments_identical=False,
                 native_SQL_identical=False,static_bias=-100,active_strategy_bias=100,
                 candidate_combined_treatment=True,
                 only_native_difference='Two CivicModifiers attachments',
                 callback_condition_difference='OFF disabled; ON actual Quarter/material eligibility',
                 lifecycle_not_tested=True)
        write(p,v)


def comparison(root):
    result=material.comparison(root)
    result.update(code_version=VERSION,test=TEST,
                  candidate_combined_treatment=True,
                  initial_no_signal_parity=len(result['initial_changes'])==0,
                  neutral_unready_at72=all(abs(result['target_deltas_by_turn'][72].get(p,99999))<0.05 for p in (1,2)),
                  restores_ready_at72=all(result['target_deltas_by_turn'][72].get(p,0)>0.05 for p in (3,4,5)),
                  limits=['Two combined candidate changes: attachments plus callback enablement; not isolated effect of each.',
                          'Compare neutral unready scores directly against matched no-attachment reference.',
                          'Real readiness, native strategy and score response measured; lifecycle and guaranteed-inert guard still pending.'])
    return result


if __name__=='__main__':
    dormant.VERSION=VERSION
    dormant.TEST=TEST
    dormant.ROUNDS=8
    dormant.MODIFIER_YIELDS=(YIELD,YIELD)
    dormant.PAIR_TABLE='CivicModifiers'
    dormant.PAIR_COLUMNS='CivicType,ModifierId'
    dormant.pair_additions=lambda:{(dormant.base.TARGET,m) for m in dormant.MODS}
    dormant.overlay=overlay
    dormant.callback_bytes=callback_bytes
    dormant.native_check=native_check
    dormant.ModifierRunner=NeutralYieldRunner
    dormant.comparison=comparison
    dormant.main()
