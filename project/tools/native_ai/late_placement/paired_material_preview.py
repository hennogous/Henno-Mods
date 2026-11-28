"""Read the AI's active local terrain cues on stock district candidates at a paused boundary."""
import re
from driver import require, write_json


def observe(controller, folder, turn):
    scan = """
local y=GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index
local best, bestRange=nil,0
for _,p in ipairs(PlayerManager.GetAliveMajors()) do
 for _,city in p:GetCities():Members() do
  local center=Map.GetPlot(city:GetX(),city:GetY())
  for d in GameInfo.Districts() do
   local key='CSC_AI_PAIR_ACTIVE_'..d.DistrictType
   local first,second=center:GetProperty(key..1),center:GetProperty(key..2)
   if first then
    local low,high,lo,hi=99,-99
    for dx=-3,3 do for dy=-3,3 do
     local s=Map.GetPlotXYWithRangeCheck(city:GetX(),city:GetY(),dx,dy,3)
     if s and s:GetOwner()==p:GetID() and s:CanHaveDistrict(d.Index,p:GetID(),city:GetID()) then
      local score=0
      for dir=0,5 do
       local adj=Map.GetAdjacentPlot(s:GetX(),s:GetY(),dir)
       if adj then
        local terrain=GameInfo.Terrains[adj:GetTerrainType()].TerrainType
        for _,rule in ipairs({first,second}) do
         local sign,t=string.match(rule,'__([PN])_(TERRAIN_.+)$')
         if t==terrain then score=score+(sign=='P' and 2 or -2) end
        end
       end
      end
      if score<low then low,lo=score,s:GetIndex() end
      if score>high then high,hi=score,s:GetIndex() end
     end
    end end
    local priority=high-low
    if second and priority>0 then priority=priority+100 end
    if priority>bestRange then
     bestRange=priority;best={p:GetID(),city:GetID(),d.Index,hi,lo,high,low,first,second or '-'}
    end
   end
  end
 end
end
if best then
 for _,p in ipairs(PlayerManager.GetAliveMajors()) do
  for _,city in p:GetCities():Members() do
   if p:GetID()~=best[1] or city:GetID()~=best[2] then
    for dx=-3,3 do for dy=-3,3 do
     local s=Map.GetPlotXYWithRangeCheck(city:GetX(),city:GetY(),dx,dy,3)
     if s and s:GetOwner()==p:GetID() and s:CanHaveDistrict(best[3],p:GetID(),city:GetID()) then
      print('CSC_PAIR_OTHER',p:GetID(),city:GetID(),s:GetIndex())
      print('CSC_PAIR_READABLE',table.concat(best,',')); return
     end
    end end
   end
  end
 end
 print('CSC_PAIR_READABLE',table.concat(best,','))
else print('CSC_PAIR_WAIT') end
"""
    raw=controller.cmd(scan,'PlotInfo','find-active-pair-'+str(turn))
    if 'CSC_PAIR_WAIT' in raw:
        return
    found=re.search(r'CSC_PAIR_READABLE\s+([\w,\-]+)',raw)
    require(found,'Missing active city readback')
    fields=found[1].split(',')
    pid,city,district,high,low,expected_high,expected_low=map(int,fields[:7])
    rules=[s for s in fields[7:] if s!='-']
    other=re.search(r'CSC_PAIR_OTHER\s+(\d+)\s+(\d+)\s+(\d+)',raw)
    sites=[(pid,city,high),(pid,city,low)]
    expected=[expected_high,expected_low]
    if other:
        sites.append(tuple(map(int,other.groups())))
        expected.append(0)
    def read(label):
        query=f"local y=GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index;print('CSC_PAIR_VALUES',"+','.join(
            f'Map.GetPlotByIndex({i}):GetAdjacencyYield({p},{c},{district},y)' for p,c,i in sites)+')'
        match=re.search(r'CSC_PAIR_VALUES'+r'\s+([-\d.]+)'*len(sites),controller.cmd(query,'PlotInfo',label))
        require(match,'Missing adjacency readback')
        return list(map(float,match.groups()))
    def set_gates(value):
        query=f'local c=CityManager.GetCity({pid},{city});local p=Map.GetPlot(c:GetX(),c:GetY());'
        controller.cmd(query+';'.join(f"p:SetProperty('{r}',{value})" for r in rules),
                       'GameCore_Tuner','temporary-pair-gates-'+str(value))
    before=read('pair-active')
    try:
        set_gates(0)
        off=read('pair-withdrawn')
    finally:
        set_gates(1)
    restored=read('pair-restored')
    delta=[a-b for a,b in zip(before,off)]
    write_json(folder/f'pair-preview-{turn}.json',dict(turn=turn,city=city,player=pid,district=district,
               plots=[high,low],rules=rules,on=before,off=off,restored=restored,delta=delta,
               expected=expected,other_city=sites[2:] or None))
    require(restored==before and delta==expected,'Signed adjacency differs from prediction')
