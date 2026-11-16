"""Diagnostic-only native lifecycle probe after the isolated material fixture.

Reads actual building and plot yields while toggling one supplier, producer or
host district at a time. It makes no AI offers and advances no turns. The caller
must own a disposable shared-controller session and close it without saving.
Unknown pillage behavior is observed rather than encoded as an expected answer;
every round-trip must restore the same physical state and payout vector.
"""
from pathlib import Path
import time

from driver import lua,parse,require,write_json

BUILDINGS=('BUILDING_CSC_BAKERS_WIND_MILL','BUILDING_CSC_BAKERS_CAFE',
           'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP')


def run(controller,output,config):
    require(config.get('diagnosticOnly')is True and config['player']==0,'Disposable human fixture required')
    output=Path(output);output.mkdir(parents=True,exist_ok=False)
    definitions='local c='+lua(config)+'\nlocal names='+lua(list(BUILDINGS))+'''
assert(Game.GetCurrentGameTurn()==c.turn and not AutoplayManager.IsActive())
local city=assert(Players[0]:GetCities():FindID(c.city))
local function district(family)
 local p=assert(Map.GetPlotByIndex(c.quarters[family]))
 return assert(city:GetDistricts():GetDistrictAtLocation(p:GetX(),p:GetY()))
end
'''
    # Independent physical readback accompanies every UI payout. In particular,
    # a district setter may also change its buildings: record those states rather
    # than interpreting a district-pillage sample as an isolated building test.
    physical=definitions+'''
local v={}
local live={}
for _,name in ipairs({'YIELD_FOOD','YIELD_PRODUCTION','YIELD_GOLD','YIELD_CULTURE'})do
 local id=assert(GameInfo.Yields[name]).Index
 live[#live+1]=string.format('"%s":%.10g',name,city:GetYield(id))
end
print('CSC_LIFECYCLE_LIVE_CITY={'..table.concat(live,',')..'}')
for key,index in pairs(c.materials)do local p=assert(Map.GetPlotByIndex(index))
 local family=key=='bamboo'and'TAILORS'or'BAKERS'
 local q=Map.GetPlotByIndex(c.quarters[family])
 v[#v+1]=string.format('"%s":{"improvement":%d,"pillaged":%s,"centerDistance":%d,"quarterDistance":%d}',
  key,p:GetImprovementType(),tostring(p:IsImprovementPillaged()),
  Map.GetPlotDistance(p:GetX(),p:GetY(),city:GetX(),city:GetY()),Map.GetPlotDistance(p:GetX(),p:GetY(),q:GetX(),q:GetY()))
end
for i,name in ipairs(names)do local id=assert(GameInfo.Buildings[name]).Index
 v[#v+1]=string.format('"b%d":%s',i,tostring(city:GetBuildings():IsPillaged(id)))
end
v[#v+1]='"bakersDistrict":'..tostring(district('BAKERS'):IsPillaged())
v[#v+1]='"tailorsDistrict":'..tostring(district('TAILORS'):IsPillaged())
print('CSC_LIFECYCLE_WORLD={'..table.concat(v,',')..'}')
'''
    payout=definitions+'''
local v={};local yieldNames={'YIELD_FOOD','YIELD_PRODUCTION','YIELD_GOLD','YIELD_CULTURE'}
for i,name in ipairs(names)do local id=assert(GameInfo.Buildings[name]).Index
 for _,y in ipairs(yieldNames)do
  local a=assert(city:GetBuildingYield(id,y))
  v[#v+1]=string.format('"b%d:%s":%.10g',i,y,a)
 end
end
for key,index in pairs(c.materials)do local p=assert(Map.GetPlotByIndex(index))
 for _,y in ipairs(yieldNames)do
  local id=assert(GameInfo.Yields[y]).Index
  v[#v+1]=string.format('"%s:%s":%.10g',key,y,p:GetYield(id))
 end
 local worker=Cities.GetPlotWorkingCity(index)
 v[#v+1]=string.format('"%s:workingCity":%d',key,worker and worker:GetID()or -1)
end
print('CSC_LIFECYCLE_YIELDS={'..table.concat(v,',')..'}')
'''
    # Debug-only owner/subject evidence distinguishes attachment lifetime from
    # effective payout. Derive wanted roots from the actual building attachments
    # and native collection type; do not maintain a second list of material IDs.
    effects=definitions+'''
local wanted={};local children={}
for r in GameInfo.BuildingModifiers()do
 for _,name in ipairs(names)do if r.BuildingType==name then
  local m=GameInfo.Modifiers[r.ModifierId]
  if m and m.ModifierType=='MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER'then wanted[r.ModifierId]=true end
 end end
end
local producerLeaves={};local inputRoots={}
for r in GameInfo.ModifierArguments()do if r.Name=='BuildingType'then
 for _,name in ipairs(names)do if r.Value==name then producerLeaves[r.ModifierId]=true end end
end end
-- Native schema uses ModifierID here, unlike BuildingModifiers.ModifierId.
for r in GameInfo.ImprovementModifiers()do inputRoots[r.ModifierID]=true end
for r in GameInfo.ModifierArguments()do
 if inputRoots[r.ModifierId]and r.Name=='ModifierId'and producerLeaves[r.Value]then wanted[r.ModifierId]=true end
end
for r in GameInfo.ModifierArguments()do if wanted[r.ModifierId]and r.Name=='ModifierId'then children[r.Value]=true end end
local function quote(s)return '"'..tostring(s):gsub('\\\\','\\\\\\\\'):gsub('"','\\\\"'):gsub('[\\r\\n]',' ')..'"'end
local records={};local count=0
for _,id in ipairs(GameEffects.GetModifiers())do
 local definition=GameEffects.GetModifierDefinition(id)
 if definition and(wanted[definition.Id]or children[definition.Id])then
  local owner=GameEffects.GetModifierOwner(id)
  local ownerText=(owner and GameEffects.GetObjectString(owner))or''
  local ownerCity=tonumber(ownerText:match('City: (%d+)'))
  local ownerPlot=tonumber(ownerText:match('PlotIndex: (%d+)'))
  local scoped=ownerCity==c.city
  for _,index in pairs(c.materials)do scoped=scoped or ownerPlot==index end
  if owner and scoped and GameEffects.GetObjectsPlayerId(owner)==0 then
   count=count+1;assert(count<=128,'Unexpectedly broad fixture modifier graph')
   local subjects={}
   for _,subject in ipairs(GameEffects.GetModifierSubjects(id)or{})do subjects[#subjects+1]=quote(GameEffects.GetObjectString(subject))end
   records[#records+1]='{"id":'..quote(id)..',"definition":'..quote(definition.Id)..',"owner":'..quote(GameEffects.GetObjectString(owner))
    ..',"subjectCount":'..tostring(GameEffects.GetModifierSubjectCount(id))
                ..',"active":'..tostring(GameEffects.GetModifierActive(id))..',"subjects":['..table.concat(subjects,',')..']}'
  end
 end
end
print('CSC_LIFECYCLE_EFFECTS=['..table.concat(records,',')..']')
'''
    def mutate(label,code):
        raw=controller.cmd(definitions+code+'\nprint("CSC_LIFECYCLE_MUTATION_OK")',
                           'CSC_AdjacencyGameplay','lifecycle-'+label)
        (output/(label+'-mutation.txt')).write_text(raw,encoding='utf-8')
        require('CSC_LIFECYCLE_MUTATION_OK'in raw,'Lifecycle mutation failed: '+label)

    def capture(label):
        world=controller.cmd(physical,'CSC_AdjacencyGameplay','lifecycle-world-'+label)
        (output/(label+'-world.txt')).write_text(world,encoding='utf-8')
        actual=parse(world,'CSC_LIFECYCLE_WORLD')
        live=parse(world,'CSC_LIFECYCLE_LIVE_CITY')
        graph=None
        if label.endswith('-on')or label.endswith('-pillaged')or label.endswith('-removed')or label.endswith('-restored'):
            raw=controller.cmd(effects,'PlotInfo','lifecycle-effects-'+label)
            (output/(label+'-effects.txt')).write_text(raw,encoding='utf-8')
            graph=parse(raw,'CSC_LIFECYCLE_EFFECTS')
            write_json(output/(label+'-effects.json'),graph)
        deadline=time.monotonic()+20;last=None;attempt=0
        while True:
            raw=controller.cmd(payout,'PlotInfo','lifecycle-yields-'+label+'-'+str(attempt))
            (output/(label+'-yields-'+str(attempt)+'.txt')).write_text(raw,encoding='utf-8')
            row=parse(raw,'CSC_LIFECYCLE_YIELDS');attempt+=1
            if row==last:return dict(world=actual,yields=row,liveCity=live,effects=graph)
            require(time.monotonic()<deadline,'Lifecycle yields did not settle: '+label)
            last=row;time.sleep(.5)

    measurements={};ui_mismatches=[]
    def restored(label,baseline,observed):
        # UI GetBuildingYield reads a precomputed vector. Native attachment state
        # plus live Gameplay city income qualifies recovery; a stale UI field is
        # retained as evidence, never treated as a continuing payment.
        def graph(rows):
            return sorted([dict((k,v)for k,v in r.items()if k!='id')for r in rows or[]],key=lambda r:repr(sorted(r.items())))
        require(observed['world']==baseline['world'],'Repair physical state differs: '+label)
        require(observed['liveCity']==baseline['liveCity'],'Live city yield failed to recover: '+label)
        require(graph(observed['effects'])==graph(baseline['effects']),'Native effect graph failed to recover: '+label)
        if observed['yields']!=baseline['yields']:ui_mismatches.append(label)
    for supplier,family,index in [('farm','BAKERS',1),('maple','BAKERS',2),('bamboo','TAILORS',3)]:
        mutate(supplier+'-on','CSC_MaterialCoverageFixture.Activate('+lua(supplier)+')')
        baseline=capture(supplier+'-on');measurements[supplier+'-on']=baseline
        for kind in('supplier','producer','district'):
            for pillaged in(True,False):
                label=supplier+'-'+kind+('-pillaged'if pillaged else'-restored')
                state='true'if pillaged else'false'
                if kind=='supplier':
                    command='ImprovementBuilder.SetImprovementPillaged(assert(Map.GetPlotByIndex(c.materials['+lua(supplier)+'])), '+state+')'
                elif kind=='producer':
                    command='city:GetBuildings():SetPillaged(assert(GameInfo.Buildings[names['+str(index)+']]).Index, '+state+')'
                else:
                    command='district('+lua(family)+'):SetPillaged('+state+')'
                    if not pillaged:
                        # Restore the fixture's known functioning producers too,
                        # should the engine's district setter propagate damage.
                        command+='\nfor _,n in ipairs(names)do city:GetBuildings():SetPillaged(GameInfo.Buildings[n].Index,false)end'
                mutate(label,command)
                measurement=capture(label);measurements[label]=measurement
                if not pillaged:restored(label,baseline,measurement)
        # Persist each completed supplier cycle, even if the next one fails.
        write_json(output/'measurements.json',measurements)
        # Recreate the input owner under damage as an independent gate check.
        # The native collection/live city yield responds to district updates,
        # while the UI building-yield cache can retain its prior value. Keep
        # those observations separate rather than inferring a missing callback.
        label=supplier+'-fresh-input-pillaged'
        mutate(label,'district('+lua(family)+'):SetPillaged(true)\nCSC_MaterialCoverageFixture.Activate('+lua(supplier)+')')
        measurements[label]=capture(label)
        label=supplier+'-fresh-input-restored'
        mutate(label,'district('+lua(family)+'):SetPillaged(false)')
        measurements[label]=capture(label)
        write_json(output/'measurements.json',measurements)
        restored(label,baseline,measurements[label])
        mutate(supplier+'-removed','CSC_MaterialCoverageFixture.Activate("none")')
        measurements[supplier+'-removed']=capture(supplier+'-removed')
    mutate('none','CSC_MaterialCoverageFixture.Activate("none")')
    result=dict(verified=True,diagnostic_only=True,ai_turns_advanced=0,
                measurements=measurements,ui_cache_mismatches=ui_mismatches,
                semantics='Recovery qualifies physical state, native effects and live Gameplay city yield; cached UI differences retained')
    write_json(output/'result.json',result)
    return result
