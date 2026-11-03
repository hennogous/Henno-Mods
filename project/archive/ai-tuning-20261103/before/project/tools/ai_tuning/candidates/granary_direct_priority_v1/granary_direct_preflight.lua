-- Read-only scope/row preflight; no callback, flag, native preference or order.
-- Leader/Civilization name getters are reused from existing CSC readers/core.
local function json(v)
 local t=type(v);if t=='nil'then return 'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 if t~='table'then return 'null'end
 local a,n,array={},0,true;for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end
 if array then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(a,',')..'}'
end
local function scalar(row)
 local out={};for k,v in pairs(row)do if type(v)=='string'or type(v)=='number'or type(v)=='boolean'then out[k]=v end end;return out
end
local LIST='CSC_AI_GranaryDirectPriority_V1'
local TRAIT='TRAIT_LEADER_GENGHIS_KHAN_ABILITY'
-- The sole driver injects its verified Gameplay INITIAL_HUMANS as a Lua literal;
-- no UI Game-property getter or current autoplay human flag is assumed here.
local roles=__ORIGINAL_HUMANS__
local out={version=1,turn=Game.GetCurrentGameTurn(),list_type=LIST,binding_trait=TRAIT,profile='OFF',
 original_humans=roles,role_source='verified Gameplay CSC_AI_ASSISTANCE_V1_INITIAL_HUMANS supplied by driver',
 roster={},eligible_player_ids={},errors={},scope_verified=false,
 rows={list_types={},lists={},favored={},leader_trait_bindings={},civilization_trait_bindings={}},
 native_preference='UNOBSERVED_BY_THIS_READER',conditional=false,player_local=false}
local function fail(text)out.errors[#out.errors+1]=text end
for row in GameInfo.CSC_AI_Profile()do if row.Id=='ACTIVE'then out.profile=row.Mode end end
for row in GameInfo.AiListTypes()do if row.ListType==LIST then out.rows.list_types[#out.rows.list_types+1]=scalar(row)end end
for row in GameInfo.AiLists()do if row.ListType==LIST then out.rows.lists[#out.rows.lists+1]=scalar(row)end end
for row in GameInfo.AiFavoredItems()do if row.ListType==LIST then out.rows.favored[#out.rows.favored+1]=scalar(row)end end
for row in GameInfo.LeaderTraits()do if row.TraitType==TRAIT then out.rows.leader_trait_bindings[#out.rows.leader_trait_bindings+1]=scalar(row)end end
for row in GameInfo.CivilizationTraits()do if row.TraitType==TRAIT then out.rows.civilization_trait_bindings[#out.rows.civilization_trait_bindings+1]=scalar(row)end end
local roleKnown=type(roles)=='table'and(roles['0']==true or roles[0]==true)
if not roleKnown then fail('original_human_mask_unknown')end
if out.profile~='RH'then fail('profile_not_RH')end
local binding=out.rows.leader_trait_bindings
if #binding~=1 or binding[1].LeaderType~='LEADER_GENGHIS_KHAN'then fail('unexpected_leader_trait_bindings')end
if #out.rows.civilization_trait_bindings~=0 then fail('unexpected_civilization_trait_binding')end
local lists=out.rows.lists;local favored=out.rows.favored
if #out.rows.list_types~=1 or #lists~=1 or lists[1].LeaderType~=TRAIT or lists[1].System~='Buildings'
 or lists[1].AgendaType~=nil or lists[1].MinDifficulty~=nil or lists[1].MaxDifficulty~=nil then fail('direct_list_rows_mismatch')end
if #favored~=1 or favored[1].Item~='BUILDING_GRANARY'or not(favored[1].Favored==true or favored[1].Favored==1)
 or favored[1].Value~=0 or favored[1].StringVal~=nil or favored[1].MinDifficulty~=nil or favored[1].MaxDifficulty~=nil then fail('favored_rows_mismatch')end
for pid=0,5 do
 local row={player=pid,original_role_known=roleKnown,original_human=roleKnown and(roles[tostring(pid)]==true or roles[pid]==true)or false,
  leader_chain={},leader_traits={},civilization_traits={},binding_sources={},candidate_membership=false}
 out.roster[#out.roster+1]=row
 local ok,error=pcall(function()
  local player=assert(Players[pid],'missing player');row.alive=player:IsAlive();row.major=player:IsMajor()
  local config=assert(PlayerConfigurations[pid],'missing configuration')
  row.leader=config:GetLeaderTypeName();row.civilization=config:GetCivilizationTypeName()
  assert(type(row.leader)=='string'and row.leader~=''and type(row.civilization)=='string'and row.civilization~='','unknown leader/civilization')
  local seen={};local leader=row.leader
  for i=1,16 do
   if leader==nil or leader==''then break end
   assert(not seen[leader],'leader inheritance cycle');seen[leader]=true;row.leader_chain[#row.leader_chain+1]=leader
   local definition=assert(GameInfo.Leaders[leader],'missing leader definition');leader=definition.InheritFrom
   if i==16 and leader~=nil and leader~=''then error('leader inheritance limit')end
  end
  for item in GameInfo.LeaderTraits()do if seen[item.LeaderType]then
   row.leader_traits[#row.leader_traits+1]=scalar(item)
   if item.TraitType==TRAIT then row.binding_sources[#row.binding_sources+1]={kind='leader',leader=item.LeaderType,trait=TRAIT}end
  end end
  for item in GameInfo.CivilizationTraits()do if item.CivilizationType==row.civilization then
   row.civilization_traits[#row.civilization_traits+1]=scalar(item)
   if item.TraitType==TRAIT then row.binding_sources[#row.binding_sources+1]={kind='civilization',civilization=item.CivilizationType,trait=TRAIT}end
  end end
  row.candidate_membership=#row.binding_sources>0
  if row.candidate_membership then out.eligible_player_ids[#out.eligible_player_ids+1]=pid end
  assert(row.alive and row.major,'roster player is not an alive major')
 end)
 if not ok then row.error=tostring(error);fail('roster_'..pid..':'..tostring(error))end
end
local selected=out.roster[4]
if not selected or selected.leader~='LEADER_GENGHIS_KHAN'or selected.civilization~='CIVILIZATION_MONGOLIA'
 or not selected.original_role_known or selected.original_human then fail('selected_original_AI_identity_mismatch')end
if #out.eligible_player_ids~=1 or out.eligible_player_ids[1]~=3 then fail('trait_scope_not_only_player3')end
out.scope_verified=#out.errors==0
print('CSC_GRANARY_DIRECT_PREFLIGHT='..json(out))
