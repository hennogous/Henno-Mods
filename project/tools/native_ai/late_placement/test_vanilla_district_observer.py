"""No-CSC controls retain event truth and reject contaminated rule databases."""
from pathlib import Path
from contextlib import closing
import sqlite3
import tempfile
import unittest
from lupa.lua51 import LuaRuntime
from test_planning_observer import FIXTURE
from vanilla_district_run import check_database


class VanillaObserver(unittest.TestCase):
    def setUp(self):
        self.lua=LuaRuntime(unpack_returned_tuples=True)
        self.lua.execute(FIXTURE+'''
CSC_AI_QuarterPlacement=nil
GameInfo.Districts.DISTRICT_CSC_BAKERS_QUARTER=nil
GameInfo.Districts[1].DistrictType='DISTRICT_HOLY_SITE'
GameInfo.Yields={}
Players[0].IsAlive=function()return true end
city.GetPopulation=function()return 7 end
CSC_VANILLA_SCOPE={players={0},through=250}
nativeStatus='{"ready":1,"enabled":0,"version":0,"entries":0,"matched":0,"changed":0,"faults":0,"managedTypes":0}'
CE_AIDistrictScoresStatus=function()return nativeStatus end
''')
        self.lua.execute(Path(__file__).with_name('vanilla_district_observer.lua').read_text(encoding='utf-8'))

    def rows(self,kind):
        return [s for s in self.lua.globals().logs.values()if s.startswith('CSC_PLANNING_'+kind+'\t')]

    def test_foundations_completions_and_ownership_are_distinct(self):
        self.lua.execute("Game.t=2;q=district(2,1,2,false);fire('DistrictAddedToMap',0,2,10,2,0,1);fire('DistrictAddedToMap',0,2,10,2,0,1);Game.t=3;q.complete=true;fire('DistrictBuildProgressChanged',0,2,10,2,0,1)")
        self.assertEqual(len(self.rows('FOUNDATION')),1)
        self.assertEqual(len(self.rows('COMPLETION')),1)
        self.lua.execute("Game.t=4;Players[1]=Players[0];q.id=42;fire('DistrictBuildProgressChanged',1,42,10,2,0,1)")
        self.assertEqual(len(self.rows('FOUNDATION')),1)
        self.assertEqual(len(self.rows('OWNERSHIP')),1)

    def test_periodic_census_and_native_policy_health(self):
        self.lua.execute("Game.t=25;poll();poll();CSC_VANILLA_DISTRICTS.Finish()")
        logs=list(self.lua.globals().logs.values())
        self.assertEqual(sum(s.startswith('CSC_FULL_RUN_CENSUS_BEGIN')for s in logs),1)
        self.assertTrue(any(s=='CSC_ENDPOINT_END\t25\t2'for s in logs))
        self.assertFalse(any('DISTRICT_FAULT'in s for s in logs))
        self.lua.execute("nativeStatus='{\"ready\":1,\"enabled\":1}'")
        self.assertIs(self.lua.eval('pcall(CSC_VANILLA_DISTRICTS.Health)')[0],False)

    def test_missed_event_is_not_invented_as_a_foundation(self):
        self.lua.execute("Game.t=2;q=district(2,1,2,false);poll()")
        self.assertEqual(len(self.rows('FOUNDATION')),0)
        self.assertEqual(len(self.rows('FIRST_OBSERVED')),2) # Seed center + missed new footprint.

    def test_baseline_database_rejects_csc_district_or_private_yield(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent)as directory:
            path=Path(directory)/'game.sqlite'
            with closing(sqlite3.connect(path))as db:
                db.executescript('CREATE TABLE Districts(DistrictType TEXT);CREATE TABLE Yields(YieldType TEXT);')
                db.execute("INSERT INTO Districts VALUES('DISTRICT_CAMPUS')")
                db.commit()
            self.assertTrue(check_database(path)['verified'])
            for table,column,value in [('Yields','YieldType','YIELD_CSC_AI_PLACEMENT'),
                                        ('Districts','DistrictType','DISTRICT_CSC_TAILORS_QUARTER')]:
                with closing(sqlite3.connect(path))as db:
                    db.execute('INSERT INTO '+table+' VALUES(?)',(value,));db.commit()
                with self.assertRaisesRegex(RuntimeError,'CSC SQL'):check_database(path)
                with closing(sqlite3.connect(path))as db:
                    db.execute('DELETE FROM '+table+' WHERE '+column+'=?',(value,));db.commit()


if __name__=='__main__':unittest.main()
