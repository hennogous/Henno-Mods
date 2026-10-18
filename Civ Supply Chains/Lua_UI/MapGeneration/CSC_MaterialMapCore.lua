-- Sparse continental material assistance. Pure Lua; no engine writes or RNG.
-- Native and offline tests execute this same planner. Arrays are sorted before
-- random selection; pairs() is used only for unordered membership/count checks.
CSC_MaterialMapCore = {};
local C = CSC_MaterialMapCore;
C.Version = 4;
-- Only implemented Quarters participate in production placement/protection.
-- Bakers already exceed the calibrated coverage aim; retain their geography.
-- Design-only rules remain a research reference, never a reason to add deposits.
C.Quarters = {'BAKERS','TAILORS'};
C.Assisted = {'TAILORS'};
C.Probability = {TAILORS=7/12};
-- Calibration: native Abundant (density 33), fifteen sampled continents.
C.NaturalCoverage = {TAILORS=3/15};
-- Temporary emphasis while Bakers/Tailors are the implemented industries.
-- Targets are relative to this map AFTER the original continental repair.
C.SiteMultipliers = {TAILORS={base_only=2,both=4}};
C.SiteMinimums = {TAILORS={both=4}}; -- scaled from the Abundant reference density
function C.ResourceProfile(setting,standard)
    standard=standard or 30;
    local offsets={[1]=-3,[2]=0,[3]=3,[4]=0};
    if standard==29 then offsets[25]=25;offsets[45]=45;end
    if offsets[setting]==nil then return nil;end
    local density=standard+offsets[setting];local scale=density/33;
    local profile={setting=setting,standard_density=standard,nominal_density=density,scale=scale,
        random_uses_expected_density=setting==4,active_quarters=C.Quarters,assisted_quarters=C.Assisted,targets={},probabilities={},
        max_per_continent=math.max(2,math.floor(4*scale+.5)),max_per_map=math.max(2,math.floor(10*scale+.5))};
    for _,q in ipairs(C.Quarters) do profile.targets[q]=math.min(1,2/3*scale);end
    for _,q in ipairs(C.Assisted) do
        local natural=C.NaturalCoverage[q];
        local target=math.min(1,(natural+(1-natural)*C.Probability[q])*scale);
        local expectedNatural=math.min(1,natural*scale);
        -- Scale the desired coverage, then calculate the chance of assisting a
        -- missing continent. Multiplying the old chance alone misses the target.
        profile.probabilities[q]=expectedNatural>=1 and 1 or math.max(0,math.min(1,(target-expectedNatural)/(1-expectedNatural)));
    end
    return profile;
end
local MODULUS = 2147483647;
function C.Seed(text)
    local value = 20261016;
    for i=1,#text do value=(value*131+string.byte(text,i))%MODULUS; end
    return math.max(1,value);
end
local function random(seed)
    local state=seed;
    -- Diffuse similar continent/configuration keys before the first draw.
    for _=1,4 do state=(state*48271)%MODULUS;end
    return function() state=(state*48271)%MODULUS;return (state-1)/(MODULUS-1);end;
