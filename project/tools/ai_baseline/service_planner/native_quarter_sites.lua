-- Read-only physical sites include natural and assisted, complete or unfinished.
-- UI cannot reliably enumerate district locations; import native Gameplay facts.
local out={turn=Game.GetCurrentGameTurn(),cities={}}
local quarters={}
for _,key in ipairs({'BAKERS','TAILORS'})do
 local def=assert(GameInfo.Districts['DISTRICT_CSC_'..key..'_QUARTER']);quarters[def.Index]=key
end
for _,player in ipairs(PlayerManager.GetAliveMajors())do
 local pid=player:GetID()
 if pid>=1 and pid<=5 then for _,c in player:GetCities():Members()do
  local key=tostring(pid)..':'..tostring(c:GetID());out.cities[key]={}
  local districts=c:GetDistricts()
  for i=0,districts:GetNumDistricts()-1 do
   local d=districts:GetDistrictByIndex(i);local quarter=quarters[d:GetType()]
   if quarter then
    local p=Map.GetPlot(d:GetX(),d:GetY());assert(p:GetOwner()==pid,'Quarter source owner mismatch')
    local row={plot=p:GetIndex(),quarter=quarter,complete=d:IsComplete(),neighbors={}}
    for _,near in ipairs(Map.GetAdjacentPlots(p:GetX(),p:GetY()))do row.neighbors[#row.neighbors+1]=near:GetIndex()end
    table.insert(out.cities[key],row)
   end
  end
 end end
end
local function json(v)
 local kind=type(v);if kind=='nil'then return 'null'end
 if kind=='number'or kind=='boolean'then return tostring(v)end
 if kind=='string'then return string.format('%q',v)end
 local a={};local n=0;local array=true;for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end
 if array then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(a,',')..'}'
end
print('CSC_QUARTER_SITES='..json(out))
