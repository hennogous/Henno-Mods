"""C9: C8 material guidance with a logically impossible economic guard.

The native ALL set requires Future Civic AND NOT Future Civic, independently
of era or AI status. Actual Service modifiers and real yields are untouched.
This diagnoses forecasting under a permanent contradiction, not performance.
"""
from pathlib import Path
import civic_modifier_trial as dormant
import civic_modifier_neutral_yield_trial as neutral
from paired_standard import read, sha
from run import write

VERSION='civic-modifiers-contradictory-economic-guard-v1'
TEST='C9-guaranteed-inert-material-signal'
INVERSE=dormant.PREFIX+'NOT_FUTURE'


def overlay(arm):
    return neutral.overlay(arm)+"""
INSERT OR IGNORE INTO Requirements (RequirementId,RequirementType,Inverse) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_NOT_FUTURE','REQUIREMENT_PLAYER_HAS_CIVIC',1);
INSERT OR IGNORE INTO RequirementArguments (RequirementId,Name,Value) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_NOT_FUTURE','CivicType','CIVIC_FUTURE_CIVIC');
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId,RequirementId) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_DORMANT','CSC_TEST_CIVIC_MODIFIER_NOT_FUTURE');
"""


def native_check(db,arm,patch,source,with_rst=False):
    result=neutral.native_check(db,arm,patch,source,with_rst)
    ids=(dormant.PREFIX+'FUTURE',INVERSE)
    assert db.execute('SELECT RequirementId,RequirementType,Inverse FROM Requirements WHERE RequirementId IN (?,?) ORDER BY RequirementId',ids).fetchall()==[
        (ids[0],'REQUIREMENT_PLAYER_HAS_CIVIC',0),(ids[1],'REQUIREMENT_PLAYER_HAS_CIVIC',1)]
    assert db.execute("SELECT RequirementId,Value FROM RequirementArguments WHERE RequirementId IN (?,?) AND Name='CivicType' ORDER BY RequirementId",ids).fetchall()==[(x,'CIVIC_FUTURE_CIVIC') for x in ids]
    assert db.execute('SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=? AND RequirementId IN (?,?) ORDER BY RequirementId',(dormant.PREFIX+'DORMANT',*ids)).fetchall()==[(x,) for x in ids]
    result.update(test=TEST,guaranteed_inert=True,contradiction='Future Civic AND NOT Future Civic under native ALL set')
    return result


class InertGuardRunner(neutral.NeutralYieldRunner):
    def pin_sources(self):
        super().pin_sources()
        p=self.out/'tuning-source-hashes.json';pins=read(p)
        pins[str(Path(__file__))]=sha(Path(__file__));write(p,pins)

    def archive_version(self):
        super().archive_version()
        p=self.out/'source-version/version.json';v=read(p)
        v.update(code_version=VERSION,test=TEST,guaranteed_inert_guard='Has Future Civic AND inverse Has Future Civic',
                 actual_services_changed=False,real_economic_benefit_possible=False)
        write(p,v)


def comparison(root):
    result=neutral.comparison(root)
    result.update(code_version=VERSION,test=TEST,guaranteed_inert_guard=True,
                  next_gate='Controlled readiness loss/reacquisition, target completion, duplicate/reload behavior and UI omission; no deployment yet')
    return result


if __name__=='__main__':
    dormant.VERSION=VERSION;dormant.TEST=TEST;dormant.ROUNDS=8
    dormant.MODIFIER_YIELDS=(neutral.YIELD,neutral.YIELD)
    dormant.GUARD_REQUIREMENT_COUNT=5
    dormant.PAIR_TABLE='CivicModifiers';dormant.PAIR_COLUMNS='CivicType,ModifierId'
    dormant.pair_additions=lambda:{(dormant.base.TARGET,m) for m in dormant.MODS}
    dormant.overlay=overlay;dormant.callback_bytes=neutral.callback_bytes
    dormant.native_check=native_check;dormant.ModifierRunner=InertGuardRunner
    dormant.comparison=comparison
    dormant.main()
