-- Opt-in cosmetic acknowledgement of the shipped NaturalWonderPopup only.
-- Fresh Core proof belongs to the sole controller; never activate a turn here.
local coreTurn=__CORE_TURN__
local targetTurn=__TARGET_TURN__
local active=__CORE_ACTIVE__
local remaining=__REMAINING__
local coreLocal=__CORE_LOCAL__
local coreHuman=__CORE_HUMAN__
local path='/InGame/WorldPopups/NaturalWonderPopup'
local function json(v)
 local t=type(v)
 if t=='nil'then return 'null'end
 if t=='boolean'or t=='number'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 local n,array=0,true;for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end;local a={}
 if array then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end
 return '{'..table.concat(a,',')..'}'
end
local function stack()
 if not UIManager or type(UIManager.GetPopupStack)~='function'then return {unavailable=true}end
 local ok,value=pcall(function()return UIManager:GetPopupStack()end)
 if not ok then return {read_error=tostring(value)}end
 local rows={}
 for _,entry in ipairs(value or{})do rows[#rows+1]={id=entry.ID,priority=entry.Priority,flags=entry.Flags}end
 return rows
end
local out={coreTurn=coreTurn,target=targetTurn,active=active,remaining=remaining,coreLocal=coreLocal,coreHuman=coreHuman,
 source_path=path,uiTurn=Game.GetCurrentGameTurn(),uiLocal=Game.GetLocalPlayer(),requested=false}
local function finish(reason)
 out.reason=reason
 print('CSC_NATURAL_WONDER_GUARD='..json(out))
end
if active~=true or coreLocal~=-1 or coreHuman~=false or remaining<1 or remaining>5 or targetTurn-coreTurn~=remaining then finish('core_proof_rejected');return end
-- UI must report the same clock as the fresh Core proof. Its local-player role
-- may still be the original human because the popup owns the playback hold.
if out.uiTurn~=coreTurn or(out.uiLocal~=-1 and out.uiLocal~=0)then finish('ui_phase_rejected');return end
out.hidden=ContextPtr:IsHidden()
local source=ContextPtr:LookUpControl(path)
if source==nil then finish('source_context_missing');return end
out.path_hidden=source:IsHidden()
out.path_visible=source:IsVisible()
if out.hidden or out.path_hidden or not out.path_visible then finish('hidden');return end
out.popup_stack_before=stack()
if type(Close)~='function'then finish('shipped_close_missing');return end
-- Retain the visibility/stack proof before the single possible native callback.
print('CSC_NATURAL_WONDER_BEFORE='..json(out))
Close()
out.requested=true
out.hidden_after=ContextPtr:IsHidden()
out.popup_stack_after=stack()
finish('shipped_cosmetic_close')
print('CSC_NATURAL_WONDER_RELEASE_REQUESTED',coreTurn,out.uiTurn,out.uiLocal,out.hidden_after)
