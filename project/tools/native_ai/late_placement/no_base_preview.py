"""Disposable intra-turn comparison of a naturally active Quarter gate and a supplied city."""
import re

from driver import write_json


def observe(controller, folder, turn):
    # Select two cities for the same Quarter type. Use a real legal footprint
    # in each. The comparison reads stock adjacency; the paired games record
    # construction later and do not require any instrumentation in CE.
    search = """
local y=GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index
for d in GameInfo.Districts() do
 local key='CSC_AI_NO_BASE_'..d.DistrictType
 local sites={}
 for _,p in ipairs(PlayerManager.GetAliveMajors()) do
  for _,city in p:GetCities():Members() do
   local reason=city:GetProperty(key..'_REASON')
   local center=Map.GetPlot(city:GetX(),city:GetY())
   if (reason=='absent' and center:GetProperty(key)==1 or reason=='base' and center:GetProperty(key)~=1)
     and not city:GetDistricts():HasDistrict(d.Index) then
    for dx=-3,3 do for dy=-3,3 do
     local s=Map.GetPlotXYWithRangeCheck(city:GetX(),city:GetY(),dx,dy,3)
     if s and s:GetOwner()==p:GetID() and s:CanHaveDistrict(d.Index,p:GetID(),city:GetID()) then
      local adj=s:GetAdjacencyYield(p:GetID(),city:GetID(),d.Index,y)
      if not sites[reason] or adj>sites[reason][4] then
       sites[reason]={p:GetID(),city:GetID(),s:GetIndex(),adj}
      end
     end
    end end
   end
  end
 end
 if sites.absent and sites.base then
  print('CSC_GATE_PAIR',key,d.Index,table.concat(sites.absent,','),table.concat(sites.base,','))
  return
 end
end
print('CSC_GATE_WAIT')
"""
    raw=controller.cmd(search,'PlotInfo',f'find-no-base-pair-{turn}')
    if 'CSC_GATE_WAIT' in raw:
        return
    match=re.search(r'CSC_GATE_PAIR\s+(\w+)\s+(\d+)\s+([-\d.,]+)\s+([-\d.,]+)',raw)
    if not match:
        raise ValueError('Missing native city-pair readback: '+raw[-450:])
    key,district=match[1],int(match[2])
    absent,base=([int(float(n)) for n in v.split(',')] for v in match.groups()[2:])

    def gate(value):
        controller.cmd(f"local c=CityManager.GetCity({absent[0]},{absent[1]});"
                       f"Map.GetPlot(c:GetX(),c:GetY()):SetProperty('{key}',{value})",
                       'GameCore_Tuner',f'no-base-gate-{value}')

    def preview(label):
        cells=[f'Map.GetPlotByIndex({site}):GetAdjacencyYield({pid},{city},{district},y)'
               for pid,city,site,_ in (absent,base)]
        result=controller.cmd("local y=GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index\n"
                              +"print('CSC_GATE_READ',"+','.join(cells)+")",'PlotInfo','no-base-'+label)
        row=re.search(r'CSC_GATE_READ\s+([-\d.]+)\s+([-\d.]+)',result)
        if not row:
            raise ValueError('Missing paired adjacency previews')
        return [float(n) for n in row.groups()]

    on=[absent[3],base[3]]
    try:
        gate(0)
        off=preview('off')
    finally:
        gate(1)
    restored=preview('restored')
    write_json(folder/'no-base-preview.json',dict(turn=turn,district=district,gate=key,
               absent=absent[:3],base=base[:3],on=on,off=off,restored=restored,
               native_penalty=on[0]-off[0],protected_change=on[1]-off[1]))
    if restored!=on or off[1]!=on[1]:
        raise ValueError('Withdrawing and restoring the gate changed the protected comparison')
