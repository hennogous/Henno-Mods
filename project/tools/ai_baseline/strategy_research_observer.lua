-- Read-only observation. No research setters, grants or preference changes.
assert(CSC_RESEARCH_PROBE_NATIVE and not CSC_RESEARCH_PROBE,'Observer already installed')
local R={history={},completions={},defeats={},errors={},owned={},initial={},version='natural-decisions-v1'}
CSC_RESEARCH_PROBE=R
local function json(v)
 local kind=type(v)
 if kind=='nil' then return 'null' end
 if kind=='number' or kind=='boolean' then return tostring(v) end
 if kind=='string' then return string.format('%q',v) end
 local parts,array,count={},true,0
 for k in pairs(v) do count=count+1;if type(k)~='number' then array=false end end
 if count~=#v then array=false end
 if array then for _,x in ipairs(v) do parts[#parts+1]=json(x) end;return '['..table.concat(parts,',')..']' end
 for k,x in pairs(v) do parts[#parts+1]=json(tostring(k))..':'..json(x) end
 return '{'..table.concat(parts,',')..'}'
end
local function capture(pid)
 local player=Players[pid];local culture=player:GetCulture()
 local def=GameInfo.Civics[culture:GetProgressingCivic()]
 local completed={};local known=R.owned[pid] or {}
 for civic in GameInfo.Civics() do
  if culture:HasCivic(civic.Index) and not known[civic.CivicType] then
   completed[#completed+1]=civic.CivicType;known[civic.CivicType]=true
  end
 end
 R.owned[pid]=known
 local native=CSC_RESEARCH_PROBE_NATIVE
 return {turn=Game.GetCurrentGameTurn(),player=pid,civic=def and def.CivicType or 'NONE',naval_completed=culture:HasCivic(GameInfo.Civics.CIVIC_NAVAL_TRADITION.Index),new_completed=completed,stock_first_true=native.first_true[tostring(pid)..':1'],custom_first_true=native.first_true[tostring(pid)..':2']}
end
for pid=1,5 do R.initial[#R.initial+1]=capture(pid) end
local function safe(fn)
 return function(...)
  local ok,err=pcall(fn,...)
  if not ok then R.errors[#R.errors+1]={turn=Game.GetCurrentGameTurn(),error=tostring(err)} end
 end
end
Events.PlayerTurnDeactivated.Add(safe(function(pid)
 if pid>=1 and pid<=5 then
  R.history[#R.history+1]=capture(pid)
  Game:SetProperty('CSC_TEST_RESEARCH_OBSERVATIONS',{history=R.history,completions=R.completions,defeats=R.defeats})
 end
end))
Events.CivicCompleted.Add(safe(function(pid,index,cancelled)
 if pid>=1 and pid<=5 and cancelled~=true and cancelled~=1 then
  local def=GameInfo.Civics[index]
  R.completions[#R.completions+1]={turn=Game.GetCurrentGameTurn(),player=pid,civic=def and def.CivicType or tostring(index)}
 end
end))
Events.PlayerDefeat.Add(safe(function(pid)
 if pid>=1 and pid<=5 then R.defeats[#R.defeats+1]={turn=Game.GetCurrentGameTurn(),player=pid} end
end))
function R.Export(request)
 print('CSC_TEST_EXPORT_BEGIN',request,#R.history,#R.completions)
 print('CSC_TEST_EXPORT='..json({turn=Game.GetCurrentGameTurn(),history=R.history,completions=R.completions,defeats=R.defeats,initial=R.initial,errors=R.errors,native=CSC_RESEARCH_PROBE_NATIVE}))
 print('CSC_TEST_EXPORT_END',request,#R.history,#R.completions)
end
