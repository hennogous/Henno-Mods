-- Explicitly enabled donated-gold diagnostic. Assignment is an assisted engine
-- operation, not a CityManager purchase command; no player-role switching.
CSC_DONATION={}
local D=CSC_DONATION
local function json(v)
 local t=type(v);if t=='nil'then return 'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 local a={};local n=0;local arr=true;for k in pairs(v)do n=n+1;if type(k)~='number'then arr=false end end
 if n~=#v then arr=false end
 if arr then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(a,',')..'}'
end
local function persist(key,x)Game:SetProperty(key,x)end
local function ui_clock(q,r)return q.turn==r.turn or q.turn==r.turn-1 end
function D.Begin(r)
 assert(r.enabled==true,'Diagnostic not enabled');assert(type(r.token)=='string'and #r.token>0)
 local key='CSC_DONATION_'..r.token;assert(Game:GetProperty(key)==nil,'Already attempted; reconcile, never resend')
 assert(Game.GetCurrentGameTurn()==r.turn and not AutoplayManager.IsActive(),'Inactive source boundary required')
 local player=assert(Players[r.player]);assert(player:IsAlive()and player:IsMajor()and not player:IsHuman())
 local city=assert(CityManager.GetCity(r.player,r.city));assert(city:GetOwner()==r.player)
 local tr=player:GetTreasury();assert(tr:GetGoldBalance()==r.original_gold,'Original treasury changed')
 local bridge=assert(ExposedMembers.CSC_DONATION_UI,'UI bridge absent')
 local source=assert(Map.GetPlotByIndex(r.source));assert(source:GetOwner()==r.player or source:GetOwner()==-1)
 assert(source:GetDistrictType()<0 and source:GetResourceType()<0 and source:GetImprovementType()<0 and source:GetFeatureType()<0,'Source changed')
 local wanted={};local ordered={};local total=0;local unknown=0
 for _,index in ipairs(r.route)do
  assert(not ordered[index],'Duplicate acquisition tile');ordered[index]=true
  local q=bridge.Quote(r,index);assert(ui_clock(q,r)and q.gold==r.original_gold and q.owner==-1 and q.city_owner==r.player)
  assert(q.revealed and q.within_range,'Missing native reveal/range')
  assert(q.source_potential and q.can_produce and not q.same_quarter,'Foundation native prerequisite changed')
  if type(q.price)=='number'and q.price>0 then assert(q.price==math.floor(q.price));total=total+q.price else unknown=unknown+1 end
 end
 assert(total==r.initial_total and (unknown==0)==r.initial_quote_complete,'Initial native quote coverage changed')
 assert(#r.route>0 and bridge.Quote(r,r.route[1]).price>0,'First native quote required')
 if source:GetOwner()==-1 then assert(ordered[r.source],'Missing source acquisition')end
 local base,spec={},{}
 for tag in GameInfo.TypeTags()do local def=GameInfo.Resources[tag.Type];if def then
  if tag.Tag=='CLASS_CSC_'..r.quarter..'_BASE'then base[def.Index]=true end
  if tag.Tag=='CLASS_CSC_'..r.quarter..'_SPEC'then spec[def.Index]=true end
 end end
 local foundBase,foundSpec=false,false
 for _,index in ipairs(r.materials)do wanted[index]=true end
 for _,p in ipairs(Map.GetAdjacentPlots(source:GetX(),source:GetY()))do if wanted[p:GetIndex()]then
  local res=GameInfo.Resources[p:GetResourceType()];assert(res,'Material disappeared')
  assert(PlayersVisibility[r.player]:IsRevealed(p:GetX(),p:GetY()),'Hidden material')
  if res.PrereqTech then assert(player:GetTechs():HasTech(GameInfo.Technologies[res.PrereqTech].Index))end
  if res.PrereqCivic then assert(player:GetCulture():HasCivic(GameInfo.Civics[res.PrereqCivic].Index))end
  assert(p:GetOwner()==r.player or(p:GetOwner()==-1 and ordered[p:GetIndex()]),'Unsecured material')
  foundBase=foundBase or base[p:GetResourceType()]or false;foundSpec=foundSpec or spec[p:GetResourceType()]or false
 end end
 assert(foundBase and foundSpec,'Both material plan required')
 local out={status='begun',token=r.token,turn=r.turn,player=r.player,city=r.city,source=r.source,
  original_gold=r.original_gold,initial_quote=total,initial_quote_complete=unknown==0,initial_unknown_tiles=unknown,donated=0,spent=0,steps={},native_purchase_command=false,backend='donated_gold_assisted_assignment'}
 persist(key,out)
 -- Donate all currently known cost even when naturally affordable. A later
 -- disconnected tile is quoted only after earlier ownership opens native reach;
 -- add its exact shortfall before buying, never fabricate a complete estimate.
 tr:ChangeGoldBalance(total);out.donated=total;persist(key,out)
 assert(tr:GetGoldBalance()==r.original_gold+total,'Donation amount mismatch')
 out.status='funded';out.pool=total;out.cursor=1;out.request=r;persist(key,out)
 print('CSC_DONATION_RECEIPT='..json(out));return out
end
function D.Advance(arg)
 local key='CSC_DONATION_'..arg.token;local out=assert(Game:GetProperty(key),'Unknown token');local r=out.request
 assert(r and r.enabled==true and out.status~='confirmed','Wrong or closed stage')
 assert(Game.GetCurrentGameTurn()==r.turn and not AutoplayManager.IsActive(),'Inactive original clock required')
 local player=assert(Players[r.player]);assert(not player:IsHuman()and player:IsAlive()and player:IsMajor())
 local tr=player:GetTreasury();local bridge=assert(ExposedMembers.CSC_DONATION_UI)
 local function emit(value)print('CSC_DONATION_RECEIPT='..json(value));return value end
 local function wait(status)return emit({status=status,token=out.token,turn=r.turn,native_gold=tr:GetGoldBalance(),cursor=out.cursor})end
 if out.status=='assignment_requested'then
  local pending=assert(out.pending);local p=assert(Map.GetPlotByIndex(pending.plot));local owner=bridge.Owner(r,pending.plot)
  assert(p:GetOwner()==-1 or p:GetOwner()==r.player,'Unexpected acquired owner')
  if p:GetOwner()~=r.player or owner.owner~=r.player or owner.plot_city==-1 then return wait('awaiting_ownership')end
  assert(owner.plot_city==r.city and owner.city_owner==r.player,'Wrong city assignment')
  assert(tr:GetGoldBalance()==pending.gold_before,'Gold changed before exact debit')
  tr:ChangeGoldBalance(-pending.price);assert(tr:GetGoldBalance()==pending.gold_before-pending.price,'Exact debit failed')
  out.pool=out.pool-pending.price;assert(out.pool>=0);out.spent=out.spent+pending.price
  out.steps[#out.steps+1]={plot=pending.plot,price=pending.price,before=pending.gold_before,after=tr:GetGoldBalance(),owner=p:GetOwner(),city=owner.plot_city,ui_turn=pending.ui_turn,core_turn=r.turn,assignment_returned=out.assignment_returned}
  out.pending=nil;out.cursor=out.cursor+1;out.status='funded';persist(key,out);return emit(out)
 end
 assert(out.status=='funded','Ambiguous transition; inspect without repeating')
 assert(tr:GetGoldBalance()==r.original_gold+out.pool,'Original wallet/pool changed')
 if out.cursor>#r.route then
  if out.pool>0 then
   local unused=out.pool;out.status='unused_grant_removal_requested';persist(key,out)
   tr:ChangeGoldBalance(-unused);out.donated=out.donated-unused;out.unused_grant_removed=unused;out.pool=0
  end
  assert(tr:GetGoldBalance()==r.original_gold,'Original wallet changed')
  out.final_gold=tr:GetGoldBalance();out.status='confirmed';persist(key,out);return emit(out)
 end
 local index=r.route[out.cursor];local q=bridge.Quote(r,index)
 assert(q.owner==-1 and ui_clock(q,r)and q.within_range and q.revealed,'Selected next plot changed')
 -- UI treasury/plot facts lag Gameplay writes until the next rendered frame.
 -- An awaiting response performs no mutation; the caller yields between ACKs.
 if q.gold~=tr:GetGoldBalance()then return wait('awaiting_UI')end
 assert(type(q.price)=='number'and q.price>0,'Next quote still unavailable after previous connector')
 if q.price>out.pool then
  local extra=q.price-out.pool;out.status='topup_requested';persist(key,out)
  tr:ChangeGoldBalance(extra);out.pool=out.pool+extra;out.donated=out.donated+extra
  assert(tr:GetGoldBalance()==r.original_gold+out.pool);out.status='funded';persist(key,out);return emit(out)
 end
 assert(q.native_reach,'Next tile absent from native purchase reach')
 out.pending={plot=index,price=q.price,gold_before=tr:GetGoldBalance(),ui_turn=q.turn}
 out.status='assignment_requested';persist(key,out)
 local ok,err=pcall(function()local p=assert(Map.GetPlotByIndex(index));assert(p:GetOwner()==-1);WorldBuilder.CityManager():SetPlotOwner(p:GetX(),p:GetY(),r.player,r.city)end);out.assignment_returned=ok;out.assignment_error=not ok and tostring(err)or nil
 persist(key,out);return emit(out)
end
print('CSC_DONATION_STAGED_TRANSACTION_READY')
