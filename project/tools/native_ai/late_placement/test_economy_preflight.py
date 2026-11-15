"""Endpoint regression: a valid zero-output city must not reject recorded play."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from lupa.lua51 import LuaRuntime
from economy_preflight import inspect


class EconomyPreflightTests(unittest.TestCase):
    def qualify(self, production):
        class Controller:
            def cmd(self, code, context, label):
                if label == 'read-only-economy-preflight':
                    return 'CSC_ECONOMY_STATUS={"pricingReady":1,"finalReady":1}\nCSC_ECONOMY_PREFLIGHT_OK=1'
                if label == 'native-valuation-api-presence':
                    return 'CSC_NATIVE_VALUATION_API=false'
                assert label == 'read-only-economy-facts-preflight'
                vm = LuaRuntime()
                rows = []
                vm.globals().print = lambda *args: rows.append('\t'.join(map(str, args)))
                vm.execute('''
local city={GetID=function()return 65536 end}
local p={GetID=function()return 1 end,IsHuman=function()return false end}
p.GetCities=function()return {Members=function()
 local yielded=false;return function()if not yielded then yielded=true;return 1,city end end
end}end
PlayerManager={GetAliveMajors=function()return {p}end}
GameInfo={Yields={YIELD_PRODUCTION={Index=1}},Districts={DISTRICT_CSC_BAKERS_QUARTER={Index=42}}}
CSC_AI_QuarterPlacement={}
CSC_AI_EconomyFacts={New=function()return {
 Research=function()return 0 end,
 DistrictCapacity=function()return {known=true,population=8,used=1,allowed=3,reason='ready'}end
}end}
ExposedMembers={CSC_Adjacency={GetDistrictCapacity=function()end,
 GetEconomyCityNumber=function(owner,id,kind)
  if kind=='yield'then return ''' + production + ''' end;return 35
 end}}
''')
                vm.execute(code)
                return '\n'.join(rows)
        with TemporaryDirectory() as directory:
            inspect(Controller(), Path(directory))
            return (Path(directory) / 'economy-facts-preflight.txt').read_text(encoding='utf-8')

    def test_zero_and_positive_output_are_known_facts(self):
        for value in ('0', '25.5'):
            with self.subTest(value=value):
                self.assertIn('CSC_ECONOMY_FACTS_OK', self.qualify(value))

    def test_missing_or_negative_output_remains_rejected(self):
        for value in ('nil', '-1'):
            with self.subTest(value=value), self.assertRaisesRegex(Exception, 'Incomplete economic readiness facts'):
                self.qualify(value)
