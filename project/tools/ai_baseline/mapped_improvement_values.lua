-- Read-only controls for the newly covered resource/improvement pairs.
-- Isolated rows exclude Quarter/care/pillage contributions; other rows are
-- observations only. A missing positive control is UNOBSERVED, never success.
local function json(v)
 local t=type(v);if t=='nil'then return 'null'end;if t=='number'or t=='boolean'then return tostring(v)end;
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r')..'"'end;
 local a={};local n=0;local arr=true;for k in pairs(v)do n=n+1;if type(k)~='number'then arr=false end end;if n~=#v then arr=false end;
 if arr then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end;
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(a,',')..'}';
end;
local prefix='MOD_CSC_AI_MAPPED_IMPROVEMENT_';local sets={};local reqs={};local types={};
for row in GameInfo.RequirementArguments()do if row.Name=='ResourceType'then reqs[row.RequirementId]=row.Value end end;
for row in GameInfo.RequirementSetRequirements()do if reqs[row.RequirementId]then local s=sets[row.RequirementSetId]or {};s[reqs[row.RequirementId]]=true;sets[row.RequirementSetId]=s end end;
local mods={};for row in GameInfo.Modifiers()do mods[row.ModifierId]=row end;
for row in GameInfo.ImprovementModifiers()do local id=assert(row.ModifierID,'Native ImprovementModifiers.ModifierID missing');if id:sub(1,#prefix)==prefix then local m=assert(mods[id]);types[row.ImprovementType]=assert(sets[m.OwnerRequirementSetId])end end;
local raw={};for row in GameInfo.Resource_YieldChanges()do if row.YieldType=='YIELD_CSC_AI_PLACEMENT'then raw[row.ResourceType]=(raw[row.ResourceType]or 0)+row.YieldChange end end;
local out={turn=Game.GetCurrentGameTurn(),rows={},eligible_isolated_controls=0,excluded_isolated_controls=0,failed_eligible=0,failed_excluded=0};
for i=0,Map.GetPlotCount()-1 do local p=Map.GetPlotByIndex(i);local owner=p:GetOwner();local imp=GameInfo.Improvements[p:GetImprovementType()];
 if owner>=1 and owner<=5 and imp and types[imp.ImprovementType]then
  local r=GameInfo.Resources[p:GetResourceType()];local resource=r and r.ResourceType or nil;
  local row={plot=i,owner=owner,resource=resource,improvement=imp.ImprovementType,private=p:GetYield(GameInfo.Yields.YIELD_CSC_AI_PLACEMENT.Index),raw_resource_private=resource and(raw[resource]or 0)or 0,pillaged=p:IsImprovementPillaged(),adjacent_Quarter=false,
   care_base=p:GetProperty('CSC_AI_CARE_LAST_BASE')or 0,care_spec=p:GetProperty('CSC_AI_CARE_LAST_SPEC')or 0,care_redundant=p:GetProperty('CSC_AI_CARE_REDUNDANT')or 0};
  for direction=0,5 do local q=Map.GetAdjacentPlot(p:GetX(),p:GetY(),direction);local d=q and GameInfo.Districts[q:GetDistrictType()];if d and d.DistrictType:match('^DISTRICT_CSC_')then row.adjacent_Quarter=true end end;
  row.eligible=resource and types[row.improvement][resource]or false;
  row.isolated=not row.pillaged and not row.adjacent_Quarter and row.care_base==0 and row.care_spec==0 and row.care_redundant==0;
  if row.isolated then
   row.expected_private=row.raw_resource_private+(row.eligible and 80 or 0);
   if row.eligible then out.eligible_isolated_controls=out.eligible_isolated_controls+1;if row.private~=row.expected_private then out.failed_eligible=out.failed_eligible+1 end;
   else out.excluded_isolated_controls=out.excluded_isolated_controls+1;if row.private~=row.expected_private then out.failed_excluded=out.failed_excluded+1 end end;
  end;
  out.rows[#out.rows+1]=row;
 end;
end;
print('CSC_MAPPED_IMPROVEMENT_VALUES='..json(out));
