"""One declared territorial opportunity after the proven1.7 deferral.

The main CSC model/CE policy remains the only live treatment. The diagnostic
changes ownership of an existing farmed Base, not its resource, improvement,
terrain, queue, population, funds or an AI plan. No acquisition claim follows.
All commands run through the exclusive shared controller; failure never resends
the edit. Later ordinary publications/decisions must supply reconsideration.
"""
import re
import json


def parse_snapshot(raw):
    rows=re.findall(r'CSC_DEFERRAL_OPPORTUNITY_CHUNK\t(\d+)\t(\d+)\t(\d+)\t([^\r\n]*)',raw)
    endings=re.findall(r'CSC_DEFERRAL_OPPORTUNITY_END\t(\d+)\t(\d+)\t(\d+)',raw)
    assert len(endings)==1 and rows,'Missing complete opportunity snapshot'
    turn,count,size=map(int,endings[0]);assert len(rows)==count
    assert [(int(t),int(i),int(n))for t,i,n,_ in rows]==[(turn,i,count)for i in range(1,count+1)]
    payload=''.join(row[3]for row in rows)
    assert len(payload.encode('utf-8'))==size,'Clipped opportunity snapshot'
    result=json.loads(payload);assert result['turn']==turn
    return result


TRANSFER=r'''
assert(Game.GetCurrentGameTurn()==204 and not AutoplayManager.IsActive() and Game.GetLocalPlayer()==0 and Players[0]:IsHuman())
local player=assert(Players[1]);local city=assert(CityManager.GetCity(1,524295))
assert(not player:IsHuman() and city:GetName()=='LOC_CITY_NAME_NICOPOLIS')
local plot=assert(Map.GetPlotByIndex(471));local oldCity=assert(Cities.GetPlotPurchaseCity(plot))
assert(plot:GetOwner()==11 and oldCity:GetID()==65536,'Territorial fixture source differs')
assert(plot:GetResourceType()==GameInfo.Resources.RESOURCE_CSC_FLAX.Index)
assert(plot:GetImprovementType()==GameInfo.Improvements.IMPROVEMENT_FARM.Index and plot:GetDistrictType()==-1)
local free=false
for _,index in ipairs({397,398})do
 local site=assert(Map.GetPlotByIndex(index));local owner=Cities.GetPlotPurchaseCity(site)
 if site:GetDistrictType()==-1 and site:CanHaveDistrict(36,1,524295)
  and (site:GetOwner()==-1 or site:GetOwner()==1 and owner and owner:GetID()==524295)
  and Map.GetPlotDistance(site:GetX(),site:GetY(),plot:GetX(),plot:GetY())==1 then free=true end
end
assert(free,'No free legal Quarter footprint before territorial edit')
local before={plot:GetResourceType(),plot:GetImprovementType(),plot:GetTerrainType(),plot:GetFeatureType(),
 plot:IsImprovementPillaged(),plot:GetRiverCrossingCount()}
local gold=player:GetTreasury():GetGoldBalance()
local population=city:GetPopulation();local queued=city:GetBuildQueue():CurrentlyBuilding()
-- The sole controlled world change. No native payment/action or policy success.
WorldBuilder.CityManager():SetPlotOwner(plot:GetX(),plot:GetY(),1,city:GetID())
local owner=assert(Cities.GetPlotPurchaseCity(plot))
assert(plot:GetOwner()==1 and owner:GetID()==524295)
local after={plot:GetResourceType(),plot:GetImprovementType(),plot:GetTerrainType(),plot:GetFeatureType(),
 plot:IsImprovementPillaged(),plot:GetRiverCrossingCount()}
for i,value in ipairs(before)do assert(value==after[i],'Territorial change altered material/terrain')end
assert(player:GetTreasury():GetGoldBalance()==gold and city:GetPopulation()==population)
assert(city:GetBuildQueue():CurrentlyBuilding()==queued,'Territorial fixture changed production queue')
print('CSC_DEFERRAL_OPPORTUNITY_TRANSFERRED',Game.GetCurrentGameTurn(),471,11,1,owner:GetID(),
 before[1],before[2],gold,population,queued)
CSC_DEFERRAL_OPPORTUNITY_Inspect()
'''

UI_CAPACITY=r'''
local function optional(object,name)
 if not object or type(object[name])~='function'then return 'unavailable'end
 local ok,value=pcall(object[name],object);return ok and value or 'unavailable'
end
local city=assert(CityManager.GetCity(1,524295));local districts=city:GetDistricts()
print('CSC_DEFERRAL_UI_CAPACITY',Game.GetCurrentGameTurn(),city:GetPopulation(),
 optional(districts,'GetNumAllowedDistrictsRequiringPopulation'),optional(districts,'GetNumZonedDistrictsRequiringPopulation'),
 optional(city:GetBuildQueue(),'GetCurrentProductionTypeHash'))
'''


