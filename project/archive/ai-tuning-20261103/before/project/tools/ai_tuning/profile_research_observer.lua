-- Read-only natural research history. No grants, preferences, properties or queues.
assert(not CSC_SERIES_RESEARCH)
CSC_SERIES_RESEARCH={version=1,history={},completions={},defeats={},errors={},seen={},duplicate_callbacks=0}
local R=CSC_SERIES_RESEARCH
local function json(v)
 local t=type(v)
 if t=='nil' then return 'null' end
 if t=='number' or t=='boolean' then return tostring(v) end
 if t=='string' then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"' end
 local parts,array,count={},true,0
 for k in pairs(v)do count=count+1;if type(k)~='number'then array=false end end
 if count~=#v then array=false end
 if array then for _,x in ipairs(v)do parts[#parts+1]=json(x)end;return '['..table.concat(parts,',')..']'end
 for k,x in pairs(v)do parts[#parts+1]=json(tostring(k))..':'..json(x)end
 return '{'..table.concat(parts,',')..'}'
end
local function optional(fn)
 local ok,v=pcall(fn);return {observed=ok,value=ok and v or nil,error=not ok and tostring(v)or nil}
end
local function safe(fn)
 return function(...)local ok,e=pcall(fn,...);if not ok then R.errors[#R.errors+1]={turn=Game.GetCurrentGameTurn(),error=tostring(e)}end end
end
Events.PlayerTurnDeactivated.Add(safe(function(pid)
 if pid<1 or pid>5 then return end
 local p=Players[pid];if not p or not p:IsAlive()or not p:IsMajor()then return end
 local turn=Game.GetCurrentGameTurn();local key=turn..':'..pid
 if R.seen[key]then R.duplicate_callbacks=R.duplicate_callbacks+1;return end
 R.seen[key]=true
 local culture=p:GetCulture();local techs=p:GetTechs();local civic=GameInfo.Civics[culture:GetProgressingCivic()]
 local ownedTechs,ownedCivics={},{}
 for row in GameInfo.Technologies()do if techs:HasTech(row.Index)then ownedTechs[#ownedTechs+1]=row.TechnologyType end end
 for row in GameInfo.Civics()do if culture:HasCivic(row.Index)then ownedCivics[#ownedCivics+1]=row.CivicType end end
 R.history[#R.history+1]={turn=turn,player=pid,civic=civic and civic.CivicType or 'NONE',tech=optional(function()local r=GameInfo.Technologies[techs:GetResearchingTech()];return r and r.TechnologyType or 'NONE'end),completed_techs=ownedTechs,completed_civics=ownedCivics,cities=p:GetCities():GetCount()}
end))
Events.CivicCompleted.Add(safe(function(pid,index,cancelled)
 if pid>=1 and pid<=5 and cancelled~=true and cancelled~=1 then local row=GameInfo.Civics[index];R.completions[#R.completions+1]={turn=Game.GetCurrentGameTurn(),player=pid,kind='civic',item=row and row.CivicType or tostring(index)}end
end))
if Events.ResearchCompleted then Events.ResearchCompleted.Add(safe(function(pid,index)
 if pid>=1 and pid<=5 then local row=GameInfo.Technologies[index];R.completions[#R.completions+1]={turn=Game.GetCurrentGameTurn(),player=pid,kind='technology',item=row and row.TechnologyType or tostring(index)}end
end))end
Events.PlayerDefeat.Add(safe(function(pid)if pid>=1 and pid<=5 then R.defeats[#R.defeats+1]={turn=Game.GetCurrentGameTurn(),player=pid}end end))
function R.Export()
 print('CSC_SERIES_RESEARCH='..json({version=R.version,turn=Game.GetCurrentGameTurn(),history=R.history,completions=R.completions,defeats=R.defeats,errors=R.errors,duplicate_callbacks=R.duplicate_callbacks}))
end
print('CSC_SERIES_RESEARCH_READY')
