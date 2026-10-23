-- One explicitly enabled assisted acquisition. This uses Gameplay city assignment
-- plus a verified gold debit, not the unproven native AI PURCHASE command.
-- Persist before every effect; an ambiguous grant/assignment/debit never repeats.
CSC_FUNDED_ACQUISITION={}
local F=CSC_FUNDED_ACQUISITION
local function json(v)
 local t=type(v);if t=='nil'then return 'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 local a={};local n=0;local arr=true;for k in pairs(v)do n=n+1;if type(k)~='number'then arr=false end end
 if n~=#v then arr=false end
 if arr then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(a,',')..'}'
end
local function emit(x)print('CSC_FUNDED_RECEIPT='..json(x));return x end
local function save(key,x)Game:SetProperty(key,x)end
local function fresh(r,ownership_pending)
 assert(Game.GetCurrentGameTurn()==r.turn and not AutoplayManager.IsActive(),'Inactive exact clock required')
 local p=assert(Players[r.player]);assert(p:IsAlive()and p:IsMajor()and not p:IsHuman())
 local c=assert(CityManager.GetCity(r.player,r.city));assert(c:GetOwner()==r.player)
 if ownership_pending then return p:GetTreasury()end
 local q=ExposedMembers.CSC_DONATION_UI.Quote(r,r.plot)
 assert((q.turn==r.turn or q.turn==r.turn-1)and q.revealed and q.within_range,'Reveal/range/clock changed')
 assert(q.source_potential and q.can_produce and not q.same_quarter,'Source prerequisite changed')
 assert(q.price==r.price and r.price>0 and r.price==math.floor(r.price),'Actual step quote changed')
 return p:GetTreasury(),q
