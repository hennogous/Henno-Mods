-- Exact building locations exist in Gameplay, not on UI CityBuildings.
-- Export only own major AI buildings; never infer a venue from its district type.
local rows={}
for pid=1,5 do local p=Players[pid]
 if p and p:IsAlive()and p:IsMajor()and not p:IsHuman()then
  for _,c in p:GetCities():Members()do local b=c:GetBuildings()
   for d in GameInfo.Buildings()do if b:HasBuilding(d.Index)and not b:IsPillaged(d.Index)then
    rows[#rows+1]='{"owner":'..pid..',"city":'..c:GetID()..',"plot":'..b:GetBuildingLocation(d.Index)..',"type":'..string.format('%q',d.BuildingType)..',"functioning":true}'
   end end
  end
 end
end
print('CSC_SERVICE_VENUES={"turn":'..Game.GetCurrentGameTurn()..',"venues":['..table.concat(rows,',')..']}')
