-- Read-only end-of-round metrics, distinct from cached first-activation censuses.
-- Native Service properties are recipient observations; sales adjacency is a
-- structural link, never a claimed monetary transaction.
local function json(v)
 local t=type(v);if t=='nil'then return 'null'end
 if t=='number'or t=='boolean'then return tostring(v)end
 if t=='string'then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"'end
 local a={};local array=true;local n=0;for k in pairs(v)do n=n+1;if type(k)~='number'then array=false end end
 if n~=#v then array=false end
 if array then for _,x in ipairs(v)do a[#a+1]=json(x)end;return '['..table.concat(a,',')..']'end
 for k,x in pairs(v)do a[#a+1]=json(tostring(k))..':'..json(x)end;return '{'..table.concat(a,',')..'}'
end
local s=CSCBASE.capture()
local out={turn=s.turn,phase='current-safe-boundary',cities={},players={},errors=s.errors,
 service_evidence='native recipient property values; no transaction observation'}
for _,p in ipairs(s.players)do if p.id>=1 and p.id<=5 then
 p.gold=Players[p.id]:GetTreasury():GetGoldBalance();out.players[#out.players+1]=p
end end
for _,c in ipairs(s.cities)do if c.player>=1 and c.player<=5 then
 local rows={};for _,d in ipairs(c.districts)do if d.quarter then rows[#rows+1]=d end end
 out.cities[#out.cities+1]={player=c.player,city=c.id,population=c.population,
  buildings=c.buildings,properties=c.properties,yields=c.yields,quarters=rows}
end end
print('CSC_CHAIN_METRICS='..json(out))
