-- Deliberately limited offline Civ resource API. Never a claim of engine parity.
unpack=unpack or table.unpack
math.pow=math.pow or function(a,b)return a^b end
math.mod=math.fmod
table.maxn=table.maxn or function(t)local n=0;for k in pairs(t)do if type(k)=='number' and k>n then n=k end end;return n end
print=OFFLINE_LOG
include=OFFLINE_INCLUDE
ExposedMembers={}
g_FEATURE_NONE=-1
g_RESOURCE_NONE=-1
DB={Query=OFFLINE_QUERY}
local W,H=OFFLINE_DATA.width,OFFLINE_DATA.height
local properties={}
Game={GetProperty=function(_,k)return properties[k] end,SetProperty=function(_,k,v)properties[k]=v end}
MapConfiguration={GetValue=function(k)if k=='resources' then return OFFLINE_SETTING elseif k=='rainfall' then return 2 end end}
GameInfo={}
local function info(rows,key)
  local t={}
  for _,r in ipairs(rows)do
    if r.Index then t[r.Index]=r end
    if key and r[key] then t[r[key]]=r end
  end
  return setmetatable(t,{__call=function()local i=0;return function()i=i+1;return rows[i]end end})
end
for name,rows in pairs(OFFLINE_TABLES)do
 local key=({Resources='ResourceType',Features='FeatureType',Terrains='TerrainType',Maps='MapSizeType'})[name]
 GameInfo[name]=info(rows,key)
end
for _,r in ipairs(OFFLINE_TABLES.Terrains)do
 _G['g_'..r.TerrainType..'_INDEX']=r.Index
 _G['g_'..r.TerrainType]=r.Index
 _G['g_'..r.TerrainType:gsub('TERRAIN_','TERRAIN_TYPE_')]=r.Index
end
for _,r in ipairs(OFFLINE_TABLES.Features)do _G['g_'..r.FeatureType]=r.Index end
DirectionTypes={NUM_DIRECTION_TYPES=6,DIRECTION_NORTHEAST=0,DIRECTION_EAST=1,DIRECTION_SOUTHEAST=2,DIRECTION_SOUTHWEST=3,DIRECTION_WEST=4,DIRECTION_NORTHWEST=5}
MapSizeTypes={MAPSIZE_DUEL=0,MAPSIZE_TINY=1,MAPSIZE_SMALL=2,MAPSIZE_STANDARD=3,MAPSIZE_LARGE=4,MAPSIZE_HUGE=5}
local plotMethods={}
function plotMethods:GetX()return self.x end
function plotMethods:GetY()return self.y end
function plotMethods:GetIndex()return self.index end
function plotMethods:IsWater()return self.water end
function plotMethods:IsLake()return self.lake end
function plotMethods:IsHills()return self.hills end
function plotMethods:IsMountain()return self.terrain:find('MOUNTAIN')~=nil end
function plotMethods:IsRiver()return self.river end
function plotMethods:GetContinentType()return self.continent end
function plotMethods:GetTerrainType()return GameInfo.Terrains[self.terrain].Index end
function plotMethods:GetFeatureType()return self.feature and GameInfo.Features[self.feature].Index or -1 end
function plotMethods:GetResourceType()return self.resource and GameInfo.Resources[self.resource].Index or -1 end
plotMethods.GetResourceTypeHash=plotMethods.GetResourceType
function plotMethods:GetResourceCount()return self.resource and 1 or 0 end
for _,p in ipairs(OFFLINE_DATA.plots)do setmetatable(p,{__index=plotMethods})end
Map={}
function Map.GetGridSize()return W,H end
function Map.GetPlotCount()return W*H end
function Map.GetMapSize()return GameInfo.Maps[OFFLINE_DATA.map_size or 'MAPSIZE_SMALL'].Index end
function Map.IsWrapX()return OFFLINE_DATA.wrap_x~=false end
function Map.IsWrapY()return OFFLINE_DATA.wrap_y==true end
function Map.GetPlotByIndex(i)return OFFLINE_DATA.plots[i+1]end
function Map.GetPlot(x,y)
 if Map.IsWrapY() then y=y%H elseif y<0 or y>=H then return nil end
 if Map.IsWrapX() then x=x%W elseif x<0 or x>=W then return nil end
 return Map.GetPlotByIndex(math.floor(y*W+x))
