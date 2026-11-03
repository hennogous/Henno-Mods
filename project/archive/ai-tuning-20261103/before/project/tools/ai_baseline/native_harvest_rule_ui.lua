-- Read native runtime instances in the UI context used by the existing probe.
-- Expose a read-only bridge, as the acquisition quote reader does.
ExposedMembers=ExposedMembers or {}
local E=assert(GameEffects,'Native GameEffects reader unavailable in UI')
assert(type(E.GetModifiers)=='function'and type(E.GetModifierDefinition)=='function'and type(E.GetModifierActive)=='function'and type(E.GetModifierOwner)=='function'and type(E.GetObjectsPlayerId)=='function','Runtime modifier API unavailable')
local currentTurn=Game.GetCurrentGameTurn
local function snapshot()
 local rows={}
 for _,id in ipairs(E.GetModifiers())do
  local def=E.GetModifierDefinition(id)
  if def and def.Id=='TRAIT_MAORI_PREVENT_HARVEST'then
   local owner=E.GetModifierOwner(id);local pid=E.GetObjectsPlayerId(owner);local active=E.GetModifierActive(id)
   local label=type(E.GetObjectString)=='function'and E.GetObjectString(owner)or tostring(owner)
   rows[#rows+1]={runtime_id=tostring(id),player=type(pid)=='number'and pid or -999,owner=tostring(label),active=active==true or active==1}
  end
 end
 table.sort(rows,function(a,b)if a.player~=b.player then return a.player<b.player end;return a.runtime_id<b.runtime_id end)
 return {ui_turn=currentTurn(),instances=rows}
end
ExposedMembers.CSC_NATIVE_HARVEST_RULE_UI={Snapshot=snapshot}
