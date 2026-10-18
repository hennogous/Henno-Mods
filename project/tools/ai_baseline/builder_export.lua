local function json(v)
    local k=type(v);
    if k=='nil' then return 'null' end
    if k=='boolean' or k=='number' then return tostring(v) end
    if k=='string' then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t'):gsub('%z','')..'"' end
    if k~='table' then return 'null' end
    local parts={}; local n=0; local array=true;
    for key in pairs(v) do n=n+1; if type(key)~='number' then array=false end end
    if n~=#v then array=false end
    if array then for _,x in ipairs(v) do parts[#parts+1]=json(x) end; return '['..table.concat(parts,',')..']' end
    for key,x in pairs(v) do parts[#parts+1]=json(tostring(key))..':'..json(x) end
    return '{'..table.concat(parts,',')..'}';
end

function CSC_BUILDERS.Export(turn)
 local B=CSC_BUILDERS
 local row=B.checkpoints[turn]
 if not row then assert(turn==Game.GetCurrentGameTurn(),'Missing frozen Builder census');row=B.Capture();B.checkpoints[turn]=row end
 print('CSC_BUILDERS_SNAPSHOT='..json(row))
end
