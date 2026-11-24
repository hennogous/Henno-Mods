-- Confirmed native Quarter intent -> bounded valuation continuity -> bid adapter.
-- This module consumes plain records only: it never calls CE, orders a purchase,
-- reserves a tile, changes production or invents a completed building. The main
-- publisher confirms choices from the native journal and persists Encode() in a
-- Game property after a successful packet. A separate layout record remembers
-- proposed partners and suppliers. Only native choices create Quarter intent.
CSC_AI_PlanContinuity={}
local C=CSC_AI_PlanContinuity
local function key(city,district,plot)return city..':'..district..':'..plot end
local function integer(v)return (type(v)=='number'or type(v)=='integer')and v==math.floor(v)end
local function event(state,kind,plan,reason)
    if #state.events<64 then
        state.events[#state.events+1]={kind=kind,city=plan.city,district=plan.district,
            plot=plan.plot,reason=reason or kind,valueQ8=plan.lastQ8,forecastTurn=plan.lastFresh,
            baselineWorkers=plan.baselineWorkers,signature=plan.signature}
    else state.eventsDropped=state.eventsDropped+1 end
end

-- Forty rounds cover the observed10-turn purchase and15-turn construction
-- decorators with preparation slack. Once the selected footprint is owned,
-- keep its original baseline at most15 rounds (including already-owned sites).
-- These are policy lifetimes, not claims
-- about every native tree. Expiry restores ordinary current-fact valuation.
C.MaxAge=40
C.AcquiredAge=15
C.MaxPlans=256

