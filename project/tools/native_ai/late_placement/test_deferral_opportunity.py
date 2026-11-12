"""Bound the one world edit and require actual fresh native choice+request."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from lupa.lua51 import LuaRuntime
from deferral_opportunity import TRANSFER,qualify_before,qualify_after,quarter_request_after,parse_snapshot


def snapshot():
    return dict(turn=204,mutationCommands=0,hasQuarter=False,city=dict(population=9,currentItem=123),
        supplier=dict(plot=471,owner=11,city=65536,resource=54,resourceType='RESOURCE_CSC_FLAX',
            improvement=1,improvementType='IMPROVEMENT_FARM',pillaged=False,terrain=2,feature=-1,
            resourceCount=1,riverEdges=0,mappedBase=True,revealed=True,resourceVisible=True),
        sites=[dict(plot=397,owner=-1,city=-1,legal=True,district=-1,supplierDistance=1,
            base=[],model=dict(declineNoBase=True),declineReceipt='{"staged":1}')])


class Opportunity(unittest.TestCase):
    def test_source_requires_free_legal_adjacent_footprint(self):
        before=snapshot();self.assertEqual(qualify_before(before)['free_sites'],[397])
        before['sites'][0]['district']=31
        with self.assertRaisesRegex(AssertionError,'No free legal'):qualify_before(before)

    def test_after_requires_main_supply_and_no_artificial_queue_change(self):
        before=snapshot();after=deepcopy(before);after['supplier'].update(owner=1,city=524295)
        after['sites'][0].update(base=[dict(plot=471)],model={})
        self.assertEqual(qualify_after(before,after),[397])
        after['city']['currentItem']=999
        with self.assertRaises(AssertionError):qualify_after(before,after)

    def test_fresh_choice_alone_or_old_request_is_not_success(self):
        event=dict(kind='selection',turn=211,winner=dict(district=36,x=27,y=5,q8=123))
        request='211, 1, LOC_CITY_NAME_NICOPOLIS, , CONTRACT 5000, SUBMITTED, NO_UNIT, NO_BUILDING, DISTRICT_CSC_BAKERS_QUARTER, VALUE 123.0, Build City District'
        self.assertIsNone(quarter_request_after('',[event]))
        self.assertIsNone(quarter_request_after(request.replace('211,','203,'),[event]))
        native=dict(k='best',generation=20,version=11,player=1,city=524295,district=36,plot=397,result=123)
        log=('CSC_AI_BAKERS_DISTRICTS turn=211 version=11\n'
            'CSC_DEFERRAL_TRACKED_BASE\t211\t11\t397\t471\ttrue\ttrue\n'
            'CSC_DEFERRAL_TRACKED_SUPPLIER\t211\t11\t1\t524295\t54\t1\tfalse\n'
            'CSC_DEFERRAL_DECLINE_PREVIOUS\t212\t11\t397\t{"staged":0}\n'
            'CSC_HOST_PREFIX_BEGIN\t212\t20\t11\t1\n'
            'CSC_HOST_NATIVE\t212\t20\t0\t'+json.dumps(native)+'\n'
            'CSC_HOST_PREFIX_END\t212\t20\t11\t1\n')
        self.assertEqual(quarter_request_after(request,[event],{397},log)['selection'],event)
        self.assertIsNone(quarter_request_after(request,[event],{398},log))
        self.assertIsNone(quarter_request_after(request,[event],{397},log.replace('"staged":0','"staged":1')))
        self.assertIsNone(quarter_request_after(request,[event,event],{397},log))
        self.assertIsNone(quarter_request_after(request,[event],{397},log.replace('CSC_HOST_PREFIX_END','CLIPPED_END')))
        with self.assertRaisesRegex(AssertionError,'reader failed'):
            quarter_request_after(request,[event],{397},log+'CSC_HOST_DIAG_FAILED\tbroken\n')

    def test_snapshot_framing_rejects_missing_duplicate_or_clipped_chunks(self):
        payload=json.dumps(dict(turn=204,city='fixture'));pieces=[payload[:10],payload[10:]]
        raw='\n'.join('CSC_DEFERRAL_OPPORTUNITY_CHUNK\t204\t%d\t2\t%s'%(i,p)for i,p in enumerate(pieces,1))
        raw+='\nCSC_DEFERRAL_OPPORTUNITY_END\t204\t2\t'+str(len(payload))
        self.assertEqual(parse_snapshot(raw)['turn'],204)
        for bad in(raw.replace(pieces[1],pieces[1][:-1]),raw+'\n'+raw.splitlines()[0],raw.replace('\t1\t2\t','\t2\t2\t')):
            with self.assertRaises(AssertionError):parse_snapshot(bad)

    def test_inspector_compiles_and_transfer_changes_only_ownership(self):
        vm=LuaRuntime();vm.eval('function(s)assert(loadstring(s))end')(
            Path(__file__).with_name('deferral_opportunity_inspect.lua').read_text())
        vm.execute('''turn=204;owner=11;ownerCity=65536;writes=0;inspections=0
print=function()end
Game={GetCurrentGameTurn=function()return turn end,GetLocalPlayer=function()return 0 end}
AutoplayManager={IsActive=function()return false end}
Players={[0]={IsHuman=function()return true end},[1]={IsHuman=function()return false end,
 GetTreasury=function()return {GetGoldBalance=function()return 50 end}end}}
city={GetID=function()return 524295 end,GetName=function()return 'LOC_CITY_NAME_NICOPOLIS'end,
 GetPopulation=function()return 9 end,GetBuildQueue=function()return {CurrentlyBuilding=function()return 123 end}end}
CityManager={GetCity=function()return city end}
GameInfo={Resources={RESOURCE_CSC_FLAX={Index=54}},Improvements={IMPROVEMENT_FARM={Index=1}}}
supplier={GetOwner=function()return owner end,GetResourceType=function()return 54 end,
 GetImprovementType=function()return 1 end,GetDistrictType=function()return -1 end,
 GetTerrainType=function()return 2 end,GetFeatureType=function()return -1 end,
 IsImprovementPillaged=function()return false end,GetRiverCrossingCount=function()return 0 end,
 GetX=function()return 27 end,GetY=function()return 6 end}
local free={GetOwner=function()return -1 end,GetDistrictType=function()return -1 end,
 CanHaveDistrict=function()return true end,GetX=function()return 27 end,GetY=function()return 5 end}
Map={GetPlotByIndex=function(i)return i==471 and supplier or free end,GetPlotDistance=function()return 1 end}
Cities={GetPlotPurchaseCity=function(p)if p==supplier then return {GetID=function()return ownerCity end}end end}
WorldBuilder={CityManager=function()return {SetPlotOwner=function(_,x,y,p,c)
 assert(x==27 and y==6 and p==1 and c==524295);writes=writes+1;owner=p;ownerCity=c end}end}
CSC_DEFERRAL_OPPORTUNITY_Inspect=function()inspections=inspections+1 end
''')
        vm.execute(TRANSFER)
        self.assertEqual(vm.eval('writes'),1);self.assertEqual(vm.eval('inspections'),1)
        with self.assertRaises(Exception):vm.execute(TRANSFER)
        self.assertEqual(vm.eval('writes'),1) # No duplicate/retry transfer.


if __name__=='__main__':unittest.main()
