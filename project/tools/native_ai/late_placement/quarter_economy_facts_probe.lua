-- Diagnostic-only. Read the central facts and native UI numbers in an ordinary
-- loaded game; publish no policy, orders, properties, gold or research changes.
local ui=assert(ExposedMembers.CSC_Adjacency)
local P=assert(CSC_AI_QuarterPlacement)
local requireReady=CSC_QUARTER_FACTS_REQUIRE_READY==true
local finiteSites,knownCapacity=0,0
if requireReady then
 for _,name in ipairs({'GetEconomyCityNumber','GetEconomyResearchNumbers','GetEconomyPlotFacts','GetDistrictCapacity'})do
  assert(type(ui[name])=='function','Missing economic UI reader '..name)
 end
end
local function read(f,...)local ok,v=pcall(f,...);return ok and tostring(v)or'error:'..tostring(v)end
for _,player in ipairs(PlayerManager.GetAliveMajors())do if not player:IsHuman()then
 local pid=player:GetID();local s=CSC_AI_EconomyAdapters.Snapshot(player,P,ui)
 assert(s,'Economic snapshot unavailable')
 for _,city in player:GetCities():Members()do
  local c=s.DistrictCapacity(city)
  if c.known then knownCapacity=knownCapacity+1 end
  print('CSC_QUARTER_CAPACITY_PROBE',pid,city:GetID(),tostring(c.population),tostring(c.used),tostring(c.allowed),c.reason)
 end
 local count=0
 for _,profile in ipairs(P.StageTwoProfiles())do
  for _,city in player:GetCities():Members()do
   if not city:GetDistricts():HasDistrict(profile.district.Index)then
    for _,plot in ipairs(CSC_Adjacency.PlotsInBand(Map.GetPlot(city:GetX(),city:GetY()),1,3))do
     local owner=plot:GetOwner();local assigned=owner==pid and Cities.GetPlotPurchaseCity(plot)
     if count<8 and assigned and assigned:GetID()==city:GetID()and plot:GetDistrictType()==-1
       and PlayersVisibility[pid]:IsRevealed(plot:GetX(),plot:GetY())then
      local geometry=s.Geometry(city,plot,profile)
      if geometry.upper>=3 then
       count=count+1;local site,message=s.Site(city,plot,profile)
       if site and site.quarterReady<math.huge then finiteSites=finiteSites+1 end
       print('CSC_QUARTER_FACT_PROBE',pid,city:GetID(),profile.key,plot:GetIndex(),
        'adjacency='..tostring(geometry.upper),'production='..tostring(s.cities[city:GetID()].production),
        'costUI='..read(ui.GetEconomyCityNumber,pid,city:GetID(),'district',profile.district.Index),
        'costGameplay='..read(city:GetBuildQueue().GetDistrictCost,city:GetBuildQueue(),profile.district.Index),
        'tech='..tostring(profile.district.PrereqTech),'civic='..tostring(profile.district.PrereqCivic),
        'techTurns='..read(s.Research,'tech',profile.district.PrereqTech),
        'civicTurns='..read(s.Research,'civic',profile.district.PrereqCivic),
        'quarterReady='..tostring(site and site.quarterReady),'reason='..tostring(message))
      end
     end
    end
   end
  end
 end
end end
assert(not requireReady or finiteSites>0,'No qualifying site has finite Quarter readiness')
assert(not requireReady or knownCapacity>0,'No live capacity facts agreed with Gameplay')
print('CSC_QUARTER_FACT_PROBE_COMPLETE',finiteSites)
