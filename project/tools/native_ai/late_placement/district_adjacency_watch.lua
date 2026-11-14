-- DIAGNOSTIC ONLY. Observe the UI's own foundation/completion notifications,
-- so Core->UI lag does not erase the placement adjacency evidence. These are
-- UI-event-time values, not a native forecast or proof of exact Core call time.
-- No bids, orders, properties, yields or random numbers are changed.
assert(not CSC_DISTRICT_ADJACENCY_WATCH,'Duplicate UI district observer')
CSC_DISTRICT_ADJACENCY_WATCH={seen={}}
local W=CSC_DISTRICT_ADJACENCY_WATCH
local function sample(source,player,districtID,cityID,x,y,kind)
 local ui=assert(ExposedMembers.CSC_Adjacency)
 local plot=assert(Map.GetPlot(x,y))
 local value=assert(ui.GetDistrictAdjacency(player,cityID,plot:GetIndex(),kind))
 local d=Players[player]and Players[player]:GetDistricts():FindID(districtID)
 local stage=d and d:IsComplete()and'complete'or'foundation'
 local signature=table.concat({player,cityID,districtID,plot:GetIndex(),kind,stage},':')
 if W.seen[signature]then return end
 W.seen[signature]=true
 local row={source=source,player=player,city=cityID,districtID=districtID,
  plot=plot:GetIndex(),district=kind,stage=stage,turn=Game.GetCurrentGameTurn(),
  available=value.available,footprintMatches=value.plotDistrict==kind,uiEventTime=true,
  exactNativeCallTime=false}
 for k,v in pairs(value.yields or{})do row[k]=v end
 local fields={};for k,v in pairs(row)do fields[#fields+1]=k..'='..tostring(v)end
 table.sort(fields);print('CSC_DISTRICT_UI_ADJACENCY\t'..table.concat(fields,'\t'))
end
local function record(source,...)
 local ok,error=pcall(sample,source,...)
 if not ok then print('CSC_DISTRICT_UI_FAULT',Game.GetCurrentGameTurn(),tostring(error))end
end
Events.DistrictAddedToMap.Add(function(...)record('added',...)end)
Events.DistrictBuildProgressChanged.Add(function(...)record('progress',...)end)
print('CSC_DISTRICT_UI_INSTALLED',Game.GetCurrentGameTurn())