def qualify_before(snapshot):
    assert snapshot['turn']==204 and snapshot['mutationCommands']==0 and not snapshot['hasQuarter']
    source=snapshot['supplier']
    assert source['plot']==471 and source['mappedBase'] and source['revealed'] and source['resourceVisible']
    assert source['resourceType']=='RESOURCE_CSC_FLAX' and source['improvementType']=='IMPROVEMENT_FARM'
    assert source['owner']==11 and source['city']==65536,'Controlled source ownership changed; inspect before editing'
    free=[site for site in snapshot['sites']if site['plot']in(397,398) and site['legal']
        and site['district']==-1 and site['supplierDistance']==1 and site['owner']in(-1,1)
        and(site['owner']==-1 or site['city']==524295)
        and site['model'].get('declineNoBase') and json.loads(site['declineReceipt'])['staged']==1]
    assert free,'No free legal Quarter footprint beside the new supplier; do not alter the world'
    return dict(mode='controlled-territorial-transfer',
        free_sites=[s['plot']for s in free],native_acquisition_claim=False)


def qualify_after(before,after):
    assert after['turn']==before['turn']==204
    assert after['supplier']['owner']==1 and after['supplier']['city']==524295
    for key in('plot','resource','resourceType','improvement','improvementType','pillaged','terrain','feature','resourceCount','riverEdges'):
        assert before['supplier'].get(key)==after['supplier'].get(key),key
    for key in('population','currentItem'):assert before['city'][key]==after['city'][key],key
    qualify_before(before)
    previously_declined={s['plot']for s in before['sites']if s['model'].get('declineNoBase')
        and json.loads(s['declineReceipt'])['staged']==1}
    recognized=[s for s in after['sites']if s['plot']in previously_declined and s['legal']and s['district']==-1
        and any(b['plot']==471 for b in s['base'])]
    assert recognized,'Main supplier reader does not recognize the changed Base'
    assert any(not s['model'].get('declineNoBase',False)for s in recognized),'Main model did not withdraw its decline proposal'
    return [s['plot']for s in recognized]


def quarter_request_after(text,selections,supported_sites=(),lua_text=''):
    """Join a new supplier, actual active publication, unique choice and request.

    An unrelated later Bakers choice is not reconsideration of this opportunity.
    The previous-version receipt is read before replacement, so staged0 proves
    retirement in the exact publication consumed by the native Best record.
    """
    publications={int(v):int(t)for t,v in re.findall(r'CSC_AI_BAKERS_DISTRICTS turn=(\d+) version=(\d+)',lua_text)}
    assert 'CSC_HOST_DIAG_FAILED' not in lua_text,'Native receipt reader failed; no reconsideration claim'
    native={}
    # Only complete, generation-checked reader prefixes can establish a native
    # Best receipt. A clipped/failed read must not supply usable-looking evidence.
    prefix=r'CSC_HOST_PREFIX_BEGIN\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)[^\r\n]*\r?\n(.*?)CSC_HOST_PREFIX_END\s+\1\s+\2\s+\3\s+\4(?:\s|$)'
    for t,g,v,count,body in re.findall(prefix,lua_text,re.S):
        for read_turn,read_gen,index,raw in re.findall(r'CSC_HOST_NATIVE\s+(\d+)\s+(\d+)\s+(\d+)\s+(\{[^\r\n]+\})',body):
            assert (read_turn,read_gen)==(t,g) and 0<=int(index)<int(count)
            item=json.loads(raw);key=(int(g),int(index))
            assert key not in native or native[key]==item
            native[key]=item
    for row in selections:
        if row.get('kind')!='selection' or row['turn']<=204 or (row.get('winner')or{}).get('district')!=36:
            continue
        plot=row['winner']['y']*74+row['winner']['x']
        if plot not in supported_sites:continue
        if sum(r.get('kind')=='selection'and r['turn']==row['turn']for r in selections)!=1:continue
        pattern=r'^'+str(row['turn'])+r', 1, LOC_CITY_NAME_NICOPOLIS, .*?, SUBMITTED, NO_UNIT, NO_BUILDING, DISTRICT_CSC_BAKERS_QUARTER, .*Build City District$'
        matches=re.findall(pattern,text,re.M)
        if len(matches)!=1:continue
        best=[r for r in native.values()if r['k']=='best'and(r['player'],r['city'],r['district'],r['plot'],r['result'])==
            (1,524295,36,plot,row['winner']['q8']) and publications.get(r['version'])==row['turn']]
        if len(best)!=1:continue
        version=best[0]['version'];turn=row['turn']
        if not re.search(r'CSC_DEFERRAL_TRACKED_BASE\s+'+str(turn)+r'\s+'+str(version)+r'\s+'+str(plot)+r'\s+471\s+true\s+(true|false)',lua_text):continue
        if not re.search(r'CSC_DEFERRAL_TRACKED_SUPPLIER\s+'+str(turn)+r'\s+'+str(version)+r'\s+1\s+524295\s+54\s+1\s+(true|false)',lua_text):continue
        receipts=[json.loads(raw)for _,v,p,raw in re.findall(
            r'CSC_DEFERRAL_DECLINE_PREVIOUS\s+(\d+)\s+(\d+)\s+(\d+)\s+(\{[^\r\n]+\})',lua_text)
            if int(v)==version and int(p)==plot]
        if len(receipts)!=1 or receipts[0].get('staged')!=0:continue
        return dict(selection=row,request=matches[0],publication_version=version,
            native_best=best[0],decline_receipt=receipts[0],verified_supplier_plot=471)
    return None
