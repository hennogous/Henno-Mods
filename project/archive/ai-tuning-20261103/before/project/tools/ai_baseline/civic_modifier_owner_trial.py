"""C2A: does a native civic-modifier OWNER requirement affect forecasting?

One unambiguous native requirement first: player owns Tailors' Quarter. Common
fixture cases also distinguish Base availability for subsequent tests. Do not
interpret this Quarter-only gate as material-aware or adjacency-aware guidance.
"""
from pathlib import Path
import re

import civic_modifier_trial as dormant
from paired_standard import HERE, read, sha
from run import write

VERSION = 'civic-modifiers-owner-quarter-gate-v2-order-safe'
TEST = 'C2A-owner-quarter-forecast'
OWNER = 'CSC_TEST_CIVIC_MODIFIER_OWNER_QUARTER'
FIXTURE = HERE / 'civic_modifier_material_fixture.lua'
original_overlay = dormant.overlay
original_native_check = dormant.native_check
original_comparison = dormant.comparison


def overlay(arm):
    return original_overlay(arm) + """
INSERT OR IGNORE INTO Requirements (RequirementId,RequirementType) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_HAS_TAILOR','REQUIREMENT_PLAYER_HAS_DISTRICT');
INSERT OR IGNORE INTO RequirementArguments (RequirementId,Name,Value) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_HAS_TAILOR','DistrictType','DISTRICT_CSC_TAILORS_QUARTER');
INSERT OR IGNORE INTO RequirementSets (RequirementSetId,RequirementSetType) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_OWNER_QUARTER','REQUIREMENTSET_TEST_ALL');
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId,RequirementId) VALUES
 ('CSC_TEST_CIVIC_MODIFIER_OWNER_QUARTER','CSC_TEST_CIVIC_MODIFIER_HAS_TAILOR');
UPDATE Modifiers SET OwnerRequirementSetId='CSC_TEST_CIVIC_MODIFIER_OWNER_QUARTER'
 WHERE ModifierId IN ('CSC_TEST_CIVIC_MODIFIER_PRODUCTION','CSC_TEST_CIVIC_MODIFIER_FOOD');
"""


def native_check(db, arm, patch, source, with_rst=False):
    result = original_native_check(db, arm, patch, source, with_rst)
    assert db.execute('SELECT ModifierId,OwnerRequirementSetId FROM Modifiers WHERE ModifierId IN (?,?) ORDER BY ModifierId', dormant.MODS).fetchall() == sorted((m, OWNER) for m in dormant.MODS)
    assert db.execute('SELECT RequirementId FROM RequirementSetRequirements WHERE RequirementSetId=?', (OWNER,)).fetchall() == [('CSC_TEST_CIVIC_MODIFIER_HAS_TAILOR',)]
    assert db.execute("SELECT RequirementType,Inverse FROM Requirements WHERE RequirementId='CSC_TEST_CIVIC_MODIFIER_HAS_TAILOR'").fetchall() == [('REQUIREMENT_PLAYER_HAS_DISTRICT', 0)]
    assert db.execute("SELECT Name,Value FROM RequirementArguments WHERE RequirementId='CSC_TEST_CIVIC_MODIFIER_HAS_TAILOR'").fetchall() == [('DistrictType', 'DISTRICT_CSC_TAILORS_QUARTER')]
    result.update(test=TEST, owner_requirement='Has Tailors Quarter; no material predicate yet')
    return result


class OwnerRunner(dormant.ModifierRunner):
    def pin_sources(self):
        super().pin_sources()
        p = self.out / 'tuning-source-hashes.json'
        pins = read(p)
        for f in (Path(__file__), FIXTURE):
            pins[str(f)] = sha(f)
        write(p, pins)

    def archive_version(self):
        super().archive_version()
        p = self.out / 'source-version/version.json'
        v = read(p)
        v.update(code_version=VERSION, test=TEST, owner_requirement=OWNER,
                 fixture_cases={1: 'NoQuarter/ownedFlax', 2: 'Quarter/noBase',
                                3: 'Quarter/unimprovedBase', 4: 'Quarter/improvedBase',
                                5: 'Quarter/improvedBase'},
                 expected_quarter_gate={p: p != 1 for p in range(1, 6)})
        write(p, v)

    def observe(self):
        self.fixture_path = FIXTURE
        return super().observe()

    def after_fixture(self):
        code = """
CSC_AI_Research.Invalidate();
for pid=1,5 do
 local row=CSC_AI_Research.Scan(pid);local q=0;
 for _,site in ipairs(row.sites) do if site.quarter=='TAILORS' then q=q+1 end end;
 local owned=0;for i=0,Map.GetPlotCount()-1 do local p=Map.GetPlotByIndex(i);if p:GetOwner()==pid and p:GetResourceType()==GameInfo.Resources.RESOURCE_CSC_FLAX.Index then owned=owned+1 end end;
 local ready=row.active[5]==true;
 assert((q>0)==(pid~=1),'Quarter fixture mismatch '..pid);
 assert(ready==(pid>=3),'Potential-material eligibility mismatch '..pid);
 print('CSC_C2_CASE',pid,q,tostring(ready),owned);
end;
"""
        text = self.cmd(code, 'CSC_AI_Research', 'material-case-validation', wait=3)
        cases = [{'player': int(p), 'quarters': int(q), 'potential_base_ready': ready == 'true', 'owned_flax_plots': int(n)}
                 for p, q, ready, n in re.findall(r'CSC_C2_CASE\s+(\d+)\s+(\d+)\s+(true|false)\s+(\d+)', text)]
        assert len(cases) == 5
        if self.arm == 'on':
            assert cases == read(self.out.parent / 'off/material-case-validation.json')['cases']
        write(self.out / 'material-case-validation.json', {'passed': True, 'cases': cases})


def comparison(root):
    result = original_comparison(root)
    cases = read(root / 'on/material-case-validation.json')['cases']
    deltas = {}
    for pid, values in result['initial_targets'].items():
        assert values['off'] and values['on']
        deltas[int(pid)] = float(values['on'][0]) - float(values['off'][0])
    expected = {p: p != 1 for p in range(1, 6)}
    result.update(code_version=VERSION, test=TEST, material_cases=cases,
                  initial_target_deltas=deltas, expected_quarter_gate=expected,
                  owner_gate_selective=all((abs(deltas[p]) > 0.05) == expected[p] for p in expected),
                  note='This tests a native Quarter OWNER requirement, not resource ownership or exact adjacency.')
    return result


if __name__ == '__main__':
    dormant.VERSION = VERSION
    dormant.TEST = TEST
    dormant.overlay = overlay
    dormant.native_check = native_check
    dormant.ModifierRunner = OwnerRunner
    dormant.comparison = comparison
    dormant.main()
