-- Read-only facts for the declared historical weak-site save. Execute in
-- GameCore_Tuner through the shared controller; no policy or original-human
-- marker is required. Nothing here changes properties, game objects or orders.
local function object(t) return setmetatable(t or {}, {__json_object=true}) end
local function json(v)
    local kind=type(v)
    if kind=='nil' then return 'null' end
    if kind=='boolean' then return tostring(v) end
    if kind=='number' then
        assert(v==v and v~=math.huge and v~=-math.huge,'Nonfinite capture number')
        return tostring(v)
    end
    if kind=='string' then
        return '"'..v:gsub('[%z\1-\31\\"]',function(c)
            if c=='\\' then return '\\\\' end
            if c=='"' then return '\\"' end
            return string.format('\\u%04x',string.byte(c))
        end)..'"'
    end
    assert(kind=='table','Non-scalar observation: '..kind)
    local count,array=0,not(getmetatable(v) and getmetatable(v).__json_object)
    for key in pairs(v) do count=count+1;if type(key)~='number' then array=false end end
    if count~=#v then array=false end
    local values={}
    if array then
        for _,x in ipairs(v) do values[#values+1]=json(x) end
        return '['..table.concat(values,',')..']'
    end
    local keys={};for key in pairs(v) do keys[#keys+1]=key end
    table.sort(keys,function(a,b) return tostring(a)<tostring(b) end)
    for _,key in ipairs(keys) do values[#values+1]=json(tostring(key))..':'..json(v[key]) end
    return '{'..table.concat(values,',')..'}'
end
local function call(owner,key,...)
    if not owner or type(owner[key])~='function' then return {unavailable=key} end
    local ok,value=pcall(owner[key],owner,...)
    if ok then return value end
    return {error=tostring(value),method=key}
end
local function fields(row,names)
    local out=object()
    for _,name in ipairs(names) do
        local value=row[name]
        if type(value)=='string' or type(value)=='number' or type(value)=='boolean' then out[name]=value end
    end
    return out
end
local family={
    'BUILDING_CSC_BAKERS_RIVER_ACCESS','BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',
    'BUILDING_CSC_BAKERS_WIND_MILL','BUILDING_CSC_BAKERS_WATER_MILL',
    'BUILDING_CSC_BAKERS_BAKERY','BUILDING_CSC_BAKERS_CAFE'
}
local scopes={{player=5,city=65536,plot=1429,label='Delhi'},
              {player=3,city=65536,plot=1829,label='Majapahit'}}
local millRules={'CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS',
                 'CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER'}
local bits={1,2,4,8,16,32,64,128,256,512}
local quarter='DISTRICT_CSC_BAKERS_QUARTER'
local district=assert(GameInfo.Districts[quarter],'Missing loaded Bakers district')
local out={schema=1,profile='bakers-components-v1',readOnly=true,
    turn=Game.GetCurrentGameTurn(),mapping={family={}},targets={},players={},
    districtCatalog={},ownerDistricts={},
    relevantDB={buildings={},prerequisites={},mutualExclusions={},adjacencyRules={},
        buildingModifiers={},modifiers={},modifierArguments={},requirements={},
        requirementMembers={},requirementArguments={}}}
out.millPropertySchema={rules=millRules,bits=bits,
    prefix='CSC_ADJ_',suffixes={'TOTAL','ACTUAL_AMOUNT','ENCODED_AMOUNT'},absent='ABSENT'}
out.width,out.height=Map.GetGridSize()
out.mapWidth,out.mapHeight=out.width,out.height
out.mapping.districtIndex=district.Index
out.mapping.districtType=quarter
local function catalog(tableName,typeField,destination)
    local count,maxIndex=0,-1
    for row in GameInfo[tableName]() do
        count=count+1;maxIndex=math.max(maxIndex,row.Index)
        if destination then destination[#destination+1]={index=row.Index,type=row[typeField]} end
    end
    if destination then table.sort(destination,function(a,b) return a.index<b.index end) end
    return count,maxIndex+1
end
out.mapping.buildingCount,out.mapping.buildingIndexLimit=catalog('Buildings','BuildingType',nil)
out.mapping.districtCount,out.mapping.districtIndexLimit=catalog('Districts','DistrictType',out.districtCatalog)
out.mapping.buildingsDense=out.mapping.buildingCount==out.mapping.buildingIndexLimit
out.mapping.districtsDense=out.mapping.districtCount==out.mapping.districtIndexLimit
local wantedBuildings={}
for _,name in ipairs(family) do
    local row=assert(GameInfo.Buildings[name],'Missing loaded family building '..name)
    wantedBuildings[name]=true
    out.mapping.family[#out.mapping.family+1]={type=name,index=row.Index}
    out.relevantDB.buildings[#out.relevantDB.buildings+1]=fields(row,{'Index','BuildingType',
        'PrereqDistrict','PrereqTech','PrereqCivic','Cost','Maintenance','Entertainment',
        'RegionalRange','CitizenSlots','MustPurchase','InternalOnly','RequiresPlacement'})
end
-- Preserve GameInfo traversal order as an observation; it is NOT asserted to be
-- the native first-prerequisite pointer order. The observer checks that vector.
for ordinal,row in ipairs((function()
    local rows={};for item in GameInfo.BuildingPrereqs() do rows[#rows+1]=item end;return rows
end)()) do
    if wantedBuildings[row.Building] then
        out.relevantDB.prerequisites[#out.relevantDB.prerequisites+1]={ordinal=ordinal,
            building=row.Building,prerequisite=row.PrereqBuilding,
            prerequisiteIndex=GameInfo.Buildings[row.PrereqBuilding].Index}
    end
end
if GameInfo.MutuallyExclusiveBuildings then
    local ordinal=0
    for row in GameInfo.MutuallyExclusiveBuildings() do
        ordinal=ordinal+1
        if wantedBuildings[row.Building] then
            out.relevantDB.mutualExclusions[#out.relevantDB.mutualExclusions+1]={ordinal=ordinal,
                building=row.Building,excluded=row.MutuallyExclusiveBuilding,
                excludedIndex=GameInfo.Buildings[row.MutuallyExclusiveBuilding].Index}
        end
    end
end
-- Capture all active family roots and their attach-child closure. Only the
-- relevant requirement/argument rows follow; obsolete unattached definitions
-- are not mistaken for active candidate roots.
local roots,mods,args,dynamic,requirements={},{},{},{},{}
for row in GameInfo.BuildingModifiers() do
    if wantedBuildings[row.BuildingType] then
        roots[row.ModifierId]=true
        out.relevantDB.buildingModifiers[#out.relevantDB.buildingModifiers+1]=
            {building=row.BuildingType,modifier=row.ModifierId}
    end
end
for row in GameInfo.Modifiers() do mods[row.ModifierId]=row end
for row in GameInfo.ModifierArguments() do
    args[row.ModifierId]=args[row.ModifierId] or {}
    args[row.ModifierId][#args[row.ModifierId]+1]=row
end
for row in GameInfo.DynamicModifiers() do dynamic[row.ModifierType]=row end
local visited={}
local function visit(name)
    if visited[name] then return end
    visited[name]=true
    local row=assert(mods[name],'Active family modifier missing '..name)
    local item=fields(row,{'ModifierId','ModifierType','OwnerRequirementSetId','SubjectRequirementSetId'})
    local definition=dynamic[row.ModifierType]
    if definition then item.CollectionType=definition.CollectionType;item.EffectType=definition.EffectType end
    item.root=not not roots[name]
    out.relevantDB.modifiers[#out.relevantDB.modifiers+1]=item
    if row.OwnerRequirementSetId then requirements[row.OwnerRequirementSetId]=true end
    if row.SubjectRequirementSetId then requirements[row.SubjectRequirementSetId]=true end
    for _,arg in ipairs(args[name] or {}) do
        out.relevantDB.modifierArguments[#out.relevantDB.modifierArguments+1]=fields(arg,{'ModifierId','Name','Value','Type'})
        if arg.Name=='ModifierId' then visit(arg.Value) end
    end
end
local rootNames={};for name in pairs(roots) do rootNames[#rootNames+1]=name end;table.sort(rootNames)
for _,name in ipairs(rootNames) do visit(name) end
local reqIDs={}
-- Nested RequirementSetId arguments expand to a fixed point. This reads table
-- definitions only; it does not evaluate or mutate gameplay requirements.
local changed=true
while changed do
    changed=false
    for row in GameInfo.RequirementSetRequirements() do
        if requirements[row.RequirementSetId] and not reqIDs[row.RequirementId] then
            reqIDs[row.RequirementId]=true;changed=true
        end
    end
    for row in GameInfo.RequirementArguments() do
        if reqIDs[row.RequirementId] and row.Name=='RequirementSetId' and not requirements[row.Value] then
            requirements[row.Value]=true;changed=true
        end
    end
end
for row in GameInfo.RequirementSetRequirements() do
    if requirements[row.RequirementSetId] then out.relevantDB.requirementMembers[#out.relevantDB.requirementMembers+1]=fields(row,{'RequirementSetId','RequirementId'}) end
end
for row in GameInfo.Requirements() do
    if reqIDs[row.RequirementId] then out.relevantDB.requirements[#out.relevantDB.requirements+1]=fields(row,{'RequirementId','RequirementType','Inverse'}) end
end
for row in GameInfo.RequirementArguments() do
    if reqIDs[row.RequirementId] then out.relevantDB.requirementArguments[#out.relevantDB.requirementArguments+1]=fields(row,{'RequirementId','Name','Value','Type'}) end
end
if GameInfo.CSC_AdjacencyRules then
    for row in GameInfo.CSC_AdjacencyRules() do
        if row.DistrictType==quarter then
            out.relevantDB.adjacencyRules[#out.relevantDB.adjacencyRules+1]=fields(row,{'ID','DistrictType',
                'ProvideType','YieldType','YieldChange','AdjacencyType','CustomAdjacentObject',
                'Rings','MinRings','MaxRings','MustOwn','ModifierOwner','WhoIsTheOwner','CollectionType'})
        end
    end
end
-- The shared core defines pure readers plus an unused writer. Initialize caches
-- in this Tuner context only; never call Write or load CSC_AdjacencyGameplay.
local A=CSC_Adjacency
if not A and type(include)=='function' then
    local ok,message=pcall(include,'CSC_AdjacencyCore')
    if not ok then out.adjacencyLoadError=tostring(message) end
    A=CSC_Adjacency
end
if A then
    local ok,message=pcall(A.Initialize)
    if not ok then out.adjacencyLoadError=tostring(message);A=nil end
end
out.sharedAdjacencyAvailable=not not A
local function properties(plot)
    local rows={}
    for ruleIndex,id in ipairs(millRules) do
        local entry={ruleIndex=ruleIndex,bitValues={},amountSum=0}
        for _,bit in ipairs(bits) do
            local key='CSC_ADJ_'..id..'_'..bit
            local value=plot:GetProperty(key)
            entry.bitValues[#entry.bitValues+1]=value==nil and 'ABSENT' or value
            if value==1 then entry.amountSum=entry.amountSum+bit end
        end
        for _,suffix in ipairs({'TOTAL','ACTUAL_AMOUNT','ENCODED_AMOUNT'}) do
            local key='CSC_ADJ_'..id..'_'..suffix
            local value=plot:GetProperty(key)
            entry[suffix]=value==nil and 'ABSENT' or value
        end
        rows[#rows+1]=entry
    end
    return rows
end
local function plotFacts(plot,pid,city)
    local row={index=plot:GetIndex(),x=plot:GetX(),y=plot:GetY(),owner=plot:GetOwner(),
        district=plot:GetDistrictType(),feature=plot:GetFeatureType(),resource=plot:GetResourceType(),
        improvement=plot:GetImprovementType(),water=plot:IsWater(),hills=plot:IsHills(),
        river=plot:IsRiver(),riverEdges=plot:GetRiverCrossingCount(),millProperties=properties(plot)}
    if pid then
        row.revealed=call(PlayersVisibility[pid],'IsRevealed',row.x,row.y)
        if city then row.legalBakers=call(plot,'CanHaveDistrict',district.Index,pid,city:GetID()) end
    end
    return row
end
local seenPlayers={}
for _,scope in ipairs(scopes) do
    local player=Players[scope.player]
    local target={player=scope.player,city=scope.city,plot=scope.plot,label=scope.label,exists=false}
    out.targets[#out.targets+1]=target
    if player then
        target.human=player:IsHuman();target.alive=player:IsAlive();target.major=player:IsMajor()
        if not seenPlayers[scope.player] then
            seenPlayers[scope.player]=true
            out.players[#out.players+1]={player=scope.player,human=target.human,alive=target.alive,major=target.major}
            for _,city in player:GetCities():Members() do
                local ds=city:GetDistricts()
                assert(ds.GetNumDistricts and ds.GetDistrictByIndex,'Native gameplay district index API required')
                for i=0,ds:GetNumDistricts()-1 do
                    local d=ds:GetDistrictByIndex(i)
                    if d then
                        local plot=assert(Map.GetPlot(d:GetX(),d:GetY()))
                        out.ownerDistricts[#out.ownerDistricts+1]={player=scope.player,city=city:GetID(),
                            cityName=city:GetName(),index=d:GetType(),
                            districtID=call(d,'GetID'),complete=call(d,'IsComplete'),pillaged=call(d,'IsPillaged'),
                            plot={index=plot:GetIndex(),x=plot:GetX(),y=plot:GetY(),millProperties=properties(plot)}}
                    end
                end
                if city:GetID()==scope.city then
                    target.exists=true;target.name=city:GetName();target.x=city:GetX();target.y=city:GetY()
                    if Locale and type(Locale.Lookup)=='function' then
                        local ok,name=pcall(Locale.Lookup,target.name)
                        if ok then target.localizedName=name end
                    end
                    local actualName=target.localizedName or target.name
                    target.nameMatches=tostring(actualName):upper():find(scope.label:upper(),1,true)~=nil
                    target.hasBakers=false
                    for i=0,ds:GetNumDistricts()-1 do
                        local d=ds:GetDistrictByIndex(i)
                        if d and d:GetType()==district.Index then target.hasBakers=true end
                    end
                    target.population=city:GetPopulation();target.buildings={}
                    local b,q=city:GetBuildings(),city:GetBuildQueue()
                    for _,entry in ipairs(out.mapping.family) do
                        target.buildings[#target.buildings+1]={type=entry.type,index=entry.index,
                            present=b:HasBuilding(entry.index),pillaged=call(b,'IsPillaged',entry.index),
                            progress=call(q,'GetBuildingProgress',entry.index)}
                    end
                    target.queue={production=call(q,'CurrentlyBuilding'),hash=call(q,'GetCurrentProductionTypeHash'),size=call(q,'GetSize')}
                    local plot=assert(Map.GetPlotByIndex(scope.plot),'Declared candidate plot missing')
                    target.candidate=plotFacts(plot,scope.player,city)
                    target.adjacency={rules={}}
                    if A then
                        local selectedMill=plot:IsRiver() and family[4] or family[3]
                        target.adjacency.plannedMill=selectedMill
                        for _,rule in ipairs(A.ByDistrict[quarter] or {}) do
                            if rule.YieldType=='YIELD_PRODUCTION' or rule.YieldType=='YIELD_GOLD' then
                                local ok,count,amount,raw=pcall(function()
                                    local n=A.Count(rule,plot,city,scope.player)
                                    local encoded,unclamped=A.Amount(rule,n)
                                    return n,encoded,unclamped
                                end)
                                local entry={rule=rule.ID,yield=rule.YieldType,provider=rule.ProvideType,
                                    owner=rule.ModifierOwner,requiresBuilding=rule.WhoIsTheOwner,
                                    selectedMill=rule.WhoIsTheOwner==selectedMill}
                                if ok then entry.count=count;entry.amount=amount;entry.raw=raw
                                else entry.error=tostring(count) end
                                target.adjacency.rules[#target.adjacency.rules+1]=entry
                            end
                        end
                    end
                end
            end
        end
    end
end
out.mappingVerified=out.mapping.buildingsDense and out.mapping.districtsDense
    and #out.mapping.family==6 and #out.targets==2 and out.targets[1].exists and out.targets[2].exists
out.player0={exists=Players[0]~=nil,human=Players[0] and Players[0]:IsHuman() or false,
    alive=Players[0] and Players[0]:IsAlive() or false}
out.sourceValidation={mappingVerified=out.mappingVerified,originalHuman0=out.player0.human,
    targetsMatch=true}
for _,target in ipairs(out.targets) do
    local valid=target.exists and target.nameMatches and target.alive and target.major
        and not target.human and not target.hasBakers and target.candidate
        and target.candidate.owner==target.player and target.candidate.district==-1
    target.sourceValid=not not valid
    if not valid then out.sourceValidation.targetsMatch=false end
end
out.sourceValidation.valid=out.mappingVerified and out.sourceValidation.originalHuman0
    and out.sourceValidation.targetsMatch
out.observerConfig={profile='bakers-components-v1',mappingVerified=out.mappingVerified,
    targets={{player=5,city=65536},{player=3,city=65536}},buildings=out.mapping.family,
    buildingCount=out.mapping.buildingCount,districtCount=out.mapping.districtCount,
    districtIndex=district.Index,mapWidth=out.width,mapHeight=out.height,
    maxPairs=4096,maxCallbacks=200000,maxThreads=8,maxDepth=16,maxRows=37}
-- Metadata uses a column schema once per table. Long database identifiers use
-- lossless {s=index} references into databaseStrings, keeping the complete
-- Tuner reply below its finite transport budget. ABSENT marks omitted fields.
local strings,stringIndexes={},{}
local function cell(value)
    if value==nil then return 'ABSENT' end
    if type(value)=='string' and #value>=20 then
        local index=stringIndexes[value]
        if not index then index=#strings+1;strings[index]=value;stringIndexes[value]=index end
        return {s=index}
    end
    return value
end
for name,rows in pairs(out.relevantDB) do
    local keys={};local seen={}
    for _,row in ipairs(rows) do
        for key in pairs(row) do if not seen[key] then seen[key]=true;keys[#keys+1]=key end end
    end
    table.sort(keys)
    local compact={columns=keys,rows={},absent='ABSENT'}
    for _,row in ipairs(rows) do
        local values={}
        for _,key in ipairs(keys) do
            values[#values+1]=cell(row[key])
        end
        compact.rows[#compact.rows+1]=values
    end
    out.relevantDB[name]=compact
end
out.databaseStrings=strings
out.relevantDBEncoding='Each {s:N} cell references databaseStrings[N], one-based; ABSENT marks an omitted field.'
local payload=json(out)
-- The shared controller retains the complete Tuner response. Lua.log caps lines
-- at2047bytes; optional chunks support standalone use when explicitly requested.
print('CSC_BAKERS_COMPONENT_WORLD='..payload)
if CSC_BAKERS_COMPONENT_DURABLE_CHUNKS and #payload>1400 then
    local sum=0;for i=1,#payload do sum=(sum+string.byte(payload,i))%4294967296 end
    local parts=math.ceil(#payload/512)
    for part=1,parts do
        local raw=payload:sub((part-1)*512+1,part*512)
        local hex=(raw:gsub('.',function(c) return string.format('%02x',string.byte(c)) end))
        print('CSC_BAKERS_COMPONENT_WORLD_CHUNK='..json({schema=1,turn=out.turn,part=part,
            parts=parts,bytes=#payload,sum32=sum,encoding='hex',data=hex}))
    end
end
return out