-- Decode saved intent into this turn's working state. Version 1 stores the
-- footprint, prior valuation and freshness bookkeeping. Current eligibility
-- comes from fresh facts when the publisher reconsiders the saved plan.
function C.New(player,turn,encoded)
    local state={player=player,turn=turn,plans={},events={},eventsDropped=0}
    if type(encoded)=='string'and encoded:sub(1,2)=='1\n'and #encoded<=65536 then
        local count=0
        for line in encoded:sub(3):gmatch('[^\n]+')do
            count=count+1;if count>C.MaxPlans then break end
            local f={};for field in line:gmatch('[^|]+')do f[#f+1]=field end
            local valid=#f==11
            for i=1,11 do if i~=8 then f[i]=tonumber(f[i]);valid=valid and integer(f[i])end end
            if valid and f[1]>=0 and f[2]>0 and f[3]>=0 and f[4]>=0
                and f[5]>=-1 and (f[6]==0 or f[6]==1)and f[7]>=-1
                and (f[8]=='_'or f[8]:match('^[-%d,]+$'))and f[9]>=0
                and f[9]<=4096*256 and f[10]>=-2 and (f[11]==0 or f[11]==1)then
                local plan={city=f[1],district=f[2],plot=f[3],observed=f[4],acquired=f[5],
                    frontier=f[6]==1,baselineWorkers=f[7],signature=f[8],lastQ8=f[9],
                    lastFresh=f[10],unknownUsed=f[11]}
                if turn<plan.observed or turn-plan.observed>C.MaxAge
                    or plan.acquired>=0 and turn-plan.acquired>C.AcquiredAge then
                    event(state,'memory_expired',plan,'lifetime')
                else state.plans[key(plan.city,plan.district,plan.plot)]=plan end
            end
        end
    end
    return state
end

function C.Selected(state,entry)
    -- The caller proves a native best-site comparison. This is not an accepted
    -- purchase/construction contract; later acquisition proves ownership only,
    -- and must not be called a paid purchase without a Treasury receipt.
    if not entry.economy or not entry.finalQ8 or entry.finalQ8<=0 then return end
    local id=key(entry.city,entry.district,entry.plot)
    local plan=state.plans[id]
    if plan and plan.plot==entry.plot then return plan end
    -- A new best site does not retarget a retained native request (AI-N131).
    -- Keep distinct selected footprints until their own release/expiry.
    plan={city=entry.city,district=entry.district,plot=entry.plot,observed=state.turn,
        acquired=entry.frontier and -1 or state.turn,frontier=entry.frontier==true,
        baselineWorkers=entry.footprintWorkers or -1,signature=entry.footprintSignature or '_',
        lastQ8=math.max(0,entry.ordinaryBidQ8 or entry.finalQ8),
        lastFresh=entry.publishedTurn or state.turn-1,unknownUsed=0}
    state.plans[id]=plan;event(state,'selected',plan,'native_best')
    -- Bound persisted memory independently of publication size. Keep recent
    -- confirmed intents; never evict by a speculative offer's score.
    local ordered={};for _,p in pairs(state.plans)do ordered[#ordered+1]=p end
    table.sort(ordered,function(a,b)
        if a.observed~=b.observed then return a.observed<b.observed end
        if a.city~=b.city then return a.city<b.city end
        if a.district~=b.district then return a.district<b.district end
        return a.plot<b.plot
    end)
    if #ordered>C.MaxPlans then
        local oldest=ordered[1];state.plans[key(oldest.city,oldest.district,oldest.plot)]=nil
        event(state,'memory_released',oldest,'memory_limit')
    end
    return plan
end

function C.Withdraw(state,city,district,plot,reason)
    local id=key(city,district,plot);local plan=state.plans[id]
    if plan then
        state.plans[id]=nil
        local finished=reason=='founded'or reason=='quarter_exists_elsewhere'
        -- This drops our baseline/support, not an engine cancellation order.
        event(state,finished and'memory_released'or'support_withdrawn',plan,reason)
    end
end

function C.Reconcile(state,plan,facts)
    local reason
    if not facts.cityExists then reason='city_lost'
    elseif facts.district>=0 then reason=facts.district==plan.district and 'founded'or'footprint_occupied'
    elseif facts.quarterExists then reason='quarter_exists_elsewhere'
    elseif facts.owner~=state.player and facts.owner~=-1 then reason='ownership_lost'
    elseif plan.acquired>=0 and facts.owner~=state.player then reason='ownership_lost'
    elseif facts.owner==state.player and facts.assigned~=plan.city then reason='city_assignment_changed'end
    if reason then C.Withdraw(state,plan.city,plan.district,plan.plot,reason);return nil end
    if plan.frontier and plan.acquired<0 and facts.owner==state.player then
        plan.acquired=state.turn;event(state,'acquired',plan,'ownership_observed')
    end
    if facts.signature~=plan.signature then
        -- A changed resource, improvement, terrain or feature invalidates the
        -- pre-acquisition baseline. A fresh quote can still justify the site.
        plan.signature=facts.signature;plan.baselineWorkers=-1
        plan.lastFresh=-2;plan.unknownUsed=1;event(state,'reprice',plan,'physical_change')
    end
    return plan
end

function C.PrepareSite(plan,site)
    local copy={};for k,v in pairs(site)do copy[k]=v end
    copy.footprintCostMode='current'
    if plan and plan.acquired>=0 and plan.baselineWorkers==0
        and plan.signature~='_'and plan.signature==site.footprintSignature then
        -- Land selected for this Quarter was unworked at the chosen baseline.
        -- Temporary citizen assignment to that selected footprint must
        -- not turn that SAME project into a full worked-tile loss. Retain its
        -- chosen baseline for this bounded plan only. Current yields, unlocks,
        -- suppliers, customers and all other costs continue to reprice.
        copy.direct={}
        for _,flow in ipairs(site.direct or{})do
            if not flow.id:find('displaced:',1,true)then copy.direct[#copy.direct+1]=flow end
        end
        copy.footprintCostMode=plan.frontier and'acquisition_baseline'or'selection_baseline'
    end
    return copy
end

function C.Grace(state,plan,reason,safe)
    -- A single missing native price/staffing read can preserve an already
    -- confirmed plan. Never turn unknown into a new project or carry through
    -- a known quality/material/ownership failure. Carried bids do not renew age.
    if plan and plan.lastQ8>0 and safe and (reason=='pricing_unavailable'or reason=='footprint_staffing_unavailable')
        and plan.unknownUsed==0 and state.turn-plan.lastFresh>=0 and state.turn-plan.lastFresh<=1 then
        plan.unknownUsed=1;event(state,'grace',plan,reason);return plan.lastQ8
    end
end

function C.Committed(state,entries)
    for _,entry in ipairs(entries)do
        local plan=state.plans[key(entry.city,entry.district,entry.plot)]
        if entry.player==state.player and plan and plan.plot==entry.plot
            and entry.economy and not entry.carried and entry.finalQ8>0 then
            -- Connection costs and the extra supply-layout preference require
            -- fresh partners and sources. Retain only the underlying Quarter
            -- quote for one-publication grace if a native fact goes missing.
            plan.lastQ8=math.max(0,entry.ordinaryBidQ8 or entry.finalQ8)
            plan.lastFresh=state.turn;plan.unknownUsed=0
        end
    end
end

function C.Encode(state)
    local rows={};for _,plan in pairs(state.plans)do rows[#rows+1]=plan end
    table.sort(rows,function(a,b)
        if a.city~=b.city then return a.city<b.city end
        if a.district~=b.district then return a.district<b.district end
        return a.plot<b.plot
    end)
    local text={'1'}
    for _,p in ipairs(rows)do text[#text+1]=table.concat({p.city,p.district,p.plot,p.observed,
        p.acquired,p.frontier and 1 or 0,p.baselineWorkers,p.signature,p.lastQ8,p.lastFresh,p.unknownUsed},'|')end
    return table.concat(text,'\n')..'\n'
end

-- A layout is a shortlist identity, never a saved bid. One record per city
-- and Quarter names both roles and the deposits that justified the proposal.
-- Substitutes are plot hints and must pass the live planner again. The first
-- foundation can arrive after reload, when the previous CE packet is gone.
local layoutFields={'city','district','plot','partnerCity','partnerDistrict','partnerPlot',
    'stage','alternateQuarter','alternatePartner','first','fresh','phase','invoice'}
local function layoutKey(p)return p.city..':'..p.district end
function C.EncodeLayouts(layouts)
    local rows={}
    for _,p in pairs(layouts) do rows[#rows+1]=p end
    table.sort(rows,function(a,b)
        if a.fresh~=b.fresh then return a.fresh>b.fresh end
        if a.city~=b.city then return a.city<b.city end
        return a.district<b.district
    end)
    local lines={'1'}
    for i=1,math.min(#rows,C.MaxPlans) do
        local p,fields=rows[i],{}
        for _,name in ipairs(layoutFields) do fields[#fields+1]=p[name] end
        fields[#fields+1]=table.concat(p.base,',')
        fields[#fields+1]=table.concat(p.specialty,',')
        lines[#lines+1]=table.concat(fields,'|')
    end
    return table.concat(lines,'\n')
end

function C.ReadLayouts(encoded,turn)
    local result={}
    if type(encoded)~='string' or #encoded>65536 or encoded:sub(1,2)~='1\n' then return result end
    local function deposits(field)
        local plots={}
        if field~='' then
            for item in (field..','):gmatch('(.-),') do
                if not item:match('^%d+$') or #plots>=6 then return nil end
                plots[#plots+1]=tonumber(item)
            end
        end
        return plots
    end
    local count=0
    for line in encoded:sub(3):gmatch('[^\n]+') do
        count=count+1
        if count>C.MaxPlans then break end
        local fields={}
        for item in (line..'|'):gmatch('(.-)|') do fields[#fields+1]=item end
        -- Layouts first captured by the continuity prototype had no invoice.
        if #fields==#layoutFields+1 then table.insert(fields,#layoutFields,'0') end
        if #fields==#layoutFields+2 then
            local p,valid={},true
            for i,name in ipairs(layoutFields) do
                local n=tonumber(fields[i])
                local minimum=(name=='alternateQuarter' or name=='alternatePartner') and -1 or 0
                if not integer(n) or n<minimum or n>2147483647 then valid=false;break end
                p[name]=n
            end
            p.base=deposits(fields[#fields-1]);p.specialty=deposits(fields[#fields])
            if valid and p.base and #p.base>0 and p.specialty and p.plot~=p.partnerPlot
                and (p.stage==0 or p.stage>=2 and p.stage<=4)
                and p.phase<=2 and p.first<=p.fresh and p.fresh<=turn and turn-p.fresh<=C.MaxAge then
                result[layoutKey(p)]=p
            end
        end
    end
    return result
end

function C.LayoutRecord(quarter,partner,supply,alternateQuarter,alternatePartner,prior,turn)
    local function plots(rows)
        local seen,indices={},{}
        for _,row in ipairs(rows) do
            if not seen[row.plot] then indices[#indices+1]=row.plot;seen[row.plot]=true end
        end
        table.sort(indices)
        return indices
    end
    local same=prior and prior.plot==quarter.plot and prior.partnerCity==partner.city
        and prior.partnerDistrict==partner.district and prior.partnerPlot==partner.plot
    return {city=quarter.city,district=quarter.district,plot=quarter.plot,partnerCity=partner.city,
        partnerDistrict=partner.district,partnerPlot=partner.plot,stage=partner.stage,
        alternateQuarter=alternateQuarter or -1,alternatePartner=alternatePartner or -1,
        first=same and prior.first or turn,fresh=turn,phase=0,
        invoice=partner.purchaseGold or (same and prior.invoice) or 0,
        base=plots(supply.base),specialty=plots(supply.specialty)}
end
