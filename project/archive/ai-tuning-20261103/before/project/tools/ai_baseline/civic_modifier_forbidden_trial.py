"""C12: Forbidden inverse condition instead of one-way Disqualifier.

Grounded by RH_Naval.sql / RH_Era_Strat.sql Forbidden conditions. All weights,
material predicates, exact-world pairing and independent C11v2 phase events
are held fixed. This asks whether native eligibility can withdraw AND return.
"""
from pathlib import Path
import shutil
import civic_modifier_trial as dormant
import civic_modifier_neutral_yield_trial as neutral
import civic_modifier_strategy_yield_trial as strategy
import civic_modifier_inert_guard_trial as guard
import civic_modifier_lifecycle_trial as life
import civic_modifier_disqualifier_trial as disq
from paired_standard import read,sha
from run import write

VERSION='civic-modifiers-reversible-forbidden-condition-v1'
TEST='C12-inverse-readiness-forbidden'
REFERENCE=dormant.RH_CIVICS.parents[1]/'RH_Naval.sql'


def overlay(arm):
    return disq.overlay(arm)+"""
UPDATE StrategyConditions SET Disqualifier=0,Forbidden=1
 WHERE StrategyType='STRATEGY_CSC_TEST_CIVIC_YIELD' AND Exclusive=1;
"""


def native_check(db,arm,patch,source,with_rst=False):
    result=guard.native_check(db,arm,patch,source,with_rst)
    assert db.execute('SELECT ThresholdValue,Forbidden,Disqualifier,Exclusive FROM StrategyConditions WHERE StrategyType=? ORDER BY Exclusive',(strategy.STRATEGY,)).fetchall()==[(1,0,0,0),(2,1,0,1)]
    result.update(test=TEST,explicit_inverse_forbidden=True,permanent_disqualifier=False,
                  reference='RH_Naval.sql Cities Under Threat Forbidden=1')
    return result


class ForbiddenRunner(disq.DisqualifierRunner):
    def pin_sources(self):
        super().pin_sources();p=self.out/'tuning-source-hashes.json';pins=read(p)
        for f in (Path(__file__),REFERENCE):pins[str(f)]=sha(f)
        write(p,pins)

    def archive_version(self):
        super().archive_version();p=self.out/'source-version/version.json';v=read(p)
        v.update(code_version=VERSION,test=TEST,explicit_inverse_readiness_disqualifier=False,
                 explicit_inverse_forbidden=True,condition_change='Secondary Forbidden1/Disqualifier0, primary unchanged',
                 inherited_telemetry_names='disqualifier_history/validation now identify inverse condition callback; native flag is Forbidden, not Disqualifier')
        dest=p.parent/'rh-readonly-examples'/REFERENCE.name;shutil.copy2(REFERENCE,dest)
        v['rh_example_hashes'][REFERENCE.name]=sha(dest);write(p,v)


def comparison(root):
    result=disq.comparison(root)
    delta=result['target_deltas_by_turn']
    result.update(code_version=VERSION,test=TEST,explicit_inverse_disqualifier=False,explicit_inverse_forbidden=True,
        phase_score_samples={t:delta[t] for t in (72,74,75,76,78,79,82,83,84,85,86)},
        first_cycle_clean_withdrawal75_76=all(all(abs(delta[t].get(pid,99999))<.05 for pid in (3,4)) for t in (75,76)),
        returned_signal79={pid:delta[79].get(pid) for pid in (3,4)},
        measured_C11_timing='Native turn-event loss73, inverse callback74, zero score75. Reacquisition77 needs evaluation78/score79; do not demand premature78 response.',
        limits=['Native Forbidden differs from Disqualifier; no new weights.',
                'One controlled save-derived diagnostic pair, not natural performance.',
                'Later world/research divergence can confound exact paired score residuals.',
                'Completion, ownership, reload, duplicates, UI and release tuning still gated.'])
    return result


if __name__=='__main__':
    dormant.VERSION=VERSION;dormant.TEST=TEST;dormant.ROUNDS=life.ROUNDS
    dormant.MODIFIER_YIELDS=(neutral.YIELD,neutral.YIELD);dormant.GUARD_REQUIREMENT_COUNT=5
    neutral.STRATEGY_CONDITION_ROWS=[('Call Lua Function',strategy.CALLBACK,1),('Call Lua Function',strategy.CALLBACK,2)]
    dormant.PAIR_TABLE='CivicModifiers';dormant.PAIR_COLUMNS='CivicType,ModifierId'
    dormant.pair_additions=lambda:{(dormant.base.TARGET,m) for m in dormant.MODS}
    dormant.overlay=overlay;dormant.callback_bytes=disq.callback_bytes;dormant.native_check=native_check
    dormant.ModifierRunner=ForbiddenRunner;dormant.comparison=comparison
    dormant.main()
