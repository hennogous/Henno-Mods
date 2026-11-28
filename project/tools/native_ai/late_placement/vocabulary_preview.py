"""After saving the endpoint, test signed city switches against native UI previews."""
import re
from driver import require, write_json


def inspect(c,out,turn):
    scan="""
local found={}
local d=GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER
for pid=1,5 do
 for _,city in Players[pid]:GetCities():Members() do
  local center=Map.GetPlot(city:GetX(),city:GetY())
  for x=-3,3 do for y=-3,3 do
   local p=Map.GetPlotXYWithRangeCheck(city:GetX(),city:GetY(),x,y,3)
   if p and p:GetOwner()==pid and p:CanHaveDistrict(d.Index,pid,city:GetID()) then
    local owner=Cities.GetPlotPurchaseCity(p)
    if owner and owner:GetID()==city:GetID() then
     local counts={}
     local function add(k) counts[k]=(counts[k] or 0)+1 end
     if p:IsRiver() then add('RIVER') end
     for j=0,5 do
      local n=Map.GetAdjacentPlot(p:GetX(),p:GetY(),j)
      if n then
       add(GameInfo.Terrains[n:GetTerrainType()].TerrainType)
       local f=GameInfo.Features[n:GetFeatureType()]
       local i=GameInfo.Improvements[n:GetImprovementType()]
       if f then add(f.FeatureType) end
       if i then add(i.ImprovementType) end
       if n:GetDistrictType()>=0 then add('ANY_DISTRICT') end
      end
     end
     local keys={}; for k in pairs(counts) do keys[#keys+1]=k end; table.sort(keys)
     for _,k in ipairs(keys) do
      local category=k:match('^[^_]+')
      if k=='TERRAIN_COAST' or k:match('_MOUNTAIN$') then category='SPECIAL_TERRAIN' end
      local id='CSC_AI_VOC_'..d.DistrictType..'__'
      if not found[category] and center:GetProperty(id..'P_'..k)~=1 and center:GetProperty(id..'N_'..k)~=1 then
       local old='NONE'
       for _,sign in ipairs({'F_','U_','D_'}) do
        if center:GetProperty(id..sign..k)==1 then old=sign..k end
       end
       print('VOC_PROBE_SITE',category,k,pid,city:GetID(),p:GetIndex(),counts[k],old)
       found[category]=true
      end
     end
    end
   end
  end end
 end
end
print('VOC_SCAN_DONE')
"""
    raw=c.cmd(scan,'PlotInfo','find-native-vocabulary-examples')
    require('VOC_SCAN_DONE' in raw,'Failed to enumerate candidate sites')
    cases=re.findall(r'VOC_PROBE_SITE\s+(\w+)\s+(\w+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\w+)',raw)
    require(cases,'No legal site for the vocabulary probe')
    checks=[]
    for family,clue,player,city,plot,count,old in cases:
        prefix='CSC_AI_VOC_DISTRICT_CSC_TAILORS_QUARTER__'
        setup=f"""local city=assert(CityManager.GetCity({player},{city}))
local center=Map.GetPlot(city:GetX(),city:GetY())
local plus='{prefix}P_{clue}';local minus='{prefix}N_{clue}'
"""
        def value(label):
            code=f"""local p=Map.GetPlotByIndex({plot});print('VOC_VALUE',p:GetAdjacencyYield({player},{city},
                GameInfo.Districts.DISTRICT_CSC_TAILORS_QUARTER.Index,GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index))"""
            raw=c.cmd(code,'PlotInfo',f'{family}-{label}')
            return int(re.search(r'VOC_VALUE\s+(-?\d+)',raw)[1])
        baseline=value('baseline')
        prior=f"center:SetProperty('{prefix}{old}'," if old!='NONE' else None
        try:
            if prior:
                c.cmd(setup+prior+'0)','CSC_AI_BakersGameplay',family+'-withdraw-original')
            neutral=value('neutral') if prior else baseline
            c.cmd(setup+"""for _,id in ipairs({plus,minus}) do
 if city:GetProperty(id..'_BOUND')~=1 then city:AttachModifierByID(id);city:SetProperty(id..'_BOUND',1) end
end
center:SetProperty(plus,1)""",'CSC_AI_BakersGameplay',family+'-enable-positive')
            positive=value('positive')
            c.cmd(setup+"center:SetProperty(plus,0);center:SetProperty(minus,1)",'CSC_AI_BakersGameplay',family+'-enable-negative')
            negative=value('negative')
        finally:
            c.cmd(setup+"center:SetProperty(plus,0);center:SetProperty(minus,0)"+
                  (';'+prior+'1)' if prior else ''),'CSC_AI_BakersGameplay',family+'-restore-original')
        restored=value('restored')
        expected=int(count)*6
        checks.append(dict(family=family,clue=clue,player=player,city=city,plot=plot,count=count,
                           baseline=baseline,original=old,neutral=neutral,positive=positive,negative=negative,restored=restored,
                           matches=positive-neutral==expected and neutral-negative==expected and restored==baseline))
        write_json(out/'vocabulary-previews.json',dict(turn=turn,cases=checks))
