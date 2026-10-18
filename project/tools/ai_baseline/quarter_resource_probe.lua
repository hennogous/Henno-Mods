-- UI-safe read-only supply signal census: scan plots, not gameplay district APIs.
local y=GameInfo.Yields['YIELD_CSC_AI_PLACEMENT'].Index
local out={turn=Game.GetCurrentGameTurn(),plots={},errors={}}
local tags={}
for t in GameInfo.TypeTags() do if t.Tag:match('^CLASS_CSC_') then tags[t.Type]=tags[t.Type] or {};tags[t.Type][t.Tag]=true end end
local function visible(player,res)
 if res.PrereqTech then local t=GameInfo.Technologies[res.PrereqTech];return t and player:GetTechs():HasTech(t.Index) end
 if res.PrereqCivic then local c=GameInfo.Civics[res.PrereqCivic];return c and player:GetCulture():HasCivic(c.Index) end
 return true
end
local targets={}
for idx=0,Map.GetPlotCount()-1 do
 local p=Map.GetPlotByIndex(idx);local pid=p:GetOwner();local player=pid>=0 and Players[pid]
 local district=GameInfo.Districts[p:GetDistrictType()];local q=district and district.DistrictType:match('^DISTRICT_CSC_(.-)_QUARTER$')
 if player and not player:IsHuman() and (q=='BAKERS' or q=='TAILORS') then
  for dir=0,5 do
   local n=Map.GetAdjacentPlot(p:GetX(),p:GetY(),dir);local res=n and GameInfo.Resources[n:GetResourceType()]
   if n and n:GetOwner()==pid and res and visible(player,res) and tags[res.ResourceType] and (tags[res.ResourceType]['CLASS_CSC_'..q..'_BASE'] or tags[res.ResourceType]['CLASS_CSC_'..q..'_SPEC']) then
    local k=n:GetIndex();targets[k]=targets[k] or {player=pid,count=0};targets[k].count=targets[k].count+1
   end
  end
 end
end
for idx,t in pairs(targets) do
 local p=Map.GetPlotByIndex(idx);local improved=p:GetImprovementType()~=-1 and not p:IsImprovementPillaged()
 local expected=t.count*(40+(improved and 80 or 0));local actual=p:GetYield(y)
 out.plots[#out.plots+1]={player=t.player,plot=idx,sources=t.count,improved=improved,pillaged=p:IsImprovementPillaged(),expected=expected,actual=actual}
 if actual~=expected then out.errors[#out.errors+1]={plot=idx,expected=expected,actual=actual} end
end
local function json(v)
 local t=type(v);if t=='nil' then return 'null' end;if t=='boolean' or t=='number' then return tostring(v) end
 if t=='string' then return string.format('%q',v) end
 local a={};local array=true;local n=0;for k in pairs(v) do n=n+1;if type(k)~='number' then array=false end end
 if n~=#v then array=false end
 if array then for _,x in ipairs(v) do a[#a+1]=json(x) end;return '['..table.concat(a,',')..']' end
 for k,x in pairs(v) do a[#a+1]=json(k)..':'..json(x) end;return '{'..table.concat(a,',')..'}'
end
print('CSC_QR_SIGNAL='..json(out))
