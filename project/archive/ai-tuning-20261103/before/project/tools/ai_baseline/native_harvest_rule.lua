-- Explicit native-rule diagnostic. No direct unit/economic/resource operation.
-- Uses a shipped definition already present in the source save's database.
CSC_NATIVE_HARVEST_RULE={version=1,definition='TRAIT_MAORI_PREVENT_HARVEST'}
local R=CSC_NATIVE_HARVEST_RULE
local function json(v)
 local t=type(v);if t=='nil'then return 'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 local out={};local array=true;local n=0;for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end
 if array then for _,x in ipairs(v)do out[#out+1]=json(x)end;return '['..table.concat(out,',')..']'end
 for k,x in pairs(v)do out[#out+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(out,',')..'}'
end
local function emit(v)print('CSC_NATIVE_RULE='..json(v));return v end
local function fresh(a)
 assert(Game.GetCurrentGameTurn()==a.turn and not AutoplayManager.IsActive(),'Inactive exact rule boundary required')
 assert(a.turn==16,'Diagnostic source16 only')
 for pid=1,5 do local p=assert(Players[pid]);assert(p:IsAlive()and p:IsMajor()and not p:IsHuman(),'Selected AI identity changed')end
end
local function snapshot()
 local bridge=assert(ExposedMembers.CSC_NATIVE_HARVEST_RULE_UI,'Read-only native UI bridge missing')
 local value=bridge.Snapshot();local turn=Game.GetCurrentGameTurn()
 assert(value.ui_turn==turn or value.ui_turn==turn-1,'Unexpected raw UI/Core phase')
 return value
end
local function read(a)
 local value=snapshot();return {turn=Game.GetCurrentGameTurn(),ui_turn=value.ui_turn,active=AutoplayManager.IsActive(),definition=R.definition,instances=value.instances,ledger=Game:GetProperty('CSC_NATIVE_RULE_'..a.token)}
end
function R.Read(a)return emit(read(a))end
function R.Begin(a)
 assert(a.enabled==true and type(a.token)=='string'and #a.token>0);fresh(a)
 local key='CSC_NATIVE_RULE_'..a.token;assert(Game:GetProperty(key)==nil,'Already attempted; inspect, NEVER resend')
 assert(#snapshot().instances==0,'Preexisting rule instance needs reconciliation')
 for pid=1,5 do assert(type(Players[pid].AttachModifierByID)=='function','Shipped player modifier attachment unavailable')end
 local out={token=a.token,definition=R.definition,turn=a.turn,status='prepared',attempted={},returned={}}
 Game:SetProperty(key,out)
 for pid=1,5 do
  out.status='attach_requested';out.attempted[#out.attempted+1]=pid;Game:SetProperty(key,out)
  Players[pid]:AttachModifierByID(R.definition)
  out.returned[#out.returned+1]=pid;Game:SetProperty(key,out)
 end
 out.status='returned';Game:SetProperty(key,out);return emit(read(a))
end
function R.Confirm(a)
 fresh(a);local key='CSC_NATIVE_RULE_'..a.token;local out=assert(Game:GetProperty(key),'No rule transaction')
 assert(out.status=='returned'and #out.attempted==5 and #out.returned==5,'Unclosed rule attempt')
 local instances=snapshot().instances;assert(#instances==5,'Exactly five live native instances required')
 local seen={};for _,x in ipairs(instances)do assert(x.player>=1 and x.player<=5 and not seen[x.player]and x.active,'Unexpected/inactive rule owner');seen[x.player]=true end
 out.status='confirmed';out.instances=instances;Game:SetProperty(key,out);return emit(read(a))
end