end
function Map.GetAdjacentPlot(x,y,d)
 local parity=y%2
 local offsets={{parity,1},{1,0},{parity,-1},{parity-1,-1},{-1,0},{parity-1,1}}
 local v=offsets[d+1];return Map.GetPlot(x+v[1],y+v[2])
end
function Map.GetContinentsInUse()
 local seen,out={},{}
 for _,p in ipairs(OFFLINE_DATA.plots)do if p.continent>=0 and not seen[p.continent] then seen[p.continent]=true;out[#out+1]=p.continent end end
 table.sort(out);return out
end
function Map.GetContinentPlots(c)local out={};for _,p in ipairs(OFFLINE_DATA.plots)do if p.continent==c then out[#out+1]=p.index end end;return out end
function GetShuffledCopyOfTable(t)
 local out={};for i,v in ipairs(t)do out[i]=v end
 for i=#out,2,-1 do local j=OFFLINE_RANDOM(i,'shuffle')+1;out[i],out[j]=out[j],out[i]end
 return out
end
function IsAdjacentToIce(x,y)
 for d=0,5 do local p=Map.GetAdjacentPlot(x,y,d);if p and p.feature=='FEATURE_ICE' then return true end end
 return false
end
local validTerrain,validFeature,featureTerrain={},{},{}
for _,r in ipairs(OFFLINE_TABLES.Resource_ValidTerrains)do validTerrain[r.ResourceType..'|'..r.TerrainType]=true end
for _,r in ipairs(OFFLINE_TABLES.Resource_ValidFeatures)do validFeature[r.ResourceType..'|'..r.FeatureType]=true end
for _,r in ipairs(OFFLINE_TABLES.Feature_ValidTerrains)do featureTerrain[r.FeatureType..'|'..r.TerrainType]=true end
ResourceBuilder={}
function ResourceBuilder.CanHaveResource(p,r)
 if not p or p.resource or p:IsMountain() then return false end
 local row=GameInfo.Resources[r];if not row then error('Unknown resource index '..tostring(r))end
 if p.feature and GameInfo.Features[p.feature].NaturalWonder==1 then return false end
 if row.NoRiver==1 and p.river then return false end
 if row.RequiresRiver==1 and not p.river then return false end
 if p.lake and row.LakeEligible==0 then return false end
 if p.feature then return validFeature[row.ResourceType..'|'..p.feature] or false end
 if not validTerrain[row.ResourceType..'|'..p.terrain] then return false end
 if row.AdjacentToLand==1 then
  local near=false;for _,n in ipairs(p.neighbors)do if not Map.GetPlotByIndex(n).water then near=true;break end end
  if not near then return false end
 end
 return true
end
function ResourceBuilder.SetResourceType(p,r,count)
 if OFFLINE_PLACEMENT then OFFLINE_PLACEMENT(p.index,r==-1 and 'NONE' or GameInfo.Resources[r].ResourceType,count or -1) end
 if r==-1 then p.resource=nil;return end
 local row=GameInfo.Resources[r];assert(row,'Unknown resource');p.resource=row.ResourceType
end
function ResourceBuilder.GetAdjacentResourceCount(p)
 local n=0;for _,i in ipairs(p.neighbors)do if Map.GetPlotByIndex(i).resource then n=n+1 end end;return n
end
TerrainBuilder={GetRandomNumber=OFFLINE_RANDOM}
function TerrainBuilder.GetAdjacentFeatureCount(p,f)
 local n=0;for _,i in ipairs(p.neighbors)do if Map.GetPlotByIndex(i):GetFeatureType()==f then n=n+1 end end;return n
end
function TerrainBuilder.CanHaveFeature(p,f)
 local row=GameInfo.Features[f]
 return p and row and not p.feature and featureTerrain[row.FeatureType..'|'..p.terrain] or false
end
function TerrainBuilder.SetFeatureType(p,f)p.feature=f==-1 and nil or GameInfo.Features[f].FeatureType end
-- Unknown engine facilities fail immediately. No invented start-position/fractal results.
for _,name in ipairs({'Fractal','AreaBuilder','StartPositioner'})do
 _G[name]=setmetatable({},{__index=function(_,k)error('Native-only API unsupported offline: '..name..'.'..k)end})
end
