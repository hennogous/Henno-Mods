"""Diagnostic native-first2.1 comparison; no replacement shipping policy.

Both arms withhold Hamburg's optional positive CE customer-site offers.
Only the Harbor–Tailors native private-yield adjacency LINK differs.
Definitions, native indices, bias and all unrelated policy remain stable.
"""
from pathlib import Path
from contextlib import closing
import sqlite3
import xml.etree.ElementTree as ET
from driver import load,sha


def database_snapshot(path):
    """Read Firaxis's loaded-game DB export without changing its contents.

    This verifies SQL loading separately from GameInfo and native consumption.
    The selector matrix remains necessary: an exported row alone cannot prove
    an instance/cache updated or that the AI valued it. Capture before the next
    cold load replaces this diagnostic database.
    """
    path=Path(path).resolve(strict=True)
    with closing(sqlite3.connect(path.as_uri()+'?mode=ro',uri=True))as db:
        db.row_factory=sqlite3.Row
        def rows(sql,args=()):return[dict(r)for r in db.execute(sql,args)]
        return dict(database=str(path),mtime_ns=path.stat().st_mtime_ns,sha256=sha(path),
            links=rows('''SELECT d.DistrictType,d.YieldChangeId,a.YieldType,
                a.YieldChange,a.TilesRequired,a.AdjacentDistrict
                FROM District_Adjacencies d JOIN Adjacency_YieldChanges a ON a.ID=d.YieldChangeId
                WHERE a.YieldType=? ORDER BY d.DistrictType,d.YieldChangeId''',('YIELD_CSC_AI_PLACEMENT',)),
            rules=rows('''SELECT rowid,ID,YieldType,YieldChange,TilesRequired,AdjacentDistrict
                FROM Adjacency_YieldChanges WHERE YieldType=? ORDER BY ID''',('YIELD_CSC_AI_PLACEMENT',)),
            yields=rows('SELECT rowid,* FROM Yields WHERE YieldType=?',('YIELD_CSC_AI_PLACEMENT',)),
            biases=rows('SELECT * FROM AiFavoredItems WHERE ListType=? AND Item=?',
                ('DefaultYieldBias','YIELD_CSC_AI_PLACEMENT')))


def qualify_database(snapshot,mode):
    assert mode in('on','off')
    target=[r for r in snapshot['links']if r['DistrictType']=='DISTRICT_HARBOR'
        and r['AdjacentDistrict']=='DISTRICT_CSC_TAILORS_QUARTER']
    assert len(target)==(1 if mode=='on'else 0),'SQL arm absent from the loaded gameplay DB'
    assert len(snapshot['yields'])==1 and snapshot['yields'][0]['DefaultValue']==1
    assert len(snapshot['biases'])==1 and snapshot['biases'][0]['Value']==25
    assert any(r['ID']=='CSC_AI_CUSTOMER_DISTRICT_HARBOR__DISTRICT_CSC_TAILORS_QUARTER'
        and r['YieldChange']==1 and r['TilesRequired']==1 for r in snapshot['rules'])
    return snapshot

SQL_PATH=Path('Data/CSC_DIAG_NATIVE_CUSTOMER_LINK.sql')
ON_SQL=b'-- Diagnostic native-on control: retain the shipped customer adjacency.\nSELECT 1;\n'
OFF_SQL=b"""-- Diagnostic only: remove one customer-to-Quarter private-yield link.
-- Keep its definition, Yield identity/index and bias, and every other row.
DELETE FROM District_Adjacencies
WHERE DistrictType = 'DISTRICT_HARBOR'
  AND YieldChangeId IN (
      SELECT ID FROM Adjacency_YieldChanges
      WHERE YieldType = 'YIELD_CSC_AI_PLACEMENT'
        AND AdjacentDistrict = 'DISTRICT_CSC_TAILORS_QUARTER'
  );
"""
WITHHOLD=b'''    -- Diagnostic sufficiency test in BOTH native-adjacency arms.
    -- Remove only an intact positive customer contribution, never a merged
    -- negative material-protection entry. Bridge forbids zero-delta entries.
    for index=#entries,1,-1 do
        local entry=entries[index]
        if entry.player==3 and entry.city==393221 and entry.customer
            and GameInfo.Districts[entry.district].DistrictType=='DISTRICT_HARBOR' then
            assert(entry.delta==40*256,'Unexpected customer aggregate; preserve protection')
            print('CSC_CUSTOMER_CE_WITHHELD',turn,version+1,entry.district,entry.plot,entry.delta)
            table.remove(entries,index)
        end
    end
'''


def stage_publisher(source):
    needle=b'    local accepted, message = bridge.Publish('
    assert source.count(needle)==1
    return source.replace(needle,WITHHOLD+needle)


def stage_metadata(source,mode):
    assert mode in('on','off')
    root=ET.fromstring(source)
    actions=assert_element(root,'InGameActions');files=assert_element(root,'Files')
    assert not any(f.text==SQL_PATH.as_posix()for f in files.findall('File'))
    highest=max([0]+[int(p.text)for action in actions for p in action.findall('Properties/LoadOrder')])
    assert highest<2147483646
    action=ET.SubElement(actions,'UpdateDatabase',id='CSC_DIAG_NATIVE_CUSTOMER_LINK')
    ET.SubElement(ET.SubElement(action,'Properties'),'LoadOrder').text=str(highest+1)
    ET.SubElement(action,'File').text=SQL_PATH.as_posix()
    ET.SubElement(files,'File').text=SQL_PATH.as_posix()
    return ET.tostring(root,encoding='utf-8',xml_declaration=True),ON_SQL if mode=='on'else OFF_SQL


def assert_element(root,name):
    item=root.find(name);assert item is not None
    return item