end
function F.Begin(r)
 assert(r.enabled==true and type(r.token)=='string')
 local key='CSC_FUNDED_'..r.token;assert(Game:GetProperty(key)==nil,'Already attempted; reconcile, never resend')
 local tr,q=fresh(r)
 assert(tr:GetGoldBalance()==r.gold and q.gold==r.gold and q.owner==-1 and q.native_reach,'Fresh wallet/reach required')
 assert(r.cashflow_observed and r.reserve>=25 and r.reserve>=math.ceil(10*math.max(0,-r.net_income)))
 assert(r.reserve>=math.ceil(2*r.maintenance),'Upkeep reserve missing')
 assert(r.price<=r.remaining_cap and r.remaining_cap<=300,'Spending cap')
 local allowance=math.max(0,math.floor(.8*math.max(0,r.gold-r.reserve)))
 local own=math.min(r.price,allowance)
 assert(r.own_gold==own and r.grant==r.price-own,'Funding split changed')
 local route={};for _,index in ipairs(r.route)do
  assert(not route[index]);route[index]=true
  local t=ExposedMembers.CSC_DONATION_UI.Quote(r,index)
  assert(t.revealed and t.within_range and t.owner==-1,'Route changed')
 end
 assert(route[r.plot]and #r.route<=5 and #r.connectors<=2,'Undeclared or excessive step')
 local s=assert(Map.GetPlotByIndex(r.source));assert(s:GetOwner()==r.player or route[r.source])
 assert(s:GetDistrictType()<0 and s:GetResourceType()<0 and s:GetFeatureType()<0 and s:GetImprovementType()<0,'Source occupied')
 local wanted={};for _,index in ipairs(r.materials)do wanted[index]=true end
 local base,spec={},{}
 for tag in GameInfo.TypeTags()do local def=GameInfo.Resources[tag.Type];if def then
  if tag.Tag=='CLASS_CSC_'..r.quarter..'_BASE'then base[def.Index]=true end
  if tag.Tag=='CLASS_CSC_'..r.quarter..'_SPEC'then spec[def.Index]=true end
 end end
 local hasBase,hasSpec=false,false
 for _,tile in ipairs(Map.GetAdjacentPlots(s:GetX(),s:GetY()))do if wanted[tile:GetIndex()]then
  assert(tile:GetOwner()==r.player or route[tile:GetIndex()],'Unsecured material')
  assert(PlayersVisibility[r.player]:IsRevealed(tile:GetX(),tile:GetY()))
  local res=assert(GameInfo.Resources[tile:GetResourceType()])
  local p=Players[r.player]
  if res.PrereqTech then assert(p:GetTechs():HasTech(GameInfo.Technologies[res.PrereqTech].Index))end
  if res.PrereqCivic then assert(p:GetCulture():HasCivic(GameInfo.Civics[res.PrereqCivic].Index))end
  hasBase=hasBase or base[res.Index]or false;hasSpec=hasSpec or spec[res.Index]or false
 end end
 assert(hasBase and hasSpec,'Both plan required')
 local out={status='prepared',token=r.token,request=r,turn=r.turn,player=r.player,city=r.city,source=r.source,
  original_gold=r.gold,donated=0,spent=0,own_gold_spent=0,steps={},native_purchase_command=false,
  backend='quoted_gold_assisted_assignment',funding_policy='own_first_shortfall_fallback'}
 save(key,out);return emit(out)
end
function F.Advance(arg)
 local key='CSC_FUNDED_'..arg.token;local out=assert(Game:GetProperty(key));local r=out.request
 assert(out.status~='confirmed','Closed token')
 local tr,q=fresh(r,out.status=='assignment_requested')
 if out.status=='prepared'then
  assert(tr:GetGoldBalance()==r.gold and q.gold==r.gold and q.owner==-1 and q.native_reach)
  out.status='grant_requested';save(key,out)
  if r.grant>0 then tr:ChangeGoldBalance(r.grant)end
  assert(tr:GetGoldBalance()==r.gold+r.grant,'Exact fallback grant mismatch')
  out.donated=r.grant;out.status='funded';save(key,out);return emit(out)
 end
 if out.status=='funded'then
  assert(tr:GetGoldBalance()==r.gold+r.grant and q.owner==-1)
  if q.gold~=tr:GetGoldBalance()then return emit({status='awaiting_UI',token=r.token})end
  assert(q.native_reach,'Fresh purchase reach lost')
  out.status='assignment_requested';save(key,out)
  local ok,err=pcall(function()local tile=Map.GetPlotByIndex(r.plot);assert(tile:GetOwner()==-1);WorldBuilder.CityManager():SetPlotOwner(tile:GetX(),tile:GetY(),r.player,r.city)end)
  out.assignment_returned=ok;out.assignment_error=not ok and tostring(err)or nil;save(key,out);return emit(out)
 end
 assert(out.status=='assignment_requested','Ambiguous transition; inspect without repeating')
 local tile=Map.GetPlotByIndex(r.plot);local owner=ExposedMembers.CSC_DONATION_UI.Owner(r,r.plot)
 assert(tile:GetOwner()==-1 or tile:GetOwner()==r.player)
 if tile:GetOwner()~=r.player or owner.owner~=r.player or owner.plot_city==-1 then return emit({status='awaiting_ownership',token=r.token})end
 assert(owner.plot_city==r.city and owner.city_owner==r.player,'Wrong city')
 assert(tr:GetGoldBalance()==r.gold+r.grant,'Gold changed before debit')
 out.status='debit_requested';save(key,out)
 tr:ChangeGoldBalance(-r.price)
 assert(tr:GetGoldBalance()==r.gold+r.grant-r.price,'Exact debit mismatch')
 assert(tr:GetGoldBalance()>=math.min(r.gold,r.reserve),'Reserve impaired')
 out.spent=r.price;out.own_gold_spent=r.own_gold;out.final_gold=tr:GetGoldBalance()
 out.steps={{plot=r.plot,price=r.price,donated=r.grant,own_gold=r.own_gold,owner=tile:GetOwner(),city=owner.plot_city}}
 out.status='confirmed';save(key,out);return emit(out)
end
