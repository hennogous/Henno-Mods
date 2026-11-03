-- Test-controller-only, read-only completion observations. No turn-by-turn
-- world export: append only the first observed completion for each city/site.
local B=assert(CSCBASE,'Install the primary observer first');
CSC_COMPLETION_OBSERVER={version=1,calls=0,major_calls=0,observations=0,seen={},ready=false};
local S=CSC_COMPLETION_OBSERVER;
local kinds={};
for _,key in ipairs({'BAKERS','TAILORS'})do
 local d=GameInfo.Districts['DISTRICT_CSC_'..key..'_QUARTER'];
 if d then kinds[d.Index]={key=key,type=d.DistrictType}end;
end;
local function identity(pid,cid,plot,kind)return pid..':'..cid..':'..plot..':'..kind end;
function S.Observe(pid)
 S.calls=S.calls+1;
 local p=Players[pid];if not p or not p:IsAlive()or not p:IsMajor()then return end;
 S.major_calls=S.major_calls+1;
 if not S.ready then
  -- On same-world recovery, inherited observations already live in B.events.
  for _,e in ipairs(B.events)do if e.event=='quarter_completion_observed'then
   S.seen[identity(e.player,e.city,e.plot,e.quarter_type)]=true;
  end end;
  S.ready=true;
 end;
 for _,city in p:GetCities():Members()do
  local districts=city:GetDistricts();
  for i=0,districts:GetNumDistricts()-1 do
   local d=districts:GetDistrictByIndex(i);local kind=kinds[d:GetType()];
   if kind and d:IsComplete()then
    local plot=Map.GetPlot(d:GetX(),d:GetY()):GetIndex();local id=identity(pid,city:GetID(),plot,kind.key);
    if not S.seen[id]then
     S.seen[id]=true;S.observations=S.observations+1;
     B.events[#B.events+1]={event='quarter_completion_observed',turn=Game.GetCurrentGameTurn(),
      player=pid,city=city:GetID(),plot=plot,quarter_type=kind.key,district_type=kind.type,
      complete=true,pillaged=d:IsPillaged(),phase='PlayerTurnDeactivated',
      evidence='native IsComplete readback; first observation for city/site, not exact completion-event time'};
    end;
   end;
  end;
 end;
end;
local function observe(pid)
 local ok,err=pcall(S.Observe,pid);
 if not ok and #B.errors<20 then B.errors[#B.errors+1]='completion observer: '..tostring(err)end;
end;
assert(Events.PlayerTurnDeactivated,'Native PlayerTurnDeactivated event unavailable');
Events.PlayerTurnDeactivated.Add(observe);
local capture=B.capture;
B.capture=function()
 local out=capture();out.completion_observer={version=S.version,calls=S.calls,major_calls=S.major_calls,observations=S.observations};return out;
end;
print('CSC_COMPLETION_OBSERVER_READY',S.version);
