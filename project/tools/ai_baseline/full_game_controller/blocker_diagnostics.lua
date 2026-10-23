-- Read-only observer diagnostics. No diplomatic response/session control.
local function safe(fn) local ok,v=pcall(fn);if ok then return v end;return {read_error=tostring(v)} end
local function clean(v,depth)
 local kind=type(v)
 if kind=='nil'or kind=='number'or kind=='boolean'or kind=='string'then return v end
 if kind~='table'or depth>3 then return tostring(v)end
 local out={};for k,x in pairs(v)do out[tostring(k)]=clean(x,depth+1)end;return out
end
local function json(v)
 local t=type(v);if t=='nil'then return 'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 local a={};for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(a,',')..'}'
end
local out={turn=Game.GetCurrentGameTurn(),local_player=Game.GetLocalPlayer(),
 hidden=safe(function()return ContextPtr:IsHidden()end),player0_human=safe(function()return Players[0]:IsHuman()end),sessions={},
 active_session=ms_ActiveSessionID,view_local_player=ms_LocalPlayerID}
if DiplomacyManager and type(DiplomacyManager.FindOpenSessionID)=='function'then
 for other=1,5 do
  out.sessions[tostring(other)]=safe(function()
   local id=DiplomacyManager.FindOpenSessionID(0,other)
   if id==nil or id<0 then return {open=false}end
   return {id=id,open=DiplomacyManager.IsSessionIDOpen(id),info=clean(DiplomacyManager.GetSessionInfo(id),0)}
  end)
 end
end
if ms_ActiveSessionID~=nil and DiplomacyManager then
 out.active_info=safe(function()return clean(DiplomacyManager.GetSessionInfo(ms_ActiveSessionID),0)end)
end
print('CSC_BLOCKER_DIAGNOSTICS='..json(out))
