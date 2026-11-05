-- Source in GameCore_Tuner via the shared controller. This collector only reads
-- definitions and current state; no policy, grants, orders or property writes.
local function numeric(v) local t=type(v);return t=='number' or t=='integer' end
local function object(v)return setmetatable(v or {},{__json_object=true})end
local function json(v)
    local t=type(v)
    if t=='nil'then return 'null'end
    if t=='boolean'then return tostring(v)end
    if numeric(v)then assert(v==v and v~=math.huge and v~=-math.huge);return tostring(v)end
    if t=='string'then return '"'..v:gsub('[%z\1-\31\\"]',function(c)
        if c=='\\'then return '\\\\'elseif c=='"'then return '\\"'end
        return string.format('\\u%04x',string.byte(c))end)..'"'end
    assert(t=='table','Unsupported receipt value '..t)
    local n,array=0,not(getmetatable(v)and getmetatable(v).__json_object)
    for k in pairs(v)do n=n+1;if not numeric(k)then array=false end end
    if n~=#v then array=false end
    local parts={}
    if array then for _,x in ipairs(v)do parts[#parts+1]=json(x)end;return '['..table.concat(parts,',')..']'end
    local keys={};for k in pairs(v)do keys[#keys+1]=k end
    table.sort(keys,function(a,b)return tostring(a)<tostring(b)end)
    for _,k in ipairs(keys)do parts[#parts+1]=json(tostring(k))..':'..json(v[k])end
    return '{'..table.concat(parts,',')..'}'
end
local function call(o,k,...)
    if not o or type(o[k])~='function'then return {unavailable=k}end
    local ok,v=pcall(o[k],o,...);if ok then return v==nil and 'ABSENT' or v end
    return {error=tostring(v),method=k}
end
local function fields(row,names)
    local out=object()
    for _,k in ipairs(names)do local v=row[k];if type(v)=='string'or type(v)=='boolean'or numeric(v)then out[k]=v end end
    return out
end
local function value(o,key)
    if not o or not o.GetProperty then return 'UNAVAILABLE'end
    local v=o:GetProperty(key);return v==nil and 'ABSENT' or v
end
local cfg=assert(CSC_MILL_STUDY_CONFIG,'CSC_MILL_STUDY_CONFIG required')
assert(type(cfg.targets)=='table'and #cfg.targets==2,'Exactly two city scopes required')
local family={
    'BUILDING_CSC_BAKERS_RIVER_ACCESS','BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',
    'BUILDING_CSC_BAKERS_WIND_MILL','BUILDING_CSC_BAKERS_WATER_MILL',
    'BUILDING_CSC_BAKERS_BAKERY','BUILDING_CSC_BAKERS_CAFE',
    'BUILDING_CSC_BAKERS_STAGE_2_SERVICE','BUILDING_CSC_BAKERS_STAGE_3_SERVICE',
    'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER','BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',
    'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP','BUILDING_CSC_TAILORS_TAILOR','BUILDING_CSC_TAILORS_FASHION_HOUSE',
    'BUILDING_CSC_TAILORS_STAGE_2_SERVICE','BUILDING_CSC_TAILORS_STAGE_3_SERVICE',
    'BUILDING_CSC_TAILORS_STAGE_4_SERVICE','BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',
    'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY','BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY'}
local quarterTypes={'DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER'}
local millRules={'CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS','CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER'}
local bits={1,2,4,8,16,32,64,128,256,512}
local out={schema=1,profile='mill-building-study-v1',readOnly=true,turn=Game.GetCurrentGameTurn(),
    mapping={family={},quarters={}},targets={},yields={},regionalRecipients={},
    metadata={buildings={},prerequisites={},mutualExclusions={},specialists={},flatYields={},
        buildingRoots={},serviceDistrictRoots={},modifiers={},modifierArguments={},
        adjacencyRules={},unitSteps={}},coverage={citycenterBitDefinitions='external pinned ledger; outside candidate building root coverage'}}
out.width,out.height=Map.GetGridSize();out.mapWidth,out.mapHeight=out.width,out.height
local function bounds(name)
    local count,maxIndex,seenIndex=0,-1,{}
    for r in GameInfo[name]()do
        assert(numeric(r.Index)and r.Index>=0 and r.Index==math.floor(r.Index)and not seenIndex[r.Index],
            'Malformed native catalog '..name)
        seenIndex[r.Index]=true;count=count+1;maxIndex=math.max(maxIndex,r.Index)
    end
    return count,maxIndex+1
end
out.mapping.buildingCount,out.mapping.buildingIndexLimit=bounds('Buildings')
out.mapping.districtCount,out.mapping.districtIndexLimit=bounds('Districts')
out.mapping.buildingsDense=out.mapping.buildingCount==out.mapping.buildingIndexLimit
out.mapping.districtsDense=out.mapping.districtCount==out.mapping.districtIndexLimit
local wanted={}
for _,name in ipairs(family)do
    local r=assert(GameInfo.Buildings[name],'Missing study building '..name);wanted[name]=true
    out.mapping.family[#out.mapping.family+1]={type=name,index=r.Index}
    out.metadata.buildings[#out.metadata.buildings+1]=fields(r,{'Index','BuildingType','PrereqDistrict','PrereqTech','PrereqCivic',
        'Cost','Maintenance','CitizenSlots','Entertainment','RegionalRange','MustPurchase','RequiresPlacement'})
end
table.sort(out.mapping.family,function(a,b)return a.index<b.index end)
for _,name in ipairs(quarterTypes)do
    local r=assert(GameInfo.Districts[name],'Missing study Quarter '..name)
    out.mapping.quarters[#out.mapping.quarters+1]={type=name,index=r.Index}
end
for r in GameInfo.Yields()do out.yields[#out.yields+1]={index=r.Index,type=r.YieldType,defaultValue=r.DefaultValue}end
table.sort(out.yields,function(a,b)return a.index<b.index end)
for ordinal,r in ipairs((function()local a={};for x in GameInfo.BuildingPrereqs()do a[#a+1]=x end;return a end)())do
    if wanted[r.Building]then out.metadata.prerequisites[#out.metadata.prerequisites+1]=
        {ordinal=ordinal,building=r.Building,prerequisite=r.PrereqBuilding,index=GameInfo.Buildings[r.PrereqBuilding].Index}end
end
for r in GameInfo.MutuallyExclusiveBuildings()do
    if wanted[r.Building]then out.metadata.mutualExclusions[#out.metadata.mutualExclusions+1]=fields(r,{'Building','MutuallyExclusiveBuilding'})end
end
for _,entry in ipairs({{'Building_CitizenYieldChanges','specialists'},{'Building_YieldChanges','flatYields'}})do
    for r in GameInfo[entry[1]]()do if wanted[r.BuildingType]then out.metadata[entry[2]][#out.metadata[entry[2]]+1]=fields(r,{'BuildingType','YieldType','YieldChange'})end end
end
local roots,mods,args,dynamic={},{},{},{}
for r in GameInfo.BuildingModifiers()do
    if wanted[r.BuildingType]then roots[r.ModifierId]=true;out.metadata.buildingRoots[#out.metadata.buildingRoots+1]={building=r.BuildingType,modifier=r.ModifierId}end
end
for r in GameInfo.DistrictModifiers()do
    if r.ModifierId=='MOD_CSC_BAKERS_RIVER_ACCESS_FLAG'or r.ModifierId=='MOD_CSC_BAKERS_NO_RIVER_ACCESS_FLAG'then
        roots[r.ModifierId]=true;out.metadata.serviceDistrictRoots[#out.metadata.serviceDistrictRoots+1]={district=r.DistrictType,modifier=r.ModifierId}
    end
end
for r in GameInfo.Modifiers()do mods[r.ModifierId]=r end
for r in GameInfo.ModifierArguments()do args[r.ModifierId]=args[r.ModifierId]or{};args[r.ModifierId][#args[r.ModifierId]+1]=r end
for r in GameInfo.DynamicModifiers()do dynamic[r.ModifierType]=r end
local seen,propertyNames={},{ }
local function visit(id)
    if seen[id]then return end;seen[id]=true
    local r=assert(mods[id],'Missing active modifier '..id)
    local kind=assert(dynamic[r.ModifierType],'Missing dynamic modifier '..r.ModifierType)
    local row=fields(r,{'ModifierId','ModifierType','OwnerRequirementSetId','SubjectRequirementSetId'})
    row.CollectionType=kind.CollectionType;row.EffectType=kind.EffectType;row.root=not not roots[id]
    if DB and DB.MakeHash then
        if r.SubjectRequirementSetId then local hash=DB.MakeHash(r.SubjectRequirementSetId);if numeric(hash)then row.subjectRequirementHash=hash end end
    end
    out.metadata.modifiers[#out.metadata.modifiers+1]=row
    for _,a in ipairs(args[id]or{})do
        out.metadata.modifierArguments[#out.metadata.modifierArguments+1]=fields(a,{'ModifierId','Name','Value','Type'})
        if a.Name=='ModifierId'then visit(a.Value)elseif a.Name=='Key'then propertyNames[a.Value]=true end
    end
end
local names={};for id in pairs(roots)do names[#names+1]=id end;table.sort(names)
for _,id in ipairs(names)do visit(id)end
for r in GameInfo.CSC_AdjacencyRules()do
    if r.DistrictType==quarterTypes[1]or r.DistrictType==quarterTypes[2]then
        out.metadata.adjacencyRules[#out.metadata.adjacencyRules+1]=fields(r,{'ID','DistrictType','ProvideType','YieldType','YieldChange',
            'AdjacencyType','CustomAdjacentObject','Rings','MinRings','MaxRings','MustOwn','ModifierOwner','WhoIsTheOwner','CollectionType'})
    end
end
for r in GameInfo.CSC_AdjacencyUnitSteps()do out.metadata.unitSteps[#out.metadata.unitSteps+1]=fields(r,{'ID','MaxAmount'})end
for _,key in ipairs({'CSC_HAS_BAKERS_QUARTER','CSC_BAKERS_STAGE_3_MARKET_CUSTOMER_POP','CSC_BAKERS_STAGE_3_MARKET_RETURN_AMOUNT',
    'CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT','CSC_BAKERS_STAGE_4_CAFE_RETURN','CSC_BAKERS_STAGE_4_ZOO_CULTURE_RETURN',
    'CSC_BAKERS_STAGE_4_FERRIS_CULTURE_RETURN','CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN',
    'CSC_TAILORS_STAGE_3_CUSTOMER_POP','CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT','CSC_TAILORS_STAGE_3_MARKET_CULTURE_AMOUNT',
    'CSC_TAILORS_STAGE_3_TEMPLE_CULTURE_AMOUNT','CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN',
    'CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN','CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN',
    'CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN','CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN',
    'CSC_BAKERS_IMPORT_CONSUMER_ROUTE','CSC_BAKERS_IMPORT_SPECIALTY_ROUTE','CSC_BAKERS_EXPORT_BAKERY_ROUTE','CSC_BAKERS_EXPORT_CAFE_ROUTE',
    'CSC_TAILORS_IMPORT_TAILOR_ROUTE','CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE','CSC_TAILORS_EXPORT_TAILOR_ROUTE','CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE'})do propertyNames[key]=true end
names={};for key in pairs(propertyNames)do names[#names+1]=key end;table.sort(names);out.propertyNames=names
local A=CSC_Adjacency
if not A and type(include)=='function'then local ok,message=pcall(include,'CSC_AdjacencyCore');if not ok then out.adjacencyError=tostring(message)end;A=CSC_Adjacency end
if A then local ok,message=pcall(A.Initialize);if not ok then out.adjacencyError=tostring(message);A=nil end end
out.sharedAdjacencyAvailable=not not A
local function propertyValues(owner)
    local result={};for _,key in ipairs(out.propertyNames)do result[#result+1]=value(owner,key)end;return result
end
local function millValues(plot)
    local result={}
    for index,id in ipairs(millRules)do
        local key='CSC_ADJ_'..id;local row={rule=index,legacyBits={},steps={},total=value(plot,key..'_TOTAL'),
            actual=value(plot,key..'_ACTUAL_AMOUNT'),encoded=value(plot,key..'_ENCODED_AMOUNT')}
        for _,bit in ipairs(bits)do row.legacyBits[#row.legacyBits+1]=value(plot,key..'_'..bit)end
        for step=1,(index==1 and 1 or 3)do row.steps[#row.steps+1]=value(plot,key..'_STEP_'..step)end
        result[#result+1]=row
    end
    return result
end
out.millPropertySchema={rules=millRules,legacyBits=bits,stepCounts={1,3},absent='ABSENT'}
local function plotFacts(plot,pid)
    local r={index=plot:GetIndex(),x=plot:GetX(),y=plot:GetY(),owner=plot:GetOwner(),district=plot:GetDistrictType(),
        resource=plot:GetResourceType(),improvement=plot:GetImprovementType(),feature=plot:GetFeatureType(),terrain=plot:GetTerrainType(),
        improvementPillaged=call(plot,'IsImprovementPillaged'),hills=call(plot,'IsHills'),river=call(plot,'IsRiver'),
        riverEdges=call(plot,'GetRiverCrossingCount'),workers=call(plot,'GetWorkerCount')}
    if PlayersVisibility and PlayersVisibility[pid]then r.revealed=call(PlayersVisibility[pid],'IsRevealed',r.x,r.y)end
    return r
end
local customerTypes={'BUILDING_GRANARY','BUILDING_MARKET','BUILDING_ZOO','BUILDING_FERRIS_WHEEL','BUILDING_LIGHTHOUSE',
    'BUILDING_TEMPLE','BUILDING_AMPHITHEATER','BUILDING_BOLSHOI_THEATRE','BUILDING_BROADWAY','BUILDING_SYDNEY_OPERA_HOUSE','BUILDING_LEU_CONSERVATORY'}
local neededTech,neededCivic={},{ }
for _,r in ipairs(out.metadata.buildings)do if r.PrereqTech then neededTech[r.PrereqTech]=true end;if r.PrereqCivic then neededCivic[r.PrereqCivic]=true end end
for _,key in ipairs({'TECH_IRRIGATION','TECH_ENGINEERING','TECH_MACHINERY','TECH_CONSTRUCTION'})do neededTech[key]=true end
for _,key in ipairs({'CIVIC_CRAFTSMANSHIP','CIVIC_FEUDALISM','CIVIC_MEDIEVAL_FAIRES','CIVIC_URBANIZATION','CIVIC_NAVAL_TRADITION','CIVIC_DIVINE_RIGHT','CIVIC_OPERA_BALLET'})do neededCivic[key]=true end
local duplicate,regionalSeen={},{ }
for _,scope in ipairs(cfg.targets)do
    assert(numeric(scope.player)and numeric(scope.city)and numeric(scope.plot),'Numeric player/city/plot required')
    local key=scope.player..':'..scope.city;assert(not duplicate[key],'Duplicate city scope');duplicate[key]=true
    local target={player=scope.player,city=scope.city,plot=scope.plot,exists=false}
    out.targets[#out.targets+1]=target
    local player=Players[scope.player]
    if player then
        target.human=player:IsHuman();target.alive=player:IsAlive();target.major=player:IsMajor()
        target.unlocks={techs=object(),civics=object()}
        for name in pairs(neededTech)do local r=GameInfo.Technologies[name];if r then target.unlocks.techs[name]=call(player:GetTechs(),'HasTech',r.Index)end end
        for name in pairs(neededCivic)do local r=GameInfo.Civics[name];if r then target.unlocks.civics[name]=call(player:GetCulture(),'HasCivic',r.Index)end end
        for _,city in player:GetCities():Members()do
            local regional={player=scope.player,city=city:GetID(),x=city:GetX(),y=city:GetY(),population=city:GetPopulation()}
            local regionalKey=scope.player..':'..city:GetID()
            if not regionalSeen[regionalKey]then regionalSeen[regionalKey]=true;out.regionalRecipients[#out.regionalRecipients+1]=regional end
            if city:GetID()==scope.city then
                target.exists=true;target.name=city:GetName();target.x=city:GetX();target.y=city:GetY();target.population=city:GetPopulation()
                local center=assert(Map.GetPlot(target.x,target.y));local bs,ds,q=city:GetBuildings(),city:GetDistricts(),city:GetBuildQueue()
                target.cityProperties=propertyValues(city);target.centerProperties=propertyValues(center)
                target.gold=call(player:GetTreasury(),'GetGoldBalance')
                target.queue={production=call(q,'CurrentlyBuilding'),hash=call(q,'GetCurrentProductionTypeHash'),size=call(q,'GetSize')}
                target.growth=object();local growth=city:GetGrowth()
                for _,method in ipairs({'GetAmenities','GetAmenitiesNeeded','GetHousing','GetFoodSurplus','GetHappiness'})do target.growth[method]=call(growth,method)end
                target.yields={};for _,y in ipairs(out.yields)do target.yields[#target.yields+1]={type=y.type,index=y.index,value=call(city,'GetYield',y.index)}end
                target.buildings={};target.customers={};target.districts={};target.cityTiles={};target.hasQuarters=object()
                for _,b in ipairs(out.mapping.family)do target.buildings[#target.buildings+1]={type=b.type,index=b.index,present=bs:HasBuilding(b.index),
                    pillaged=call(bs,'IsPillaged',b.index),location=call(bs,'GetBuildingLocation',b.index),progress=call(q,'GetBuildingProgress',b.index)}end
                for _,name in ipairs(customerTypes)do local b=GameInfo.Buildings[name];if b then target.customers[#target.customers+1]={type=name,index=b.Index,
                    present=bs:HasBuilding(b.Index),pillaged=call(bs,'IsPillaged',b.Index),location=call(bs,'GetBuildingLocation',b.Index)}end end
                assert(ds.GetNumDistricts and ds.GetDistrictByIndex,'Gameplay indexed district API required')
                for _,d in ipairs(out.mapping.quarters)do target.hasQuarters[d.type]=false end
                for i=0,ds:GetNumDistricts()-1 do
                    local d=ds:GetDistrictByIndex(i)
                    if d then local p=assert(Map.GetPlot(d:GetX(),d:GetY()));local definition=assert(GameInfo.Districts[d:GetType()])
                        local row={index=d:GetType(),type=definition.DistrictType,plot=p:GetIndex(),x=d:GetX(),y=d:GetY(),complete=call(d,'IsComplete'),pillaged=call(d,'IsPillaged'),workers=call(p,'GetWorkerCount')}
                        if target.hasQuarters[definition.DistrictType]~=nil then target.hasQuarters[definition.DistrictType]=true;row.millProperties=millValues(p)end
                        target.districts[#target.districts+1]=row
                    end
                end
                local plot=assert(Map.GetPlotByIndex(scope.plot),'Declared candidate missing')
                target.candidate=plotFacts(plot,scope.player);target.candidate.millProperties=millValues(plot)
                target.candidate.adjacency={}
                for _,district in ipairs(out.mapping.quarters)do
                    local item={district=district.type,index=district.index,legal=call(plot,'CanHaveDistrict',district.index,scope.player,scope.city),rules={}}
                    if A then for _,r in ipairs(A.ByDistrict[district.type]or{})do
                        local ok,count,amount,eligible=pcall(function()local n=A.Count(r,plot,city,scope.player);return n,A.Amount(r,n),A.Eligible(r,city,scope.player)end)
                        local entry={rule=r.ID,provider=r.ProvideType,yield=r.YieldType,owner=r.ModifierOwner,building=r.WhoIsTheOwner}
                        if ok then entry.count=count;entry.amount=amount;entry.eligible=eligible else entry.error=tostring(count)end
                        item.rules[#item.rules+1]=entry
                    end end
                    target.candidate.adjacency[#target.candidate.adjacency+1]=item
                end
                local tiles=A and A.PlotsInBand(center,0,3)or{center}
                target.cityTilesRadius=A and 3 or 0
                for _,p in ipairs(tiles)do target.cityTiles[#target.cityTiles+1]=plotFacts(p,scope.player)end
            end
        end
    end
end
out.mappingVerified=out.mapping.buildingsDense and out.mapping.districtsDense and #out.mapping.family==19 and #out.mapping.quarters==2
out.player0={exists=Players[0]~=nil,human=Players[0]and Players[0]:IsHuman()or false}
out.sourceValidation={mappingVerified=out.mappingVerified,targetsExist=true,targetsAI=true,ownedEmptyCandidates=true,noQuarterAtSource=true}
local nativeTargets={}
for _,target in ipairs(out.targets)do
    if not target.exists then out.sourceValidation.targetsExist=false end
    if not(target.alive and target.major and target.human==false)then out.sourceValidation.targetsAI=false end
    if not(target.candidate and target.candidate.owner==target.player and target.candidate.district==-1)then out.sourceValidation.ownedEmptyCandidates=false end
    for _,present in pairs(target.hasQuarters or{})do if present then out.sourceValidation.noQuarterAtSource=false end end
    nativeTargets[#nativeTargets+1]={player=target.player,city=target.city}
end
out.sourceValidation.valid=out.mappingVerified and out.sourceValidation.targetsExist and out.sourceValidation.targetsAI
    and out.sourceValidation.ownedEmptyCandidates and out.sourceValidation.noQuarterAtSource
out.observerConfig={profile='mill-building-study-v1',mappingVerified=out.mappingVerified,targets=nativeTargets,buildings=out.mapping.family,
    districtIndices={out.mapping.quarters[1].index,out.mapping.quarters[2].index},buildingCount=out.mapping.buildingCount,
    districtCount=out.mapping.districtCount,mapWidth=out.width,mapHeight=out.height,maxPairs=16384,maxCallbacks=300000,
    maxThreads=8,maxDepth=16,maxRows=37,maxModifierName=256}
-- Repeated long definition identifiers are dictionary cells inside metadata.
-- The world facts and observerConfig remain ordinary JSON for controller gates.
local strings,stringIDs={},{ }
local function cell(v)
    if v==nil then return 'ABSENT'end
    if type(v)=='string'and #v>=20 then local index=stringIDs[v];if not index then index=#strings+1;strings[index]=v;stringIDs[v]=index end;return{s=index}end
    return v
end
local tableNames={};for name in pairs(out.metadata)do tableNames[#tableNames+1]=name end;table.sort(tableNames)
for _,name in ipairs(tableNames)do
    local rows=out.metadata[name];local columns,seenColumns={},{ }
    for _,r in ipairs(rows)do for k in pairs(r)do if not seenColumns[k]then seenColumns[k]=true;columns[#columns+1]=k end end end;table.sort(columns)
    local compact={columns=columns,rows={},absent='ABSENT'}
    for _,r in ipairs(rows)do local values={};for _,k in ipairs(columns)do values[#values+1]=cell(r[k])end;compact.rows[#compact.rows+1]=values end
    out.metadata[name]=compact
end
out.databaseStrings=strings;out.metadataEncoding='Each {s:N} cell references databaseStrings[N], one-based; ABSENT marks an omitted field.'
-- Radius-three plot rows repeat the same numeric fields. A shared column list
-- retains every fact without spending the Tuner budget on repeated field names.
out.cityTileColumns={'index','x','y','owner','district','resource','improvement','feature','terrain',
    'improvementPillaged','hills','river','riverEdges','workers','revealed'}
for _,target in ipairs(out.targets)do if target.cityTiles then
    local rows={}
    for _,plot in ipairs(target.cityTiles)do
        local row={};for _,key in ipairs(out.cityTileColumns)do local v=plot[key];row[#row+1]=v==nil and 'ABSENT'or v end;rows[#rows+1]=row
    end
    target.cityTiles=rows
end end
-- Keep every Tuner record below its per-print limit. Hex framing is independent
-- of JSON escaping/UTF-8 boundaries; the controller validates and rejoins bytes.
local payload=json(out)
assert(#payload<1024*1024,'World receipt exceeds one MiB transport bound')
local checksum=0
for i=1,#payload do checksum=(checksum+payload:byte(i))%4294967296 end
local parts=math.ceil(#payload/512)
for part=1,parts do
    local raw=payload:sub((part-1)*512+1,part*512)
    local hex=raw:gsub('.',function(c)return string.format('%02x',c:byte())end)
    print('CSC_MILL_BUILDING_WORLD_CHUNK='..json({schema=1,part=part,parts=parts,
        bytes=#payload,sum32=checksum,encoding='hex',data=hex}))
end
return out
