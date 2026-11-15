"""Read-only real-map valuation capture at an inactive controller boundary.

Captures at most eight plain economic ledgers after inspecting current legal
map potential. It never publishes an offer, changes a queue or edits the world.
The normal main-CSC publisher supplies every live bid in the qualification run.
"""
import json
import re
import time
from driver import read,require,write_json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def inspect(controller,out):
    # Reuse only the diagnostic JSON encoder, before the target loop.
    encoder=read(HERE/'economy_component_probe.lua').split('for _,target in ipairs(CSC_COMPONENT_TARGETS)do',1)[0]
    encoder=encoder[encoder.index('local function encode'):]
    code=encoder+'''
local P,M,E=CSC_AI_QuarterPlacement,CSC_AI_EconomyModel,CSC_AI_EconomyAdapters
local context=assert(CE_AIEvaluationContext(),'Native evaluation context unavailable')
print('CSC_NATIVE_CONTEXT='..context)
assert(CE_AIDistrictSiteAdjustment(-1,0,0,0,0,0,50,1024)==nil)
assert(CE_AIDistrictSiteAdjustment(1,0,-1,0,0,0,50,1024)==nil)
local samples={}
local examined,quoted=0,0
for _,player in ipairs(PlayerManager.GetAliveMajors())do if player:GetID()>=1 and player:GetID()<=5 and not player:IsHuman()then
 local snapshot=assert(E.Snapshot(player,P,ExposedMembers.CSC_Adjacency))
 for _,city in player:GetCities():Members()do
  local center=Map.GetPlot(city:GetX(),city:GetY())
  for _,profile in ipairs(P.StageTwoProfiles())do
   for _,plot in ipairs(CSC_Adjacency.PlotsInBand(center,1,3))do
    local owner=plot:GetOwner()
    if plot:GetDistrictType()==-1 and(owner==player:GetID()or owner==-1)then
     local geometry=snapshot.Geometry(city,plot,profile)
     if geometry.upper>=2 then
      examined=examined+1
      local site,why=snapshot.Site(city,plot,profile)
      if site and site.baseCount>0 then
       local q=M.Forecast(site,snapshot.Price,function(v)return E.PlacementValue(v,site)end)
       if q and q.valueQ8>0 then
        local bid,reason,parts=E.PlacementValue(q,site)
        if reason=='positive'then
         quoted=quoted+1
         local key=q.adjacency<3 and'two'or q.adjacency<4 and'three'or'fourPlus'
         local list=samples[key]or{};samples[key]=list
         list[#list+1]={player=player:GetID(),city=city:GetID(),quarter=profile.key,plot=plot:GetIndex(),
          turn=Game.GetCurrentGameTurn(),adjacency=q.adjacency,startingAdjacency=site.adjacency,
          base=site.baseCount,spec=site.specialtyCount,bidQ8=bid,parts=parts,quote=q,site=site,
          nativeNetQ8=site.nativeSiteNetQ8,nativeIntrinsicQ8=site.nativeIntrinsicQ8}
         table.sort(list,function(a,b)if a.bidQ8~=b.bidQ8 then return a.bidQ8>b.bidQ8 end;return a.plot<b.plot end)
         local cap=key=='fourPlus'and 4 or 2
         if #list>cap then list[#list]=nil end
        end
       end
      end
     end
    end
   end
  end
 end
end end
local n=0
for _,key in ipairs({'two','three','fourPlus'})do for _,row in ipairs(samples[key]or{})do
 if row.nativeNetQ8 and row.nativeIntrinsicQ8 then
  assert(row.nativeNetQ8-row.nativeIntrinsicQ8==row.site.nativeSiteAdjustmentQ8)
 end
 local raw,bid=row.quote.siteAdjustmentQ8,row.quote.siteAdjustmentQ8
 for _,s in ipairs(row.quote.streams)do raw=raw+s.valueQ8;bid=bid+s.bidValueQ8 end
 assert(raw==row.quote.valueQ8 and bid==row.quote.bidValueQ8)
 print('CSC_NATIVE_VALUATION='..encode(row));n=n+1
end end
print('CSC_NATIVE_VALUATION_COMPLETE='..encode({count=n,examined=examined,quoted=quoted,turn=Game.GetCurrentGameTurn()}))
'''
    start=time.monotonic()
    raw=controller.cmd(code,'CSC_AI_BakersGameplay','native-valuation-preflight')
    elapsed=time.monotonic()-start
    (out/'native-valuation-preflight.txt').write_text(raw,encoding='utf-8')
    def records(prefix):return [json.loads(x)for x in re.findall(prefix+r'=([^\r\n]+)',raw)]
    context=records('CSC_NATIVE_CONTEXT')
    rows=records('CSC_NATIVE_VALUATION')
    complete=records('CSC_NATIVE_VALUATION_COMPLETE')
    require(len(context)==len(complete)==1 and len(rows)==complete[0]['count'],'Incomplete native valuation qualification')
    write_json(out/'native-valuation-preflight.json',dict(read_only=True,context=context[0],
        summary=complete[0],records=rows,controller_command_seconds=elapsed))