def source_case(folder,home,policy):
    assert load(folder/'complete.json')['verified']and load(folder/'session-closed.json')['verified']
    origin=load(folder/'customer-placement-source.json')
    assert origin['verified']and origin['prepared_quarter']and origin['inspection_eligible']
    assert (origin['player'],origin['city'])==(3,393221)
    assert origin['source_world_sha256']=='e333251ec7318fb6b170678a956c28e02e2f9b01c4c4753c99e84b1a112fe19a'
    assert all(sha(policy/relative)==digest for relative,digest in origin['main_policy_sha256'].items())
    checkpoint=load(folder/'checkpoint.json')
    assert checkpoint['verified']and checkpoint['turn']==208 and checkpoint['save_complete_event']and checkpoint['native_phase_unchanged']
    assert all(checkpoint[p]['turn']==208 and not checkpoint[p]['active']and checkpoint[p]['local_player']==0
        and checkpoint[p]['player0_human']for p in('before','after'))
    native=Path(checkpoint['native_save']).resolve(strict=True)
    assert native.parent==(home/'Saves/Single').resolve()
    assert sha(native)==sha(folder/'source.Civ6Save')==checkpoint['sha256']
    comparison=folder/origin['inspection_relative']
    facts=load(comparison/'common-world-inspection.json')
    preflight=load(comparison/'customer-preflight.json')
    assert preflight['eligible']and preflight['native_signal_active']and facts['city']['hasQuarter']and not facts['city']['hasHarbor']
    assert origin['plot']==preflight['quarter_plot']
    harbor,quarter=facts['harbor'],facts['quarter']
    assert harbor['type']=='DISTRICT_HARBOR'and quarter['type']=='DISTRICT_CSC_TAILORS_QUARTER'
    targets=preflight['legal_customer_candidates'];assert targets
    return dict(player=3,city=393221,name='LOC_CITY_NAME_HAMBURG',district=harbor['index'],
        profile='TAILORS',profileDistrict=quarter['index'],quarterPlot=origin['plot'],
        plots=sorted(set(targets+[origin['plot'],1084])),purchasePlots=targets,
        turn=208,max_turn=210,sha256=checkpoint['sha256'],archive='source.Civ6Save',metadata='checkpoint.json')


WATCHER=r'''
-- Read-only native-first customer trace. No score, queue or world writes.
local scope=__SCOPE__
local q=assert(GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER)
local h=assert(GameInfo.Districts.DISTRICT_HARBOR)
assert(q.Index==scope.profileDistrict and h.Index==scope.district)
local profile
for _,p in ipairs(CSC_AI_QuarterPlacement.StageTwoProfiles())do if p.key=='TAILORS'then profile=p end end
assert(profile)
local function definitions()
 local y=assert(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT)
 print('CSC_CUSTOMER_NATIVE_YIELD',y.YieldType,y.Index,y.DefaultValue)
 local biases=0
 for row in GameInfo.AiFavoredItems()do
  if row.ListType=='DefaultYieldBias'and row.Item==y.YieldType then
   assert(row.Value==25);biases=biases+1;print('CSC_CUSTOMER_NATIVE_BIAS',row.Item,row.Value)
  end
 end
 assert(biases==1 and y.DefaultValue==1)
 local linked=0
 for edge in GameInfo.District_Adjacencies()do
  if edge.DistrictType==h.DistrictType then
   local rule=GameInfo.Adjacency_YieldChanges[edge.YieldChangeId]
   if rule and rule.YieldType==y.YieldType and rule.AdjacentDistrict==q.DistrictType then
    assert(rule.YieldChange==1 and rule.TilesRequired==1);linked=linked+1
    print('CSC_CUSTOMER_NATIVE_LINK',edge.DistrictType,edge.YieldChangeId,rule.YieldChange)
   end
  end
 end
 assert(linked==__LINK_COUNT__,'Native adjacency arm does not match runtime database')
 print('CSC_CUSTOMER_NATIVE_LINK_COUNT',linked)
end
definitions()
function CSC_CUSTOMER_Snapshot()
 local turn=Game.GetCurrentGameTurn();if turn<208 or turn>210 then return end
 local city=assert(CityManager.GetCity(3,393221));assert(city:GetName()==scope.name)
 local version=assert(tonumber(CE_AIDistrictScoresStatus():match('"version":(%d+)')))
 print('CSC_CUSTOMER_CITY',turn,version,city:GetPopulation(),city:GetBuildQueue():CurrentlyBuilding())
 local plot=assert(Map.GetPlotByIndex(scope.quarterPlot))
 print('CSC_CUSTOMER_QUARTER',turn,scope.quarterPlot,plot:GetOwner(),plot:GetDistrictType())
 local supply=CSC_AI_QuarterPlacement.ReadSuppliers(Players[3],plot,profile)
 for _,base in ipairs(supply.base)do
  local p=Map.GetPlotByIndex(base.plot)
  print('CSC_CUSTOMER_BASE',turn,base.plot,base.resource,tostring(base.ready),tostring(base.working),
   p:GetOwner(),p:GetImprovementType())
 end
 for _,index in ipairs(scope.purchasePlots)do
  local p=Map.GetPlotByIndex(index);local owner=Cities.GetPlotPurchaseCity(p)
  print('CSC_CUSTOMER_PLOT',turn,index,p:GetOwner(),owner and owner:GetID()or -1,
   p:GetResourceType(),p:GetImprovementType(),p:GetDistrictType(),
   CE_AIDistrictScoresReceipt(version,3,393221,h.Index,index))
 end
end
CSC_CUSTOMER_Snapshot()
GameEvents.OnGameTurnStarted.Add(CSC_CUSTOMER_Snapshot)
'''
