-- Read-only complete map census. No plot/property/configuration writes.
local function json(v)
    local k=type(v);
    if k=='nil' then return 'null' end
    if k=='boolean' or k=='number' then return tostring(v) end
    if k=='string' then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t'):gsub('%z','')..'"' end
    if k~='table' then return 'null' end
    local n=0;local array=true;for key in pairs(v) do n=n+1;if type(key)~='number' then array=false end end
    if n~=#v then array=false end
    local parts={};if array then for _,x in ipairs(v) do parts[#parts+1]=json(x) end;return '['..table.concat(parts,',')..']' end
    for key,x in pairs(v) do parts[#parts+1]=json(tostring(key))..':'..json(x) end;return '{'..table.concat(parts,',')..'}'
end
local function kind(tab,index,field) local r=GameInfo[tab][index];return r and r[field] or nil end
local w,h=Map.GetGridSize();local s={turn=Game.GetCurrentGameTurn(),width=w,height=h,wrap_x=Map.IsWrapX(),wrap_y=Map.IsWrapY(),map_size=kind('Maps',Map.GetMapSize(),'MapSizeType'),plots={},players={},resources={},features={},terrains={},harvests={},material_tags={}};
for row in GameInfo.Resources() do s.resources[#s.resources+1]={type=row.ResourceType,class=row.ResourceClassType,tech=row.PrereqTech,civic=row.PrereqCivic} end
s.continents={};for row in GameInfo.Continents() do s.continents[#s.continents+1]={index=row.Index,type=row.ContinentType,name=Locale.Lookup(row.Description)} end
s.lua_version=_VERSION;s.starting_plots={};
for row in GameInfo.Features() do s.features[#s.features+1]={type=row.FeatureType,natural_wonder=row.NaturalWonder,removable=row.Removable,remove_tech=row.RemoveTech,impassable=row.Impassable} end
for row in GameInfo.Terrains() do s.terrains[#s.terrains+1]={type=row.TerrainType,hills=row.Hills,water=row.Water,impassable=row.Impassable} end
for row in GameInfo.Resource_Harvests() do s.harvests[#s.harvests+1]={resource=row.ResourceType,tech=row.PrereqTech} end
for row in GameInfo.TypeTags() do if row.Tag:match('^CLASS_CSC_.*_BASE$') or row.Tag:match('^CLASS_CSC_.*_SPEC$') then s.material_tags[#s.material_tags+1]={type=row.Type,tag=row.Tag} end end
for _,p in ipairs(PlayerManager.GetAliveMajors()) do local pc=PlayerConfigurations[p:GetID()];s.players[#s.players+1]={id=p:GetID(),leader=kind('Leaders',pc:GetLeaderTypeID(),'LeaderType'),civ=kind('Civilizations',pc:GetCivilizationTypeID(),'CivilizationType')} end
for index=0,w*h-1 do local p=Map.GetPlotByIndex(index);local ns={};for direction=0,5 do local a=Map.GetAdjacentPlot(p:GetX(),p:GetY(),direction);if a then ns[#ns+1]=a:GetIndex() end end
    if p:IsStartingPlot() then s.starting_plots[#s.starting_plots+1]=index end
    s.plots[#s.plots+1]={index=index,x=p:GetX(),y=p:GetY(),owner=p:GetOwner(),terrain=kind('Terrains',p:GetTerrainType(),'TerrainType'),feature=kind('Features',p:GetFeatureType(),'FeatureType'),resource=kind('Resources',p:GetResourceType(),'ResourceType'),resource_count=p:GetResourceCount(),district=kind('Districts',p:GetDistrictType(),'DistrictType'),water=p:IsWater(),hills=p:IsHills(),impassable=p:IsImpassable(),continent=p:GetContinentType(),river=p:IsRiver(),lake=p:IsLake(),neighbors=ns};
end
print('CSCMAP_SURVEY='..json(s));
