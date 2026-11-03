-- Read-only initial census for future campaign arms. Invoke once before play.
-- The installed host's receipt exporter supplies the local json() serializer.
assert(Game.GetCurrentGameTurn()==1,'Initial census requires native turn1');
local out={turn=1,phase='before-external-autoplay',plots={},players={},units={},cities={}};
local width,height=Map.GetGridSize();out.width=width;out.height=height;
for i=0,Map.GetPlotCount()-1 do
 local p=Map.GetPlotByIndex(i);
 local terrain=GameInfo.Terrains[p:GetTerrainType()];
 local feature=GameInfo.Features[p:GetFeatureType()];
 local resource=GameInfo.Resources[p:GetResourceType()];
 out.plots[#out.plots+1]={index=i,x=p:GetX(),y=p:GetY(),terrain=terrain and terrain.TerrainType,
  feature=feature and feature.FeatureType,resource=resource and resource.ResourceType,
  resource_count=p:GetResourceCount(),continent=p:GetContinentType(),owner=p:GetOwner(),
  hills=p:IsHills(),water=p:IsWater(),river=p:IsRiver(),lake=p:IsLake(),
  impassable=p:IsImpassable(),starting_plot=p:IsStartingPlot()};
end;
for _,p in ipairs(PlayerManager.GetAliveMajors())do
 local start=p.GetStartingPlot and p:GetStartingPlot()or nil;
 local config=PlayerConfigurations[p:GetID()];
 out.players[#out.players+1]={player=p:GetID(),leader=config:GetLeaderTypeName(),
  starting_plot=start and start:GetIndex(),starting_plot_getter_observed=start~=nil,
  gold=p:GetTreasury():GetGoldBalance()};
 for _,u in p:GetUnits():Members()do
  local info=GameInfo.Units[u:GetType()];
  out.units[#out.units+1]={player=p:GetID(),id=u:GetID(),type=info and info.UnitType,
   x=u:GetX(),y=u:GetY(),damage=u:GetDamage()};
 end;
 for _,c in p:GetCities():Members()do
  out.cities[#out.cities+1]={player=p:GetID(),id=c:GetID(),x=c:GetX(),y=c:GetY(),name=c:GetName()};
 end;
end;
print('CSC_PROFILE_INITIAL='..json(out));