end
local function count(t) local n=0;for _ in pairs(t) do n=n+1;end;return n;end
local function copy(t) local out={};for k,v in pairs(t) do out[k]=v;end;return out;end
local function sorted(t) local out={};for k in pairs(t) do out[#out+1]=k;end;table.sort(out);return out;end
local function key(cid,q) return tostring(cid)..':'..q;end
local function shuffle(t,rng)
    for i=#t,2,-1 do local j=1+math.floor(rng()*i);t[i],t[j]=t[j],t[i];end
end
local function weighted(values,weights,rng)
    local total=0;for _,w in ipairs(weights) do total=total+w;end
    local point=rng()*total;
    for i,w in ipairs(weights) do point=point-w;if point<0 then return values[i];end;end
    return values[#values];
end
function C.Json(v)
    local kind=type(v);
    if kind=='nil' then return 'null';end
    if kind=='number' or kind=='boolean' then return tostring(v);end
    if kind=='string' then return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t')..'"';end
    assert(kind=='table','Nonserializable material map value');
    local n=count(v);local array=n>0 and n==#v;
    for k in pairs(v) do if type(k)~='number' then array=false;break;end;end
    local out={};
    if array then for _,x in ipairs(v) do out[#out+1]=C.Json(x);end;return '['..table.concat(out,',')..']';end
    for _,k in ipairs(sorted(v)) do out[#out+1]=C.Json(tostring(k))..':'..C.Json(v[k]);end
    return '{'..table.concat(out,',')..'}';
end

function C.Plan(data,definitions,eligible,mapSeed,profile)
    profile=profile or C.ResourceProfile(3,30);
    local plots,regions,localTypes,classes,features={},{},{},{},{};
    for _,r in ipairs(data.resources) do classes[r.type]=r.class;end
    for _,f in ipairs(data.features) do features[f.type]=f;end
    for _,p in ipairs(data.plots) do
        plots[p.index]=copy(p);
        if not p.water and p.continent>=0 then
            regions[p.continent]=regions[p.continent] or {};localTypes[p.continent]=localTypes[p.continent] or {};
            regions[p.continent][#regions[p.continent]+1]=p.index;
            if p.resource then localTypes[p.continent][p.resource]=true;end
        end
    end
    local continents=sorted(regions);
    for _,indices in pairs(regions) do table.sort(indices);end
    local rng=random(C.Seed(tostring(mapSeed)..':placement:v1'));
    local result={version=C.Version,seed=mapSeed,rng='Park-Miller 48271; CSC-owned stream',additions={},attempts={},palettes={},coverage={},abundance=profile,max_per_continent=profile.max_per_continent,max_per_map=profile.max_per_map};
    local palette,allocated,budget,reserved={},{},{},{};
    local function matches(p,rule)
        if rule.hills and p.hills then return true;end
        for _,r in ipairs(rule.resources or {}) do if p.resource==r then return true;end;end
        for _,f in ipairs(rule.features or {}) do if p.feature==f then return true;end;end
        return false;
    end
    local function clearable(p)
        if p.water or p.impassable or p.district then return false;end
        local f=features[p.feature];
        if f and not (f.removable==true or f.removable==1) and not (p.feature=='FEATURE_FLOODPLAINS' or p.feature=='FEATURE_FLOODPLAINS_PLAINS' or p.feature=='FEATURE_FLOODPLAINS_GRASSLAND') then return false;end
        return not p.resource or classes[p.resource]=='RESOURCECLASS_BONUS';
    end
    local function supported(p,q,mode)
        if not clearable(p) then return false;end
        local b,s=false,false;
        for _,i in ipairs(p.neighbors) do
            b=b or matches(plots[i],definitions[q].base);s=s or matches(plots[i],definitions[q].spec);
        end
        return b and (mode=='base' or s);
    end
    local function sites(mode)
        local out={};
        for _,cid in ipairs(continents) do for _,q in ipairs(C.Quarters) do
            local set={};out[key(cid,q)]=set;
            for _,i in ipairs(regions[cid]) do if supported(plots[i],q,mode) then set[i]=true;end;end
        end;end
        return out;
    end
    local both,base=sites('both'),sites('base');local beforeBoth,beforeBase=both,base;
    local function localSites(deposits,old,mode)
        local affected={};for _,d in ipairs(deposits) do affected[d.plot]=true;for _,i in ipairs(plots[d.plot].neighbors) do affected[i]=true;end;end
        local out={};for k,set in pairs(old) do out[k]=copy(set);for i in pairs(affected) do out[k][i]=nil;end;end
        for i in pairs(affected) do local p=plots[i];if regions[p.continent] then
            for _,q in ipairs(C.Quarters) do if supported(p,q,mode) then out[key(p.continent,q)][i]=true;end;end
        end;end
        return out;
    end
    local function retains(old,new)
        for k,set in pairs(old) do if next(set) and not next(new[k]) then return false;end;end
        return true;
    end
    local continentOrder={};for _,cid in ipairs(continents) do continentOrder[#continentOrder+1]=cid;end;shuffle(continentOrder,rng);
    for _,q in ipairs(C.Assisted) do for _,kind in ipairs({'base','spec'}) do for _,cid in ipairs(continentOrder) do
        local candidates,weights={},{};
        for _,r in ipairs(definitions[q][kind].resources or {}) do
            local possible=false;for _,i in ipairs(regions[cid]) do if eligible[r] and eligible[r][i] then possible=true;break;end;end
            if possible then candidates[#candidates+1]=r;weights[#weights+1]=(localTypes[cid][r] and 4 or 2)/(1+3*(allocated[r] or 0));end
        end
        if #candidates>0 then
            local r=weighted(candidates,weights,rng);palette[key(cid,q)..':'..kind]=r;allocated[r]=(allocated[r] or 0)+1;
            result.palettes[#result.palettes+1]={continent=cid,quarter=q,kind=kind,resource=r};
        end
    end;end;end
    local function options(cid,q,cost)
        local protected=copy(reserved);
        for _,set in pairs(both) do if count(set)==1 then protected[next(set)]=true;end;end
        local seen,out={},{};
        for _,center in ipairs(regions[cid]) do local p=plots[center];if clearable(p) then
            local needs={};
            for _,kind in ipairs({'base','spec'}) do
                local has=false;for _,i in ipairs(p.neighbors) do if matches(plots[i],definitions[q][kind]) then has=true;break;end;end
                if not has then needs[#needs+1]=kind;end
            end
            if #needs==cost then
                local choices={};for _,kind in ipairs(needs) do
                    local values={};choices[kind]=values;
                    for _,r in ipairs(definitions[q][kind].resources or {}) do for _,i in ipairs(p.neighbors) do
                        if eligible[r] and eligible[r][i] and plots[i].continent==cid and not plots[i].resource and not protected[i] then values[#values+1]={plot=i,resource=r};end
                    end;end
                end
                local function add(deposits)
                    table.sort(deposits,function(a,b)if a.plot~=b.plot then return a.plot<b.plot;end;return a.resource<b.resource;end);
                    local parts={};for _,d in ipairs(deposits) do parts[#parts+1]=d.plot..':'..d.resource;end;local id=table.concat(parts,'|');
                    if not seen[id] then seen[id]=true;out[#out+1]={deposits=deposits,center=center,needs=needs};end
                end
                if cost==1 then for _,a in ipairs(choices[needs[1]]) do add({a});end
                else for _,a in ipairs(choices.base) do for _,b in ipairs(choices.spec) do if a.plot~=b.plot then add({a,b});end;end;end;end
            end
        end;end
        return out;
    end
    local function choose(cid,q,cost)
        if (budget[cid] or 0)+cost>result.max_per_continent or #result.additions+cost>result.max_per_map then return nil;end
        local groups,types={},{ };
        for _,option in ipairs(options(cid,q,cost)) do
            for _,d in ipairs(option.deposits) do plots[d.plot].resource=d.resource;end
            local safe=retains(both,localSites(option.deposits,both,'both')) and retains(base,localSites(option.deposits,base,'base'));
            for _,d in ipairs(option.deposits) do plots[d.plot].resource=nil;end
            if safe then
                local names={};for _,d in ipairs(option.deposits) do names[#names+1]=d.resource;end;table.sort(names);local id=table.concat(names,'|');
                if not groups[id] then groups[id]={};types[id]=names;end;groups[id][#groups[id]+1]=option;
            end
        end
        local keys=sorted(groups);if #keys==0 then return nil;end
        local weights={};for _,id in ipairs(keys) do
            local weight=1;
            for _,r in ipairs(types[id]) do
                local preferred=palette[key(cid,q)..':base']==r or palette[key(cid,q)..':spec']==r;
                local elsewhere=0;for _,a in ipairs(result.additions) do if a.resource==r and a.continent~=cid then elsewhere=elsewhere+1;end;end
                weight=weight*(preferred and 12 or localTypes[cid][r] and 4 or 1)/(1+3*elsewhere);
            end
            weights[#weights+1]=weight;
        end
        local values=groups[weighted(keys,weights,rng)];return values[1+math.floor(rng()*#values)];
    end
    local order={};for _,cid in ipairs(continents) do for _,q in ipairs(C.Assisted) do order[#order+1]={continent=cid,quarter=q};end;end;shuffle(order,rng);
    for _,a in ipairs(order) do
        local cid,q=a.continent,a.quarter;
        a.probability=profile.probabilities[q];a.roll=random(C.Seed(tostring(mapSeed)..':'..cid..':'..q..':assist:v1'))();
        if next(both[key(cid,q)]) then a.outcome='already covered';
        elseif a.roll>=a.probability then a.outcome='not selected';
        else
            local option=choose(cid,q,1) or choose(cid,q,2);
            if not option then a.outcome='no safe feasible repair within budget';
            else
                for _,d in ipairs(option.deposits) do plots[d.plot].resource=d.resource;end
                local after=localSites(option.deposits,both,'both');base=localSites(option.deposits,base,'base');
                assert(next(after[key(cid,q)]),'Repair failed to create its promised Quarter site');
                local gains={};for _,region in ipairs(continents) do for _,industry in ipairs(C.Quarters) do local k=key(region,industry);if not next(both[k]) and next(after[k]) then gains[#gains+1]={continent=region,quarter=industry,sites=count(after[k])};end;end;end
                for _,d in ipairs(option.deposits) do
                    local p=plots[d.plot];local kinds={};for _,kind in ipairs({'base','spec'}) do for _,r in ipairs(definitions[q][kind].resources or {}) do if r==d.resource then kinds[#kinds+1]=kind;break;end;end;end
                    result.additions[#result.additions+1]={number=#result.additions+1,plot=d.plot,x=p.x,y=p.y,resource=d.resource,quantity=1,continent=cid,quarter=q,material_class=table.concat(kinds,' + '),center=option.center,repair_size=#option.deposits,coverage_gains=gains};
                    budget[cid]=(budget[cid] or 0)+1;
                end
                reserved[option.center]=true;both=after;a.outcome='added';
            end
        end
        result.attempts[#result.attempts+1]=a;
    end
    -- A separate owned RNG keeps the established continental repair unchanged.
    -- A small abundance-scaled floor handles maps with no both-class sites.
    -- There are no equal continent quotas. The original repair runs first.
    if C.SiteMultipliers and C.SiteMultipliers.TAILORS then
        local q='TAILORS';local multipliers=C.SiteMultipliers[q];
        local function totals()
            local b,s=0,0;for _,cid in ipairs(continents) do b=b+count(base[key(cid,q)]);s=s+count(both[key(cid,q)]);end
            return {base_only=b-s,both=s};
        end
        local reference=totals();local minimum=math.max(1,math.floor(C.SiteMinimums[q].both*profile.scale+.5));
        local targets={base_only=math.ceil(reference.base_only*multipliers.base_only),both=math.max(minimum,math.ceil(reference.both*multipliers.both))};
        local passable=0;local limits,spent={},{};
        for _,cid in ipairs(continents) do
            local land=0;for _,i in ipairs(regions[cid]) do if not plots[i].impassable then land=land+1;end;end
            passable=passable+land;limits[cid]=math.max(2,math.ceil(land*.08*profile.scale));
        end
        local cap=math.max(8,math.ceil(passable*.05*profile.scale));
        local density={reference=reference,targets=targets,multipliers=copy(multipliers),minimum_both=minimum,max_per_map=cap,max_per_continent=limits,additions=0};
        result.site_density=density;
        local densityRng=random(C.Seed(tostring(mapSeed)..':tailors-density:v1'));
        local starts={};for _,i in ipairs(data.starting_plots or {}) do starts[i]=true;end
        local resources={};for _,kind in ipairs({'base','spec'}) do for _,r in ipairs(definitions[q][kind].resources or {}) do resources[r]=true;end;end
        local resourceOrder=sorted(resources);
        local function delta(i,r)
            plots[i].resource=r;
            local affected={[i]=true};for _,n in ipairs(plots[i].neighbors) do affected[n]=true;end
            local changes={base={},both={}};
            for n in pairs(affected) do local p=plots[n];if regions[p.continent] then
                for _,industry in ipairs(C.Quarters) do local k=key(p.continent,industry);
                    for _,mode in ipairs({'base','both'}) do local set=mode=='base' and base[k] or both[k];
                        local was=set[n] and 1 or 0;local now=supported(p,industry,mode) and 1 or 0;
                        changes[mode][k]=(changes[mode][k] or 0)+now-was;
                    end
                end
            end;end
            plots[i].resource=nil;
            local gainBase,gainBoth=0,0;
            for _,cid in ipairs(continents) do for _,industry in ipairs(C.Quarters) do local k=key(cid,industry);
                local db=changes.base[k] or 0;local ds=changes.both[k] or 0;
                -- Do not trade away Baker opportunities for the temporary boost.
                if industry=='BAKERS' and (db<0 or ds<0) then return nil;end
                if count(base[k])>0 and count(base[k])+db<=0 then return nil;end
                if count(both[k])>0 and count(both[k])+ds<=0 then return nil;end
                if industry==q then gainBase=gainBase+db;gainBoth=gainBoth+ds;end
            end;end
            if gainBoth<0 then return nil;end
            return {base_only=gainBase-gainBoth,both=gainBoth};
        end
        -- Specialty connections first: converting a Base-only site into a both
        -- site must not silently consume the separate Base-only increase.
        for _,goal in ipairs({'both','base_only'}) do
            local current=totals();
            while current[goal]<targets[goal] and density.additions<cap do
                local best,choices,weights=0,{},{};
                for _,r in ipairs(resourceOrder) do
                    local isBase=false;for _,v in ipairs(definitions[q].base.resources or {}) do if v==r then isBase=true;break;end;end
                    if goal=='both' or isBase then
                        for _,i in ipairs(sorted(eligible[r] or {})) do local p=plots[i];local cid=p and p.continent;
                            if p and regions[cid] and not p.resource and not p.district and not p.water and not p.impassable and not starts[i] and not reserved[i] and (spent[cid] or 0)<limits[cid] then
                                local gains=delta(i,r);
                                if gains and gains[goal]>0 then
                                    local score=math.min(gains[goal],targets[goal]-current[goal]);
                                    if score>best then best=score;choices={};weights={};end
                                    if score==best then
                                        local kind=isBase and 'base' or 'spec';local preferred=palette[key(cid,q)..':'..kind]==r;
                                        local elsewhere=0;for _,a in ipairs(result.additions) do if a.resource==r and a.continent~=cid then elsewhere=elsewhere+1;end;end
                                        choices[#choices+1]={plot=i,resource=r,continent=cid,kind=kind,gains=gains};
                                        weights[#weights+1]=(preferred and 12 or localTypes[cid][r] and 4 or 1)/(1+3*elsewhere);
                                    end
                                end
                            end
                        end
                    end
                end
                if #choices==0 then break;end
                local chosen=weighted(choices,weights,densityRng);local i,r,cid=chosen.plot,chosen.resource,chosen.continent;
                local p=plots[i];p.resource=r;
                local afterBase=localSites({chosen},base,'base');local afterBoth=localSites({chosen},both,'both');
                local centers={};for _,n in ipairs(p.neighbors) do local np=plots[n];local k=key(np.continent,q);
                    if afterBase[k] and afterBase[k][n] and (goal=='both' and afterBoth[k][n] or goal=='base_only' and not afterBoth[k][n]) then centers[#centers+1]=n;end
                end;table.sort(centers);assert(centers[1],'Density placement has no supported center');
                result.additions[#result.additions+1]={number=#result.additions+1,plot=i,x=p.x,y=p.y,resource=r,quantity=1,continent=cid,quarter=q,material_class=chosen.kind,center=centers[1],repair_size=1,coverage_gains={},phase='site_density',goal=goal,site_gains=chosen.gains};
                reserved[centers[1]]=true;base=afterBase;both=afterBoth;
                spent[cid]=(spent[cid] or 0)+1;density.additions=density.additions+1;current=totals();
            end
        end
        density.after=totals();density.met={base_only=density.after.base_only>=targets.base_only,both=density.after.both>=targets.both};
        density.additions_per_continent=spent;
        -- Combined ceilings include the original repair and the density stage.
        result.legacy_limits={max_per_map=result.max_per_map,max_per_continent=result.max_per_continent};
        result.max_per_map=result.max_per_map+cap;
        local largest=0;for _,cid in ipairs(continents) do largest=math.max(largest,limits[cid]);end
        result.max_per_continent=result.max_per_continent+largest;
    end
    for _,cid in ipairs(continents) do for _,q in ipairs(C.Quarters) do local k=key(cid,q);
        result.coverage[#result.coverage+1]={continent=cid,quarter=q,base_before=count(beforeBase[k]),both_before=count(beforeBoth[k]),base_after=count(base[k]),both_after=count(both[k])};
    end;end
    return result;
end
