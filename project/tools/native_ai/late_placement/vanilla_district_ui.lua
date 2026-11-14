-- Passive no-CSC counterpart of CSC's ordinary UI adjacency reader. This is
-- observational stock API use, not an adjacency modifier or an AI preference.
assert(not GameInfo.Yields.YIELD_CSC_AI_PLACEMENT)
function CSC_DISTRICT_ADJACENCY_READER(player,city,index,kind)
 local plot=assert(Map.GetPlotByIndex(index))
 local row={available=true,plotDistrict=plot:GetDistrictType(),yields={}}
 for yield in GameInfo.Yields()do
  local amount=plot:GetAdjacencyYield(player,city,kind,yield.Index)
  assert(type(amount)=='number'or type(amount)=='integer','Non-numeric native adjacency')
  row.yields[yield.YieldType]=amount
 end
 return row
end
