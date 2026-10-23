"""C4A: can a dedicated internal yield reach civic research valuation?

Static consumer control only, not a conditional strategy. Same registered yield,
DefaultValue=1, dormant capital-modifier definitions in both fresh worlds. Only
two CivicModifiers attachments differ. No existing placement channel is changed.
"""
import json
import shutil
from pathlib import Path

import civic_modifier_trial as dormant
from paired_standard import read, sha
from run import SAVES, write

VERSION = 'civic-modifiers-custom-yield-consumer-v2-pristine-world'
TEST = 'C4A-dedicated-yield-civic-consumer'
YIELD = 'YIELD_CSC_TEST_CIVIC_GUIDANCE'
original_overlay = dormant.overlay
original_native_check = dormant.native_check


def overlay(arm):
    return original_overlay(arm) + """
INSERT OR IGNORE INTO Types (Type,Kind) VALUES
 ('YIELD_CSC_TEST_CIVIC_GUIDANCE','KIND_YIELD');
INSERT OR IGNORE INTO Yields (YieldType,Name,IconString,OccupiedCityChange,DefaultValue) VALUES
 ('YIELD_CSC_TEST_CIVIC_GUIDANCE','LOC_CSC_TEST_CIVIC_GUIDANCE','',0,1);
UPDATE ModifierArguments SET Value='YIELD_CSC_TEST_CIVIC_GUIDANCE'
 WHERE ModifierId IN ('CSC_TEST_CIVIC_MODIFIER_PRODUCTION','CSC_TEST_CIVIC_MODIFIER_FOOD') AND Name='YieldType';
"""


def native_check(db, arm, patch, source, with_rst=False):
    result = original_native_check(db, arm, patch, source, with_rst)
    assert db.execute('SELECT Kind FROM Types WHERE Type=?', (YIELD,)).fetchall() == [('KIND_YIELD',)]
    assert db.execute('SELECT Name,IconString,OccupiedCityChange,DefaultValue FROM Yields WHERE YieldType=?', (YIELD,)).fetchall() == [('LOC_CSC_TEST_CIVIC_GUIDANCE', '', 0, 1)]
    assert not db.execute('SELECT * FROM AiFavoredItems WHERE Item=?', (YIELD,)).fetchall()
    assert not db.execute('SELECT ModifierId,OwnerRequirementSetId FROM Modifiers WHERE ModifierId IN (?,?) AND OwnerRequirementSetId IS NOT NULL', dormant.MODS).fetchall()
    result.update(test=TEST, custom_yield=YIELD, default_value=1,
                  no_custom_yield_preferences=True, total_dormant_amount=200)
    return result


class CustomYieldRunner(dormant.ModifierRunner):
    def start_pair(self, i, resume_map=False):
        if self.arm == 'on':
            # A fresh same-seed world changed resources AND start positions.
            # Reuse the exact unplayed OFF world instead of normalizing it.
            # Native preflight below must independently see the ON definitions.
            meta = read(self.out.parent / 'off/game-01/initial-save.json')
            archive = self.out.parent / 'off/game-01' / Path(meta['path']).name
            assert sha(archive) == meta['sha256']
            native = SAVES / 'CSC_C4_PrIstine_20261020.Civ6Save'
            shutil.copy2(archive, native)
            assert sha(native) == meta['sha256']
            self.select_mods(False)
            self.cmd('Automation.SetAutoStartEnabled(true);Network.LoadGame(' + json.dumps(str(native)) + ',ServerType.SERVER_TYPE_NONE);',
                     'MainMenu', 'start-c4-pristine-load', wait=5, check=False)
            self.resume_origin = self.out.parent / 'off'
            write(self.out / 'same-world-provenance.json', {
                'pristine_origin': str(archive), 'sha256': meta['sha256'],
                'native_copy': str(native), 'turn': 71, 'no_fixture_in_save': True,
                'source': 'OFF native world; not independently regenerated',
                'interpretation_gate': 'Native DB current ON rows plus exact world/census parity; null requires stock-yield reload positive control.'})
        return super().start_pair(i, resume_map)

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
        v.update(code_version=VERSION, test=TEST, dedicated_yield=YIELD,
                 default_value=1, no_custom_yield_preferences=True,
                 total_dormant_amount=200, owner_requirement=None,
                 fixture='Original identical coastal Tailor/Flax/Workshop/Harbor/Lighthouse fixture, all five players')
        write(p, v)


if __name__ == '__main__':
    dormant.VERSION = VERSION
    dormant.TEST = TEST
    dormant.MODIFIER_YIELDS = (YIELD, YIELD)
    dormant.overlay = overlay
    dormant.native_check = native_check
    dormant.ModifierRunner = CustomYieldRunner
    dormant.main()
